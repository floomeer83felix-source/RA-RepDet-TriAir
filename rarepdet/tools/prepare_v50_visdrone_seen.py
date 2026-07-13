#!/usr/bin/env python
"""Audit, source-lock, manifest, and convert the local V50 dataset."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys

from PIL import Image
import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_SPLITS = {
    "train": "VisDrone2019-DET-train",
    "devval": "VisDrone2019-DET-val",
    "test": "VisDrone2019-DET-test-dev",
}
LOCAL_SPLITS = {"train": "train", "devval": "val", "test": "test"}
NAMES = {
    0: "pedestrian",
    1: "people",
    2: "bicycle",
    3: "car",
    4: "van",
    5: "truck",
    6: "tricycle",
    7: "awning-tricycle",
    8: "bus",
    9: "motor",
}
SEEN_IDS = {0, 3, 4, 5, 8, 9}
VEHICLE_YOLO_IDS = {3, 4, 5, 8}
VEHICLE_ORIGINAL_IDS = {value + 1 for value in VEHICLE_YOLO_IDS}
FILENAME_PATTERN = re.compile(r"^(\d{7})_(\d+)_d_(\d+)$")


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_hash(records):
    digest = hashlib.sha256()
    for record in sorted(records, key=lambda item: item["path"]):
        digest.update(record["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(record["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def write_json(path, value, *, compact=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if compact:
        content = json.dumps(value, sort_keys=True, separators=(",", ":"))
    else:
        content = json.dumps(value, indent=2, sort_keys=True)
    path.write_text(content + "\n", encoding="utf-8")


def git_value(*args):
    return subprocess.check_output(
        ["git", *args], cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def package_version(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "NA"


def cache_header(path):
    data = path.read_bytes()
    if data[:6] != b"\x93NUMPY":
        return {"sha256": hashlib.sha256(data).hexdigest(), "format": "unknown"}
    major, minor = data[6], data[7]
    if major == 1:
        header_length = struct.unpack("<H", data[8:10])[0]
        header_start = 10
    else:
        header_length = struct.unpack("<I", data[8:12])[0]
        header_start = 12
    header = data[header_start : header_start + header_length].decode("latin1").strip()
    payload = data[header_start + header_length :]
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "format": "NumPy object array containing a pickle payload",
        "npy_version": [major, minor],
        "header": header,
        "payload_prefix_hex": payload[:16].hex(),
        "safety": "inspected as raw bytes only; never unpickled",
    }


def parse_yolo(path):
    rows = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) != 5:
            raise ValueError(f"{path}:{line_number}: expected five fields")
        class_value = float(fields[0])
        if not class_value.is_integer():
            raise ValueError(f"{path}:{line_number}: class is not an integer")
        values = [float(value) for value in fields[1:]]
        if not all(0.0 <= value <= 1.0 for value in values):
            raise ValueError(f"{path}:{line_number}: normalized box outside [0,1]")
        if values[2] <= 0.0 or values[3] <= 0.0:
            raise ValueError(f"{path}:{line_number}: non-positive box")
        rows.append((int(class_value), *values))
    return rows


def parse_original(path):
    rows = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.strip().rstrip(",")
        if not line:
            continue
        fields = [value.strip() for value in line.split(",")]
        if len(fields) != 8:
            raise ValueError(f"{path}:{line_number}: expected eight comma-separated fields")
        x, y, width, height, score, category, truncation, occlusion = map(float, fields)
        rows.append(
            {
                "bbox": [x, y, width, height],
                "score": score,
                "category_id": int(category),
                "truncation": int(truncation),
                "occlusion": int(occlusion),
            }
        )
    return rows


def expected_seen_label(source_label, split):
    output = []
    for raw_line in source_label.read_text(encoding="utf-8").splitlines():
        fields = raw_line.strip().split()
        if len(fields) != 5:
            continue
        class_id = int(float(fields[0]))
        if split == "train" and class_id not in SEEN_IDS:
            continue
        output.append(" ".join(fields))
    return "\n".join(output)


def convert_split(root, source_root, output_dir, manifest_path, split):
    entries = [
        line.strip().replace("\\", "/")
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    source_name = SOURCE_SPLITS[split]
    annotations_dir = source_root / source_name / "annotations"
    images = []
    annotations = []
    annotation_id = 1
    positive_count = 0
    ignored_count = 0
    clipped_count = 0
    dropped_nonpositive_count = 0

    for image_id, relative_name in enumerate(entries, 1):
        image_path = root / relative_name
        with Image.open(image_path) as image:
            width, height = image.size
        images.append(
            {
                "id": image_id,
                "file_name": relative_name,
                "width": width,
                "height": height,
            }
        )
        original_path = annotations_dir / f"{image_path.stem}.txt"
        for item in parse_original(original_path):
            x, y, box_width, box_height = item["bbox"]
            x1 = max(0.0, min(float(width), x))
            y1 = max(0.0, min(float(height), y))
            x2 = max(0.0, min(float(width), x + box_width))
            y2 = max(0.0, min(float(height), y + box_height))
            clipped = [x1, y1, max(0.0, x2 - x1), max(0.0, y2 - y1)]
            if clipped[2] <= 0.0 or clipped[3] <= 0.0:
                dropped_nonpositive_count += 1
                continue
            if any(abs(a - b) > 1e-9 for a, b in zip(clipped, item["bbox"])):
                clipped_count += 1

            is_ignore = item["score"] == 0 or item["category_id"] == 0
            is_positive = item["score"] > 0 and item["category_id"] in VEHICLE_ORIGINAL_IDS
            if not is_ignore and not is_positive:
                continue

            annotations.append(
                {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": 1,
                    "bbox": clipped,
                    "area": clipped[2] * clipped[3],
                    "iscrowd": 1 if is_ignore else 0,
                    "ignore": 1 if is_ignore else 0,
                    "source_category_id": item["category_id"],
                    "source_score": item["score"],
                    "truncation": item["truncation"],
                    "occlusion": item["occlusion"],
                }
            )
            annotation_id += 1
            if is_ignore:
                ignored_count += 1
            else:
                positive_count += 1

    output = {
        "info": {
            "description": "V50 local VisDrone-SEEN four-wheel vehicle mapping",
            "mapping": "YOLO IDs 3 car, 4 van, 5 truck, 8 bus -> vehicle",
            "ignored_regions": "source score=0 or category=0 -> COCO crowd/ignore",
        },
        "licenses": [],
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": "vehicle"}],
    }
    output_path = output_dir / "converted_annotations" / f"{split}.json"
    write_json(output_path, output, compact=True)
    return {
        "path": str(output_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "sha256": file_sha256(output_path),
        "images": len(images),
        "positive_vehicle_boxes": positive_count,
        "ignored_regions": ignored_count,
        "clipped_source_boxes": clipped_count,
        "dropped_nonpositive_source_boxes": dropped_nonpositive_count,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=r"D:\datasets\visdrone_seen")
    parser.add_argument("--source-data", default=r"D:\datasets\visdrone")
    parser.add_argument(
        "--generator-script", default=r"E:\yolo\yolo26-e\create_visdrone_seen.py"
    )
    parser.add_argument("--triair-data", default=r"D:\download\triair")
    parser.add_argument("--out", default="runs/v50_visdrone_seen")
    args = parser.parse_args()

    root = Path(args.data).expanduser().resolve()
    source_root = Path(args.source_data).expanduser().resolve()
    generator_script = Path(args.generator_script).expanduser().resolve()
    triair_root = Path(args.triair_data).expanduser().resolve()
    output_dir = Path(args.out)
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir = output_dir / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    for required in (root, source_root, generator_script):
        if not required.exists():
            raise FileNotFoundError(required)

    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    audit = {
        "generated_at": generated_at,
        "dataset_root": str(root),
        "source_root": str(source_root),
        "generator_script": str(generator_script),
        "generator_script_sha256": file_sha256(generator_script),
        "local_yaml_sha256": file_sha256(root / "VisDrone_seen.yaml"),
        "modalities": {
            "rgb": True,
            "thermal": False,
            "event": False,
            "decision": "RGB-only; no aligned additional modality files are present",
        },
        "local_readme": None,
        "local_license": None,
        "provider_statement": (
            "The target directory has no README/license. A timestamp-adjacent local generator "
            "script identifies D:/datasets/visdrone as its source; exact generation validation "
            "is recorded below."
        ),
        "seen_meaning": (
            "The generator keeps YOLO IDs 0,3,4,5,8,9 in train labels and leaves val/test "
            "labels unchanged. Images are not filtered."
        ),
        "annotation_format": "YOLO normalized: class_id center_x center_y width height",
        "original_annotation_format": (
            "8-column VisDrone-style rows: x,y,width,height,score,category,truncation,occlusion"
        ),
        "source_categories": {str(key): value for key, value in NAMES.items()},
        "splits": {},
        "split_intersections": {},
        "cache_files": {},
    }

    image_records = []
    label_records = []
    image_hash_paths = defaultdict(list)
    split_stems = {}
    split_sequences = {}
    generation_image_mismatches = []
    generation_label_mismatches = []

    for split, local_name in LOCAL_SPLITS.items():
        image_dir = root / "images" / local_name
        label_dir = root / "labels" / local_name
        source_name = SOURCE_SPLITS[split]
        source_images = source_root / source_name / "images"
        source_labels = source_root / source_name / "labels"
        source_original = source_root / source_name / "annotations"
        images = sorted(image_dir.glob("*.jpg"))
        labels = sorted(label_dir.glob("*.txt"))
        image_stems = {path.stem for path in images}
        label_stems = {path.stem for path in labels}
        split_stems[split] = image_stems
        sequences = Counter()
        for stem in image_stems:
            match = FILENAME_PATTERN.fullmatch(stem)
            if match:
                sequences[match.group(1)] += 1
        split_sequences[split] = set(sequences)

        class_counts = Counter()
        original_categories = Counter()
        original_scores = Counter()
        truncation = Counter()
        occlusion = Counter()
        dimensions = Counter()
        modes = Counter()
        formats = Counter()
        empty_labels = 0
        boxes_crossing_edges = 0

        manifest_entries = []
        for image_path in images:
            relative = image_path.relative_to(root).as_posix()
            manifest_entries.append(relative)
            with Image.open(image_path) as image:
                dimensions[f"{image.width}x{image.height}"] += 1
                modes[image.mode] += 1
                formats[image.format] += 1
                image.verify()
            digest = file_sha256(image_path)
            image_record = {"path": relative, "sha256": digest, "bytes": image_path.stat().st_size}
            image_records.append(image_record)
            image_hash_paths[digest].append(relative)

            source_image = source_images / image_path.name
            if not source_image.is_file() or file_sha256(source_image) != digest:
                generation_image_mismatches.append(relative)

            source_label = source_labels / f"{image_path.stem}.txt"
            current_label = label_dir / f"{image_path.stem}.txt"
            if not source_label.is_file() or not current_label.is_file():
                generation_label_mismatches.append(relative)
            elif current_label.read_text(encoding="utf-8") != expected_seen_label(
                source_label, local_name
            ):
                generation_label_mismatches.append(relative)

            original_path = source_original / f"{image_path.stem}.txt"
            if not original_path.is_file():
                raise FileNotFoundError(original_path)
            for item in parse_original(original_path):
                original_categories[item["category_id"]] += 1
                original_scores[str(item["score"])] += 1
                truncation[item["truncation"]] += 1
                occlusion[item["occlusion"]] += 1

        manifest_path = manifests_dir / f"{split}.txt"
        manifest_path.write_text("\n".join(manifest_entries) + "\n", encoding="utf-8")

        for label_path in labels:
            relative = label_path.relative_to(root).as_posix()
            digest = file_sha256(label_path)
            label_records.append({"path": relative, "sha256": digest, "bytes": label_path.stat().st_size})
            rows = parse_yolo(label_path)
            if not rows:
                empty_labels += 1
            for class_id, center_x, center_y, width, height in rows:
                class_counts[class_id] += 1
                if (
                    center_x - width / 2.0 < -1e-7
                    or center_y - height / 2.0 < -1e-7
                    or center_x + width / 2.0 > 1.0 + 1e-7
                    or center_y + height / 2.0 > 1.0 + 1e-7
                ):
                    boxes_crossing_edges += 1

        audit["splits"][split] = {
            "local_directory": local_name,
            "source_directory": source_name,
            "images": len(images),
            "labels": len(labels),
            "test_annotations_available": split != "test" or len(labels) == len(images),
            "missing_labels": sorted(image_stems - label_stems),
            "orphan_labels": sorted(label_stems - image_stems),
            "empty_labels": empty_labels,
            "yolo_class_counts": dict(sorted(class_counts.items())),
            "original_category_counts": dict(sorted(original_categories.items())),
            "original_score_counts": dict(sorted(original_scores.items())),
            "truncation_counts": dict(sorted(truncation.items())),
            "occlusion_counts": dict(sorted(occlusion.items())),
            "boxes_crossing_normalized_edges": boxes_crossing_edges,
            "candidate_sequence_prefix_count": len(sequences),
            "dimensions": dict(sorted(dimensions.items())),
            "modes": dict(modes),
            "formats": dict(formats),
            "manifest": str(manifest_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "manifest_sha256": file_sha256(manifest_path),
        }

    split_names = list(LOCAL_SPLITS)
    for index, first in enumerate(split_names):
        for second in split_names[index + 1 :]:
            audit["split_intersections"][f"{first}-{second}"] = {
                "same_stem": len(split_stems[first] & split_stems[second]),
                "candidate_sequence_prefix": len(
                    split_sequences[first] & split_sequences[second]
                ),
                "candidate_sequence_values": sorted(
                    split_sequences[first] & split_sequences[second]
                ),
            }

    for cache_path in sorted((root / "labels").glob("*.cache")):
        audit["cache_files"][str(cache_path.relative_to(root)).replace("\\", "/")] = cache_header(
            cache_path
        )

    duplicate_groups = [paths for paths in image_hash_paths.values() if len(paths) > 1]
    cross_split_duplicate_groups = [
        paths
        for paths in duplicate_groups
        if len({Path(path).parts[1] for path in paths}) > 1
    ]
    audit["exact_content"] = {
        "image_tree_sha256": tree_hash(image_records),
        "annotation_tree_sha256": tree_hash(label_records),
        "duplicate_image_groups": duplicate_groups,
        "cross_split_duplicate_image_groups": cross_split_duplicate_groups,
        "generation_image_mismatches": generation_image_mismatches,
        "generation_label_mismatches": generation_label_mismatches,
    }

    triair_images = sorted((triair_root / "data" / "images").glob("*.npy"))
    triair_sizes = Counter(path.stat().st_size for path in triair_images)
    audit["triair_cross_check"] = {
        "inventory_count": len(triair_images),
        "file_size_counts": dict(triair_sizes),
        "sample_headers_checked": min(5, len(triair_images)),
        "sample_shape": [301, 391, 5] if triair_images else None,
        "sample_dtype": "uint8" if triair_images else None,
        "conclusion": (
            "Raw-byte identity is impossible because every TriAir item is an NPY file and every "
            "V50 item is a JPEG. Sampled TriAir decoded dimensions (391x301) do not overlap any "
            "V50 dimension; a full cross-format perceptual duplicate claim is not made."
        ),
    }

    write_json(output_dir / "image_file_hashes.json", image_records)
    write_json(output_dir / "annotation_file_hashes.json", label_records)
    write_json(output_dir / "dataset_audit.json", audit)

    class_mapping = {
        "generated_at": generated_at,
        "target_category": {"id": 1, "name": "vehicle"},
        "definition": "four-wheel road vehicles, consistent with the project DroneVehicle mapping",
        "source_categories": [
            {
                "yolo_id": class_id,
                "original_id": class_id + 1,
                "name": name,
                "mapping": "vehicle" if class_id in VEHICLE_YOLO_IDS else "background/non-target",
            }
            for class_id, name in NAMES.items()
        ],
        "positive_yolo_ids": sorted(VEHICLE_YOLO_IDS),
        "positive_original_ids": sorted(VEHICLE_ORIGINAL_IDS),
        "ignored_regions": (
            "Original score=0 or category=0 boxes become category 1 COCO crowd/ignore regions "
            "for evaluation; they are not positive training boxes."
        ),
        "flags": (
            "Truncation and occlusion are retained as annotation attributes and are not used to "
            "discard otherwise valid vehicle boxes."
        ),
    }
    write_json(output_dir / "class_mapping.json", class_mapping)

    converted = {}
    for split in LOCAL_SPLITS:
        converted[split] = convert_split(
            root,
            source_root,
            output_dir,
            manifests_dir / f"{split}.txt",
            split,
        )

    split_manifest = {
        "generated_at": generated_at,
        "rule": "source-provided train/val/test-dev partition copied by the local generator",
        "test_access_rule": (
            "test is inaccessible to tuning, threshold selection, checkpoint selection, run "
            "continuation, or architecture selection"
        ),
        "splits": {
            split: {
                "path": str((manifests_dir / f"{split}.txt").relative_to(PROJECT_ROOT)).replace(
                    "\\", "/"
                ),
                "sha256": file_sha256(manifests_dir / f"{split}.txt"),
                "images": audit["splits"][split]["images"],
            }
            for split in LOCAL_SPLITS
        },
        "candidate_sequence_overlap": audit["split_intersections"],
        "exact_cross_split_duplicates": len(cross_split_duplicate_groups),
    }
    write_json(output_dir / "split_manifest.json", split_manifest)

    audit_md = f"""# V50 Dataset Audit

