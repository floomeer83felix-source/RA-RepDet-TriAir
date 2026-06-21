#!/usr/bin/env python
"""
Check TriAir-style 5-channel NPY images and YOLO-format TXT labels.

Example:
    python tools/check_triair_dataset.py --data D:\\download\\triair
"""

import argparse
from collections import Counter
from pathlib import Path
import random

import numpy as np


def find_dataset_dirs(data_root):
    candidates = [
        (data_root / "images", data_root / "labels"),
        (data_root / "data" / "images", data_root / "data" / "labels"),
    ]

    existing = [(img_dir, label_dir) for img_dir, label_dir in candidates if img_dir.is_dir() and label_dir.is_dir()]

    if not existing:
        tried = "\n".join(f"  images: {img_dir}\n  labels: {label_dir}" for img_dir, label_dir in candidates)
        raise SystemExit(
            "ERROR: Could not find dataset image/label directories.\n"
            "Expected one of these layouts:\n"
            f"{tried}"
        )

    if len(existing) > 1:
        print("WARNING: Found both supported layouts. Using the direct images/labels layout.")

    return existing[0]


def list_files(image_dir, label_dir):
    image_files = sorted(image_dir.rglob("*.npy"))
    label_files = sorted(label_dir.rglob("*.txt"))

    if not image_files:
        raise SystemExit(f"ERROR: No .npy files found in image directory: {image_dir}")

    if not label_files:
        print(f"WARNING: No .txt files found in label directory: {label_dir}")

    return image_files, label_files


def format_examples(items, limit=10):
    if not items:
        return "None"
    shown = ", ".join(items[:limit])
    if len(items) > limit:
        shown += f", ... (+{len(items) - limit} more)"
    return shown


def check_pairs(image_files, label_files):
    image_stems = {path.stem for path in image_files}
    label_stems = {path.stem for path in label_files}
    matched_images = [path for path in image_files if path.stem in label_stems]
    missing_label_images = [path for path in image_files if path.stem not in label_stems]
    orphan_label_files = [path for path in label_files if path.stem not in image_stems]
    one_to_one = not missing_label_images and not orphan_label_files and len(image_files) == len(label_files)
    return one_to_one, matched_images, missing_label_images, orphan_label_files


def load_npy(path):
    try:
        return np.load(path, allow_pickle=False)
    except Exception as exc:
        raise RuntimeError(f"Failed to read NPY file {path}: {exc}") from exc


def print_random_image_samples(image_files, sample_count):
    print("\n=== Random NPY Image Checks ===")
    sample_files = random.sample(image_files, min(sample_count, len(image_files)))

    for path in sample_files:
        try:
            arr = load_npy(path)
            print(
                f"{path.name}: shape={arr.shape}, dtype={arr.dtype}, "
                f"min={arr.min()}, max={arr.max()}"
            )
        except Exception as exc:
            print(f"{path.name}: ERROR: {exc}")


def compute_channel_stats(image_files):
    channel_min = None
    channel_max = None
    channel_sum = None
    channel_sum_sq = None
    channel_count = None
    valid_images = 0
    invalid_images = []

    for path in image_files:
        try:
            arr = load_npy(path)
        except Exception as exc:
            invalid_images.append((path.name, str(exc)))
            continue

        if arr.ndim != 3:
            invalid_images.append((path.name, f"expected 3D HxWxC array, got shape={arr.shape}"))
            continue

        flat = arr.reshape(-1, arr.shape[2])
        per_min = flat.min(axis=0)
        per_max = flat.max(axis=0)
        per_sum = flat.sum(axis=0, dtype=np.float64)
        per_sum_sq = np.einsum("ij,ij->j", flat, flat, dtype=np.float64)
        per_count = np.full(arr.shape[2], flat.shape[0], dtype=np.float64)

        if channel_min is None:
            channel_min = per_min
            channel_max = per_max
            channel_sum = per_sum
            channel_sum_sq = per_sum_sq
            channel_count = per_count
        else:
            if arr.shape[2] != len(channel_min):
                invalid_images.append(
                    (path.name, f"channel count {arr.shape[2]} does not match previous count {len(channel_min)}")
                )
                continue
            channel_min = np.minimum(channel_min, per_min)
            channel_max = np.maximum(channel_max, per_max)
            channel_sum += per_sum
            channel_sum_sq += per_sum_sq
            channel_count += per_count

        valid_images += 1

    return {
        "valid_images": valid_images,
        "invalid_images": invalid_images,
        "min": channel_min,
        "max": channel_max,
        "sum": channel_sum,
        "sum_sq": channel_sum_sq,
        "count": channel_count,
    }


