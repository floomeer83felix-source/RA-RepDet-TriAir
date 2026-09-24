#!/usr/bin/env python3
"""Read-only M3OT RGB/IR/vehicle audit and pretraining visual contact sheets."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.m3ot_dataset import M3OTExternalDataset
from tools.prepare_m3ot import inspect_one


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frame_identity(row: dict) -> tuple[str, str, str]:
    return row["group"], row["sequence"], row["frame"]


def validate_manifest_records(train: list[dict], val: list[dict]) -> dict:
    identities = []
    for split, records in (("train", train), ("val", val)):
        seen = set()
        for row in records:
            if row["split"] != split:
                raise ValueError(f"Wrong record split: {row['sample_id']}")
            key = frame_identity(row)
            if key in seen:
                raise ValueError(f"Duplicate {split} frame identity: {key}")
            seen.add(key)
            width, height = row["width"], row["height"]
            if (width, height) != (640, 512):
                raise ValueError(f"Unexpected dimensions at {row['sample_id']}")
            for box in row["boxes_xywh"]:
                if len(box) != 4 or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in box):
                    raise ValueError(f"Malformed box at {row['sample_id']}")
                x, y, w, h = box
                if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
                    raise ValueError(f"Out-of-bounds box at {row['sample_id']}: {box}")
        identities.append(seen)
    overlap = identities[0] & identities[1]
    if overlap:
        raise ValueError(f"Train/val frame overlap: {sorted(overlap)[:5]}")
    return {"train_frame_identities": len(identities[0]),
            "val_frame_identities": len(identities[1]),
            "cross_split_frame_overlap": 0}


def font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def render_pair(dataset: M3OTExternalDataset, index: int, output: Path) -> None:
    row = dataset.get_record(index)
    rgb, thermal = dataset.read_images(index)
    rgb_panel = Image.fromarray(rgb, mode="RGB")
    ir_panel = Image.fromarray(thermal, mode="L").convert("RGB")
    draw = ImageDraw.Draw(rgb_panel)
    for box in dataset.boxes_xyxy(index):
        draw.rectangle(tuple(float(x) for x in box), outline=(0, 255, 60), width=2)
    canvas = Image.new("RGB", (1280, 552), "white")
    canvas.paste(rgb_panel, (0, 40))
    canvas.paste(ir_panel, (640, 40))
    heading = ImageDraw.Draw(canvas)
    heading.text((10, 8), f"{row['sample_id']}  RGB + {len(row['boxes_xywh'])} vehicle GT", fill="black", font=font(19))
    heading.text((650, 8), "Paired IR (RGB boxes are not overlaid)", fill="black", font=font(19))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.data_root.resolve(strict=True)
    out = args.output_dir.resolve()
    if out.exists():
        parser.error(f"Refusing to overwrite existing audit: {out}")

    manifests = {}
    audits = []
    for split in ("train", "val"):
        records = {}
        for group in ("1", "2"):
            audit, group_records = inspect_one(root, group, split)
            if audit["invalid_bbox_count"] or audit["outside_bbox_count"] or audit["orphan_annotations"]:
                raise ValueError(f"Invalid official {group}/{split} annotations: {audit}")
            if audit["rgb_thermal_size_mismatches"] or audit["pairs_with_official_coco"] != audit["paired_frames"]:
                raise ValueError(f"Broken {group}/{split} pairing: {audit}")
            audits.append(audit)
            records.update(group_records)
        manifests[split] = {"source": str(root), "split": split,
                            "records": [records[key] for key in sorted(records)]}
    train = manifests["train"]["records"]
    val = manifests["val"]["records"]
    overlap = validate_manifest_records(train, val)
    totals = {split: {"images": len(manifests[split]["records"]),
                      "boxes": sum(len(row["boxes_xywh"]) for row in manifests[split]["records"]),
                      "zero_gt": sum(not row["boxes_xywh"] for row in manifests[split]["records"])}
              for split in ("train", "val")}
    if (totals["train"]["images"], totals["train"]["boxes"],
            totals["val"]["images"], totals["val"]["boxes"]) != (8630, 111678, 1200, 13781):
        raise ValueError(f"Dataset count mismatch: {totals}")

    out.mkdir(parents=True)
    manifest_hashes = {}
    selected = []
    rng = random.Random(8404)
    for split in ("train", "val"):
        path = out / f"{split}_manifest.json"
        path.write_text(json.dumps(manifests[split], indent=2) + "\n", encoding="utf-8")
        manifest_hashes[split] = sha256(path)
        dataset = M3OTExternalDataset(path, model_type="early", expected_split=split)
        for group in ("1", "2"):
            indices = [i for i, row in enumerate(dataset.records) if row["group"] == group]
            for index in sorted(rng.sample(indices, 2)):
                row = dataset.get_record(index)
                image_file = out / "visual_samples" / f"{split}_{group}_{row['sequence']}_{row['frame']}.png"
                render_pair(dataset, index, image_file)
                selected.append({"sample_id": row["sample_id"], "rgb": row["rgb"],
                                 "thermal": row["thermal"], "gt_boxes": len(row["boxes_xywh"]),
                                 "figure": str(image_file)})
    summary = {"status": "CPU_AUDIT_COMPLETE_VISUAL_REVIEW_PENDING",
               "source_root": str(root), "totals": totals, "split_integrity": overlap,
               "group_audits": audits, "manifest_sha256": manifest_hashes,
               "visual_samples": selected,
               "source_files_modified": False, "test_split_accessed": False}
    (out / "pairing_audit.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Train: {totals['train']}; val: {totals['val']}; overlap: 0")
    print(f"Visual samples: {len(selected)}; audit: {out / 'pairing_audit.json'}")


if __name__ == "__main__":
    main()
