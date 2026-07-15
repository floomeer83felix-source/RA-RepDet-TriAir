"""Audit the usable MM-UAV extraction and freeze the user-authorized interval-20 sample."""

from __future__ import annotations

import configparser
import csv
import hashlib
import json
import math
import os
import statistics
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = Path(r"E:\MM-UAV_extracted\MMMUAV\train")
QUARANTINE = Path(r"D:\MM-UAV_incomplete_quarantine\train\0512")
OUTPUT = PROJECT_ROOT / "runs" / "v52_mmuav_audit"
INTERVAL = 20
SPLIT_SALT = "v52-mmuav-interval20-sequence-split-v1"
DEVVAL_FRACTION = 0.20


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - position) + ordered[high] * (position - low)


def read_seq_length(sequence_dir: Path) -> int:
    parser = configparser.ConfigParser()
    parser.read(sequence_dir / "seqinfo-rgb.ini", encoding="utf-8")
    return parser.getint("Sequence", "seqLength")


def indexed_files(folder: Path, expected: int) -> tuple[bool, str]:
    indices = []
    for entry in os.scandir(folder):
        if not entry.is_file():
            continue
        try:
            indices.append(int(Path(entry.name).stem))
        except ValueError:
            return False, f"non-numeric filename {entry.name}"
    valid = (
        len(indices) == expected
        and len(set(indices)) == expected
        and min(indices, default=0) == 1
        and max(indices, default=0) == expected
    )
    return valid, f"count={len(indices)} unique={len(set(indices))} range={min(indices, default=0)}-{max(indices, default=0)}"


def parse_gt(path: Path, width: int, height: int):
    by_frame = defaultdict(list)
    stats = defaultdict(int)
    with path.open(encoding="utf-8", newline="") as handle:
        for line_number, row in enumerate(csv.reader(handle), 1):
            stats["rows"] += 1
            if len(row) < 6:
                stats["malformed"] += 1
                continue
            try:
                frame, track = int(row[0]), int(row[1])
                x, y, w, h = map(float, row[2:6])
            except ValueError:
                stats["malformed"] += 1
                continue
            if w <= 0 or h <= 0:
                stats["zero_or_negative_area"] += 1
            if x < 0 or y < 0 or x + w > width or y + h > height:
                stats["out_of_bounds"] += 1
            by_frame[frame].append((track, x, y, w, h, row[6:], line_number))
    return by_frame, dict(stats)


def box_iou(a, b) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1, y1 = max(ax, bx), max(ay, by)
    x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    union = aw * ah + bw * bh - intersection
    return intersection / union if union > 0 else 0.0


def split_sequences(sequence_names: list[str]):
    ranked = sorted(
        sequence_names,
        key=lambda name: hashlib.sha256(f"{SPLIT_SALT}\0{name}".encode()).hexdigest(),
    )
    devval_count = max(20, round(len(ranked) * DEVVAL_FRACTION))
    devval = set(ranked[:devval_count])
    return sorted(set(ranked) - devval), sorted(devval)


def manifest_row(sequence: str, frame: int) -> dict[str, str | int]:
    base = DATA_ROOT / sequence
    name = f"{frame:04d}.jpg"
    return {
        "sequence": sequence,
        "frame_index": frame,
        "rgb": str(base / "rgb_frame" / name),
        "ir": str(base / "ir_frame" / name),
        "event": str(base / "event_frame" / name),
        "gt_rgb": str(base / "gt_rgb" / "gt.txt"),
        "gt_ir": str(base / "gt_ir" / "gt.txt"),
    }


