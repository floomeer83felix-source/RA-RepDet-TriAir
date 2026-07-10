#!/usr/bin/env python
"""Create the immutable-input record required before V46 execution."""

from datetime import datetime
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v46_coco_ablation"
DATASET_ROOT = Path(r"D:\download\triair")

MANIFESTS = {
    "train": "reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt",
    "devval": "reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt",
    "guard": "runs/component_disjoint_v40/guard.txt",
}

RUNS = [
    ("matched_early_seed0", "matched_early", "early", 0, 0.00, "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt", "23331a6e668634f5f1ca1c7dfaddd23e9ee5445c0558e325621e8f454a0b1602"),
    ("matched_early_seed1", "matched_early", "early", 1, 0.00, "runs/v41_q1_upgrade/seed1/matched_early_seed1/weights/best.pt", "60a338ed887c15d94d3f274df39684c1dc6de68f9f29ba13f9f9cb4d6fbcd804"),
    ("matched_early_seed2", "matched_early", "early", 2, 0.00, "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed2/weights/best.pt", "b36b4965931da68b77a6be82e85e47b34f952445d64b941337f56a722f62737e"),
    ("reliability_p015_seed0", "ra_full_p015", "reliability", 0, 0.15, "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt", "4284aaa188cb7f065a01b6cf32b78265ab937da0de2d3423d4594d2102787436"),
    ("reliability_p015_seed1", "ra_full_p015", "reliability", 1, 0.15, "runs/v41_q1_upgrade/seed1/reliability_p015_seed1/weights/best.pt", "a59366dd0687754577d23d3e21358127199345d4ebf3a55a06472b933b57813d"),
    ("reliability_p015_seed2", "ra_full_p015", "reliability", 2, 0.15, "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed2/weights/best.pt", "27affa96df1b3baad3df6f0a591e0599c1f5c0f77f91fad9fdaa408e549f1415"),
]

CODE_PATHS = [
    "rarepdet/coco_metrics.py",
    "rarepdet/tools/eval_coco_map.py",
    "rarepdet/tools/smoke_test_coco_metrics.py",
    "rarepdet/tools/create_v46_source_lock.py",
    "rarepdet/eval_map.py",
    "rarepdet/metrics.py",
    "rarepdet/train_early_fusion.py",
    "rarepdet/data.py",
    "rarepdet/models/early_fusion_fcos.py",
    "rarepdet/models/repvit_fpn_backbone.py",
    "datasets/triair_dataset.py",
]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_lf_sha256(path):
    content = Path(path).read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=PROJECT_ROOT, text=True).strip()


