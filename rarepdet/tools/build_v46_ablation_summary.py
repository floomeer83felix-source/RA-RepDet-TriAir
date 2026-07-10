#!/usr/bin/env python
"""Build the V46 development-validation causal ablation evidence package."""

import csv
from datetime import datetime
import json
from pathlib import Path
import re
from statistics import mean, stdev


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v46_coco_ablation"

BASE_RUNS = [
    ("matched_early_seed0", "matched_early", 0),
    ("matched_early_seed1", "matched_early", 1),
    ("matched_early_seed2", "matched_early", 2),
    ("reliability_p015_seed0", "ra_full_p015", 0),
    ("reliability_p015_seed1", "ra_full_p015", 1),
    ("reliability_p015_seed2", "ra_full_p015", 2),
]

NEW_RUNS = [
    ("ra_no_moddrop_seed0", "ra_no_moddrop", 0),
    ("early_moddrop_seed0", "early_moddrop", 0),
]

METRICS = ["precision", "recall", "f1", "ap50_95", "ap50", "ap75", "ar100"]
IOU_KEYS = [f"{0.50 + 0.05 * index:.2f}" for index in range(10)]
CSV_FIELDS = [
    "run_id",
    "variant",
    "seed",
    "model",
    "modality_dropout",
    "evidence_source",
    "images",
    "gt_boxes",
    "detections",
    *METRICS,
    *[f"ap_iou_{key.replace('.', '')}" for key in IOU_KEYS],
    "project_ap50",
    "project_ap75",
    "checkpoint_sha256",
    "split_sha256",
    "training_elapsed_seconds",
    "training_runtime_source",
    "checkpoint_selection_rule",
    "weights",
    "eval_command",
]


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def relative(path_text):
    path = Path(path_text)
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def logged_training_seconds(run_id):
    log_path = OUTPUT_DIR / "local_training" / run_id / "train_log.txt"
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    epoch_times = [
        float(match.group(1))
        for match in re.finditer(r"epoch_time_sec=([0-9]+(?:\.[0-9]+)?)", log_text)
    ]
    if len(epoch_times) != 50:
        raise RuntimeError(f"expected 50 epoch runtimes in {log_path}, found {len(epoch_times)}")
    return sum(epoch_times)


def load_records(source_lock, execution_status):
    expected_split_hash = source_lock["manifests"]["devval"]["sha256"]
    status_by_run = {record["run_id"]: record for record in execution_status["runs"]}
    records = []

    for run_id, variant, seed in BASE_RUNS:
        path = OUTPUT_DIR / "raw" / "coco" / "devval" / f"{run_id}.json"
        record = load_json(path)
        record["evidence_source"] = "source-locked existing checkpoint"
        record["training_elapsed_seconds"] = None
        record["training_runtime_source"] = "pre-existing run; see V40/V41 source lock"
        record["checkpoint_selection_rule"] = "pre-existing development-validation project-local AP50"
        record["eval_command"] = record["command"]
        records.append(record)

    for run_id, variant, seed in NEW_RUNS:
        path = OUTPUT_DIR / "raw" / "ablation_devval" / f"{run_id}.json"
        record = load_json(path)
        status = status_by_run.get(run_id)
        if status is None:
            raise RuntimeError(f"missing execution status for {run_id}")
        if status["checkpoint_sha256"] != record["checkpoint_sha256"]:
            raise RuntimeError(f"checkpoint hash mismatch for {run_id}")
        record["evidence_source"] = "V46 fresh seed0 training"
        if status.get("train_elapsed_seconds") is None:
            record["training_elapsed_seconds"] = logged_training_seconds(run_id)
            record["training_runtime_source"] = "sum of 50 per-epoch train_log epoch_time_sec values"
        else:
            record["training_elapsed_seconds"] = status["train_elapsed_seconds"]
            record["training_runtime_source"] = "runner wall-clock elapsed_seconds"
        record["checkpoint_selection_rule"] = execution_status["selection_rule"]
        record["eval_command"] = status["eval_command"]
        records.append(record)

    for record in records:
        if record["split_sha256"] != expected_split_hash:
            raise RuntimeError(f"development-validation split mismatch for {record['run_id']}")
    return records


