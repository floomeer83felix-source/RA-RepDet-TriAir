#!/usr/bin/env python
"""Create the immutable source and protocol lock for V48 execution."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import timm
import torch
import torchvision


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v48_complete_ablation"
TRAIN_MANIFEST = (
    "reproducibility/v40_expanded_adjacency_component_split_v2/manifests/"
    "v40_expanded_adjacency_component_disjoint_train.txt"
)
DEVVAL_MANIFEST = (
    "reproducibility/v40_expanded_adjacency_component_split_v2/manifests/"
    "v40_expanded_adjacency_component_disjoint_val.txt"
)
FIXED_CHECKPOINTS = [
    ("matched_early_seed0", "matched_early", "early", 0, 0.00, "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt", "23331a6e668634f5f1ca1c7dfaddd23e9ee5445c0558e325621e8f454a0b1602"),
    ("matched_early_seed1", "matched_early", "early", 1, 0.00, "runs/v41_q1_upgrade/seed1/matched_early_seed1/weights/best.pt", "60a338ed887c15d94d3f274df39684c1dc6de68f9f29ba13f9f9cb4d6fbcd804"),
    ("matched_early_seed2", "matched_early", "early", 2, 0.00, "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed2/weights/best.pt", "b36b4965931da68b77a6be82e85e47b34f952445d64b941337f56a722f62737e"),
    ("reliability_p015_seed0", "ra_full_p015", "reliability", 0, 0.15, "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt", "4284aaa188cb7f065a01b6cf32b78265ab937da0de2d3423d4594d2102787436"),
    ("reliability_p015_seed1", "ra_full_p015", "reliability", 1, 0.15, "runs/v41_q1_upgrade/seed1/reliability_p015_seed1/weights/best.pt", "a59366dd0687754577d23d3e21358127199345d4ebf3a55a06472b933b57813d"),
    ("reliability_p015_seed2", "ra_full_p015", "reliability", 2, 0.15, "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed2/weights/best.pt", "27affa96df1b3baad3df6f0a591e0599c1f5c0f77f91fad9fdaa408e549f1415"),
]
CODE_PATHS = [
    "rarepdet/coco_metrics.py",
    "rarepdet/metrics.py",
    "rarepdet/data.py",
    "rarepdet/train_early_fusion.py",
    "rarepdet/eval_map.py",
    "rarepdet/models/early_fusion_fcos.py",
    "rarepdet/models/repvit_fpn_backbone.py",
    "rarepdet/models/ablation_fusion_fcos.py",
    "rarepdet/tools/eval_coco_map.py",
    "rarepdet/tools/create_v48_source_lock.py",
    "rarepdet/tools/profile_v48_models.py",
    "rarepdet/tools/run_v48_training.py",
    "rarepdet/tools/build_v48_summary.py",
    "rarepdet/tools/scan_v48_claims.py",
    "rarepdet/tools/run_v48_preflight.py",
    "rarepdet/tools/run_v48_queue.py",
    "rarepdet/tools/finalize_v48_task.py",
    "rarepdet/tools/v48_handoff.py",
    "rarepdet/tools/generate_handoff.py",
    "rarepdet/tools/update_project_status.py",
    "tests/test_v48_ablation_fusion.py",
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


def manifest_record(path_text):
    path = PROJECT_ROOT / path_text
    return {
        "path": path_text,
        "rows": len(path.read_text(encoding="utf-8").splitlines()),
        "sha256": sha256(path),
        "normalized_lf_sha256": normalized_lf_sha256(path),
    }


def main():
    branch = git("branch", "--show-current")
    if branch != "research/ra-repdet-triair":
        raise RuntimeError(f"unexpected branch: {branch}")

    manifests = {"train": manifest_record(TRAIN_MANIFEST), "devval": manifest_record(DEVVAL_MANIFEST)}
    fixed_checkpoints = []
    for run_id, variant, model, seed, dropout, path_text, expected_hash in FIXED_CHECKPOINTS:
        path = PROJECT_ROOT / path_text
        observed_hash = sha256(path)
        if observed_hash != expected_hash:
            raise RuntimeError(f"checkpoint hash mismatch for {run_id}: {observed_hash}")
        fixed_checkpoints.append(
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
        "status": "V48_SOURCE_LOCKED_BEFORE_TRAINING",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "git_commit": git("rev-parse", "HEAD"),
        "git_branch": branch,
        "working_tree_clean": not bool(git("status", "--short")),
        "project_profile_note": "PROJECT_PROFILE.md requested by NEXT_TASK.md is absent from the repository root.",
        "manifests": manifests,
        "fixed_checkpoints": fixed_checkpoints,
        "code_sha256": code_hashes,
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
        "evaluation_settings": {
            "protocol": "development-validation only",
            "detector_score_thr": 0.001,
            "metric_score_thr": 0.50,
            "nms_thresh": 0.6,
            "detections_per_img": 100,
            "coco_iou_thresholds": [round(0.50 + 0.05 * index, 2) for index in range(10)],
            "coco_recall_samples": 101,
        },
        "guard_policy": "Locked holdout access is forbidden in V48: it must not be read, evaluated, predicted on, reported for, or used for training, checkpoint selection, architecture selection, seed continuation, or threshold selection.",
        "environment": {
            "platform": platform.platform(),
            "python_executable": sys.executable,
            "python": platform.python_version(),
            "pytorch": torch.__version__,
            "torchvision": torchvision.__version__,
            "timm": timm.__version__,
            "torch_cuda": str(torch.version.cuda),
            "cuda_available": torch.cuda.is_available(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NA",
            "nvidia_smi": gpu_query,
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "source_lock_v48.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# V48 Causal Ablation and Efficiency Source Lock",
        "",
        f"Generated: {lock['generated_at']}",
        "",
        f"Status: `{lock['status']}`",
        "",
        "## Repository",
        "",
        f"- Starting commit: `{lock['git_commit']}`",
        f"- Branch: `{lock['git_branch']}`",
        f"- Working tree clean at lock time: `{lock['working_tree_clean']}`",
        f"- Note: {lock['project_profile_note']}",
        "",
        "## Frozen manifests",
        "",
        "| Role | Path | Rows | SHA256 | Normalized-LF SHA256 |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for role, record in manifests.items():
        lines.append(f"| {role} | `{record['path']}` | {record['rows']} | `{record['sha256']}` | `{record['normalized_lf_sha256']}` |")
    lines.extend(["", "## Inherited fixed checkpoint hashes", "", "| Run | Variant | Model | Seed | SHA256 |", "| --- | --- | --- | ---: | --- |"])
    for record in fixed_checkpoints:
        lines.append(f"| {record['run_id']} | {record['variant']} | {record['model']} | {record['seed']} | `{record['sha256']}` |")
    lines.extend(["", "## Source hashes", ""])
    for path_text, digest in code_hashes.items():
        lines.append(f"- `{path_text}`: `{digest}`")
    lines.extend(
        [
            "",
            "## Protocol",
            "",
            "- All V48 model selection uses development-validation project-local AP50 only.",
            "- Fresh training uses 50 epochs, batch size 4, image size 640, AdamW (lr=1e-4, weight decay=1e-4), and seeds 0/1/2 as applicable.",
            "- COCO-style metrics use `pycocotools.cocoeval.COCOeval` at IoU 0.50:0.05:0.95, 101 recall samples, area=all, and maxDets=100.",
            "",
            "## Locked-holdout boundary",
            "",
            lock["guard_policy"],
            "",
            "## Environment",
            "",
        ]
    )
    lines.extend(f"- {key}: `{value}`" for key, value in lock["environment"].items())
    (OUTPUT_DIR / "source_lock_v48.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": lock["status"], "output_dir": str(OUTPUT_DIR)}, indent=2))


if __name__ == "__main__":
    main()
