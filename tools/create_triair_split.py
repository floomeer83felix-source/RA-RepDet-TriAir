#!/usr/bin/env python
"""Create a fixed 8:2 train/val split for TriAir without moving data."""

import argparse
from pathlib import Path
import random


def find_image_dir(data_root):
    candidates = [
        data_root / "images",
        data_root / "data" / "images",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    tried = "\n".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Could not find TriAir images directory. Tried:\n{tried}")


def write_split(path, data_root, image_files):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for image_path in image_files:
            f.write(f"{image_path.relative_to(data_root).as_posix()}\n")


def main():
    parser = argparse.ArgumentParser(description="Create fixed TriAir train/val split files.")
    parser.add_argument("--data", default=r"D:\download\triair", type=Path, help="TriAir dataset root")
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--train-ratio", default=0.8, type=float)
    parser.add_argument("--val-ratio", default=None, type=float)
    parser.add_argument("--out", default=None, type=Path, help="Output split directory")
    args = parser.parse_args()

    data_root = args.data.expanduser()
    if not data_root.is_dir():
        raise NotADirectoryError(f"Dataset root is not a directory: {data_root}")
    train_ratio = 1.0 - args.val_ratio if args.val_ratio is not None else args.train_ratio
    if not (0.0 < train_ratio < 1.0):
        raise ValueError("--train-ratio or --val-ratio must define a split between 0 and 1")

    image_dir = find_image_dir(data_root)
    image_files = sorted(image_dir.rglob("*.npy"))
    if not image_files:
        raise FileNotFoundError(f"No .npy files found under {image_dir}")

    rng = random.Random(args.seed)
    rng.shuffle(image_files)
    train_count = int(len(image_files) * train_ratio)
    train_files = image_files[:train_count]
    val_files = image_files[train_count:]

    split_dir = args.out.expanduser() if args.out is not None else data_root / "splits"
    train_path = split_dir / "train.txt"
    val_path = split_dir / "val.txt"
    write_split(train_path, data_root, train_files)
    write_split(val_path, data_root, val_files)

    print("=== TriAir Split Created ===")
    print(f"data_root: {data_root}")
    print(f"seed: {args.seed}")
    print(f"train_ratio: {train_ratio}")
    print(f"val_ratio: {1.0 - train_ratio}")
    print(f"total images: {len(image_files)}")
    print(f"train images: {len(train_files)}")
    print(f"val images: {len(val_files)}")
    print(f"train split: {train_path}")
    print(f"val split: {val_path}")


if __name__ == "__main__":
    main()