def csv_row(record):
    row = {field: record.get(field, "") for field in CSV_FIELDS}
    for key in IOU_KEYS:
        row[f"ap_iou_{key.replace('.', '')}"] = record["ap_by_iou"][key]
    row["weights"] = relative(record["weights"])
    return row


def descriptive(values):
    return {
        "mean": mean(values),
        "sample_sd": stdev(values) if len(values) > 1 else None,
        "min": min(values),
        "max": max(values),
        "n": len(values),
    }


def group_summaries(records):
    summaries = {}
    for variant in ("matched_early", "ra_full_p015", "ra_no_moddrop", "early_moddrop"):
        selected = [record for record in records if record["variant"] == variant]
        summaries[variant] = {
            "seeds": sorted(int(record["seed"]) for record in selected),
            "metrics": {
                metric: descriptive([float(record[metric]) for record in selected])
                for metric in METRICS
            },
        }
    return summaries


def contrast(minuend, subtrahend, label, interpretation):
    values = {metric: float(minuend[metric]) - float(subtrahend[metric]) for metric in METRICS}
    values["ap_by_iou"] = {
        key: float(minuend["ap_by_iou"][key]) - float(subtrahend["ap_by_iou"][key])
        for key in IOU_KEYS
    }
    return {
        "contrast": label,
        "minuend_run": minuend["run_id"],
        "subtrahend_run": subtrahend["run_id"],
        "seed": 0,
        "metrics": values,
        "interpretation": interpretation,
    }


def build_contrasts(records):
    by_run = {record["run_id"]: record for record in records}
    return [
        contrast(
            by_run["reliability_p015_seed0"],
            by_run["ra_no_moddrop_seed0"],
            "ra_full_p015_minus_ra_no_moddrop",
            "Seed0 modality-dropout increment within the same reliability-stem and dynamic-gate architecture.",
        ),
        contrast(
            by_run["ra_no_moddrop_seed0"],
            by_run["matched_early_seed0"],
            "ra_no_moddrop_minus_matched_early",
            "Seed0 combined increment of modality-specific stems plus dynamic softmax gating; it does not isolate the gate alone.",
        ),
        contrast(
            by_run["early_moddrop_seed0"],
            by_run["matched_early_seed0"],
            "early_moddrop_minus_matched_early",
            "Seed0 modality-dropout increment within the matched early-fusion architecture.",
        ),
        contrast(
            by_run["reliability_p015_seed0"],
            by_run["early_moddrop_seed0"],
            "ra_full_p015_minus_early_moddrop",
            "Seed0 architecture increment at matched modality-dropout probability; stems and dynamic gating remain bundled.",
        ),
    ]


def value(number):
    return f"{float(number):.6f}"


