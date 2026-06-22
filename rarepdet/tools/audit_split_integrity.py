#!/usr/bin/env python
"""Audit train/validation split integrity for TriAir.

The audit is deterministic and lightweight enough for local post-processing:
it streams .npy files one at a time for SHA256 and RGB signatures, then keeps
only compact signatures in memory for cross-split nearest-neighbor search.
"""

import argparse
import csv
import hashlib
import re
from pathlib import Path
import sys

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"


SUMMARY_HEADERS = ["Metric", "Value", "Notes"]
PAIR_HEADERS = [
    "val_path",
    "nearest_train_path",
    "val_id",
    "train_id",
    "id_distance",
    "signature_distance",
    "direct_rgb_mae",
    "val_gt_boxes",
    "train_gt_boxes",
    "exact_sha256_duplicate",
]
REVIEW_HEADERS = [
    "rank",
    "val_path",
    "train_path",
    "val_id",
    "train_id",
    "id_distance",
    "signature_distance",
    "direct_rgb_mae",
    "val_gt_boxes",
    "train_gt_boxes",
    "manual_review",
]
EXACT_DUPLICATE_HEADERS = ["train_path", "val_path", "sha256", "train_id", "val_id", "train_gt_boxes", "val_gt_boxes"]


def resolve_data_path(data_root, entry):
    path = Path(entry.strip())
    if not path.is_absolute():
        path = data_root / path
    return path.resolve()