def write_manifest(path: Path, rows: list[dict]) -> None:
    fields = [
        "sequence", "frame_index", "rgb", "ir", "event", "gt_rgb", "gt_ir",
        "rgb_annotation_rows", "ir_annotation_rows", "annotation_state",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    generated = datetime.now().astimezone().isoformat(timespec="seconds")
    if not DATA_ROOT.is_dir():
        raise FileNotFoundError(DATA_ROOT)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "manifests").mkdir(exist_ok=True)

    complete: dict[str, int] = {}
    rejected = []
    dimension_counts = defaultdict(int)
    sample_extrema = []
    for sequence_dir in sorted((path for path in DATA_ROOT.iterdir() if path.is_dir()), key=lambda path: path.name):
        reasons = []
        try:
            length = read_seq_length(sequence_dir)
        except Exception as exc:
            rejected.append({"sequence": sequence_dir.name, "reason": f"invalid seqinfo: {exc}"})
            continue
        for folder in ("rgb_frame", "ir_frame", "event_frame"):
            valid, detail = indexed_files(sequence_dir / folder, length)
            if not valid:
                reasons.append(f"{folder}: {detail}")
        for relative in ("gt_rgb/gt.txt", "gt_ir/gt.txt", "seqinfo-ir.ini"):
            path = sequence_dir / relative
            if not path.is_file() or path.stat().st_size == 0:
                reasons.append(f"missing or empty {relative}")
        if reasons:
            rejected.append({"sequence": sequence_dir.name, "reason": "; ".join(reasons)})
        else:
            complete[sequence_dir.name] = length

    if len(complete) < 20:
        raise RuntimeError(f"Only {len(complete)} complete sequences")

    train_sequences, devval_sequences = split_sequences(list(complete))
    train_set = set(train_sequences)
    rows = {"train": [], "devval": []}
    sampled_indices = {}
    for sequence, length in sorted(complete.items()):
        indices = list(range(1, length + 1, INTERVAL))
        sampled_indices[sequence] = indices
        split = "train" if sequence in train_set else "devval"
        rows[split].extend(manifest_row(sequence, frame) for frame in indices)

    train_manifest = OUTPUT / "manifests" / "train_sampled.txt"
    devval_manifest = OUTPUT / "manifests" / "devval_sampled.txt"

    annotation_summary = {
        "rgb": defaultdict(int),
        "ir": defaultdict(int),
        "sampled_rgb_objects": 0,
        "sampled_ir_objects": 0,
        "sampled_without_rgb_gt_rows": 0,
        "sampled_without_ir_gt_rows": 0,
    }
    annotations = {}
    for sequence in sorted(complete):
        rgb, rgb_stats = parse_gt(DATA_ROOT / sequence / "gt_rgb" / "gt.txt", 640, 360)
        ir, ir_stats = parse_gt(DATA_ROOT / sequence / "gt_ir" / "gt.txt", 640, 512)
        annotations[sequence] = (rgb, ir)
        for key, value in rgb_stats.items():
            annotation_summary["rgb"][key] += value
        for key, value in ir_stats.items():
            annotation_summary["ir"][key] += value
        for frame in sampled_indices[sequence]:
            annotation_summary["sampled_rgb_objects"] += len(rgb.get(frame, []))
            annotation_summary["sampled_ir_objects"] += len(ir.get(frame, []))
            annotation_summary["sampled_without_rgb_gt_rows"] += not rgb.get(frame)
            annotation_summary["sampled_without_ir_gt_rows"] += not ir.get(frame)

    for split_rows in rows.values():
        for row in split_rows:
            rgb_count = len(annotations[row["sequence"]][0].get(row["frame_index"], []))
            ir_count = len(annotations[row["sequence"]][1].get(row["frame_index"], []))
            row["rgb_annotation_rows"] = rgb_count
            row["ir_annotation_rows"] = ir_count
            row["annotation_state"] = (
                "SOURCE_GT_ROW_PRESENT"
                if rgb_count or ir_count
                else "UNLABELED_OR_EMPTY_UNRESOLVED"
            )
    write_manifest(train_manifest, rows["train"])
    write_manifest(devval_manifest, rows["devval"])

    geometry_rows = []
    centers, ious, width_ratios, height_ratios = [], [], [], []
    geometry_sequences = sorted(
        complete,
        key=lambda name: hashlib.sha256(f"v52-geometry-v1\0{name}".encode()).hexdigest(),
    )[:20]
    for sequence in geometry_sequences:
        rgb, ir = annotations[sequence]
        frames_added = 0
        for frame in sampled_indices[sequence]:
            rgb_by_id = {row[0]: row[1:5] for row in rgb.get(frame, [])}
            ir_by_id = {row[0]: row[1:5] for row in ir.get(frame, [])}
            matched = sorted(set(rgb_by_id) & set(ir_by_id))
            if not matched:
                continue
            frame_centers, frame_ious = [], []
            for track in matched:
                rb = rgb_by_id[track]
                ib = ir_by_id[track]
                mapped_ir = (ib[0], ib[1] * 360 / 512, ib[2], ib[3] * 360 / 512)
                dx = (rb[0] + rb[2] / 2 - mapped_ir[0] - mapped_ir[2] / 2) / 640
                dy = (rb[1] + rb[3] / 2 - mapped_ir[1] - mapped_ir[3] / 2) / 360
                displacement = math.hypot(dx, dy)
                overlap = box_iou(rb, mapped_ir)
                wr = rb[2] / mapped_ir[2] if mapped_ir[2] else math.inf
                hr = rb[3] / mapped_ir[3] if mapped_ir[3] else math.inf
                centers.append(displacement)
                ious.append(overlap)
                width_ratios.append(wr)
                height_ratios.append(hr)
                frame_centers.append(displacement)
                frame_ious.append(overlap)
            geometry_rows.append(
                {
                    "sequence": sequence,
                    "frame_index": frame,
                    "matched_track_ids": len(matched),
                    "mean_normalized_center_displacement": statistics.fmean(frame_centers),
                    "mean_iou_after_dimension_scaling": statistics.fmean(frame_ious),
                }
            )
            frames_added += 1
            if frames_added == 5:
                break
    if len(geometry_rows) < 100:
        raise RuntimeError(f"Geometry sample has only {len(geometry_rows)} frames")

    with (OUTPUT / "geometry_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(geometry_rows[0]))
        writer.writeheader()
        writer.writerows(geometry_rows)

    representative = []
    for sequence in sorted(complete)[:20]:
        frame = sampled_indices[sequence][0]
        record = {"sequence": sequence, "frame": frame}
        for folder in ("rgb_frame", "ir_frame", "event_frame"):
            path = DATA_ROOT / sequence / folder / f"{frame:04d}.jpg"
            with Image.open(path) as image:
                record[folder] = {"size": list(image.size), "mode": image.mode, "format": image.format}
                dimension_counts[f"{folder}:{image.size[0]}x{image.size[1]}:{image.mode}"] += 1
                if len(sample_extrema) < 9:
                    sample_extrema.append({"path": str(path), "extrema": image.getextrema()})
        representative.append(record)

    benchmark_rows = (rows["train"] + rows["devval"])[:200]
    start = time.perf_counter()
    bytes_read = 0
    for row in benchmark_rows:
        for key in ("rgb", "ir", "event"):
            path = Path(row[key])
            bytes_read += path.stat().st_size
            with Image.open(path) as image:
                image.load()
    elapsed = time.perf_counter() - start
    benchmark = {
        "status": "PASS_CPU_ONLY",
        "samples": len(benchmark_rows),
        "modal_files_decoded": len(benchmark_rows) * 3,
        "elapsed_seconds": elapsed,
        "triplets_per_second": len(benchmark_rows) / elapsed,
        "compressed_megabytes_per_second": bytes_read / 1_000_000 / elapsed,
        "gpu_used": False,
    }
    write_json(OUTPUT / "loader_benchmark.json", benchmark)

    annotation_json = {
        "status": "BLOCKED_SPARSE_GT_EMPTY_FRAME_CONTRACT_UNVERIFIED",
        "format": "MOT-like CSV: frame, track_id, x, y, width, height, three source fields of unverified semantics",
        "coordinate_convention": "top-left xywh in modality-native pixels",
        "rgb_size": [640, 360],
        "ir_size": [640, 512],
        "event_size": [346, 260],
        "separate_rgb_ir_boxes": True,
        "event_specific_boxes": False,
        "annotation_cadence": "predominantly frames 1, 101, 201, ... plus sequence end",
        "summary": {
            "rgb": dict(annotation_summary["rgb"]),
            "ir": dict(annotation_summary["ir"]),
            **{key: value for key, value in annotation_summary.items() if not isinstance(value, defaultdict)},
        },
    }
    write_json(OUTPUT / "annotation_audit.json", annotation_json)
    write_text(
        OUTPUT / "annotation_audit.md",
        f"""# V52 Extracted Annotation Audit

Status: `BLOCKED_SPARSE_GT_EMPTY_FRAME_CONTRACT_UNVERIFIED`.

- RGB and IR each use separate MOT-like `gt.txt` files with native-coordinate `xywh` boxes and track IDs.
- RGB dimensions are 640x360; IR dimensions are 640x512; event frames are 346x260 and have no separate boxes.
- Sampled RGB/IR objects: {annotation_summary['sampled_rgb_objects']:,} / {annotation_summary['sampled_ir_objects']:,}.
- Sampled frames without RGB/IR GT rows: {annotation_summary['sampled_without_rgb_gt_rows']:,} / {annotation_summary['sampled_without_ir_gt_rows']:,}.
- GT is predominantly present at `1, 101, 201, ...` plus the sequence end. Missing rows cannot be treated as verified empty-target frames without the provider contract.
- The final three source columns and target category name remain unverified without provider documentation.
""",
    )

    geometry = {
        "status": "ALIGNMENT_MODULE_REQUIRED",
        "sample_frames": len(geometry_rows),
        "sample_sequences": len(set(row["sequence"] for row in geometry_rows)),
        "matched_targets": len(ious),
        "matching_rule": "same source frame index and same track ID; IR y/h scaled 360/512 into RGB dimensions",
        "normalized_center_displacement": {
            "mean": statistics.fmean(centers),
            "p50": percentile(centers, 0.5),
            "p95": percentile(centers, 0.95),
        },
        "matched_iou": {
            "mean": statistics.fmean(ious),
            "p50": percentile(ious, 0.5),
            "p95": percentile(ious, 0.95),
        },
        "rgb_to_scaled_ir_width_ratio_mean": statistics.fmean(width_ratios),
        "rgb_to_scaled_ir_height_ratio_mean": statistics.fmean(height_ratios),
        "conclusion": "Independent resizing is not a geometric calibration; direct channel-aligned fusion is not authorized.",
    }
    write_json(OUTPUT / "geometry_audit.json", geometry)

    manifest_metadata = {
        "generated_at": generated,
        "dataset_root": str(DATA_ROOT),
        "interval": INTERVAL,
        "index_origin": 1,
        "rule": "per complete sequence keep 1, 21, 41, ... <= seqLength",
        "complete_sequences": len(complete),
        "rejected_sequences": rejected,
        "train_sequences": len(train_sequences),
        "devval_sequences": len(devval_sequences),
        "train_samples": len(rows["train"]),
        "devval_samples": len(rows["devval"]),
        "total_samples": len(rows["train"]) + len(rows["devval"]),
        "samples_with_any_source_gt_row": sum(
            row["annotation_state"] == "SOURCE_GT_ROW_PRESENT"
            for split_rows in rows.values() for row in split_rows
        ),
        "samples_with_unresolved_annotation_state": sum(
            row["annotation_state"] == "UNLABELED_OR_EMPTY_UNRESOLVED"
            for split_rows in rows.values() for row in split_rows
        ),
        "split_salt": SPLIT_SALT,
        "train_manifest_sha256": sha256(train_manifest),
        "devval_manifest_sha256": sha256(devval_manifest),
        "script_sha256": sha256(Path(__file__)),
        "user_override": "2026-07-15: completed extraction is sufficient; sample one frame per 20 frames",
    }
    write_json(OUTPUT / "sampled_manifest.json", manifest_metadata)
    write_json(OUTPUT / "sampling_protocol.json", manifest_metadata)
    write_text(
        OUTPUT / "sampling_protocol.md",
        f"""# V52 Interval-20 Sampling Protocol

Frozen before any MM-UAV model metric: `{generated}`.

- User-authorized interval: 20.
- Source indexing begins at 1; every complete sequence keeps `1, 21, 41, ...` without renumbering.
- Complete/rejected sequences: {len(complete)} / {len(rejected)}.
- Train/devval sequences: {len(train_sequences)} / {len(devval_sequences)}; split is sequence-disjoint and SHA256-ranked with salt `{SPLIT_SALT}`.
- Train/devval samples: {len(rows['train']):,} / {len(rows['devval']):,}.
- Frames without source GT rows remain marked `UNLABELED_OR_EMPTY_UNRESOLVED`; they are not authorized as negative training samples.
- No model metric was inspected and no GPU operation was executed.
""",
    )
    write_text(
        OUTPUT / "split_integrity.md",
        f"""# V52 Split Integrity

- Train and devval sequence intersection: 0.
- Train sequence count: {len(train_sequences)}.
- Development-validation sequence count: {len(devval_sequences)}.
- The source test split is unavailable in the partial extraction and is not used.
- Incomplete sequence 0512 is quarantined at `{QUARANTINE}` and excluded.
""",
    )

    audit = {
        "status": "INTERVAL20_FROZEN_SUPERVISED_LABEL_CONTRACT_BLOCKED",
        "generated_at": generated,
        "dataset_root": str(DATA_ROOT),
        "filesystem": "exFAT, 262144-byte allocation unit",
        "complete_train_sequences": len(complete),
        "rejected_sequences": rejected,
        "synchronized_triplets": sum(complete.values()),
        "sampled_triplets_interval20": manifest_metadata["total_samples"],
        "dimensions": dict(dimension_counts),
        "representative_files": representative,
        "representative_extrema": sample_extrema,
        "quarantined_incomplete_sequence": str(QUARANTINE),
        "limitations": [
            "This is a partial source-train extraction, not the complete official dataset split.",
            "Provider/version/license text is not locally available.",
            "RGB, IR, and event have different native dimensions and no verified calibration.",
            "The target category name and final three annotation columns remain unverified.",
            "Most interval-20 frames have no source GT row; absence is not established as an empty target.",
        ],
    }
    write_json(OUTPUT / "dataset_audit.json", audit)
    write_text(
        OUTPUT / "dataset_audit.md",
        f"""# V52 MM-UAV Extracted Dataset Audit

Status: `INTERVAL20_FROZEN_SUPERVISED_LABEL_CONTRACT_BLOCKED`.

- Complete train sequences: {len(complete)}; rejected: {len(rejected)} (`0512`).
- Exact synchronized triplets: {sum(complete.values()):,}.
- Frozen interval-20 samples: {manifest_metadata['total_samples']:,}.
- Samples with any source GT row / unresolved no-row state: {manifest_metadata['samples_with_any_source_gt_row']:,} / {manifest_metadata['samples_with_unresolved_annotation_state']:,}.
- RGB/IR/event native dimensions: 640x360 / 640x512 / 346x260.
- CPU loader benchmark: {benchmark['triplets_per_second']:.2f} triplets/s over {benchmark['samples']} triplets.
- No source test sequence, provider license, or calibration evidence is available in this partial extraction.
""",
    )

    write_json(
        OUTPUT / "pilot_gate.json",
        {
            "generated_at": generated,
            "locked": True,
            "gpu_steps": 0,
            "reasons": [
                "Direct channel-aligned fusion is invalid across 640x360, 640x512, and 346x260 native grids.",
                "No source/provider license text is locally available.",
                "Most interval-20 frames lack source GT rows, and missing rows are not verified empty targets.",
                "V51 remains incomplete and its status is stale RUNNING with no active process.",
            ],
            "unlock_requirements": [
                "Pre-register and source-lock an explicit alignment module or coordinate transformation.",
                "Establish provider/version/license and target-category semantics.",
                "Resolve the V51 concurrency gate or obtain explicit authorization.",
            ],
        },
    )
    decision = {
        "outcome": "NO_GO_DATA_OR_LICENSE_BLOCKER",
        "data_sampling_ready": True,
        "supervised_detection_ready": False,
        "gpu_pilot_authorized": False,
        "license_verified": False,
        "scope": "424 complete source-train sequences in the interrupted local extraction",
        "reason": "Interval-20 paths are frozen, but the sparse-GT empty-frame contract, direct alignment, category semantics, and license are unresolved.",
    }
    write_json(OUTPUT / "feasibility_decision.json", decision)
    write_text(
        OUTPUT / "feasibility_decision.md",
        """# V52 Feasibility Decision

Outcome: `NO_GO_DATA_OR_LICENSE_BLOCKER` for supervised training on the interval-20 sample.

Interval-20 paths are frozen for 424 complete sequences, but most sampled frames lack source GT rows and cannot be interpreted as empty targets. A GPU pilot remains locked until the sparse-label contract is established, an explicit alignment method is pre-registered and source-locked, provider/license/category semantics are established, and the V51 gate is resolved.
""",
    )
    write_text(
        OUTPUT / "claim_boundary.md",
        """# V52 Claim Boundary

- The partial extraction supports a controlled interval-20 file manifest on 424 complete source-train sequences; it does not yet support supervised training on every manifest row.
- It does not establish an official full-dataset result, a source test result, or a second ground-vehicle dataset claim.
- Matching frame IDs do not establish pixel alignment; native grids differ and direct early fusion is not authorized.
- No AP, robustness, calibrated reliability, real-fault, significance, generalization, causality, or optimal-dropout claim is supported.
""",
    )

    alignment_rows = []
    for sequence, length in sorted(complete.items()):
        rgb, ir = annotations[sequence]
        alignment_rows.append(
            {
                "split": "train" if sequence in train_set else "devval",
                "sequence": sequence,
                "rgb_count": length,
                "ir_count": length,
                "event_count": length,
                "index_min": 1,
                "index_max": length,
                "exact_filename_index_match": True,
                "interval20_samples": len(sampled_indices[sequence]),
                "rgb_annotated_frames": len(rgb),
                "ir_annotated_frames": len(ir),
            }
        )
    with (OUTPUT / "sequence_alignment.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(alignment_rows[0]))
        writer.writeheader()
        writer.writerows(alignment_rows)
    with (OUTPUT / "missing_frame_report.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["sequence", "status", "location", "reason"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "sequence": "0512",
                "status": "QUARANTINED_INCOMPLETE_EXTRACTION",
                "location": str(QUARANTINE),
                "reason": "missing seqinfo-rgb.ini, IR frames, and source GT files after disk-full interruption",
            }
        )
    synchronization = {
        "status": "PASS_FILENAME_INDEX_SYNC_FOR_424_COMPLETE_SEQUENCES",
        "complete_sequences": len(complete),
        "synchronized_triplets": sum(complete.values()),
        "index_origin": 1,
        "filename_mapping": "exact same zero-padded numeric JPEG name",
        "native_dimensions_differ": True,
        "pixel_alignment_established": False,
    }
    write_json(OUTPUT / "synchronization_audit.json", synchronization)
    write_text(
        OUTPUT / "synchronization_audit.md",
        f"""# V52 Extracted Synchronization Audit

- {len(complete)} complete sequences have exact one-to-one RGB/IR/event numeric filename sets from 1 through `seqLength`.
- Exact synchronized triplets: {sum(complete.values()):,}.
- Sequence 0512 is excluded and quarantined after interrupted extraction.
- Filename synchronization does not imply pixel alignment; native dimensions are 640x360, 640x512, and 346x260.
""",
    )
    category_mapping = {
        "status": "PROVISIONAL_NOT_AUTHORIZED_FOR_TRAINING",
        "source_category_field": None,
        "provisional_detector_label": 1,
        "provisional_name": "UNVERIFIED_TRACKED_TARGET",
        "reason": "MOT-like rows contain track IDs but no locally documented category semantics.",
    }
    write_json(OUTPUT / "category_mapping.json", category_mapping)
    write_text(
        OUTPUT / "category_mapping.md",
        """# V52 Category Mapping

Status: `PROVISIONAL_NOT_AUTHORIZED_FOR_TRAINING`.

Rows can be provisionally represented as detector label 1 (`UNVERIFIED_TRACKED_TARGET`), but no locally available provider document establishes a category field or target name. This mapping is not authorized for a GPU pilot.
""",
    )
    write_text(
        OUTPUT / "provenance_and_license.md",
        """# V52 Provenance And License

- Local archive name: `MM-UAV`; internal root: `MMMUAV`.
- The interrupted extraction contains 424 complete source-train sequences and no source test split.
- No README, provider metadata, version identifier, or license text is present in the extracted subset or archive metadata inventory.
- Provider, version, category semantics, and redistribution/research-use terms remain unresolved.
""",
    )
    inventory_rows = []
    for sequence, length in sorted(complete.items()):
        inventory_rows.append(
            {
                "relative_path": f"train/{sequence}",
                "status": "COMPLETE",
                "triplet_frames": length,
                "sampled_interval20": len(sampled_indices[sequence]),
                "split": "train" if sequence in train_set else "devval",
            }
        )
    with (OUTPUT / "directory_inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(inventory_rows[0]))
        writer.writeheader()
        writer.writerows(inventory_rows)

    source_lock = {
        "generated_at": generated,
        "status": "LOCKED_CPU_ARTIFACTS_GPU_NOT_AUTHORIZED",
        "dataset_root": str(DATA_ROOT),
        "complete_sequences": len(complete),
        "interval": INTERVAL,
        "hashes": {
            "prepare_script": sha256(Path(__file__)),
            "train_manifest": sha256(train_manifest),
            "devval_manifest": sha256(devval_manifest),
            "sampling_protocol": sha256(OUTPUT / "sampling_protocol.json"),
            "geometry_audit": sha256(OUTPUT / "geometry_audit.json"),
            "annotation_audit": sha256(OUTPUT / "annotation_audit.json"),
        },
        "gpu_pilot_authorized": False,
    }
    write_json(OUTPUT / "source_lock_v52.json", source_lock)
    write_text(
        OUTPUT / "source_lock_v52.md",
        "# V52 CPU Source Lock\n\n"
        f"Status: `{source_lock['status']}`.\n\n"
        f"Interval: {INTERVAL}; complete sequences: {len(complete)}. "
        "The hashes in `source_lock_v52.json` freeze CPU audit artifacts only; GPU execution remains prohibited.\n",
    )
    write_text(
        OUTPUT / "preflight_commands.txt",
        f"""{Path(os.sys.executable)} rarepdet/tools/prepare_v52_mmuav_extracted.py
python -m unittest discover -s tests -p test_v52_mmuav.py -v
""",
    )
    write_text(
        OUTPUT / "preflight_outputs.txt",
        f"""Complete sequences: {len(complete)}
Rejected sequences: {len(rejected)}
Interval-20 samples: {manifest_metadata['total_samples']}
Samples with source GT / unresolved no-row state: {manifest_metadata['samples_with_any_source_gt_row']}/{manifest_metadata['samples_with_unresolved_annotation_state']}
Geometry frames/sequences: {len(geometry_rows)}/{len(set(row['sequence'] for row in geometry_rows))}
CPU loader: {benchmark['triplets_per_second']:.4f} triplets/s
GPU operations: 0
Pilot gate: LOCKED
""",
    )
    print(json.dumps(manifest_metadata, indent=2))


if __name__ == "__main__":
    main()
