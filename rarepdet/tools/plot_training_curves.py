#!/usr/bin/env python
"""Plot training curves from RarePDet train_log.txt files."""

import argparse
import csv
from pathlib import Path
import re
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def parse_log(run_dir):
    run_dir = resolve_path(run_dir)
    log_path = run_dir / "train_log.txt"
    rows = []
    if not log_path.is_file():
        print(f"WARNING: missing {log_path}", file=sys.stderr)
        return rows
    text = log_path.read_text(encoding="utf-8", errors="replace")
    method = run_dir.name
    for line in text.splitlines():
        m = re.search(r"epoch\s+(\d+)/(\d+)\s+iter\s+(\d+)/(\d+)\s+loss=([0-9.]+)", line)
        if m:
            epoch, _, iteration, total_iter, loss = m.groups()
            x = int(epoch) + int(iteration) / max(int(total_iter), 1)
            rows.append({"method": method, "kind": "train", "x": x, "epoch": int(epoch), "loss": float(loss)})
            continue
        m = re.search(
            r"epoch\s+(\d+)\s+validation\s+Precision=([0-9.]+)\s+Recall=([0-9.]+)\s+AP50=([0-9.]+)",
            line,
        )
        if m:
            epoch, precision, recall, ap50 = m.groups()
            rows.append(
                {
                    "method": method,
                    "kind": "val",
                    "x": int(epoch),
                    "epoch": int(epoch),
                    "precision": float(precision),
                    "recall": float(recall),
                    "ap50": float(ap50),
                }
            )
    return rows


def save_plot(rows, out_dir, metric, filename):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"WARNING: matplotlib unavailable, skipping {filename}: {exc}", file=sys.stderr)
        return

    plt.figure(figsize=(8, 5))
    methods = sorted({row["method"] for row in rows if metric in row})
    for method in methods:
        points = sorted([row for row in rows if row["method"] == method and metric in row], key=lambda row: row["x"])
        if not points:
            continue
        plt.plot([row["x"] for row in points], [row[metric] for row in points], label=method)
    plt.xlabel("Epoch")
    plt.ylabel(metric)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / filename, dpi=180)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Plot RarePDet training curves.")
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--out", default="runs/training_curves")
    args = parser.parse_args()

    out_dir = resolve_path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for run in args.runs:
        rows.extend(parse_log(run))

    csv_path = out_dir / "parsed_metrics.csv"
    fieldnames = ["method", "kind", "x", "epoch", "loss", "precision", "recall", "ap50"]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})

    save_plot(rows, out_dir, "loss", "loss_curve.png")
    save_plot(rows, out_dir, "ap50", "ap50_curve.png")
    save_plot(rows, out_dir, "precision", "precision_curve.png")
    save_plot(rows, out_dir, "recall", "recall_curve.png")
    print(f"Saved parsed metrics and plots to: {out_dir}")


if __name__ == "__main__":
    main()
