#!/usr/bin/env python
"""Build the Phase 2C MSCD evidence report."""

import csv
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def read_csv(path):
    path = PROJECT_ROOT / path
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_key_values(path):
    path = PROJECT_ROOT / path
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def as_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt(value):
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return "NA"


def f1(precision, recall):
    precision = as_float(precision)
    recall = as_float(recall)
    return 0.0 if precision + recall <= 0 else 2 * precision * recall / (precision + recall)


def find_row(rows, key, value):
    for row in rows:
        if row.get(key) == value:
            return row
    return {}


def config_value(path, key):
    return read_key_values(path).get(key, "NA")


def eval_row(path):
    values = read_key_values(path)
    return {
        "Precision": fmt(values.get("Precision")),
        "Recall": fmt(values.get("Recall")),
        "F1": f"{f1(values.get('Precision'), values.get('Recall')):.6f}",
        "AP50": fmt(values.get("AP50")),
        "AP75": fmt(values.get("AP75")),
    }


def missing_by_mode(path):
    return {row.get("Mode"): row for row in read_csv(path)}


def mean_missing(row):
    values = [as_float(row["w/o RGB AP50"]), as_float(row["w/o Thermal AP50"]), as_float(row["w/o Event AP50"])]
    return f"{sum(values) / 3:.6f}"


