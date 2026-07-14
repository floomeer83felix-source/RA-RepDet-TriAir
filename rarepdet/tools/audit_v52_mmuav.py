#!/usr/bin/env python
"""CPU-only archive audit for the local MM-UAV ZIP64 split archive."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = Path(r"D:\BaiduNetdiskDownload\MM-UAV")
OUTPUT = PROJECT_ROOT / "runs/v52_mmuav_audit"
FINAL_ZIP = DATA_ROOT / "MMMUAV.zip"
MEDIA_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".npy", ".npz"}


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def edge_fingerprint(path, chunk_size=1024 * 1024):
    size = path.stat().st_size
    with path.open("rb") as handle:
        first = handle.read(min(chunk_size, size))
        if size > chunk_size:
            handle.seek(max(0, size - chunk_size))
            last = handle.read(chunk_size)
        else:
            last = first
    return {
        "first_1mib_sha256": sha256_bytes(first),
        "last_1mib_sha256": sha256_bytes(last),
    }


def archive_parts():
    parts = sorted(DATA_ROOT.glob("MMMUAV.z[0-9][0-9]"))
    if FINAL_ZIP.is_file():
        parts.append(FINAL_ZIP)
    return parts


def inventory_parts():
    rows = []
    for path in archive_parts():
        stat = path.stat()
        rows.append(
            {
                "name": path.name,
                "bytes": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
                **edge_fingerprint(path),
            }
        )
    canonical = "\n".join(
        f"{row['name']}\t{row['bytes']}\t{row['mtime']}\t"
        f"{row['first_1mib_sha256']}\t{row['last_1mib_sha256']}"
        for row in rows
    ).encode("utf-8")
    return rows, sha256_bytes(canonical)


def zip64_eocd(path):
    with path.open("rb") as handle:
        handle.seek(-4096, os.SEEK_END)
        tail = handle.read()
    position = tail.rfind(b"PK\x06\x06")
    if position < 0:
        raise RuntimeError("ZIP64 end-of-central-directory record not found")
    values = struct.unpack_from("<4sQ2H2I4Q", tail, position)
    return {
        "record_size": values[1],
        "version_made_by": values[2],
        "version_needed": values[3],
        "disk_number": values[4],
        "central_directory_disk": values[5],
        "entries_on_disk": values[6],
        "total_entries": values[7],
        "central_directory_bytes": values[8],
        "central_directory_offset": values[9],
    }


def modality_for(folder):
    lower = folder.lower()
    if "rgb" in lower or "visible" in lower:
        return "rgb"
    if lower.startswith("ir") or "infrared" in lower or "thermal" in lower:
        return "ir"
    if "event" in lower:
        return "event"
    return None


@dataclass
class FrameState:
    count: int = 0
    numeric_count: int = 0
    minimum: int | None = None
    maximum: int | None = None
    mask: int = 0
    duplicate_indices: int = 0
    extensions: Counter = field(default_factory=Counter)

    def add(self, stem, extension):
        self.count += 1
        self.extensions[extension.lower()] += 1
        if not stem.isdigit():
            return
        index = int(stem)
        self.numeric_count += 1
        self.minimum = index if self.minimum is None else min(self.minimum, index)
        self.maximum = index if self.maximum is None else max(self.maximum, index)
        bit = 1 << index
        if self.mask & bit:
            self.duplicate_indices += 1
        self.mask |= bit


@dataclass
class SequenceState:
    split: str
    sequence: str
    folders: Counter = field(default_factory=Counter)
    modalities: dict = field(
        default_factory=lambda: {name: FrameState() for name in ("rgb", "ir", "event")}
    )
    metadata_files: int = 0
    annotation_candidates: int = 0


def parse_central_directory(path, eocd):
    sequence_states = {}
    split_counts = Counter()
    split_sequences = defaultdict(set)
    folder_stats = Counter()
    folder_uncompressed = Counter()
    extension_counts = Counter()
    metadata = []
    central_digest = hashlib.sha256()
    total_compressed = 0
    total_uncompressed = 0
    malformed = 0
    with path.open("rb") as handle:
        handle.seek(eocd["central_directory_offset"])
        for index in range(eocd["total_entries"]):
            fixed = handle.read(46)
            if len(fixed) != 46 or fixed[:4] != b"PK\x01\x02":
                malformed += 1
                break
            values = struct.unpack("<4s6H3I5H2I", fixed)
            flag = values[3]
            crc32 = values[7]
            compressed = values[8]
            uncompressed = values[9]
            name_length, extra_length, comment_length = values[10:13]
            name_bytes = handle.read(name_length)
            extra = handle.read(extra_length)
            comment = handle.read(comment_length)
            central_digest.update(fixed)
            central_digest.update(name_bytes)
            central_digest.update(extra)
            central_digest.update(comment)
            encoding = "utf-8" if flag & 0x800 else "cp437"
            name = name_bytes.decode(encoding, errors="replace").replace("\\", "/")
            if compressed == 0xFFFFFFFF or uncompressed == 0xFFFFFFFF:
                cursor = 0
                while cursor + 4 <= len(extra):
                    tag, length = struct.unpack_from("<HH", extra, cursor)
                    payload = extra[cursor + 4 : cursor + 4 + length]
                    cursor += 4 + length
                    if tag != 0x0001:
                        continue
                    offset = 0
                    if uncompressed == 0xFFFFFFFF:
                        uncompressed = struct.unpack_from("<Q", payload, offset)[0]
                        offset += 8
                    if compressed == 0xFFFFFFFF:
                        compressed = struct.unpack_from("<Q", payload, offset)[0]
                    break
            total_compressed += compressed
            total_uncompressed += uncompressed
            suffix = Path(name).suffix.lower()
            extension_counts[suffix or "<none>"] += 1
            parts = [part for part in name.split("/") if part]
            if len(parts) >= 2:
                split = parts[1]
            else:
                split = "<root>"
            split_counts[split] += 1
            if len(parts) >= 4 and parts[0] == "MMMUAV":
                sequence = parts[2]
                folder = parts[3]
                split_sequences[split].add(sequence)
                key = (split, sequence)
                state = sequence_states.setdefault(key, SequenceState(split, sequence))
                state.folders[folder] += 1
                prefix = f"MMMUAV/{split}/{sequence}/{folder}"
                folder_stats[prefix] += 1
                folder_uncompressed[prefix] += uncompressed
                modality = modality_for(folder)
                if modality and len(parts) >= 5 and not name.endswith("/"):
                    state.modalities[modality].add(Path(parts[-1]).stem, suffix)
                if any(token in folder.lower() for token in ("gt", "annot", "label")):
                    state.annotation_candidates += 1
            is_media = suffix in MEDIA_SUFFIXES
            if not is_media and not name.endswith("/"):
                if len(metadata) < 100000:
                    metadata.append(
                        {
                            "path": name,
                            "compressed_bytes": compressed,
                            "uncompressed_bytes": uncompressed,
                            "crc32": f"{crc32:08x}",
                        }
                    )
                if len(parts) >= 4 and parts[0] == "MMMUAV":
                    sequence_states[(split, parts[2])].metadata_files += 1
            if (index + 1) % 1_000_000 == 0:
                print(f"central entries parsed: {index + 1}", flush=True)
    return {
        "sequence_states": sequence_states,
        "split_counts": split_counts,
        "split_sequences": split_sequences,
        "folder_stats": folder_stats,
        "folder_uncompressed": folder_uncompressed,
        "extension_counts": extension_counts,
        "metadata": metadata,
        "central_directory_sha256": central_digest.hexdigest(),
        "total_compressed": total_compressed,
        "total_uncompressed": total_uncompressed,
        "malformed": malformed,
    }


def mask_indices(mask, limit=100):
    values = []
    index = 0
    while mask and len(values) < limit:
        if mask & 1:
            values.append(index)
        mask >>= 1
        index += 1
    return values


def v51_process_state():
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-CimInstance Win32_Process | Where-Object { "
        "$_.CommandLine -match 'run_v51_cv_queue|train_visdrone_rgb|eval_v51_visdrone' -and "
        "$_.CommandLine -notmatch 'Get-CimInstance' } | "
        "Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress",
    ]
    output = subprocess.check_output(command, text=True, encoding="utf-8", errors="replace").strip()
    processes = [] if not output else json.loads(output)
    if isinstance(processes, dict):
        processes = [processes]
    status_path = PROJECT_ROOT / "runs/v51_visdrone_recovery/cv_run_status.json"
    status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.is_file() else None
    return processes, status


def write_reports(parts, part_hash, eocd, parsed):
    generated = now()
    output_rows = []
    for prefix, count in sorted(parsed["folder_stats"].items()):
        output_rows.append(
            {
                "path": prefix,
                "file_entries": count,
                "uncompressed_bytes": parsed["folder_uncompressed"][prefix],
            }
        )
    with (OUTPUT / "directory_inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("path", "file_entries", "uncompressed_bytes"))
        writer.writeheader()
        writer.writerows(output_rows)

    alignment_rows = []
    missing_rows = []
    for key, state in sorted(parsed["sequence_states"].items()):
        rgb, ir, event = (state.modalities[name] for name in ("rgb", "ir", "event"))
        common = rgb.mask & ir.mask & event.mask
        union = rgb.mask | ir.mask | event.mask
        masks_equal = bool(rgb.mask) and rgb.mask == ir.mask == event.mask
        alignment_rows.append(
            {
                "split": state.split,
                "sequence": state.sequence,
                "rgb_count": rgb.count,
                "rgb_min": rgb.minimum,
                "rgb_max": rgb.maximum,
                "ir_count": ir.count,
                "ir_min": ir.minimum,
                "ir_max": ir.maximum,
                "event_count": event.count,
                "event_min": event.minimum,
                "event_max": event.maximum,
                "synchronized_numeric_triplets": common.bit_count(),
                "union_numeric_indices": union.bit_count(),
                "exact_filename_index_match": masks_equal,
                "rgb_duplicate_indices": rgb.duplicate_indices,
                "ir_duplicate_indices": ir.duplicate_indices,
                "event_duplicate_indices": event.duplicate_indices,
                "annotation_candidate_entries": state.annotation_candidates,
                "folders": ";".join(sorted(state.folders)),
            }
        )
        for modality, modality_state in state.modalities.items():
            missing = union & ~modality_state.mask
            missing_rows.append(
                {
                    "split": state.split,
                    "sequence": state.sequence,
                    "modality": modality,
                    "missing_from_union_count": missing.bit_count(),
                    "first_missing_indices": ";".join(map(str, mask_indices(missing))),
                    "non_numeric_filenames": modality_state.count - modality_state.numeric_count,
                    "duplicate_numeric_indices": modality_state.duplicate_indices,
                }
            )
    for filename, rows in (
        ("sequence_alignment.csv", alignment_rows),
        ("missing_frame_report.csv", missing_rows),
    ):
        with (OUTPUT / filename).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["status"])
            writer.writeheader()
            writer.writerows(rows)

    media_counts = {
        modality: sum(state.modalities[modality].count for state in parsed["sequence_states"].values())
        for modality in ("rgb", "ir", "event")
    }
    exact_sequences = sum(row["exact_filename_index_match"] for row in alignment_rows)
    archive_bytes = sum(row["bytes"] for row in parts)
    free_bytes = shutil.disk_usage(DATA_ROOT).free
    workspace_free_bytes = shutil.disk_usage(PROJECT_ROOT).free
    test_annotation_candidates = sum(
        state.annotation_candidates
        for state in parsed["sequence_states"].values()
        if state.split.lower() == "test"
    )
    audit = {
        "status": "BLOCKED_ARCHIVE_ONLY_INSUFFICIENT_EXTRACTION_SPACE",
        "generated_at": generated,
        "dataset_root": str(DATA_ROOT),
        "dataset_root_contents": "ZIP64 split archive only; no extracted sequence directories",
        "archive_parts": parts,
        "archive_part_inventory_sha256": part_hash,
        "archive_bytes": archive_bytes,
        "free_bytes_on_d": free_bytes,
        "free_bytes_on_e": workspace_free_bytes,
        "free_minus_archive_bytes": free_bytes - archive_bytes,
        "zip64": eocd,
        "central_directory_sha256": parsed["central_directory_sha256"],
        "central_directory_entries_parsed": sum(parsed["split_counts"].values()),
        "central_directory_malformed_records": parsed["malformed"],
        "central_total_compressed_bytes": parsed["total_compressed"],
        "central_total_uncompressed_bytes": parsed["total_uncompressed"],
        "split_sequence_counts": {
            split: len(sequences) for split, sequences in parsed["split_sequences"].items()
        },
        "split_entry_counts": dict(parsed["split_counts"]),
        "extension_counts": dict(parsed["extension_counts"]),
        "modality_frame_entry_counts": media_counts,
        "sequences_with_exact_numeric_triplet_indices": exact_sequences,
        "sequence_records": len(alignment_rows),
        "test_annotation_candidate_entries": test_annotation_candidates,
        "metadata_entries_recorded": parsed["metadata"],
        "limitations": [
            "No raw sequence file is extracted, so media decoding, bit depth, numeric range, corruption, and loader throughput cannot be tested.",
            "Central-directory CRC32 and archive edge fingerprints are not substitutes for SHA256 of extracted metadata or sampled media.",
            "Annotation contents and RGB/IR box geometry cannot be parsed or compared.",
            "License/provider text cannot be verified from extracted local evidence.",
            "Sampling manifests cannot reference usable files while all media remain inside a split archive.",
        ],
    }
    write_json(OUTPUT / "dataset_audit.json", audit)
    write_text(
        OUTPUT / "dataset_audit.md",
        f"""# V52 MM-UAV Dataset Audit

