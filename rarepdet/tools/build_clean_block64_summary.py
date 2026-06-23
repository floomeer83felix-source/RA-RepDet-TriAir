#!/usr/bin/env python
"""Build Phase 4A clean block64/guard16 summary tables."""

import argparse
import csv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"


RUNS = [
    {
        "id": "B0",
        "method": "B0 Early Fusion",
        "dropout": "NA",
        "model_family": "early",
        "dir": RUNS_DIR / "B0_early_block64g16_e50",
        "missing_required": False,
    },
    {
        "id": "B1",
        "method": "B1 Reliability p=0.00",
        "dropout": "0.00",
        "model_family": "reliability",
        "dir": RUNS_DIR / "B1_reliability_p000_block64g16_e50",
        "missing_required": True,
    },
    {
        "id": "B2",
        "method": "B2 Reliability p=0.15",
        "dropout": "0.15",
        "model_family": "reliability",
        "dir": RUNS_DIR / "B2_reliability_p015_block64g16_e50",
        "missing_required": True,
    },
    {
        "id": "B4",
        "method": "B4 Reliability p=0.20",
        "dropout": "0.20",
        "model_family": "reliability",
        "dir": RUNS_DIR / "B4_reliability_p020_block64g16_e50",
        "missing_required": True,
    },
]


HEADERS = [
    "Method",
    "Dropout Ratio",
    "Params",
    "P@0.50",
    "R@0.50",
    "F1@0.50",
    "Full AP50",
    "Full AP75",
    "w/o RGB AP50",
    "w/o Thermal AP50",
    "w/o Event AP50",
]


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def read_key_values(path):
    path = Path(path)
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
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, headers, rows):
    path = Path(path)
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
    if precision is None or recall is None or precision + recall <= 0:
        return None
    return 2.0 * precision * recall / (precision + recall)


def load_params():
    rows = read_csv(RUNS_DIR / "profile_summary.csv")
    params = {"early": "6591609", "reliability": "6593293"}
    for row in rows:
        model = (row.get("Model") or "").lower()
        if "early" in model:
            params["early"] = row.get("Params") or params["early"]
        if "reliability" in model:
            params["reliability"] = row.get("Params") or params["reliability"]
    return params


def missing_ap(run_dir, mode):
    rows = read_csv(run_dir / "missing_modality" / "missing_modality_results.csv")
    for row in rows:
        if row.get("Mode") == mode:
            return row.get("AP50")
    return None


def build_rows():
    params = load_params()
    rows = []
    missing = []
    for run in RUNS:
        eval_values = read_key_values(run["dir"] / "eval_thr050" / "eval_results.txt")
        if not eval_values:
            missing.append(f"{run['id']} eval_thr050/eval_results.txt")
        if run["missing_required"] and not (run["dir"] / "missing_modality" / "missing_modality_results.csv").exists():
            missing.append(f"{run['id']} missing_modality/missing_modality_results.csv")
        precision = eval_values.get("Precision")
        recall = eval_values.get("Recall")
        row = {
            "Method": run["method"],
            "Dropout Ratio": run["dropout"],
            "Params": params[run["model_family"]],
            "P@0.50": fmt(precision),
            "R@0.50": fmt(recall),
            "F1@0.50": fmt(f1(precision, recall)),
            "Full AP50": fmt(eval_values.get("AP50")),
            "Full AP75": fmt(eval_values.get("AP75")),
            "w/o RGB AP50": "NA" if not run["missing_required"] else fmt(missing_ap(run["dir"], "no_rgb")),
            "w/o Thermal AP50": "NA" if not run["missing_required"] else fmt(missing_ap(run["dir"], "no_thermal")),
            "w/o Event AP50": "NA" if not run["missing_required"] else fmt(missing_ap(run["dir"], "no_event")),
        }
        rows.append(row)
    return rows, missing


def row_by_id(rows, run_id):
    for run, row in zip(RUNS, rows):
        if run["id"] == run_id:
            return row
    return None


def best_by(rows, metric, candidates):
    best = None
    for run, row in zip(RUNS, rows):
        if run["id"] not in candidates:
            continue
        value = as_float(row.get(metric))
        if value is None:
            continue
        if best is None or value > best[0]:
            best = (value, run["id"], row)
    return best


def missing_wins(rows, left_id, right_id):
    left = row_by_id(rows, left_id)
    right = row_by_id(rows, right_id)
    wins = {left_id: 0, right_id: 0, "ties": 0}
    for metric in ("w/o RGB AP50", "w/o Thermal AP50", "w/o Event AP50"):
        left_value = as_float(left.get(metric))
        right_value = as_float(right.get(metric))
        if left_value is None or right_value is None:
            continue
        if abs(left_value - right_value) < 1e-9:
            wins["ties"] += 1
        elif left_value > right_value:
            wins[left_id] += 1
        else:
            wins[right_id] += 1
    return wins