def print_channel_stats(stats):
    print("\n=== Per-Channel Statistics Over All Readable 3D Images ===")
    if stats["valid_images"] == 0:
        print("ERROR: No readable 3D images available for channel statistics.")
        return

    means = stats["sum"] / stats["count"]
    variances = stats["sum_sq"] / stats["count"] - means * means
    variances = np.maximum(variances, 0.0)
    stds = np.sqrt(variances)

    print(f"valid_images_for_stats: {stats['valid_images']}")
    for idx in range(len(means)):
        print(
            f"channel_{idx}: min={stats['min'][idx]:.6g}, max={stats['max'][idx]:.6g}, "
            f"mean={means[idx]:.6g}, std={stds[idx]:.6g}"
        )

    invalid_images = stats["invalid_images"]
    print(f"invalid_or_unreadable_image_count: {len(invalid_images)}")
    for name, reason in invalid_images[:10]:
        print(f"  {name}: {reason}")
    if len(invalid_images) > 10:
        print(f"  ... (+{len(invalid_images) - 10} more)")


def parse_label_file(path):
    issues = []
    labels = []

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as exc:
        return labels, [(0, f"read_error: {exc}", "")]

    nonempty_lines = [(line_no, line.strip()) for line_no, line in enumerate(lines, 1) if line.strip()]

    for line_no, line in nonempty_lines:
        fields = line.split()
        if len(fields) != 5:
            issues.append((line_no, f"field_count_not_5: {len(fields)}", line))
            continue

        try:
            class_id = int(fields[0])
        except ValueError:
            issues.append((line_no, "class_id_not_integer", line))
            continue

        try:
            cx, cy, width, height = [float(value) for value in fields[1:]]
        except ValueError:
            issues.append((line_no, "bbox_value_not_numeric", line))
            continue

        if class_id < 0:
            issues.append((line_no, "class_id_negative", line))
            continue

        if not (0.0 <= cx <= 1.0 and 0.0 <= cy <= 1.0 and 0.0 <= width <= 1.0 and 0.0 <= height <= 1.0):
            issues.append((line_no, "bbox_value_outside_0_to_1", line))
            continue

        labels.append((class_id, cx, cy, width, height, line))

    return labels, issues


def audit_labels(label_files):
    class_counts = Counter()
    empty_label_files = []
    invalid_label_files = Counter()
    invalid_lines = []
    total_valid_boxes = 0

    for path in label_files:
        labels, issues = parse_label_file(path)
        if not labels and not issues:
            empty_label_files.append(path.name)

        for class_id, _, _, _, _, _ in labels:
            class_counts[class_id] += 1
            total_valid_boxes += 1

        if issues:
            invalid_label_files[path.name] += len(issues)
            for line_no, reason, line in issues:
                invalid_lines.append((path.name, line_no, reason, line))

    return {
        "class_counts": class_counts,
        "empty_label_files": empty_label_files,
        "invalid_label_files": invalid_label_files,
        "invalid_lines": invalid_lines,
        "total_valid_boxes": total_valid_boxes,
    }


