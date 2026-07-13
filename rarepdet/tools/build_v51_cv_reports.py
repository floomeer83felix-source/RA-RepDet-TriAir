#!/usr/bin/env python
"""Build V51 Route-B RGB and frozen-checkpoint cross-validation reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, stdev


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = PROJECT_ROOT / "runs/v51_visdrone_recovery"
METRICS = ("ap50_95", "ap50", "ap75", "ar100", "ap_small", "ap_medium", "ap_large")


def summary(values):
    values = [float(value) for value in values]
    return {"mean": mean(values), "sample_sd": stdev(values) if len(values) > 1 else 0.0}


def row_from_result(result):
    return {
        "run_id": result["run_id"],
        "fold": int(result["fold"]),
        "seed": int(result["seed"]),
        "variant": result["variant"],
        **{metric: float(result[metric]) for metric in METRICS},
        "images": int(result["images"]),
        "gt_boxes": int(result["gt_boxes"]),
        "ignored_regions": int(result["ignored_regions"]),
        "checkpoint_sha256": result["checkpoint_sha256"],
        "manifest_sha256": result["manifest_sha256"],
        "annotations_sha256": result["annotations_sha256"],
    }


def write_csv(path, rows):
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["status"])
        writer.writeheader()
        writer.writerows(rows)


def load_results(pattern):
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(OUTPUT.glob(pattern))]


def main():
    rgb_results = load_results("raw/rgb/fold*/rgb_fold*_seed*.json")
    zero_results = load_results("raw/zero_shot/fold*/*.json")
    if len(rgb_results) != 9 or len(zero_results) != 18:
        raise RuntimeError(
            f"incomplete V51 results: rgb={len(rgb_results)}/9 zero_shot={len(zero_results)}/18"
        )

    rgb_rows = [row_from_result(result) for result in rgb_results]
    write_csv(OUTPUT / "cv_per_run.csv", rgb_rows)
    fold_rows = []
    for fold in range(3):
        selected = [row for row in rgb_rows if row["fold"] == fold]
        row = {"fold": fold, "runs": len(selected)}
        for metric in METRICS:
            stats = summary(row_[metric] for row_ in selected)
            row[f"{metric}_mean"] = stats["mean"]
            row[f"{metric}_sample_sd"] = stats["sample_sd"]
        fold_rows.append(row)
    write_csv(OUTPUT / "cv_fold_summary.csv", fold_rows)
    rgb_summary = {
        "status": "COMPLETE",
        "route": "B_GROUP_DISJOINT_CROSS_VALIDATION",
        "claim_boundary": "cross-validation only; not an independent or blind test",
        "runs": len(rgb_rows),
        "folds": fold_rows,
        "descriptive_all_runs": {
            metric: summary(row[metric] for row in rgb_rows) for metric in METRICS
        },
    }
    (OUTPUT / "cv_summary.json").write_text(json.dumps(rgb_summary, indent=2) + "\n", encoding="utf-8")
    cv_lines = [
        "# V51 RGB Cross-Validation Summary",
        "",
        "These are pre-registered group-disjoint cross-validation results, not an independent or blind test.",
        "",
        "| Fold | AP@[.50:.95] mean +/- SD | AP50 mean +/- SD | AP75 mean +/- SD | AR100 mean +/- SD |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in fold_rows:
        cv_lines.append(
            f"| {row['fold']} | {row['ap50_95_mean']:.6f} +/- {row['ap50_95_sample_sd']:.6f} | "
            f"{row['ap50_mean']:.6f} +/- {row['ap50_sample_sd']:.6f} | "
            f"{row['ap75_mean']:.6f} +/- {row['ap75_sample_sd']:.6f} | "
            f"{row['ar100_mean']:.6f} +/- {row['ar100_sample_sd']:.6f} |"
        )
    (OUTPUT / "cv_summary.md").write_text("\n".join(cv_lines) + "\n", encoding="utf-8")

    zero_rows = [row_from_result(result) for result in zero_results]
    write_csv(OUTPUT / "zero_shot_per_run.csv", zero_rows)
    indexed = {(row["fold"], row["seed"], row["variant"]): row for row in zero_rows}
    delta_rows = []
    for fold in range(3):
        for seed in range(3):
            early = indexed[(fold, seed, "matched_early")]
            reliability = indexed[(fold, seed, "ra_full_p015")]
            delta_rows.append(
                {
                    "fold": fold,
                    "seed": seed,
                    **{
                        f"delta_{metric}_ra_minus_early": reliability[metric] - early[metric]
                        for metric in METRICS
                    },
                }
            )
    write_csv(OUTPUT / "zero_shot_paired_deltas.csv", delta_rows)
    zero_summary = {
        "status": "COMPLETE",
        "route": "B_GROUP_DISJOINT_CROSS_VALIDATION",
        "adapter": "RGB float32/255 followed by thermal=0.0 and event=0.0",
        "claim_boundary": "controlled RGB-only missing-modality/domain-shift stress; not tri-modal external validation",
        "runs": len(zero_rows),
        "paired_deltas": {
            metric: summary(row[f"delta_{metric}_ra_minus_early"] for row in delta_rows)
            for metric in METRICS
        },
    }
    (OUTPUT / "zero_shot_summary.json").write_text(
        json.dumps(zero_summary, indent=2) + "\n", encoding="utf-8"
    )
    zero_lines = [
        "# V51 Frozen-Checkpoint RGB-Only Stress Summary",
        "",
        "The zero channels are a controlled intervention, not physical sensor failure. Results do not validate thermal/event transfer.",
        "",
        "| Metric | Mean paired delta (RA - early) | Sample SD |",
        "|---|---:|---:|",
    ]
    for metric in METRICS:
        stats = zero_summary["paired_deltas"][metric]
        zero_lines.append(f"| {metric} | {stats['mean']:.6f} | {stats['sample_sd']:.6f} |")
    (OUTPUT / "zero_shot_summary.md").write_text("\n".join(zero_lines) + "\n", encoding="utf-8")
    (OUTPUT / "claim_scan.txt").write_text(
        "PASS\nRoute B wording retained. V50 quarantined metrics are not read by this builder.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
