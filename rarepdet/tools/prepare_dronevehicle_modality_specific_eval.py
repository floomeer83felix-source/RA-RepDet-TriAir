#!/usr/bin/env python
"""Prepare locked DroneVehicle RGB-only / thermal-only external evaluation files.

This script does not run a model. It audits native RGB and IR streams separately
and writes deterministic horizontal-box GT files for zero-shot modality-specific
evaluation.
"""

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = PROJECT_ROOT / "reproducibility" / "external_dronevehicle_modality_specific"
VEHICLE_CLASSES = {"car", "truck", "bus", "van", "freight_car"}
CLASS_MAP = {name: "vehicle" for name in VEHICLE_CLASSES}


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_class(name):
    value = (name or "").strip().lower().replace(" ", "_")
    if value in {"feright_car", "ferightcar", "freight_car", "freightcar"}:
        return "freight_car"
    return value


def as_float(text):
    if text is None:
        return None
    try:
        value = float(str(text).strip())
    except Exception:
        return None
    return value if math.isfinite(value) else None


def polygon_area(points):
    if len(points) < 3:
        return 0.0
    total = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        total += x1 * y2 - x2 * y1
    return abs(total) * 0.5


def parse_polygon(poly):
    if poly is None:
        return None
    pairs = []
    idx = 1
    while True:
        x = as_float(poly.findtext(f"x{idx}"))
        y = as_float(poly.findtext(f"y{idx}"))
        if x is None and y is None:
            break
        if x is None or y is None:
            return None
        pairs.append((x, y))
        idx += 1
    if len(pairs) < 4 or polygon_area(pairs) <= 0:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    return [min(xs), min(ys), max(xs), max(ys)]


def parse_bndbox(bndbox):
    if bndbox is None:
        return None
    xmin = as_float(bndbox.findtext("xmin"))
    ymin = as_float(bndbox.findtext("ymin"))
    xmax = as_float(bndbox.findtext("xmax"))
    ymax = as_float(bndbox.findtext("ymax"))
    if None in (xmin, ymin, xmax, ymax):
        return None
    if xmax <= xmin or ymax <= ymin:
        return None
    return [xmin, ymin, xmax, ymax]


def clip_box(box, width, height):
    x1, y1, x2, y2 = box
    clipped = [
        max(0.0, min(float(width), x1)),
        max(0.0, min(float(height), y1)),
        max(0.0, min(float(width), x2)),
        max(0.0, min(float(height), y2)),
    ]
    if clipped[2] - clipped[0] <= 1.0 or clipped[3] - clipped[1] <= 1.0:
        return None
    return clipped


