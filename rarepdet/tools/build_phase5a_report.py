#!/usr/bin/env python
"""Build Phase 5A paper-readiness report and summary CSV."""

import argparse
import csv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def read_csv(path):
    path = resolve_path(path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    path = resolve_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(rows[0].keys()) if rows else ["Section", "Item", "Status", "Value", "Notes"]
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


def md_table(rows, headers=None):
    if headers is None:
        headers = list(rows[0].keys()) if rows else []
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


def yolo_rows():
    rows = []
    for seed in ("0", "2"):
        path = RUNS_DIR / f"Y11n_rgb_seed{seed}_block64g16_e50" / "eval_project" / "eval_results.csv"
        data = read_csv(path)
        if data:
            rows.append(data[0])
    return rows


def aggregate_yolo(rows):
    if not rows:
        return []
    metrics = ["Precision", "Recall", "F1", "AP50", "AP75", "Predictions", "Mean Confidence"]
    out = []
    for metric in metrics:
        values = [as_float(row.get(metric)) for row in rows]
        values = [value for value in values if value is not None]
        if not values:
            continue
        out.append(
            {
                "Metric": metric,
                "Mean": fmt(sum(values) / len(values)),
                "Min": fmt(min(values)),
                "Max": fmt(max(values)),
                "Range": fmt(max(values) - min(values)),
            }
        )
    return out


def summarize_convergence(rows):
    counts = {}
    for row in rows:
        counts[row.get("Status", "NA")] = counts.get(row.get("Status", "NA"), 0) + 1
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts)) if counts else "NA"


def summarize_qualitative(rows):
    counts = {}
    for row in rows:
        counts[row.get("Category", "NA")] = counts.get(row.get("Category", "NA"), 0) + 1
    return "; ".join(f"{key}: {counts[key]}" for key in sorted(counts)) if counts else "NA"


def blocker_is_current():
    path = PROJECT_ROOT / "docs" / "TASK_BLOCKER.md"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return "Resolved:" not in text


def required_status():
    required = {
        "Phase 4B report": RUNS_DIR / "phase4b_report.md",
        "Seed replication table": RUNS_DIR / "clean_block64g16_seed_replication.csv",
        "Convergence audit": RUNS_DIR / "clean_block64g16_convergence.csv",
        "Efficiency profile": RUNS_DIR / "clean_efficiency_profile.csv",
        "R4 reliability audit": RUNS_DIR / "r4_reliability_weight_audit.csv",
        "Qualitative manifest": RUNS_DIR / "clean_qualitative_manifest.csv",
        "YOLO protocol": RUNS_DIR / "yolo11n_rgb_baseline_protocol.md",
        "YOLO seed0 eval": RUNS_DIR / "Y11n_rgb_seed0_block64g16_e50" / "eval_project" / "eval_results.csv",
        "YOLO seed2 eval": RUNS_DIR / "Y11n_rgb_seed2_block64g16_e50" / "eval_project" / "eval_results.csv",
    }
    rows = []
    for name, path in required.items():
        rows.append(
            {
                "Section": "Required Output",
                "Item": name,
                "Status": "present" if path.exists() else "missing",
                "Value": str(path),
                "Notes": "",
            }
        )
    rows.append(
        {
            "Section": "Protocol",
            "Item": "Current blocker",
            "Status": "present" if blocker_is_current() else "none",
            "Value": "docs/TASK_BLOCKER.md" if blocker_is_current() else "NA",
            "Notes": "Old resolved blocker files do not block Phase 5A.",
        }
    )
    return rows


def build_summary_rows(r_rows, y_rows, y_agg, conv_rows, eff_rows, alpha_rows, qual_rows, decision):
    rows = required_status()
    r4_ap50 = [as_float(row.get("AP50")) for row in r_rows if row.get("Variant") == "R4 Reliability p=0.20"]
    rows.append(
        {
            "Section": "Clean split main variant",
            "Item": "R4 Full AP50 mean",
            "Status": "complete" if r4_ap50 else "NA",
            "Value": fmt(sum(r4_ap50) / len(r4_ap50)) if r4_ap50 else "NA",
            "Notes": "R4 is marked as main variant by Phase 4B.",
        }
    )
    for row in y_rows:
        rows.append(
            {
                "Section": "YOLO11n RGB-only",
                "Item": f"Seed {row.get('Seed')}",
                "Status": "complete",
                "Value": f"AP50={row.get('AP50')} AP75={row.get('AP75')} F1={row.get('F1')}",
                "Notes": "External RGB-only baseline; not an architecture-only ablation.",
            }
        )
    rows.append(
        {
            "Section": "Convergence",
            "Item": "R-run audit",
            "Status": "complete" if conv_rows else "NA",
            "Value": summarize_convergence(conv_rows),
            "Notes": "Descriptive only; no retraining triggered.",
        }
    )
    rows.append(
        {
            "Section": "Efficiency",
            "Item": "Clean profile rows",
            "Status": "complete" if eff_rows else "NA",
            "Value": len(eff_rows),
            "Notes": "Current-code profile, batch 1, 100 warmup, 300 iters, 3 repeats.",
        }
    )
    rows.append(
        {
            "Section": "Reliability audit",
            "Item": "R4 alpha rows",
            "Status": "complete" if alpha_rows else "NA",
            "Value": len(alpha_rows),
            "Notes": "Synthetic modality removal gating behavior only.",
        }
    )
    rows.append(
        {
            "Section": "Qualitative",
            "Item": "Manifest rows",
            "Status": "complete" if len(qual_rows) == 20 else "incomplete",
            "Value": len(qual_rows),
            "Notes": summarize_qualitative(qual_rows),
        }
    )
    rows.append({"Section": "Decision", "Item": "Phase 5A gate", "Status": decision, "Value": decision, "Notes": ""})
    return rows


