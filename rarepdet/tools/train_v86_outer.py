#!/usr/bin/env python3
"""Train one V86 outer-fold model without reading the held-out fold."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.models.early_fusion_fcos import build_detector
from rarepdet.train_early_fusion import (
    configure_reproducibility,
    loss_is_finite,
    make_train_generator,
    move_targets_to_device,
    seed_worker,
)


V86_ROOT = ROOT / "reproducibility/v86_proxy_sequence_outer_folds"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def save_checkpoint(path: Path, model, optimizer, args, manifest: Path) -> None:
    torch.save(
        {
            "epoch": 50,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "model_cfg": {
                "experiment": "V86_PROXY_SEQUENCE_OUTER_EVALUATION",
                "model_type": args.model,
                "model_name": "repvit_m0_9.dist_300e_in1k",
                "in_chans": 5,
                "img_size": 640,
                "num_classes": 2,
                "fpn_out_channels": 128,
            },
            "train_args": vars(args),
            "selection_rule": "final checkpoint after exactly 50 epochs; no validation inference",
            "train_manifest": str(manifest),
            "train_manifest_sha256": sha256(manifest),
        },
        path,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("reliability_rgbt",), required=True)
    parser.add_argument("--outer-fold", type=int, choices=range(5), required=True)
    parser.add_argument("--seed", type=int, choices=range(5), required=True)
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--out", required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--num-workers", type=int, default=0)
    args = parser.parse_args()
    if (args.epochs, args.batch_size, args.img_size, args.lr, args.num_workers) != (
        50,
        4,
        640,
        1e-4,
        0,
    ):
        raise SystemExit("V86 is frozen at epochs=50, batch=4, size=640, lr=1e-4, workers=0")
    return args


def main() -> None:
    args = parse_args()
    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8":
        raise RuntimeError("V86 requires CUBLAS_WORKSPACE_CONFIG=:4096:8 before process start")
    device = torch.device(args.device)
    if device.type != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("V86 training requires CUDA")
    manifest = V86_ROOT / "manifests" / f"v86_outer_fold_{args.outer_fold}_train_complement.txt"
    if not manifest.is_file():
        raise FileNotFoundError(manifest)
    out = Path(args.out).resolve()
    weights = out / "weights"
    weights.mkdir(parents=True, exist_ok=True)
    status_path = out / "run_status.json"
    settings = configure_reproducibility(args.seed)
    dataset = DetectionTriAirDataset(
        args.data,
        split_file=str(manifest),
        mode="rgbte",
        train=True,
        modality_dropout=0.0,
    )
    generator = make_train_generator(args.seed, device)
    loader = DataLoader(
        dataset,
        batch_size=4,
        shuffle=True,
        num_workers=0,
        collate_fn=collate_fn,
        pin_memory=True,
        generator=generator,
        worker_init_fn=seed_worker,
    )
    model = build_detector(args.model, img_size=640).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    started = time.time()
    log_path = out / "train_log.txt"
    atomic_json(
        status_path,
        {
            "state": "RUNNING",
            "model": args.model,
            "outer_fold": args.outer_fold,
            "seed": args.seed,
            "train_images": len(dataset),
            "train_manifest_sha256": sha256(manifest),
            "outer_fold_accessed": False,
            "selection_rule": "final epoch 50; no validation inference",
            "started_at": started,
            "reproducibility": settings,
        },
    )
    try:
        for epoch in range(1, 51):
            model.train()
            running_loss = 0.0
            epoch_started = time.time()
            for images, targets in loader:
                images = [image.to(device, non_blocking=True) for image in images]
                targets = move_targets_to_device(targets, device)
                optimizer.zero_grad(set_to_none=True)
                loss_dict = model(images, targets)
                loss = sum(loss_dict.values())
                if not loss_is_finite(loss, loss_dict):
                    raise RuntimeError(f"non-finite loss at epoch {epoch}")
                loss.backward()
                optimizer.step()
                running_loss += float(loss.detach().cpu())
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(
                    f"epoch={epoch} mean_loss={running_loss / len(loader):.8f} "
                    f"seconds={time.time() - epoch_started:.3f}\n"
                )
        checkpoint = weights / "epoch_050_final.pt"
        save_checkpoint(checkpoint, model, optimizer, args, manifest)
        atomic_json(
            status_path,
            {
                "state": "COMPLETE",
                "model": args.model,
                "outer_fold": args.outer_fold,
                "seed": args.seed,
                "epochs": 50,
                "train_images": len(dataset),
                "train_manifest_sha256": sha256(manifest),
                "outer_fold_accessed": False,
                "selection_rule": "final epoch 50; no validation inference",
                "checkpoint": str(checkpoint),
                "checkpoint_sha256": sha256(checkpoint),
                "training_seconds": time.time() - started,
                "reproducibility": settings,
            },
        )
    except Exception as exc:
        atomic_json(
            status_path,
            {
                "state": "FAILED",
                "model": args.model,
                "outer_fold": args.outer_fold,
                "seed": args.seed,
                "outer_fold_accessed": False,
                "error": repr(exc),
                "training_seconds": time.time() - started,
            },
        )
        raise


if __name__ == "__main__":
    main()
