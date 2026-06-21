#!/usr/bin/env python
"""Analyze reliability alpha weights under selected missing-modality modes."""

import argparse
import csv
from collections import Counter
from pathlib import Path
import sys

import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.models.early_fusion_fcos import build_detector
from rarepdet.tools.eval_missing_modality import apply_missing_mode
from phase2a_common import pick_device, resolve_path


RUNS = (
    {
        "method": "E1 Reliability Fusion",
        "weights": "runs/E1_reliability_repvit_fcos_e50/weights/best.pt",
    },
    {
        "method": "E2 Reliability + Dropout 0.15",
        "weights": "runs/E2_reliability_dropout015_repvit_fcos_e50/weights/best.pt",
    },
)
MODES = ("full", "no_rgb", "no_thermal", "no_event")


def load_model(weights, img_size, device):
    checkpoint = torch.load(resolve_path(weights), map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type="reliability",
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        score_thresh=0.50,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device).eval()
    return model


def mean_std(values):
    if not values:
        return 0.0, 0.0
    tensor = torch.tensor(values, dtype=torch.float32)
    return float(tensor.mean()), float(tensor.std(unbiased=False))


def summarize_alpha(records):
    dominant = Counter()
    for item in records:
        values = [item["alpha_rgb"], item["alpha_thermal"], item["alpha_event"]]
        dominant[("rgb", "thermal", "event")[int(torch.tensor(values).argmax())]] += 1
    rgb_mean, rgb_std = mean_std([item["alpha_rgb"] for item in records])
    thermal_mean, thermal_std = mean_std([item["alpha_thermal"] for item in records])
    event_mean, event_std = mean_std([item["alpha_event"] for item in records])
    total = max(len(records), 1)
    return {
        "Samples": len(records),
        "alpha_rgb_mean": f"{rgb_mean:.6f}",
        "alpha_rgb_std": f"{rgb_std:.6f}",
        "alpha_thermal_mean": f"{thermal_mean:.6f}",
        "alpha_thermal_std": f"{thermal_std:.6f}",
        "alpha_event_mean": f"{event_mean:.6f}",
        "alpha_event_std": f"{event_std:.6f}",
        "dominant_rgb": dominant["rgb"],
        "dominant_thermal": dominant["thermal"],
        "dominant_event": dominant["event"],
        "dominant_rgb_ratio": f"{dominant['rgb'] / total:.6f}",
        "dominant_thermal_ratio": f"{dominant['thermal'] / total:.6f}",
        "dominant_event_ratio": f"{dominant['event'] / total:.6f}",
    }


def evaluate_mode(model, loader, mode, device):
    records = []
    with torch.no_grad():
        for images, _ in loader:
            images = [apply_missing_mode(image, mode).to(device, non_blocking=True) for image in images]
            _ = model(images)
            alpha = model.backbone.last_alpha.detach().float().cpu()
            for row in alpha:
                records.append(
                    {
                        "alpha_rgb": float(row[0]),
                        "alpha_thermal": float(row[1]),
                        "alpha_event": float(row[2]),
                    }
                )
    return records


def write_outputs(summary_rows, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "alpha_mode_summary.csv"
    txt_path = out_dir / "alpha_mode_summary.txt"
    headers = list(summary_rows[0].keys()) if summary_rows else []
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(summary_rows)
    with txt_path.open("w", encoding="utf-8") as f:
        f.write("Reliability alpha mode summary\n")
        f.write("==============================\n\n")
        f.write(" | ".join(headers) + "\n")
        f.write(" | ".join(["---"] * len(headers)) + "\n")
        for row in summary_rows:
            f.write(" | ".join(str(row[h]) for h in headers) + "\n")
    return csv_path, txt_path


def main():
    parser = argparse.ArgumentParser(description="Analyze reliability alpha modes.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--out", default="runs/phase2a_alpha")
    args = parser.parse_args()

    device = pick_device(args.device)
    dataset = DetectionTriAirDataset(args.data, split_file=args.split_file, mode="rgbte", train=False)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )

    summary_rows = []
    for run in RUNS:
        print(f"Analyzing {run['method']}")
        model = load_model(run["weights"], args.img_size, device)
        for mode in MODES:
            records = evaluate_mode(model, loader, mode, device)
            summary = summarize_alpha(records)
            summary_rows.append({"Method": run["method"], "Mode": mode, **summary})
            print(
                f"  {mode}: rgb={summary['alpha_rgb_mean']} "
                f"thermal={summary['alpha_thermal_mean']} event={summary['alpha_event_mean']}"
            )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    paths = write_outputs(summary_rows, resolve_path(args.out))
    for path in paths:
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()

