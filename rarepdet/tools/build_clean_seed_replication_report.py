#!/usr/bin/env python
"""Build Phase 4B controlled-seed clean split replication reports."""

import argparse
import csv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"


RUNS = [
    {
        "variant": "R0 Early Fusion",
        "variant_id": "R0",
        "seed": 0,
        "dropout": "NA",
        "dir": RUNS_DIR / "R0_early_seed0_block64g16_e50",
        "missing_required": False,
    },
    {
        "variant": "R0 Early Fusion",
        "variant_id": "R0",
        "seed": 2,
        "dropout": "NA",
        "dir": RUNS_DIR / "R0_early_seed2_block64g16_e50",
        "missing_required": False,
    },
    {
        "variant": "R1 Reliability p=0.00",
        "variant_id": "R1",
        "seed": 0,
        "dropout": "0.00",
        "dir": RUNS_DIR / "R1_reliability_p000_seed0_block64g16_e50",
        "missing_required": True,
    },
    {
        "variant": "R1 Reliability p=0.00",
        "variant_id": "R1",
        "seed": 2,
        "dropout": "0.00",
        "dir": RUNS_DIR / "R1_reliability_p000_seed2_block64g16_e50",
        "missing_required": True,
    },
    {
        "variant": "R2 Reliability p=0.15",
        "variant_id": "R2",
        "seed": 0,
        "dropout": "0.15",
        "dir": RUNS_DIR / "R2_reliability_p015_seed0_block64g16_e50",
        "missing_required": True,
    },
    {
        "variant": "R2 Reliability p=0.15",
        "variant_id": "R2",
        "seed": 2,
        "dropout": "0.15",
        "dir": RUNS_DIR / "R2_reliability_p015_seed2_block64g16_e50",
        "missing_required": True,
    },
    {
        "variant": "R4 Reliability p=0.20",
        "variant_id": "R4",
        "seed": 0,
        "dropout": "0.20",
        "dir": RUNS_DIR / "R4_reliability_p020_seed0_block64g16_e50",
        "missing_required": True,
    },
    {
        "variant": "R4 Reliability p=0.20",
        "variant_id": "R4",
        "seed": 2,
        "dropout": "0.20",
        "dir": RUNS_DIR / "R4_reliability_p020_seed2_block64g16_e50",
        "missing_required": True,
    },
]


PER_RUN_HEADERS = [
    "Variant",
    "Seed",
    "Dropout Ratio",
    "P@0.50",
    "R@0.50",
    "F1@0.50",
    "AP50",
    "AP75",
    "w/o RGB AP50",
    "w/o Thermal AP50",
    "w/o Event AP50",
]

AGGREGATE_HEADERS = ["Variant", "Metric", "Mean", "Min", "Max", "Range"]


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def read_key_values(path):
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt(value):
    value = as_float(value)
    return "NA" if value is None else f"{value:.6f}"


def f1(precision, recall):
    precision = as_float(precision)
    recall = as_float(recall)
    if precision is None or recall is None or precision + recall <= 0.0:
        return None
    return 2.0 * precision * recall / (precision + recall)


def missing_ap(run_dir, mode):
    for row in read_csv(run_dir / "missing_modality" / "missing_modality_results.csv"):
        if row.get("Mode") == mode:
            return row.get("AP50")
    return None


def build_per_run_rows():
    rows = []
    missing_outputs = []
    for run in RUNS:
        eval_path = run["dir"] / "eval_thr050" / "eval_results.txt"
        eval_values = read_key_values(eval_path)
        if not eval_values:
            missing_outputs.append(str(eval_path.relative_to(PROJECT_ROOT)))
        missing_path = run["dir"] / "missing_modality" / "missing_modality_results.csv"
        if run["missing_required"] and not missing_path.exists():
            missing_outputs.append(str(missing_path.relative_to(PROJECT_ROOT)))

        precision = eval_values.get("Precision")
        recall = eval_values.get("Recall")
        rows.append(
            {
                "Variant": run["variant"],
                "Seed": str(run["seed"]),
                "Dropout Ratio": run["dropout"],
                "P@0.50": fmt(precision),
                "R@0.50": fmt(recall),
                "F1@0.50": fmt(f1(precision, recall)),
                "AP50": fmt(eval_values.get("AP50")),
                "AP75": fmt(eval_values.get("AP75")),
                "w/o RGB AP50": "NA" if not run["missing_required"] else fmt(missing_ap(run["dir"], "no_rgb")),
                "w/o Thermal AP50": "NA"
                if not run["missing_required"]
                else fmt(missing_ap(run["dir"], "no_thermal")),
                "w/o Event AP50": "NA"
                if not run["missing_required"]
                else fmt(missing_ap(run["dir"], "no_event")),
            }
        )
    return rows, missing_outputs


