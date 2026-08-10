#!/usr/bin/env python
"""Evaluate one retained V84 RGB+thermal checkpoint with canonical COCO metrics."""

from __future__ import annotations

import argparse
import hashlib
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
from rarepdet.coco_metrics import coco_detection_metrics
from rarepdet.data import DetectionTriAirDataset
from rarepdet.models.early_fusion_fcos import build_early_fusion_fcos


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, choices=(0, 1, 2), required=True)
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    device = torch.device(args.device)
    if device.type != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("V84 RGB+thermal evaluation requires CUDA")
    weights = Path(args.weights)
    split = Path(args.split_file)
    checkpoint = torch.load(weights, map_location="cpu", weights_only=False)
    cfg = checkpoint.get("model_cfg", {})
    if cfg.get("experiment") != "V84_RGB_THERMAL_BASELINE" or cfg.get("input_mode") != "rgbt" or cfg.get("in_chans") != 4:
        raise RuntimeError("checkpoint is not an exact V84 RGB+thermal checkpoint")
    if checkpoint.get("train_args", {}).get("seed") != args.seed:
        raise RuntimeError("checkpoint seed mismatch")
    model = build_early_fusion_fcos(in_chans=4, img_size=640, score_thresh=0.001, nms_thresh=0.6, detections_per_img=100).to(device)
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.eval()
    dataset = DetectionTriAirDataset(args.data, split_file=split, mode="rgbt", train=False, modality_dropout=0.0)
    loader = DataLoader(dataset, batch_size=4, shuffle=False, num_workers=0, collate_fn=collate_fn, pin_memory=True)
    predictions, targets = [], []
    started = time.time()
    with torch.inference_mode():
        for images, batch_targets in loader:
            outputs = model([image.to(device, non_blocking=True) for image in images])
            predictions.extend({key: value.detach().cpu() for key, value in item.items()} for item in outputs)
            targets.extend({key: value.detach().cpu() for key, value in item.items()} for item in batch_targets)
    metrics = coco_detection_metrics(predictions, targets, score_thresh=0.0, max_detections=100)
    metrics.update({"run_id": f"rgbt_seed{args.seed}", "input_mode": "rgbt", "seed": args.seed, "checkpoint_epoch": checkpoint["epoch"], "checkpoint_sha256": sha256(weights), "weights": str(weights), "split_file": str(split), "split_sha256": sha256(split), "inference_and_metric_seconds": time.time() - started, "selection_rule": "highest development-validation project-local AP50, then one standardized COCO evaluation", "guard_used": False})
    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
