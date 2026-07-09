from __future__ import annotations

import csv
import hashlib
import json
import statistics
import subprocess
from datetime import datetime
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "runs" / "v42_locked_guard_heldout"
GUARD = REPO / "runs" / "component_disjoint_v40" / "guard.txt"
ARCHIVAL_GUARD = (
    REPO
    / "reproducibility"
    / "v40_expanded_adjacency_component_split_v2"
    / "manifests"
    / "v40_guard_unchanged_archival.txt"
)
SPLIT_MANIFEST = REPO / "runs" / "component_disjoint_v40" / "split_manifest.json"

RUNS = [
    {
        "run_id": "matched_early_seed0",
        "model_group": "matched_early",
        "seed": "0",
        "checkpoint_source": "V40 compute-minimized seed0/2 run set",
    },
    {
        "run_id": "matched_early_seed1",
        "model_group": "matched_early",
        "seed": "1",
        "checkpoint_source": "V41 fresh paired seed1 run set",
    },
    {
        "run_id": "matched_early_seed2",
        "model_group": "matched_early",
        "seed": "2",
        "checkpoint_source": "V40 compute-minimized seed0/2 run set",
    },
    {
        "run_id": "reliability_p015_seed0",
        "model_group": "reliability_p015",
        "seed": "0",
        "checkpoint_source": "V40 compute-minimized seed0/2 run set",
    },
    {
        "run_id": "reliability_p015_seed1",
        "model_group": "reliability_p015",
        "seed": "1",
        "checkpoint_source": "V41 fresh paired seed1 run set",
    },
    {
        "run_id": "reliability_p015_seed2",
        "model_group": "reliability_p015",
        "seed": "2",
        "checkpoint_source": "V40 compute-minimized seed0/2 run set",
    },
]

