#!/usr/bin/env python
"""
Visualize TriAir 5-channel NPY samples and YOLO-format labels.

Example:
    python tools/visualize_triair.py --data D:\\download\\triair
"""

import argparse
from collections import Counter
from pathlib import Path
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = PROJECT_ROOT / "runs" / "triair_vis"


def find_dataset_dirs(data_root):
    candidates = [
        (data_root / "images", data_root / "labels"),
        (data_root / "data" / "images", data_root / "data" / "labels"),
    ]
    existing = [(image_dir, label_dir) for image_dir, label_dir in candidates if image_dir.is_dir() and label_dir.is_dir()]

    if not existing:
        tried = "\n".join(f"  images: {image_dir}\n  labels: {label_dir}" for image_dir, label_dir in candidates)
        raise FileNotFoundError(
            "Could not find TriAir image/label directories. Expected one of:\n"
            f"{tried}"
        )

    if len(existing) > 1:
        print("WARNING: Found both supported layouts. Using direct images/labels layout.")

    return existing[0]


def build_unique_stem_map(paths, kind):
    mapping = {}
    duplicates = []
    for path in paths:
        previous = mapping.get(path.stem)
        if previous is not None:
            duplicates.append((path.stem, previous, path))
        else:
            mapping[path.stem] = path

    if duplicates:
        examples = "\n".join(f"  stem={stem}: {first} | {second}" for stem, first, second in duplicates[:10])
        raise ValueError(f"Duplicate {kind} stems found. Stem matching would be ambiguous.\n{examples}")

    return mapping


def parse_yolo_label_file(label_path, image_width, image_height):
    boxes = []
    raw_lines = []
    if label_path is None:
        return boxes, raw_lines

    try:
        lines = label_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as exc:
        raise ValueError(f"Failed to read label file {label_path}: {exc}") from exc

    for line_number, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        if not line:
            continue

        fields = line.split()
        if len(fields) != 5:
            raise ValueError(
                f"Invalid label in {label_path}, line {line_number}: "
                f"expected 5 fields 'class cx cy w h', got {len(fields)}: {line}"
            )

        try:
            class_id = int(fields[0])
            cx, cy, width, height = [float(value) for value in fields[1:]]
        except ValueError as exc:
            raise ValueError(
                f"Invalid label in {label_path}, line {line_number}: "
                f"class must be int and cx/cy/w/h must be numeric: {line}"
            ) from exc

        if not (0.0 <= cx <= 1.0 and 0.0 <= cy <= 1.0 and 0.0 <= width <= 1.0 and 0.0 <= height <= 1.0):
            raise ValueError(
                f"Invalid label in {label_path}, line {line_number}: "
                f"cx/cy/w/h must be in [0, 1]: {line}"
            )

        x1 = (cx - width / 2.0) * image_width
        y1 = (cy - height / 2.0) * image_height
        x2 = (cx + width / 2.0) * image_width
        y2 = (cy + height / 2.0) * image_height
        boxes.append((class_id, x1, y1, x2, y2))
        raw_lines.append(line)

    return boxes, raw_lines


def to_uint8_rgb(array):
    array = np.asarray(array)
    if array.ndim == 2:
        array = normalize_to_uint8(array)
        return np.stack([array, array, array], axis=-1)

    if array.ndim != 3:
        raise ValueError(f"Expected 2D or 3D array for visualization, got shape {array.shape}")

    if array.shape[2] == 1:
        return to_uint8_rgb(array[:, :, 0])

    if array.dtype == np.uint8:
        return array[:, :, :3]

    channels = [normalize_to_uint8(array[:, :, idx]) for idx in range(min(3, array.shape[2]))]
    while len(channels) < 3:
        channels.append(channels[-1])
    return np.stack(channels, axis=-1)


def normalize_to_uint8(array):
    array = np.asarray(array)
    if array.dtype == np.uint8:
        return array

    array = array.astype(np.float32)
    finite = np.isfinite(array)
    if not finite.any():
        return np.zeros(array.shape, dtype=np.uint8)

    valid = array[finite]
    min_value = float(valid.min())
    max_value = float(valid.max())
    if max_value <= min_value:
        return np.zeros(array.shape, dtype=np.uint8)

    scaled = (array - min_value) / (max_value - min_value) * 255.0
    scaled = np.clip(scaled, 0.0, 255.0)
    return scaled.astype(np.uint8)


