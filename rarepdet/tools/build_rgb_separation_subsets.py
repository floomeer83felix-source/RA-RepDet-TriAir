#!/usr/bin/env python
"""Build RGB-separation diagnostic strata and evaluate existing E2/E4 checkpoints."""

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

from datasets.triair_dataset import collate_fn  # noqa: E402
from rarepdet.data import DetectionTriAirDataset  # noqa: E402
from rarepdet.metrics import detection_metrics  # noqa: E402
from rarepdet.models.early_fusion_fcos import build_detector  # noqa: E402
from rarepdet.tools.split_audit_common import (  # noqa: E402
    RUNS_DIR,
    fmt,
    markdown_table,
    read_split_records,
    value_quantiles,
    write_csv,
)


SUMMARY_HEADERS = [
    "subset",
    "model",
    "image_count",
    "gt_boxes",
    "id_distance_min",
    "id_distance_p25",
    "id_distance_p50",
    "id_distance_p75",
    "id_distance_p90",
    "precision",
    "recall",
    "f1",
    "ap50",
    "ap75",
    "predictions",
    "mean_confidence",
    "fps",
    "weights",
    "warning",
]


def read_csv(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_split(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(record["rel_path"] for record in records) + "\n", encoding="utf-8")


def load_nearest_by_val(path):
    rows = read_csv(path)
    return {row["val_path"].replace("\\", "/"): row for row in rows}


def load_exact_rgb_val_paths(path):
    rows = read_csv(path)
    return {row["val_path"].replace("\\", "/") for row in rows if row.get("val_path")}


def to_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def build_strata(data_root, val_split, nearest_csv, exact_pairs_csv):
    val_records = read_split_records(data_root, val_split, "val")
    nearest = load_nearest_by_val(nearest_csv)
    exact_val_paths = load_exact_rgb_val_paths(exact_pairs_csv)
    near = []
    higher = []
    diagnostics = {}

    for record in val_records:
        row = nearest.get(record["rel_path"], {})
        signature_distance = to_int(row.get("signature_distance"))
        id_distance = to_int(row.get("id_distance"))
        exact_match = record["rel_path"] in exact_val_paths
        diagnostics[record["rel_path"]] = {
            "signature_distance": signature_distance,
            "id_distance": id_distance,
            "exact_rgb_match": exact_match,
        }
        if exact_match or (signature_distance is not None and signature_distance <= 4):
            near.append(record)
        if (not exact_match) and signature_distance is not None and signature_distance > 16:
            higher.append(record)
    return val_records, near, higher, diagnostics


def load_detector(weights_path, model_type, device, img_size, score_thresh):
    weights_path = Path(weights_path)
    if not weights_path.exists():
        raise FileNotFoundError(f"Weights not found: {weights_path}")
    checkpoint = torch.load(weights_path, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type=model_type,
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        score_thresh=min(score_thresh, 0.2),
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device)
    model.eval()
    return model


def evaluate_subset(data_root, split_file, weights_path, model_type, device, img_size, batch_size, num_workers, score_thresh):
    dataset = DetectionTriAirDataset(
        data_root,
        split_file=str(split_file),
        mode="rgbte",
        train=False,
        modality_dropout=0.0,
    )
    if len(dataset) == 0:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "ap50": 0.0,
            "ap75": 0.0,
            "gt_boxes": 0,
            "predictions": 0,
            "mean_confidence": 0.0,
            "fps": 0.0,
        }

    model = load_detector(weights_path, model_type, device, img_size, score_thresh)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
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
    elapsed = max(time.time() - start, 1e-6)
    metrics = detection_metrics(predictions, targets_cpu, score_thresh=score_thresh)
    precision = metrics["precision"]
    recall = metrics["recall"]
    metrics["f1"] = 2.0 * precision * recall / max(precision + recall, 1e-12)
    metrics["fps"] = len(dataset) / elapsed
    return metrics


