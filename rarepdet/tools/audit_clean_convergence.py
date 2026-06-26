#!/usr/bin/env python
"""Audit validation AP50 trajectories for controlled clean-split R runs."""

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"


RUNS = [
    ("R0 Early Fusion", "0", RUNS_DIR / "R0_early_seed0_block64g16_e50"),
    ("R0 Early Fusion", "2", RUNS_DIR / "R0_early_seed2_block64g16_e50"),
    ("R1 Reliability p=0.00", "0", RUNS_DIR / "R1_reliability_p000_seed0_block64g16_e50"),
    ("R1 Reliability p=0.00", "2", RUNS_DIR / "R1_reliability_p000_seed2_block64g16_e50"),
    ("R2 Reliability p=0.15", "0", RUNS_DIR / "R2_reliability_p015_seed0_block64g16_e50"),
    ("R2 Reliability p=0.15", "2", RUNS_DIR / "R2_reliability_p015_seed2_block64g16_e50"),
    ("R4 Reliability p=0.20", "0", RUNS_DIR / "R4_reliability_p020_seed0_block64g16_e50"),
    ("R4 Reliability p=0.20", "2", RUNS_DIR / "R4_reliability_p020_seed2_block64g16_e50"),
]

HEADERS = [
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

VAL_RE = re.compile(
    r"epoch\s+(?P<epoch>\d+)\s+validation\s+"
    r"Precision=(?P<precision>[0-9.]+)\s+"
    r"Recall=(?P<recall>[0-9.]+)\s+"
    r"AP50=(?P<ap50>[0-9.]+)\s+"
    r"AP75=(?P<ap75>[0-9.]+)"
)


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def parse_log(path):
    if not path.exists():
        return {}
    epochs = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = VAL_RE.search(line)
        if not match:
            continue
        epoch = int(match.group("epoch"))
        epochs[epoch] = float(match.group("ap50"))
    return epochs


def fmt(value):
    return "NA" if value is None else f"{value:.6f}"


def classify_status(best_epoch, ap40, ap50, final_max):
    if best_epoch is None or ap40 is None or ap50 is None:
        return "NA"
    delta = ap50 - ap40
    if best_epoch >= 46 and delta > 0.002:
        return "TAIL_STILL_IMPROVING"
    if abs(delta) <= 0.003 and (final_max - ap50) <= 0.003:
        return "CLEARLY_PLATEAUED"
    if best_epoch < 46 and delta <= 0.003:
        return "CLEARLY_PLATEAUED"
    return "NEAR_PLATEAU"


def build_rows():
    rows = []
    for variant, seed, run_dir in RUNS:
        epochs = parse_log(run_dir / "train_log.txt")
        if epochs:
            best_epoch = max(epochs, key=lambda epoch: epochs[epoch])
            best_ap50 = epochs[best_epoch]
            final_values = [epochs[epoch] for epoch in range(46, 51) if epoch in epochs]
            final_max = max(final_values) if final_values else best_ap50
        else:
            best_epoch = None
            best_ap50 = None
            final_max = None

        ap40 = epochs.get(40)
        ap45 = epochs.get(45)
        ap50 = epochs.get(50)
        delta = None if ap40 is None or ap50 is None else ap50 - ap40
        best_in_final = "NA" if best_epoch is None else str(best_epoch >= 46).lower()
        status = classify_status(best_epoch, ap40, ap50, final_max)
        rows.append(
            {
                "Variant": variant,
                "Seed": seed,
                "Best Epoch": "NA" if best_epoch is None else best_epoch,
                "Best AP50": fmt(best_ap50),
                "AP50 Epoch 40": fmt(ap40),
                "AP50 Epoch 45": fmt(ap45),
                "AP50 Epoch 50": fmt(ap50),
                "Delta AP50 40->50": fmt(delta),
                "Best In Final Five": best_in_final,
                "Status": status,
            }
        )
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def md_table(rows):
    lines = [
        "| " + " | ".join(HEADERS) + " |",
        "| " + " | ".join(["---"] * len(HEADERS)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "NA")) for header in HEADERS) + " |")
    return lines


def write_md(path, rows):
    counts = {}
    for row in rows:
        counts[row["Status"]] = counts.get(row["Status"], 0) + 1
    lines = [
        "# Clean Block64G16 Convergence Audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This audit reads existing R-run `train_log.txt` files only. It does not retrain and does not claim convergence solely because epoch 50 is the best checkpoint.",
        "",
        "## Summary",
        "",
    ]
    for key in ("CLEARLY_PLATEAUED", "NEAR_PLATEAU", "TAIL_STILL_IMPROVING", "NA"):
        if key in counts:
            lines.append(f"- {key}: {counts[key]}")
    lines.extend(["", "## Per-Run Audit", ""])
    lines.extend(md_table(rows))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `CLEARLY_PLATEAUED` means the late-epoch AP50 trajectory is flat or below earlier best values.",
            "- `NEAR_PLATEAU` means the late trajectory is mostly stable but not decisively flat.",
            "- `TAIL_STILL_IMPROVING` flags a descriptive late upward trend that may justify a reviewer-requested extension.",
            "- The fixed 50-epoch schedule should be disclosed for the clean-split controlled comparison.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Audit clean-split R-run convergence from train logs.")
    parser.add_argument("--out-dir", default="runs")
    args = parser.parse_args()

    out_dir = resolve_path(args.out_dir)
    rows = build_rows()
    csv_path = out_dir / "clean_block64g16_convergence.csv"
    md_path = out_dir / "clean_block64g16_convergence.md"
    write_csv(csv_path, rows)
    write_md(md_path, rows)
    print(f"Saved: {csv_path}")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()