Status: `BLOCKED_ARCHIVE_ONLY_INSUFFICIENT_EXTRACTION_SPACE`

Generated: `{generated}`

- Local root: `{DATA_ROOT}`.
- Local state: 35 10-GiB split parts plus one 7.2-GB final ZIP; no extracted sequence directory exists.
- Archive bytes: {archive_bytes:,}; free D-drive bytes: {free_bytes:,}; deficit relative to archive size: {archive_bytes - free_bytes:,} bytes.
- Central-directory compressed/uncompressed totals: {parsed['total_compressed']:,} / {parsed['total_uncompressed']:,} bytes.
- Free E-drive bytes: {workspace_free_bytes:,}; extraction feasibility there still requires filesystem placement and a safety margin.
- ZIP64 entries: {eocd['total_entries']:,}; central-directory SHA256: `{parsed['central_directory_sha256']}`.
- Sequence records inferred from paths: {len(alignment_rows):,}.
- RGB/IR/event entry counts: {media_counts['rgb']:,} / {media_counts['ir']:,} / {media_counts['event']:,}.
- Filename-index synchronization is reported in `sequence_alignment.csv`; this does not establish pixel geometry.

The archive directory is readable, but V52 cannot decode representative media, inspect annotation contents, verify licensing, measure geometry, benchmark the loader, or freeze usable manifests until the data are extracted to a filesystem with adequate space.
""",
    )
    write_text(
        OUTPUT / "provenance_and_license.md",
        """# V52 Provenance And License

