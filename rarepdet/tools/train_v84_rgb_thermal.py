#!/usr/bin/env python
"""Train one frozen V84 RGB+thermal RepViT-FCOS baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.models.early_fusion_fcos import build_early_fusion_fcos
from rarepdet.train_early_fusion import (
    configure_reproducibility,
    evaluate,
    loss_is_finite,
    make_train_generator,
    move_targets_to_device,
    seed_worker,
)


def resolve(path: str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def save_checkpoint(path: Path, model, optimizer, epoch: int, args, best_ap50: float, metrics: dict) -> None:
    torch.save(
        {
            "epoch": epoch,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "best_ap50": best_ap50,
            "metrics": metrics,
            "model_cfg": {
                "experiment": "V84_RGB_THERMAL_BASELINE",
                "input_mode": "rgbt",
                "model_type": "early",
                "in_chans": 4,
                "model_name": "repvit_m0_9.dist_300e_in1k",
                "img_size": 640,
                "num_classes": 2,
                "fpn_out_channels": 128,
            },
            "train_args": vars(args),
        },
        path,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, choices=(0, 1, 2), required=True)
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--train-split", required=True)
    parser.add_argument("--val-split", required=True)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if (args.epochs, args.batch_size, args.img_size, args.lr) != (50, 4, 640, 1e-4):
        raise SystemExit("V84 RGB+thermal protocol is frozen at 50 epochs, batch 4, 640x640, lr 1e-4")
    return args


def main() -> None:
    args = parse_args()
    out = resolve(args.out)
    weights = out / "weights"
    weights.mkdir(parents=True, exist_ok=True)
    status_path = out / "run_status.json"
    reproducibility = configure_reproducibility(args.seed)
    device = torch.device(args.device)
    if device.type != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("V84 RGB+thermal training requires CUDA")
    train_set = DetectionTriAirDataset(args.data, split_file=resolve(args.train_split), mode="rgbt", train=True, modality_dropout=0.0)
    val_set = DetectionTriAirDataset(args.data, split_file=resolve(args.val_split), mode="rgbt", train=False, modality_dropout=0.0)
    generator = make_train_generator(args.seed, device)
    train_loader = DataLoader(train_set, batch_size=4, shuffle=True, num_workers=0, collate_fn=collate_fn, pin_memory=True, generator=generator, worker_init_fn=seed_worker)
    val_loader = DataLoader(val_set, batch_size=4, shuffle=False, num_workers=0, collate_fn=collate_fn, pin_memory=True)
    model = build_early_fusion_fcos(in_chans=4, img_size=640).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    started = time.time()
    best_ap50 = -1.0
    best_epoch = None
    log_path = out / "train_log.txt"
    atomic_json(status_path, {"state": "RUNNING", "input_mode": "rgbt", "seed": args.seed, "started_at": started, "guard_used": False, "selection_rule": "highest development-validation project-local AP50"})
    try:
        for epoch in range(1, 51):
            model.train()
            running = 0.0
            for images, targets in train_loader:
                images = [image.to(device, non_blocking=True) for image in images]
                targets = move_targets_to_device(targets, device)
                optimizer.zero_grad(set_to_none=True)
                loss_dict = model(images, targets)
                loss = sum(loss_dict.values())
                if not loss_is_finite(loss, loss_dict):
                    raise RuntimeError(f"non-finite training loss at epoch {epoch}")
                loss.backward()
                optimizer.step()
                running += float(loss.detach().cpu())
            metrics = evaluate(model, val_loader, device, score_thresh=0.05)
            ap50 = float(metrics["ap50"])
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"epoch={epoch} mean_loss={running / len(train_loader):.8f} project_ap50={ap50:.8f} project_ap75={float(metrics['ap75']):.8f}\n")
            if ap50 > best_ap50:
                best_ap50, best_epoch = ap50, epoch
                save_checkpoint(weights / "best.pt", model, optimizer, epoch, args, best_ap50, metrics)
            save_checkpoint(weights / "last.pt", model, optimizer, epoch, args, best_ap50, metrics)
        atomic_json(status_path, {"state": "COMPLETE", "input_mode": "rgbt", "seed": args.seed, "epochs": 50, "best_epoch": best_epoch, "best_project_ap50": best_ap50, "selection_rule": "highest development-validation project-local AP50", "guard_used": False, "training_runtime_seconds": time.time() - started, "reproducibility": reproducibility, "best_checkpoint": str(weights / "best.pt")})
    except Exception as exc:
        atomic_json(status_path, {"state": "FAILED", "input_mode": "rgbt", "seed": args.seed, "guard_used": False, "error": repr(exc), "training_runtime_seconds": time.time() - started})
        raise


if __name__ == "__main__":
    main()
