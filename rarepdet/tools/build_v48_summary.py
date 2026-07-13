#!/usr/bin/env python
"""Build V48 development-validation records and seed-paired causal contrasts."""

import csv
from datetime import datetime
import json
from pathlib import Path
from statistics import mean, stdev
import sys

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v48_complete_ablation"
V46_DIR = PROJECT_ROOT / "runs" / "v46_coco_ablation"
METRICS = ("precision", "recall", "f1", "ap50_95", "ap50", "ap75", "ar100")
BASE_RUNS = (
    ("matched_early_seed0", "matched_early", 0, "runs/v46_coco_ablation/raw/coco/devval/matched_early_seed0.json"),
    ("matched_early_seed1", "matched_early", 1, "runs/v46_coco_ablation/raw/coco/devval/matched_early_seed1.json"),
    ("matched_early_seed2", "matched_early", 2, "runs/v46_coco_ablation/raw/coco/devval/matched_early_seed2.json"),
    ("reliability_p015_seed0", "ra_full_p015", 0, "runs/v46_coco_ablation/raw/coco/devval/reliability_p015_seed0.json"),
    ("reliability_p015_seed1", "ra_full_p015", 1, "runs/v46_coco_ablation/raw/coco/devval/reliability_p015_seed1.json"),
    ("reliability_p015_seed2", "ra_full_p015", 2, "runs/v46_coco_ablation/raw/coco/devval/reliability_p015_seed2.json"),
    ("ra_no_moddrop_seed0", "ra_no_moddrop", 0, "runs/v46_coco_ablation/raw/ablation_devval/ra_no_moddrop_seed0.json"),
    ("early_moddrop_seed0", "early_moddrop", 0, "runs/v46_coco_ablation/raw/ablation_devval/early_moddrop_seed0.json"),
)
FRESH_SPECS = (
    ("ra_no_moddrop_seed1", "ra_no_moddrop", "reliability", 0.00, 1),
    ("ra_no_moddrop_seed2", "ra_no_moddrop", "reliability", 0.00, 2),
    ("early_moddrop_seed1", "early_moddrop", "early", 0.15, 1),
    ("early_moddrop_seed2", "early_moddrop", "early", 0.15, 2),
    ("ra_static_equal_seed0", "ra_static_equal", "ra_static_equal", 0.00, 0),
    ("ra_static_equal_seed1", "ra_static_equal", "ra_static_equal", 0.00, 1),
    ("ra_static_equal_seed2", "ra_static_equal", "ra_static_equal", 0.00, 2),
    ("ra_stems_project_seed0", "ra_stems_project", "ra_stems_project", 0.00, 0),
    ("ra_stems_project_seed1", "ra_stems_project", "ra_stems_project", 0.00, 1),
    ("ra_stems_project_seed2", "ra_stems_project", "ra_stems_project", 0.00, 2),
)
CONTRASTS = (
    ("ra_full_p015", "matched_early", "ra_full_p015_minus_matched_early", "Development-validation full reliability-aware fusion minus matched early fusion."),
    ("ra_no_moddrop", "matched_early", "ra_no_moddrop_minus_matched_early", "Development-validation combination of separate stems and dynamic gate minus matched early fusion."),
    ("ra_full_p015", "ra_no_moddrop", "ra_full_p015_minus_ra_no_moddrop", "Development-validation modality-dropout increment within the reliability-aware architecture."),
    ("early_moddrop", "matched_early", "early_moddrop_minus_matched_early", "Development-validation modality-dropout increment within early fusion."),
    ("ra_static_equal", "matched_early", "ra_static_equal_minus_matched_early", "Development-validation increment from separate stems with fixed equal feature fusion."),
    ("ra_no_moddrop", "ra_static_equal", "ra_no_moddrop_minus_ra_static_equal", "Development-validation dynamic-gating increment beyond equal-weight stem fusion."),
    ("ra_stems_project", "matched_early", "ra_stems_project_minus_matched_early", "Development-validation learned deterministic fusion control minus matched early fusion."),
    ("ra_no_moddrop", "ra_stems_project", "ra_no_moddrop_minus_ra_stems_project", "Development-validation dynamic-gating contrast against deterministic learned projection control."),
)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def checkpoint_epoch(weights):
    try:
        return int(torch.load(weights, map_location="cpu", weights_only=False).get("epoch"))
    except Exception:
        return None


def inherited_records():
    records = []
    for run_id, variant, seed, relative_path in BASE_RUNS:
        record = load_json(PROJECT_ROOT / relative_path)
        record.update(
            variant=variant,
            seed=seed,
            evidence_source="inherited V46 source-locked checkpoint" if variant in {"matched_early", "ra_full_p015"} else "inherited V46 fresh seed0 training",
            selected_epoch=checkpoint_epoch(record["weights"]),
            training_runtime_seconds=None,
            checkpoint_selection_rule="development-validation project-local AP50",
        )
        records.append(record)
    return records


