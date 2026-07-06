#!/usr/bin/env python
"""Build the frozen V40 v2 experiment contract.

This script writes configuration, provenance, and smoke-check records only. It
does not start training, metric evaluation, profiling, manuscript work, or any
external-data workflow.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
from datetime import datetime


CONTRACT_REL = Path("reproducibility/v40_experiment_contract_v1")
V40_SPLIT_REL = Path("reproducibility/v40_expanded_adjacency_component_split_v2")
TRAIN_MANIFEST_REL = V40_SPLIT_REL / "manifests" / "v40_expanded_adjacency_component_disjoint_train.txt"
VAL_MANIFEST_REL = V40_SPLIT_REL / "manifests" / "v40_expanded_adjacency_component_disjoint_val.txt"
V40_STATUS_REL = V40_SPLIT_REL / "reports" / "V40_V2_EXPANDED_ADJACENCY_SPLIT_STATUS.json"

DEFAULT_DATASET_ROOT = Path(r"D:\download\triair")
DEFAULT_PYTHON = Path(r"C:\Users\xinnan\.conda\envs\pytorch\python.exe")

LOCKED_EPOCHS = 50
LOCKED_IMG_SIZE = 640
LOCKED_BATCH_SIZE = 4
LOCKED_LR = "1e-4"
LOCKED_LR_FLOAT = 1e-4
LOCKED_NUM_WORKERS = 0
LOCKED_DEVICE = "cuda"
DETECTOR_SCORE_THR = 0.001
METRIC_SCORE_THR = 0.50
NMS_THRESH = 0.6
DETECTIONS_PER_IMG = 100
RUN_SEEDS = (0, 2)

SOURCE_FILES = [
    ("task_doc", Path("docs/V40_CONTRACT_NEXT_TASK.md")),
    ("master_plan", Path("docs/PRE_MANUSCRIPT_V40_MASTER_PLAN.md")),
    ("v40_status_json", V40_STATUS_REL),
    ("v40_status_md", V40_SPLIT_REL / "reports" / "V40_V2_EXPANDED_ADJACENCY_SPLIT_STATUS.md"),
    ("v40_split_audit_json", V40_SPLIT_REL / "audits" / "v40_split_audit_report.json"),
    ("v40_split_audit_md", V40_SPLIT_REL / "audits" / "v40_split_audit_report.md"),
    ("train_manifest", TRAIN_MANIFEST_REL),
    ("validation_manifest", VAL_MANIFEST_REL),
    ("trainer", Path("rarepdet/train_early_fusion.py")),
    ("evaluator", Path("rarepdet/eval_map.py")),
    ("metrics", Path("rarepdet/metrics.py")),
    ("detection_dataset_adapter", Path("rarepdet/data.py")),
    ("triair_dataset", Path("datasets/triair_dataset.py")),
    ("detector_builder", Path("rarepdet/models/early_fusion_fcos.py")),
    ("repvit_backbone", Path("rarepdet/models/repvit_fpn_backbone.py")),
    ("availability_model_not_used_in_v40_core", Path("rarepdet/models/availability_reliability_fusion_fcos.py")),
    ("standardized_eval_protocol_doc", Path("docs/STANDARDIZED_EVALUATION_V23.md")),
    ("requirements", Path("requirements.txt")),
]


def project_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def rel_to_root(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_output(root: Path, args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"NA ({exc})"


def read_nonempty_manifest_lines(path: Path) -> list[str]:
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        item = raw.strip()
        if item and not item.startswith("#"):
            lines.append(item)
    return lines


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def find_dataset_dirs(data_root: Path) -> tuple[Path, Path]:
    candidates = [
        (data_root / "images", data_root / "labels"),
        (data_root / "data" / "images", data_root / "data" / "labels"),
    ]
    for image_dir, label_dir in candidates:
        if image_dir.is_dir() and label_dir.is_dir():
            return image_dir, label_dir
    tried = "; ".join(f"{image_dir} | {label_dir}" for image_dir, label_dir in candidates)
    raise FileNotFoundError(f"Could not find TriAir images/labels under {data_root}; tried {tried}")


def build_unique_stem_map(paths: list[Path], kind: str) -> dict[str, Path]:
    by_stem: dict[str, Path] = {}
    duplicates = []
    for path in paths:
        previous = by_stem.get(path.stem)
        if previous is not None:
            duplicates.append((path.stem, previous, path))
        else:
            by_stem[path.stem] = path
    if duplicates:
        sample = "; ".join(f"{stem}: {first} | {second}" for stem, first, second in duplicates[:5])
        raise ValueError(f"Duplicate {kind} stems would make the label-count method ambiguous: {sample}")
    return by_stem


def resolve_manifest_image(entry: str, data_root: Path, image_dir: Path, image_by_stem: dict[str, Path]) -> Path:
    item = Path(entry)
    if item.is_absolute():
        candidate = item
    elif item.suffix.lower() == ".npy":
        candidates = [data_root / item, image_dir / item, image_by_stem.get(item.stem)]
        candidate = next((path for path in candidates if path is not None and path.is_file()), None)
    else:
        candidate = image_by_stem.get(entry)
    if candidate is None or not candidate.is_file():
        raise FileNotFoundError(f"Could not resolve manifest entry {entry!r} under {data_root}")
    return candidate.resolve()


def count_label_rows_for_manifest(manifest_path: Path, data_root: Path) -> dict:
    image_dir, label_dir = find_dataset_dirs(data_root)
    image_by_stem = build_unique_stem_map(sorted(image_dir.rglob("*.npy")), ".npy image")
    label_by_stem = build_unique_stem_map(sorted(label_dir.rglob("*.txt")), ".txt label")

    entries = read_nonempty_manifest_lines(manifest_path)
    image_paths = []
    missing_txt = 0
    empty_txt = 0
    labeled_images = 0
    total_boxes = 0
    class_counts: dict[str, int] = {}

    for entry in entries:
        image_path = resolve_manifest_image(entry, data_root, image_dir, image_by_stem)
        image_paths.append(str(image_path))
        label_path = label_by_stem.get(image_path.stem)
        if label_path is None:
            missing_txt += 1
            continue
        nonempty = [line.strip() for line in label_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
        if not nonempty:
            empty_txt += 1
            continue
        labeled_images += 1
        total_boxes += len(nonempty)
        for line in nonempty:
            class_id = line.split()[0]
            class_counts[class_id] = class_counts.get(class_id, 0) + 1

    duplicate_paths = len(image_paths) - len(set(image_paths))
    return {
        "manifest": rel_to_root(manifest_path, project_root_from_script()),
        "entries": len(entries),
        "resolved_images": len(image_paths),
        "duplicate_resolved_images": duplicate_paths,
        "images_with_label_txt_and_boxes": labeled_images,
        "missing_label_txt_images": missing_txt,
        "empty_label_txt_images": empty_txt,
        "gt_boxes": total_boxes,
        "raw_class_distribution": class_counts,
        "image_dir": str(image_dir),
        "label_dir": str(label_dir),
    }


def runtime_environment(device_preference: str) -> dict:
    env = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "cuda_device_preference": device_preference,
    }
    try:
        import numpy
        import timm
        import torch
        import torchvision

        env.update(
            {
                "numpy": numpy.__version__,
                "pytorch": torch.__version__,
                "torchvision": torchvision.__version__,
                "timm": getattr(timm, "__version__", "NA"),
                "torch_cuda": str(torch.version.cuda),
                "cuda_available": str(torch.cuda.is_available()),
                "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NA",
                "cudnn_version": str(torch.backends.cudnn.version()),
            }
        )
    except Exception as exc:
        env["torch_stack_probe_error"] = f"{type(exc).__name__}: {exc}"
    try:
        smi = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        env["nvidia_smi"] = smi
    except Exception as exc:
        env["nvidia_smi"] = f"NA ({exc})"
    return env


def source_lock_rows(root: Path) -> list[dict]:
    rows = []
    for role, rel_path in SOURCE_FILES:
        path = root / rel_path
        exists = path.is_file()
        rows.append(
            {
                "role": role,
                "path": rel_path.as_posix(),
                "exists": "yes" if exists else "no",
                "bytes": path.stat().st_size if exists else "NA",
                "sha256": sha256_file(path) if exists else "NA",
            }
        )
    for role, rel_path in [
        ("contract_builder_script", CONTRACT_REL / "scripts" / "build_v40_experiment_contract.py"),
        ("contract_validator_script", CONTRACT_REL / "scripts" / "validate_v40_experiment_contract.py"),
    ]:
        path = root / rel_path
        exists = path.is_file()
        rows.append(
            {
                "role": role,
                "path": rel_path.as_posix(),
                "exists": "yes" if exists else "no",
                "bytes": path.stat().st_size if exists else "NA",
                "sha256": sha256_file(path) if exists else "NA",
            }
        )
    return rows


def run_matrix() -> list[dict]:
    rows = []
    specs = [
        ("early", "matched early fusion", "NA", "early", "0.00"),
        ("reliability_p000", "reliability-aware fusion p=0.00", "0.00", "reliability", "0.00"),
        ("reliability_p015", "reliability-aware fusion p=0.15", "0.15", "reliability", "0.15"),
        ("reliability_p020", "reliability-aware fusion p=0.20", "0.20", "reliability", "0.20"),
    ]
    for prefix, description, dropout_label, model_type, dropout_arg in specs:
        for seed in RUN_SEEDS:
            run_id = f"{prefix}_seed{seed}_e50"
            rows.append(
                {
                    "run_id": run_id,
                    "description": description,
                    "model_type": model_type,
                    "seed": seed,
                    "modality_dropout": dropout_arg,
                    "dropout_label": dropout_label,
                    "epochs": LOCKED_EPOCHS,
                    "img_size": LOCKED_IMG_SIZE,
                    "batch_size": LOCKED_BATCH_SIZE,
                    "lr": LOCKED_LR,
                    "num_workers": LOCKED_NUM_WORKERS,
                    "train_manifest": TRAIN_MANIFEST_REL.as_posix(),
                    "validation_manifest": VAL_MANIFEST_REL.as_posix(),
                    "out_dir": f"runs/v40_expanded_adjacency/{run_id}",
                    "eligible_for_reliability_selection": "yes" if model_type == "reliability" else "no_comparator_only",
                }
            )
    return rows


def command_templates(root: Path, dataset_root: Path, python_path: Path) -> list[dict]:
    rows = []
    train_manifest_abs = root / TRAIN_MANIFEST_REL
    val_manifest_abs = root / VAL_MANIFEST_REL
    python_token = str(python_path) if python_path.is_file() else "<PYTORCH_PYTHON>"
    for row in run_matrix():
        train_cmd = [
            python_token,
            "rarepdet/train_early_fusion.py",
            "--model",
            row["model_type"],
            "--data",
            str(dataset_root),
            "--train-split",
            str(train_manifest_abs),
            "--val-split",
            str(val_manifest_abs),
            "--epochs",
            str(LOCKED_EPOCHS),
            "--batch-size",
            str(LOCKED_BATCH_SIZE),
            "--img-size",
            str(LOCKED_IMG_SIZE),
            "--device",
            LOCKED_DEVICE,
            "--lr",
            LOCKED_LR,
            "--num-workers",
            str(LOCKED_NUM_WORKERS),
            "--modality-dropout",
            row["modality_dropout"],
            "--seed",
            str(row["seed"]),
            "--out",
            row["out_dir"],
        ]
        eval_cmd = [
            python_token,
            "rarepdet/eval_map.py",
            "--model",
            row["model_type"],
            "--data",
            str(dataset_root),
            "--split-file",
            str(val_manifest_abs),
            "--weights",
            f"{row['out_dir']}/weights/best.pt",
            "--img-size",
            str(LOCKED_IMG_SIZE),
            "--device",
            LOCKED_DEVICE,
            "--batch-size",
            str(LOCKED_BATCH_SIZE),
            "--num-workers",
            str(LOCKED_NUM_WORKERS),
            "--detector-score-thr",
            str(DETECTOR_SCORE_THR),
            "--metric-score-thr",
            f"{METRIC_SCORE_THR:.2f}",
            "--nms-thresh",
            str(NMS_THRESH),
            "--detections-per-img",
            str(DETECTIONS_PER_IMG),
            "--out",
            f"{row['out_dir']}/standardized_eval/eval_results.txt",
        ]
        rows.append(
            {
                "run_id": row["run_id"],
                "train_command_template": " ".join(train_cmd),
                "standardized_evaluator_command_template": " ".join(eval_cmd),
            }
        )
    return rows


def label_free_config_smoke(root: Path, dataset_root: Path, python_path: Path) -> tuple[dict, list[dict]]:
    checks = []
    status = "PASS"

    def add(name: str, observed, expected, ok: bool) -> None:
        nonlocal status
        checks.append({"check": name, "observed": observed, "expected": expected, "status": "PASS" if ok else "FAIL"})
        if not ok:
            status = "FAIL"

    gate0 = json.loads((root / V40_STATUS_REL).read_text(encoding="utf-8"))
    add("gate0_status", gate0.get("status"), "V40_V2_READY_FOR_FROZEN_RERUN", gate0.get("status") == "V40_V2_READY_FOR_FROZEN_RERUN")
    add("gate0_training_started", gate0.get("training_started"), False, gate0.get("training_started") is False)
    add("gate0_evaluation_started", gate0.get("evaluation_started"), False, gate0.get("evaluation_started") is False)

    train_lines = read_nonempty_manifest_lines(root / TRAIN_MANIFEST_REL)
    val_lines = read_nonempty_manifest_lines(root / VAL_MANIFEST_REL)
    add("train_manifest_count", len(train_lines), 7439, len(train_lines) == 7439)
    add("validation_manifest_count", len(val_lines), 2213, len(val_lines) == 2213)
    add("manifest_overlap", len(set(train_lines) & set(val_lines)), 0, len(set(train_lines) & set(val_lines)) == 0)
    add("run_matrix_count", len(run_matrix()), 8, len(run_matrix()) == 8)
    add("dataset_root_recorded", str(dataset_root), str(DEFAULT_DATASET_ROOT), str(dataset_root) == str(DEFAULT_DATASET_ROOT))
    add("python_for_future_commands_recorded", str(python_path), "existing path or <PYTORCH_PYTHON>", python_path.is_file() or str(python_path) == "<PYTORCH_PYTHON>")

    commands = command_templates(root, dataset_root, python_path)
    forbidden_tokens = ["v40_expanded_adjacency_component_split_v1", "v40_guard", "finish_task.ps1", "eval_missing_modality", "profile_", "DroneVehicle"]
    command_blob = "\n".join(item["train_command_template"] + "\n" + item["standardized_evaluator_command_template"] for item in commands)
    for token in forbidden_tokens:
        add(f"command_excludes_{token}", str(token in command_blob), "False", token not in command_blob)

    source_rows = source_lock_rows(root)
    missing = [row["path"] for row in source_rows if row["exists"] != "yes"]
    add("source_lock_files_exist", ",".join(missing) if missing else "all_present", "all_present", not missing)

    return {"status": status, "checks": checks}, checks


def model_forward_smoke(root: Path, dataset_root: Path, device_preference: str) -> dict:
    sys.path.insert(0, str(root))
    smoke = {
        "status": "PASS",
        "note": "One validation-batch loader read plus eval-mode forward passes only; no loss, optimizer step, checkpoint, metric computation, or result recording.",
        "device_preference": device_preference,
        "models_checked": [],
    }
    try:
        import torch
        from torch.utils.data import DataLoader

        from datasets.triair_dataset import collate_fn
        from rarepdet.data import DetectionTriAirDataset
        from rarepdet.models.early_fusion_fcos import build_detector

        random.seed(20260706)
        torch.manual_seed(20260706)
        requested = torch.device(device_preference)
        if requested.type == "cuda" and not torch.cuda.is_available():
            requested = torch.device("cpu")
        smoke["device_used"] = str(requested)

        dataset = DetectionTriAirDataset(
            str(dataset_root),
            split_file=str(root / VAL_MANIFEST_REL),
            mode="rgbte",
            train=False,
            modality_dropout=0.0,
        )
        loader = DataLoader(
            dataset,
            batch_size=1,
            shuffle=False,
            num_workers=0,
            collate_fn=collate_fn,
            pin_memory=(requested.type == "cuda"),
        )
        images, _targets = next(iter(loader))
        smoke["loader"] = {
            "split": VAL_MANIFEST_REL.as_posix(),
            "dataset_len": len(dataset),
            "batch_size": 1,
            "shuffle": False,
            "num_workers": 0,
            "sample_image_shape": list(images[0].shape),
            "sample_path": str(dataset.dataset.sample_infos[0]["image_path"]),
            "target_loaded_but_not_scored": True,
        }
        device_images = [image.to(requested, non_blocking=True) for image in images]
        for model_type in ("early", "reliability"):
            model = build_detector(
                model_type=model_type,
                model_name="repvit_m0_9.dist_300e_in1k",
                img_size=LOCKED_IMG_SIZE,
                num_classes=2,
                fpn_out_channels=128,
                score_thresh=DETECTOR_SCORE_THR,
                nms_thresh=NMS_THRESH,
                detections_per_img=DETECTIONS_PER_IMG,
            ).to(requested)
            model.eval()
            with torch.inference_mode():
                outputs = model(device_images)
            if not isinstance(outputs, list) or len(outputs) != 1:
                raise RuntimeError(f"{model_type} smoke output shape was not a one-item list")
            output = outputs[0]
            required = {"boxes", "labels", "scores"}
            if set(output.keys()) != required:
                raise RuntimeError(f"{model_type} output keys {sorted(output.keys())} != {sorted(required)}")
            smoke["models_checked"].append(
                {
                    "model_type": model_type,
                    "mode": "eval",
                    "forward_completed": True,
                    "output_keys": sorted(output.keys()),
                    "experimental_result_recorded": False,
                }
            )
            del model
            if requested.type == "cuda":
                torch.cuda.empty_cache()
    except Exception as exc:
        smoke["status"] = "FAIL"
        smoke["error"] = f"{type(exc).__name__}: {exc}"
    return smoke


def write_markdown_outputs(root: Path, payload: dict) -> None:
    contract_dir = root / CONTRACT_REL / "contract"
    smoke_dir = root / CONTRACT_REL / "smoke_tests"
    source_dir = root / CONTRACT_REL / "source_lock"
    reports_dir = root / CONTRACT_REL / "reports"

    contract = payload["contract"]
    lines = [
        "# V40 v2 Experiment Contract",
        "",
        f"- Status: `{contract['status']}`",
        f"- Generated: `{contract['generated_at']}`",
        f"- Input commit: `{contract['input_commit']}`",
        f"- Output commit: `{contract['output_commit']}`",
        f"- Evidence scope: `{contract['evidence_scope']}`",
        f"- Required split status: `{contract['gate0_status']}`",
        "",
        "## Locked Inputs",
        "",
        f"- Train manifest: `{contract['manifests']['train']['path']}`",
        f"- Train manifest SHA-256: `{contract['manifests']['train']['sha256']}`",
        f"- Validation manifest: `{contract['manifests']['validation']['path']}`",
        f"- Validation manifest SHA-256: `{contract['manifests']['validation']['sha256']}`",
        f"- Dataset root: `{contract['dataset']['root']}`",
        f"- Label-count method: {contract['dataset']['label_count_method']}",
        "",
        "## Locked Training Recipe",
        "",
        f"- Epochs: `{LOCKED_EPOCHS}`",
        f"- Image size: `{LOCKED_IMG_SIZE}`",
        f"- Batch size: `{LOCKED_BATCH_SIZE}`",
        f"- Learning rate: `{LOCKED_LR}`",
        f"- Optimizer: `{contract['training_recipe']['optimizer']}`",
        f"- Scheduler: `{contract['training_recipe']['scheduler']}`",
        f"- Data loader: `{contract['training_recipe']['data_loader']}`",
        f"- Deterministic settings: `{contract['training_recipe']['deterministic_settings']}`",
        f"- Augmentations: `{contract['training_recipe']['augmentations']}`",
        "",
        "## Locked Evaluation Recipe",
        "",
        f"- Evaluator: `{contract['evaluation_recipe']['evaluator_path']}`",
        f"- Detector score threshold: `{DETECTOR_SCORE_THR}`",
        f"- Metric operating threshold: `{METRIC_SCORE_THR:.2f}`",
        f"- NMS threshold: `{NMS_THRESH}`",
        f"- Detections per image: `{DETECTIONS_PER_IMG}`",
        f"- AP definition: {contract['evaluation_recipe']['ap_definition']}",
        "",
        "## Selection Rule",
        "",
        contract["selection_rule"],
        "",
        "## No Adaptive Changes",
        "",
        contract["no_adaptive_changes_rule"],
        "",
        "## Prohibited Tuning Actions",
        "",
    ]
    lines.extend(f"- {item}" for item in contract["prohibited_tuning_actions"])
    lines.extend(
        [
            "",
            "## Smoke Checks",
            "",
            f"- Label-free configuration smoke: `{payload['label_free_smoke']['status']}`",
            f"- Data-loader/model-forward smoke: `{payload['model_forward_smoke']['status']}`",
            "",
            "This contract is a pre-run gate. Smoke outputs are not experimental results.",
        ]
    )
    (contract_dir / "V40_EXPERIMENT_CONTRACT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    selection_lines = [
        "# V40 Selection Rule",
        "",
        contract["selection_rule"],
        "",
        "Early fusion is a comparator and is not eligible for reliability-dropout selection.",
        "The rule may not be altered because of V40 validation performance.",
    ]
    (contract_dir / "selection_rule.md").write_text("\n".join(selection_lines) + "\n", encoding="utf-8")

    prohibited_lines = [
        "# V40 Prohibited Tuning Actions",
        "",
        "The following actions are disallowed after this contract is frozen:",
        "",
    ]
    prohibited_lines.extend(f"- {item}" for item in contract["prohibited_tuning_actions"])
    (contract_dir / "prohibited_tuning_actions.md").write_text("\n".join(prohibited_lines) + "\n", encoding="utf-8")

    source_lines = [
        "# V40 Contract Source Lock",
        "",
        f"- Input commit: `{contract['input_commit']}`",
        f"- Source rows: `{len(payload['source_lock_rows'])}`",
        f"- Train manifest SHA-256: `{contract['manifests']['train']['sha256']}`",
        f"- Validation manifest SHA-256: `{contract['manifests']['validation']['sha256']}`",
        "",
        "See `input_lock_manifest.csv` for all locked paths.",
    ]
    (source_dir / "input_lock.md").write_text("\n".join(source_lines) + "\n", encoding="utf-8")

    smoke_lines = [
        "# V40 Label-Free Configuration Smoke",
        "",
        f"- Status: `{payload['label_free_smoke']['status']}`",
        "- This smoke reads manifests, hashes, source files, and command templates only.",
        "- It does not read label txt files, image arrays, checkpoints, or predictions.",
        "",
        "| Check | Observed | Expected | Status |",
        "| --- | --- | --- | --- |",
    ]
    for check in payload["label_free_smoke"]["checks"]:
        smoke_lines.append(f"| {check['check']} | `{check['observed']}` | `{check['expected']}` | `{check['status']}` |")
    (smoke_dir / "label_free_config_smoke.md").write_text("\n".join(smoke_lines) + "\n", encoding="utf-8")

    forward = payload["model_forward_smoke"]
    forward_lines = [
        "# V40 Data-Loader / Model-Forward Smoke",
        "",
        f"- Status: `{forward['status']}`",
        f"- Note: {forward.get('note', '')}",
        f"- Device used: `{forward.get('device_used', 'NA')}`",
        "- This check performs one loader read and eval-mode forward passes only.",
        "- It does not compute AP, F1, precision, recall, loss, runtime, or checkpoint output.",
        "",
    ]
    if "loader" in forward:
        loader = forward["loader"]
        forward_lines.extend(
            [
                "## Loader",
                "",
                f"- Split: `{loader['split']}`",
                f"- Dataset length: `{loader['dataset_len']}`",
                f"- Sample image shape: `{loader['sample_image_shape']}`",
                f"- Sample path: `{loader['sample_path']}`",
                "",
            ]
        )
    forward_lines.extend(["## Models", "", "| Model | Forward Completed | Output Keys | Experimental Result Recorded |", "| --- | --- | --- | --- |"])
    for item in forward.get("models_checked", []):
        forward_lines.append(
            f"| {item['model_type']} | `{item['forward_completed']}` | `{','.join(item['output_keys'])}` | `{item['experimental_result_recorded']}` |"
        )
    if "error" in forward:
        forward_lines.extend(["", f"Error: `{forward['error']}`"])
    (smoke_dir / "model_forward_smoke.md").write_text("\n".join(forward_lines) + "\n", encoding="utf-8")

    status = payload["status_report"]
    status_lines = [
        "# V40 Experiment Contract Status",
        "",
        f"- Status: `{status['status']}`",
        f"- Generated: `{status['generated_at']}`",
        f"- Input commit: `{status['input_commit']}`",
        f"- Output commit: `{status['output_commit']}`",
        f"- Gate 0 status: `{status['gate0_status']}`",
        f"- Training started: `{status['training_started']}`",
        f"- Metric evaluation started: `{status['metric_evaluation_started']}`",
        f"- Profiling started: `{status['profiling_started']}`",
        f"- Manuscript changed: `{status['manuscript_changed']}`",
        f"- DroneVehicle changed: `{status['dronevehicle_changed']}`",
        "",
        "## Core Counts",
        "",
        f"- Train images: `{status['train_count']}`",
        f"- Validation images: `{status['validation_count']}`",
        f"- Validation GT boxes: `{status['validation_gt_boxes']}`",
        "",
        "## Next Allowed Action",
        "",
        "After this contract is accepted, the next allowed action is Gate 2 core V40 fusion comparison under this frozen contract.",
    ]
    (reports_dir / "V40_EXPERIMENT_CONTRACT_STATUS.md").write_text("\n".join(status_lines) + "\n", encoding="utf-8")


def write_output_manifest(root: Path) -> None:
    contract_root = root / CONTRACT_REL
    rows = []
    for path in sorted(contract_root.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        rel = rel_to_root(path, root)
        if rel == (CONTRACT_REL / "reports" / "output_sha256_manifest.csv").as_posix():
            continue
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    write_csv(contract_root / "reports" / "output_sha256_manifest.csv", rows, ["path", "bytes", "sha256"])


def build_contract_payload(root: Path, dataset_root: Path, python_path: Path, device: str) -> dict:
    generated_at = datetime.now().isoformat(timespec="seconds")
    input_commit = git_output(root, ["rev-parse", "HEAD"])
    output_commit = "PENDING_FINAL_COMMIT_RECORDED_IN_GIT_HISTORY_AND_FINAL_RESPONSE"
    gate0_status = json.loads((root / V40_STATUS_REL).read_text(encoding="utf-8"))

    train_count = count_label_rows_for_manifest(root / TRAIN_MANIFEST_REL, dataset_root)
    val_count = count_label_rows_for_manifest(root / VAL_MANIFEST_REL, dataset_root)
    source_rows = source_lock_rows(root)
    label_free_payload, label_free_rows = label_free_config_smoke(root, dataset_root, python_path)
    forward_payload = model_forward_smoke(root, dataset_root, device)
    overall_pass = (
        gate0_status.get("status") == "V40_V2_READY_FOR_FROZEN_RERUN"
        and label_free_payload["status"] == "PASS"
        and forward_payload["status"] == "PASS"
        and train_count["entries"] == 7439
        and val_count["entries"] == 2213
        and val_count["gt_boxes"] == 5867
    )
    status = "V40_EXPERIMENT_CONTRACT_PASS" if overall_pass else "V40_EXPERIMENT_CONTRACT_BLOCKED"

    contract = {
        "schema_version": "v40_experiment_contract_v1",
        "status": status,
        "generated_at": generated_at,
        "input_commit": input_commit,
        "output_commit": output_commit,
        "evidence_scope": "validation-only evidence on the V40 v2 expanded-adjacency component-disjoint split",
        "required_phrase": "human-adjudicated adjacent-or-near-identical component",
        "gate0_status": gate0_status.get("status"),
        "manifests": {
            "train": {
                "path": TRAIN_MANIFEST_REL.as_posix(),
                "sha256": sha256_file(root / TRAIN_MANIFEST_REL),
                "count": train_count["entries"],
                "gt_boxes": train_count["gt_boxes"],
            },
            "validation": {
                "path": VAL_MANIFEST_REL.as_posix(),
                "sha256": sha256_file(root / VAL_MANIFEST_REL),
                "count": val_count["entries"],
                "gt_boxes": val_count["gt_boxes"],
            },
        },
        "dataset": {
            "root": str(dataset_root),
            "image_dir": val_count["image_dir"],
            "label_dir": val_count["label_dir"],
            "label_count_method": "Resolve each manifest entry to a .npy image, match the label txt by unique stem under the TriAir label directory, count non-empty txt rows as GT boxes, and count missing txt files as zero-target images.",
            "class_mapping": "TriAir raw class 0 is shifted to torchvision foreground label 1; background remains 0.",
            "channels": "RGB channels 0-2, thermal channel 3, event channel 4; mode=rgbte.",
        },
        "model_source": {
            "model_name": "repvit_m0_9.dist_300e_in1k",
            "pretrained": False,
            "num_classes": 2,
            "fpn_out_channels": 128,
            "fc_os_anchor_sizes": "((4,), (8,), (16,), (32,))",
            "relevant_file_hashes": {row["path"]: row["sha256"] for row in source_rows if row["exists"] == "yes"},
        },
        "training_recipe": {
            "trainer_path": "rarepdet/train_early_fusion.py",
            "epochs": LOCKED_EPOCHS,
            "img_size": LOCKED_IMG_SIZE,
            "batch_size": LOCKED_BATCH_SIZE,
            "learning_rate": LOCKED_LR_FLOAT,
            "optimizer": "torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)",
            "scheduler": "none in trainer source",
            "augmentations": "No mosaic, mixup, crop, flip, color jitter, or spatial augmentation in the project DetectionTriAirDataset path; modality dropout is the only training-time augmentation and is locked per run.",
            "deterministic_settings": "Seeds 0 and 2 set Python random, NumPy, torch, CUDA manual_seed_all, cudnn.deterministic=True, cudnn.benchmark=False, torch deterministic algorithms warn_only when supported.",
            "data_loader": "train DataLoader batch_size=4 shuffle=True num_workers=0 collate_fn=datasets.triair_dataset.collate_fn pin_memory=True on CUDA with seeded CPU generator; validation DataLoader shuffle=False.",
            "checkpoint_policy": "trainer writes weights/last.pt each epoch and weights/best.pt when in-training validation AP50 improves under the frozen trainer recipe",
        },
        "evaluation_recipe": {
            "evaluator_path": "rarepdet/eval_map.py",
            "metrics_path": "rarepdet/metrics.py",
            "detector_score_thr": DETECTOR_SCORE_THR,
            "metric_score_thr": METRIC_SCORE_THR,
            "nms_thresh": NMS_THRESH,
            "detections_per_img": DETECTIONS_PER_IMG,
            "img_size": LOCKED_IMG_SIZE,
            "batch_size": LOCKED_BATCH_SIZE,
            "num_workers": LOCKED_NUM_WORKERS,
            "ap_definition": "Project-local single-class score-ranked AP at IoU 0.50 and 0.75 from rarepdet/metrics.py; not COCO AP50:95 and not pycocotools.",
        },
        "run_seeds": list(RUN_SEEDS),
        "output_directory_naming": "runs/v40_expanded_adjacency/{run_id}",
        "selection_rule": "Choose one reliability-dropout setting only after all six reliability runs finish: highest two-run mean AP50, then highest two-run mean F1, then highest two-run mean AP75, with exact-tie fallback p=0.00 then p=0.15 then p=0.20.",
        "no_adaptive_changes_rule": "No model, loader, optimizer, scheduler, augmentation, threshold, checkpoint-selection, seed, split, command, or output-naming setting may be changed because of V40 validation performance.",
        "prohibited_tuning_actions": [
            "Do not start p=0.20 or any other V40 training until this contract is accepted.",
            "Do not change V40 v2 train, validation, or guard manifests.",
            "Do not use the guard partition for model selection or performance reporting.",
            "Do not change raw data, labels, model code, loader code, trainer core, evaluator core, or prior V38/V39 artifacts.",
            "Do not use AP, F1, loss, predictions, confidence, checkpoints, or qualitative images to change split or training settings.",
            "Do not use DroneVehicle or any external data in the V40 evidence pipeline.",
            "Do not run robustness, profiling, qualitative, manuscript, or submission work under Gate 1.",
            "Do not selectively retry a weak-scoring run; resolve technical failures only by documented full-contract policy.",
            "Do not call finish_task.ps1 for V40 master-plan gates.",
        ],
    }

    status_report = {
        "status": status,
        "generated_at": generated_at,
        "input_commit": input_commit,
        "output_commit": output_commit,
        "gate0_status": gate0_status.get("status"),
        "train_count": train_count["entries"],
        "validation_count": val_count["entries"],
        "validation_gt_boxes": val_count["gt_boxes"],
        "source_lock_manifest_sha256": "written_after_payload",
        "training_started": False,
        "metric_evaluation_started": False,
        "profiling_started": False,
        "robustness_started": False,
        "manuscript_changed": False,
        "dronevehicle_changed": False,
        "raw_data_changed": False,
        "labels_changed": False,
        "model_or_training_core_changed": False,
        "guard_used_for_model_selection": False,
        "next_allowed_action": "Gate 2 core V40 fusion comparison under this frozen contract only.",
    }

    return {
        "contract": contract,
        "status_report": status_report,
        "source_lock_rows": source_rows,
        "run_matrix": run_matrix(),
        "command_templates": command_templates(root, dataset_root, python_path),
        "label_counts": {"train": train_count, "validation": val_count},
        "label_free_smoke": label_free_payload,
        "label_free_rows": label_free_rows,
        "model_forward_smoke": forward_payload,
        "environment": runtime_environment(device),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the V40 v2 experiment contract without training.")
    parser.add_argument("--root", default=str(project_root_from_script()), type=Path)
    parser.add_argument("--dataset-root", default=str(DEFAULT_DATASET_ROOT), type=Path)
    parser.add_argument("--python", default=str(DEFAULT_PYTHON), type=Path, help="Python path to record in future command templates")
    parser.add_argument("--device", default=LOCKED_DEVICE, help="Device preference for the one-batch model-forward smoke")
    args = parser.parse_args()

    root = args.root.resolve()
    dataset_root = args.dataset_root
    python_path = args.python
    contract_root = root / CONTRACT_REL
    (contract_root / "contract").mkdir(parents=True, exist_ok=True)
    (contract_root / "source_lock").mkdir(parents=True, exist_ok=True)
    (contract_root / "smoke_tests").mkdir(parents=True, exist_ok=True)
    (contract_root / "reports").mkdir(parents=True, exist_ok=True)

    payload = build_contract_payload(root, dataset_root, python_path, args.device)

    write_csv(contract_root / "source_lock" / "input_lock_manifest.csv", payload["source_lock_rows"], ["role", "path", "exists", "bytes", "sha256"])
    payload["status_report"]["source_lock_manifest_sha256"] = sha256_file(contract_root / "source_lock" / "input_lock_manifest.csv")

    write_json(contract_root / "contract" / "v40_experiment_contract.json", payload["contract"])
    write_csv(
        contract_root / "contract" / "v40_run_matrix.csv",
        payload["run_matrix"],
        [
            "run_id",
            "description",
            "model_type",
            "seed",
            "modality_dropout",
            "dropout_label",
            "epochs",
            "img_size",
            "batch_size",
            "lr",
            "num_workers",
            "train_manifest",
            "validation_manifest",
            "out_dir",
            "eligible_for_reliability_selection",
        ],
    )
    write_csv(
        contract_root / "contract" / "v40_training_command_templates.csv",
        payload["command_templates"],
        ["run_id", "train_command_template", "standardized_evaluator_command_template"],
    )
    write_json(contract_root / "contract" / "v40_label_counts.json", payload["label_counts"])
    write_json(contract_root / "contract" / "v40_environment.json", payload["environment"])

    write_json(contract_root / "smoke_tests" / "label_free_config_smoke.json", payload["label_free_smoke"])
    write_csv(contract_root / "smoke_tests" / "label_free_config_smoke.csv", payload["label_free_rows"], ["check", "observed", "expected", "status"])
    write_json(contract_root / "smoke_tests" / "model_forward_smoke.json", payload["model_forward_smoke"])

    write_json(contract_root / "reports" / "V40_EXPERIMENT_CONTRACT_STATUS.json", payload["status_report"])
    write_markdown_outputs(root, payload)
    write_output_manifest(root)

    print(json.dumps({"status": payload["contract"]["status"], "contract_root": str(contract_root)}, indent=2))
    return 0 if payload["contract"]["status"] == "V40_EXPERIMENT_CONTRACT_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