def parse_xml_to_record(xml_path, image_path, modality, image_width, image_height):
    root = ET.parse(xml_path).getroot()
    xml_width = int(float(root.findtext("size/width") or image_width))
    xml_height = int(float(root.findtext("size/height") or image_height))
    boxes = []
    object_rows = []
    invalid_rows = []
    ignored_rows = []
    raw_counter = Counter()
    mapped_counter = Counter()
    polygon_count = 0
    bndbox_count = 0

    for object_index, obj in enumerate(root.findall("object"), start=1):
        raw_class = (obj.findtext("name") or "").strip()
        normalized = normalize_class(raw_class)
        raw_counter[raw_class] += 1
        if normalized not in CLASS_MAP:
            ignored_rows.append(
                {
                    "modality": modality,
                    "image_id": image_path.stem,
                    "image_path": str(image_path),
                    "annotation_path": str(xml_path),
                    "object_index": object_index,
                    "raw_class": raw_class,
                    "normalized_class": normalized,
                    "reason": "unknown_or_unmapped_class",
                }
            )
            continue

        polygon_box = parse_polygon(obj.find("polygon"))
        geometry_source = "polygon"
        box = polygon_box
        if box is None:
            box = parse_bndbox(obj.find("bndbox"))
            geometry_source = "bndbox_fallback"
        if box is None:
            invalid_rows.append(
                {
                    "modality": modality,
                    "image_id": image_path.stem,
                    "image_path": str(image_path),
                    "annotation_path": str(xml_path),
                    "object_index": object_index,
                    "raw_class": raw_class,
                    "normalized_class": normalized,
                    "reason": "no_valid_polygon_or_bndbox",
                }
            )
            continue

        clipped = clip_box(box, xml_width, xml_height)
        if clipped is None:
            invalid_rows.append(
                {
                    "modality": modality,
                    "image_id": image_path.stem,
                    "image_path": str(image_path),
                    "annotation_path": str(xml_path),
                    "object_index": object_index,
                    "raw_class": raw_class,
                    "normalized_class": normalized,
                    "reason": "box_invalid_after_clipping",
                }
            )
            continue

        if geometry_source == "polygon":
            polygon_count += 1
        else:
            bndbox_count += 1
        mapped_counter["vehicle"] += 1
        boxes.append(clipped)
        object_rows.append(
            {
                "modality": modality,
                "image_id": image_path.stem,
                "image_path": str(image_path),
                "annotation_path": str(xml_path),
                "object_index": object_index,
                "raw_class": raw_class,
                "normalized_class": normalized,
                "mapped_class": "vehicle",
                "geometry_source": geometry_source,
                "x1": f"{clipped[0]:.6f}",
                "y1": f"{clipped[1]:.6f}",
                "x2": f"{clipped[2]:.6f}",
                "y2": f"{clipped[3]:.6f}",
                "status": "valid",
            }
        )

    return {
        "record": {
            "image_id": image_path.stem,
            "modality": modality,
            "image_path": str(image_path),
            "annotation_path": str(xml_path),
            "width": xml_width,
            "height": xml_height,
            "boxes": boxes,
            "labels": [1] * len(boxes),
            "classes": ["vehicle"] * len(boxes),
        },
        "object_rows": object_rows,
        "invalid_rows": invalid_rows,
        "ignored_rows": ignored_rows,
        "raw_counter": raw_counter,
        "mapped_counter": mapped_counter,
        "polygon_count": polygon_count,
        "bndbox_count": bndbox_count,
    }


