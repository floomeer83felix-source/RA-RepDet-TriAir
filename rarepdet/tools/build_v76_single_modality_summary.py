#!/usr/bin/env python
"""Build compact per-run and three-seed V76 single-modality summaries."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, stdev

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "runs" / "v76_triair_single_modality_ablation"
METRICS = ("ap50_95", "ap50", "ap75", "ar100")


def main() -> None:
    records = []
    missing = []
    for mode in ("rgb", "thermal", "event"):
        for seed in (0, 1, 2):
            path = OUT / "raw" / f"{mode}_seed{seed}.json"
            if not path.is_file():
                missing.append(path.relative_to(PROJECT_ROOT).as_posix())
                continue
            records.append(json.loads(path.read_text(encoding="utf-8")))

    complete = len(records) == 9
    groups = {}
    for mode in ("rgb", "thermal", "event"):
        rows = sorted((row for row in records if row["input_mode"] == mode), key=lambda row: int(row["seed"]))
        groups[mode] = {
            "seeds": [int(row["seed"]) for row in rows],
            "metrics": {
                metric: {"mean": mean(float(row[metric]) for row in rows), "sample_std": stdev(float(row[metric]) for row in rows) if len(rows) > 1 else None, "n": len(rows)}
                for metric in METRICS if rows
            },
        }

    payload = {
        "status": "V76_SINGLE_MODALITY_ABLATION_COMPLETE" if complete else "V76_SINGLE_MODALITY_ABLATION_INCOMPLETE",
        "completed_runs": len(records),
        "required_runs": 9,
        "missing": missing,
        "per_run": records,
        "group_summaries": groups,
        "claim_boundary": {
            "allowed_when_complete": ["descriptive three-seed comparison of trained RGB-only, thermal-only, and event-only baselines", "comparison under the frozen component-disjoint development-validation protocol"],
            "disallowed": ["independent test performance", "physical sensor-failure robustness", "statistical significance", "selective seed replacement or result-driven reruns"],
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "single_modality_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if records:
        fields = ["run_id", "input_mode", "seed", *METRICS, "checkpoint_epoch", "checkpoint_sha256", "split_sha256"]
        with (OUT / "single_modality_per_run.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(records)
    if not complete:
        raise RuntimeError(f"V76 incomplete: {len(records)}/9 results; missing={missing}")


if __name__ == "__main__":
    main()
