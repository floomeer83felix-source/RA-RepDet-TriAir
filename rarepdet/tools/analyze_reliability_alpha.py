#!/usr/bin/env python
"""Analyze reliability alpha weights on the validation split."""

import argparse
import csv
from collections import Counter
from pathlib import Path
import random
import sys

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.data import DetectionTriAirDataset, get_sample_info
from rarepdet.models.early_fusion_fcos import build_detector


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def get_alpha(model):
    alpha = getattr(model.backbone, "last_alpha", None)
    if alpha is None:
        raise RuntimeError("Model did not expose backbone.last_alpha; use --model reliability.")
    return alpha.detach().float().mean(dim=0).cpu().tolist()


def mean_std(values):
    if not values:
        return 0.0, 0.0
    tensor = torch.tensor(values, dtype=torch.float32)
    return float(tensor.mean()), float(tensor.std(unbiased=False))


def write_plot(rows, out_dir):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"WARNING: matplotlib unavailable, skipping plot: {exc}")
        return

    plt.figure(figsize=(8, 5))
    plt.hist([row["alpha_rgb"] for row in rows], bins=30, alpha=0.55, label="RGB")
    plt.hist([row["alpha_thermal"] for row in rows], bins=30, alpha=0.55, label="Thermal")
    plt.hist([row["alpha_event"] for row in rows], bins=30, alpha=0.55, label="Event")
    plt.xlabel("Reliability alpha")
    plt.ylabel("Image count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "alpha_distribution.png", dpi=180)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Analyze reliability alpha weights.")
    parser.add_argument("--model", default="reliability", choices=("reliability",))
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--num-samples", default=1000, type=int)
    parser.add_argument("--seed", default=20260617, type=int)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        device = torch.device("cpu")

    checkpoint = torch.load(resolve_path(args.weights), map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type="reliability",
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", args.img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device).eval()

    dataset = DetectionTriAirDataset(args.data, split_file=args.split_file, mode="rgbte", train=False)
    indices = list(range(len(dataset)))
    random.Random(args.seed).shuffle(indices)
    indices = indices[: min(args.num_samples, len(indices))]

    rows = []
    with torch.no_grad():
        for index in indices:
            image, target = dataset[index]
            _ = model([image.to(device)])
            alpha = get_alpha(model)
            info = get_sample_info(dataset, index)
            rows.append(
                {
                    "file_name": info["image_path"].name,
                    "alpha_rgb": alpha[0],
                    "alpha_thermal": alpha[1],
                    "alpha_event": alpha[2],
                    "gt_boxes": int(target["boxes"].shape[0]),
                    "mean_rgb_brightness": float(image[0:3].mean()),
                    "mean_thermal_intensity": float(image[3:4].mean()),
                    "mean_event_intensity": float(image[4:5].mean()),
                }
            )

    out_dir = resolve_path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "alpha_records.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)

    rgb_mean, rgb_std = mean_std([row["alpha_rgb"] for row in rows])
    th_mean, th_std = mean_std([row["alpha_thermal"] for row in rows])
    ev_mean, ev_std = mean_std([row["alpha_event"] for row in rows])
    dominant = Counter()
    for row in rows:
        values = [row["alpha_rgb"], row["alpha_thermal"], row["alpha_event"]]
        dominant[("rgb", "thermal", "event")[int(torch.tensor(values).argmax())]] += 1

    summary_path = out_dir / "alpha_summary.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write(f"samples: {len(rows)}\n")
        f.write(f"mean alpha_rgb: {rgb_mean:.6f}\n")
        f.write(f"mean alpha_thermal: {th_mean:.6f}\n")
        f.write(f"mean alpha_event: {ev_mean:.6f}\n")
        f.write(f"std alpha_rgb: {rgb_std:.6f}\n")
        f.write(f"std alpha_thermal: {th_std:.6f}\n")
        f.write(f"std alpha_event: {ev_std:.6f}\n")
        for name in ("rgb", "thermal", "event"):
            ratio = dominant[name] / max(len(rows), 1)
            f.write(f"dominant {name}: {dominant[name]} ({ratio:.6f})\n")

    write_plot(rows, out_dir)
    print(f"Saved: {csv_path}")
    print(f"Saved: {summary_path}")


if __name__ == "__main__":
    main()
