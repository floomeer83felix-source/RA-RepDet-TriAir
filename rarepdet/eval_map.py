#!/usr/bin/env python
"""Evaluate RarePDet checkpoints without pycocotools."""

import argparse
from pathlib import Path
import sys
import time

import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.metrics import detection_metrics, format_metrics
from rarepdet.models.availability_reliability_fusion_fcos import build_availability_reliability_fcos
from rarepdet.models.early_fusion_fcos import build_detector


def resolve_path(path):
    path = Path(path)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def evaluate_checkpoint(args):
    requested_device = torch.device(args.device)
    if requested_device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but not available. Falling back to CPU.")
        requested_device = torch.device("cpu")
    device = requested_device
    print(f"Using device: {device}")

    weights = resolve_path(args.weights)
    if not weights.is_file():
        raise FileNotFoundError(f"Weights not found: {weights}")

    checkpoint = torch.load(weights, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model_type = args.model or model_cfg.get("model_type", "early")
    if model_type == "availability_reliability":
        model = build_availability_reliability_fcos(
            model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
            img_size=model_cfg.get("img_size", args.img_size),
            num_classes=model_cfg.get("num_classes", 2),
            fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
            score_thresh=min(args.score_thresh, 0.2),
        )
    else:
        model = build_detector(
            model_type=model_type,
            model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
            img_size=model_cfg.get("img_size", args.img_size),
            num_classes=model_cfg.get("num_classes", 2),
            fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
            score_thresh=min(args.score_thresh, 0.2),
        )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device)
    model.eval()

    dataset = DetectionTriAirDataset(
        args.data,
        split_file=args.split_file,
        mode="rgbte",
        train=False,
        modality_dropout=0.0,
    )
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )

    predictions = []
    targets_cpu = []
    start = time.time()
    with torch.no_grad():
        for images, targets in loader:
            device_images = [image.to(device, non_blocking=True) for image in images]
            outputs = model(device_images)
            predictions.extend([{key: value.detach().cpu() for key, value in output.items()} for output in outputs])
            targets_cpu.extend([{key: value.detach().cpu() for key, value in target.items()} for target in targets])

    metrics = detection_metrics(predictions, targets_cpu, score_thresh=args.score_thresh)
    elapsed = max(time.time() - start, 1e-6)
    metrics["fps"] = len(dataset) / elapsed
    metrics["images"] = len(dataset)
    metrics["weights"] = str(weights)
    metrics["model"] = model_type
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate RarePDet AP without pycocotools.")
    parser.add_argument("--model", default=None, choices=("early", "reliability", "availability_reliability"), help="Override model type")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--weights", default="runs/rarepdet_early/best.pt")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=2, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--score-thresh", "--score-thr", dest="score_thresh", default=0.05, type=float)
    parser.add_argument("--out", default="runs/rarepdet_early/eval_results.txt")
    args = parser.parse_args()

    metrics = evaluate_checkpoint(args)
    result_text = (
        "RarePDet eval results\n"
        "====================\n"
        f"model: {metrics['model']}\n"
        f"weights: {metrics['weights']}\n"
        f"images: {metrics['images']}\n"
        f"Precision: {metrics['precision']:.6f}\n"
        f"Recall: {metrics['recall']:.6f}\n"
        f"AP50: {metrics['ap50']:.6f}\n"
        f"AP75: {metrics['ap75']:.6f}\n"
        f"GT boxes: {metrics['gt_boxes']}\n"
        f"Predictions: {metrics['predictions']}\n"
        f"Mean Confidence: {metrics['mean_confidence']:.6f}\n"
        f"FPS: {metrics['fps']:.2f}\n"
    )
    print(result_text)

    out_path = resolve_path(args.out)
    if out_path.suffix.lower() != ".txt":
        out_path = out_path / "eval_results.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result_text, encoding="utf-8")
    print(f"Saved eval results to: {out_path}")


if __name__ == "__main__":
    main()