def subset_summary_row(subset_name, records, diagnostics):
    distances = [
        diagnostics[record["rel_path"]]["id_distance"]
        for record in records
        if diagnostics[record["rel_path"]]["id_distance"] is not None
    ]
    q = value_quantiles(distances)
    return {
        "subset": subset_name,
        "model": "subset_only",
        "image_count": len(records),
        "gt_boxes": sum(int(record["gt_boxes"]) for record in records),
        "id_distance_min": fmt(q["min"], digits=0),
        "id_distance_p25": fmt(q["p25"], digits=0),
        "id_distance_p50": fmt(q["p50"], digits=0),
        "id_distance_p75": fmt(q["p75"], digits=0),
        "id_distance_p90": fmt(q["p90"], digits=0),
        "precision": "NA",
        "recall": "NA",
        "f1": "NA",
        "ap50": "NA",
        "ap75": "NA",
        "predictions": "NA",
        "mean_confidence": "NA",
        "fps": "NA",
        "weights": "NA",
        "warning": "",
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate E2/E4 on RGB-separation diagnostic strata.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--val-split", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--nearest-csv", default="runs/split_integrity_nearest_pairs.csv")
    parser.add_argument("--exact-pairs-csv", default="runs/rgb_cross_split_exact_pairs.csv")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--score-thr", default=0.50, type=float)
    parser.add_argument("--out", default="runs")
    parser.add_argument("--e2-weights", default="runs/E2_reliability_dropout015_repvit_fcos_e50/weights/best.pt")
    parser.add_argument("--e4-weights", default="runs/E4_reliability_dropout020_repvit_fcos_e50/weights/best.pt")
    args = parser.parse_args()

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = PROJECT_ROOT / out_dir
    subset_dir = out_dir / "rgb_separation_subsets"

    nearest_csv = Path(args.nearest_csv)
    if not nearest_csv.is_absolute():
        nearest_csv = PROJECT_ROOT / nearest_csv
    exact_pairs_csv = Path(args.exact_pairs_csv)
    if not exact_pairs_csv.is_absolute():
        exact_pairs_csv = PROJECT_ROOT / exact_pairs_csv

    _, near_records, higher_records, diagnostics = build_strata(args.data, args.val_split, nearest_csv, exact_pairs_csv)
    subsets = {
        "near_rgb_match_or_near_neighbor": near_records,
        "higher_rgb_separation": higher_records,
    }
    for subset_name, records in subsets.items():
        write_split(subset_dir / f"{subset_name}.txt", records)

    rows = [subset_summary_row(name, records, diagnostics) for name, records in subsets.items()]

    requested_device = torch.device(args.device)
    if requested_device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but not available. Falling back to CPU.")
        requested_device = torch.device("cpu")
    device = requested_device

    models = [
        ("E2 Reliability + Dropout 0.15", "reliability", Path(args.e2_weights)),
        ("E4 Reliability + Dropout 0.20", "reliability", Path(args.e4_weights)),
    ]
    for method, model_type, weights in models:
        if not weights.is_absolute():
            weights = PROJECT_ROOT / weights
        for subset_name, records in subsets.items():
            base = subset_summary_row(subset_name, records, diagnostics)
            base["model"] = method
            base["weights"] = str(weights)
            split_file = subset_dir / f"{subset_name}.txt"
            try:
                metrics = evaluate_subset(
                    args.data,
                    split_file,
                    weights,
                    model_type,
                    device,
                    args.img_size,
                    args.batch_size,
                    args.num_workers,
                    args.score_thr,
                )
                base.update(
                    {
                        "precision": fmt(metrics["precision"]),
                        "recall": fmt(metrics["recall"]),
                        "f1": fmt(metrics["f1"]),
                        "ap50": fmt(metrics["ap50"]),
                        "ap75": fmt(metrics["ap75"]),
                        "predictions": metrics["predictions"],
                        "mean_confidence": fmt(metrics["mean_confidence"]),
                        "fps": fmt(metrics["fps"], digits=2),
                        "warning": "",
                    }
                )
            except RuntimeError as exc:
                if "out of memory" in str(exc).lower() and args.batch_size > 2 and device.type == "cuda":
                    torch.cuda.empty_cache()
                    metrics = evaluate_subset(
                        args.data,
                        split_file,
                        weights,
                        model_type,
                        device,
                        args.img_size,
                        2,
                        args.num_workers,
                        args.score_thr,
                    )
                    base.update(
                        {
                            "precision": fmt(metrics["precision"]),
                            "recall": fmt(metrics["recall"]),
                            "f1": fmt(metrics["f1"]),
                            "ap50": fmt(metrics["ap50"]),
                            "ap75": fmt(metrics["ap75"]),
                            "predictions": metrics["predictions"],
                            "mean_confidence": fmt(metrics["mean_confidence"]),
                            "fps": fmt(metrics["fps"], digits=2),
                            "warning": "batch_size_4_oom_used_2",
                        }
                    )
                else:
                    raise
            rows.append(base)

    write_csv(out_dir / "rgb_separation_strata_summary.csv", SUMMARY_HEADERS, rows)
    lines = [
        "# RGB Separation Strata Summary",
        "",
        "These validation subsets are diagnostics for sensitivity to RGB similarity. The higher-separation subset is not a clean independent test set.",
        "",
        f"Score threshold for P/R/F1: `{args.score_thr}`. AP50/AP75 are score-ranked.",
        "",
        "## Results",
        "",
    ]
    lines.extend(markdown_table(SUMMARY_HEADERS, rows))
    lines.append("")
    (out_dir / "rgb_separation_strata_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved RGB separation strata outputs to: {out_dir}")


if __name__ == "__main__":
    main()