- Audit time: `{generated_at}`
- Target root: `{root}`
- Local source root: `{source_root}`
- Generator: `{generator_script}` (`{audit['generator_script_sha256']}`)
- Decision: RGB-only. No thermal or event files are present.
- Local README/license: absent in the target directory.
- Annotation format: five-column normalized YOLO labels. The linked source retains eight-column original annotations.
- `seen` meaning: train labels retain IDs `{sorted(SEEN_IDS)}`; val/test remain unchanged; no images are removed.
- Generation validation: image mismatches `{len(generation_image_mismatches)}`; label mismatches `{len(generation_label_mismatches)}`.

## Partitions

| split | images | labels | empty labels | candidate sequence prefixes |
|---|---:|---:|---:|---:|
"""
    for split in LOCAL_SPLITS:
        item = audit["splits"][split]
        audit_md += (
            f"| {split} | {item['images']} | {item['labels']} | {item['empty_labels']} | "
            f"{item['candidate_sequence_prefix_count']} |\n"
        )
    audit_md += f"""

## Integrity

- Exact cross-partition image duplicates: `{len(cross_split_duplicate_groups)}`.
- Within-partition exact duplicate image groups: `{len(duplicate_groups)}`.
- Train/devval candidate filename-prefix overlap: `{audit['split_intersections']['train-devval']['candidate_sequence_prefix']}` groups. These prefixes are leakage warnings, not asserted video IDs; the source-provided split is retained and the limitation must be reported.
- YOLO boxes are syntactically valid. Boxes crossing normalized image edges are clipped only in derived COCO annotations; source files are unchanged.
- Test labels and linked original annotations are locally available.
- `.cache` files are NumPy object arrays with pickle payloads. They were inspected only as raw bytes and were never unpickled.