def main():
    phase2a = read_csv("runs/phase2a_main_results.csv")
    missing_summary = read_csv("runs/missing_modality_summary.csv")
    acrf = read_csv("runs/acrf_evidence_summary.csv")
    e6_eval = eval_row("runs/E6_mscd_dropout015_repvit_fcos_e50/eval_thr050/eval_results.txt")
    e6_missing = missing_by_mode("runs/E6_mscd_dropout015_repvit_fcos_e50/missing_modality/missing_modality_results.csv")

    e1_main = find_row(phase2a, "Method", "E1 Reliability Fusion")
    e2_main = find_row(phase2a, "Method", "E2 Reliability + Dropout 0.15")
    e1_missing = find_row(missing_summary, "Method", "E1 Reliability Fusion")
    e2_missing = find_row(missing_summary, "Method", "E2 Reliability + Dropout 0.15")
    e5_row = find_row(acrf, "Method", "E5 ACRF + Dropout 0.15")

    rows = [
        {
            "Method": "E1 Reliability Fusion",
            "Extra inference params": "0",
            "Full AP50": e1_main.get("AP50", "NA"),
            "Full AP75": e1_main.get("AP75", "NA"),
            "P@0.50": e1_main.get("Precision", "NA"),
            "R@0.50": e1_main.get("Recall", "NA"),
            "F1@0.50": e1_main.get("F1", "NA"),
            "w/o RGB AP50": e1_missing.get("w/o RGB", "NA"),
            "w/o Thermal AP50": e1_missing.get("w/o Thermal", "NA"),
            "w/o Event AP50": e1_missing.get("w/o Event", "NA"),
        },
        {
            "Method": "E2 Reliability + Dropout 0.15",
            "Extra inference params": "0",
            "Full AP50": e2_main.get("AP50", "NA"),
            "Full AP75": e2_main.get("AP75", "NA"),
            "P@0.50": e2_main.get("Precision", "NA"),
            "R@0.50": e2_main.get("Recall", "NA"),
            "F1@0.50": e2_main.get("F1", "NA"),
            "w/o RGB AP50": e2_missing.get("w/o RGB", "NA"),
            "w/o Thermal AP50": e2_missing.get("w/o Thermal", "NA"),
            "w/o Event AP50": e2_missing.get("w/o Event", "NA"),
        },
        {
            "Method": "E5 ACRF + Dropout 0.15",
            "Extra inference params": "48",
            "Full AP50": e5_row.get("Full AP50", "NA"),
            "Full AP75": e5_row.get("Full AP75", "NA"),
            "P@0.50": e5_row.get("P@0.50", "NA"),
            "R@0.50": e5_row.get("R@0.50", "NA"),
            "F1@0.50": e5_row.get("F1@0.50", "NA"),
            "w/o RGB AP50": e5_row.get("w/o RGB AP50", "NA"),
            "w/o Thermal AP50": e5_row.get("w/o Thermal AP50", "NA"),
            "w/o Event AP50": e5_row.get("w/o Event AP50", "NA"),
        },
        {
            "Method": "E6 MSCD + Dropout 0.15",
            "Extra inference params": config_value("runs/E6_mscd_dropout015_repvit_fcos_e50/config.txt", "extra_inference_params"),
            "Full AP50": e6_eval["AP50"],
            "Full AP75": e6_eval["AP75"],
            "P@0.50": e6_eval["Precision"],
            "R@0.50": e6_eval["Recall"],
            "F1@0.50": e6_eval["F1"],
            "w/o RGB AP50": fmt(e6_missing.get("no_rgb", {}).get("AP50")),
            "w/o Thermal AP50": fmt(e6_missing.get("no_thermal", {}).get("AP50")),
            "w/o Event AP50": fmt(e6_missing.get("no_event", {}).get("AP50")),
        },
    ]

    for row in rows:
        row["Mean Missing-Modality AP50"] = mean_missing(row)

    e2 = rows[1]
    e5 = rows[2]
    e6 = rows[3]
    e6_keeps_full = as_float(e6["Full AP50"]) >= as_float(e2["Full AP50"]) - 0.001
    e6_improves_missing = as_float(e6["Mean Missing-Modality AP50"]) > as_float(e2["Mean Missing-Modality AP50"])
    e6_improves_full = as_float(e6["Full AP50"]) > as_float(e2["Full AP50"]) or as_float(e6["Full AP75"]) > as_float(e2["Full AP75"])
    replace_e2 = (e6_keeps_full and e6_improves_missing) or e6_improves_full

    headers = [
        "Method",
        "Extra inference params",
        "Full AP50",
        "Full AP75",
        "P@0.50",
        "R@0.50",
        "F1@0.50",
        "w/o RGB AP50",
        "w/o Thermal AP50",
        "w/o Event AP50",
        "Mean Missing-Modality AP50",
    ]
    out_csv = PROJECT_ROOT / "runs" / "mscd_evidence_summary.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# MSCD Evidence Report",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "NA")) for header in headers) + " |")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- E6 keeps full AP50 within 0.001 of E2: {'Yes' if e6_keeps_full else 'No'}",
            f"- E6 improves mean missing-modality AP50 over E2: {'Yes' if e6_improves_missing else 'No'}",
            f"- E6 improves full AP50 or AP75 outright: {'Yes' if e6_improves_full else 'No'}",
            f"- Decision: {'E6 can replace E2 under the stated rule.' if replace_e2 else 'E2 remains the paper main model; E6 is a training-strategy ablation.'}",
            "",
        ]
    )
    out_md = PROJECT_ROOT / "runs" / "mscd_evidence_report.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")

    phase2c = [
        "# Phase 2C Report",
        "",
        "Phase 2C evaluated MSCD as a training-only consistency-distillation strategy. E6 uses the same reliability-fusion inference architecture as E2, with zero extra inference parameters.",
        "",
        "## E5 And E6 Decision Summary",
        "",
        f"- E5 ACRF: exact absent-modality alpha suppression, but full AP50/AP75 are below E2. Keep as an alpha-correctness ablation.",
        f"- E6 MSCD: {'meets' if replace_e2 else 'does not meet'} the predefined replacement rule for E2.",
        f"- Recommended main model: {'E6 MSCD' if replace_e2 else 'E2 Reliability + Dropout 0.15'}.",
        "",
        "## Evidence Table",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        phase2c.append("| " + " | ".join(str(row.get(header, "NA")) for header in headers) + " |")
    phase2c.append("")
    out_phase2c = PROJECT_ROOT / "runs" / "phase2c_report.md"
    out_phase2c.write_text("\n".join(phase2c), encoding="utf-8")

    print(f"Saved: {out_csv}")
    print(f"Saved: {out_md}")
    print(f"Saved: {out_phase2c}")


if __name__ == "__main__":
    main()
