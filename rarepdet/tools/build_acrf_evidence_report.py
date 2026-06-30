#!/usr/bin/env python
"""Build the Phase 2B ACRF evidence report."""

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
    number = as_float(value, default=None)
    if number is None:
        return "NA"
    return f"{number:.6f}"


def f1(p, r):
    p = as_float(p)
    r = as_float(r)
    return 0.0 if p + r <= 0 else 2 * p * r / (p + r)


def find_row(rows, key, value):
    for row in rows:
        if row.get(key) == value:
            return row
    return {}


def e5_eval_row():
    values = read_key_values("runs/E5_acrf_dropout015_repvit_fcos_e50/eval_thr050/eval_results.txt")
    return {
        "Precision": fmt(values.get("Precision")),
        "Recall": fmt(values.get("Recall")),
        "F1": f"{f1(values.get('Precision'), values.get('Recall')):.6f}",
        "AP50": fmt(values.get("AP50")),
        "AP75": fmt(values.get("AP75")),
    }


def config_params(path):
    values = read_key_values(path)
    return values.get("params", "NA")


def main():
    phase2a = read_csv("runs/phase2a_main_results.csv")
    missing_summary = read_csv("runs/missing_modality_summary.csv")
    e5_missing = read_csv("runs/E5_acrf_dropout015_repvit_fcos_e50/missing_modality/missing_modality_results.csv")
    e5_alpha = read_csv("runs/E5_acrf_dropout015_repvit_fcos_e50/alpha_modes/alpha_mode_summary.csv")

    e1_main = find_row(phase2a, "Method", "E1 Reliability Fusion")
    e2_main = find_row(phase2a, "Method", "E2 Reliability + Dropout 0.15")
    e5_main = e5_eval_row()

    e1_missing = find_row(missing_summary, "Method", "E1 Reliability Fusion")
    e2_missing = find_row(missing_summary, "Method", "E2 Reliability + Dropout 0.15")
    e5_missing_by_mode = {row.get("Mode"): row for row in e5_missing}

    rows = [
        {
            "Method": "E1 Reliability Fusion",
            "Params": config_params("runs/E1_reliability_repvit_fcos_e50/config.txt"),
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
            "Params": config_params("runs/E2_reliability_dropout015_repvit_fcos_e50/config.txt"),
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
            "Params": config_params("runs/E5_acrf_dropout015_repvit_fcos_e50/config.txt"),
            "Full AP50": e5_main.get("AP50", "NA"),
            "Full AP75": e5_main.get("AP75", "NA"),
            "P@0.50": e5_main.get("Precision", "NA"),
            "R@0.50": e5_main.get("Recall", "NA"),
            "F1@0.50": e5_main.get("F1", "NA"),
            "w/o RGB AP50": fmt(e5_missing_by_mode.get("no_rgb", {}).get("AP50")),
            "w/o Thermal AP50": fmt(e5_missing_by_mode.get("no_thermal", {}).get("AP50")),
            "w/o Event AP50": fmt(e5_missing_by_mode.get("no_event", {}).get("AP50")),
        },
    ]

    for row in rows:
        values = [as_float(row["w/o RGB AP50"]), as_float(row["w/o Thermal AP50"]), as_float(row["w/o Event AP50"])]
        row["Mean Missing-Modality AP50"] = f"{sum(values) / 3:.6f}"

    headers = [
        "Method",
        "Params",
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
    out_csv = PROJECT_ROOT / "runs" / "acrf_evidence_summary.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    e2 = rows[1]
    e5 = rows[2]
    param_increase = as_float(e5["Params"]) - as_float(e2["Params"])
    e5_alpha_zero = True
    for row in e5_alpha:
        mode = row.get("Mode")
        if mode == "no_rgb":
            e5_alpha_zero &= as_float(row.get("alpha_rgb_mean")) <= 1e-7
        elif mode == "no_thermal":
            e5_alpha_zero &= as_float(row.get("alpha_thermal_mean")) <= 1e-7
        elif mode == "no_event":
            e5_alpha_zero &= as_float(row.get("alpha_event_mean")) <= 1e-7

    answers = [
        (
            "Does E5 maintain or improve E2 full-modality AP50/AP75?",
            "Yes" if as_float(e5["Full AP50"]) >= as_float(e2["Full AP50"]) and as_float(e5["Full AP75"]) >= as_float(e2["Full AP75"]) else "No; keep wording conservative.",
        ),
        (
            "Does E5 improve the three missing-modality AP50 values, particularly w/o Thermal?",
            "Yes" if all(as_float(e5[k]) >= as_float(e2[k]) for k in ("w/o RGB AP50", "w/o Thermal AP50", "w/o Event AP50")) else "Mixed; inspect the table before claiming robustness improvement.",
        ),
        ("Are absent-modality alpha values actually zero in E5?", "Yes" if e5_alpha_zero else "No"),
        ("Is the parameter increase <=0.03M?", "Yes" if param_increase <= 30000 else "No"),
        (
            "Should E5 replace E2 as the paper main model, or remain an ablation?",
            "Replace E2 only if both full-modality and missing-modality metrics are maintained or improved; otherwise present E5 as an ablation targeted at alpha correctness.",
        ),
    ]

    out_md = PROJECT_ROOT / "runs" / "acrf_evidence_report.md"
    lines = [
        "# ACRF Evidence Report",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "NA")) for header in headers) + " |")
    lines.extend(["", "## Required Answers", ""])
    for question, answer in answers:
        lines.append(f"- {question} {answer}")
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {out_csv}")
    print(f"Saved: {out_md}")


if __name__ == "__main__":
    main()
