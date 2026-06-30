#!/usr/bin/env python
"""Train availability-conditioned reliability fusion RepViT + FCOS."""

import argparse
import random
from pathlib import Path
import subprocess
import sys
import time

import torch
from torch.utils.data import DataLoader, Dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.metrics import detection_metrics, format_metrics
from rarepdet.models.availability_reliability_fusion_fcos import build_availability_reliability_fcos


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def log_line(message, log_file=None):
    print(message)
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(message + "\n")


class AvailabilityTriAirDataset(Dataset):
    """Detection dataset wrapper that returns a modality availability vector."""

    def __init__(self, data_root, split_file=None, train=False, modality_dropout=0.0):
        self.dataset = DetectionTriAirDataset(
            data_root,
            split_file=split_file,
            mode="rgbte",
            train=False,
            modality_dropout=0.0,
        )
        self.train = train
        self.modality_dropout = float(modality_dropout)
        if self.modality_dropout < 0.0 or self.modality_dropout >= 1.0:
            raise ValueError("--modality-dropout must be in [0, 1)")

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, index):
        image, target = self.dataset[index]
        availability = torch.ones(3, dtype=torch.float32)
        if self.train and self.modality_dropout > 0.0:
            original = image.clone()
            dropped = []
            if random.random() < self.modality_dropout:
                image[0:3] = 0
                availability[0] = 0
                dropped.append("rgb")
            if random.random() < self.modality_dropout:
                image[3:4] = 0
                availability[1] = 0
                dropped.append("thermal")
            if random.random() < self.modality_dropout:
                image[4:5] = 0
                availability[2] = 0
                dropped.append("event")
            if len(dropped) == 3:
                keep = random.choice((0, 1, 2))
                availability[keep] = 1
                if keep == 0:
                    image[0:3] = original[0:3]
                elif keep == 1:
                    image[3:4] = original[3:4]
                else:
                    image[4:5] = original[4:5]
        return image, target, availability


def availability_collate(batch):
    images, targets, availability = zip(*batch)
    images, targets = collate_fn(list(zip(images, targets)))
    return images, targets, torch.stack(list(availability), dim=0)


def move_targets_to_device(targets, device):
    return [{key: value.to(device) for key, value in target.items()} for target in targets]


def count_params(model):
    return sum(parameter.numel() for parameter in model.parameters())


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


def save_checkpoint(path, model, optimizer, epoch, args, best_ap50, metrics):
    checkpoint = {
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "best_ap50": best_ap50,
        "metrics": metrics,
        "model_cfg": {
            "model_type": "availability_reliability",
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
    image_count = 0
    start = time.time()
    with torch.no_grad():
        for images, targets, availability in loader:
            images = [image.to(device, non_blocking=True) for image in images]
            availability = availability.to(device, non_blocking=True)
            outputs = model(images, availability=availability)
            predictions.extend([{key: value.detach().cpu() for key, value in output.items()} for output in outputs])
            targets_cpu.extend([{key: value.detach().cpu() for key, value in target.items()} for target in targets])
            image_count += len(images)
    metrics = detection_metrics(predictions, targets_cpu, score_thresh=score_thresh)
    metrics["eval_fps"] = image_count / max(time.time() - start, 1e-6)
    return metrics


def write_config(path, args, model, train_len, val_len):
    with path.open("w", encoding="utf-8") as f:
        f.write("Availability-conditioned RarePDet experiment config\n")
        f.write("===================================================\n")
        for key, value in sorted(vars(args).items()):
            f.write(f"{key}: {value}\n")
        f.write(f"train_samples: {train_len}\n")
        f.write(f"val_samples: {val_len}\n")
        f.write(f"params: {count_params(model)}\n")


def main():
    parser = argparse.ArgumentParser(description="Train ACRF RepViT-FCOS on TriAir.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--train-split", default=r"D:\download\triair\splits\train.txt")
    parser.add_argument("--val-split", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--epochs", default=50, type=int)
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--lr", default=1e-4, type=float)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--out", default="runs/E5_acrf_dropout015_repvit_fcos_e50")
    parser.add_argument("--modality-dropout", default=0.15, type=float)
    args = parser.parse_args()

    out_dir = resolve_path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    weights_dir = out_dir / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    log_file = out_dir / "train_log.txt"
    resume_path = weights_dir / "last.pt"
    resume_available = resume_path.exists()
    if log_file.exists() and not resume_available:
        log_file.unlink()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        log_line("WARNING: CUDA requested but unavailable. Falling back to CPU.", log_file)
        device = torch.device("cpu")
    log_line(f"Using device: {device}", log_file)

    train_dataset = AvailabilityTriAirDataset(
        args.data,
        split_file=args.train_split,
        train=True,
        modality_dropout=args.modality_dropout,
    )
    val_dataset = AvailabilityTriAirDataset(args.data, split_file=args.val_split, train=False, modality_dropout=0.0)
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        collate_fn=availability_collate,
        pin_memory=(device.type == "cuda"),
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=availability_collate,
        pin_memory=(device.type == "cuda"),
    )

    model = build_availability_reliability_fcos(img_size=args.img_size).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    best_ap50 = -1.0
    start_epoch = 1
    if resume_available:
        checkpoint = torch.load(resume_path, map_location=device)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        best_ap50 = float(checkpoint.get("best_ap50", -1.0))
        start_epoch = int(checkpoint.get("epoch", 0)) + 1
        log_line(f"Resuming from checkpoint: {resume_path} at epoch {start_epoch}", log_file)

    write_config(out_dir / "config.txt", args, model, len(train_dataset), len(val_dataset))
    log_line(f"train samples: {len(train_dataset)}", log_file)
    log_line(f"val samples: {len(val_dataset)}", log_file)
    log_line(f"params: {count_params(model)}", log_file)
    log_line(f"total train iterations per epoch: {len(train_loader)}", log_file)

    if start_epoch > args.epochs:
        log_line(f"Checkpoint already reached epoch {start_epoch - 1}; nothing to train.", log_file)
        return

    for epoch in range(start_epoch, args.epochs + 1):
        model.train()
        running_loss = 0.0
        epoch_start = time.time()

        for iteration, (images, targets, availability) in enumerate(train_loader, 1):
            images = [image.to(device, non_blocking=True) for image in images]
            targets = move_targets_to_device(targets, device)
            availability = availability.to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)
            loss_dict = model(images, targets, availability=availability)
            loss = sum(loss_dict.values())
            if not loss_is_finite(loss, loss_dict):
                log_line("ERROR: NaN or Inf loss detected. Stopping training.", log_file)
                raise SystemExit(1)
            loss.backward()
            optimizer.step()
            running_loss += float(loss.detach().cpu())

            if iteration == 1 or iteration % 20 == 0 or iteration == len(train_loader):
                loss_parts = ", ".join(f"{key}={float(value.detach().cpu()):.4f}" for key, value in loss_dict.items())
                log_line(
                    f"epoch {epoch}/{args.epochs} iter {iteration}/{len(train_loader)} "
                    f"loss={float(loss.detach().cpu()):.4f} mean_loss={running_loss / iteration:.4f} {loss_parts}",
                    log_file,
                )
            if iteration % 50 == 0:
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
        if is_cuda_oom(exc) and current_batch_size_from_argv(default=4) > 2:
            print("CUDA out of memory detected. Automatically retrying with --batch-size 2.")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            raise SystemExit(subprocess.call([sys.executable, sys.argv[0], *argv_with_batch_size(2)]))
        raise
