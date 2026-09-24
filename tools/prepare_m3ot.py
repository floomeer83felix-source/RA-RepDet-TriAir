#!/usr/bin/env python3
"""Audit local M3OT pairs against official RGB COCO annotations without editing data."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random

from PIL import Image


SPLITS = ("train", "val", "test")
GROUPS = ("1", "2")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frame_map(root: Path, group: str, modality: str, split: str) -> dict[tuple[str, str], Path]:
    base = root / group / modality / split
    if not base.is_dir():
        raise FileNotFoundError(base)
    result = {}
    for sequence in sorted(base.iterdir()):
        if not sequence.is_dir():
            continue
        name = sequence.name.removesuffix("T") if modality == "ir" else sequence.name
        for path in sorted((sequence / "img1").glob("*")):
            if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
                continue
            key = (name, path.stem)
            if key in result:
                raise ValueError(f"Ambiguous frame key {group}/{split}/{key}: {result[key]} and {path}")
            result[key] = path
    return result


def coco_key(image: dict) -> tuple[str, str]:
    parts = Path(image["file_name"].replace("\\", "/")).parts
    if len(parts) < 3 or parts[-2] != "img1":
        raise ValueError(f"Unrecognized official COCO image path: {image['file_name']}")
    return parts[-3], Path(parts[-1]).stem


def inspect_one(root: Path, group: str, split: str) -> tuple[dict, dict]:
    rgb = frame_map(root, group, "rgb", split)
    ir = frame_map(root, group, "ir", split)
    paired = sorted(set(rgb) & set(ir))
    annotation_file = root / "Annotations" / group / "rgb" / f"{split}_cocoformat.json"
    official = json.loads(annotation_file.read_text(encoding="utf-8"))
    categories = official.get("categories", [])
    if categories != [{"id": 1, "name": "vehicle"}]:
        raise ValueError(f"Unexpected RGB categories in {annotation_file}: {categories}")

    images = {}
    images_by_id = {}
    ids = set()
    for image in official["images"]:
        key = coco_key(image)
        if key in images or image["id"] in ids:
            raise ValueError(f"Duplicate COCO image key or ID in {annotation_file}: {key}")
        images[key] = image
        images_by_id[image["id"]] = image
        ids.add(image["id"])

    boxes_by_image = defaultdict(list)
    invalid, outside, nonvehicle, orphan = [], [], 0, 0
    for ann in official["annotations"]:
        if ann.get("category_id") != 1:
            nonvehicle += 1
            continue
        if ann.get("image_id") not in ids:
            orphan += 1
            continue
        box = ann.get("bbox", [])
        if len(box) != 4 or not all(isinstance(v, (int, float)) for v in box):
            invalid.append(ann.get("id"))
            continue
        x, y, width, height = map(float, box)
        if not all(math.isfinite(v) for v in (x, y, width, height)) or width <= 0 or height <= 0:
            invalid.append(ann.get("id"))
            continue
        image = images_by_id[ann["image_id"]]
        if x < 0 or y < 0 or x + width > image["width"] or y + height > image["height"]:
            outside.append(ann.get("id"))
        boxes_by_image[ann["image_id"]].append(ann)

    pair_with_coco = [key for key in paired if key in images]
    rgb_dims, ir_dims, unequal_dims = Counter(), Counter(), 0
    for key in paired:
        with Image.open(rgb[key]) as source_rgb, Image.open(ir[key]) as source_ir:
            rgb_dims[f"{source_rgb.width}x{source_rgb.height}"] += 1
            ir_dims[f"{source_ir.width}x{source_ir.height}"] += 1
            unequal_dims += source_rgb.size != source_ir.size
            if key in images and source_rgb.size != (images[key]["width"], images[key]["height"]):
                raise ValueError(f"COCO/RGB size mismatch: {rgb[key]}")

    paired_gt = sum(len(boxes_by_image[images[key]["id"]]) for key in pair_with_coco)
    audit = {
        "group": group,
        "split": split,
        "official_rgb_coco": str(annotation_file),
        "official_rgb_coco_sha256": sha256(annotation_file),
        "rgb_frames": len(rgb),
        "thermal_frames": len(ir),
        "paired_frames": len(paired),
        "unpaired_rgb": len(set(rgb) - set(ir)),
        "unpaired_thermal": len(set(ir) - set(rgb)),
        "unpaired_rgb_examples": [list(key) for key in sorted(set(rgb) - set(ir))[:10]],
        "unpaired_thermal_examples": [list(key) for key in sorted(set(ir) - set(rgb))[:10]],
        "official_coco_images": len(images),
        "pairs_with_official_coco": len(pair_with_coco),
        "paired_images_with_gt": sum(bool(boxes_by_image[images[key]["id"]]) for key in pair_with_coco),
        "paired_zero_gt_images": sum(not boxes_by_image[images[key]["id"]] for key in pair_with_coco),
        "paired_gt_boxes": paired_gt,
        "vehicles_per_paired_image": paired_gt / len(pair_with_coco) if pair_with_coco else 0,
        "invalid_bbox_count": len(invalid),
        "outside_bbox_count": len(outside),
        "invalid_bbox_examples": invalid[:10],
        "outside_bbox_examples": outside[:10],
        "nonvehicle_annotations": nonvehicle,
        "orphan_annotations": orphan,
        "rgb_resolutions": dict(rgb_dims),
        "thermal_resolutions": dict(ir_dims),
        "rgb_thermal_size_mismatches": unequal_dims,
        "rgb_coco_unmatched_keys": [list(key) for key in sorted(set(images) - set(rgb))[:10]],
    }
    records = {}
    for key in pair_with_coco:
        image = images[key]
        sample_id = f"{group}/{split}/{key[0]}/{key[1]}"
        records[sample_id] = {
            "sample_id": sample_id,
            "group": group,
            "split": split,
            "sequence": key[0],
            "frame": key[1],
            "rgb": str(rgb[key]),
            "thermal": str(ir[key]),
            "coco_image_id": image["id"],
            "width": image["width"],
            "height": image["height"],
            "boxes_xywh": [ann["bbox"] for ann in boxes_by_image[image["id"]]],
        }
    return audit, records


def write_report(path: Path, audits: list[dict], selected: str, data_root: Path) -> None:
    lines = ["M3OT read-only dataset audit", f"Dataset root: {data_root}", f"Evaluation split: {selected}",
             "Ground truth: official RGB COCO vehicle annotations; RGB is output coordinate system.",
             "Pairing key: group + actual local sequence name + exact frame stem; IR sequence suffix T removed.",
             "Original image and annotation files were not modified.", ""]
    for audit in audits:
        lines.append(f"{audit['group']}/{audit['split']}: {audit['paired_frames']} pairs, "
                     f"{audit['paired_gt_boxes']} GT boxes, {audit['paired_zero_gt_images']} zero-GT images, "
                     f"{audit['unpaired_rgb']} missing IR, {audit['unpaired_thermal']} missing RGB, "
                     f"{audit['invalid_bbox_count']} invalid boxes, {audit['outside_bbox_count']} outside boxes, "
                     f"RGB {audit['rgb_resolutions']}, IR {audit['thermal_resolutions']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--split", choices=SPLITS, default="test")
    parser.add_argument("--output-dir", type=Path, default=Path("results/m3ot_external"))
    parser.add_argument("--seed", type=int, default=8404)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    root = args.data_root.resolve(strict=True)
    out = args.output_dir.resolve()
    planned = [out / "data_audit.json", out / "data_audit.txt", out / "category_mapping.json",
               out / "evaluation_manifest.json", out / "sanity_sample_ids.json"]
    present = [path for path in planned if path.exists()]
    if present and not args.overwrite:
        parser.error(f"Output already exists; use --overwrite: {present}")

    audits, selected_records = [], {}
    for group in GROUPS:
        for split in SPLITS:
            audit, records = inspect_one(root, group, split)
            audits.append(audit)
            if split == args.split:
                selected_records.update(records)

    chosen = [audit for audit in audits if audit["split"] == args.split]
    if any(audit["invalid_bbox_count"] or audit["orphan_annotations"] or audit["rgb_thermal_size_mismatches"]
           or audit["pairs_with_official_coco"] != audit["paired_frames"] for audit in chosen):
        raise RuntimeError("Selected split violates the pairing/annotation contract; review the audit before evaluation")
    out.mkdir(parents=True, exist_ok=True)
    summary = {
        "data_root": str(root),
        "evaluation_split": args.split,
        "annotation_policy": "Official RGB COCO vehicle boxes, no label conversion or edits",
        "pairing_policy": "Local group/sequence/frame; remove terminal T from IR sequence name",
        "groups": audits,
        "evaluation_images": len(selected_records),
        "evaluation_gt_boxes": sum(len(row["boxes_xywh"]) for row in selected_records.values()),
        "evaluation_zero_gt_images": sum(not row["boxes_xywh"] for row in selected_records.values()),
        "config": {"seed": args.seed, "split": args.split},
    }
    rng = random.Random(args.seed)
    sample_ids = sorted(selected_records)
    sanity_ids = sorted(rng.sample(sample_ids, min(8, len(sample_ids))))
    for path, payload in ((planned[0], summary), (planned[2], {"official_category_id": 1,
                           "official_category_name": "vehicle", "torchvision_foreground_label": 1,
                           "excluded_categories": []}), (planned[3], {"source": str(root), "split": args.split,
                           "records": [selected_records[key] for key in sample_ids]}),
                           (planned[4], {"seed": args.seed, "sample_ids": sanity_ids})):
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(planned[1], audits, args.split, root)
    print(f"M3OT audit complete: {summary['evaluation_images']} {args.split} pairs, "
          f"{summary['evaluation_gt_boxes']} vehicle GT boxes, "
          f"{summary['evaluation_zero_gt_images']} zero-GT images")
    print(f"Audit: {planned[0]}")


if __name__ == "__main__":
    main()
