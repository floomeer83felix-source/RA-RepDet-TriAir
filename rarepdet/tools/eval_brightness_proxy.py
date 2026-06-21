#!/usr/bin/env python
"""Evaluate E0/E1/E2 by RGB brightness-proxy groups."""

import argparse
import csv
from pathlib import Path
import sys

import torch
from torch.utils.data import DataLoader, Subset


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.metrics import detection_metrics
from rarepdet.models.early_fusion_fcos import build_detector
from phase2a_common import RUNS, f1_score, pick_device, resolve_path


GROUPS = ("brightness_low", "brightness_mid", "brightness_high")


def load_model(run, img_size, device, score_floor):
    weights = resolve_path(run["weights"])
    checkpoint = torch.load(weights, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type=run["model"],
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        score_thresh=score_floor,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device).eval()
    return model


def compute_brightness_groups(dataset):
    records = []
    for index in range(len(dataset)):
        image, _ = dataset[index]
        records.append((index, float(image[0:3].mean())))
    records.sort(key=lambda item: item[1])
    n = len(records)
    cuts = [n // 3, (2 * n) // 3]
    groups = {
        GROUPS[0]: records[: cuts[0]],
        GROUPS[1]: records[cuts[0] : cuts[1]],
        GROUPS[2]: records[cuts[1] :],
    }
    return groups


def evaluate_subset(model, dataset, indices, args, device):
    subset = Subset(dataset, indices)
    loader = DataLoader(
        subset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )
    predictions = []
    targets_cpu = []
    with torch.no_grad():
        for images, targets in loader:
            images = [image.to(device, non_blocking=True) for image in images]
            outputs = model(images)
            predictions.extend([{k: v.detach().cpu() for k, v in output.items()} for output in outputs])
            targets_cpu.extend([{k: v.detach().cpu() for k, v in target.items()} for target in targets])
    metrics = detection_metrics(predictions, targets_cpu, score_thresh=args.score_thr)
    metrics["f1"] = f1_score(metrics["precision"], metrics["recall"])
    return metrics


def write_outputs(rows, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "brightness_proxy_results.csv"
    txt_path = out_dir / "brightness_proxy_results.txt"
    headers = [
        "Method",
        "Group",
        "Images",
        "Brightness min",
        "Brightness max",
        "Brightness mean",
        "Precision",
        "Recall",
        "F1",
        "AP50",
        "AP75",
        "GT boxes",
        "Predictions",
        "Mean Confidence",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    with txt_path.open("w", encoding="utf-8") as f:
        f.write("Brightness-proxy grouped evaluation\n")
        f.write("===================================\n\n")
        f.write("Groups are RGB mean-intensity terciles and are not day/night labels.\n\n")
        f.write(" | ".join(headers) + "\n")
        f.write(" | ".join(["---"] * len(headers)) + "\n")
        for row in rows:
            f.write(" | ".join(str(row[h]) for h in headers) + "\n")
    return csv_path, txt_path


def main():
    parser = argparse.ArgumentParser(description="Evaluate brightness-proxy groups.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--score-thr", default=0.50, type=float)
    parser.add_argument("--out", default="runs/phase2a_brightness_proxy")
    args = parser.parse_args()

    device = pick_device(args.device)
    dataset = DetectionTriAirDataset(args.data, split_file=args.split_file, mode="rgbte", train=False)
    groups = compute_brightness_groups(dataset)

    rows = []
    for run in RUNS:
        print(f"Evaluating {run['method']}")
        model = load_model(run, args.img_size, device, score_floor=min(args.score_thr, 0.001))
        for group_name in GROUPS:
            records = groups[group_name]
            indices = [index for index, _ in records]
            values = [value for _, value in records]
            metrics = evaluate_subset(model, dataset, indices, args, device)
            row = {
                "Method": run["method"],
                "Group": group_name,
                "Images": len(indices),
                "Brightness min": f"{min(values):.6f}",
                "Brightness max": f"{max(values):.6f}",
                "Brightness mean": f"{sum(values) / max(len(values), 1):.6f}",
                "Precision": f"{metrics['precision']:.6f}",
                "Recall": f"{metrics['recall']:.6f}",
                "F1": f"{metrics['f1']:.6f}",
                "AP50": f"{metrics['ap50']:.6f}",
                "AP75": f"{metrics['ap75']:.6f}",
                "GT boxes": metrics["gt_boxes"],
                "Predictions": metrics["predictions"],
                "Mean Confidence": f"{metrics['mean_confidence']:.6f}",
            }
            rows.append(row)
            print(
                f"  {group_name}: P={row['Precision']} R={row['Recall']} "
                f"F1={row['F1']} AP50={row['AP50']}"
            )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    paths = write_outputs(rows, resolve_path(args.out))
    for path in paths:
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()