def main():
    source_lock = load_json(OUTPUT_DIR / "source_lock_v46.json")
    execution_status = load_json(OUTPUT_DIR / "ablation_execution_status.json")
    if execution_status["status"] != "SEED0_FEASIBLE_ABLATIONS_COMPLETE":
        raise RuntimeError(f"ablation execution is not complete: {execution_status['status']}")

    records = load_records(source_lock, execution_status)
    summaries = group_summaries(records)
    contrasts = build_contrasts(records)
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")

    with (OUTPUT_DIR / "ablation_devval_per_run.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(csv_row(record) for record in records)

    variant_status = {
        "matched_early": "complete for existing fixed seeds 0,1,2",
        "ra_full_p015": "complete for existing fixed seeds 0,1,2",
        "ra_no_moddrop": "fresh V46 seed0 complete; seeds 1,2 deferred for GPU time",
        "early_moddrop": "fresh V46 seed0 complete; seeds 1,2 deferred for GPU time",
        "ra_static_equal": "skipped because it requires architecture/model-loading changes outside the allowed V46 file scope and protected training-core plumbing",
        "ra_stems_concat_or_project": "skipped because it requires architecture/model-loading changes outside the allowed V46 file scope and protected training-core plumbing",
    }
    summary = {
        "status": "V46_CAUSAL_ABLATION_SEED0_PARTIAL_COMPLETE",
        "generated_at": generated_at,
        "protocol": "frozen V40 component-disjoint development-validation",
        "checkpoint_selection_rule": execution_status["selection_rule"],
        "guard_used_for_training_or_selection": False,
        "per_run": records,
        "group_summaries": summaries,
        "seed0_contrasts": contrasts,
        "variant_status": variant_status,
        "ablation_guard_evaluation_run": False,
        "partial_completion_reason": "The two feasible seed0 runs require approximately 14-17 GPU hours under the locked 50-epoch protocol; seeds 1 and 2 would require roughly 28-34 additional GPU hours. The task-authorized partial path is used.",
    }
    (OUTPUT_DIR / "ablation_devval_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# V46 Development-Validation Causal Ablation Summary",
        "",
        f"Generated: {generated_at}",
        "",
        "Status: `V46_CAUSAL_ABLATION_SEED0_PARTIAL_COMPLETE`",
        "",
        "All fresh ablation checkpoints were trained for 50 epochs on the frozen V40 training manifest and selected only by development-validation project-local AP50. The locked guard was not accessed for ablation training, selection, continuation, or reporting.",
        "",
        "## Per-run evidence",
        "",
        "| Run | Variant | Seed | Source | Dropout | AP50:95 | AP50 | AP75 | F1@0.50 |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for record in records:
        lines.append(
            f"| {record['run_id']} | {record['variant']} | {record['seed']} | {record['evidence_source']} | {float(record['modality_dropout']):.2f} | {value(record['ap50_95'])} | {value(record['ap50'])} | {value(record['ap75'])} | {value(record['f1'])} |"
        )
    lines.extend(
        [
            "",
            "## Seed0 controlled contrasts",
            "",
            "| Contrast | Delta AP50:95 | Delta AP50 | Delta AP75 | Delta F1 | Scope |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for item in contrasts:
        metrics = item["metrics"]
        lines.append(
            f"| {item['contrast']} | {value(metrics['ap50_95'])} | {value(metrics['ap50'])} | {value(metrics['ap75'])} | {value(metrics['f1'])} | {item['interpretation']} |"
        )
    lines.extend(["", "## Variant completion", ""])
    for variant, status in variant_status.items():
        lines.append(f"- `{variant}`: {status}.")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "The fresh contrasts contain one seed only and are descriptive. The available implementation isolates modality dropout within each architecture, but modality-specific stems and dynamic softmax gating remain bundled because static-equal and deterministic-projection variants would require out-of-scope protected model/training changes. No guard ablation evaluation was run.",
            "",
        ]
    )
    (OUTPUT_DIR / "ablation_devval_summary.md").write_text("\n".join(lines), encoding="utf-8")

    boundary = """# V46 Causal Ablation Claim Boundary

## Allowed statements

- The V46 package reports canonical COCO-style bbox AP for six fixed baseline/main checkpoints on frozen development-validation and locked same-dataset guard manifests.
- The fresh causal-ablation evidence is a seed0-only development-validation comparison under the locked 50-epoch protocol.
- `ra_full_p015 - ra_no_moddrop` is a seed0 estimate of the modality-dropout increment within the reliability architecture.
- `early_moddrop - matched_early` is a seed0 estimate of the modality-dropout increment within early fusion.
- `ra_no_moddrop - matched_early` bundles modality-specific stems and dynamic gating and cannot be attributed to the gate alone.

## Required cautions

- The new ablation contrasts have one seed and do not establish statistical significance.
- The held-out guard is same-dataset evidence and is not an independent public benchmark or external generalization test.
- No result establishes optimal dropout, calibrated sensor reliability, or real sensor-fault robustness.
- COCO-style metric reporting is an evaluation convention, not COCO proof of generalization or robustness.
- Static-equal and deterministic-projection controls were not implemented because the task's allowed-file scope forbids the required protected model/training plumbing changes.
- Seeds 1 and 2 for the two fresh feasible variants remain deferred because of the measured GPU runtime.
"""
    (OUTPUT_DIR / "ablation_claim_boundary.md").write_text(boundary, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": summary["status"],
                "new_runs": [record["run_id"] for record in records if record["evidence_source"].startswith("V46")],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
