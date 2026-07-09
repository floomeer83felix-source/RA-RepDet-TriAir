#!/usr/bin/env python
"""Consolidate V40 seed0/seed2 and V41 seed1 development-validation evidence.

This script reads only lightweight report artifacts. It does not load checkpoints,
raw data, predictions, guard/test manifests, or image assets.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from datetime import datetime
from pathlib import Path

METRICS = ["precision", "recall", "f1", "ap50", "ap75"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--v40-summary", required=True)
    parser.add_argument("--seed1-summary", required=True)
    parser.add_argument("--seed1-source-lock", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def read_seed1_csv(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 2:
        raise RuntimeError(f"Expected exactly two seed1 rows, got {len(rows)} from {path}")
    out = []
    for row in rows:
        out.append({
            "seed": str(row["seed"]),
            "model_group": row["model_group"],
            "model": row["model"],
            "run_id": row["run_id"],
            "evidence_source": "V41_seed1",
            "precision": float(row["precision"]),
            "recall": float(row["recall"]),
            "f1": float(row["f1"]),
            "ap50": float(row["ap50"]),
            "ap75": float(row["ap75"]),
            "checkpoint_sha256": row.get("best_checkpoint_sha256") or row.get("checkpoint_sha256", ""),
            "source_reference": str(path).replace("\\", "/"),
        })
    return out


def read_v40_json(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for row in data.get("per_run", []):
        seed = str(row.get("seed"))
        group = row.get("model_group")
        if seed not in {"0", "2"} or group not in {"matched_early", "reliability_p015"}:
            continue
        rows.append({
            "seed": seed,
            "model_group": group,
            "model": row.get("model", ""),
            "run_id": row.get("run_id", ""),
            "evidence_source": "V40",
            "precision": float(row["precision"]),
            "recall": float(row["recall"]),
            "f1": float(row["f1"]),
            "ap50": float(row["ap50"]),
            "ap75": float(row["ap75"]),
            "checkpoint_sha256": row.get("checkpoint_sha256", ""),
            "source_reference": str(path).replace("\\", "/"),
        })
    if len(rows) != 4:
        raise RuntimeError(f"Expected four V40 rows for seeds 0/2, got {len(rows)} from {path}")
    return rows


def paired_deltas(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for seed in ["0", "1", "2"]:
        early = [r for r in rows if r["seed"] == seed and r["model_group"] == "matched_early"]
        rel = [r for r in rows if r["seed"] == seed and r["model_group"] == "reliability_p015"]
        if len(early) != 1 or len(rel) != 1:
            raise RuntimeError(f"Missing paired rows for seed {seed}")
        early = early[0]
        rel = rel[0]
        delta = {"seed": seed, "comparison": "reliability_p015_minus_matched_early"}
        for metric in METRICS:
            delta[metric] = float(rel[metric]) - float(early[metric])
        out.append(delta)
    return out


def fmt(value: float) -> str:
    return f"{value:.12f}"


def write_outputs(out_dir: Path, rows: list[dict[str, object]], deltas: list[dict[str, object]], seed1_source_lock: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().isoformat(timespec="seconds")

    delta_summary = []
    for metric in METRICS:
        vals = [float(d[metric]) for d in deltas]
        delta_summary.append({
            "metric": metric,
            "mean_delta": statistics.mean(vals),
            "sample_sd_delta": statistics.stdev(vals),
            "n_seed_pairs": 3,
        })

    csv_path = out_dir / "three_seed_interim_devval_summary.csv"
    fieldnames = [
        "row_type", "seed", "model_group", "model", "run_id", "evidence_source",
        "precision", "recall", "f1", "ap50", "ap75", "checkpoint_sha256",
        "source_reference", "comparison", "mean_delta", "sample_sd_delta", "n_seed_pairs",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            record = {**row, "row_type": "per_run"}
            for metric in METRICS:
                record[metric] = fmt(float(record[metric]))
            writer.writerow(record)
        for delta in deltas:
            writer.writerow({
                "row_type": "paired_delta",
                "seed": delta["seed"],
                "comparison": delta["comparison"],
                **{metric: fmt(float(delta[metric])) for metric in METRICS},
            })
        for summary in delta_summary:
            writer.writerow({
                "row_type": "delta_summary",
                "model_group": summary["metric"],
                "comparison": "three_seed_interim_development_validation_descriptive_summary",
                "mean_delta": fmt(float(summary["mean_delta"])),
                "sample_sd_delta": fmt(float(summary["sample_sd_delta"])),
                "n_seed_pairs": summary["n_seed_pairs"],
            })

    payload = {
        "generated_at": generated_at,
        "status": "V41_INTERIM_DEVVAL_CONSOLIDATION_COMPLETE",
        "claim_boundary": "three-seed interim development-validation descriptive summary only",
        "inputs": {
            "v40_summary": rows[0]["source_reference"],
            "seed1_summary": [r for r in rows if r["evidence_source"] == "V41_seed1"][0]["source_reference"],
            "seed1_source_lock": str(seed1_source_lock).replace("\\", "/"),
        },
        "per_run": rows,
        "paired_deltas": deltas,
        "delta_summary": delta_summary,
        "limitations": [
            "development-validation only",
            "three seed pairs only",
            "no independent test",
            "no causal ablations",
            "no COCO metrics",
            "no guard/test access in this consolidation task",
        ],
    }
    (out_dir / "three_seed_interim_devval_summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [
        "# Three-Seed Interim Development-Validation Summary",
        "",
        f"Generated: {generated_at}",
        "",
        "Status: `V41_INTERIM_DEVVAL_CONSOLIDATION_COMPLETE`",
        "",
        "This is a **three-seed interim development-validation descriptive summary**. It is not an independent-test result, statistical-significance result, external-generalization result, or manuscript-final aggregate.",
        "",
        "## Per-run rows",
        "",
        "| Seed | Model group | Run | Source | Precision | Recall | F1 | AP50 | AP75 | Checkpoint SHA256 |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        md.append(
            f"| {row['seed']} | {row['model_group']} | {row['run_id']} | {row['evidence_source']} | "
            f"{float(row['precision']):.6f} | {float(row['recall']):.6f} | {float(row['f1']):.6f} | "
            f"{float(row['ap50']):.6f} | {float(row['ap75']):.6f} | `{row['checkpoint_sha256']}` |"
        )
    md.extend([
        "",
        "## Paired deltas: reliability p=0.15 minus matched early",
        "",
        "| Seed | Precision | Recall | F1 | AP50 | AP75 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for delta in deltas:
        md.append(
            f"| {delta['seed']} | {float(delta['precision']):+.6f} | {float(delta['recall']):+.6f} | "
            f"{float(delta['f1']):+.6f} | {float(delta['ap50']):+.6f} | {float(delta['ap75']):+.6f} |"
        )
    md.extend([
        "",
        "## Descriptive delta mean ± sample SD across three seed pairs",
        "",
        "| Metric | Mean delta | Sample SD | n seed pairs |",
        "| --- | ---: | ---: | ---: |",
    ])
    for summary in delta_summary:
        md.append(
            f"| {summary['metric']} | {float(summary['mean_delta']):+.6f} | "
            f"{float(summary['sample_sd_delta']):.6f} | {summary['n_seed_pairs']} |"
        )
    md.extend([
        "",
        "## Boundary",
        "",
        "No new training, evaluation, checkpoint loading, raw data access, prediction-cache access, guard/test access, or manuscript rewriting was performed by this consolidation task.",
    ])
    (out_dir / "three_seed_interim_devval_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    claim = [
        "# V41 Interim Claim Boundary",
        "",
        f"Generated: {generated_at}",
        "",
        "Allowed wording: three-seed interim development-validation descriptive evidence on the frozen V40 component-disjoint development-validation split.",
        "",
        "Disallowed wording: independent test, external generalization, statistical significance, manuscript-final aggregate, optimal dropout, calibrated sensor reliability, or physical sensor-fault robustness.",
        "",
        "No guard/test evaluation, new training, or new evaluation was run in this consolidation task.",
    ]
    (out_dir / "interim_claim_boundary.md").write_text("\n".join(claim) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo = Path(args.repo).resolve()
    v40_summary = repo / args.v40_summary
    seed1_summary = repo / args.seed1_summary
    seed1_source_lock = repo / args.seed1_source_lock
    out_dir = repo / args.out

    for path in [v40_summary, seed1_summary, seed1_source_lock]:
        if not path.exists():
            raise FileNotFoundError(path)

    rows = read_v40_json(v40_summary) + read_seed1_csv(seed1_summary)
    rows = sorted(rows, key=lambda r: (str(r["seed"]), str(r["model_group"])))
    deltas = paired_deltas(rows)
    write_outputs(out_dir, rows, deltas, seed1_source_lock)


if __name__ == "__main__":
    main()
