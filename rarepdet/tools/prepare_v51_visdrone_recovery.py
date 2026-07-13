#!/usr/bin/env python
"""Prepare the non-GPU V51 Route-B recovery evidence and frozen folds."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASETS_ROOT = Path(r"D:\datasets")
V50_ROOT = PROJECT_ROOT / "runs/v50_visdrone_seen"
OUTPUT = PROJECT_ROOT / "runs/v51_visdrone_recovery"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
FOLD_COUNT = 3
SEEDS = (0, 1, 2)


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, sort_keys=True, separators=(",", ":"))
        handle.write("\n")


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def git(*args):
    return subprocess.check_output(
        ["git", *args], cwd=PROJECT_ROOT, text=True, encoding="utf-8"
    ).strip()


def rel(path, base=PROJECT_ROOT):
    path = Path(path)
    try:
        return path.resolve().relative_to(Path(base).resolve()).as_posix()
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def candidate_specs():
    visdrone = DATASETS_ROOT / "visdrone"
    specs = [
        ("visdrone_det_train", visdrone / "VisDrone2019-DET-train", "source DET train partition", True),
        ("visdrone_det_val", visdrone / "VisDrone2019-DET-val", "source DET validation partition", True),
        ("visdrone_det_test_dev", visdrone / "VisDrone2019-DET-test-dev", "source DET test-dev partition", True),
        ("visdrone_seen", DATASETS_ROOT / "visdrone_seen", "V50 copied/label-filtered derivative", True),
        ("visdrone_seen_strict", DATASETS_ROOT / "visdrone_seen_strict", "strict subset copied from the same DET source", True),
        ("visdrone_object", visdrone / "VisDrone_object", "class-agnostic derivative of DET train/val", False),
        ("visdrone_prompt_bank", visdrone / "prompt_bank_quality_k4", "derived prompt/reference crops, not an evaluation partition", False),
        ("visdrone_tvpa_refer_banks", visdrone / "tvpa_refer_banks", "repeated reference banks, not an evaluation partition", False),
        ("uavdt_visdrone_mapping", DATASETS_ROOT / "UAVDT_yolo_visdrone_vehicle_subset", "UAVDT data remapped to VisDrone classes; not VisDrone-family source data", False),
    ]
    for path in sorted(visdrone.glob("VisDrone_DAPA_ST_*")):
        if path.is_dir():
            specs.append(
                (
                    path.name.lower(),
                    path,
                    "pseudo-label training derivative built from VisDrone DET train images",
                    False,
                )
            )
    return specs


def list_images(root):
    return sorted(
        path
        for path in Path(root).rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def list_annotation_and_metadata_files(root, include_annotations=True):
    root = Path(root)
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        lower_parts = {part.lower() for part in path.parts}
        is_annotation = path.suffix.lower() == ".txt" and bool(
            {"labels", "annotations"} & lower_parts
        )
        is_metadata = path.suffix.lower() in {".yaml", ".yml", ".json", ".csv", ".md"}
        if (include_annotations and is_annotation) or is_metadata:
            files.append(path)
    return sorted(files)


def v50_image_state():
    inventory = json.loads((V50_ROOT / "image_file_hashes.json").read_text(encoding="utf-8"))
    hashes = {item["sha256"] for item in inventory}
    stems = {Path(item["path"]).stem for item in inventory}
    return inventory, hashes, stems


@lru_cache(maxsize=1)
def v50_text_documents():
    documents = []
    for path in V50_ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".txt", ".csv"}:
            continue
        try:
            documents.append((path, path.read_text(encoding="utf-8", errors="replace").lower()))
        except OSError:
            continue
    return documents


def text_mentions(needle):
    needle = needle.lower()
    hits = []
    for path, text in v50_text_documents():
        if needle in text:
            hits.append(rel(path))
    return sorted(hits)


def audit_candidates():
    cached_audit = OUTPUT / "recovery_audit.json"
    image_inventory_path = OUTPUT / "candidate_image_hashes.json"
    annotation_inventory_path = OUTPUT / "candidate_annotation_hashes.json"
    if cached_audit.is_file() and image_inventory_path.is_file() and annotation_inventory_path.is_file():
        cached = json.loads(cached_audit.read_text(encoding="utf-8"))
        summaries = cached.get("candidates", [])
        if summaries and all("v50_exact_content_overlap_files" in item for item in summaries):
            print("reusing complete candidate hash inventories", flush=True)
            return summaries
    _, v50_hashes, v50_stems = v50_image_state()
    image_inventory = []
    annotation_inventory = []
    summaries = []
    for key, root, lineage, hash_candidate_files in candidate_specs():
        if not root.is_dir():
            continue
        images = list_images(root)
        annotations = list_annotation_and_metadata_files(
            root, include_annotations=hash_candidate_files
        )
        overlap_hashes = set()
        overlap_files = 0
        overlap_stems = 0
        content_hashes = set()
        total_bytes = 0
        for path in images:
            digest = sha256(path) if hash_candidate_files else None
            if digest:
                content_hashes.add(digest)
            if digest in v50_hashes:
                overlap_hashes.add(digest)
                overlap_files += 1
            if path.stem in v50_stems:
                overlap_stems += 1
            total_bytes += path.stat().st_size
            if hash_candidate_files:
                image_inventory.append(
                    {
                        "candidate": key,
                        "path": rel(path, DATASETS_ROOT),
                        "bytes": path.stat().st_size,
                        "sha256": digest,
                        "v50_exact_content_overlap": digest in v50_hashes,
                    }
                )
        for path in annotations:
            annotation_inventory.append(
                {
                    "candidate": key,
                    "path": rel(path, DATASETS_ROOT),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
        name_hits = text_mentions(root.name)
        root_hits = text_mentions(str(root).replace("\\", "/"))
        reasons = []
        if overlap_hashes:
            reasons.append("contains exact image-content overlap with V50")
        if overlap_stems:
            reasons.append("contains V50 filename/sequence-ID overlap")
        if "derivative" in lineage or "subset" in lineage or "reference" in lineage:
            reasons.append("local evidence identifies a derivative/subset rather than an untouched partition")
        if key == "uavdt_visdrone_mapping":
            reasons.append("source identity is UAVDT rather than VisDrone-family data")
        if key.startswith("visdrone_dapa_st"):
            reasons.append("pseudo-label training data are not an untouched evaluation partition")
        if key in {"visdrone_det_train", "visdrone_det_val", "visdrone_det_test_dev"}:
            reasons.append("the V50 generator names this local DET partition as its direct source")
        if not hash_candidate_files:
            reasons.append(
                "excluded by provenance/type gate before per-image hashing; counts and metadata hashes retained"
            )
        eligible = not reasons
        summaries.append(
            {
                "candidate": key,
                "root": str(root),
                "lineage": lineage,
                "candidate_partition_content_hashed": hash_candidate_files,
                "image_files": len(images),
                "unique_image_hashes": len(content_hashes) if hash_candidate_files else None,
                "image_bytes": total_bytes,
                "annotation_or_metadata_files": len(annotations),
                "v50_exact_content_overlap_files": overlap_files if hash_candidate_files else None,
                "v50_exact_content_overlap_unique_hashes": len(overlap_hashes) if hash_candidate_files else None,
                "v50_filename_or_sequence_id_overlap": overlap_stems,
                "v50_reference_hits": sorted(set(name_hits + root_hits)),
                "route_a_eligible": eligible,
                "route_a_rejection_reasons": reasons,
            }
        )
        print(
            f"audited {key}: images={len(images)} exact_v50="
            f"{overlap_files if hash_candidate_files else 'not_applicable'} "
            f"id_overlap={overlap_stems} eligible={eligible}",
            flush=True,
        )
    write_json(image_inventory_path, image_inventory)
    write_json(annotation_inventory_path, annotation_inventory)
    return summaries


def source_lock_checks():
    lock_path = V50_ROOT / "source_lock_v50.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    checks = []

    def add(kind, name, path, expected):
        path = Path(path)
        actual = sha256(path) if path.is_file() else None
        checks.append(
            {
                "kind": kind,
                "name": name,
                "path": rel(path),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "match": actual == expected,
            }
        )

    for path, expected in lock["code_hashes"].items():
        add("code", path, PROJECT_ROOT / path, expected)
    metadata_paths = {
        "annotation_hash_inventory": V50_ROOT / "annotation_file_hashes.json",
        "class_mapping": V50_ROOT / "class_mapping.json",
        "image_hash_inventory": V50_ROOT / "image_file_hashes.json",
        "split_manifest": V50_ROOT / "split_manifest.json",
        "target_yaml": Path(lock["dataset_root"]) / "VisDrone_seen.yaml",
    }
    for name, expected in lock["metadata_hashes"].items():
        add("metadata", name, metadata_paths[name], expected)
    for name, expected in lock["manifests"].items():
        add("manifest", name, V50_ROOT / f"manifests/{name}.txt", expected)
    for name, record in lock["converted_annotations"].items():
        add("converted_annotation", name, PROJECT_ROOT / record["path"], record["sha256"])
    for name, record in lock["checkpoints"].items():
        add("checkpoint", name, PROJECT_ROOT / record["path"], record["sha256"])

    violation = json.loads(
        (V50_ROOT / "protocol_violation_evidence.json").read_text(encoding="utf-8")
    )
    add(
        "protocol_evidence",
        "frozen_source_lock",
        lock_path,
        violation["frozen_rule"]["source_sha256"],
    )
    for event in violation["timeline"]:
        if event.get("path") and event.get("sha256"):
            add("protocol_evidence", event["event"], PROJECT_ROOT / event["path"], event["sha256"])
    continuation = violation.get("training_stop", {}).get("unauthorized_continuation", {})
    continuation_log = V50_ROOT / "rgb_training/seed0/train_log.txt"
    if continuation.get("train_log_sha256") and continuation_log.is_file():
        add(
            "protocol_evidence",
            "unauthorized_continuation_log",
            continuation_log,
            continuation["train_log_sha256"],
        )
    return checks


def active_v50_processes():
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-CimInstance Win32_Process | Where-Object { "
        "$_.CommandLine -match 'run_v50_rgb_queue|train_visdrone_rgb' -and "
        "$_.CommandLine -notmatch 'Get-CimInstance Win32_Process' } | "
        "Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress",
    ]
    output = subprocess.check_output(command, text=True, encoding="utf-8", errors="replace").strip()
    if not output:
        return []
    parsed = json.loads(output)
    return parsed if isinstance(parsed, list) else [parsed]


def load_combined_coco():
    combined = {
        "info": {"description": "V51 immutable union of V50 converted annotations"},
        "licenses": [],
        "categories": [{"id": 1, "name": "vehicle", "supercategory": "vehicle"}],
        "images": [],
        "annotations": [],
    }
    image_lookup = {}
    next_image_id = 1
    next_annotation_id = 1
    for split in ("train", "devval", "test"):
        source = json.loads(
            (V50_ROOT / f"converted_annotations/{split}.json").read_text(encoding="utf-8")
        )
        old_to_new = {}
        for image in source["images"]:
            item = dict(image)
            item["id"] = next_image_id
            old_to_new[int(image["id"])] = next_image_id
            image_lookup[item["file_name"].replace("\\", "/")] = item
            combined["images"].append(item)
            next_image_id += 1
        for annotation in source["annotations"]:
            item = dict(annotation)
            item["id"] = next_annotation_id
            item["image_id"] = old_to_new[int(annotation["image_id"])]
            combined["annotations"].append(item)
            next_annotation_id += 1
    return combined, image_lookup


def make_folds():
    combined, image_lookup = load_combined_coco()
    annotations_by_image = defaultdict(list)
    for annotation in combined["annotations"]:
        annotations_by_image[int(annotation["image_id"])].append(annotation)

    entries = []
    for split in ("train", "devval", "test"):
        for line in (V50_ROOT / f"manifests/{split}.txt").read_text(encoding="utf-8").splitlines():
            entry = line.strip().replace("\\", "/")
            if entry:
                entries.append(entry)
    if len(entries) != len(set(entries)):
        raise RuntimeError("duplicate V50 manifest entries prevent fold freezing")

    groups = defaultdict(list)
    for entry in entries:
        group = Path(entry).stem.split("_")[0]
        groups[group].append(entry)

    group_stats = []
    for group, members in groups.items():
        positives = 0
        ignored = 0
        for entry in members:
            image_id = int(image_lookup[entry]["id"])
            for annotation in annotations_by_image[image_id]:
                if int(annotation.get("ignore", 0)) or int(annotation.get("iscrowd", 0)):
                    ignored += 1
                elif int(annotation.get("category_id", 0)) == 1:
                    positives += 1
        group_stats.append(
            {"group": group, "images": len(members), "positives": positives, "ignored": ignored}
        )

    fold_groups = [set() for _ in range(FOLD_COUNT)]
    fold_totals = [Counter(images=0, positives=0, ignored=0, groups=0) for _ in range(FOLD_COUNT)]
    target_images = len(entries) / FOLD_COUNT
    target_positives = sum(item["positives"] for item in group_stats) / FOLD_COUNT
    ordered = sorted(
        group_stats,
        key=lambda item: (-item["images"], -item["positives"], item["group"]),
    )
    for item in ordered:
        def score(index):
            return (
                fold_totals[index]["images"] / max(target_images, 1)
                + fold_totals[index]["positives"] / max(target_positives, 1),
                fold_totals[index]["images"],
                index,
            )

        selected = min(range(FOLD_COUNT), key=score)
        fold_groups[selected].add(item["group"])
        fold_totals[selected].update(
            images=item["images"], positives=item["positives"], ignored=item["ignored"], groups=1
        )

    folds_dir = OUTPUT / "folds"
    annotations_dir = OUTPUT / "converted_annotations"
    manifest = {
        "generated_at": now(),
        "route": "B_GROUP_DISJOINT_CROSS_VALIDATION",
        "fold_count": FOLD_COUNT,
        "seeds": list(SEEDS),
        "group_rule": "first underscore-delimited filename field",
        "group_rule_regex": r"^([^_]+)_",
        "assignment": "deterministic greedy balance by image and positive-box counts; group-name tie break",
        "source_entries": len(entries),
        "source_groups": len(groups),
        "folds": [],
    }
    integrity_lines = [
        "# V51 Fold Integrity",
        "",
        "- Route: B, pre-registered group-disjoint cross-validation.",
        "- Group key: first underscore-delimited filename field.",
        "- Assignment: deterministic greedy image/positive-box balancing.",
        "- V50 quarantined metrics were not read by this fold builder.",
        "",
        "| Fold | Train images | Val images | Train groups | Val groups | Val positive boxes | Val ignored |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    all_groups = set(groups)
    for fold in range(FOLD_COUNT):
        val_groups = fold_groups[fold]
        train_groups = all_groups - val_groups
        train_entries = sorted(entry for group in train_groups for entry in groups[group])
        val_entries = sorted(entry for group in val_groups for entry in groups[group])
        if train_groups & val_groups:
            raise RuntimeError(f"fold {fold} has group leakage")
        write_text(folds_dir / f"fold_{fold}_train.txt", "\n".join(train_entries))
        write_text(folds_dir / f"fold_{fold}_val.txt", "\n".join(val_entries))

        for role, selected_entries in (("train", train_entries), ("val", val_entries)):
            selected = set(selected_entries)
            selected_images = [image for image in combined["images"] if image["file_name"] in selected]
            selected_ids = {int(image["id"]) for image in selected_images}
            selected_annotations = [
                annotation
                for annotation in combined["annotations"]
                if int(annotation["image_id"]) in selected_ids
            ]
            coco = dict(combined)
            coco["images"] = selected_images
            coco["annotations"] = selected_annotations
            write_json(annotations_dir / f"fold_{fold}_{role}.json", coco)

        val_positive = sum(
            item["positives"] for item in group_stats if item["group"] in val_groups
        )
        val_ignored = sum(item["ignored"] for item in group_stats if item["group"] in val_groups)
        record = {
            "fold": fold,
            "train_images": len(train_entries),
            "val_images": len(val_entries),
            "train_groups": len(train_groups),
            "val_groups": len(val_groups),
            "val_positive_boxes": val_positive,
            "val_ignored_regions": val_ignored,
            "train_manifest_sha256": sha256(folds_dir / f"fold_{fold}_train.txt"),
            "val_manifest_sha256": sha256(folds_dir / f"fold_{fold}_val.txt"),
            "train_annotations_sha256": sha256(annotations_dir / f"fold_{fold}_train.json"),
            "val_annotations_sha256": sha256(annotations_dir / f"fold_{fold}_val.json"),
            "val_group_ids": sorted(val_groups),
        }
        manifest["folds"].append(record)
        integrity_lines.append(
            f"| {fold} | {len(train_entries)} | {len(val_entries)} | {len(train_groups)} | "
            f"{len(val_groups)} | {val_positive} | {val_ignored} |"
        )
    write_json(OUTPUT / "fold_manifest.json", manifest)
    write_text(OUTPUT / "fold_integrity.md", "\n".join(integrity_lines))
    return manifest


def environment():
    result = {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
    }
    try:
        import torch
        import torchvision

        result.update(
            {
                "torch": torch.__version__,
                "torchvision": torchvision.__version__,
                "cuda_runtime": torch.version.cuda,
                "cuda_available": torch.cuda.is_available(),
                "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            }
        )
    except Exception as exc:
        result["torch_error"] = repr(exc)
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=driver_version,name",
                "--format=csv,noheader",
            ],
            text=True,
        ).strip()
        result["nvidia_smi"] = output
    except Exception as exc:
        result["nvidia_smi_error"] = repr(exc)
    return result


def build_source_lock(starting_commit, fold_manifest):
    paths = [
        Path(__file__),
        PROJECT_ROOT / "datasets/visdrone_seen_dataset.py",
        PROJECT_ROOT / "rarepdet/models/rgb_fcos.py",
        PROJECT_ROOT / "rarepdet/train_visdrone_rgb.py",
        PROJECT_ROOT / "rarepdet/tools/eval_v50_visdrone_seen.py",
        PROJECT_ROOT / "rarepdet/tools/eval_v51_visdrone_recovery.py",
        PROJECT_ROOT / "rarepdet/tools/run_v51_cv_queue.py",
        PROJECT_ROOT / "rarepdet/tools/build_v51_cv_reports.py",
        PROJECT_ROOT / "rarepdet/v50_coco.py",
        V50_ROOT / "class_mapping.json",
        OUTPUT / "recovery_audit.json",
        OUTPUT / "route_decision.json",
        OUTPUT / "candidate_image_hashes.json",
        OUTPUT / "candidate_annotation_hashes.json",
        OUTPUT / "fold_manifest.json",
        OUTPUT / "fold_integrity.md",
        OUTPUT / "cv_train_commands.txt",
    ]
    paths.extend(sorted((OUTPUT / "folds").glob("*.txt")))
    paths.extend(sorted((OUTPUT / "converted_annotations").glob("*.json")))
    v50_lock = json.loads((V50_ROOT / "source_lock_v50.json").read_text(encoding="utf-8"))
    lock = {
        "generated_at": now(),
        "starting_commit": starting_commit,
        "branch": git("branch", "--show-current"),
        "route": "B_GROUP_DISJOINT_CROSS_VALIDATION",
        "route_justification": "No untouched VisDrone-family partition exists locally; source partitions overlap V50, while non-overlapping local directories are derived/pseudo/reference data or UAVDT.",
        "dataset_roots": [r"D:\datasets\visdrone_seen", r"D:\datasets\visdrone"],
        "fold_count": FOLD_COUNT,
        "seeds": list(SEEDS),
        "training": {
            "model": "pure RGB RepViT-M0.9--FPN--FCOS",
            "from_scratch": True,
            "epochs": 50,
            "img_size": 640,
            "optimizer": "AdamW",
            "learning_rate": 0.0001,
            "weight_decay": 0.0001,
            "batch_size": 4,
            "checkpoint_selection": "highest frozen-fold validation canonical COCO AP50; first exact tie wins",
        },
        "evaluation": {
            "backend": "pycocotools COCOeval bbox",
            "detector_score_threshold": 0.001,
            "nms_threshold": 0.6,
            "max_detections": 100,
            "fold_access_rule": "evaluate only the frozen validation manifest paired with each training fold; no held-out-test claim",
        },
        "mapping": {
            "vehicle_source_categories": ["car", "van", "truck", "bus"],
            "ignored_regions": "preserved from frozen V50 conversion and excluded as positives",
            "v50_mapping_sha256": sha256(V50_ROOT / "class_mapping.json"),
        },
        "v50_quarantine": "V50 test metrics are excluded from V51 route, fold, checkpoint, threshold, and narrative decisions.",
        "frozen_triair_checkpoints": v50_lock["checkpoints"],
        "fold_summary": fold_manifest["folds"],
        "environment": environment(),
        "frozen_hashes": {rel(path): sha256(path) for path in paths},
    }
    write_json(OUTPUT / "source_lock_v51.json", lock)
    lines = [
        "# V51 Source Lock",
        "",
        f"Generated: `{lock['generated_at']}`",
        f"Starting commit: `{starting_commit}`",
        f"Branch: `{lock['branch']}`",
        "Route: `B_GROUP_DISJOINT_CROSS_VALIDATION`.",
        "",
        "## Frozen protocol",
        "",
        "- Three group-disjoint folds; filename field 1 is the immutable group key.",
        "- Seeds 0, 1, and 2 start from scratch for every fold.",
        "- 50 epochs, RGB 640, batch 4, AdamW, learning rate 1e-4.",
        "- Checkpoint selection uses only the paired frozen validation fold's canonical COCO AP50.",
        "- Score threshold 0.001, NMS 0.6, max detections 100.",
        "- V50 quarantined test metrics are not inputs and cannot become V51 evidence.",
        "- Route B reports cross-validation only; it has no independent or blind test.",
        "",
        "## Frozen artifacts",
        "",
    ]
    lines.extend(f"- `{path}`: `{digest}`" for path, digest in sorted(lock["frozen_hashes"].items()))
    write_text(OUTPUT / "source_lock_v51.md", "\n".join(lines))
    return lock


def write_commands():
    lines = []
    python = sys.executable
    for fold in range(FOLD_COUNT):
        for seed in SEEDS:
            out = OUTPUT / f"cv_training/fold{fold}/seed{seed}"
            command = [
                python,
                str(PROJECT_ROOT / "rarepdet/train_visdrone_rgb.py"),
                "--data", r"D:\datasets\visdrone_seen",
                "--train-manifest", str(OUTPUT / f"folds/fold_{fold}_train.txt"),
                "--train-annotations", str(OUTPUT / f"converted_annotations/fold_{fold}_train.json"),
                "--val-manifest", str(OUTPUT / f"folds/fold_{fold}_val.txt"),
                "--val-annotations", str(OUTPUT / f"converted_annotations/fold_{fold}_val.json"),
                "--epochs", "50", "--batch-size", "4", "--img-size", "640",
                "--device", "cuda", "--lr", "1e-4", "--num-workers", "0",
                "--seed", str(seed), "--detector-score-thr", "0.001",
                "--nms-thresh", "0.6", "--detections-per-img", "100",
                "--out", str(out),
            ]
            lines.append(f"FOLD={fold} SEED={seed} " + subprocess.list2cmdline(command))
    write_text(OUTPUT / "cv_train_commands.txt", "\n".join(lines))
    status = {
        "state": "AWAITING_GPU_AUTHORIZATION",
        "updated_at": now(),
        "route": "B_GROUP_DISJOINT_CROSS_VALIDATION",
        "total_training_runs": FOLD_COUNT * len(SEEDS),
        "runs": [
            {"fold": fold, "seed": seed, "state": "PENDING_FROM_SCRATCH"}
            for fold in range(FOLD_COUNT)
            for seed in SEEDS
        ],
        "zero_shot_fold_evaluations_pending": FOLD_COUNT * 6,
    }
    write_json(OUTPUT / "cv_run_status.json", status)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    starting_commit = git("rev-parse", "HEAD")
    processes = active_v50_processes()
    if processes:
        raise RuntimeError(f"V50 training processes remain alive: {processes}")
    checks = source_lock_checks()
    if not all(item["match"] for item in checks):
        failed = [item for item in checks if not item["match"]]
        raise RuntimeError(f"V50 immutable evidence hash mismatch: {failed}")
    summaries = audit_candidates()
    route_a_candidates = [item for item in summaries if item["route_a_eligible"]]
    if route_a_candidates:
        raise RuntimeError(
            "Route A requires manual provenance review before inference; eligible candidates: "
            + repr(route_a_candidates)
        )

    audit = {
        "generated_at": now(),
        "starting_commit": starting_commit,
        "v50_processes_alive": processes,
        "v50_source_lock_checks": checks,
        "v50_all_hashes_match": all(item["match"] for item in checks),
        "candidate_image_inventory": "runs/v51_visdrone_recovery/candidate_image_hashes.json",
        "candidate_image_inventory_sha256": sha256(OUTPUT / "candidate_image_hashes.json"),
        "candidate_annotation_inventory": "runs/v51_visdrone_recovery/candidate_annotation_hashes.json",
        "candidate_annotation_inventory_sha256": sha256(OUTPUT / "candidate_annotation_hashes.json"),
        "candidates": summaries,
        "seen_meaning": "Local generator evidence establishes only label filtering/subsetting from the same VisDrone DET source; it does not establish an untouched seen/unseen benchmark protocol.",
    }
    write_json(OUTPUT / "recovery_audit.json", audit)
    audit_lines = [
        "# V51 Recovery Audit",
        "",
        f"Generated: `{audit['generated_at']}`",
        f"Starting commit: `{starting_commit}`",
        "",
        "- All frozen V50 source-lock and protocol-evidence hashes match.",
        "- No V50 queue or RGB training process is alive.",
        "- Exact per-file hashes are stored in `candidate_image_hashes.json` and `candidate_annotation_hashes.json`.",
        "- The local `seen` and `seen_strict` directories are copied/filtered derivatives of the same DET train/val/test-dev source used in V50.",
        "- DAPA/object/reference directories are locally documented derivatives, not untouched evaluation partitions.",
        "- The UAVDT directory is a separate dataset remapped to VisDrone class names, not a VisDrone-family partition.",
        "",
        "| Candidate | Images | Exact V50 overlap | ID overlap | Route A |",
        "|---|---:|---:|---:|---|",
    ]
    for item in summaries:
        audit_lines.append(
            f"| {item['candidate']} | {item['image_files']} | {item['v50_exact_content_overlap_files']} | "
            f"{item['v50_filename_or_sequence_id_overlap']} | {'yes' if item['route_a_eligible'] else 'no'} |"
        )
    write_text(OUTPUT / "recovery_audit.md", "\n".join(audit_lines))

    decision = {
        "generated_at": now(),
        "selected_route": "B_GROUP_DISJOINT_CROSS_VALIDATION",
        "route_a_rejected": True,
        "route_a_reasons": [
            "All source VisDrone DET train/val/test-dev images are already present in the V50 inventory.",
            "visdrone_seen_strict is a subset copied from the same source.",
            "Non-overlapping DAPA/reference content is derived from V50-related source identities and is not an untouched evaluation partition.",
            "The local UAVDT mapping is not VisDrone-family data and lacks a train/development/final-test provenance contract for this task.",
        ],
        "blind_or_independent_test_claim_abandoned": True,
        "fold_count": FOLD_COUNT,
        "seeds": list(SEEDS),
        "training_runs": FOLD_COUNT * len(SEEDS),
        "zero_shot_fold_evaluations": FOLD_COUNT * 6,
    }
    write_json(OUTPUT / "route_decision.json", decision)
    write_text(
        OUTPUT / "route_decision.md",
        """# V51 Route Decision