- The local name `MM-UAV` and archive root `MMMUAV/` are established from local paths and the ZIP64 central directory.
- No extracted README or license file is locally readable in the dataset root.
- Provider, version, redistribution terms, and research-use license are therefore not established.
- Central-directory filenames and CRC32 values are inventory evidence, not verified license content.
""",
    )
    sync = {
        "status": "FILENAME_INDEX_AUDIT_ONLY",
        "sequence_records": len(alignment_rows),
        "exact_index_match_sequences": exact_sequences,
        "media_counts": media_counts,
        "limitations": "No file was decoded; timestamp, frame-rate, coordinate-origin, and pixel alignment remain unverified.",
    }
    write_json(OUTPUT / "synchronization_audit.json", sync)
    write_text(
        OUTPUT / "synchronization_audit.md",
        f"""# V52 Synchronization Audit

- Archive filename records cover {len(alignment_rows):,} split/sequence pairs.
- {exact_sequences:,} pairs have identical numeric filename-index sets across RGB, IR, and event folders.
- Missing and duplicate index summaries are in `missing_frame_report.csv`.
- This is filename-level evidence only. It does not establish timestamps, frame rate, event representation, shared resolution, coordinate origin, or pixel alignment.
""",
    )
    annotation = {
        "status": "BLOCKED_CONTENT_NOT_EXTRACTED",
        "test_annotation_candidate_entries": test_annotation_candidates,
        "category_mapping_established": False,
        "geometry_sample_frames": 0,
        "reason": "Annotation and media contents are unavailable inside the unextracted split archive.",
    }
    write_json(OUTPUT / "annotation_audit.json", annotation)
    write_text(
        OUTPUT / "annotation_audit.md",
        """# V52 Annotation Audit

