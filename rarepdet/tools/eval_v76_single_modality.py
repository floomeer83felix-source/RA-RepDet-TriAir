#!/usr/bin/env python
"""Evaluate one V76 single-modality checkpoint with the frozen COCO metric contract."""

from __future__ import annotations

import argparse
import hashlib
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
from rarepdet.coco_metrics import coco_detection_metrics
from rarepdet.data import DetectionTriAirDataset
from rarepdet.experimental.v76_single_modality_detector import build_v76_single_modality_detector


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-mode", choices=("rgb", "thermal", "event"), required=True)
    parser.add_argument("--seed", type=int, choices=(0, 1, 2), required=True)
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--device", default="cuda")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device(args.device)
    if device.type != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("V76 standardized evaluation requires CUDA.")
    dataset = DetectionTriAirDataset(args.data, split_file=args.split_file, mode=args.input_mode, train=False, modality_dropout=0.0)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers, collate_fn=collate_fn, pin_memory=True)
    model = build_v76_single_modality_detector(args.input_mode, img_size=args.img_size, score_thresh=0.001, nms_thresh=0.6, detections_per_img=100).to(device)
    weights = Path(args.weights)
    checkpoint = torch.load(weights, map_location="cpu", weights_only=False)
    cfg = checkpoint.get("model_cfg", {})
    if cfg.get("input_mode") != args.input_mode:
        raise RuntimeError(f"checkpoint input_mode mismatch: {cfg.get('input_mode')} vs {args.input_mode}")
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.eval()

    predictions, targets = [], []
    started = time.time()
    with torch.inference_mode():
        for images, batch_targets in loader:
            outputs = model([image.to(device, non_blocking=True) for image in images])
            predictions.extend({key: value.detach().cpu() for key, value in item.items()} for item in outputs)
            targets.extend({key: value.detach().cpu() for key, value in item.items()} for item in batch_targets)
    metrics = coco_detection_metrics(predictions, targets, score_thresh=0.001, max_detections=100)
    metrics.update({"run_id": f"{args.input_mode}_seed{args.seed}", "input_mode": args.input_mode, "seed": args.seed, "checkpoint_epoch": checkpoint.get("epoch"), "checkpoint_sha256": sha256(weights), "weights": str(weights), "split_file": str(Path(args.split_file)), "split_sha256": sha256(Path(args.split_file)), "inference_and_metric_seconds": time.time() - started, "selection_rule": "best development-validation project-local AP50 checkpoint, then one COCO evaluation", "guard_used": False})
    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