METRICS = ["precision", "recall", "f1", "ap50", "ap75"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalized_manifest_sha(path: Path) -> str:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def manifest_rows(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def read_eval_csv(run_id: str) -> dict[str, str]:
    path = OUT_DIR / run_id / "standardized_guard_eval" / "eval_results.csv"
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1:
        raise RuntimeError(f"Expected exactly one row in {path}, got {len(rows)}")
    return rows[0]


def f(value: str) -> float:
    return float(value)


def mean(values: list[float]) -> float:
    return statistics.mean(values)


def sample_sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float) -> str:
    return f"{value:.6f}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().isoformat(timespec="seconds")
    split_manifest = json.loads(SPLIT_MANIFEST.read_text(encoding="utf-8"))

    per_run = []
    for spec in RUNS:
        row = read_eval_csv(spec["run_id"])
        merged = {
            **spec,
            "model": row["model"],
            "images": int(row["images"]),
            "gt_boxes": int(row["gt_boxes"]),
            "predictions": int(row["predictions"]),
            "precision": f(row["precision"]),
            "recall": f(row["recall"]),
            "f1": f(row["f1"]),
            "ap50": f(row["ap50"]),
            "ap75": f(row["ap75"]),
            "mean_confidence": f(row["mean_confidence"]),
            "runtime_seconds": f(row["runtime_seconds"]),
            "fps": f(row["fps"]),
            "weights": row["weights"],
            "checkpoint_sha256": row["checkpoint_sha256"],
            "eval_results_csv": str(
                OUT_DIR / spec["run_id"] / "standardized_guard_eval" / "eval_results.csv"
            ),
            "eval_results_txt": str(
                OUT_DIR / spec["run_id"] / "standardized_guard_eval" / "eval_results.txt"
            ),
            "eval_command": str(
                OUT_DIR / spec["run_id"] / "standardized_guard_eval" / "eval_command.txt"
            ),
            "detector_score_thr": f(row["detector_score_thr"]),
            "metric_score_thr": f(row["metric_score_thr"]),
            "nms_thresh": f(row["nms_thresh"]),
            "detections_per_img": int(row["detections_per_img"]),
            "split_file": row["split_file"],
            "split_sha256_raw_file": row["split_sha256"],
            "git_commit_recorded_by_eval": row["git_commit"],
            "env_python": row["env_python"],
            "env_pytorch": row["env_pytorch"],
            "env_torchvision": row["env_torchvision"],
            "env_timm": row["env_timm"],
            "env_torch_cuda": row["env_torch_cuda"],
            "env_cuda_available": row["env_cuda_available"],
            "env_gpu": row["env_gpu"],
            "env_device": row["env_device"],
        }
        per_run.append(merged)

    by_group = {
        group: [r for r in per_run if r["model_group"] == group]
        for group in ["matched_early", "reliability_p015"]
    }
    aggregates = []
    for group, rows in by_group.items():
        for metric in METRICS:
            vals = [r[metric] for r in rows]
            aggregates.append(
                {
                    "model_group": group,
                    "metric": metric,
                    "mean": mean(vals),
                    "sample_sd": sample_sd(vals),
                    "min": min(vals),
                    "max": max(vals),
                    "n": len(vals),
                }
            )

    paired = []
    for seed in ["0", "1", "2"]:
        early = next(r for r in per_run if r["model_group"] == "matched_early" and r["seed"] == seed)
        reliability = next(
            r for r in per_run if r["model_group"] == "reliability_p015" and r["seed"] == seed
        )
        row = {"seed": seed}
        for metric in METRICS:
            row[metric] = reliability[metric] - early[metric]
        paired.append(row)

    paired_aggregate = []
    for metric in METRICS:
        vals = [r[metric] for r in paired]
        paired_aggregate.append(
            {
                "comparison": "reliability_p015_minus_matched_early",
                "metric": metric,
                "mean_delta": mean(vals),
                "sample_sd": sample_sd(vals),
                "min_delta": min(vals),
                "max_delta": max(vals),
                "n_seed_pairs": len(vals),
            }
        )

    raw_guard_sha = sha256_file(GUARD)
    norm_guard_sha = normalized_manifest_sha(GUARD)
    archival_raw_sha = sha256_file(ARCHIVAL_GUARD)
    archival_norm_sha = normalized_manifest_sha(ARCHIVAL_GUARD)
    current_commit = git_output("rev-parse", "HEAD")
    branch = git_output("branch", "--show-current")

    source_lock = {
        "status": "V42_LOCKED_HELDOUT_GUARD_EVALUATION_COMPLETE",
        "generated_at": generated_at,
        "git_branch": branch,
        "git_commit": current_commit,
        "dataset_root": "D:\\download\\triair",
        "heldout_guard_source": {
            "path": str(GUARD),
            "rows": manifest_rows(GUARD),
            "raw_file_sha256": raw_guard_sha,
            "normalized_lf_sha256": norm_guard_sha,
            "split_manifest_path": str(SPLIT_MANIFEST),
            "split_manifest_declared_normalized_guard_sha256": split_manifest["split_sha256"]["guard"],
            "component_count": split_manifest["component_count"],
            "guard_distance": split_manifest["guard_distance"],
            "inventory_count": split_manifest["inventory_count"],
            "deterministic_rerun_consistency": split_manifest["deterministic_rerun_consistency"],
        },
        "non_source_guard_note": {
            "path": str(ARCHIVAL_GUARD),
            "rows": manifest_rows(ARCHIVAL_GUARD),
            "raw_file_sha256": archival_raw_sha,
            "normalized_lf_sha256": archival_norm_sha,
            "used_for_v42_eval": False,
            "reason": "Different content from runs/component_disjoint_v40/guard.txt; the latter matches the frozen split_manifest guard hash.",
        },
        "evaluator": {
            "path": str(REPO / "rarepdet" / "eval_map.py"),
            "sha256": sha256_file(REPO / "rarepdet" / "eval_map.py"),
            "metrics_path": str(REPO / "rarepdet" / "metrics.py"),
            "metrics_sha256": sha256_file(REPO / "rarepdet" / "metrics.py"),
        },
        "fixed_eval_settings": {
            "img_size": 640,
            "device": "cuda",
            "batch_size": 4,
            "num_workers": 0,
            "detector_score_thr": 0.001,
            "metric_score_thr": 0.50,
            "nms_thresh": 0.6,
            "detections_per_img": 100,
        },
        "per_run": per_run,
    }

    summary = {
        "status": source_lock["status"],
        "generated_at": generated_at,
        "guard_rows": manifest_rows(GUARD),
        "guard_gt_boxes": per_run[0]["gt_boxes"],
        "guard_normalized_lf_sha256": norm_guard_sha,
        "guard_raw_file_sha256": raw_guard_sha,
        "per_run": per_run,
        "aggregates": aggregates,
        "paired_deltas": paired,
        "paired_delta_aggregates": paired_aggregate,
        "claim_boundary": {
            "allowed": [
                "Locked held-out guard evaluation on the frozen V40 component-disjoint guard manifest.",
                "Three fixed checkpoint pairs: seed0, seed1, and seed2.",
                "Descriptive paired comparison of reliability-aware p=0.15 minus matched early fusion.",
            ],
            "disallowed": [
                "External dataset generalization.",
                "Independent public benchmark test.",
                "Training-time model selection or tuning using guard results.",
                "Statistical significance.",
                "Optimal dropout or calibrated physical sensor reliability.",
                "COCO AP@[0.50:0.95].",
            ],
        },
    }

    write_csv(
        OUT_DIR / "heldout_guard_per_run_summary.csv",
        per_run,
        [
            "run_id",
            "model_group",
            "model",
            "seed",
            "checkpoint_source",
            "precision",
            "recall",
            "f1",
            "ap50",
            "ap75",
            "images",
            "gt_boxes",
            "predictions",
            "checkpoint_sha256",
            "weights",
        ],
    )
    write_csv(OUT_DIR / "heldout_guard_paired_deltas.csv", paired, ["seed", *METRICS])
    write_csv(
        OUT_DIR / "heldout_guard_paired_delta_aggregates.csv",
        paired_aggregate,
        ["comparison", "metric", "mean_delta", "sample_sd", "min_delta", "max_delta", "n_seed_pairs"],
    )

    (OUT_DIR / "heldout_guard_source_lock.json").write_text(
        json.dumps(source_lock, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "heldout_guard_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    source_lock_md = [
        "# V42 Locked Held-out Guard Source Lock",
        "",
        f"Generated: {generated_at}",
        "",
        "## Scope",
        "",
        "This record freezes the sources used for the V42 held-out guard evaluation. No training, checkpoint selection, hyperparameter tuning, split modification, robustness run, profiling run, manuscript edit, or external-data task was performed.",
        "",
        "## Held-out guard source",
        "",
        f"- Source manifest: `{GUARD.relative_to(REPO)}`",
        f"- Rows: {manifest_rows(GUARD)}",
        f"- Raw file SHA256: `{raw_guard_sha}`",
        f"- Normalized LF SHA256: `{norm_guard_sha}`",
        f"- Split-manifest declared guard SHA256: `{split_manifest['split_sha256']['guard']}`",
        f"- Components: {split_manifest['component_count']}",
        f"- Guard distance: {split_manifest['guard_distance']}",
        f"- Inventory count: {split_manifest['inventory_count']}",
        f"- Deterministic rerun consistency: {split_manifest['deterministic_rerun_consistency']}",
        "",
        "## Non-source archival guard note",
        "",
        f"- Not used: `{ARCHIVAL_GUARD.relative_to(REPO)}`",
        f"- Rows: {manifest_rows(ARCHIVAL_GUARD)}",
        f"- Raw file SHA256: `{archival_raw_sha}`",
        f"- Normalized LF SHA256: `{archival_norm_sha}`",
        "- Reason: this file has different content from the V42 source manifest; V42 uses the guard file matching `runs/component_disjoint_v40/split_manifest.json`.",
        "",
        "## Evaluator",
        "",
        f"- Evaluator: `rarepdet/eval_map.py` `{source_lock['evaluator']['sha256']}`",
        f"- Metrics: `rarepdet/metrics.py` `{source_lock['evaluator']['metrics_sha256']}`",
        f"- Branch: `{branch}`",
        f"- Commit at evaluation/reporting: `{current_commit}`",
        "",
        "## Fixed checkpoints",
        "",
        "| Run | Model | Seed | Checkpoint SHA256 | Source |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in per_run:
        source_lock_md.append(
            f"| {row['run_id']} | {row['model']} | {row['seed']} | `{row['checkpoint_sha256']}` | {row['checkpoint_source']} |"
        )
    source_lock_md += [
        "",
        "## Fixed evaluation settings",
        "",
        "- `img_size=640`, `device=cuda`, `batch_size=4`, `num_workers=0`.",
        "- `detector_score_thr=0.001`, `metric_score_thr=0.50`, `nms_thresh=0.6`, `detections_per_img=100`.",
    ]
    (OUT_DIR / "heldout_guard_source_lock.md").write_text(
        "\n".join(source_lock_md) + "\n", encoding="utf-8"
    )

    summary_md = [
        "# V42 Locked Held-out Guard Evaluation Summary",
        "",
        f"Generated: {generated_at}",
        "",
        "## Evaluation source",
        "",
        f"- Guard manifest: `{GUARD.relative_to(REPO)}`",
        f"- Guard rows: {manifest_rows(GUARD)} images",
        f"- Guard GT boxes: {per_run[0]['gt_boxes']}",
        f"- Normalized guard SHA256: `{norm_guard_sha}`",
        f"- Raw file SHA256 recorded by evaluator: `{raw_guard_sha}`",
        "",
        "## Per-run results",
        "",
        "| Run | Precision | Recall | F1 | AP50 | AP75 | Predictions |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in per_run:
        summary_md.append(
            f"| {row['run_id']} | {fmt(row['precision'])} | {fmt(row['recall'])} | {fmt(row['f1'])} | {fmt(row['ap50'])} | {fmt(row['ap75'])} | {row['predictions']} |"
        )
    summary_md += [
        "",
        "## Group descriptive aggregates",
        "",
        "| Model group | Metric | Mean | Sample SD | Min | Max | n |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in aggregates:
        summary_md.append(
            f"| {row['model_group']} | {row['metric']} | {fmt(row['mean'])} | {fmt(row['sample_sd'])} | {fmt(row['min'])} | {fmt(row['max'])} | {row['n']} |"
        )
    summary_md += [
        "",
        "## Paired deltas",
        "",
        "Reliability-aware p=0.15 minus matched early fusion, paired by seed.",
        "",
        "| Seed | Precision | Recall | F1 | AP50 | AP75 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in paired:
        summary_md.append(
            f"| {row['seed']} | {fmt(row['precision'])} | {fmt(row['recall'])} | {fmt(row['f1'])} | {fmt(row['ap50'])} | {fmt(row['ap75'])} |"
        )
    summary_md += [
        "",
        "| Metric | Mean delta | Sample SD | Min | Max | n seed pairs |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in paired_aggregate:
        summary_md.append(
            f"| {row['metric']} | {fmt(row['mean_delta'])} | {fmt(row['sample_sd'])} | {fmt(row['min_delta'])} | {fmt(row['max_delta'])} | {row['n_seed_pairs']} |"
        )
    summary_md += [
        "",
        "## Interpretation",
        "",
        "On this locked held-out guard manifest, reliability-aware p=0.15 improves the three-seed mean recall, F1, AP50, and AP75 relative to matched early fusion. The per-seed deltas remain mixed for F1 and AP75, including a seed0 F1 decrease and a seed2 AP75 decrease, so the result should be treated as descriptive guard evidence only and was not used for training or tuning.",
    ]
    (OUT_DIR / "heldout_guard_summary.md").write_text(
        "\n".join(summary_md) + "\n", encoding="utf-8"
    )

    boundary_md = [
        "# V42 Held-out Guard Claim Boundary",
        "",
        "## Allowed claims",
        "",
        "- Locked held-out guard evaluation on `runs/component_disjoint_v40/guard.txt`.",
        "- Three fixed seed pairs: matched early fusion vs reliability-aware p=0.15 for seed0, seed1, and seed2.",
        "- Descriptive AP50/AP75/F1/precision/recall comparisons under the project-local evaluator and fixed operating threshold.",
        "- The guard manifest was not used to train, tune, select checkpoints, sweep dropout, profile, or edit manuscript claims during this task.",
        "",
        "## Required cautions",
        "",
        "- This is a held-out TriAir guard partition from the same project dataset, not an external dataset.",
        "- The result is descriptive with n=3 seed pairs; do not state statistical significance.",
        "- Do not claim optimal dropout, calibrated physical sensor reliability, robustness to real sensor faults, or COCO AP@[0.50:0.95].",
        "- Do not use the guard results for future model selection unless the guard is explicitly reclassified and the claim boundary is rewritten.",
        "",
        "## Recommended wording",
        "",
        "A locked held-out guard evaluation on the frozen V40 component-disjoint guard manifest showed descriptive mean AP50/AP75/F1 gains for reliability-aware p=0.15 over matched early fusion across three fixed seed pairs, with mixed per-seed F1 and AP75 deltas. These results remain within-dataset held-out evidence and should not be described as external generalization or statistical proof.",
    ]
    (OUT_DIR / "heldout_guard_claim_boundary.md").write_text(
        "\n".join(boundary_md) + "\n", encoding="utf-8"
    )

    print(OUT_DIR / "heldout_guard_summary.md")
    print(OUT_DIR / "heldout_guard_source_lock.md")
    print(OUT_DIR / "heldout_guard_claim_boundary.md")


if __name__ == "__main__":
    main()