def decide_next_action(rows, missing_outputs, protocol_exists):
    if missing_outputs or not protocol_exists:
        return "STOP: CLEAN-SPLIT INTEGRITY OR TRAINING PROBLEM"
    b2 = row_by_id(rows, "B2")
    b4 = row_by_id(rows, "B4")
    if not b2 or not b4:
        return "STOP: CLEAN-SPLIT INTEGRITY OR TRAINING PROBLEM"
    b2_ap50 = as_float(b2.get("Full AP50"))
    b4_ap50 = as_float(b4.get("Full AP50"))
    if b2_ap50 is None or b4_ap50 is None:
        return "STOP: CLEAN-SPLIT INTEGRITY OR TRAINING PROBLEM"
    full_gap = abs(b2_ap50 - b4_ap50)
    wins = missing_wins(rows, "B2", "B4")
    full_leader = "B2" if b2_ap50 > b4_ap50 else "B4"
    robust_leader = "B2" if wins["B2"] > wins["B4"] else "B4" if wins["B4"] > wins["B2"] else "tie"
    if full_leader == robust_leader and full_gap >= 0.005:
        return "REPLICATE THE SINGLE LEADING VARIANT WITH SEED 2"
    return "REPLICATE B2 AND B4 WITH SEED 2"


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "NA")) for header in headers) + " |")
    return lines


def relation_statement(rows):
    b0 = row_by_id(rows, "B0")
    b1 = row_by_id(rows, "B1")
    if not b0 or not b1:
        return "Reliability-vs-early comparison is NA because one required run is missing."
    b0_ap50 = as_float(b0.get("Full AP50"))
    b1_ap50 = as_float(b1.get("Full AP50"))
    b0_f1 = as_float(b0.get("F1@0.50"))
    b1_f1 = as_float(b1.get("F1@0.50"))
    if b0_ap50 is None or b1_ap50 is None:
        return "Reliability-vs-early comparison is NA because eval output is incomplete."
    direction = "improves" if b1_ap50 > b0_ap50 else "does not improve"
    return (
        f"B1 reliability fusion {direction} B0 early fusion by Full AP50 "
        f"({b1_ap50:.6f} vs {b0_ap50:.6f}); F1 is {b1_f1:.6f} vs {b0_f1:.6f}."
    )


def ratio_statement(rows):
    full_best = best_by(rows, "Full AP50", {"B2", "B4"})
    ap75_best = best_by(rows, "Full AP75", {"B2", "B4"})
    f1_best = best_by(rows, "F1@0.50", {"B2", "B4"})
    wins = missing_wins(rows, "B2", "B4")
    if not full_best:
        return "B2/B4 ratio comparison is NA because eval output is incomplete."
    robust = "tie"
    if wins["B2"] > wins["B4"]:
        robust = "B2"
    elif wins["B4"] > wins["B2"]:
        robust = "B4"
    return (
        f"Full-modality AP50 leader: {full_best[1]} ({full_best[0]:.6f}). "
        f"AP75 leader: {ap75_best[1] if ap75_best else 'NA'}. "
        f"F1 leader: {f1_best[1] if f1_best else 'NA'}. "
        f"Missing-modality AP50 per-mode wins: B2={wins['B2']}, B4={wins['B4']}, ties={wins['ties']}; robustness leader by per-mode wins: {robust}."
    )


def main():
    parser = argparse.ArgumentParser(description="Build clean block64g16 Phase 4A summary.")
    parser.add_argument("--out", default="runs")
    args = parser.parse_args()

    out_dir = resolve_path(args.out)
    rows, missing_outputs = build_rows()
    protocol_exists = (RUNS_DIR / "clean_block64g16_protocol.md").exists()
    next_action = decide_next_action(rows, missing_outputs, protocol_exists)

    csv_path = out_dir / "clean_block64g16_summary.csv"
    md_path = out_dir / "clean_block64g16_summary.md"
    report_path = out_dir / "phase4a_report.md"
    write_csv(csv_path, HEADERS, rows)

    md_lines = [
        "# Clean Block64G16 Summary",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "All headline values in this table use the validated `block64_guard16_seed0` split only.",
        "",
    ]
    md_lines.extend(md_table(HEADERS, rows))
    md_lines.append("")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    report_lines = [
        "# Phase 4A Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Clean Split Protocol",
        "",
        "- Protocol: `runs/clean_block64g16_protocol.md`" if protocol_exists else "- Protocol: NA",
        "- Candidate: `block64_guard16_seed0`",
        "- Former random-split results are historical diagnostics only and are not mixed into this table.",
        "- This is single training-seed evidence; no statistical significance is claimed.",
        "",
        "## Main Clean-Split Table",
        "",
    ]
    report_lines.extend(md_table(HEADERS, rows))
    report_lines.extend(
        [
            "",
            "## Comparisons",
            "",
            f"- {relation_statement(rows)}",
            f"- {ratio_statement(rows)}",
            "- The dropout-ratio decision is not based on an arithmetic mean alone.",
            "",
            "## Missing Outputs",
            "",
        ]
    )
    if missing_outputs:
        report_lines.extend(f"- {item}" for item in missing_outputs)
    else:
        report_lines.append("- none")
    report_lines.extend(["", "## Next Action", "", next_action, ""])
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Saved: {csv_path}")
    print(f"Saved: {md_path}")
    print(f"Saved: {report_path}")
    print(next_action)


if __name__ == "__main__":
    main()
