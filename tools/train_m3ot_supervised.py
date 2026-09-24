#!/usr/bin/env python3
"""Matched from-scratch RGB+IR FCOS training on audited M3OT train/val."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

# PyTorch's deterministic CuBLAS kernels require this before CUDA initializes.
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import timm
import torch
import torchvision
from torch.utils.data import DataLoader, RandomSampler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.m3ot_dataset import M3OTExternalDataset
from datasets.triair_dataset import collate_fn
from rarepdet.coco_metrics import coco_detection_metrics
from rarepdet.models.early_fusion_fcos import (
    build_early_fusion_fcos, build_reliability_rgbt_fcos,
)
from rarepdet.train_early_fusion import configure_reproducibility, seed_worker


EPOCHS = 50
BATCH_SIZE = 4
IMAGE_SIZE = 640
LR = 1e-4
WEIGHT_DECAY = 1e-4
SCORE_FLOOR = 0.001
NMS_IOU = 0.60
MAX_DETECTIONS = 100


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def should_update_best(ap50: float, best_ap50: float) -> bool:
    return ap50 > best_ap50


def atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_torch(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def rng_state(sampler_generator: torch.Generator) -> dict:
    import random
    import numpy as np

    return {"python": random.getstate(), "numpy": np.random.get_state(),
            "torch": torch.get_rng_state(),
            "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
            "sampler": sampler_generator.get_state()}


def restore_rng_state(state: dict, sampler_generator: torch.Generator) -> None:
    import random
    import numpy as np

    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])
    if state["cuda"] is not None and torch.cuda.is_available():
        torch.cuda.set_rng_state_all(state["cuda"])
    sampler_generator.set_state(state["sampler"])


def make_model(model_type: str) -> torch.nn.Module:
    kwargs = {"img_size": IMAGE_SIZE, "num_classes": 2, "fpn_out_channels": 128,
              "score_thresh": SCORE_FLOOR, "nms_thresh": NMS_IOU,
              "detections_per_img": MAX_DETECTIONS}
    if model_type == "early":
        return build_early_fusion_fcos(in_chans=4, **kwargs)
    if model_type == "reliability_rgbt":
        return build_reliability_rgbt_fcos(**kwargs)
    raise ValueError(f"Unsupported model type: {model_type}")


def config(args, train_manifest: Path, val_manifest: Path) -> dict:
    return {"protocol": "M3OT_SUPERVISED_RGBT_SIX_SEED_V1",
            "model": args.model, "seed": args.seed,
            "train_manifest": str(train_manifest), "train_manifest_sha256": sha256(train_manifest),
            "val_manifest": str(val_manifest), "val_manifest_sha256": sha256(val_manifest),
            "epochs": EPOCHS, "batch_size": BATCH_SIZE, "img_size": IMAGE_SIZE,
            "optimizer": "AdamW", "lr": LR, "weight_decay": WEIGHT_DECAY,
            "lr_schedule": "constant", "pretrained": False,
            "augmentations": [], "modality_dropout": 0.0,
            "score_threshold": SCORE_FLOOR, "nms_iou": NMS_IOU,
            "max_detections": MAX_DETECTIONS, "best_rule": "strictly higher val AP50; earliest tie",
            "target_class": "vehicle", "target_label": 1,
            "output_coordinates": "RGB", "num_workers": args.num_workers}


def assert_audit(audit_dir: Path, train_manifest: Path, val_manifest: Path) -> None:
    audit = json.loads((audit_dir / "pairing_audit.json").read_text(encoding="utf-8"))
    visual = (audit_dir / "visual_review.md").read_text(encoding="utf-8")
    if "Status: `PASS_WITH_CROSS_MODAL_VIEW_OFFSET`" not in visual:
        raise RuntimeError("M3OT pretraining visual review has not passed")
    if audit["totals"]["train"] != {"images": 8630, "boxes": 111678, "zero_gt": 0}:
        raise RuntimeError("M3OT train audit counts changed")
    if audit["totals"]["val"] != {"images": 1200, "boxes": 13781, "zero_gt": 0}:
        raise RuntimeError("M3OT val audit counts changed")
    if audit["split_integrity"]["cross_split_frame_overlap"] != 0:
        raise RuntimeError("M3OT train/val overlap detected")
    for split, path in (("train", train_manifest), ("val", val_manifest)):
        if sha256(path) != audit["manifest_sha256"][split]:
            raise RuntimeError(f"M3OT {split} manifest hash differs from audited file")


def evaluate(model: torch.nn.Module, loader: DataLoader, device: torch.device) -> dict:
    model.eval()
    predictions, targets = [], []
    with torch.inference_mode():
        for images, batch_targets in loader:
            outputs = model([image.to(device, non_blocking=True) for image in images])
            for output in outputs:
                predictions.append({key: output[key].detach().cpu() for key in ("boxes", "scores", "labels")})
            targets.extend(batch_targets)
    return coco_detection_metrics(predictions, targets, score_thresh=0.0,
                                  max_detections=MAX_DETECTIONS)


def train_epoch(model: torch.nn.Module, loader: DataLoader,
                optimizer: torch.optim.Optimizer, device: torch.device,
                epoch: int, smoke_steps: int = 0) -> tuple[float, float, int]:
    model.train()
    start = time.monotonic()
    total_loss = 0.0
    count = 0
    for step, (images, targets) in enumerate(loader, 1):
        images = [image.to(device, non_blocking=True) for image in images]
        targets = [{key: value.to(device) for key, value in target.items()}
                   for target in targets]
        optimizer.zero_grad(set_to_none=True)
        losses = model(images, targets)
        loss = sum(losses.values())
        if not bool(torch.isfinite(loss)):
            raise RuntimeError(f"Non-finite loss at epoch {epoch}, step {step}: {losses}")
        loss.backward()
        optimizer.step()
        total_loss += float(loss.detach().cpu())
        count += 1
        if step == 1 or step % 100 == 0:
            print(f"epoch={epoch}/{EPOCHS} step={step}/{len(loader)} "
                  f"loss={total_loss / count:.5f}", flush=True)
        if smoke_steps and step >= smoke_steps:
            break
    if device.type == "cuda":
        torch.cuda.synchronize()
    return total_loss / count, time.monotonic() - start, count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--model", choices=("early", "reliability_rgbt"), required=True)
    parser.add_argument("--seed", type=int, choices=(0, 1, 2), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--smoke-steps", type=int, default=0)
    parser.add_argument("--num-workers", type=int, choices=(0, 2, 4), default=2)
    args = parser.parse_args()
    if args.smoke_steps < 0:
        parser.error("--smoke-steps must be nonnegative")
    if not args.smoke_steps and args.num_workers != 2:
        parser.error("Official six-seed training freezes --num-workers at 2")
    audit_dir = args.audit_dir.resolve(strict=True)
    train_manifest = audit_dir / "train_manifest.json"
    val_manifest = audit_dir / "val_manifest.json"
    assert_audit(audit_dir, train_manifest, val_manifest)
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the frozen M3OT training protocol")
    device = torch.device("cuda")
    reproducibility = configure_reproducibility(args.seed)
    settings = config(args, train_manifest, val_manifest)
    settings["reproducibility"] = reproducibility
    settings["runtime"] = {"python": platform.python_version(), "torch": str(torch.__version__),
                           "torchvision": torchvision.__version__, "timm": timm.__version__,
                           "cuda": torch.version.cuda,
                           "cublas_workspace_config": os.environ["CUBLAS_WORKSPACE_CONFIG"],
                           "gpu": torch.cuda.get_device_name(0)}
    train_data = M3OTExternalDataset(train_manifest, model_type=args.model,
                                     expected_split="train")
    val_data = M3OTExternalDataset(val_manifest, model_type=args.model,
                                   expected_split="val")
    if (len(train_data), len(val_data)) != (8630, 1200):
        raise RuntimeError("M3OT manifest sample counts changed")
    sampler_generator = torch.Generator(device="cpu").manual_seed(args.seed)
    worker_generator = torch.Generator(device="cpu").manual_seed(args.seed + 1000000)
    sampler = RandomSampler(train_data, generator=sampler_generator)
    train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, sampler=sampler,
                              num_workers=args.num_workers, collate_fn=collate_fn,
                              pin_memory=True, generator=worker_generator,
                              worker_init_fn=seed_worker if args.num_workers else None,
                              persistent_workers=args.num_workers > 0)
    val_loader = DataLoader(val_data, batch_size=BATCH_SIZE, shuffle=False,
                            num_workers=args.num_workers, collate_fn=collate_fn,
                            pin_memory=True,
                            generator=torch.Generator(device="cpu").manual_seed(args.seed + 2000000),
                            persistent_workers=args.num_workers > 0)
    model = make_model(args.model).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    print(f"model={args.model} seed={args.seed} params="
          f"{sum(parameter.numel() for parameter in model.parameters())} "
          f"train={len(train_data)} val={len(val_data)} "
          f"steps_per_epoch={len(train_loader)}", flush=True)

    if args.smoke_steps:
        loss, seconds, steps = train_epoch(model, train_loader, optimizer, device,
                                          epoch=1, smoke_steps=args.smoke_steps)
        print(f"SMOKE_OK model={args.model} seed={args.seed} steps={steps} "
              f"mean_loss={loss:.5f} seconds_per_step={seconds / steps:.4f}", flush=True)
        return

    out = args.out.resolve()
    weights = out / "weights"
    config_path = out / "config.json"
    last_path = weights / "last.pt"
    best_path = weights / "best.pt"
    history_path = out / "history.jsonl"
    status_path = out / "status.json"
    if args.resume:
        if not config_path.is_file() or not last_path.is_file():
            raise RuntimeError(f"Cannot resume without config and last checkpoint: {out}")
        saved_config = json.loads(config_path.read_text(encoding="utf-8"))
        if saved_config != settings:
            raise RuntimeError(f"Resume protocol fingerprint differs: {out}")
        checkpoint = torch.load(last_path, map_location="cpu", weights_only=False)
        if checkpoint["config"] != settings:
            raise RuntimeError(f"Last checkpoint protocol fingerprint differs: {last_path}")
        model.load_state_dict(checkpoint["model_state"], strict=True)
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        for state in optimizer.state.values():
            for key, value in state.items():
                if isinstance(value, torch.Tensor):
                    state[key] = value.to(device)
        restore_rng_state(checkpoint["rng_state"], sampler_generator)
        next_epoch = checkpoint["epoch"] + 1
        best_ap50 = checkpoint["best_ap50"]
        best_epoch = checkpoint["best_epoch"]
        print(f"RESUME {out}: epoch {next_epoch}/{EPOCHS}, "
              f"best_epoch={best_epoch}, best_AP50={best_ap50:.6f}", flush=True)
    else:
        if out.exists():
            raise RuntimeError(f"Refusing to overwrite nonempty run directory: {out}")
        weights.mkdir(parents=True)
        atomic_json(config_path, settings)
        next_epoch, best_ap50, best_epoch = 1, -1.0, 0

    for epoch in range(next_epoch, EPOCHS + 1):
        train_loss, train_seconds, steps = train_epoch(model, train_loader, optimizer,
                                                      device, epoch)
        val_start = time.monotonic()
        metrics = evaluate(model, val_loader, device)
        if metrics["images"] != 1200 or metrics["gt_boxes"] != 13781:
            raise RuntimeError(f"Validation coverage mismatch: {metrics}")
        val_seconds = time.monotonic() - val_start
        improved = should_update_best(metrics["ap50"], best_ap50)
        if improved:
            best_ap50, best_epoch = metrics["ap50"], epoch
            atomic_torch(best_path, {"epoch": epoch, "model_state": model.state_dict(),
                                     "metrics": metrics, "config": settings})
        atomic_torch(last_path, {"epoch": epoch, "model_state": model.state_dict(),
                                 "optimizer_state": optimizer.state_dict(),
                                 "rng_state": rng_state(sampler_generator),
                                 "best_ap50": best_ap50, "best_epoch": best_epoch,
                                 "metrics": metrics, "config": settings})
        row = {"epoch": epoch, "train_loss": train_loss,
               "train_seconds": train_seconds, "val_seconds": val_seconds,
               "val_AP": metrics["ap50_95"], "val_AP50": metrics["ap50"],
               "val_AP75": metrics["ap75"], "val_AR100": metrics["ar100"],
               "best_epoch": best_epoch, "best_AP50": best_ap50}
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row) + "\n")
        atomic_json(status_path, {"status": "COMPLETE" if epoch == EPOCHS else "RUNNING",
                                  "model": args.model, "seed": args.seed,
                                  "completed_epochs": epoch, "total_epochs": EPOCHS,
                                  "best_epoch": best_epoch, "best_AP50": best_ap50,
                                  "last_epoch_metrics": metrics,
                                  "best_checkpoint_sha256": sha256(best_path)})
        print(f"epoch={epoch}/{EPOCHS} AP={metrics['ap50_95']:.6f} "
              f"AP50={metrics['ap50']:.6f} AP75={metrics['ap75']:.6f} "
              f"AR100={metrics['ar100']:.6f} best_epoch={best_epoch} "
              f"train_sec={train_seconds:.1f} val_sec={val_seconds:.1f}", flush=True)
    print(f"TRAINING_COMPLETE model={args.model} seed={args.seed} "
          f"best_epoch={best_epoch} best_AP50={best_ap50:.6f}", flush=True)


if __name__ == "__main__":
    main()