def image_info(path):
    try:
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:
            return {"readable": True, "width": img.size[0], "height": img.size[1], "mode": img.mode}
    except Exception as exc:
        return {"readable": False, "width": "", "height": "", "mode": "", "error": str(exc)}


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def process_stream(name, image_dir, xml_dir, out):
    images = sorted(image_dir.glob("*.jpg"))
    xml_by_stem = {p.stem: p for p in sorted(xml_dir.glob("*.xml"))}
    manifest_rows = []
    annotation_rows = []
    jsonl_rows = []
    invalid_rows = []
    ignored_rows = []
    raw_counts = Counter()
    mapped_counts = Counter()
    image_sizes = Counter()
    summary = Counter()

    for idx, image_path in enumerate(images, start=1):
        if idx % 1000 == 0:
            print(f"{name}: {idx}/{len(images)}")
        info = image_info(image_path)
        xml_path = xml_by_stem.get(image_path.stem)
        xml_exists = xml_path is not None and xml_path.is_file()
        parse_ok = False
        valid_boxes = 0
        error = ""
        polygon_count = 0
        bndbox_count = 0
        if info["readable"]:
            image_sizes[(info["width"], info["height"])] += 1
        if info["readable"] and xml_exists:
            try:
                parsed = parse_xml_to_record(xml_path, image_path, name, info["width"], info["height"])
                parse_ok = True
                jsonl_rows.append(parsed["record"])
                annotation_rows.extend(parsed["object_rows"])
                invalid_rows.extend(parsed["invalid_rows"])
                ignored_rows.extend(parsed["ignored_rows"])
                raw_counts.update(parsed["raw_counter"])
                mapped_counts.update(parsed["mapped_counter"])
                polygon_count = parsed["polygon_count"]
                bndbox_count = parsed["bndbox_count"]
                valid_boxes = len(parsed["record"]["boxes"])
                summary["valid_vehicle_boxes"] += valid_boxes
                summary["polygon_boxes"] += polygon_count
                summary["bndbox_fallback_boxes"] += bndbox_count
                summary["invalid_annotations"] += len(parsed["invalid_rows"])
                summary["ignored_or_unknown_annotations"] += len(parsed["ignored_rows"])
                if valid_boxes == 0:
                    summary["empty_label_images"] += 1
            except Exception as exc:
                error = str(exc)
        else:
            error = "unreadable_image" if not info["readable"] else "missing_xml"
        manifest_rows.append(
            {
                "image_id": image_path.stem,
                "modality": name,
                "image_path": str(image_path),
                "annotation_path": str(xml_path) if xml_path else "",
                "image_readable": "yes" if info["readable"] else "no",
                "xml_exists": "yes" if xml_exists else "no",
                "xml_parse_ok": "yes" if parse_ok else "no",
                "width": info.get("width", ""),
                "height": info.get("height", ""),
                "mode": info.get("mode", ""),
                "valid_vehicle_boxes": valid_boxes,
                "polygon_boxes": polygon_count,
                "bndbox_fallback_boxes": bndbox_count,
                "error": error,
            }
        )

    summary["images"] = len(images)
    summary["xml_files"] = len(xml_by_stem)
    summary["readable_images"] = sum(1 for row in manifest_rows if row["image_readable"] == "yes")
    summary["xml_present"] = sum(1 for row in manifest_rows if row["xml_exists"] == "yes")
    summary["xml_parse_ok"] = sum(1 for row in manifest_rows if row["xml_parse_ok"] == "yes")
    summary["valid_images"] = len(jsonl_rows)
    summary["dominant_width"] = image_sizes.most_common(1)[0][0][0] if image_sizes else ""
    summary["dominant_height"] = image_sizes.most_common(1)[0][0][1] if image_sizes else ""
    summary["white_border_preserved"] = "yes"

    manifest_path = out / "manifests" / f"{name}_native_manifest.csv"
    inventory_path = out / "manifests" / f"{name}_annotation_inventory.csv"
    jsonl_path = out / "prepared_annotations" / f"{name}_native_hbb_annotations.jsonl"
    write_csv(
        manifest_path,
        manifest_rows,
        [
            "image_id",
            "modality",
            "image_path",
            "annotation_path",
            "image_readable",
            "xml_exists",
            "xml_parse_ok",
            "width",
            "height",
            "mode",
            "valid_vehicle_boxes",
            "polygon_boxes",
            "bndbox_fallback_boxes",
            "error",
        ],
    )
    write_csv(
        inventory_path,
        annotation_rows,
        [
            "modality",
            "image_id",
            "image_path",
            "annotation_path",
            "object_index",
            "raw_class",
            "normalized_class",
            "mapped_class",
            "geometry_source",
            "x1",
            "y1",
            "x2",
            "y2",
            "status",
        ],
    )
    write_jsonl(jsonl_path, jsonl_rows)
    return {
        "name": name,
        "summary": summary,
        "manifest_path": manifest_path,
        "inventory_path": inventory_path,
        "jsonl_path": jsonl_path,
        "raw_counts": raw_counts,
        "mapped_counts": mapped_counts,
        "invalid_rows": invalid_rows,
        "ignored_rows": ignored_rows,
        "eligible": (
            summary["images"] == summary["readable_images"] == summary["xml_present"] == summary["xml_parse_ok"] == summary["valid_images"]
            and summary["valid_vehicle_boxes"] > 0
            and set(raw_counts.keys())
        ),
    }


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


