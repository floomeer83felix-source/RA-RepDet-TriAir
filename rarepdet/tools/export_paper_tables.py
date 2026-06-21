#!/usr/bin/env python
"""Export paper-ready markdown/csv tables from RarePDet result CSV files."""

import argparse
import csv
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def read_csv(path):
    path = resolve_path(path)
    if not path.is_file():
        print(f"WARNING: missing {path}; using empty table", file=sys.stderr)
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def fmt(value):
    if value in (None, "", "NA"):
        return "NA"
    try:
        return f"{float(value):.3f}"
    except Exception:
        return str(value)


def infer_fusion(method):
    name = method.lower()
    if "dropout" in name:
        return "Reliability + Dropout"
    if "reliability" in name:
        return "Reliability"
    return "Early"


def infer_dropout(method):
    return "0.15" if "dropout015" in method.lower() or "dropout 0.15" in method.lower() else "0"


def write_table(out_dir, name, fields, rows):
    csv_path = out_dir / f"{name}.csv"
    md_path = out_dir / f"{name}.md"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with md_path.open("w", encoding="utf-8") as f:
        f.write(" | ".join(fields) + "\n")
        f.write(" | ".join(["---"] * len(fields)) + "\n")
        for row in rows:
            f.write(" | ".join(str(row.get(field, "NA")) for field in fields) + "\n")


def build_main(summary_rows, profile_rows):
    profile_by_method = {row.get("Model", row.get("Method", "")): row for row in profile_rows}
    rows = []
    for row in summary_rows:
        method = row.get("Method", "NA")
        profile = profile_by_method.get(method, {})
        rows.append(
            {
                "Method": method,
                "Backbone": "RepViT-M0.9",
                "Fusion": infer_fusion(method),
                "Params": row.get("Params", profile.get("Params", "NA")),
                "GFLOPs": fmt(row.get("GFLOPs", profile.get("GFLOPs", "NA"))),
                "FPS": fmt(row.get("FPS", profile.get("FPS", "NA"))),
                "Precision": fmt(row.get("Precision")),
                "Recall": fmt(row.get("Recall")),
                "AP50": fmt(row.get("AP50")),
                "AP75": fmt(row.get("AP75")),
            }
        )
    return rows


def build_ablation(summary_rows):
    rows = []
    for row in summary_rows:
        method = row.get("Method", "NA")
        rows.append(
            {
                "Method": method,
                "Reliability Fusion": "Yes" if "reliability" in method.lower() else "No",
                "Modality Dropout": infer_dropout(method),
                "Precision": fmt(row.get("Precision")),
                "Recall": fmt(row.get("Recall")),
                "AP50": fmt(row.get("AP50")),
                "AP75": fmt(row.get("AP75")),
            }
        )
    return rows


def build_missing(missing_rows):
    if not missing_rows:
        return []
    mode_map = {
        "full": "Full",
        "no_rgb": "w/o RGB",
        "no_thermal": "w/o Thermal",
        "no_event": "w/o Event",
        "rgb_only": "RGB only",
        "thermal_only": "Thermal only",
        "event_only": "Event only",
    }
    row = {"Method": missing_rows[0].get("Method", missing_rows[0].get("Model", "RarePDet"))}
    for item in missing_rows:
        label = mode_map.get(item.get("Mode", ""), item.get("Mode", "NA"))
        row[label] = fmt(item.get("AP50"))
    for label in mode_map.values():
        row.setdefault(label, "NA")
    return [row]


def main():
    parser = argparse.ArgumentParser(description="Export paper tables from result CSVs.")
    parser.add_argument("--summary-csv", required=True)
    parser.add_argument("--missing-csv", required=True)
    parser.add_argument("--profile-csv", required=True)
    parser.add_argument("--out-dir", default="runs/paper_tables")
    args = parser.parse_args()

    out_dir = resolve_path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = read_csv(args.summary_csv)
    missing_rows = read_csv(args.missing_csv)
    profile_rows = read_csv(args.profile_csv)

    write_table(
        out_dir,
        "table_main_comparison",
        ["Method", "Backbone", "Fusion", "Params", "GFLOPs", "FPS", "Precision", "Recall", "AP50", "AP75"],
        build_main(summary_rows, profile_rows),
    )
    write_table(
        out_dir,
        "table_ablation",
        ["Method", "Reliability Fusion", "Modality Dropout", "Precision", "Recall", "AP50", "AP75"],
        build_ablation(summary_rows),
    )
    write_table(
        out_dir,
        "table_missing_modality",
        ["Method", "Full", "w/o RGB", "w/o Thermal", "w/o Event", "RGB only", "Thermal only", "Event only"],
        build_missing(missing_rows),
    )
    print(f"Saved paper tables to: {out_dir}")


if __name__ == "__main__":
    main()