Selected route: `B_GROUP_DISJOINT_CROSS_VALIDATION`.

Route A is rejected because every local source DET partition overlaps V50 exactly, while the remaining VisDrone-named directories are documented derivatives, pseudo-label datasets, or reference banks. The UAVDT mapping is not VisDrone-family data.

V51 therefore abandons independent/blind-test wording. It will use three immutable filename-sequence-group-disjoint folds and seeds 0/1/2, reporting cross-validation only.
""",
    )
    fold_manifest = make_folds()
    write_commands()
    build_source_lock(starting_commit, fold_manifest)
    write_text(
        OUTPUT / "fold_evaluation_log.jsonl",
        json.dumps(
            {
                "at": now(),
                "event": "FROZEN_FOLD_PROTOCOL_CREATED",
                "rule": "append one event per frozen-fold evaluation",
            },
            sort_keys=True,
        ),
    )
    write_text(
        OUTPUT / "claim_boundary.md",
        """# V51 Claim Boundary

- Route B reports pre-registered group-disjoint cross-validation, not an independent or blind test.
- V50 test metrics remain quarantined and are excluded from V51 selection and reporting.
- RGB-only evidence does not validate thermal or event generalization.
- Zero-filled channels are a controlled missing-modality intervention, not physical sensor failure.
- No official VisDrone benchmark status, calibrated reliability, significance, universal causality, or optimal-dropout claim is allowed.
""",
    )
    write_text(
        OUTPUT / "preflight_commands.txt",
        f"{sys.executable} rarepdet/tools/prepare_v51_visdrone_recovery.py\n"
        f"{sys.executable} -m unittest discover -s tests -p 'test_v51_visdrone_recovery.py' -v",
    )
    write_text(
        OUTPUT / "preflight_outputs.txt",
        f"starting_commit={starting_commit}\n"
        f"v50_hash_checks={len(checks)} all_match=true\n"
        "v50_processes_alive=0\n"
        f"candidate_partitions={len(summaries)} route_a_eligible=0\n"
        f"route=B folds={FOLD_COUNT} groups={fold_manifest['source_groups']} images={fold_manifest['source_entries']}\n"
        "gpu_training_started=false awaiting_explicit_authorization=true",
    )
    print(f"prepared V51 Route B under {OUTPUT}")


if __name__ == "__main__":
    main()