def fresh_records():
    records = []
    for run_id, variant, model, dropout, seed in FRESH_SPECS:
        run_dir = OUTPUT_DIR / "training" / run_id
        status_path = run_dir / "run_status.json"
        result_path = OUTPUT_DIR / "raw" / "devval" / f"{run_id}.json"
        if not status_path.is_file() or not result_path.is_file():
            continue
        status = load_json(status_path)
        if status.get("state") != "COMPLETE":
            continue
        result = load_json(result_path)
        if result.get("checkpoint_sha256") != status.get("checkpoint_sha256"):
            raise RuntimeError(f"checkpoint hash mismatch for {run_id}")
        if result.get("split_sha256") != load_json(OUTPUT_DIR / "source_lock_v48.json")["manifests"]["devval"]["sha256"]:
            raise RuntimeError(f"development-validation manifest mismatch for {run_id}")
        result.update(
            variant=variant,
            model=model,
            seed=seed,
            modality_dropout=dropout,
            evidence_source="V48 fresh training",
            selected_epoch=status.get("selected_epoch"),
            training_runtime_seconds=status.get("training_runtime_seconds"),
            checkpoint_selection_rule=status.get("checkpoint_selection_rule"),
            train_command=status.get("train_command"),
            eval_command=status.get("eval_command"),
        )
        records.append(result)
    return records


def status_payload():
    runs = []
    for run_id, variant, model, dropout, seed in FRESH_SPECS:
        status_path = OUTPUT_DIR / "training" / run_id / "run_status.json"
        if status_path.is_file():
            runs.append(load_json(status_path))
        else:
            runs.append({
                "run_id": run_id,
                "variant": variant,
                "model": model,
                "modality_dropout": dropout,
                "seed": seed,
                "state": "PENDING",
                "checkpoint_selection_rule": "development-validation project-local AP50",
                "guard_used": False,
            })
    complete = [record for record in runs if record.get("state") == "COMPLETE"]
    status = "V48_CAUSAL_ABLATION_COMPLETE" if len(complete) == len(FRESH_SPECS) else "V48_CAUSAL_ABLATION_PARTIAL_GPU_RUNNING"
    return {
        "status": status,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "selection_rule": "highest development-validation project-local AP50",
        "guard_used": False,
        "completed_fresh_runs": len(complete),
        "required_fresh_runs": len(FRESH_SPECS),
        "runs": runs,
    }


def descriptive(values):
    return {
        "mean": mean(values),
        "sample_sd": stdev(values) if len(values) > 1 else None,
        "n": len(values),
    }


def group_summaries(records):
    results = {}
    for variant in ("matched_early", "early_moddrop", "ra_static_equal", "ra_stems_project", "ra_no_moddrop", "ra_full_p015"):
        group = [record for record in records if record["variant"] == variant]
        results[variant] = {
            "seeds": sorted(int(record["seed"]) for record in group),
            "metrics": {metric: descriptive([float(record[metric]) for record in group]) for metric in METRICS} if group else {},
        }
    return results


