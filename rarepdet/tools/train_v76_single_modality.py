#!/usr/bin/env python
"""Train one frozen V76 RGB-only, thermal-only, or event-only TriAir baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.experimental.v76_single_modality_detector import INPUT_CHANNELS, build_v76_single_modality_detector
from rarepdet.train_early_fusion import configure_reproducibility, evaluate, loss_is_finite, make_train_generator, move_targets_to_device, seed_worker


def atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def save_checkpoint(path: Path, model, optimizer, epoch: int, args, best_ap50: float, metrics: dict) -> None:
    torch.save({
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "best_ap50": best_ap50,
        "metrics": metrics,
        "model_cfg": {
            "experiment": "V76_TRIAIR_SINGLE_MODALITY_ABLATION",
            "input_mode": args.input_mode,
            "in_chans": INPUT_CHANNELS[args.input_mode],
            "model_name": "repvit_m0_9.dist_300e_in1k",
            "img_size": args.img_size,
            "num_classes": 2,
            "fpn_out_channels": 128,
        },
        "train_args": vars(args),
    }, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-mode", choices=sorted(INPUT_CHANNELS), required=True)
    parser.add_argument("--seed", type=int, choices=(0, 1, 2), required=True)
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--train-split", default=r"reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_train.txt")
    parser.add_argument("--val-split", default=r"reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_val.txt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.epochs != 50:
        raise SystemExit("V76 is frozen at exactly 50 epochs.")
    if args.batch_size != 4 or args.img_size != 640 or args.lr != 1e-4:
        raise SystemExit("V76 batch size, image size, and learning rate are frozen.")
    return args


def resolve(path: str) -> Path:
    value = Path(path)
    return value if value.is_absolute() else PROJECT_ROOT / value


def main() -> None:
    args = parse_args()
    out = resolve(args.out)
    weights = out / "weights"
    out.mkdir(parents=True, exist_ok=True)
    weights.mkdir(parents=True, exist_ok=True)
    status_path = out / "run_status.json"
    atomic_json(status_path, {"state": "RUNNING", "input_mode": args.input_mode, "seed": args.seed, "selection_rule": "highest development-validation project-local AP50", "guard_used": False, "started_at": time.time()})

    reproducibility = configure_reproducibility(args.seed)
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("V76 requires CUDA; CPU fallback is disabled to preserve the execution contract.")

    train_dataset = DetectionTriAirDataset(args.data, split_file=resolve(args.train_split), mode=args.input_mode, train=True, modality_dropout=0.0)
    val_dataset = DetectionTriAirDataset(args.data, split_file=resolve(args.val_split), mode=args.input_mode, train=False, modality_dropout=0.0)
    generator = make_train_generator(args.seed, device)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers, collate_fn=collate_fn, pin_memory=True, generator=generator, worker_init_fn=seed_worker)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers, collate_fn=collate_fn, pin_memory=True)

    model = build_v76_single_modality_detector(args.input_mode, img_size=args.img_size).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    log_path = out / "train_log.txt"
    best_ap50 = -1.0
    best_epoch = None
    started = time.time()

    try:
        for epoch in range(1, args.epochs + 1):
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
                handle.write(f"epoch={epoch} mean_loss={running / max(len(train_loader), 1):.8f} project_ap50={ap50:.8f} project_ap75={float(metrics['ap75']):.8f}\n")
            if ap50 > best_ap50:
                best_ap50 = ap50
                best_epoch = epoch
                save_checkpoint(weights / "best.pt", model, optimizer, epoch, args, best_ap50, metrics)
            save_checkpoint(weights / "last.pt", model, optimizer, epoch, args, best_ap50, metrics)

        atomic_json(status_path, {"state": "COMPLETE", "input_mode": args.input_mode, "seed": args.seed, "epochs": args.epochs, "best_epoch": best_epoch, "best_project_ap50": best_ap50, "selection_rule": "highest development-validation project-local AP50", "guard_used": False, "training_runtime_seconds": time.time() - started, "reproducibility": reproducibility, "best_checkpoint": str(weights / "best.pt")})
    except Exception as exc:
        atomic_json(status_path, {"state": "FAILED", "input_mode": args.input_mode, "seed": args.seed, "guard_used": False, "error": repr(exc), "training_runtime_seconds": time.time() - started})
        raise


if __name__ == "__main__":
    main()
