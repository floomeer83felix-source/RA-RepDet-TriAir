#!/usr/bin/env python
"""Create a paper-style grid from prediction visualization PNG files."""

import argparse
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFont


def resolve_out(path):
    path = Path(path)
    return path if path.suffix.lower() == ".png" else path / "visual_grid.png"


def main():
    parser = argparse.ArgumentParser(description="Make visual grid from PNG visualizations.")
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--cols", default=4, type=int)
    parser.add_argument("--num", default=16, type=int)
    parser.add_argument("--seed", default=20260617, type=int)
    args = parser.parse_args()

    files = sorted(args.input_dir.glob("*.png"))
    if not files:
        raise FileNotFoundError(f"No PNG files found in {args.input_dir}")
    random.Random(args.seed).shuffle(files)
    files = files[: min(args.num, len(files))]

    thumbs = []
    for path in files:
        image = Image.open(path).convert("RGB")
        thumbs.append((path, image))
    cell_w = max(image.width for _, image in thumbs)
    cell_h = max(image.height for _, image in thumbs)
    rows = (len(thumbs) + args.cols - 1) // args.cols
    grid = Image.new("RGB", (args.cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(grid)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for idx, (path, image) in enumerate(thumbs):
        row = idx // args.cols
        col = idx % args.cols
        x = col * cell_w
        y = row * cell_h
        grid.paste(image, (x, y))
        label = path.stem[:28]
        draw.rectangle((x, y, x + min(cell_w, 185), y + 14), fill=(255, 255, 255))
        draw.text((x + 3, y + 2), label, fill=(0, 0, 0), font=font)

    out_path = resolve_out(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    grid.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
