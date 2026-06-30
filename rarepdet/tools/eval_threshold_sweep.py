#!/usr/bin/env python
"""Sweep score thresholds for E0/E1/E2 RarePDet checkpoints.

This is an evaluation-only script. It does not modify training code or weights.
"""

import argparse
import csv
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
from rarepdet.metrics import average_precision, precision_recall
from rarepdet.models.early_fusion_fcos import build_detector


DEFAULT_THRESHOLDS = (0.001, 0.01, 0.03, 0.05, 0.10, 0.20, 0.30, 0.50)

RUNS = (
    {
        "method": "E0 Early Fusion",
        "model": "early",
        "weights_arg": "weights_e0",
        "default_weights": "runs/E0_early_repvit_fcos_e50/weights/best.pt",
    },
    {
        "method": "E1 Reliability Fusion",
        "model": "reliability",
        "weights_arg": "weights_e1",
        "default_weights": "runs/E1_reliability_repvit_fcos_e50/weights/best.pt",
    },
    {
        "method": "E2 Reliability + Dropout 0.15",
        "model": "reliability",
        "weights_arg": "weights_e2",
        "default_weights": "runs/E2_reliability_dropout015_repvit_fcos_e50/weights/best.pt",
    },
)


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def count_thresholded_predictions(predictions, score_thr):
    scores_kept = []
    count = 0
    for pred in predictions:
        scores = pred["scores"]
        labels = pred["labels"]
        keep = (labels == 1) & (scores >= score_thr)
        kept_scores = scores[keep]
        count += int(kept_scores.numel())
        if kept_scores.numel() > 0:
            scores_kept.append(kept_scores)
    if scores_kept:
        mean_conf = float(torch.cat(scores_kept).mean())
    else:
        mean_conf = 0.0
    return count, mean_conf


def count_gt_boxes(targets):
    total = 0
    for target in targets:
        total += int((target["labels"] == 1).sum().item())
    return total


def f1_score(precision, recall):
    denom = precision + recall
    if denom <= 0:
        return 0.0
    return 2.0 * precision * recall / denom


def load_model(run, weights, img_size, score_floor, device):
    weights = resolve_path(weights)
    if not weights.is_file():
        raise FileNotFoundError(f"Missing weights for {run['method']}: {weights}")

    checkpoint = torch.load(weights, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type=run["model"],
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        # Keep the detector output floor at the lowest swept threshold so all
        # higher-threshold metrics are computed from the same prediction pool.
        score_thresh=score_floor,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device)
    model.eval()
    return model, weights


def run_inference(model, loader, device):
    predictions = []
    targets_cpu = []
    start = time.time()
    with torch.no_grad():
        for images, targets in loader:
            images = [image.to(device, non_blocking=True) for image in images]
            outputs = model(images)
            predictions.extend([{key: value.detach().cpu() for key, value in output.items()} for output in outputs])
            targets_cpu.extend([{key: value.detach().cpu() for key, value in target.items()} for target in targets])
    elapsed = time.time() - start
    return predictions, targets_cpu, elapsed


def evaluate_run(run, weights, dataset, loader, thresholds, img_size, device):
    score_floor = min(thresholds)
    model, weights_path = load_model(run, weights, img_size, score_floor, device)
    print(f"Running inference: {run['method']} ({weights_path})")
    predictions, targets, elapsed = run_inference(model, loader, device)
    print(f"  inference done: {len(dataset)} images in {elapsed:.1f}s")

    gt_boxes = count_gt_boxes(targets)
    ap50 = average_precision(predictions, targets, iou_thresh=0.50)
    ap75 = average_precision(predictions, targets, iou_thresh=0.75)

    rows = []
    for thr in thresholds:
        precision, recall = precision_recall(predictions, targets, iou_thresh=0.50, score_thresh=thr)
        predictions_count, mean_conf = count_thresholded_predictions(predictions, thr)
        f1 = f1_score(precision, recall)
        row = {
            "Method": run["method"],
            "Model": run["model"],
            "Weights": str(weights_path),
            "Threshold": thr,
            "Precision": precision,
            "Recall": recall,
            "F1": f1,
            "AP50": ap50,
            "AP75": ap75,
            "GT boxes": gt_boxes,
            "Predictions": predictions_count,
            "Mean Confidence": mean_conf,
        }
        rows.append(row)
        print(
            f"  thr={thr:.3f} P={precision:.4f} R={recall:.4f} "
            f"F1={f1:.4f} preds={predictions_count}"
        )
    return rows