def decision(rows):
    missing = [row for row in rows if row["Section"] == "Required Output" and row["Status"] != "present"]
    if missing or blocker_is_current():
        return "STOP: BASELINE OR PROTOCOL BLOCKER"
    return "READY FOR MANUSCRIPT DRAFTING"


def write_report(path, r_rows, y_rows, y_agg, conv_rows, eff_rows, alpha_rows, qual_rows, summary_rows, final_decision):
    path = resolve_path(path)
    lines = [
        "# Phase 5A Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Clean-Split Main Results",
        "",
        "The table below is copied from Phase 4B controlled-seed clean-split results. R4 is the selected main variant.",
        "",
    ]
    r_headers = [
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
    marked_r_rows = []
    for row in r_rows:
        marked = dict(row)
        if marked.get("Variant") == "R4 Reliability p=0.20":
            marked["Variant"] = marked["Variant"] + " [MAIN]"
        marked_r_rows.append(marked)
    lines.extend(md_table(marked_r_rows, r_headers))

    lines.extend(["", "## YOLO11n RGB-Only External Baseline", ""])
    y_headers = [
        "Method",
        "Seed",
        "Precision",
        "Recall",
        "F1",
        "AP50",
        "AP75",
        "GT boxes",
        "Predictions",
        "Mean Confidence",
    ]
    lines.extend(md_table(y_rows, y_headers))
    lines.extend(["", "### YOLO11n Mean/Range", ""])
    lines.extend(md_table(y_agg, ["Metric", "Mean", "Min", "Max", "Range"]))

    lines.extend(["", "## Efficiency", ""])
    eff_headers = [
        "Model",
        "Path",
        "Params",
        "FPS mean",
        "Latency ms/img mean",
        "CUDA Memory MB mean",
        "Note",
    ]
    lines.extend(md_table(eff_rows, eff_headers))

    lines.extend(["", "## Convergence Audit", ""])
    conv_headers = [
        "Variant",
        "Seed",
        "Best Epoch",
        "Best AP50",
        "AP50 Epoch 40",
        "AP50 Epoch 45",
        "AP50 Epoch 50",
        "Delta AP50 40->50",
        "Best In Final Five",
        "Status",
    ]
    lines.extend(md_table(conv_rows, conv_headers))
    lines.append("")
    lines.append(f"Convergence status summary: {summarize_convergence(conv_rows)}.")

    lines.extend(["", "## Reliability-Weight Audit", ""])
    alpha_headers = [
        "Seed",
        "Mode",
        "alpha_rgb_mean",
        "alpha_thermal_mean",
        "alpha_event_mean",
        "alpha_sum_mean",
        "finite_values",
    ]
    lines.extend(md_table(alpha_rows, alpha_headers))
    lines.append("")
    lines.append(
        "Interpretation: these values describe implemented gating behavior under synthetic modality removal; they do not establish causal physical modality importance."
    )

    lines.extend(["", "## Qualitative Manifest", ""])
    lines.append(f"- Rows: {len(qual_rows)}")
    lines.append(f"- Category counts: {summarize_qualitative(qual_rows)}")
    lines.append("- Cases are illustrative only; local panels are not committed.")

    lines.extend(["", "## Publication-Safe Interpretation", ""])
    lines.append(
        "YOLO11n is reported strictly as a standard lightweight RGB-only external detector under the same clean split. "
        "It answers how the proposed full tri-modal system compares with a common RGB-only detector, but it does not isolate architecture-only benefit because the input modalities differ."
    )
    lines.append(
        "R0 versus R1/R4 remains the relevant architecture/fusion ablation within the same RepViT-FCOS detection family and tri-modal input setting."
    )

    lines.extend(["", "## Output Checklist", ""])
    lines.extend(md_table(summary_rows, ["Section", "Item", "Status", "Value", "Notes"]))
    lines.extend(["", "## Decision", "", final_decision])
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Build Phase 5A paper-readiness report.")
    parser.add_argument("--out-summary", default="runs/paper_readiness_summary.csv")
    parser.add_argument("--out-report", default="runs/phase5a_report.md")
    args = parser.parse_args()

    r_rows = read_csv(RUNS_DIR / "clean_block64g16_seed_replication.csv")
    y_rows = yolo_rows()
    y_agg = aggregate_yolo(y_rows)
    conv_rows = read_csv(RUNS_DIR / "clean_block64g16_convergence.csv")
    eff_rows = read_csv(RUNS_DIR / "clean_efficiency_profile.csv")
    alpha_rows = read_csv(RUNS_DIR / "r4_reliability_weight_audit.csv")
    qual_rows = read_csv(RUNS_DIR / "clean_qualitative_manifest.csv")
    final_decision = decision(required_status())
    summary_rows = build_summary_rows(r_rows, y_rows, y_agg, conv_rows, eff_rows, alpha_rows, qual_rows, final_decision)

    write_csv(args.out_summary, summary_rows)
    write_report(args.out_report, r_rows, y_rows, y_agg, conv_rows, eff_rows, alpha_rows, qual_rows, summary_rows, final_decision)
    print(f"Saved: {resolve_path(args.out_summary)}")
    print(f"Saved: {resolve_path(args.out_report)}")
    print(final_decision)


if __name__ == "__main__":
    main()
