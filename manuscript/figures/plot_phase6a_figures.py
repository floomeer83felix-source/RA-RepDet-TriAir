#!/usr/bin/env python
"""Render Phase 6A chart panels locally from commit-safe CSV sources."""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "local_rendered"
OUT.mkdir(parents=True, exist_ok=True)


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def mean(values):
    vals = [float(v) for v in values]
    return sum(vals) / len(vals)


def save(fig, stem):
    fig.tight_layout()
    fig.savefig(OUT / f"{stem}.png", dpi=300)
    fig.savefig(OUT / f"{stem}.pdf")
    plt.close(fig)


def plot_fig3():
    rows = read_csv(ROOT / "fig3_controlled_ablation_source.csv")
    variants = []
    for row in rows:
        if row["Variant"] not in variants:
            variants.append(row["Variant"])
    metrics = ["F1", "AP50", "AP75"]
    x = range(len(variants))
    width = 0.22
    fig, ax = plt.subplots(figsize=(9, 4.8))
    colors = ["#4C78A8", "#F58518", "#54A24B"]
    for idx, metric in enumerate(metrics):
        vals = [mean([r[metric] for r in rows if r["Variant"] == variant]) for variant in variants]
        ax.bar([p + (idx - 1) * width for p in x], vals, width=width, label=metric, color=colors[idx])
    ax.set_ylim(0.80, 1.00)
    ax.set_ylabel("Score")
    ax.set_title("Controlled clean-split two-seed comparison")
    ax.set_xticks(list(x))
    ax.set_xticklabels([v.replace(" Reliability ", "\nReliability ") for v in variants], rotation=0)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, "Fig3_controlled_ablation")


def plot_fig4():
    rows = read_csv(ROOT / "fig4_missing_modality_source.csv")
    variants = []
    conditions = ["w/o RGB", "w/o Thermal", "w/o Event"]
    for row in rows:
        if row["Variant"] not in variants:
            variants.append(row["Variant"])
    x = range(len(variants))
    width = 0.24
    fig, ax = plt.subplots(figsize=(9, 4.8))
    colors = ["#E45756", "#72B7B2", "#B279A2"]
    for idx, condition in enumerate(conditions):
        vals = [
            mean([r["AP50"] for r in rows if r["Variant"] == variant and r["Condition"] == condition])
            for variant in variants
        ]
        ax.bar([p + (idx - 1) * width for p in x], vals, width=width, label=condition, color=colors[idx])
    ax.set_ylim(0.25, 1.00)
    ax.set_ylabel("AP50")
    ax.set_title("Synthetic missing-modality robustness")
    ax.set_xticks(list(x))
    ax.set_xticklabels([v.replace(" Reliability ", "\nReliability ") for v in variants], rotation=0)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, "Fig4_missing_modality")


def plot_fig5():
    rows = read_csv(ROOT / "fig5_reliability_weight_source.csv")
    modes = ["full", "no_rgb", "no_thermal", "no_event"]
    channels = [
        ("alpha_rgb_mean", "RGB", "#4C78A8"),
        ("alpha_thermal_mean", "Thermal", "#F58518"),
        ("alpha_event_mean", "Event", "#54A24B"),
    ]
    x = range(len(modes))
    width = 0.24
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    for idx, (field, label, color) in enumerate(channels):
        vals = [mean([r[field] for r in rows if r["Mode"] == mode]) for mode in modes]
        ax.bar([p + (idx - 1) * width for p in x], vals, width=width, label=label, color=color)
    ax.set_ylim(0.0, 0.85)
    ax.set_ylabel("Mean alpha")
    ax.set_title("R4 reliability-gating audit")
    ax.set_xticks(list(x))
    ax.set_xticklabels(modes)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, "Fig5_reliability_weights")


if __name__ == "__main__":
    plot_fig3()
    plot_fig4()
    plot_fig5()
    print(f"Saved local chart outputs to {OUT}")
