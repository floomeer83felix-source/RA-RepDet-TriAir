#!/usr/bin/env python
"""Train Early/Reliability RepViT + FPN + FCOS on TriAir."""

import argparse
import random
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.metrics import detection_metrics, format_metrics
from rarepdet.models.early_fusion_fcos import build_detector


def resolve_path(path):
    path = Path(path)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def log_line(message, log_file=None):
    print(message)
    if log_file is not None:
        with log_file.open("a", encoding="utf-8") as f:
            f.write(message + "\n")


def move_targets_to_device(targets, device):
    return [{key: value.to(device) for key, value in target.items()} for target in targets]


def count_params(model):
    return sum(parameter.numel() for parameter in model.parameters())


def configure_reproducibility(seed):
    """Enable deterministic seeded execution only when explicitly requested."""

    if seed is None:
        return {
            "seed": "None",
            "deterministic_algorithms": "legacy_unseeded",
            "cudnn_deterministic": torch.backends.cudnn.deterministic,
            "cudnn_benchmark": torch.backends.cudnn.benchmark,
        }

    seed = int(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
        deterministic_algorithms = "warn_only"
    except TypeError:
        torch.use_deterministic_algorithms(True)
        deterministic_algorithms = "enabled_without_warn_only"
    except Exception as exc:
        deterministic_algorithms = f"unavailable: {exc}"
    return {
        "seed": seed,
        "deterministic_algorithms": deterministic_algorithms,
        "cudnn_deterministic": torch.backends.cudnn.deterministic,
        "cudnn_benchmark": torch.backends.cudnn.benchmark,
    }


def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


def make_train_generator(seed, device):
    if seed is None:
        return None
    # DataLoader uses a CPU generator for deterministic shuffling.
    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(seed))
    return generator


def reproducibility_lines(args, settings):
    return [
        f"requested_seed: {args.seed}",
        f"deterministic_algorithms: {settings['deterministic_algorithms']}",
        f"cudnn_deterministic: {settings['cudnn_deterministic']}",
        f"cudnn_benchmark: {settings['cudnn_benchmark']}",
    ]


def is_cuda_oom(exc):
    message = str(exc).lower()
    return "out of memory" in message or "cuda error: out of memory" in message


def current_batch_size_from_argv(default=2):
    if "--batch-size" not in sys.argv:
        return default
    index = sys.argv.index("--batch-size")
    if index + 1 >= len(sys.argv):
        return default
    try:
        return int(sys.argv[index + 1])
    except ValueError:
        return default


def argv_with_batch_size(batch_size):
    args = sys.argv[1:]
    if "--batch-size" in args:
        index = args.index("--batch-size")
        if index + 1 < len(args):
            args[index + 1] = str(batch_size)
        else:
            args.append(str(batch_size))
    else:
        args.extend(["--batch-size", str(batch_size)])
    return args


def get_alpha(model):
    alpha = getattr(model.backbone, "last_alpha", None)
    if alpha is None:
        return None
    return alpha.detach().float().mean(dim=0).cpu().tolist()


def loss_is_finite(loss, loss_dict):
    if not torch.isfinite(loss):
        return False
    return all(torch.isfinite(value).all() for value in loss_dict.values())


def print_bad_batch(epoch, iteration, images, targets, loss_dict, log_file):
    log_line("\nERROR: NaN or Inf loss detected. Stopping training.", log_file)
    log_line(f"epoch={epoch} iteration={iteration}", log_file)
    for key, value in loss_dict.items():
        log_line(f"  {key}: {float(value.detach().cpu())}", log_file)
    image_ids = [int(target["image_id"].item()) for target in targets]
    box_counts = [int(target["boxes"].shape[0]) for target in targets]
    shapes = [tuple(image.shape) for image in images]
    log_line(f"  image_ids: {image_ids}", log_file)
    log_line(f"  image_shapes: {shapes}", log_file)
    log_line(f"  target_box_counts: {box_counts}", log_file)


def save_checkpoint(path, model, optimizer, epoch, args, best_ap50, metrics):
    checkpoint = {
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "best_ap50": best_ap50,
        "metrics": metrics,
        "model_cfg": {
            "model_type": args.model,
            "model_name": "repvit_m0_9.dist_300e_in1k",
            "in_chans": 5,
            "img_size": args.img_size,
            "num_classes": 2,
            "fpn_out_channels": 128,
        },
        "train_args": vars(args),
    }
    torch.save(checkpoint, path)


def evaluate(model, loader, device, score_thresh=0.05):
    model.eval()
    predictions = []
    targets_cpu = []
    start = time.time()
    image_count = 0

    with torch.no_grad():
        for images, targets in loader:
            device_images = [image.to(device, non_blocking=True) for image in images]
            outputs = model(device_images)
            predictions.extend([{key: value.detach().cpu() for key, value in output.items()} for output in outputs])
            targets_cpu.extend([{key: value.detach().cpu() for key, value in target.items()} for target in targets])
            image_count += len(images)

    metrics = detection_metrics(predictions, targets_cpu, score_thresh=score_thresh)
    elapsed = max(time.time() - start, 1e-6)
    metrics["eval_fps"] = image_count / elapsed
    return metrics


def write_config(path, args, model, train_len, val_len, reproducibility_settings=None):
    with path.open("w", encoding="utf-8") as f:
        f.write("RarePDet experiment config\n")
        f.write("==========================\n")
        for key, value in sorted(vars(args).items()):
            f.write(f"{key}: {value}\n")
        if reproducibility_settings is not None:
            for line in reproducibility_lines(args, reproducibility_settings):
                f.write(line + "\n")
        f.write(f"train_samples: {train_len}\n")
        f.write(f"val_samples: {val_len}\n")
        f.write(f"params: {count_params(model)}\n")
        f.write("gflops: skipped (no project-compatible detector GFLOPs helper wired yet)\n")
        f.write("fps: reported as eval_fps in train_log.txt after validation\n")