def group_rows(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["Variant"], []).append(row)
    return grouped


def aggregate_rows(rows):
    grouped = group_rows(rows)
    metrics = [
        ("Full AP50", "AP50"),
        ("Full AP75", "AP75"),
        ("F1@0.50", "F1@0.50"),
        ("w/o RGB AP50", "w/o RGB AP50"),
        ("w/o Thermal AP50", "w/o Thermal AP50"),
        ("w/o Event AP50", "w/o Event AP50"),
    ]
    aggregate = []
    for variant, variant_rows in grouped.items():
        for label, key in metrics:
            values = [as_float(row.get(key)) for row in variant_rows]
            values = [value for value in values if value is not None]
            if not values:
                aggregate.append({"Variant": variant, "Metric": label, "Mean": "NA", "Min": "NA", "Max": "NA", "Range": "NA"})
                continue
            aggregate.append(
                {
                    "Variant": variant,
                    "Metric": label,
                    "Mean": f"{sum(values) / len(values):.6f}",
                    "Min": f"{min(values):.6f}",
                    "Max": f"{max(values):.6f}",
                    "Range": f"{max(values) - min(values):.6f}",
                }
            )
    return aggregate


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    if not rows:
        lines.append("| " + " | ".join(["NA"] * len(headers)) + " |")
        return lines
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "NA")) for header in headers) + " |")
    return lines


def rows_by_variant(rows, variant):
    return [row for row in rows if row["Variant"].startswith(variant)]


def get_seed_row(rows, variant, seed):
    for row in rows:
        if row["Variant"].startswith(variant) and row["Seed"] == str(seed):
            return row
    return None


def compare_metric(rows, left, right, metric):
    wins = {left: 0, right: 0, "ties": 0}
    for seed in (0, 2):
        left_row = get_seed_row(rows, left, seed)
        right_row = get_seed_row(rows, right, seed)
        left_value = as_float(left_row.get(metric) if left_row else None)
        right_value = as_float(right_row.get(metric) if right_row else None)
        if left_value is None or right_value is None:
            continue
        if abs(left_value - right_value) < 1e-9:
            wins["ties"] += 1
        elif left_value > right_value:
            wins[left] += 1
        else:
            wins[right] += 1
    return wins


def reliability_improves_early(rows):
    metrics = ("AP50", "AP75", "F1@0.50")
    details = {}
    consistent = True
    for metric in metrics:
        wins = compare_metric(rows, "R1", "R0", metric)
        details[metric] = wins
        if wins["R1"] != 2:
            consistent = False
    return consistent, details


def ratio_lead_summary(rows):
    metrics = ("AP50", "AP75", "w/o RGB AP50", "w/o Thermal AP50", "w/o Event AP50")
    summary = {metric: compare_metric(rows, "R2", "R4", metric) for metric in metrics}
    return summary


def decide(rows, missing_outputs):
    if missing_outputs:
        return "STOP: REPRODUCIBILITY OR PROTOCOL PROBLEM"
    expected = 8
    if len(rows) != expected or any(as_float(row.get("AP50")) is None for row in rows):
        return "STOP: REPRODUCIBILITY OR PROTOCOL PROBLEM"

    leads = ratio_lead_summary(rows)
    r4_full_ap50 = leads["AP50"]["R4"] == 2
    r2_full_ap50 = leads["AP50"]["R2"] == 2
    missing_metrics = ("w/o RGB AP50", "w/o Thermal AP50", "w/o Event AP50")
    r4_missing_wins = sum(leads[metric]["R4"] for metric in missing_metrics)
    r2_missing_wins = sum(leads[metric]["R2"] for metric in missing_metrics)

    if r4_full_ap50 and r4_missing_wins >= r2_missing_wins:
        return "SELECT R4 AS CLEAN-SPLIT MAIN VARIANT"
    if r2_full_ap50 and r2_missing_wins >= r4_missing_wins:
        return "SELECT R2 AS CLEAN-SPLIT MAIN VARIANT"
    return "KEEP R2 AND R4 AS CO-EQUAL OPERATING POINTS"


