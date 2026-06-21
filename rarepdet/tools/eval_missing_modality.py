#!/usr/bin/env python
"""Evaluate detector robustness under missing RGB/Thermal/Event modalities."""

import argparse
import csv
from pathlib import Path
import sys

import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.metrics import detection_metrics
from rarepdet.models.early_fusion_fcos import build_detector


MODES = ("full", "no_rgb", "no_thermal", "no_event", "rgb_only", "thermal_only", "event_only")


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def apply_missing_mode(image, mode):
    image = image.clone()
    if mode == "full":
        return image
    if mode == "no_rgb":
        image[0:3] = 0
    elif mode == "no_thermal":
        image[3:4] = 0
    elif mode == "no_event":
        image[4:5] = 0
    elif mode == "rgb_only":
        image[3:5] = 0
    elif mode == "thermal_only":
        image[0:3] = 0
        image[4:5] = 0
    elif mode == "event_only":
        image[0:4] = 0
    else:
        raise ValueError(f"Unknown missing-modality mode: {mode}")
    return image


def load_model(args, device):
    checkpoint = torch.load(resolve_path(args.weights), map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model_type = args.model or model_cfg.get("model_type", "early")
    model = build_detector(
        model_type=model_type,
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", args.img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        score_thresh=args.score_thr,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device)
    model.eval()
    return model, model_type


def evaluate_mode(model, loader, device, mode, score_thr):
    predictions = []
    targets_cpu = []
    with torch.no_grad():
        for images, targets in loader:
            images = [apply_missing_mode(image, mode).to(device, non_blocking=True) for image in images]
            outputs = model(images)
            predictions.extend([{k: v.detach().cpu() for k, v in output.items()} for output in outputs])
            targets_cpu.extend([{k: v.detach().cpu() for k, v in target.items()} for target in targets])
    return detection_metrics(predictions, targets_cpu, score_thresh=score_thr)


def write_outputs(rows, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / "missing_modality_results.txt"
    csv_path = out_dir / "missing_modality_results.csv"
    headers = ["Mode", "Precision", "Recall", "AP50", "AP75", "GT boxes", "Predictions", "Mean Confidence"]

    with txt_path.open("w", encoding="utf-8") as f:
        f.write(" | ".join(headers) + "\n")
        f.write(" | ".join(["---"] * len(headers)) + "\n")
        for row in rows:
            f.write(
                f"{row['Mode']} | {row['Precision']:.6f} | {row['Recall']:.6f} | "
                f"{row['AP50']:.6f} | {row['AP75']:.6f} | {row['GT boxes']} | "
                f"{row['Predictions']} | {row['Mean Confidence']:.6f}\n"
            )

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return txt_path, csv_path


def main():
    parser = argparse.ArgumentParser(description="Evaluate missing-modality robustness.")
    parser.add_argument("--model", choices=("early", "reliability"), default=None)
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--score-thr", "--score-thresh", dest="score_thr", default=0.001, type=float)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        device = torch.device("cpu")

    model, model_type = load_model(args, device)
    dataset = DetectionTriAirDataset(args.data, split_file=args.split_file, mode="rgbte", train=False)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )

    rows = []
    for mode in MODES:
        metrics = evaluate_mode(model, loader, device, mode, args.score_thr)
        row = {
            "Mode": mode,
            "Precision": metrics["precision"],
            "Recall": metrics["recall"],
            "AP50": metrics["ap50"],
            "AP75": metrics["ap75"],
            "GT boxes": metrics["gt_boxes"],
            "Predictions": metrics["predictions"],
            "Mean Confidence": metrics["mean_confidence"],
        }
        rows.append(row)
        print(
            f"{model_type} {mode}: Precision={row['Precision']:.4f} Recall={row['Recall']:.4f} "
            f"AP50={row['AP50']:.4f} AP75={row['AP75']:.4f}"
        )

    txt_path, csv_path = write_outputs(rows, resolve_path(args.out))
    print(f"Saved: {txt_path}")
    print(f"Saved: {csv_path}")


if __name__ == "__main__":
    main()