def print_label_audit(audit, missing_label_images, image_files):
    print("\n=== Label Audit ===")
    class_counts = audit["class_counts"]
    print(f"label_class_count: {len(class_counts)}")
    print(f"valid_box_count: {audit['total_valid_boxes']}")
    if class_counts:
        for class_id, count in sorted(class_counts.items()):
            print(f"  class {class_id}: {count} boxes")
    else:
        print("  No valid boxes found.")

    empty_files = audit["empty_label_files"]
    invalid_files = audit["invalid_label_files"]
    invalid_lines = audit["invalid_lines"]
    image_stems = {path.stem for path in image_files}
    empty_label_image_count = sum(1 for name in empty_files if Path(name).stem in image_stems)
    empty_or_missing_label_image_count = empty_label_image_count + len(missing_label_images)
    print(f"empty_label_file_count: {len(empty_files)}")
    print(f"empty_label_examples: {format_examples(empty_files)}")
    print(f"missing_label_image_count_as_empty: {len(missing_label_images)}")
    print(f"empty_label_image_count: {empty_label_image_count}")
    print(f"empty_or_missing_label_image_count: {empty_or_missing_label_image_count}")
    print(f"invalid_label_file_count: {len(invalid_files)}")
    print(f"invalid_label_line_count: {len(invalid_lines)}")
    for name, line_no, reason, line in invalid_lines[:10]:
        print(f"  {name}:{line_no}: {reason}: {line}")
    if len(invalid_lines) > 10:
        print(f"  ... (+{len(invalid_lines) - 10} more)")


def print_random_sample_pairs(image_files, label_dir, sample_count):
    print("\n=== Random Image/Label Sample Pairs ===")
    sample_files = random.sample(image_files, min(sample_count, len(image_files)))

    for image_path in sample_files:
        label_path = label_dir / f"{image_path.stem}.txt"
        try:
            arr = load_npy(image_path)
            shape = arr.shape
        except Exception as exc:
            shape = f"ERROR: {exc}"

        if label_path.is_file():
            try:
                lines = [line.strip() for line in label_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
                label_count = len(lines)
                first_label = lines[0] if lines else "None"
            except Exception as exc:
                label_count = "ERROR"
                first_label = f"ERROR: {exc}"
        else:
            label_count = 0
            first_label = "None (missing .txt; treated as empty target)"

        print(f"{image_path.name}")
        print(f"  image_shape: {shape}")
        print(f"  label_line_count: {label_count}")
        print(f"  first_label: {first_label}")


def main():
    parser = argparse.ArgumentParser(description="Check TriAir NPY images and YOLO TXT labels.")
    parser.add_argument("--data", required=True, type=Path, help="Dataset root, e.g. D:\\download\\triair")
    args = parser.parse_args()

    data_root = args.data.expanduser()
    if not data_root.exists():
        raise SystemExit(f"ERROR: Dataset path does not exist: {data_root}")
    if not data_root.is_dir():
        raise SystemExit(f"ERROR: Dataset path is not a directory: {data_root}")

    image_dir, label_dir = find_dataset_dirs(data_root)
    image_files, label_files = list_files(image_dir, label_dir)
    one_to_one, matched_images, missing_label_images, orphan_label_files = check_pairs(image_files, label_files)

    print("=== Dataset Paths ===")
    print(f"data_root: {data_root}")
    print(f"image_dir: {image_dir}")
    print(f"label_dir: {label_dir}")

    print("\n=== File Counts And Pairing ===")
    print(f"npy_image_count: {len(image_files)}")
    print(f"txt_label_count: {len(label_files)}")
    print(f"matched_sample_count: {len(matched_images)}")
    print(f"images_and_labels_one_to_one: {one_to_one}")
    print(f"images_missing_label_count: {len(missing_label_images)}")
    print(f"images_missing_label_examples: {format_examples([path.name for path in missing_label_images], limit=30)}")
    print(f"labels_missing_image_count: {len(orphan_label_files)}")
    print(f"labels_missing_image_examples: {format_examples([path.name for path in orphan_label_files], limit=30)}")

    print_random_image_samples(image_files, 10)
    print_channel_stats(compute_channel_stats(image_files))
    print_label_audit(audit_labels(label_files), missing_label_images, image_files)
    print_random_sample_pairs(image_files, label_dir, 5)


if __name__ == "__main__":
    main()