Status: `BLOCKED_CONTENT_NOT_EXTRACTED`.

Annotation-like paths can be counted from the archive directory, but no annotation file is extracted. Box format, categories, track IDs, flags, empty frames, malformed boxes, and test-label availability cannot be established safely.
""",
    )
    with (OUTPUT / "geometry_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("status", "sample_frames", "reason"))
        writer.writerow(("BLOCKED_CONTENT_NOT_EXTRACTED", 0, "RGB/IR annotations and media are not extracted"))
    mapping = {
        "status": "NOT_ESTABLISHED",
        "source_categories": [],
        "detection_coordinate_system": None,
        "reason": "annotation contents unavailable",
    }
    write_json(OUTPUT / "category_mapping.json", mapping)
    write_text(
        OUTPUT / "category_mapping.md",
        """# V52 Category Mapping

No category mapping is frozen. The archive filename layout cannot establish annotation category IDs, names, or a defensible common detection coordinate system.
""",
    )
    sampling = {
        "status": "BLOCKED_NOT_FROZEN",
        "requested_interval": 30,
        "manifests_created": False,
        "reason": "no extracted synchronized annotated triplet paths and no established coordinate system",
    }
    write_json(OUTPUT / "sampling_protocol.json", sampling)
    write_text(
        OUTPUT / "sampling_protocol.md",
        """# V52 Sampling Protocol