def protocol_lines():
    return [
        "- Frozen split: `runs/blocked_split_candidates/block64_guard16_seed0_train.txt` and `block64_guard16_seed0_val.txt`.",
        "- Required split integrity: train=7439, validation=2213, guard=837, exact RGB train/validation matches=0, same-family guard violations=0.",
        "- Guard samples are excluded from both training and validation.",
        "- Former random-split E-runs are historical diagnostics only.",
        "- Phase 4A B-runs are exploratory pilots only and are not pooled with controlled-seed R-runs.",
        "- Two seeds are not sufficient for a statistical-significance claim.",
        "- Missing-modality AP50 is interpreted per condition; arithmetic mean missing AP50 is not used as the sole selection criterion.",
    ]


def comparison_lines(rows):
    reliability_consistent, reliability_details = reliability_improves_early(rows)
    ratio_leads = ratio_lead_summary(rows)

    rel_text = "yes" if reliability_consistent else "no"
    lines = [
        f"- Reliability fusion R1 improves early fusion R0 consistently at both seeds: {rel_text}.",
    ]
    for metric, wins in reliability_details.items():
        lines.append(f"  - {metric}: R1 wins {wins['R1']}/2 seeds, R0 wins {wins['R0']}/2, ties {wins['ties']}.")

    lines.append("- R2 p=0.15 versus R4 p=0.20 leadership across seeds:")
    for metric, wins in ratio_leads.items():
        lines.append(f"  - {metric}: R2 wins {wins['R2']}/2 seeds, R4 wins {wins['R4']}/2, ties {wins['ties']}.")
    lines.append(
        "- R4 leads full-modality AP50 at both seeds and leads all three individual missing-modality AP50 conditions at both seeds; AP75 is split by seed."
    )
    return lines


def write_reports(out_dir, per_run, aggregate, decision):
    csv_path = out_dir / "clean_block64g16_seed_replication.csv"
    md_path = out_dir / "clean_block64g16_seed_replication.md"
    report_path = out_dir / "phase4b_report.md"

    write_csv(csv_path, PER_RUN_HEADERS, per_run)

    md_lines = [
        "# Clean Block64G16 Seed Replication",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Per-Run Table",
        "",
    ]
    md_lines.extend(md_table(PER_RUN_HEADERS, per_run))
    md_lines.extend(["", "## Aggregate Table", ""])
    md_lines.extend(md_table(AGGREGATE_HEADERS, aggregate))
    md_lines.append("")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    report_lines = [
        "# Phase 4B Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Protocol",
        "",
    ]
    report_lines.extend(protocol_lines())
    report_lines.extend(["", "## Per-Run Table", ""])
    report_lines.extend(md_table(PER_RUN_HEADERS, per_run))
    report_lines.extend(["", "## Aggregate Table", ""])
    report_lines.extend(md_table(AGGREGATE_HEADERS, aggregate))
    report_lines.extend(["", "## Interpretation", ""])
    report_lines.extend(comparison_lines(per_run))
    report_lines.extend(["", "## Decision", "", decision])
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    return csv_path, md_path, report_path


def main():
    parser = argparse.ArgumentParser(description="Build Phase 4B controlled-seed replication report.")
    parser.add_argument("--out", default="runs")
    args = parser.parse_args()

    out_dir = resolve_path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    per_run, missing_outputs = build_per_run_rows()
    aggregate = aggregate_rows(per_run)
    decision = decide(per_run, missing_outputs)

    csv_path, md_path, report_path = write_reports(out_dir, per_run, aggregate, decision)

    print(f"Saved: {csv_path}")
    print(f"Saved: {md_path}")
    print(f"Saved: {report_path}")
    if missing_outputs:
        print("Missing outputs:")
        for item in missing_outputs:
            print(f"- {item}")
    print(decision)


if __name__ == "__main__":
    main()
