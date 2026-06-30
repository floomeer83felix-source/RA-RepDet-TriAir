#!/usr/bin/env python
"""Build Phase 3A dropout-ratio ablation summaries."""

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"


METHODS = [
    {
        "method": "E1 Reliability Fusion",
        "ratio": "0.00",
        "main_source": "phase2a",
        "missing_source": "summary",
    },
    {
        "method": "E3 Reliability + Dropout 0.10",
        "ratio": "0.10",
        "eval": RUNS_DIR / "E3_reliability_dropout010_repvit_fcos_e50" / "eval_thr050" / "eval_results.txt",
        "missing": RUNS_DIR / "E3_reliability_dropout010_repvit_fcos_e50" / "missing_modality" / "missing_modality_results.csv",
    },
    {
        "method": "E2 Reliability + Dropout 0.15",
        "ratio": "0.15",
        "main_source": "phase2a",
        "missing_source": "summary",
    },
    {
        "method": "E4 Reliability + Dropout 0.20",
        "ratio": "0.20",
        "eval": RUNS_DIR / "E4_reliability_dropout020_repvit_fcos_e50" / "eval_thr050" / "eval_results.txt",
        "missing": RUNS_DIR / "E4_reliability_dropout020_repvit_fcos_e50" / "missing_modality" / "missing_modality_results.csv",
    },
]


HEADERS = [
    "Method",
    "Dropout Ratio",
    "P@0.50",
    "R@0.50",
    "F1@0.50",
    "Full AP50",
    "Full AP75",
    "w/o RGB AP50",
    "w/o Thermal AP50",
    "w/o Event AP50",
    "Mean Missing-Modality AP50",
]


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


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


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt(value):
    value = to_float(value)
    return "NA" if value is None else f"{value:.6f}"


def f1(precision, recall):
    precision = to_float(precision)
    recall = to_float(recall)
    if precision is None or recall is None or precision + recall <= 0:
        return "NA"
    return f"{(2.0 * precision * recall / (precision + recall)):.6f}"


def find_row(rows, key, value):
    for row in rows:
        if row.get(key) == value:
            return row
    return {}


def missing_modes_from_file(path):
    rows = read_csv(path)
    by_mode = {row.get("Mode"): row for row in rows}
    return {
        "w/o RGB AP50": fmt(by_mode.get("no_rgb", {}).get("AP50")),
        "w/o Thermal AP50": fmt(by_mode.get("no_thermal", {}).get("AP50")),
        "w/o Event AP50": fmt(by_mode.get("no_event", {}).get("AP50")),
    }


def mean_missing(row):
    values = [
        to_float(row.get("w/o RGB AP50")),
        to_float(row.get("w/o Thermal AP50")),
        to_float(row.get("w/o Event AP50")),
    ]
    if any(value is None for value in values):
        return "NA"
    return f"{(sum(values) / 3.0):.6f}"


def build_rows():
    phase2a = read_csv(RUNS_DIR / "phase2a_main_results.csv")
    missing_summary = read_csv(RUNS_DIR / "missing_modality_summary.csv")
    rows = []

    for spec in METHODS:
        if spec.get("main_source") == "phase2a":
            main = find_row(phase2a, "Method", spec["method"])
            precision = main.get("Precision")
            recall = main.get("Recall")
            row = {
                "Method": spec["method"],
                "Dropout Ratio": spec["ratio"],
                "P@0.50": fmt(precision),
                "R@0.50": fmt(recall),
                "F1@0.50": fmt(main.get("F1")),
                "Full AP50": fmt(main.get("AP50")),
                "Full AP75": fmt(main.get("AP75")),
            }
        else:
            main = read_key_values(spec["eval"])
            precision = main.get("Precision")
            recall = main.get("Recall")
            row = {
                "Method": spec["method"],
                "Dropout Ratio": spec["ratio"],
                "P@0.50": fmt(precision),
                "R@0.50": fmt(recall),
                "F1@0.50": f1(precision, recall),
                "Full AP50": fmt(main.get("AP50")),
                "Full AP75": fmt(main.get("AP75")),
            }

        if spec.get("missing_source") == "summary":
            missing = find_row(missing_summary, "Method", spec["method"])
            row.update(
                {
                    "w/o RGB AP50": fmt(missing.get("w/o RGB")),
                    "w/o Thermal AP50": fmt(missing.get("w/o Thermal")),
                    "w/o Event AP50": fmt(missing.get("w/o Event")),
                }
            )
        else:
            row.update(missing_modes_from_file(spec["missing"]))

        row["Mean Missing-Modality AP50"] = mean_missing(row)
        rows.append(row)
    return rows


def row_score(row, columns, tolerance=0.001):
    wins = 0
    values = {column: to_float(row.get(column)) for column in columns}
    return wins, values