## Provenance Boundary

The target is a locally generated derivative whose file counts and source directory names match the VisDrone2019-DET train/val/test-dev layout. It must be described as the audited local VisDrone-SEEN derivative, not as an untouched official release. The local generator is unversioned, so its exact SHA256 is the provenance pin.
"""
    (output_dir / "dataset_audit.md").write_text(audit_md, encoding="utf-8")

    mapping_rows = "\n".join(
        f"| {item['yolo_id']} | {item['original_id']} | {item['name']} | {item['mapping']} |"
        for item in class_mapping["source_categories"]
    )
    (output_dir / "class_mapping.md").write_text(
        "# V50 Class Mapping\n\n"
        "The frozen target is four-wheel road-vehicle detection: car, van, truck, and bus map "
        "to one foreground class. This matches the existing project mapping used for "
        "DroneVehicle; pedestrian, people, bicycle, tricycle, awning-tricycle, and motor remain "
        "non-target categories.\n\n"
        "| YOLO ID | original ID | name | mapping |\n|---:|---:|---|---|\n"
        + mapping_rows
        + "\n\nOriginal score=0/category=0 regions are restored from linked source annotations as "
        "COCO crowd/ignore regions. Truncation and occlusion flags are preserved but do not "
        "remove valid vehicle boxes.\n",
        encoding="utf-8",
    )

    (output_dir / "split_integrity.md").write_text(
        "# V50 Split Integrity\n\n"
        f"- Exact cross-split image duplicate groups: `{len(cross_split_duplicate_groups)}`.\n"
        f"- Same-stem train/devval overlap: `{audit['split_intersections']['train-devval']['same_stem']}`.\n"
        f"- Candidate filename-prefix train/devval overlap: `{audit['split_intersections']['train-devval']['candidate_sequence_prefix']}`.\n"
        "- Frozen rule: preserve the local generator's source train/val/test-dev partition.\n"
        "- Limitation: candidate prefix overlap prevents a claim of sequence-disjoint external testing.\n"
        "- Test is reserved until all settings and RGB checkpoints are frozen.\n",
        encoding="utf-8",
    )

    checkpoints = {
        "matched_early_seed0": PROJECT_ROOT
        / "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt",
        "matched_early_seed1": PROJECT_ROOT
        / "runs/v41_q1_upgrade/seed1/matched_early_seed1/weights/best.pt",
        "matched_early_seed2": PROJECT_ROOT
        / "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed2/weights/best.pt",
        "reliability_p015_seed0": PROJECT_ROOT
        / "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt",
        "reliability_p015_seed1": PROJECT_ROOT
        / "runs/v41_q1_upgrade/seed1/reliability_p015_seed1/weights/best.pt",
        "reliability_p015_seed2": PROJECT_ROOT
        / "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed2/weights/best.pt",
    }
    code_paths = [
        PROJECT_ROOT / "datasets/visdrone_seen_dataset.py",
        PROJECT_ROOT / "rarepdet/models/rgb_fcos.py",
        PROJECT_ROOT / "rarepdet/tools/prepare_v50_visdrone_seen.py",
        PROJECT_ROOT / "rarepdet/tools/eval_v50_visdrone_seen.py",
        PROJECT_ROOT / "rarepdet/train_visdrone_rgb.py",
        PROJECT_ROOT / "rarepdet/v50_coco.py",
        PROJECT_ROOT / "rarepdet/models/early_fusion_fcos.py",
        PROJECT_ROOT / "rarepdet/models/repvit_fpn_backbone.py",
    ]
    source_lock = {
        "generated_at": generated_at,
        "starting_commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dataset_root": str(root),
        "source_root": str(source_root),
        "generator_script": str(generator_script),
        "generator_script_sha256": file_sha256(generator_script),
        "metadata_hashes": {
            "target_yaml": file_sha256(root / "VisDrone_seen.yaml"),
            "image_hash_inventory": file_sha256(output_dir / "image_file_hashes.json"),
            "annotation_hash_inventory": file_sha256(output_dir / "annotation_file_hashes.json"),
            "class_mapping": file_sha256(output_dir / "class_mapping.json"),
            "split_manifest": file_sha256(output_dir / "split_manifest.json"),
        },
        "manifests": {
            split: file_sha256(manifests_dir / f"{split}.txt") for split in LOCAL_SPLITS
        },
        "converted_annotations": converted,
        "checkpoints": {
            name: {"path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"), "sha256": file_sha256(path)}
            for name, path in checkpoints.items()
        },
        "code_hashes": {
            str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"): file_sha256(path)
            for path in code_paths
            if path.is_file()
        },
        "environment": {
            "python": platform.python_version(),
            "pytorch": torch.__version__,
            "torchvision": package_version("torchvision"),
            "timm": package_version("timm"),
            "pycocotools": package_version("pycocotools"),
            "torch_cuda": str(torch.version.cuda),
            "cuda_available": torch.cuda.is_available(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NA",
            "os": platform.platform(),
        },
        "preprocessing": (
            "PIL RGB -> float32 / 255.0. Zero-shot appends thermal=0.0 and event=0.0 "
            "after scaling, before the frozen torchvision fixed-size 640 transform."
        ),
        "thresholds": {
            "detector_score": 0.001,
            "nms": 0.6,
            "detections_per_image": 100,
            "coco_iou": "0.50:0.05:0.95",
        },
        "rgb_checkpoint_selection": "highest devval canonical COCO AP50; first epoch wins exact ties",
        "test_access_rule": split_manifest["test_access_rule"],
        "claim_boundary": (
            "RGB-only domain-shift/missing-modality stress evidence; not tri-modal external "
            "validation or physical sensor-failure evidence"
        ),
    }
    write_json(output_dir / "source_lock_v50.json", source_lock)

    checkpoint_lines = "\n".join(
        f"- `{name}`: `{item['path']}` `{item['sha256']}`"
        for name, item in source_lock["checkpoints"].items()
    )
    source_lock_md = f"""# V50 Source Lock

