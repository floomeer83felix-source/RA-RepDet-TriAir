#!/usr/bin/env python
"""Prepare local RGB cache and protocol file for the official YOLO11n baseline."""

import argparse
import csv
import hashlib
import platform
from datetime import datetime
from pathlib import Path
import sys

import numpy as np
import torch
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import TriAirDataset, parse_yolo_label_file


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def import_ultralytics():
    try:
        import ultralytics
        from ultralytics import YOLO
    except Exception as exc:
        raise RuntimeError(f"Ultralytics is required for YOLO11n baseline but could not be imported: {exc}") from exc
    return ultralytics, YOLO


def read_split_paths(path):
    entries = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            entries.append(Path(line).resolve())
    return entries


def rgb_to_uint8(rgb):
    arr = np.asarray(rgb)
    note = f"source dtype={arr.dtype}, min={float(np.nanmin(arr)):.6f}, max={float(np.nanmax(arr)):.6f}"
    if arr.dtype == np.uint8:
        return np.ascontiguousarray(arr), note + "; kept uint8 values"
    arr = arr.astype(np.float32)
    if float(np.nanmax(arr)) <= 1.0 and float(np.nanmin(arr)) >= 0.0:
        arr = arr * 255.0
        note += "; scaled float [0,1] to [0,255]"
    else:
        note += "; clipped/cast to uint8 [0,255]"
    return np.ascontiguousarray(np.clip(np.rint(arr), 0, 255).astype(np.uint8)), note


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def clean_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    for item in path.iterdir():
        if item.is_file():
            item.unlink()


def export_split(dataset, split_name, out_dir):
    image_dir = out_dir / "images" / split_name
    label_dir = out_dir / "labels" / split_name
    clean_dir(image_dir)
    clean_dir(label_dir)

    rows = []
    rgb_hashes = {}
    conversion_notes = []
    for index, info in enumerate(dataset.sample_infos):
        image_path = Path(info["image_path"])
        label_path = info["label_path"]
        arr = np.load(image_path, allow_pickle=False)
        if arr.ndim != 3 or arr.shape[2] < 3:
            raise RuntimeError(f"Expected at least 3 channels in {image_path}, got {arr.shape}")
        rgb, note = rgb_to_uint8(arr[:, :, 0:3])
        if len(conversion_notes) < 5:
            conversion_notes.append(f"{image_path.name}: {note}")

        out_stem = image_path.stem
        out_image = image_dir / f"{out_stem}.png"
        out_label = label_dir / f"{out_stem}.txt"
        Image.fromarray(rgb, mode="RGB").save(out_image)

        boxes, labels = ([], [])
        if label_path is not None:
            boxes, labels = parse_yolo_label_file(label_path)
        with out_label.open("w", encoding="utf-8") as f:
            for (cx, cy, width, height), class_id in zip(boxes, labels):
                if int(class_id) != 0:
                    raise RuntimeError(f"Unexpected TriAir class id {class_id} in {label_path}; expected 0.")
                f.write(f"0 {cx:.8f} {cy:.8f} {width:.8f} {height:.8f}\n")

        rgb_hash = sha256_bytes(rgb.tobytes())
        rgb_hashes.setdefault(rgb_hash, []).append(str(image_path))
        rows.append(
            {
                "split": split_name,
                "index": index,
                "source_image": str(image_path),
                "exported_image": str(out_image),
                "exported_label": str(out_label),
                "gt_boxes": len(labels),
                "rgb_sha256": rgb_hash,
                "height": rgb.shape[0],
                "width": rgb.shape[1],
            }
        )
    return rows, rgb_hashes, conversion_notes