def draw_overlay(rgb_array, boxes):
    image = Image.fromarray(to_uint8_rgb(rgb_array))
    draw = ImageDraw.Draw(image)
    width, height = image.size
    line_width = max(2, min(width, height) // 160)

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for class_id, x1, y1, x2, y2 in boxes:
        x1 = max(0, min(width - 1, x1))
        y1 = max(0, min(height - 1, y1))
        x2 = max(0, min(width - 1, x2))
        y2 = max(0, min(height - 1, y2))
        draw.rectangle((x1, y1, x2, y2), outline=(255, 40, 40), width=line_width)
        label = str(class_id)
        label_x = int(x1)
        label_y = max(0, int(y1) - 12)
        draw.text((label_x, label_y), label, fill=(255, 40, 40), font=font)

    return image


def save_sample_visuals(index, sample_info, out_dir):
    image_path = sample_info["image_path"]
    label_path = sample_info["label_path"]
    image = np.load(image_path, allow_pickle=False)
    if image.ndim != 3 or image.shape[2] < 5:
        raise ValueError(f"Expected HxWx5 NPY image, got shape {image.shape}: {image_path}")

    height, width = image.shape[:2]
    boxes, _ = parse_yolo_label_file(label_path, width, height)

    prefix = f"{index:03d}_{image_path.stem}"
    rgb_path = out_dir / f"{prefix}_rgb.png"
    thermal_path = out_dir / f"{prefix}_thermal.png"
    event_path = out_dir / f"{prefix}_event.png"
    overlay_path = out_dir / f"{prefix}_overlay.png"

    Image.fromarray(to_uint8_rgb(image[:, :, 0:3])).save(rgb_path)
    Image.fromarray(to_uint8_rgb(image[:, :, 3])).save(thermal_path)
    Image.fromarray(to_uint8_rgb(image[:, :, 4])).save(event_path)
    draw_overlay(image[:, :, 0:3], boxes).save(overlay_path)

    return {
        "file": image_path.name,
        "label_exists": label_path is not None,
        "label_file": label_path.name if label_path is not None else "",
        "state": sample_info["state"],
        "bbox_count": len(boxes),
        "image_shape": tuple(image.shape),
        "rgb": rgb_path.name,
        "thermal": thermal_path.name,
        "event": event_path.name,
        "overlay": overlay_path.name,
    }


def classify_samples(image_files, label_by_stem):
    samples = []
    state_counts = Counter()

    for image_path in image_files:
        label_path = label_by_stem.get(image_path.stem)
        if label_path is None:
            state = "missing_txt"
        else:
            nonempty_lines = [line.strip() for line in label_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
            state = "labeled" if nonempty_lines else "empty_txt"

        state_counts[state] += 1
        samples.append(
            {
                "image_path": image_path,
                "label_path": label_path,
                "state": state,
            }
        )

    return samples, state_counts


def pick_samples(samples, total_count, seed):
    rng = random.Random(seed)
    by_state = {
        "labeled": [sample for sample in samples if sample["state"] == "labeled"],
        "missing_txt": [sample for sample in samples if sample["state"] == "missing_txt"],
        "empty_txt": [sample for sample in samples if sample["state"] == "empty_txt"],
    }

    chosen = []
    for state, required in (("labeled", 30), ("missing_txt", 10), ("empty_txt", 1)):
        candidates = by_state[state][:]
        rng.shuffle(candidates)
        if state == "empty_txt" and not candidates:
            continue
        if len(candidates) < required:
            print(f"WARNING: Requested {required} {state} samples, but only found {len(candidates)}.")
        chosen.extend(candidates[: min(required, len(candidates))])

    chosen_paths = {sample["image_path"] for sample in chosen}
    remaining = [sample for sample in samples if sample["image_path"] not in chosen_paths]
    rng.shuffle(remaining)
    chosen.extend(remaining[: max(0, total_count - len(chosen))])

    if len(chosen) < total_count:
        print(f"WARNING: Requested {total_count} samples, but only selected {len(chosen)}.")

    rng.shuffle(chosen)
    return chosen[:total_count]


def write_summary(out_dir, selected, saved_rows, dataset_counts):
    summary_path = out_dir / "summary.txt"
    selected_counts = Counter(sample["state"] for sample in selected)

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("TriAir visualization summary\n")
        f.write("===========================\n")
        f.write(f"total_npy_images: {dataset_counts['images']}\n")
        f.write(f"total_txt_labels: {dataset_counts['labels']}\n")
        f.write(f"all_labeled_images: {dataset_counts['labeled']}\n")
        f.write(f"all_missing_txt_images: {dataset_counts['missing_txt']}\n")
        f.write(f"all_empty_txt_images: {dataset_counts['empty_txt']}\n")
        f.write(f"selected_total: {len(selected)}\n")
        f.write(f"selected_labeled: {selected_counts['labeled']}\n")
        f.write(f"selected_missing_txt: {selected_counts['missing_txt']}\n")
        f.write(f"selected_empty_txt: {selected_counts['empty_txt']}\n")
        f.write("\nSamples\n")
        f.write("-------\n")
        for row in saved_rows:
            f.write(
                f"{row['file']}\t"
                f"state={row['state']}\t"
                f"txt_exists={row['label_exists']}\t"
                f"txt={row['label_file']}\t"
                f"bbox_count={row['bbox_count']}\t"
                f"shape={row['image_shape']}\t"
                f"rgb={row['rgb']}\t"
                f"thermal={row['thermal']}\t"
                f"event={row['event']}\t"
                f"overlay={row['overlay']}\n"
            )

    return summary_path


def main():
    parser = argparse.ArgumentParser(description="Visualize TriAir RGB/Thermal/Event samples with YOLO bboxes.")
    parser.add_argument("--data", required=True, type=Path, help="Dataset root, e.g. D:\\download\\triair")
    parser.add_argument("--out", default=DEFAULT_OUT_DIR, type=Path, help="Output directory")
    parser.add_argument("--count", default=50, type=int, help="Number of samples to visualize")
    parser.add_argument("--seed", default=20260617, type=int, help="Random seed")
    args = parser.parse_args()

    data_root = args.data.expanduser()
    if not data_root.is_dir():
        raise NotADirectoryError(f"Dataset root is not a directory: {data_root}")

    image_dir, label_dir = find_dataset_dirs(data_root)
    image_files = sorted(image_dir.rglob("*.npy"))
    label_files = sorted(label_dir.rglob("*.txt"))
    if not image_files:
        raise FileNotFoundError(f"No .npy images found under {image_dir}")

    label_by_stem = build_unique_stem_map(label_files, ".txt label")
    samples, state_counts = classify_samples(image_files, label_by_stem)
    selected = pick_samples(samples, args.count, args.seed)

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    saved_rows = []
    for index, sample in enumerate(selected, 1):
        row = save_sample_visuals(index, sample, out_dir)
        saved_rows.append(row)
        print(
            f"[{index:02d}/{len(selected)}] {row['file']} "
            f"state={row['state']} bbox_count={row['bbox_count']} shape={row['image_shape']}"
        )

    summary_path = write_summary(
        out_dir,
        selected,
        saved_rows,
        {
            "images": len(image_files),
            "labels": len(label_files),
            "labeled": state_counts["labeled"],
            "missing_txt": state_counts["missing_txt"],
            "empty_txt": state_counts["empty_txt"],
        },
    )

    selected_counts = Counter(sample["state"] for sample in selected)
    print("\n=== Visualization Complete ===")
    print(f"output_dir: {out_dir}")
    print(f"summary: {summary_path}")
    print(f"selected_total: {len(selected)}")
    print(f"selected_labeled: {selected_counts['labeled']}")
    print(f"selected_missing_txt: {selected_counts['missing_txt']}")
    print(f"selected_empty_txt: {selected_counts['empty_txt']}")


if __name__ == "__main__":
    main()