- Starting commit: `{source_lock['starting_commit']}`
- Branch: `{source_lock['branch']}`
- Dataset: `{root}`
- Source mirror: `{source_root}`
- Generator SHA256: `{source_lock['generator_script_sha256']}`
- Mapping SHA256: `{source_lock['metadata_hashes']['class_mapping']}`
- Split-manifest SHA256: `{source_lock['metadata_hashes']['split_manifest']}`
- Adapter: RGB scaled to `[0,1]`, then append thermal/event channels fixed at `0.0` for frozen-checkpoint stress evaluation.
- Frozen detector settings: score `0.001`, NMS `0.6`, max detections `100`.
- RGB selection: highest devval canonical COCO AP50; first epoch wins exact ties.
- Test rule: no test access before adapter, mapping, evaluator, thresholds, and all three RGB checkpoints are frozen.

## Frozen Checkpoints

{checkpoint_lines}

## Boundary

The data are an audited local RGB-only VisDrone-SEEN derivative. Results can support only RGB-only domain-shift and zero-filled missing-modality stress claims. They cannot validate thermal/event generalization, calibrated reliability, a physical sensor fault, or a sequence-disjoint independent test.
"""
    (output_dir / "source_lock_v50.md").write_text(source_lock_md, encoding="utf-8")

    print(json.dumps({
        "audit": str(output_dir / "dataset_audit.json"),
        "image_mismatches": len(generation_image_mismatches),
        "label_mismatches": len(generation_label_mismatches),
        "cross_split_duplicates": len(cross_split_duplicate_groups),
        "converted": converted,
    }, indent=2))


if __name__ == "__main__":
    main()
