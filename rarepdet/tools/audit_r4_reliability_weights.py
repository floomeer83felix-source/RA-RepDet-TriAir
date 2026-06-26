#!/usr/bin/env python
"""Audit R4 reliability alpha weights under synthetic modality removal."""

import argparse
import csv
from collections import Counter
from datetime import datetime
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


RUNS = [
    ("R4 Reliability p=0.20", "0", "runs/R4_reliability_p020_seed0_block64g16_e50/weights/best.pt"),
    ("R4 Reliability p=0.20", "2", "runs/R4_reliability_p020_seed2_block64g16_e50/weights/best.pt"),
]

MODES = ("full", "no_rgb", "no_thermal", "no_event")
HEADERS = [
    "Variant",
    "Seed",
    "Mode",
    "Samples",
    "alpha_rgb_mean",
    "alpha_rgb_std",
    "alpha_thermal_mean",
    "alpha_thermal_std",
    "alpha_event_mean",
    "alpha_event_std",
    "alpha_sum_mean",
    "alpha_sum_std",
    "alpha_sum_min",
    "alpha_sum_max",
    "finite_values",
    "dominant_rgb",
    "dominant_thermal",
    "dominant_event",
]


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def pick_device(requested):
    device = torch.device(requested)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        return torch.device("cpu")
    return device


def load_model(weights, img_size, device):
    checkpoint = torch.load(resolve_path(weights), map_location=device)
    cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type="reliability",
        model_name=cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=cfg.get("img_size", img_size),
        num_classes=cfg.get("num_classes", 2),
        fpn_out_channels=cfg.get("fpn_out_channels", 128),
        score_thresh=0.50,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device).eval()
    return model


def mean_std(values):
    tensor = torch.as_tensor(values, dtype=torch.float32)
    return float(tensor.mean()), float(tensor.std(unbiased=False))


def summarize(records, variant, seed, mode):
    if not records:
        return {
            "Variant": variant,
            "Seed": seed,
            "Mode": mode,
            "Samples": 0,
            **{key: "NA" for key in HEADERS[4:]},
        }
    tensor = torch.tensor(records, dtype=torch.float32)
    sums = tensor.sum(dim=1)
    finite_values = bool(torch.isfinite(tensor).all() and torch.isfinite(sums).all())
    dominant = Counter()
    for row in tensor:
        dominant[("rgb", "thermal", "event")[int(torch.argmax(row).item())]] += 1
    rgb_mean, rgb_std = mean_std(tensor[:, 0])
    th_mean, th_std = mean_std(tensor[:, 1])
    ev_mean, ev_std = mean_std(tensor[:, 2])
    sum_mean, sum_std = mean_std(sums)
    return {
        "Variant": variant,
        "Seed": seed,
        "Mode": mode,
        "Samples": len(records),
        "alpha_rgb_mean": f"{rgb_mean:.6f}",
        "alpha_rgb_std": f"{rgb_std:.6f}",
        "alpha_thermal_mean": f"{th_mean:.6f}",
        "alpha_thermal_std": f"{th_std:.6f}",
        "alpha_event_mean": f"{ev_mean:.6f}",
        "alpha_event_std": f"{ev_std:.6f}",
        "alpha_sum_mean": f"{sum_mean:.6f}",
        "alpha_sum_std": f"{sum_std:.6f}",
        "alpha_sum_min": f"{float(sums.min()):.6f}",
        "alpha_sum_max": f"{float(sums.max()):.6f}",
        "finite_values": str(finite_values).lower(),
        "dominant_rgb": dominant["rgb"],
        "dominant_thermal": dominant["thermal"],
        "dominant_event": dominant["event"],
    }


def collect_records(model, loader, mode, device):
    records = []
    with torch.no_grad():
        for images, _ in loader:
            device_images = [apply_missing_mode(image, mode).to(device, non_blocking=True) for image in images]
            _ = model(device_images)
            alpha = model.backbone.last_alpha.detach().float().cpu()
            records.extend(alpha.tolist())
    return records


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def md_table(rows):
    lines = [
        "| " + " | ".join(HEADERS) + " |",
        "| " + " | ".join(["---"] * len(HEADERS)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "NA")) for header in HEADERS) + " |")
    return lines


def write_md(path, rows):
    lines = [
        "# R4 Reliability Weight Audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This is a gating-behavior audit under synthetic modality removal. It does not claim causal physical modality importance.",
        "",
        "Absent modalities are zeroed in the input tensor. Do not claim exact zero absent-modality weights unless the observed values are exactly zero.",
        "",
    ]
    lines.extend(md_table(rows))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Audit R4 reliability weights.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"runs\blocked_split_candidates\block64_guard16_seed0_val.txt")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--out-dir", default="runs")
    args = parser.parse_args()

    device = pick_device(args.device)
    dataset = DetectionTriAirDataset(args.data, split_file=resolve_path(args.split_file), mode="rgbte", train=False)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )

    rows = []
    for variant, seed, weights in RUNS:
        model = load_model(weights, args.img_size, device)
        for mode in MODES:
            records = collect_records(model, loader, mode, device)
            row = summarize(records, variant, seed, mode)
            rows.append(row)
            print(
                f"{variant} seed={seed} {mode}: "
                f"rgb={row['alpha_rgb_mean']} thermal={row['alpha_thermal_mean']} event={row['alpha_event_mean']}"
            )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    out_dir = resolve_path(args.out_dir)
    csv_path = out_dir / "r4_reliability_weight_audit.csv"
    md_path = out_dir / "r4_reliability_weight_audit.md"
    write_csv(csv_path, rows)
    write_md(md_path, rows)
    print(f"Saved: {csv_path}")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()
