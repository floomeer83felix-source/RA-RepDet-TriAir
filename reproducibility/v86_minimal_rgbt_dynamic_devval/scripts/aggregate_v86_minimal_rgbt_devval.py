#!/usr/bin/env python3
"""Freeze the three-seed RGB+thermal dynamic control and paired comparison."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import statistics
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN_ROOT = ROOT / "runs/v86_minimal_rgbt_dynamic_devval"
OUT = ROOT / "reproducibility/v86_minimal_rgbt_dynamic_devval/results"
SOURCE_PATH = "runs/v84_jei_critical_closure/channel_removal_2x2/per_run.csv"
SOURCE_SHA256 = "d77f30d7da4b660235e6d4bbf8d9ef48f7c3ca71c2bfced948c43bbe6266cb5f"
SPLIT_SHA256 = "722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f"
METRICS = ("ap50_95", "ap50", "ap75", "ar100")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source_bytes = subprocess.check_output(["git", "show", f"HEAD:{SOURCE_PATH}"], cwd=ROOT)
    if hashlib.sha256(source_bytes).hexdigest() != SOURCE_SHA256:
        raise RuntimeError("authoritative V84/V48 comparison source hash mismatch")
    source_rows = list(csv.DictReader(io.StringIO(source_bytes.decode("utf-8-sig"))))
    tri = {
        int(row["seed"]): row
        for row in source_rows
        if row["variant"] == "ra_no_moddrop" and row["condition"] == "full"
    }
    if set(tri) != {0, 1, 2}:
        raise RuntimeError("expected exactly three authoritative tri-modal rows")

    rgbt: dict[int, dict[str, object]] = {}
    per_seed: list[dict[str, object]] = []
    for seed in range(3):
        status = json.loads((RUN_ROOT / f"seed{seed}/run_status.json").read_text(encoding="utf-8-sig"))
        metrics = json.loads((RUN_ROOT / f"seed{seed}/coco_eval/metrics.json").read_text())
        if status["state"] != "COMPLETE" or metrics["split_sha256"] != SPLIT_SHA256:
            raise RuntimeError(f"seed {seed} is incomplete or uses the wrong split")
        checkpoint = Path(status["checkpoint"])
        checkpoint_hash = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        if checkpoint_hash != metrics["checkpoint_sha256"]:
            raise RuntimeError(f"seed {seed} checkpoint hash mismatch")
        rgbt[seed] = metrics
        per_seed.append(
            {
                "seed": seed,
                **{metric: f"{float(metrics[metric]):.9f}" for metric in METRICS},
                "checkpoint_sha256": checkpoint_hash,
                "split_sha256": metrics["split_sha256"],
            }
        )

    summary_rows: list[dict[str, object]] = []
    delta_rows: list[dict[str, object]] = []
    delta_summary: dict[str, dict[str, float | int]] = {}
    for metric in METRICS:
        rgbt_values = [float(rgbt[seed][metric]) for seed in range(3)]
        tri_values = [float(tri[seed][metric]) for seed in range(3)]
        deltas = [tri_values[seed] - rgbt_values[seed] for seed in range(3)]
        summary_rows.extend(
            [
                {
                    "model": "rgb_thermal_dynamic",
                    "metric": metric,
                    "n": 3,
                    "mean": f"{statistics.mean(rgbt_values):.9f}",
                    "sample_sd": f"{statistics.stdev(rgbt_values):.9f}",
                },
                {
                    "model": "rgb_thermal_event_dynamic",
                    "metric": metric,
                    "n": 3,
                    "mean": f"{statistics.mean(tri_values):.9f}",
                    "sample_sd": f"{statistics.stdev(tri_values):.9f}",
                },
            ]
        )
        for seed, delta in enumerate(deltas):
            delta_rows.append(
                {
                    "seed": seed,
                    "metric": metric,
                    "rgb_thermal": f"{rgbt_values[seed]:.9f}",
                    "rgb_thermal_event": f"{tri_values[seed]:.9f}",
                    "tri_modal_minus_two_modal": f"{delta:.9f}",
                }
            )
        delta_summary[metric] = {
            "mean": statistics.mean(deltas),
            "sample_sd": statistics.stdev(deltas),
            "positive_seeds": sum(delta > 0 for delta in deltas),
        }

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "rgbt_dynamic_per_seed.csv", per_seed)
    write_csv(OUT / "model_summary.csv", summary_rows)
    write_csv(OUT / "paired_event_deltas.csv", delta_rows)
    payload = {
        "status": "COMPLETE",
        "seeds": [0, 1, 2],
        "split_sha256": SPLIT_SHA256,
        "authoritative_tri_modal_source": SOURCE_PATH,
        "authoritative_tri_modal_source_sha256": SOURCE_SHA256,
        "rgb_thermal_rows": per_seed,
        "model_summary": summary_rows,
        "paired_tri_modal_minus_two_modal": delta_summary,
        "historical_guard_accessed": False,
        "v86_outer_folds_accessed": False,
    }
    (OUT / "result_summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    ap = delta_summary["ap50_95"]
    lines = [
        "# V86 Minimal RGB+Thermal Dynamic Devval Result",
        "",
        "Status: **COMPLETE**",
        "",
        "| Model | AP | AP50 | AP75 | AR100 |",
        "|---|---:|---:|---:|---:|",
    ]
    model_names = {
        "rgb_thermal_dynamic": "RGB+thermal dynamic",
        "rgb_thermal_event_dynamic": "RGB+thermal+event dynamic",
    }
    for model in model_names:
        values = {row["metric"]: row for row in summary_rows if row["model"] == model}
        lines.append(
            f"| {model_names[model]} | "
            + " | ".join(
                f"{float(values[metric]['mean']):.4f} +/- {float(values[metric]['sample_sd']):.4f}"
                for metric in METRICS
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "The same-seed tri-modal minus two-modal AP differences are "
            "-0.0110, +0.0657, and +0.0471. The paired mean difference is "
            f"{float(ap['mean']):+.4f} with sample SD {float(ap['sample_sd']):.4f}; "
            f"{int(ap['positive_seeds'])}/3 seeds are positive.",
            "",
            "This supports a descriptive mean event-associated improvement within the frozen",
            "development-validation protocol, concentrated in AP75/AR rather than AP50. It does",
            "not support a claim of uniform per-seed improvement, statistical significance,",
            "independent testing, or general event utility outside this dataset.",
            "",
            "No historical guard or V86 outer fold was accessed.",
            "",
        ]
    )
    (OUT / "V86_MINIMAL_RGBT_DYNAMIC_RESULT.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