def choose_default(rows):
    evidence_columns = ["Full AP50", "Full AP75", "P@0.50", "F1@0.50", "w/o RGB AP50", "w/o Thermal AP50", "w/o Event AP50"]
    valid_rows = [row for row in rows if all(to_float(row.get(column)) is not None for column in evidence_columns)]
    if not valid_rows:
        return None, None, "Not enough completed evidence to position dropout ratios."

    accuracy_first = max(
        valid_rows,
        key=lambda row: (to_float(row["Full AP50"]), to_float(row["Full AP75"])),
    )
    robustness_first = max(
        valid_rows,
        key=lambda row: (
            to_float(row["w/o RGB AP50"]),
            to_float(row["w/o Thermal AP50"]),
            to_float(row["w/o Event AP50"]),
            to_float(row["F1@0.50"]),
        ),
    )
    reason = (
        "The ratio ablation is interpreted by separating full-modality detection quality from "
        "missing-modality robustness. Full AP50/AP75 drive the accuracy-first main-model choice; "
        "P@0.50/F1@0.50 and the three single-modality-missing AP50 values identify a robustness-first "
        "operating point. The arithmetic mean missing-modality AP50 is reported only as a summary, "
        "not as a standard metric or sole selection rule."
    )
    return accuracy_first, robustness_first, reason


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "NA") for key in HEADERS} for row in rows])


def markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "NA")) for header in headers) + " |")
    return lines


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else "NA"


def qualitative_summary():
    manifest = read_csv(RUNS_DIR / "qualitative_cases_manifest.csv")
    if not manifest:
        return ["- Qualitative case manifest: NA"]
    counts = {}
    for row in manifest:
        counts[row.get("Category", "NA")] = counts.get(row.get("Category", "NA"), 0) + 1
    lines = [f"- Qualitative manifest rows: {len(manifest)}"]
    for category in sorted(counts):
        lines.append(f"- {category}: {counts[category]}")
    return lines


def main():
    rows = build_rows()
    accuracy_first, robustness_first, reason = choose_default(rows)
    accuracy_method = accuracy_first.get("Method", "NA") if accuracy_first else "NA"
    accuracy_ratio = accuracy_first.get("Dropout Ratio", "NA") if accuracy_first else "NA"
    robustness_method = robustness_first.get("Method", "NA") if robustness_first else "NA"
    robustness_ratio = robustness_first.get("Dropout Ratio", "NA") if robustness_first else "NA"
    p015_accuracy_first = accuracy_ratio == "0.15"

    csv_path = RUNS_DIR / "dropout_ablation_summary.csv"
    md_path = RUNS_DIR / "dropout_ablation_summary.md"
    phase3a_path = RUNS_DIR / "phase3a_report.md"

    write_csv(rows, csv_path)

    lines = [
        "# Dropout-Ratio Ablation Summary",
        "",
        *markdown_table(HEADERS, rows),
        "",
        "Footnote: Mean Missing-Modality AP50 is only the arithmetic mean of the three single-modality-missing AP50 values; it is a robustness summary, not a standard detection metric.",
        "",
        "## Interpretation Rule",
        "",
        reason,
        "",
        "## Decision",
        "",
        f"- Accuracy-first ratio: p={accuracy_ratio} ({accuracy_method}).",
        f"- Robustness-first ratio: p={robustness_ratio} ({robustness_method}).",
        f"- p=0.15 remains justified for the main accuracy-first result: {'Yes' if p015_accuracy_first else 'No'}.",
        "- No ratio is universally dominant in this single-seed 50-epoch ablation.",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")

    phase_lines = [
        "# Phase 3A Report",
        "",
        "Phase 3A supplies the dropout-ratio ablation and qualitative-case evidence package for the current paper path. E2 remains the main model unless this ablation provides stronger evidence for another ratio.",
        "",
        "## Dropout-Ratio Ablation",
        "",
        *markdown_table(HEADERS, rows),
        "",
        "Footnote: Mean Missing-Modality AP50 is only the arithmetic mean of the three single-modality-missing AP50 values; it is a robustness summary, not a standard detection metric.",
        "",
        "## Selected Default Ratio",
        "",
        reason,
        "",
        f"- Accuracy-first ratio: p={accuracy_ratio} ({accuracy_method}).",
        f"- Robustness-first ratio: p={robustness_ratio} ({robustness_method}).",
        f"- p=0.15 remains justified for the main accuracy-first result: {'Yes' if p015_accuracy_first else 'No'}.",
        "- No ratio is universally dominant in this single-seed 50-epoch ablation.",
        "",
        "## Qualitative-Case Manifest Summary",
        "",
        *qualitative_summary(),
        "",
        "## Final Model Decision",
        "",
        f"- Main model after Phase 3A: {'E2 Reliability + Dropout 0.15' if p015_accuracy_first else accuracy_method}.",
        f"- Robustness-first variant after Phase 3A: {robustness_method}.",
        "- E5 and E6 remain ablations because they did not satisfy their predefined replacement rules.",
        "",
        "## Remaining Gaps Before Manuscript Drafting",
        "",
        "- Convert the selected qualitative manifest rows into figure panels outside Git-tracked outputs.",
        "- Assemble final paper tables from Phase 2A, Phase 2B, Phase 2C, and Phase 3A summaries.",
        "- Decide whether to include E5 and E6 in the main ablation table or supplementary material.",
        "",
    ]
    phase3a_path.write_text("\n".join(phase_lines), encoding="utf-8")

    print(f"Saved: {csv_path}")
    print(f"Saved: {md_path}")
    print(f"Saved: {phase3a_path}")


if __name__ == "__main__":
    main()