def write_protocol_files(out, data_root, rgb_result, thermal_result, checkpoint_rows):
    protocol_dir = out / "protocol"
    protocol_dir.mkdir(parents=True, exist_ok=True)
    (protocol_dir / "annotation_conversion_spec.md").write_text(
        "\n".join(
            [
                "# DroneVehicle Modality-Specific Annotation Conversion Spec",
                "",
                "This protocol is locked before model inference.",
                "",
                "Class mapping: `car`, `truck`, `bus`, `van`, and `freight_car` map to one foreground class, `vehicle`.",
                "Unknown or empty classes are not silently retained; they are written to `ignored_or_unknown_annotations.csv`.",
                "",
                "Box conversion:",
                "",
                "1. If a valid polygon with at least four finite points exists, use the enclosing horizontal box `min(x), min(y), max(x), max(y)` over all polygon points.",
                "2. If the polygon is missing or invalid, fall back to a valid VOC-style `bndbox` when present.",
                "3. If neither geometry is valid, drop the object and write it to `invalid_annotation_records.csv`.",
                "4. Clip all boxes to the native image range `[0,width] x [0,height]`; boxes with width or height <= 1 pixel after clipping are invalid.",
                "5. These rules are independent of model predictions and must not be changed after seeing DroneVehicle results.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (protocol_dir / "preprocessing_lock.yaml").write_text(
        "\n".join(
            [
                "dataset_root: \"" + str(data_root) + "\"",
                "native_image_size: [840, 712]",
                "white_border_crop: false",
                "image_value_scaling: divide_by_255",
                "model_transform: existing_torchvision_fcos_fixed_size_transform",
                "img_size: 640",
                "rgb_only:",
                "  real_input: DroneVehicle RGB image",
                "  unavailable_modalities: [thermal, event]",
                "  tensor_channels: RGB in channels 0..2, thermal channel zero, event channel zero",
                "thermal_only:",
                "  real_input: DroneVehicle infrared/thermal image",
                "  unavailable_modalities: [rgb, event]",
                "  tensor_channels: RGB channels zero, thermal grayscale in channel 3, event channel zero",
                "thermal_channel_rule: deterministic PIL grayscale conversion to one channel before divide_by_255",
                "dronevehicle_specific_tuning: forbidden",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (protocol_dir / "evaluation_protocol.md").write_text(
        "\n".join(
            [
                "# DroneVehicle Zero-Shot Modality-Specific Evaluation Protocol",
                "",
                "Allowed settings:",
                "",
                "- RGB-only: DroneVehicle RGB images with their native RGB XML annotations; thermal and event channels unavailable.",
                "- Thermal-only: DroneVehicle IR images with their native IR XML annotations; RGB and event channels unavailable.",
                "",
                "Forbidden settings:",
                "",
                "- RGB+thermal fused evaluation.",
                "- Merging RGB and IR annotations.",
                "- Intersection, union, nearest-neighbor matching, or synthetic fused GT.",
                "- Any DroneVehicle-driven tuning of thresholds, NMS, input size, normalization, cropping, checkpoint, model, or dropout.",
                "",
                "Fixed evaluation parameters:",
                "",
                "- detector score threshold: 0.001",
                "- metric score threshold: 0.50",
                "- NMS threshold: 0.60",
                "- detections per image: 100",
                "",
                "Aggregation:",
                "",
                "All validation-selected checkpoints for a method are evaluated. Main summaries use a fixed arithmetic mean across those checkpoints; per-checkpoint records remain in the reproducibility directory.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    commands = [
        "# Commands are generated before external inference and use fixed thresholds.",
        "# Run only protocols marked eligible in audit/modality_specific_eligibility.md.",
        "",
    ]
    for row in checkpoint_rows:
        for setting in ("rgb_only", "thermal_only"):
            commands.append(
                "python rarepdet/tools/eval_dronevehicle_modality_specific.py "
                f"--setting {setting} --model {row['model_type']} --weights \"{row['weights']}\" "
                f"--checkpoint-label {row['checkpoint_label']} --method-name \"{row['method_name']}\" "
                "--prepared-root reproducibility/external_dronevehicle_modality_specific "
                "--img-size 640 --device cuda --batch-size 4 --num-workers 0 "
                "--detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.60 --detections-per-img 100"
            )
    (protocol_dir / "evaluation_commands.txt").write_text("\n".join(commands) + "\n", encoding="utf-8")


def checkpoint_manifest():
    candidates = [
        {
            "method_name": "matched early fusion baseline",
            "model_type": "early",
            "checkpoint_label": "early_validation_selected_1",
            "weights": PROJECT_ROOT / "runs" / "R0_early_seed0_block64g16_e50" / "weights" / "best.pt",
        },
        {
            "method_name": "matched early fusion baseline",
            "model_type": "early",
            "checkpoint_label": "early_validation_selected_2",
            "weights": PROJECT_ROOT / "runs" / "R0_early_seed2_block64g16_e50" / "weights" / "best.pt",
        },
        {
            "method_name": "reliability-gated detector with 20% modality dropout",
            "model_type": "reliability",
            "checkpoint_label": "reliability_p020_validation_selected_1",
            "weights": PROJECT_ROOT / "runs" / "R4_reliability_p020_seed0_block64g16_e50" / "weights" / "best.pt",
        },
        {
            "method_name": "reliability-gated detector with 20% modality dropout",
            "model_type": "reliability",
            "checkpoint_label": "reliability_p020_validation_selected_2",
            "weights": PROJECT_ROOT / "runs" / "R4_reliability_p020_seed2_block64g16_e50" / "weights" / "best.pt",
        },
    ]
    for row in candidates:
        row["exists"] = row["weights"].is_file()
        row["sha256"] = sha256_file(row["weights"]) if row["exists"] else "MISSING"
        row["weights"] = str(row["weights"])
    return candidates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=r"E:\BaiduNetdiskDownload\test\test")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    data_root = Path(args.data)
    out = Path(args.out)
    for name in [
        "audit",
        "manifests",
        "protocol",
        "prepared_annotations",
        "inference_outputs",
        "per_model_results",
        "aggregate_results",
        "logs",
        "environment",
        "qualitative_fixed_selection",
    ]:
        (out / name).mkdir(parents=True, exist_ok=True)

    rgb_result = process_stream("rgb", data_root / "testimg", data_root / "testlabel", out)
    thermal_result = process_stream("thermal", data_root / "testimgr", data_root / "testlabelr", out)

    invalid_rows = rgb_result["invalid_rows"] + thermal_result["invalid_rows"]
    ignored_rows = rgb_result["ignored_rows"] + thermal_result["ignored_rows"]
    write_csv(
        out / "prepared_annotations" / "invalid_annotation_records.csv",
        invalid_rows,
        ["modality", "image_id", "image_path", "annotation_path", "object_index", "raw_class", "normalized_class", "reason"],
    )
    write_csv(
        out / "prepared_annotations" / "ignored_or_unknown_annotations.csv",
        ignored_rows,
        ["modality", "image_id", "image_path", "annotation_path", "object_index", "raw_class", "normalized_class", "reason"],
    )

    summary_rows = []
    for result in (rgb_result, thermal_result):
        s = result["summary"]
        summary_rows.append(
            {
                "protocol": "rgb_only" if result["name"] == "rgb" else "thermal_only",
                "valid_images": s["valid_images"],
                "vehicle_boxes": s["valid_vehicle_boxes"],
                "empty_label_images": s["empty_label_images"],
                "polygon_boxes": s["polygon_boxes"],
                "bndbox_fallback_boxes": s["bndbox_fallback_boxes"],
                "invalid_annotations": s["invalid_annotations"],
                "ignored_or_unknown_annotations": s["ignored_or_unknown_annotations"],
                "dominant_width": s["dominant_width"],
                "dominant_height": s["dominant_height"],
                "white_border_preserved": s["white_border_preserved"],
            }
        )
    write_csv(
        out / "prepared_annotations" / "annotation_conversion_summary.csv",
        summary_rows,
        [
            "protocol",
            "valid_images",
            "vehicle_boxes",
            "empty_label_images",
            "polygon_boxes",
            "bndbox_fallback_boxes",
            "invalid_annotations",
            "ignored_or_unknown_annotations",
            "dominant_width",
            "dominant_height",
            "white_border_preserved",
        ],
    )

    checkpoint_rows = checkpoint_manifest()
    write_csv(
        out / "manifests" / "checkpoint_manifest.csv",
        checkpoint_rows,
        ["method_name", "model_type", "checkpoint_label", "weights", "exists", "sha256"],
    )

    rgb_eligibility = "RGB_ONLY_ELIGIBLE" if rgb_result["eligible"] else "RGB_ONLY_BLOCKED"
    thermal_eligibility = "THERMAL_ONLY_ELIGIBLE" if thermal_result["eligible"] else "THERMAL_ONLY_BLOCKED"

    write_protocol_files(out, data_root, rgb_result, thermal_result, checkpoint_rows)

    eligibility_md = [
        "# DroneVehicle Modality-Specific Eligibility",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"RGB-only eligibility: `{rgb_eligibility}`",
        f"Thermal-only eligibility: `{thermal_eligibility}`",
        "",
        "This audit reuses the earlier fused-pairing preflight but evaluates each native stream separately.",
        "",
        md_table(
            [
                "Protocol",
                "Images",
                "Readable",
                "XML present",
                "XML parse OK",
                "Vehicle boxes",
                "Empty-label images",
                "Invalid annotations dropped",
                "Unknown annotations ignored",
                "Decision",
            ],
            [
                [
                    "RGB-only",
                    rgb_result["summary"]["images"],
                    rgb_result["summary"]["readable_images"],
                    rgb_result["summary"]["xml_present"],
                    rgb_result["summary"]["xml_parse_ok"],
                    rgb_result["summary"]["valid_vehicle_boxes"],
                    rgb_result["summary"]["empty_label_images"],
                    rgb_result["summary"]["invalid_annotations"],
                    rgb_result["summary"]["ignored_or_unknown_annotations"],
                    rgb_eligibility,
                ],
                [
                    "Thermal-only",
                    thermal_result["summary"]["images"],
                    thermal_result["summary"]["readable_images"],
                    thermal_result["summary"]["xml_present"],
                    thermal_result["summary"]["xml_parse_ok"],
                    thermal_result["summary"]["valid_vehicle_boxes"],
                    thermal_result["summary"]["empty_label_images"],
                    thermal_result["summary"]["invalid_annotations"],
                    thermal_result["summary"]["ignored_or_unknown_annotations"],
                    thermal_eligibility,
                ],
            ],
        ),
        "",
        "Locked interpretation:",
        "",
        "- RGB-only uses DroneVehicle RGB images and native RGB XML only; thermal and event inputs are unavailable.",
        "- Thermal-only uses DroneVehicle IR images and native IR XML only; RGB and event inputs are unavailable.",
        "- No fused RGB-thermal target is constructed.",
        "- White borders are preserved; no DroneVehicle-specific crop is introduced.",
        "- All valid observed classes map to one `vehicle` class.",
        "- Invalid geometry is dropped by the pre-locked conversion rule and recorded in `invalid_annotation_records.csv`.",
        "- Existing project missing-modality semantics are used by zeroing unavailable channels before FCOS inference.",
    ]
    (out / "audit" / "modality_specific_eligibility.md").write_text("\n".join(eligibility_md) + "\n", encoding="utf-8")

    dataset_manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data_root": str(data_root),
        "rgb_only_eligibility": rgb_eligibility,
        "thermal_only_eligibility": thermal_eligibility,
        "detector_score_thr": 0.001,
        "metric_score_thr": 0.50,
        "nms_thresh": 0.60,
        "detections_per_img": 100,
        "files": {
            "rgb_manifest": str(rgb_result["manifest_path"]),
            "thermal_manifest": str(thermal_result["manifest_path"]),
            "rgb_gt_jsonl": str(rgb_result["jsonl_path"]),
            "thermal_gt_jsonl": str(thermal_result["jsonl_path"]),
            "annotation_conversion_summary": str(out / "prepared_annotations" / "annotation_conversion_summary.csv"),
            "checkpoint_manifest": str(out / "manifests" / "checkpoint_manifest.csv"),
        },
        "sha256": {
            "rgb_manifest": sha256_file(rgb_result["manifest_path"]),
            "thermal_manifest": sha256_file(thermal_result["manifest_path"]),
            "rgb_gt_jsonl": sha256_file(rgb_result["jsonl_path"]),
            "thermal_gt_jsonl": sha256_file(thermal_result["jsonl_path"]),
        },
    }
    lines = []
    for key, value in dataset_manifest.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for sub_key, sub_val in value.items():
                lines.append(f"  {sub_key}: \"{sub_val}\"")
        else:
            lines.append(f"{key}: \"{value}\"")
    (out / "manifests" / "dataset_manifest.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"RGB-only eligibility: {rgb_eligibility}")
    print(f"Thermal-only eligibility: {thermal_eligibility}")
    print(f"Output root: {out}")


if __name__ == "__main__":
    main()