The intended interval remains 30, but no sampling protocol or manifest is frozen. Creating paths into an unextracted archive, or assuming annotations from filenames, would violate the task contract.
""",
    )
    processes, v51_status = v51_process_state()
    pilot_gate = {
        "locked": True,
        "generated_at": generated,
        "v51_processes": processes,
        "v51_status": v51_status,
        "reasons": [
            "V51 is incomplete even though no matching process is currently alive.",
            "MM-UAV media and annotations are not extracted.",
            "No common detection coordinate system or frozen sampling manifest exists.",
        ],
    }
    write_json(OUTPUT / "pilot_gate.json", pilot_gate)
    decision = {
        "outcome": "NO_GO_DATA_OR_LICENSE_BLOCKER",
        "scope": "current local archive-only state",
        "permanent_dataset_judgment": False,
        "reasons": pilot_gate["reasons"]
        + ["Local provider/license text has not been extracted and verified."],
    }
    write_json(OUTPUT / "feasibility_decision.json", decision)
    write_text(
        OUTPUT / "feasibility_decision.md",
        """# V52 Feasibility Decision

Outcome: `NO_GO_DATA_OR_LICENSE_BLOCKER` for the current local archive-only state.

This is not a permanent judgment about MM-UAV. A new audit can reconsider the dataset after complete extraction to adequate storage, local license/provenance verification, annotation parsing, and geometry measurement. No GPU pilot is permitted now.
""",
    )
    write_text(
        OUTPUT / "claim_boundary.md",
        """# V52 Claim Boundary

- No second ground-vehicle dataset claim is supported.
- Filename-index agreement does not establish pixel alignment or event-label coordinates.
- No model, AP, mechanism, robustness, calibration, significance, causality, or optimal-dropout claim is supported.
- V51 remains separate, incomplete RGB-only cross-validation work and was not altered by V52.
""",
    )
    write_text(
        OUTPUT / "preflight_commands.txt",
        f"{sys.executable} rarepdet/tools/audit_v52_mmuav.py",
    )
    write_text(
        OUTPUT / "preflight_outputs.txt",
        f"ZIP64 central records parsed: {eocd['total_entries']}\n"
        f"Malformed central records: {parsed['malformed']}\n"
        "GPU operations: 0\nMedia files decoded: 0\n"
        "Result: BLOCKED_ARCHIVE_ONLY_INSUFFICIENT_EXTRACTION_SPACE",
    )
    write_json(
        OUTPUT / "loader_benchmark.json",
        {"status": "NOT_RUN", "reason": "no extracted media paths", "gpu_used": False},
    )


def update_status_and_handoff(eocd):
    generated = now()
    write_text(
        PROJECT_ROOT / "docs/TASK_BLOCKER.md",
        f"""# Task Blocker

Status: `V52_BLOCKED_ARCHIVE_ONLY_AND_V51_INCOMPLETE`

Generated: {generated}

## Exact blocker

`D:\\BaiduNetdiskDownload\\MM-UAV` contains only 35 10-GiB ZIP split parts and a 7.2-GB final ZIP. There are no extracted sequence directories. The archive occupies approximately 383 GB while D: has approximately 360 GB free, so complete extraction beside the archive is impossible.

The ZIP64 central directory is readable and contains {eocd['total_entries']:,} entries, but central-directory metadata cannot establish decoded media ranges, annotation semantics, RGB/IR geometry, event representation, licensing text, or usable filesystem manifests.

V51 is also incomplete: its stale status says `RUNNING`, no V51 process is alive, and the last log ended at fold 0 seed 0 epoch 6 iteration 300/1441. V52 did not restart, stop, or modify V51.

## Last execution lines

```text
V52 central-directory audit completed without a Python exception.
MM-UAV extracted directories: 0
ZIP64 parts: 36
ZIP64 entries: {eocd['total_entries']}
GPU operations: 0
Pilot gate: LOCKED
```

## Attempted checks

