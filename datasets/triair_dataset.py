#!/usr/bin/env python
"""
PyTorch Dataset for TriAir 5-channel NPY images and YOLO-format labels.

Example:
    python datasets/triair_dataset.py --data D:\\download\\triair --mode rgbte
"""

import argparse
from collections import Counter
from pathlib import Path
import random

import numpy as np
import torch
from torch.utils.data import Dataset


MODE_CHANNELS = {
    "rgb": (0, 1, 2),
    "thermal": (3,),
    "event": (4,),
    "rgbt": (0, 1, 2, 3),
    "rgbe": (0, 1, 2, 4),
    "te": (3, 4),
    "rgbte": (0, 1, 2, 3, 4),
}


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


def build_unique_stem_map(paths, file_kind):
    by_stem = {}
    duplicates = []
    for path in paths:
        previous = by_stem.get(path.stem)
        if previous is not None:
            duplicates.append((path.stem, previous, path))
        else:
            by_stem[path.stem] = path

    if duplicates:
        examples = "\n".join(f"  stem={stem}: {first} | {second}" for stem, first, second in duplicates[:10])
        raise ValueError(
            f"Duplicate {file_kind} stems found. Stem-based matching would be ambiguous.\n"
            f"{examples}"
        )

    return by_stem


def parse_yolo_label_file(label_path, image_width=None, image_height=None):
    boxes = []
    labels = []

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
                f"expected 5 fields 'class cx cy w h', got {len(fields)} fields: {line}"
            )

        try:
            class_id = int(fields[0])
        except ValueError as exc:
            raise ValueError(
                f"Invalid label in {label_path}, line {line_number}: "
                f"class id must be an int: {line}"
            ) from exc

        try:
            cx, cy, width, height = [float(value) for value in fields[1:]]
        except ValueError as exc:
            raise ValueError(
                f"Invalid label in {label_path}, line {line_number}: "
                f"cx/cy/w/h must be numeric: {line}"
            ) from exc

        if class_id < 0:
            raise ValueError(
                f"Invalid label in {label_path}, line {line_number}: "
                f"class id must be non-negative: {line}"
            )

        values = (cx, cy, width, height)
        if not all(0.0 <= value <= 1.0 for value in values):
            raise ValueError(
                f"Invalid label in {label_path}, line {line_number}: "
                f"cx/cy/w/h must be in [0, 1]: {line}"
            )

        labels.append(class_id)
        if image_width is None or image_height is None:
            boxes.append((cx, cy, width, height))
        else:
            x1 = (cx - width / 2.0) * image_width
            y1 = (cy - height / 2.0) * image_height
            x2 = (cx + width / 2.0) * image_width
            y2 = (cy + height / 2.0) * image_height
            boxes.append((x1, y1, x2, y2))

    return boxes, labels


