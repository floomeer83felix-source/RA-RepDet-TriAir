#!/usr/bin/env python
"""Summarize RarePDet run folders into txt/csv/md tables."""

import argparse
import csv
from pathlib import Path
import re
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]


FIELDS = [
    "Method",
    "Best Epoch",
    "Precision",
    "Recall",
    "AP50",
    "AP75",
    "GT boxes",
    "Predictions",
    "Mean Confidence",
    "Params",
    "GFLOPs",
    "FPS",
]


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def warn(message):
    print(f"WARNING: {message}", file=sys.stderr)


def parse_key_value_file(path):
    values = {}
    if not path.is_file():
        warn(f"missing {path}")
        return values
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def parse_best_epoch(train_log):
    if not train_log.is_file():
        warn(f"missing {train_log}")
        return "NA", "NA"
    text = train_log.read_text(encoding="utf-8", errors="replace")
    matches = re.findall(r"epoch\s+(\d+)\s+validation\s+Precision=([0-9.]+)\s+Recall=([0-9.]+)\s+AP50=([0-9.]+)", text)
    if not matches:
        return "NA", "NA"
    best = max(matches, key=lambda item: float(item[3]))
    return best[0], best[3]


def parse_run(run_dir):
    run_dir = resolve_path(run_dir)
    eval_values = parse_key_value_file(run_dir / "eval" / "eval_results.txt")
    config_values = parse_key_value_file(run_dir / "config.txt")
    train_values = parse_key_value_file(run_dir / "train_log.txt")
    best_epoch, _ = parse_best_epoch(run_dir / "train_log.txt")

    row = {field: "NA" for field in FIELDS}
    row["Method"] = run_dir.name
    row["Best Epoch"] = best_epoch
    for key in ("Precision", "Recall", "AP50", "AP75", "GT boxes", "Predictions", "Mean Confidence"):
        row[key] = eval_values.get(key, "NA")
    row["Params"] = config_values.get("params", train_values.get("params", "NA"))
    row["GFLOPs"] = config_values.get("gflops", train_values.get("gflops", "NA"))
    row["FPS"] = eval_values.get("FPS", train_values.get("eval_fps", "NA"))
    return row


def write_tables(rows, out_txt):
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    out_csv = out_txt.with_suffix(".csv")
    out_md = out_txt.with_suffix(".md")

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    with out_md.open("w", encoding="utf-8") as f:
        md_fields = ["Method", "Precision", "Recall", "AP50", "AP75", "Params", "GFLOPs", "FPS"]
        f.write(" | ".join(md_fields) + "\n")
        f.write(" | ".join(["---"] * len(md_fields)) + "\n")
        for row in rows:
            f.write(" | ".join(str(row.get(field, "NA")) for field in md_fields) + "\n")

    with out_txt.open("w", encoding="utf-8") as f:
        f.write("RarePDet run summary\n")
        f.write("====================\n\n")
        f.write(" | ".join(FIELDS) + "\n")
        f.write(" | ".join(["---"] * len(FIELDS)) + "\n")
        for row in rows:
            f.write(" | ".join(str(row.get(field, "NA")) for field in FIELDS) + "\n")

    return out_txt, out_csv, out_md


def main():
    parser = argparse.ArgumentParser(description="Summarize RarePDet runs.")
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--out", default="runs/summary_first_batch.txt")
    args = parser.parse_args()

    rows = [parse_run(run) for run in args.runs]
    paths = write_tables(rows, resolve_path(args.out))
    for path in paths:
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()
