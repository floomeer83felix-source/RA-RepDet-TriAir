#!/usr/bin/env python
"""Build the paper-facing Phase 2A main table at score threshold 0.50."""

import argparse

from phase2a_common import PROJECT_ROOT, format_float, markdown_table, read_csv, write_csv


def main():
    parser = argparse.ArgumentParser(description="Create Phase 2A main result table.")
    parser.add_argument("--threshold-csv", default="runs/threshold_sweep/threshold_sweep_results.csv")
    parser.add_argument("--threshold", default=0.50, type=float)
    parser.add_argument("--out-csv", default="runs/phase2a_main_results.csv")
    parser.add_argument("--out-md", default="runs/phase2a_main_results.md")
    args = parser.parse_args()

    source_rows = read_csv(args.threshold_csv)
    rows = []
    for row in source_rows:
        try:
            threshold = float(row.get("Threshold", "nan"))
        except ValueError:
            continue
        if abs(threshold - args.threshold) > 1e-9:
            continue
        rows.append(
            {
                "Method": row.get("Method", "NA"),
                "Threshold": f"{args.threshold:.2f}",
                "Precision": format_float(row.get("Precision")),
                "Recall": format_float(row.get("Recall")),
                "F1": format_float(row.get("F1")),
                "AP50": format_float(row.get("AP50")),
                "AP75": format_float(row.get("AP75")),
                "GT boxes": row.get("GT boxes", "NA"),
                "Predictions": row.get("Predictions", "NA"),
                "Mean Confidence": format_float(row.get("Mean Confidence")),
            }
        )

    headers = [
        "Method",
        "Threshold",
        "Precision",
        "Recall",
        "F1",
        "AP50",
        "AP75",
        "GT boxes",
        "Predictions",
        "Mean Confidence",
    ]
    csv_path = write_csv(args.out_csv, rows, headers)
    md_path = PROJECT_ROOT / args.out_md
    md_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 2A Main Results",
        "",
        "Paper-facing Precision, Recall, and F1 use score threshold 0.50. AP50/AP75 remain score-ranked AP values from the threshold sweep.",
        "",
    ]
    lines.extend(markdown_table(headers, rows))
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {csv_path}")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()