def write_outputs(rows, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "threshold_sweep_results.csv"
    txt_path = out_dir / "threshold_sweep_results.txt"
    fieldnames = [
        "Method",
        "Model",
        "Weights",
        "Threshold",
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
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    methods = []
    for row in rows:
        if row["Method"] not in methods:
            methods.append(row["Method"])

    summary_rows = []
    for method in methods:
        method_rows = [row for row in rows if row["Method"] == method]
        best = max(method_rows, key=lambda row: row["F1"])
        summary_rows.append(best)

    with txt_path.open("w", encoding="utf-8") as f:
        f.write("Threshold sweep results\n")
        f.write("=======================\n\n")
        f.write("Full sweep\n")
        f.write("----------\n")
        f.write(
            "Method | Threshold | Precision | Recall | F1 | AP50 | AP75 | "
            "GT boxes | Predictions | Mean Confidence\n"
        )
        f.write("--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---:\n")
        for row in rows:
            f.write(
                f"{row['Method']} | {row['Threshold']:.3f} | {row['Precision']:.6f} | "
                f"{row['Recall']:.6f} | {row['F1']:.6f} | {row['AP50']:.6f} | "
                f"{row['AP75']:.6f} | {row['GT boxes']} | {row['Predictions']} | "
                f"{row['Mean Confidence']:.6f}\n"
            )
        f.write("\nBest F1 summary\n")
        f.write("----------------\n")
        f.write("Method | Best Threshold | Precision | Recall | F1 | AP50 | AP75 | Predictions\n")
        f.write("--- | ---: | ---: | ---: | ---: | ---: | ---: | ---:\n")
        for row in summary_rows:
            f.write(
                f"{row['Method']} | {row['Threshold']:.3f} | {row['Precision']:.6f} | "
                f"{row['Recall']:.6f} | {row['F1']:.6f} | {row['AP50']:.6f} | "
                f"{row['AP75']:.6f} | {row['Predictions']}\n"
            )

    return csv_path, txt_path, summary_rows


def main():
    parser = argparse.ArgumentParser(description="Sweep score thresholds for E0/E1/E2.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--out", default="runs/threshold_sweep")
    parser.add_argument("--thresholds", nargs="+", type=float, default=list(DEFAULT_THRESHOLDS))
    parser.add_argument("--weights-e0", default=RUNS[0]["default_weights"])
    parser.add_argument("--weights-e1", default=RUNS[1]["default_weights"])
    parser.add_argument("--weights-e2", default=RUNS[2]["default_weights"])
    args = parser.parse_args()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        device = torch.device("cpu")

    thresholds = sorted(set(args.thresholds))
    dataset = DetectionTriAirDataset(args.data, split_file=args.split_file, mode="rgbte", train=False)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )

    all_rows = []
    for run in RUNS:
        weights = getattr(args, run["weights_arg"])
        all_rows.extend(evaluate_run(run, weights, dataset, loader, thresholds, args.img_size, device))
        if device.type == "cuda":
            torch.cuda.empty_cache()

    csv_path, txt_path, summary_rows = write_outputs(all_rows, resolve_path(args.out))
    print(f"Saved: {csv_path}")
    print(f"Saved: {txt_path}")
    print("Best F1 thresholds:")
    for row in summary_rows:
        print(
            f"  {row['Method']}: threshold={row['Threshold']:.3f}, "
            f"F1={row['F1']:.4f}, P={row['Precision']:.4f}, R={row['Recall']:.4f}"
        )


if __name__ == "__main__":
    main()
