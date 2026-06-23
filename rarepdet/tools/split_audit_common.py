#!/usr/bin/env python
"""Shared helpers for TriAir split leakage diagnostics."""

import bisect
import csv
import hashlib
import re
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"


def resolve_project_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def resolve_data_path(data_root, entry):
    path = Path(str(entry).strip())
    return path.resolve() if path.is_absolute() else (Path(data_root) / path).resolve()


def relative_to_data(path, data_root):
    path = Path(path).resolve()
    try:
        return str(path.relative_to(Path(data_root).resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_split_entries(split_file):
    split_path = Path(split_file)
    if not split_path.exists():
        raise FileNotFoundError(f"Split file not found: {split_path}")
    return [line.strip() for line in split_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_split_records(data_root, split_file, split_name):
    records = []
    data_root = Path(data_root)
    for entry in read_split_entries(split_file):
        path = resolve_data_path(data_root, entry)
        if not path.exists():
            raise FileNotFoundError(f"Image referenced by {split_name} split does not exist: {path}")
        family, numeric_id = parse_family_and_id(path)
        records.append(
            {
                "split": split_name,
                "entry": entry.replace("\\", "/"),
                "path": path,
                "rel_path": relative_to_data(path, data_root),
                "stem": path.stem,
                "family": family,
                "id": numeric_id,
                "gt_boxes": count_gt_boxes(path),
            }
        )
    return records


def parse_family_and_id(path):
    stem = Path(path).stem
    match = re.match(r"^(n?frame)_(\d+)$", stem)
    if match:
        return match.group(1), int(match.group(2))
    tail = re.search(r"(\d+)(?!.*\d)", stem)
    return "unknown", int(tail.group(1)) if tail else None


def label_path_for_image(image_path):
    parts = list(Path(image_path).parts)
    for idx, part in enumerate(parts):
        if part.lower() == "images":
            parts[idx] = "labels"
            return Path(*parts).with_suffix(".txt")
    return Path(image_path).with_suffix(".txt")


def count_gt_boxes(image_path):
    label_path = label_path_for_image(image_path)
    if not label_path.exists():
        return 0
    return sum(1 for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip())


def load_rgb_raw(path):
    array = np.load(path, mmap_mode="r")
    if array.ndim != 3 or array.shape[2] < 3:
        raise ValueError(f"Expected HxWxC array with at least 3 channels, got {array.shape}: {path}")
    return np.ascontiguousarray(array[:, :, :3])


def rgb_content_sha256(path):
    """Hash exact RGB channel content while preserving dtype and shape."""

    rgb = load_rgb_raw(path)
    digest = hashlib.sha256()
    digest.update(str(rgb.dtype).encode("utf-8"))
    digest.update(b"|")
    digest.update(",".join(str(dim) for dim in rgb.shape).encode("utf-8"))
    digest.update(b"|")
    digest.update(rgb.tobytes(order="C"))
    return digest.hexdigest()


def gray_from_rgb(rgb):
    rgb = rgb.astype(np.float32, copy=False)
    return 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]


def pooled_signature(path, grid=16):
    rgb = load_rgb_raw(path)
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
    rgb_a = load_rgb_raw(path_a).astype(np.float32, copy=False)
    rgb_b = load_rgb_raw(path_b).astype(np.float32, copy=False)
    if rgb_a.shape != rgb_b.shape:
        return None
    return float(np.mean(np.abs(rgb_a - rgb_b)))


def hamming_distance(sig_a, sig_b):
    popcount = np.array([bin(value).count("1") for value in range(256)], dtype=np.uint8)
    return int(popcount[np.bitwise_xor(sig_a, sig_b)].sum())


def add_rgb_hashes(records, label):
    total = len(records)
    for idx, record in enumerate(records, 1):
        record["rgb_sha256"] = rgb_content_sha256(record["path"])
        if idx % 500 == 0 or idx == total:
            print(f"{label}: RGB SHA {idx}/{total}")
    return records


def add_signatures(records, label):
    total = len(records)
    for idx, record in enumerate(records, 1):
        record["signature"] = pooled_signature(record["path"])
        if idx % 500 == 0 or idx == total:
            print(f"{label}: signature {idx}/{total}")
    return records


def exact_cross_split_groups(train_records, val_records, key="rgb_sha256"):
    train_by_key = {}
    val_by_key = {}
    for record in train_records:
        train_by_key.setdefault(record[key], []).append(record)
    for record in val_records:
        val_by_key.setdefault(record[key], []).append(record)
    groups = []
    for group_key in sorted(set(train_by_key) & set(val_by_key)):
        groups.append((group_key, train_by_key[group_key], val_by_key[group_key]))
    return groups


def value_quantiles(values):
    values = [float(value) for value in values if value not in (None, "NA")]
    if not values:
        return {
            "min": "NA",
            "p25": "NA",
            "p50": "NA",
            "p75": "NA",
            "p90": "NA",
            "p95": "NA",
            "max": "NA",
        }
    arr = np.asarray(values, dtype=np.float32)
    return {
        "min": float(np.min(arr)),
        "p25": float(np.quantile(arr, 0.25)),
        "p50": float(np.quantile(arr, 0.50)),
        "p75": float(np.quantile(arr, 0.75)),
        "p90": float(np.quantile(arr, 0.90)),
        "p95": float(np.quantile(arr, 0.95)),
        "max": float(np.max(arr)),
    }


def fmt(value, digits=6):
    if value in (None, "NA"):
        return "NA"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def write_csv(path, headers, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    if not rows:
        lines.append("| " + " | ".join(["NA"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "NA")) for header in headers) + " |")
    return lines


def nearest_signature_pairs(train_records, val_records):
    if not train_records or not val_records:
        return []
    train_sigs = np.stack([record["signature"] for record in train_records], axis=0).astype(np.uint8)
    popcount = np.array([bin(value).count("1") for value in range(256)], dtype=np.uint8)
    pairs = []
    for idx, val in enumerate(val_records, 1):
        xor = np.bitwise_xor(train_sigs, val["signature"])
        distances = popcount[xor].sum(axis=1)
        train_index = int(np.argmin(distances))
        pairs.append((val, train_records[train_index], int(distances[train_index])))
        if idx % 500 == 0 or idx == len(val_records):
            print(f"nearest signature: {idx}/{len(val_records)}")
    return pairs


def nearest_id_distance(train_ids, query_id):
    if query_id is None or not train_ids:
        return None
    pos = bisect.bisect_left(train_ids, query_id)
    candidates = []
    if pos < len(train_ids):
        candidates.append(abs(train_ids[pos] - query_id))
    if pos > 0:
        candidates.append(abs(train_ids[pos - 1] - query_id))
    return min(candidates) if candidates else None


def count_id_guard_violations(train_records, val_records, guard_band):
    train_ids_by_family = {}
    for record in train_records:
        if record["id"] is not None:
            train_ids_by_family.setdefault(record["family"], []).append(record["id"])
    for family in train_ids_by_family:
        train_ids_by_family[family] = sorted(train_ids_by_family[family])

    violations = 0
    nearest_distances = []
    for val in val_records:
        nearest = nearest_id_distance(train_ids_by_family.get(val["family"], []), val["id"])
        if nearest is None:
            continue
        nearest_distances.append(nearest)
        if nearest <= guard_band:
            violations += 1
    return violations, nearest_distances


def total_gt(records):
    return sum(int(record.get("gt_boxes", 0)) for record in records)