def main():
    parser = argparse.ArgumentParser(description="Train RarePDet fusion FCOS variants.")
    parser.add_argument(
        "--model",
        default="early",
        choices=("early", "reliability", "reliability_rgbt", "ra_static_equal", "ra_stems_project"),
    )
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--train-split", default=r"D:\download\triair\splits\train.txt")
    parser.add_argument("--val-split", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--epochs", default=1, type=int)
    parser.add_argument("--batch-size", default=2, type=int)
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--lr", default=1e-4, type=float)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--out", default="runs/rarepdet_early")
    parser.add_argument("--modality-dropout", default=0.0, type=float)
    parser.add_argument("--seed", default=None, type=int)
    args = parser.parse_args()

    if args.epochs <= 0:
        raise SystemExit("ERROR: --epochs must be positive.")
    if args.batch_size <= 0:
        raise SystemExit("ERROR: --batch-size must be positive.")
    if args.img_size <= 0:
        raise SystemExit("ERROR: --img-size must be positive.")

    reproducibility_settings = configure_reproducibility(args.seed)

    out_dir = resolve_path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    weights_dir = out_dir / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    log_file = out_dir / "train_log.txt"
    if log_file.exists():
        log_file.unlink()

    requested_device = torch.device(args.device)
    if requested_device.type == "cuda" and not torch.cuda.is_available():
        log_line("WARNING: CUDA requested but not available. Falling back to CPU.", log_file)
        requested_device = torch.device("cpu")
    device = requested_device
    log_line(f"Using device: {device}", log_file)
    for line in reproducibility_lines(args, reproducibility_settings):
        log_line(line, log_file)

    train_dataset = DetectionTriAirDataset(
        args.data,
        split_file=args.train_split,
        mode="rgbte",
        train=True,
        modality_dropout=args.modality_dropout,
    )
    val_dataset = DetectionTriAirDataset(
        args.data,
        split_file=args.val_split,
        mode="rgbte",
        train=False,
        modality_dropout=0.0,
    )

    train_generator = make_train_generator(args.seed, device)
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
        generator=train_generator,
        worker_init_fn=seed_worker if args.seed is not None else None,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )

    model = build_detector(
        model_type=args.model,
        model_name="repvit_m0_9.dist_300e_in1k",
        img_size=args.img_size,
        num_classes=2,
        fpn_out_channels=128,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    write_config(out_dir / "config.txt", args, model, len(train_dataset), len(val_dataset), reproducibility_settings)
    log_line(f"train samples: {len(train_dataset)}", log_file)
    log_line(f"val samples: {len(val_dataset)}", log_file)
    log_line(f"params: {count_params(model)}", log_file)
    log_line("gflops: skipped (no project-compatible detector GFLOPs helper wired yet)", log_file)
    log_line(f"total train iterations per epoch: {len(train_loader)}", log_file)

    best_ap50 = -1.0
    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss = 0.0
        epoch_start = time.time()

        for iteration, (images, targets) in enumerate(train_loader, 1):
            images = [image.to(device, non_blocking=True) for image in images]
            targets = move_targets_to_device(targets, device)

            optimizer.zero_grad(set_to_none=True)
            loss_dict = model(images, targets)
            loss = sum(loss_dict.values())

            if not loss_is_finite(loss, loss_dict):
                print_bad_batch(epoch, iteration, images, targets, loss_dict, log_file)
                raise SystemExit(1)

            loss.backward()
            optimizer.step()
            running_loss += float(loss.detach().cpu())

            if iteration == 1 or iteration % 20 == 0 or iteration == len(train_loader):
                loss_parts = ", ".join(f"{key}={float(value.detach().cpu()):.4f}" for key, value in loss_dict.items())
                message = (
                    f"epoch {epoch}/{args.epochs} iter {iteration}/{len(train_loader)} "
                    f"loss={float(loss.detach().cpu()):.4f} "
                    f"mean_loss={running_loss / iteration:.4f} {loss_parts}"
                )
                log_line(message, log_file)

            if args.model == "reliability" and iteration % 50 == 0:
                alpha = get_alpha(model)
                if alpha is not None:
                    log_line(
                        f"epoch {epoch} iter {iteration} alpha_rgb={alpha[0]:.4f} "
                        f"alpha_thermal={alpha[1]:.4f} alpha_event={alpha[2]:.4f}",
                        log_file,
                    )

        metrics = evaluate(model, val_loader, device)
        elapsed = time.time() - epoch_start
        log_line(
            f"epoch {epoch} validation {format_metrics(metrics)} "
            f"eval_fps={metrics['eval_fps']:.2f} epoch_time_sec={elapsed:.1f}",
            log_file,
        )

        last_path = weights_dir / "last.pt"
        save_checkpoint(last_path, model, optimizer, epoch, args, best_ap50, metrics)
        log_line(f"saved checkpoint: {last_path}", log_file)

        if metrics["ap50"] > best_ap50:
            best_ap50 = metrics["ap50"]
            best_path = weights_dir / "best.pt"
            save_checkpoint(best_path, model, optimizer, epoch, args, best_ap50, metrics)
            log_line(f"new best AP50={best_ap50:.4f}; saved checkpoint: {best_path}", log_file)

    log_line("Training complete.", log_file)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        if is_cuda_oom(exc) and current_batch_size_from_argv(default=2) > 2:
            print("CUDA out of memory detected. Automatically retrying with --batch-size 2.")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            retry_args = argv_with_batch_size(2)
            raise SystemExit(subprocess.call([sys.executable, sys.argv[0], *retry_args]))
        raise
