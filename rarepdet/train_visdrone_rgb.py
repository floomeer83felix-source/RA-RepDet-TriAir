#!/usr/bin/env python
"""Train the V50 pure RGB RepViT-M0.9 FPN FCOS baseline."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.visdrone_seen_dataset import VisDroneSeenVehicleDataset, collate_fn
from rarepdet.models.rgb_fcos import build_rgb_fcos
from rarepdet.train_early_fusion import (
    configure_reproducibility,
    count_params,
    log_line,
    make_train_generator,
    move_targets_to_device,
    reproducibility_lines,
    seed_worker,
)
from rarepdet.v50_coco import evaluate_detections, outputs_to_detections


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def save_checkpoint(path, model, optimizer, epoch, args, best_ap50, metrics):
    torch.save(
        {
            "epoch": epoch,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "best_ap50": best_ap50,
            "metrics": metrics,
            "model_cfg": {
                "model_type": "rgb",
                "model_name": "repvit_m0_9.dist_300e_in1k",
                "in_chans": 3,
                "img_size": args.img_size,
                "num_classes": 2,
                "fpn_out_channels": 128,
            },
            "train_args": vars(args),
        },
        path,
    )


def evaluate(model, loader, annotations, device, score_threshold, max_detections):
    model.eval()
    detections = []
    with torch.no_grad():
        for images, targets in loader:
            outputs = model([image.to(device, non_blocking=True) for image in images])
            detections.extend(
                outputs_to_detections(
                    outputs,
                    targets,
                    score_threshold=score_threshold,
                    max_detections=max_detections,
                )
            )
    return evaluate_detections(annotations, detections, max_detections=max_detections)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=r"D:\datasets\visdrone_seen")
    parser.add_argument("--train-manifest", required=True)
    parser.add_argument("--train-annotations", required=True)
    parser.add_argument("--val-manifest", required=True)
    parser.add_argument("--val-annotations", required=True)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--detector-score-thr", type=float, default=0.001)
    parser.add_argument("--nms-thresh", type=float, default=0.6)
    parser.add_argument("--detections-per-img", type=int, default=100)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    if args.epochs <= 0 or args.batch_size <= 0:
        raise SystemExit("epochs and batch size must be positive")
    output = resolve_path(args.out)
    weights_dir = output / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    log_file = output / "train_log.txt"
    if log_file.exists():
        log_file.unlink()

    settings = configure_reproducibility(args.seed)
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    for line in reproducibility_lines(args, settings):
        log_line(line, log_file)

    train_dataset = VisDroneSeenVehicleDataset(
        args.data,
        resolve_path(args.train_manifest),
        resolve_path(args.train_annotations),
        five_channel=False,
    )
    val_dataset = VisDroneSeenVehicleDataset(
        args.data,
        resolve_path(args.val_manifest),
        resolve_path(args.val_annotations),
        five_channel=False,
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=device.type == "cuda",
        generator=make_train_generator(args.seed, device),
        worker_init_fn=seed_worker,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=device.type == "cuda",
    )
    model = build_rgb_fcos(
        img_size=args.img_size,
        score_thresh=args.detector_score_thr,
        nms_thresh=args.nms_thresh,
        detections_per_img=args.detections_per_img,
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    (output / "config.txt").write_text(
        "V50 pure RGB baseline\n"
        + "\n".join(f"{key}: {value}" for key, value in sorted(vars(args).items()))
        + f"\ntrain_samples: {len(train_dataset)}\nval_samples: {len(val_dataset)}\n"
        + f"params: {count_params(model)}\n",
        encoding="utf-8",
    )
    log_line(f"device: {device}", log_file)
    log_line(f"train samples: {len(train_dataset)}", log_file)
    log_line(f"val samples: {len(val_dataset)}", log_file)
    log_line(f"params: {count_params(model)}", log_file)
    log_line(f"iterations per epoch: {len(train_loader)}", log_file)

    best_ap50 = -1.0
    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss = 0.0
        epoch_start = time.time()
        for iteration, (images, targets) in enumerate(train_loader, 1):
            images = [image.to(device, non_blocking=True) for image in images]
            targets = move_targets_to_device(targets, device)
            optimizer.zero_grad(set_to_none=True)
            losses = model(images, targets)
            loss = sum(losses.values())
            if not torch.isfinite(loss):
                raise RuntimeError(f"non-finite loss at epoch={epoch} iteration={iteration}")
            loss.backward()
            optimizer.step()
            running_loss += float(loss.detach().cpu())
            if iteration == 1 or iteration % 20 == 0 or iteration == len(train_loader):
                log_line(
                    f"epoch {epoch}/{args.epochs} iter {iteration}/{len(train_loader)} "
                    f"loss={float(loss.detach().cpu()):.4f} mean_loss={running_loss / iteration:.4f}",
                    log_file,
                )

        metrics = evaluate(
            model,
            val_loader,
            resolve_path(args.val_annotations),
            device,
            args.detector_score_thr,
            args.detections_per_img,
        )
        elapsed = time.time() - epoch_start
        log_line(
            f"epoch {epoch} devval AP50_95={metrics['ap50_95']:.6f} "
            f"AP50={metrics['ap50']:.6f} AP75={metrics['ap75']:.6f} "
            f"AR100={metrics['ar100']:.6f} epoch_time_sec={elapsed:.1f}",
            log_file,
        )
        save_checkpoint(weights_dir / "last.pt", model, optimizer, epoch, args, best_ap50, metrics)
        if metrics["ap50"] > best_ap50:
            best_ap50 = metrics["ap50"]
            save_checkpoint(weights_dir / "best.pt", model, optimizer, epoch, args, best_ap50, metrics)
            log_line(f"new best canonical AP50={best_ap50:.6f}", log_file)
    log_line("Training complete.", log_file)


if __name__ == "__main__":
    main()