def read_split(data_root, split_file):
    split_path = Path(split_file)
    if not split_path.is_absolute():
        split_path = data_root / split_path
    if not split_path.exists():
        raise FileNotFoundError(f"Split file not found: {split_path}")
    entries = [line.strip() for line in split_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [resolve_data_path(data_root, entry) for entry in entries]


def sha256_file(path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def parse_numeric_id(path):
    match = re.search(r"(\d+)(?!.*\d)", Path(path).stem)
    return int(match.group(1)) if match else None


def label_path_for_image(image_path):
    parts = list(image_path.parts)
    for idx, part in enumerate(parts):
        if part.lower() == "images":
            parts[idx] = "labels"
            return Path(*parts).with_suffix(".txt")
    return image_path.with_suffix(".txt")


def count_gt_boxes(image_path):
    label_path = label_path_for_image(image_path)
    if not label_path.exists():
        return 0
    count = 0
    for raw_line in label_path.read_text(encoding="utf-8").splitlines():
        if raw_line.strip():
            count += 1
    return count


def load_rgb(path):
    array = np.load(path, mmap_mode="r")
    if array.ndim != 3 or array.shape[2] < 3:
        raise ValueError(f"Expected HxWxC array with at least 3 channels, got {array.shape}: {path}")
    return np.asarray(array[:, :, :3], dtype=np.float32)


def gray_from_rgb(rgb):
    return 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]


def pooled_signature(path, grid=16):
    rgb = load_rgb(path)
    gray = gray_from_rgb(rgb)
    height, width = gray.shape
    y_edges = np.linspace(0, height, grid + 1, dtype=np.int32)
    x_edges = np.linspace(0, width, grid + 1, dtype=np.int32)
    pooled = np.empty((grid, grid), dtype=np.float32)
    for yi in range(grid):
        y0, y1 = int(y_edges[yi]), int(y_edges[yi + 1])
        for xi in range(grid):
            x0, x1 = int(x_edges[xi]), int(x_edges[xi + 1])
            pooled[yi, xi] = float(gray[y0:y1, x0:x1].mean())
    bits = pooled.reshape(-1) >= float(np.median(pooled))
    return np.packbits(bits.astype(np.uint8))


def direct_rgb_mae(path_a, path_b):
    rgb_a = load_rgb(path_a)
    rgb_b = load_rgb(path_b)
    if rgb_a.shape != rgb_b.shape:
        return "NA"
    return float(np.mean(np.abs(rgb_a - rgb_b)))


def compute_records(paths, split_name):
    records = []
    for idx, path in enumerate(paths, 1):
        if not path.exists():
            raise FileNotFoundError(f"Missing {split_name} image: {path}")
        records.append(
            {
                "split": split_name,
                "path": path,
                "path_str": str(path),
                "stem": path.stem,
                "id": parse_numeric_id(path),
                "sha256": sha256_file(path),
                "signature": pooled_signature(path),
                "gt_boxes": count_gt_boxes(path),
            }
        )
        if idx % 500 == 0:
            print(f"{split_name}: processed {idx}/{len(paths)}")
    return records


def duplicate_pairs(train_records, val_records):
    train_by_sha = {}
    for record in train_records:
        train_by_sha.setdefault(record["sha256"], []).append(record)
    pairs = []
    for val in val_records:
        for train in train_by_sha.get(val["sha256"], []):
            pairs.append((train, val))
    return pairs


def adjacency_stats(train_records, val_records, distances=(1, 2, 5, 10)):
    train_ids = {record["id"] for record in train_records if record["id"] is not None}
    val_ids = [record["id"] for record in val_records if record["id"] is not None]
    if not train_ids or len(val_ids) != len(val_records):
        return None
    stats = {}
    for distance in distances:
        hit = 0
        for val_id in val_ids:
            if any((val_id - delta in train_ids) or (val_id + delta in train_ids) for delta in range(1, distance + 1)):
                hit += 1
        stats[distance] = hit / max(len(val_ids), 1)
    return stats


def nearest_pairs(train_records, val_records):
    train_signatures = np.stack([record["signature"] for record in train_records], axis=0).astype(np.uint8)
    popcount = np.array([bin(value).count("1") for value in range(256)], dtype=np.uint8)
    pairs = []
    for idx, val in enumerate(val_records, 1):
        xor = np.bitwise_xor(train_signatures, val["signature"])
        distances = popcount[xor].sum(axis=1)
        nearest_index = int(np.argmin(distances))
        train = train_records[nearest_index]
        distance = int(distances[nearest_index])
        pairs.append((val, train, distance))
        if idx % 250 == 0:
            print(f"nearest search: processed {idx}/{len(val_records)}")
    return pairs


def quantiles(values):
    values = np.asarray(values, dtype=np.float32)
    if values.size == 0:
        return {}
    return {
        "min": float(np.min(values)),
        "p01": float(np.quantile(values, 0.01)),
        "p05": float(np.quantile(values, 0.05)),
        "p10": float(np.quantile(values, 0.10)),
        "p25": float(np.quantile(values, 0.25)),
        "p50": float(np.quantile(values, 0.50)),
        "p75": float(np.quantile(values, 0.75)),
        "p90": float(np.quantile(values, 0.90)),
        "p95": float(np.quantile(values, 0.95)),
        "p99": float(np.quantile(values, 0.99)),
        "max": float(np.max(values)),
    }


def fmt_float(value):
    if value == "NA":
        return "NA"
    return f"{float(value):.6f}"


def write_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def path_rel(path, data_root):
    try:
        return str(Path(path).resolve().relative_to(data_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def write_optional_panels(top_rows, out_dir):
    try:
        from PIL import Image, ImageDraw
    except Exception as exc:
        print(f"Skipping local panels because PIL is unavailable: {exc}")
        return 0
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for row in top_rows:
        val_rgb = load_rgb(Path(row["val_path"]))
        train_rgb = load_rgb(Path(row["train_path"]))
        if val_rgb.shape != train_rgb.shape:
            continue
        val_img = np.clip(val_rgb[:, :, :3], 0, 255).astype(np.uint8)
        train_img = np.clip(train_rgb[:, :, :3], 0, 255).astype(np.uint8)
        left = Image.fromarray(train_img)
        right = Image.fromarray(val_img)
        width, height = left.width + right.width, max(left.height, right.height)
        canvas = Image.new("RGB", (width, height + 24), (255, 255, 255))
        canvas.paste(left, (0, 24))
        canvas.paste(right, (left.width, 24))
        draw = ImageDraw.Draw(canvas)
        draw.text((4, 4), "train", fill=(0, 0, 0))
        draw.text((left.width + 4, 4), "val", fill=(0, 0, 0))
        canvas.save(out_dir / f"pair_{int(row['rank']):03d}.png")
        count += 1
    return count


def build_status(exact_duplicate_count, adjacency_stats_value, distances, thresholds):
    if exact_duplicate_count > 0:
        return "BLOCKED: exact cross-split duplicates found"
    close_fraction = thresholds.get("<=16", 0.0)
    adjacent_fraction = 0.0
    if adjacency_stats_value:
        adjacent_fraction = max(adjacency_stats_value.values())
    if close_fraction > 0.0 or adjacent_fraction > 0.0:
        return "CAUTION: near-duplicate or adjacent-frame review required"
    return "NO STRONG AUTOMATIC EVIDENCE OF LEAKAGE"


def main():
    parser = argparse.ArgumentParser(description="Audit TriAir train/val split integrity.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--train-split", default=r"D:\download\triair\splits\train.txt")
    parser.add_argument("--val-split", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--out", default="runs")
    parser.add_argument("--panel-dir", default="runs/local_split_audit_panels")
    parser.add_argument("--make-panels", action="store_true")
    args = parser.parse_args()

    data_root = Path(args.data)
    out_dir = PROJECT_ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    train_paths = read_split(data_root, args.train_split)
    val_paths = read_split(data_root, args.val_split)

    train_resolved = {str(path) for path in train_paths}
    val_resolved = {str(path) for path in val_paths}
    path_overlap = sorted(train_resolved & val_resolved)

    print("Computing train records...")
    train_records = compute_records(train_paths, "train")
    print("Computing val records...")
    val_records = compute_records(val_paths, "val")

    exact_pairs = duplicate_pairs(train_records, val_records)
    id_stats = adjacency_stats(train_records, val_records)

    print("Finding nearest train signature for each val sample...")
    nearest = nearest_pairs(train_records, val_records)
    distances = [distance for _, _, distance in nearest]
    q = quantiles(distances)
    threshold_counts = {
        "<=0": sum(1 for value in distances if value <= 0) / max(len(distances), 1),
        "<=4": sum(1 for value in distances if value <= 4) / max(len(distances), 1),
        "<=8": sum(1 for value in distances if value <= 8) / max(len(distances), 1),
        "<=16": sum(1 for value in distances if value <= 16) / max(len(distances), 1),
        "<=32": sum(1 for value in distances if value <= 32) / max(len(distances), 1),
    }
    final_status = build_status(len(exact_pairs), id_stats, distances, threshold_counts)

    nearest_rows = []
    for val, train, distance in nearest:
        id_distance = "NA" if val["id"] is None or train["id"] is None else abs(val["id"] - train["id"])
        nearest_rows.append(
            {
                "val_path": path_rel(val["path"], data_root),
                "nearest_train_path": path_rel(train["path"], data_root),
                "val_id": val["id"] if val["id"] is not None else "NA",
                "train_id": train["id"] if train["id"] is not None else "NA",
                "id_distance": id_distance,
                "signature_distance": distance,
                "direct_rgb_mae": "NA",
                "val_gt_boxes": val["gt_boxes"],
                "train_gt_boxes": train["gt_boxes"],
                "exact_sha256_duplicate": val["sha256"] == train["sha256"],
            }
        )

    top_pairs = sorted(nearest, key=lambda item: item[2])[:50]
    review_rows = []
    for rank, (val, train, distance) in enumerate(top_pairs, 1):
        id_distance = "NA" if val["id"] is None or train["id"] is None else abs(val["id"] - train["id"])
        mae = direct_rgb_mae(val["path"], train["path"])
        review_rows.append(
            {
                "rank": rank,
                "val_path": str(val["path"]),
                "train_path": str(train["path"]),
                "val_id": val["id"] if val["id"] is not None else "NA",
                "train_id": train["id"] if train["id"] is not None else "NA",
                "id_distance": id_distance,
                "signature_distance": distance,
                "direct_rgb_mae": fmt_float(mae),
                "val_gt_boxes": val["gt_boxes"],
                "train_gt_boxes": train["gt_boxes"],
                "manual_review": "",
            }
        )

    for review in review_rows:
        for row in nearest_rows:
            if row["val_path"] == path_rel(review["val_path"], data_root):
                row["direct_rgb_mae"] = review["direct_rgb_mae"]
                break

    summary_rows = [
        {"Metric": "train_count", "Value": len(train_records), "Notes": "Existing split file rows."},
        {"Metric": "val_count", "Value": len(val_records), "Notes": "Existing split file rows."},
        {"Metric": "path_overlap_count", "Value": len(path_overlap), "Notes": "Identical resolved paths in both splits."},
        {"Metric": "exact_sha256_duplicate_pairs", "Value": len(exact_pairs), "Notes": "Exact .npy byte duplicates across train/val."},
        {
            "Metric": "numeric_id_parseable",
            "Value": "yes" if id_stats is not None else "no",
            "Notes": "Numeric id parsed from final number in filename stem.",
        },
    ]
    if id_stats is None:
        for distance in (1, 2, 5, 10):
            summary_rows.append({"Metric": f"val_with_train_id_within_{distance}", "Value": "NA", "Notes": "Numeric ids unavailable."})
    else:
        for distance in (1, 2, 5, 10):
            summary_rows.append(
                {
                    "Metric": f"val_with_train_id_within_{distance}",
                    "Value": fmt_float(id_stats[distance]),
                    "Notes": "Fraction of val ids with a train id within +/- this distance.",
                }
            )
    for key, value in q.items():
        summary_rows.append({"Metric": f"signature_distance_{key}", "Value": fmt_float(value), "Notes": "Hamming distance, 256-bit RGB pooled signature."})
    for key, value in threshold_counts.items():
        summary_rows.append({"Metric": f"fraction_signature_distance_{key}", "Value": fmt_float(value), "Notes": "Fraction of val samples at or below threshold."})
    summary_rows.append({"Metric": "final_status", "Value": final_status, "Notes": "Automatic audit label required by Phase 3B."})

    write_csv(out_dir / "split_integrity_summary.csv", SUMMARY_HEADERS, summary_rows)
    write_csv(
        out_dir / "split_integrity_exact_duplicates.csv",
        EXACT_DUPLICATE_HEADERS,
        [
            {
                "train_path": path_rel(train["path"], data_root),
                "val_path": path_rel(val["path"], data_root),
                "sha256": train["sha256"],
                "train_id": train["id"] if train["id"] is not None else "NA",
                "val_id": val["id"] if val["id"] is not None else "NA",
                "train_gt_boxes": train["gt_boxes"],
                "val_gt_boxes": val["gt_boxes"],
            }
            for train, val in exact_pairs
        ],
    )
    write_csv(out_dir / "split_integrity_nearest_pairs.csv", PAIR_HEADERS, nearest_rows)
    write_csv(out_dir / "split_integrity_manual_review.csv", REVIEW_HEADERS, review_rows)

    panel_count = 0
    if args.make_panels:
        panel_count = write_optional_panels(review_rows, PROJECT_ROOT / args.panel_dir if not Path(args.panel_dir).is_absolute() else Path(args.panel_dir))

    md_lines = [
        "# Split Integrity Summary",
        "",
        f"Data root: `{data_root}`",
        f"Train split: `{args.train_split}`",
        f"Val split: `{args.val_split}`",
        "",
        "## Final Status",
        "",
        f"**{final_status}**",
        "",
        "Exact byte duplicates and path overlap are separated from near-duplicate signature similarity. A compact RGB perceptual signature can flag candidates for review, but no distance threshold proves leakage by itself.",
        "",
        "## Summary Metrics",
        "",
        "| Metric | Value | Notes |",
        "| --- | --- | --- |",
    ]
    for row in summary_rows:
        md_lines.append(f"| {row['Metric']} | {row['Value']} | {row['Notes']} |")
    md_lines.extend(
        [
            "",
            "## Closest-Pair Review",
            "",
            "- Exact byte duplicate pairs, if any: `runs/split_integrity_exact_duplicates.csv`.",
            "- Nearest train partner for every validation sample: `runs/split_integrity_nearest_pairs.csv`.",
            "- Top 50 closest cross-split pairs for manual review: `runs/split_integrity_manual_review.csv`.",
            f"- Local-only panels created: {panel_count}.",
            "",
            "Human review of the closest pairs is required when the final status is `CAUTION: near-duplicate or adjacent-frame review required`.",
            "",
        ]
    )
    (out_dir / "split_integrity_summary.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Final status: {final_status}")
    print(f"Saved outputs under: {out_dir}")


if __name__ == "__main__":
    main()