def write_yaml(path, cache_dir):
    text = "\n".join(
        [
            f"path: {cache_dir.as_posix()}",
            "train: images/train",
            "val: images/val",
            "names:",
            "  0: vehicle",
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def write_csv(path, rows):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def version_info(ultralytics):
    info = {
        "Python": sys.version.replace("\n", " "),
        "Platform": platform.platform(),
        "Ultralytics": getattr(ultralytics, "__version__", "NA"),
        "PyTorch": torch.__version__,
        "CUDA available": str(torch.cuda.is_available()).lower(),
        "CUDA version": torch.version.cuda or "NA",
        "GPU": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NA",
    }
    return info


def write_protocol(path, info, train_rows, val_rows, train_val_rgb_overlap, yaml_path, checkpoint_source, conversion_notes):
    lines = [
        "# YOLO11n RGB Baseline Protocol",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Environment",
        "",
    ]
    for key, value in info.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Official Checkpoint",
            "",
            f"- Requested model: `yolo11n.pt`",
            f"- Resolved checkpoint/source: `{checkpoint_source}`",
            "- No substitute detector is allowed for this baseline.",
            "",
            "## Cache",
            "",
            f"- YAML: `{yaml_path}`",
            f"- Train images exported: {len(train_rows)}",
            f"- Val images exported: {len(val_rows)}",
            f"- RGB-content train/val overlap after export: {train_val_rgb_overlap}",
            "- Guard samples are excluded from train and val exports.",
            "- RGB source channels: `[0:3]` from TriAir `rgbte` arrays.",
            "- Aspect ratio is preserved by writing each RGB frame at its native HxW size; YOLO letterboxes internally at `imgsz=640`.",
            "",
            "## RGB Conversion Notes",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in conversion_notes)
    lines.extend(
        [
            "",
            "## Exact Training Commands",
            "",
            "```powershell",
            f"yolo detect train model=yolo11n.pt data={yaml_path} epochs=50 imgsz=640 seed=0 deterministic=True project=runs name=Y11n_rgb_seed0_block64g16_e50 exist_ok=False device=0",
            f"yolo detect train model=yolo11n.pt data={yaml_path} epochs=50 imgsz=640 seed=2 deterministic=True project=runs name=Y11n_rgb_seed2_block64g16_e50 exist_ok=False device=0",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Prepare YOLO11n RGB baseline cache.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--train-split", default=r"runs\blocked_split_candidates\block64_guard16_seed0_train.txt")
    parser.add_argument("--val-split", default=r"runs\blocked_split_candidates\block64_guard16_seed0_val.txt")
    parser.add_argument("--guard-split", default=r"runs\blocked_split_candidates\block64_guard16_seed0_guard.txt")
    parser.add_argument("--out", default=r"runs\local_yolo11n_rgb_cache")
    parser.add_argument("--protocol", default=r"runs\yolo11n_rgb_baseline_protocol.md")
    parser.add_argument("--model", default="yolo11n.pt")
    args = parser.parse_args()

    if args.model != "yolo11n.pt":
        raise RuntimeError(f"This baseline must use official yolo11n.pt, got {args.model}")

    ultralytics, YOLO = import_ultralytics()
    try:
        model = YOLO(args.model)
    except Exception as exc:
        raise RuntimeError(f"Could not resolve official yolo11n.pt in the installed Ultralytics environment: {exc}") from exc
    checkpoint_source = getattr(model, "ckpt_path", None) or args.model

    train_split = resolve_path(args.train_split)
    val_split = resolve_path(args.val_split)
    guard_split = resolve_path(args.guard_split)
    cache_dir = resolve_path(args.out)
    protocol_path = resolve_path(args.protocol)

    train_paths = set(read_split_paths(train_split))
    val_paths = set(read_split_paths(val_split))
    guard_paths = set(read_split_paths(guard_split))
    if len(train_paths) != 7439 or len(val_paths) != 2213 or len(guard_paths) != 837:
        raise RuntimeError(
            f"Unexpected split counts: train={len(train_paths)}, val={len(val_paths)}, guard={len(guard_paths)}"
        )
    if train_paths & guard_paths or val_paths & guard_paths:
        raise RuntimeError("Guard samples overlap train or val split; aborting YOLO cache export.")

    train_dataset = TriAirDataset(args.data, mode="rgbte", split_file=train_split)
    val_dataset = TriAirDataset(args.data, mode="rgbte", split_file=val_split)
    train_rows, train_hashes, train_notes = export_split(train_dataset, "train", cache_dir)
    val_rows, val_hashes, val_notes = export_split(val_dataset, "val", cache_dir)

    if len(train_rows) != 7439 or len(val_rows) != 2213:
        raise RuntimeError(f"Export count mismatch: train={len(train_rows)}, val={len(val_rows)}")
    overlap = set(train_hashes) & set(val_hashes)
    if overlap:
        raise RuntimeError(f"RGB-content train/val overlap after export is nonzero: {len(overlap)}")

    yaml_path = cache_dir / "triair_yolo11n_rgb.yaml"
    write_yaml(yaml_path, cache_dir)
    write_csv(cache_dir / "export_manifest.csv", train_rows + val_rows)
    write_protocol(
        protocol_path,
        version_info(ultralytics),
        train_rows,
        val_rows,
        len(overlap),
        yaml_path,
        checkpoint_source,
        train_notes + val_notes,
    )
    print(f"Saved cache: {cache_dir}")
    print(f"Saved YAML: {yaml_path}")
    print(f"Saved protocol: {protocol_path}")


if __name__ == "__main__":
    main()
