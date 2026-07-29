#!/usr/bin/env python
"""Build fail-closed summaries for V79 evaluator-only single-modality completion."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, stdev

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODES = ("rgb", "thermal", "event")
SEEDS = (0, 1, 2)
METRICS = ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")
REFERENCE = PROJECT_ROOT / "runs" / "v77_single_modality_results_integration" / "single_modality_per_run.csv"
MODE_TO_REFERENCE = {"rgb": "RGB-only", "thermal": "Thermal-only", "event": "Event-only"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(PROJECT_ROOT / "runs" / "v79_single_modality_evaluator_completion"))
    return parser.parse_args()


def load_reference() -> dict[tuple[str, int], dict]:
    if not REFERENCE.is_file():
        return {}
    with REFERENCE.open(newline="", encoding="utf-8") as handle:
        return {
            (row["modality"], int(row["seed"])): row
            for row in csv.DictReader(handle)
        }


def main() -> None:
    args = parse_args()
    out = Path(args.out).expanduser()
    if not out.is_absolute():
        out = PROJECT_ROOT / out
    reference = load_reference()
    records = []
    missing = []
    invalid = []

    for mode in MODES:
        for seed in SEEDS:
            run_id = f"{mode}_seed{seed}"
            path = out / "raw" / f"{run_id}.json"
            if not path.is_file():
                missing.append(str(path))
                continue
            row = json.loads(path.read_text(encoding="utf-8"))
            required = (*METRICS, "checkpoint_sha256", "split_sha256")
            absent = [key for key in required if key not in row]
            if row.get("input_mode") != mode or int(row.get("seed", -1)) != seed or absent:
                invalid.append({"run_id": run_id, "absent": absent, "reported_mode": row.get("input_mode"), "reported_seed": row.get("seed")})
                continue
            ref = reference.get((MODE_TO_REFERENCE[mode], seed))
            if ref:
                row["v77_reference_ap50"] = float(ref["ap50"])
                row["v77_reference_ap75"] = float(ref["ap75"])
                row["delta_vs_v77_ap50"] = float(row["ap50"]) - float(ref["ap50"])
                row["delta_vs_v77_ap75"] = float(row["ap75"]) - float(ref["ap75"])
            records.append(row)

    if missing or invalid or len(records) != 9:
        payload = {
            "status": "V79_SINGLE_MODALITY_EVALUATOR_INCOMPLETE",
            "completed_runs": len(records),
            "required_runs": 9,
            "missing": missing,
            "invalid": invalid,
        }
        out.mkdir(parents=True, exist_ok=True)
        (out / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        raise RuntimeError(f"V79 evaluator incomplete: {len(records)}/9")

    groups = {}
    for mode in MODES:
        rows = sorted((row for row in records if row["input_mode"] == mode), key=lambda row: int(row["seed"]))
        groups[mode] = {
            "seeds": [int(row["seed"]) for row in rows],
            "metrics": {
                metric: {
                    "mean": mean(float(row[metric]) for row in rows),
                    "sample_std": stdev(float(row[metric]) for row in rows),
                    "n": len(rows),
                }
                for metric in METRICS
            },
        }

    payload = {
        "status": "V79_SINGLE_MODALITY_EVALUATOR_COMPLETE",
        "completed_runs": 9,
        "required_runs": 9,
        "metrics": list(METRICS),
        "per_run": records,
        "group_summaries": groups,
        "reference_reconciliation": "AP50/AP75 deltas compare the standardized evaluator outputs with the user-supplied V77 rows; differences are reported, never silently overwritten.",
        "claim_boundary": {
            "allowed": ["descriptive component-disjoint development-validation results", "uniform COCO AP/AR comparison of retained checkpoints"],
            "disallowed": ["independent-test performance", "statistical significance", "retraining or tuning", "guard-partition access"],
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    fields = [
        "run_id", "input_mode", "seed", *METRICS,
        "checkpoint_epoch", "checkpoint_sha256", "split_sha256",
        "v77_reference_ap50", "delta_vs_v77_ap50",
        "v77_reference_ap75", "delta_vs_v77_ap75",
        "inference_and_metric_seconds",
    ]
    with (out / "per_run.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted(records, key=lambda row: (MODES.index(row["input_mode"]), int(row["seed"]))))

    lines = [
        "# V79 standardized single-modality evaluator completion",
        "",
        "| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode in MODES:
        values = groups[mode]["metrics"]

        def fmt(metric: str) -> str:
            return f"{values[metric]['mean']:.4f} ± {values[metric]['sample_std']:.4f}"

        lines.append(f"| {MODE_TO_REFERENCE[mode]} | {fmt('ap50_95')} | {fmt('ap50')} | {fmt('ap75')} | {fmt('ar1')} | {fmt('ar10')} | {fmt('ar100')} |")
    lines.extend(["", "All values are mean ± sample standard deviation over seeds 0, 1, and 2.", ""])
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