class TriAirDataset(Dataset):
    """Dataset using every .npy image, including images with missing label txt files."""

    def __init__(self, data, mode="rgbte", split_file=None):
        self.data_root = Path(data).expanduser()
        if not self.data_root.exists():
            raise FileNotFoundError(f"Dataset path does not exist: {self.data_root}")
        if not self.data_root.is_dir():
            raise NotADirectoryError(f"Dataset path is not a directory: {self.data_root}")
        if mode not in MODE_CHANNELS:
            allowed = ", ".join(MODE_CHANNELS)
            raise ValueError(f"Unsupported mode '{mode}'. Allowed modes: {allowed}")

        self.mode = mode
        self.channels = MODE_CHANNELS[mode]
        self.split_file = Path(split_file).expanduser() if split_file is not None else None
        self.image_dir, self.label_dir = find_dataset_dirs(self.data_root)
        all_image_files = sorted(self.image_dir.rglob("*.npy"))
        self.label_files = sorted(self.label_dir.rglob("*.txt"))

        if not all_image_files:
            raise FileNotFoundError(f"No .npy files found under image directory: {self.image_dir}")

        self.image_by_stem = build_unique_stem_map(all_image_files, ".npy image")
        self.label_by_stem = build_unique_stem_map(self.label_files, ".txt label")
        self.image_files = self._load_split_images() if self.split_file is not None else all_image_files
        self.sample_infos = []
        self.class_distribution = Counter()
        self.empty_label_txt_files = []
        self.total_boxes = 0

        self._audit_labels()
        self._build_sample_infos()
        self._print_summary()

    def _load_split_images(self):
        if not self.split_file.is_file():
            raise FileNotFoundError(f"Split file not found: {self.split_file}")

        image_files = []
        seen = set()
        for line_number, raw_line in enumerate(self.split_file.read_text(encoding="utf-8").splitlines(), 1):
            entry = raw_line.strip()
            if not entry or entry.startswith("#"):
                continue

            path = Path(entry)
            if path.is_absolute():
                image_path = path
            elif path.suffix.lower() == ".npy":
                candidates = [
                    self.data_root / path,
                    self.image_dir / path,
                    self.image_by_stem.get(path.stem),
                ]
                image_path = next((candidate for candidate in candidates if candidate is not None and candidate.is_file()), None)
            else:
                image_path = self.image_by_stem.get(entry)

            if image_path is None or not image_path.is_file():
                raise FileNotFoundError(
                    f"Split file {self.split_file}, line {line_number}: "
                    f"could not resolve image entry '{entry}'"
                )

            image_path = image_path.resolve()
            if image_path in seen:
                raise ValueError(f"Split file {self.split_file} contains duplicate image: {image_path}")
            seen.add(image_path)
            image_files.append(image_path)

        if not image_files:
            raise ValueError(f"Split file has no usable image entries: {self.split_file}")

        return image_files

    def _audit_labels(self):
        self.label_box_count_by_stem = {}

        for image_path in self.image_files:
            label_path = self.label_by_stem.get(image_path.stem)
            if label_path is None:
                continue
            boxes, labels = parse_yolo_label_file(label_path)
            self.label_box_count_by_stem[label_path.stem] = len(labels)
            if not labels:
                self.empty_label_txt_files.append(label_path)

            self.total_boxes += len(labels)
            self.class_distribution.update(labels)

    def _build_sample_infos(self):
        for image_path in self.image_files:
            label_path = self.label_by_stem.get(image_path.stem)
            if label_path is None:
                label_state = "missing_txt"
                box_count = 0
            else:
                box_count = self.label_box_count_by_stem.get(image_path.stem, 0)
                label_state = "empty_txt" if box_count == 0 else "labeled"

            self.sample_infos.append(
                {
                    "image_path": image_path,
                    "label_path": label_path,
                    "label_state": label_state,
                    "box_count": box_count,
                }
            )

    def _print_summary(self):
        images_with_label = sum(1 for info in self.sample_infos if info["label_path"] is not None)
        images_without_label = sum(1 for info in self.sample_infos if info["label_path"] is None)

        print("=== TriAirDataset Summary ===")
        print(f"data_root: {self.data_root}")
        print(f"image_dir: {self.image_dir}")
        print(f"label_dir: {self.label_dir}")
        if self.split_file is not None:
            print(f"split_file: {self.split_file}")
        print(f"mode: {self.mode}")
        print(f"channels: {self.channels}")
        print(f"total images: {len(self.image_files)}")
        print(f"images with label txt: {images_with_label}")
        print(f"images without label txt: {images_without_label}")
        print(f"empty label txt files: {len(self.empty_label_txt_files)}")
        print(f"total boxes: {self.total_boxes}")
        print("class distribution:")
        if self.class_distribution:
            for class_id, count in sorted(self.class_distribution.items()):
                print(f"  class {class_id}: {count}")
        else:
            print("  none")

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, index):
        info = self.sample_infos[index]
        image_path = info["image_path"]
        label_path = info["label_path"]

        try:
            image = np.load(image_path, allow_pickle=False)
        except Exception as exc:
            raise RuntimeError(f"Failed to read image file {image_path}: {exc}") from exc

        if image.ndim != 3:
            raise ValueError(f"Expected image shape HxWxC in {image_path}, got shape {image.shape}")
        if image.shape[2] < 5:
            raise ValueError(f"Expected at least 5 channels in {image_path}, got shape {image.shape}")

        height, width = image.shape[:2]
        image = image[:, :, self.channels]
        if image.ndim == 2:
            image = image[:, :, None]

        image_tensor = torch.from_numpy(np.ascontiguousarray(image)).permute(2, 0, 1).float()

        if label_path is None:
            boxes_tensor = torch.zeros((0, 4), dtype=torch.float32)
            labels_tensor = torch.zeros((0,), dtype=torch.int64)
        else:
            boxes, labels = parse_yolo_label_file(label_path, image_width=width, image_height=height)
            if boxes:
                boxes_tensor = torch.as_tensor(boxes, dtype=torch.float32)
                labels_tensor = torch.as_tensor(labels, dtype=torch.int64)
            else:
                boxes_tensor = torch.zeros((0, 4), dtype=torch.float32)
                labels_tensor = torch.zeros((0,), dtype=torch.int64)

        target = {
            "boxes": boxes_tensor,
            "labels": labels_tensor,
        }
        return image_tensor, target


def collate_fn(batch):
    images, targets = zip(*batch)
    return list(images), list(targets)


def choose_test_indices(dataset, sample_count, seed):
    rng = random.Random(seed)
    forced_indices = []

    for wanted_state in ("labeled", "missing_txt", "empty_txt"):
        candidates = [idx for idx, info in enumerate(dataset.sample_infos) if info["label_state"] == wanted_state]
        if candidates:
            forced_indices.append(rng.choice(candidates))

    all_indices = list(range(len(dataset)))
    rng.shuffle(all_indices)

    chosen = []
    seen = set()
    for idx in forced_indices + all_indices:
        if idx in seen:
            continue
        chosen.append(idx)
        seen.add(idx)
        if len(chosen) >= sample_count:
            break

    return chosen


def main():
    parser = argparse.ArgumentParser(description="Smoke test the TriAirDataset.")
    parser.add_argument("--data", required=True, type=Path, help="Dataset root, e.g. D:\\download\\triair")
    parser.add_argument("--mode", default="rgbte", choices=sorted(MODE_CHANNELS), help="Input channel mode")
    parser.add_argument("--split-file", default=None, type=Path, help="Optional train/val split txt")
    parser.add_argument("--samples", default=20, type=int, help="Number of random samples to read")
    parser.add_argument("--seed", default=20260617, type=int, help="Random seed for the smoke test")
    args = parser.parse_args()

    if args.samples < 20:
        raise ValueError("--samples must be at least 20 for this smoke test")

    dataset = TriAirDataset(args.data, mode=args.mode, split_file=args.split_file)
    print(f"\nDataset length: {len(dataset)}")

    print("\n=== Random Read Smoke Test ===")
    indices = choose_test_indices(dataset, args.samples, args.seed)
    for index in indices:
        image, target = dataset[index]
        info = dataset.sample_infos[index]
        print(
            f"idx={index} file={info['image_path'].name} "
            f"state={info['label_state']} image_shape={tuple(image.shape)} "
            f"boxes_shape={tuple(target['boxes'].shape)} labels_shape={tuple(target['labels'].shape)}"
        )

    states = Counter(dataset.sample_infos[index]["label_state"] for index in indices)
    print("\nSmoke test included states:")
    for state in ("labeled", "missing_txt", "empty_txt"):
        print(f"  {state}: {states[state]}")


if __name__ == "__main__":
    main()