def paired_deltas(records):
    by_variant = {}
    for record in records:
        by_variant.setdefault(record["variant"], {})[int(record["seed"])] = record
    rows = []
    summaries = {}
    for minuend, subtrahend, label, interpretation in CONTRASTS:
        shared = sorted(set(by_variant.get(minuend, {})) & set(by_variant.get(subtrahend, {})))
        metric_values = {metric: [] for metric in METRICS}
        for seed in shared:
            row = {
                "contrast": label,
                "minuend": minuend,
                "subtrahend": subtrahend,
                "seed": seed,
                "interpretation": interpretation,
            }
            for metric in METRICS:
                delta = float(by_variant[minuend][seed][metric]) - float(by_variant[subtrahend][seed][metric])
                row[f"delta_{metric}"] = delta
                metric_values[metric].append(delta)
            rows.append(row)
        summaries[label] = {
            "minuend": minuend,
            "subtrahend": subtrahend,
            "shared_seeds": shared,
            "interpretation": interpretation,
            "metrics": {metric: descriptive(values) for metric, values in metric_values.items() if values},
        }
    return rows, summaries


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        headers = list(rows[0]) if rows else ["no_completed_records"]
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main():
    if not (OUTPUT_DIR / "source_lock_v48.json").is_file():
        raise FileNotFoundError("V48 source lock is required before summaries")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    execution = status_payload()
    atomic_json(OUTPUT_DIR / "run_status.json", execution)
    records = inherited_records() + fresh_records()
    records.sort(key=lambda record: (record["variant"], int(record["seed"])))
    groups = group_summaries(records)
    deltas, delta_summaries = paired_deltas(records)
    summary = {
        "status": execution["status"],
        "generated_at": execution["generated_at"],
        "protocol": "frozen V40 component-disjoint development-validation",
        "guard_used_for_training_or_selection": False,
        "checkpoint_selection_rule": execution["selection_rule"],
        "per_run": records,
        "group_summaries": groups,
        "paired_deltas": delta_summaries,
        "fresh_execution": execution,
    }
    (OUTPUT_DIR / "causal_ablation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    per_run_rows = []
    for record in records:
        row = {key: record.get(key, "") for key in ("run_id", "variant", "model", "seed", "modality_dropout", "evidence_source", "precision", "recall", "f1", "ap50_95", "ap50", "ap75", "ar100", "selected_epoch", "training_runtime_seconds", "checkpoint_selection_rule", "checkpoint_sha256", "weights")}
        per_run_rows.append(row)
    write_csv(OUTPUT_DIR / "devval_per_run.csv", per_run_rows)
    write_csv(OUTPUT_DIR / "devval_paired_deltas.csv", deltas)

    lines = [
        "# V48 Causal Ablation Summary",
        "",
        f"Generated: {execution['generated_at']}",
        "",
        f"Status: `{execution['status']}`",
        "",
        "All V48 comparisons are frozen development-validation evidence. Checkpoint selection is development-validation project-local AP50. No V48 variant accesses the locked holdout.",
        "",
        "## Per-run evidence",
        "",
        "| Run | Variant | Seed | Source | AP50:95 | AP50 | AP75 | F1 | Selected epoch | Runtime sec |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for record in records:
        runtime = record.get("training_runtime_seconds")
        lines.append(f"| {record['run_id']} | {record['variant']} | {record['seed']} | {record['evidence_source']} | {float(record['ap50_95']):.6f} | {float(record['ap50']):.6f} | {float(record['ap75']):.6f} | {float(record['f1']):.6f} | {record.get('selected_epoch', 'NA')} | {'NA' if runtime is None else f'{float(runtime):.1f}'} |")
    lines.extend(["", "## Paired contrasts", "", "| Contrast | Shared seeds | Mean delta AP50:95 | Sample SD | Scope |", "| --- | --- | ---: | ---: | --- |"])
    for label, item in delta_summaries.items():
        metric = item["metrics"].get("ap50_95")
        mean_value = "NA" if metric is None else f"{metric['mean']:.6f}"
        sd_value = "NA" if metric is None or metric["sample_sd"] is None else f"{metric['sample_sd']:.6f}"
        lines.append(f"| {label} | {item['shared_seeds']} | {mean_value} | {sd_value} | {item['interpretation']} |")
    lines.extend(["", "## Completion", ""])
    for record in execution["runs"]:
        lines.append(f"- `{record['run_id']}`: `{record.get('state', 'PENDING')}`.")
    lines.extend(["", "## Boundary", "", "Means and sample SDs are descriptive for only the shared completed seeds. No significance test is run or claimed. The deterministic-projection control is a learned fixed-order fusion control and does not isolate stems alone.", ""])
    (OUTPUT_DIR / "causal_ablation_summary.md").write_text("\n".join(lines), encoding="utf-8")
    boundary = """# V48 Causal Ablation Claim Boundary

## Permitted interpretation

- All V48 comparisons are descriptive development-validation contrasts under the frozen V40 component-disjoint protocol.
- `early_moddrop - matched_early` is the architecture-specific training-time modality-dropout contrast for early fusion.
- `ra_full_p015 - ra_no_moddrop` is the training-time modality-dropout contrast within the reliability-aware architecture.
- `ra_static_equal - matched_early` combines modality-specific stems and fixed equal-weight feature fusion.
- `ra_no_moddrop - ra_static_equal` is the cleanest available dynamic-gating contrast beyond equal-weight stem fusion.
- `ra_stems_project` is a deterministic learned fixed-order fusion control; it does not isolate modality-specific stems alone.

## Required limitations

- Report only the completed shared seed coverage with descriptive means and sample SDs.
- Do not treat this same-dataset development-validation evidence as external or independent validation.
- Do not infer a universal dropout choice, calibrated reliability, sensor-health probabilities, or real fault behavior.
- The locked holdout was not used for V48 training, selection, continuation, or reporting.
"""
    (OUTPUT_DIR / "claim_boundary.md").write_text(boundary, encoding="utf-8")
    print(json.dumps({"status": execution["status"], "completed_fresh_runs": execution["completed_fresh_runs"]}, indent=2))


if __name__ == "__main__":
    main()