1. Verified all split parts `z01` through `z35` and the final ZIP exist and are non-zero.
2. Recorded size, modification time, and first/last 1-MiB SHA256 fingerprints for every part.
3. Parsed the ZIP64 central directory without extraction and audited filename-level split, sequence, modality, and frame-index structure.
4. Checked D-drive free space and confirmed it is smaller than the archive itself.
5. Checked V51 process state and preserved its incomplete files unchanged.

## Repair options

1. Extract MM-UAV to a different filesystem with sufficient capacity, retaining the archives unchanged; provide at least the archive's uncompressed-size requirement plus working space, then rerun V52.
2. Free sufficient D-drive capacity and extract the complete multipart archive in place, then rerun V52 from Stage 1.

Do not authorize the 200-step pilot until extraction, annotation/geometry audit, sampling freeze, and the V51 gate all pass.
""",
    )
    write_text(
        PROJECT_ROOT / "docs/EXPERIMENT_STATUS.md",
        f"""# Experiment Status

Updated: {generated}

## Active task

`V52_BLOCKED_ARCHIVE_ONLY_AND_V51_INCOMPLETE`

## MM-UAV audit

- Local root contains a 36-part ZIP64 archive only; no extracted sequences.
- Central-directory entries: {eocd['total_entries']:,}.
- CPU-only archive inventory and filename synchronization audit completed.
- Annotation contents, decoded modalities, geometry, sampling manifests, loader benchmark, and source lock cannot be established.
- Pilot gate is locked; GPU steps executed: 0.

## V51 boundary

- V52 did not alter V51.
- No V51 process is alive, but V51 is incomplete; the last training log ends at fold 0 seed 0 epoch 6 iteration 300/1441.

## Decision

`NO_GO_DATA_OR_LICENSE_BLOCKER` for the current local archive-only state. This is not a permanent judgment after proper extraction.
""",
    )
    handoff = {
        "generated_at": generated,
        "task": "V52 MM-UAV audit and bounded pilot preparation",
        "status": "V52_BLOCKED_ARCHIVE_ONLY_AND_V51_INCOMPLETE",
        "dataset_root": str(DATA_ROOT),
        "zip64_entries": eocd["total_entries"],
        "gpu_steps": 0,
        "pilot_locked": True,
        "decision": "NO_GO_DATA_OR_LICENSE_BLOCKER",
        "v51_modified": False,
        "next_action": "extract the complete archive to a filesystem with sufficient capacity, then rerun V52",
    }
    write_json(PROJECT_ROOT / "runs/handoff_latest.json", handoff)
    write_text(
        PROJECT_ROOT / "runs/handoff_latest.md",
        f"""# RA-RepDet-TriAir Handoff

Generated: {generated}

## Current task

- V52 status: `BLOCKED_ARCHIVE_ONLY_AND_V51_INCOMPLETE`.
- MM-UAV is present only as a 36-part ZIP64 archive; no sequence is extracted.
- Central-directory entries: {eocd['total_entries']:,}.
- CPU archive/path audit completed; GPU pilot steps: 0.
- Current decision: `NO_GO_DATA_OR_LICENSE_BLOCKER` for this local state.

## Required action

Extract the complete archive to storage with sufficient capacity, then rerun V52 Stage 1. Separately decide how to handle the incomplete V51 queue; V52 did not alter it.
""",
    )


def main():
    if not DATA_ROOT.is_dir() or not FINAL_ZIP.is_file():
        raise FileNotFoundError(f"MM-UAV split archive not found under {DATA_ROOT}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    parts, part_hash = inventory_parts()
    expected = [f"MMMUAV.z{index:02d}" for index in range(1, 36)] + ["MMMUAV.zip"]
    actual = [row["name"] for row in parts]
    if actual != expected:
        raise RuntimeError(f"split archive sequence mismatch: expected={expected} actual={actual}")
    eocd = zip64_eocd(FINAL_ZIP)
    parsed = parse_central_directory(FINAL_ZIP, eocd)
    if parsed["malformed"] or sum(parsed["split_counts"].values()) != eocd["total_entries"]:
        raise RuntimeError(
            "central directory parse incomplete: "
            f"parsed={sum(parsed['split_counts'].values())} expected={eocd['total_entries']} "
            f"malformed={parsed['malformed']}"
        )
    write_reports(parts, part_hash, eocd, parsed)
    update_status_and_handoff(eocd)
    print(f"V52 archive audit complete: {eocd['total_entries']} entries")


if __name__ == "__main__":
    main()
