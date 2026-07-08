#!/usr/bin/env python
"""Build V41 seed1 development-validation reports from completed fixed runs."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs" / "v41_q1_upgrade" / "seed1"
TRAIN_MANIFEST = ROOT / "reproducibility" / "v40_expanded_adjacency_component_split_v2" / "manifests" / "v40_expanded_adjacency_component_disjoint_train.txt"
VAL_MANIFEST = ROOT / "reproducibility" / "v40_expanded_adjacency_component_split_v2" / "manifests" / "v40_expanded_adjacency_component_disjoint_val.txt"
V40_CONFIGS = {
    "early": ROOT / "runs" / "v40_expanded_adjacency_v2_compute_minimized" / "matched_early_seed0" / "config.json",
    "reliability": ROOT / "runs" / "v40_expanded_adjacency_v2_compute_minimized" / "reliability_p015_seed0" / "config.json",
}
RUNS = [
    {
        "run_id": "matched_early_seed1",
        "model_group": "matched_early",
        "model": "early",
        "modality_dropout": "0.00",
    },
    {
        "run_id": "reliability_p015_seed1",
        "model_group": "reliability_p015",
        "model": "reliability",
        "modality_dropout": "0.15",
    },
]
HASH_FILES = [
    "rarepdet/train_early_fusion.py",
    "rarepdet/eval_map.py",
    "rarepdet/metrics.py",
    "rarepdet/data.py",
    "datasets/triair_dataset.py",
    "rarepdet/models/early_fusion_fcos.py",
    "rarepdet/models/repvit_fpn_backbone.py",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def read_eval_csv(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1:
        raise RuntimeError(f"Expected exactly one row in {path}, got {len(rows)}")
    return rows[0]


def parse_training_log(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(
        r"epoch (?P<epoch>\d+) validation Precision=(?P<precision>[0-9.]+) "
        r"Recall=(?P<recall>[0-9.]+) AP50=(?P<ap50>[0-9.]+) AP75=(?P<ap75>[0-9.]+)"
    )
    rows = []
    for match in pattern.finditer(text):
        row = match.groupdict()
        row["epoch"] = int(row["epoch"])
        for key in ["precision", "recall", "ap50", "ap75"]:
            row[key] = float(row[key])
        rows.append(row)
    if not rows:
        raise RuntimeError(f"No validation rows found in {path}")
    best = max(rows, key=lambda r: (r["ap50"], r["ap75"]))
    final = rows[-1]
    return {
        "validation_epochs": len(rows),
        "complete": "Training complete." in text and final["epoch"] == 50,
        "best_epoch_by_train_val_ap50": best,
        "final_epoch": final,
    }


def fmt_float(value: str | float) -> str:
    return f"{float(value):.6f}"


def make_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def load_v40_template(model: str) -> str:
    path = V40_CONFIGS[model]
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["standardized_evaluator_command_template"]


def adapted_eval_command(model: str, run_id: str) -> str:
    template = load_v40_template(model)
    if model == "early":
        return (
            template.replace(
                "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt",
                f"runs/v41_q1_upgrade/seed1/{run_id}/weights/best.pt",
            )
            .replace(
                "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/standardized_eval/eval_results.txt",
                f"runs/v41_q1_upgrade/seed1/{run_id}/standardized_eval/eval_results.txt",
            )
        )
    return (
        template.replace(
            "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt",
            f"runs/v41_q1_upgrade/seed1/{run_id}/weights/best.pt",
        )
        .replace(
            "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/standardized_eval/eval_results.txt",
            f"runs/v41_q1_upgrade/seed1/{run_id}/standardized_eval/eval_results.txt",
        )
    )


def main() -> None:
    generated_at = datetime.now().isoformat(timespec="seconds")
    commit = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    contract_path = OUT / "contract" / "contract_verification.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))

    per_run = []
    for run in RUNS:
        run_dir = OUT / run["run_id"]
        eval_row = read_eval_csv(run_dir / "standardized_eval" / "eval_results.csv")
        train_status = parse_training_log(run_dir / "train_log.txt")
        best_pt = run_dir / "weights" / "best.pt"
        last_pt = run_dir / "weights" / "last.pt"
        row = {
            **run,
            "seed": "1",
            "train_complete": train_status["complete"],
            "validation_epochs": train_status["validation_epochs"],
            "best_epoch_by_train_val_ap50": train_status["best_epoch_by_train_val_ap50"]["epoch"],
            "final_epoch": train_status["final_epoch"]["epoch"],
            "best_checkpoint_sha256": sha256(best_pt),
            "last_checkpoint_sha256": sha256(last_pt),
            "train_command": (
                "python rarepdet/train_early_fusion.py "
                f"--model {run['model']} --data D:\\download\\triair "
                "--train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt "
                "--val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt "
                f"--epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 "
                f"--modality-dropout {run['modality_dropout']} --seed 1 --out runs/v41_q1_upgrade/seed1/{run['run_id']}"
            ),
            "eval_command": adapted_eval_command(run["model"], run["run_id"]),
            **eval_row,
        }
        per_run.append(row)

    early = next(r for r in per_run if r["model"] == "early")
    reliability = next(r for r in per_run if r["model"] == "reliability")
    diffs = {
        metric: float(reliability[metric]) - float(early[metric])
        for metric in ["precision", "recall", "f1", "ap50", "ap75"]
    }

    commands_md = [
        "# V41 Seed1 Frozen Evaluation Command",
        "",
        f"Generated: {generated_at}",
        "",
        "The V40 standardized evaluator command templates were recovered verbatim from:",
        "",
        "- `runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/config.json`",
        "- `runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/config.json`",
        "",
        "## V40 Verbatim Templates",
        "",
    ]
    for run in RUNS:
        commands_md.extend([
            f"### {run['model']}",
            "",
            "```powershell",
            load_v40_template(run["model"]),
            "```",
            "",
        ])
    commands_md.extend([
        "## V41 Seed1 Executed Commands",
        "",
    ])
    for row in per_run:
        commands_md.extend([
            f"### {row['run_id']}",
            "",
            "```powershell",
            row["eval_command"],
            "```",
            "",
        ])
    commands_md.extend([
        "## Verified Fixed Convention",
        "",
        "- Development-validation split only: V40 component-disjoint validation manifest.",
        "- Detector candidate threshold: `0.001`.",
        "- Precision/recall/F1 metric threshold: `0.50`.",
        "- NMS threshold: `0.6`.",
        "- Maximum detections per image: `100`.",
        "- Project-local AP50/AP75 via `rarepdet/eval_map.py`; no COCO, guard, channel-removal, degradation, efficiency, qualitative, gate, or aggregate analysis.",
        "",
    ])
    (OUT / "frozen_evaluation_command.md").write_text("\n".join(commands_md), encoding="utf-8")

    summary_fields = [
        "run_id",
        "model_group",
        "model",
        "seed",
        "modality_dropout",
        "train_complete",
        "validation_epochs",
        "best_epoch_by_train_val_ap50",
        "precision",
        "recall",
        "f1",
        "ap50",
        "ap75",
        "gt_boxes",
        "predictions",
        "mean_confidence",
        "fps",
        "detector_score_thr",
        "metric_score_thr",
        "nms_thresh",
        "detections_per_img",
        "checkpoint_sha256",
        "best_checkpoint_sha256",
        "split_sha256",
    ]
    with (OUT / "seed1_per_run_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields, extrasaction="ignore")
        writer.writeheader()
        for row in per_run:
            writer.writerow(row)

    md_rows = []
    for row in per_run:
        md_rows.append([
            row["run_id"],
            row["model"],
            row["modality_dropout"],
            row["seed"],
            str(row["best_epoch_by_train_val_ap50"]),
            fmt_float(row["precision"]),
            fmt_float(row["recall"]),
            fmt_float(row["f1"]),
            fmt_float(row["ap50"]),
            fmt_float(row["ap75"]),
            row["best_checkpoint_sha256"],
        ])
    summary_md = [
        "# V41 Fresh Paired Seed1 Development-Validation Summary",
        "",
        f"Generated: {generated_at}",
        "",
        make_markdown_table(
            [
                "Run",
                "Model",
                "Dropout",
                "Seed",
                "Best epoch by train-val AP50",
                "Precision",
                "Recall",
                "F1",
                "AP50",
                "AP75",
                "Best checkpoint SHA256",
            ],
            md_rows,
        ),
        "",
        "Both rows are fresh seed1 trainings from this task and were evaluated once on the frozen V40 development-validation manifest.",
        "",
    ]
    (OUT / "seed1_per_run_summary.md").write_text("\n".join(summary_md), encoding="utf-8")

    pair_md = [
        "# V41 Seed1 Paired Comparison",
        "",
        f"Generated: {generated_at}",
        "",
        "Comparison: reliability-aware p=0.15 seed1 minus matched early-fusion seed1 on the same frozen V40 development-validation split.",
        "",
        make_markdown_table(
            ["Metric", "Early", "Reliability p=0.15", "Delta"],
            [
                [metric.upper() if metric.startswith("ap") else metric.capitalize(), fmt_float(early[metric]), fmt_float(reliability[metric]), f"{diffs[metric]:+.6f}"]
                for metric in ["precision", "recall", "f1", "ap50", "ap75"]
            ],
        ),
        "",
        "Decision note: This is paired development-validation evidence only, not an independent-test, stability, significance, or manuscript-final claim.",
        "",
        "Protocol note: one earlier reliability seed1 process terminated before completion and was archived locally under `runs/v41_q1_upgrade/seed1/reliability_p015_seed1_incomplete_attempt1_20260708`; its checkpoint and metrics were not used.",
        "",
    ]
    (OUT / "seed1_pair_comparison.md").write_text("\n".join(pair_md), encoding="utf-8")

    source_hashes = {path: sha256(ROOT / path) for path in HASH_FILES}
    source_lock = {
        "status": "V41_SEED1_FRESH_PAIRED_DEVVAL_COMPLETE",
        "generated_at": generated_at,
        "git_branch": branch,
        "git_commit_before_report_commit": commit,
        "dataset_root": "D:\\download\\triair",
        "train_manifest": str(TRAIN_MANIFEST),
        "train_manifest_sha256": sha256(TRAIN_MANIFEST),
        "val_manifest": str(VAL_MANIFEST),
        "val_manifest_sha256": sha256(VAL_MANIFEST),
        "contract_verification": str(contract_path),
        "contract_status": contract["status"],
        "contract_environment": contract["environment"],
        "source_hashes": source_hashes,
        "runs": per_run,
        "paired_differences_reliability_minus_early": diffs,
        "guard_access": "not read, inspected, audited, evaluated, copied, or included",
        "out_of_scope_not_run": [
            "p=0.00 seed1 reliability",
            "p=0.20 seed1 reliability",
            "channel removal",
            "COCO",
            "degradation",
            "efficiency",
            "qualitative",
            "gate",
            "aggregate analysis",
            "manuscript update",
        ],
        "incomplete_attempt_note": "One reliability p=0.15 seed1 process terminated before completion and was archived locally; no metrics or checkpoint from that incomplete attempt were used.",
    }
    (OUT / "source_lock_seed1.json").write_text(json.dumps(source_lock, indent=2), encoding="utf-8")

    source_md = [
        "# V41 Seed1 Source Lock",
        "",
        f"Generated: {generated_at}",
        "",
        f"- Status: `{source_lock['status']}`",
        f"- Git branch: `{branch}`",
        f"- Git commit before report commit: `{commit}`",
        f"- Contract verification: `{contract['status']}`",
        f"- Train manifest SHA256: `{source_lock['train_manifest_sha256']}`",
        f"- Development-validation manifest SHA256: `{source_lock['val_manifest_sha256']}`",
        "- Guard partition: not accessed or evaluated.",
        "",
        "## Source Hashes",
        "",
        make_markdown_table(["Path", "SHA256"], [[k, v] for k, v in source_hashes.items()]),
        "",
        "## Checkpoints",
        "",
        make_markdown_table(
            ["Run", "Best checkpoint SHA256", "Last checkpoint SHA256"],
            [[r["run_id"], r["best_checkpoint_sha256"], r["last_checkpoint_sha256"]] for r in per_run],
        ),
        "",
        "## Commands",
        "",
    ]
    for row in per_run:
        source_md.extend([
            f"### {row['run_id']} training",
            "",
            "```powershell",
            row["train_command"],
            "```",
            "",
            f"### {row['run_id']} evaluation",
            "",
            "```powershell",
            row["eval_command"],
            "```",
            "",
        ])
    (OUT / "source_lock_seed1.md").write_text("\n".join(source_md), encoding="utf-8")

    status_block = [
        "\n## V41 fresh paired seed1 development-validation outputs",
        "",
        f"- Generated: {generated_at}",
        "- Status: COMPLETE.",
        "- Scope: exactly two fresh seed1 trainings on the frozen V40 train/development-validation split.",
        "- Guard/non-test partition: not accessed, inspected, copied, or evaluated.",
        f"- Contract verification: `runs/v41_q1_upgrade/seed1/contract/contract_verification.md` ({contract['status']}).",
        f"- Frozen train/val manifest SHA256: `{source_lock['train_manifest_sha256']}` / `{source_lock['val_manifest_sha256']}`.",
        "- Standardized evaluation: detector threshold 0.001, P/R/F1 threshold 0.50, NMS 0.6, max detections/image 100, project-local AP50/AP75.",
        "",
        make_markdown_table(
            ["Run", "Precision", "Recall", "F1", "AP50", "AP75", "Checkpoint SHA256"],
            [
                [r["run_id"], fmt_float(r["precision"]), fmt_float(r["recall"]), fmt_float(r["f1"]), fmt_float(r["ap50"]), fmt_float(r["ap75"]), r["best_checkpoint_sha256"]]
                for r in per_run
            ],
        ),
        "",
        make_markdown_table(
            ["Delta reliability p=0.15 - early", "Value"],
            [[metric, f"{value:+.6f}"] for metric, value in diffs.items()],
        ),
        "",
        "- Required reports: `runs/v41_q1_upgrade/seed1/frozen_evaluation_command.md`, `seed1_per_run_summary.csv/md`, `seed1_pair_comparison.md`, and `source_lock_seed1.md/json`.",
        "- Note: this is development-validation evidence only, not a manuscript-final or independent-test claim.",
        "",
    ]
    status_path = ROOT / "docs" / "EXPERIMENT_STATUS.md"
    status_text = status_path.read_text(encoding="utf-8", errors="replace")
    marker = "\n## V41 fresh paired seed1 development-validation outputs"
    if marker in status_text:
        status_text = status_text[: status_text.index(marker)].rstrip() + "\n"
    status_path.write_text(status_text.rstrip() + "\n" + "\n".join(status_block), encoding="utf-8")

    handoff_path = ROOT / "runs" / "handoff_latest.md"
    handoff_text = handoff_path.read_text(encoding="utf-8", errors="replace")
    if marker in handoff_text:
        handoff_text = handoff_text[: handoff_text.index(marker)].rstrip() + "\n"
    handoff_path.write_text(handoff_text.rstrip() + "\n" + "\n".join(status_block), encoding="utf-8")

    handoff_json_path = ROOT / "runs" / "handoff_latest.json"
    handoff = json.loads(handoff_json_path.read_text(encoding="utf-8"))
    handoff["generated_at"] = generated_at
    handoff["current_task"] = {
        "task_file": "docs/NEXT_TASK.md",
        "current_task": "Fresh paired seed1 training and V40 development-validation evaluation.",
        "status": "complete",
        "commit_message": "v41: add fresh paired seed1 development validation evidence",
    }
    handoff["v41_seed1"] = source_lock
    handoff["current_pending_experiments"] = [
        "V41 fresh paired seed1 development-validation training/evaluation is complete.",
        "Do not treat V41 seed1 development-validation evidence as independent-test or manuscript-final evidence without explicit later approval.",
        "Do not commit raw data, checkpoints, weights, prediction dumps, or visual artifacts.",
    ]
    handoff_json_path.write_text(json.dumps(handoff, indent=2), encoding="utf-8")

    print("Wrote V41 seed1 report packet")


if __name__ == "__main__":
    main()