def version(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "NA"


def relative(path):
    return Path(path).resolve().relative_to(PROJECT_ROOT).as_posix()


def main():
    branch = git("branch", "--show-current")
    if branch != "research/ra-repdet-triair":
        raise RuntimeError(f"unexpected branch: {branch}")

    manifest_records = {}
    for role, path_text in MANIFESTS.items():
        path = PROJECT_ROOT / path_text
        if not path.is_file():
            raise FileNotFoundError(path)
        manifest_records[role] = {
            "path": path_text,
            "rows": len(path.read_text(encoding="utf-8").splitlines()),
            "sha256": sha256(path),
            "normalized_lf_sha256": normalized_lf_sha256(path),
        }

    checkpoint_records = []
    for run_id, variant, model, seed, dropout, path_text, expected_hash in RUNS:
        path = PROJECT_ROOT / path_text
        if not path.is_file():
            raise FileNotFoundError(path)
        observed_hash = sha256(path)
        if observed_hash != expected_hash:
            raise RuntimeError(f"checkpoint hash mismatch for {run_id}: {observed_hash}")
        checkpoint_records.append(
            {
                "run_id": run_id,
                "variant": variant,
                "model": model,
                "seed": seed,
                "modality_dropout": dropout,
                "path": path_text,
                "sha256": observed_hash,
                "bytes": path.stat().st_size,
            }
        )

    code_hashes = {}
    for path_text in CODE_PATHS:
        path = PROJECT_ROOT / path_text
        if not path.is_file():
            raise FileNotFoundError(path)
        code_hashes[path_text] = sha256(path)

    gpu_query = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
        text=True,
    ).strip()
    lock = {
        "status": "V46_SOURCE_LOCKED_BEFORE_EXECUTION",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "git_commit": git("rev-parse", "HEAD"),
        "git_branch": branch,
        "working_tree_clean": not bool(git("status", "--short")),
        "project_profile_note": "PROJECT_PROFILE.md requested by NEXT_TASK.md is absent from the repository root.",
        "dataset_root": str(DATASET_ROOT),
        "dataset_root_exists": DATASET_ROOT.is_dir(),
        "manifests": manifest_records,
        "fixed_checkpoints": checkpoint_records,
        "code_sha256": code_hashes,
        "evaluation_settings": {
            "img_size": 640,
            "device": "cuda",
            "batch_size": 4,
            "num_workers": 0,
            "detector_score_thr": 0.001,
            "metric_score_thr": 0.50,
            "nms_thresh": 0.6,
            "detections_per_img": 100,
            "coco_iou_thresholds": [round(0.50 + 0.05 * index, 2) for index in range(10)],
            "coco_recall_samples": 101,
        },
        "training_settings": {
            "epochs": 50,
            "batch_size": 4,
            "img_size": 640,
            "optimizer": "AdamW",
            "lr": 1e-4,
            "weight_decay": 1e-4,
            "num_workers": 0,
            "checkpoint_selection": "highest development-validation project-local AP50",
        },
        "environment": {
            "platform": platform.platform(),
            "python_executable": sys.executable,
            "python": platform.python_version(),
            "pytorch": torch.__version__,
            "torchvision": version("torchvision"),
            "timm": version("timm"),
            "pycocotools": version("pycocotools"),
            "torch_cuda": str(torch.version.cuda),
            "cuda_available": torch.cuda.is_available(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NA",
            "nvidia_smi": gpu_query,
        },
        "guard_policy": "The locked same-dataset guard is evaluation-only and is not used for training, tuning, threshold selection, dropout selection, checkpoint selection, ablation selection, or run continuation decisions.",
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "source_lock_v46.json"
    md_path = OUTPUT_DIR / "source_lock_v46.md"
    json_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# V46 COCO Metrics and Causal Ablation Source Lock",
        "",
        f"Generated: {lock['generated_at']}",
        "",
        "Status: `V46_SOURCE_LOCKED_BEFORE_EXECUTION`",
        "",
        "## Repository",
        "",
        f"- Commit before V46 reporting commit: `{lock['git_commit']}`",
        f"- Branch: `{branch}`",
        f"- Working tree clean at lock time: `{lock['working_tree_clean']}`",
        f"- Note: {lock['project_profile_note']}",
        "",
        "## Frozen manifests",
        "",
        "| Role | Path | Rows | Raw SHA256 | Normalized-LF SHA256 |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for role, record in manifest_records.items():
        lines.append(
            f"| {role} | `{record['path']}` | {record['rows']} | `{record['sha256']}` | `{record['normalized_lf_sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Six fixed baseline/main checkpoints",
            "",
            "| Run | Variant | Model | Seed | Dropout | Path | SHA256 |",
            "| --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for record in checkpoint_records:
        lines.append(
            f"| {record['run_id']} | {record['variant']} | {record['model']} | {record['seed']} | {record['modality_dropout']:.2f} | `{record['path']}` | `{record['sha256']}` |"
        )
    lines.extend(["", "## Evaluator and training code hashes", ""])
    for path_text, digest in code_hashes.items():
        lines.append(f"- `{path_text}`: `{digest}`")
    lines.extend(
        [
            "",
            "## Fixed conventions",
            "",
            "- COCO bbox AP uses `pycocotools.cocoeval.COCOeval`, IoU 0.50:0.05:0.95, 101 recall samples, area=all, and maxDets=100.",
            "- Detector score threshold is 0.001; the project operating threshold for precision/recall/F1 is 0.50.",
            "- Training uses 50 epochs, batch size 4, image size 640, AdamW at 1e-4 with weight decay 1e-4, and best checkpoint selection by development-validation project-local AP50.",
            "",
            "## Environment",
            "",
        ]
    )
    for key, value in lock["environment"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Guard boundary",
            "",
            lock["guard_policy"],
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"json": relative(json_path), "markdown": relative(md_path), "status": lock["status"]}, indent=2))


if __name__ == "__main__":
    main()
