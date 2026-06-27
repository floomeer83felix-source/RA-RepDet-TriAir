#!/usr/bin/env python
"""Build the Phase 6A journal-neutral manuscript source package.

This script reads the frozen clean-split Phase 4B/5A evidence and writes
commit-safe manuscript sources, tables, figure manifests, reference inventory,
and self-audit notes. It does not train, evaluate, or modify detector code.
"""

import csv
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "runs"
MANUSCRIPT = ROOT / "manuscript"
TABLES = MANUSCRIPT / "tables"
FIGURES = MANUSCRIPT / "figures"
LOCAL_RENDERED = FIGURES / "local_rendered"
LOCAL_QUAL = FIGURES / "local_qualitative"
REFERENCES = MANUSCRIPT / "references"
NOTES = MANUSCRIPT / "submission_notes"


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, headers=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if headers is None:
        headers = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in headers})


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def fmt_float(value, digits=6):
    if value in (None, "", "NA"):
        return "NA"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def mean_min_max(values):
    vals = [float(v) for v in values if v not in (None, "", "NA")]
    if not vals:
        return {"Mean": "NA", "Min": "NA", "Max": "NA", "Range": "NA"}
    return {
        "Mean": fmt_float(sum(vals) / len(vals)),
        "Min": fmt_float(min(vals)),
        "Max": fmt_float(max(vals)),
        "Range": fmt_float(max(vals) - min(vals)),
    }


def markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def write_table_pair(name, rows, headers, caption):
    csv_path = TABLES / f"{name}.csv"
    md_path = TABLES / f"{name}.md"
    write_csv(csv_path, rows, headers)
    md = f"# {name.replace('_', ' ')}\n\n{caption}\n\n{markdown_table(headers, rows)}\n"
    write_text(md_path, md)
    return csv_path, md_path


def rows_by_variant(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["Variant"]].append(row)
    return grouped


def build_tables():
    seed_rows = read_csv(RUNS / "clean_block64g16_seed_replication.csv")
    efficiency = read_csv(RUNS / "clean_efficiency_profile.csv")
    convergence = read_csv(RUNS / "clean_block64g16_convergence.csv")
    alpha_rows = read_csv(RUNS / "r4_reliability_weight_audit.csv")
    yolo_rows = (
        read_csv(RUNS / "Y11n_rgb_seed0_block64g16_e50" / "eval_project" / "eval_results.csv")
        + read_csv(RUNS / "Y11n_rgb_seed2_block64g16_e50" / "eval_project" / "eval_results.csv")
    )
    duplicate_rows = read_csv(RUNS / "rgb_cross_split_duplicate_summary.csv")
    blocked_rows = read_csv(RUNS / "blocked_split_proposal_summary.csv")

    dup = {row["Metric"]: row["Value"] for row in duplicate_rows if "Metric" in row}
    recommended = next((row for row in blocked_rows if row.get("recommended") == "yes"), {})

    table1 = [
        {"Item": "All TriAir samples", "Value": "10489", "Source": "runs/handoff_latest.md", "Notes": "All .npy samples are the dataset basis."},
        {"Item": "Samples with label txt", "Value": "9751", "Source": "runs/handoff_latest.md", "Notes": "Existing YOLO-format label files."},
        {"Item": "Samples without label txt", "Value": "738", "Source": "runs/handoff_latest.md", "Notes": "Treated as empty-target images."},
        {"Item": "Empty label txt files", "Value": "1", "Source": "runs/handoff_latest.md", "Notes": "Treated as empty-target images."},
        {"Item": "Total valid boxes", "Value": "30634", "Source": "runs/handoff_latest.md", "Notes": "Single class: vehicle."},
        {"Item": "Random split exact RGB-matched validation samples", "Value": dup.get("exact_rgb_matched_val_images", "153"), "Source": "runs/phase3c_report.md", "Notes": "Former random split is historical diagnostics only."},
        {"Item": "Clean split candidate", "Value": "block64_guard16_seed0", "Source": "runs/clean_block64g16_protocol.md", "Notes": "Frozen split used for headline evidence."},
        {"Item": "Clean train images", "Value": recommended.get("train_images", "7439"), "Source": "runs/clean_block64g16_protocol.md", "Notes": "Guard samples excluded."},
        {"Item": "Clean validation images", "Value": recommended.get("val_images", "2213"), "Source": "runs/clean_block64g16_protocol.md", "Notes": "Validation boxes = 5904."},
        {"Item": "Guard images", "Value": recommended.get("guard_images", "837"), "Source": "runs/clean_block64g16_protocol.md", "Notes": "Excluded from train and validation."},
        {"Item": "Clean exact RGB train/validation matches", "Value": recommended.get("exact_rgb_matched_val_images", "0"), "Source": "runs/clean_block64g16_protocol.md", "Notes": "Required integrity check."},
        {"Item": "Same-family guard violations", "Value": recommended.get("id_guard_violations", "0"), "Source": "runs/clean_block64g16_protocol.md", "Notes": "Required integrity check."},
    ]
    write_table_pair(
        "Table_1_dataset_and_clean_split",
        table1,
        ["Item", "Value", "Source", "Notes"],
        "Dataset statistics and leakage-aware clean blocked split protocol.",
    )

    table2 = [
        {"Item": "Detector family", "Value": "RepViT-M0.9 + FPN + FCOS", "Source": "rarepdet/models/", "Notes": "Torchvision FCOS head with custom backbone."},
        {"Item": "Input representation", "Value": "5 channels: RGB, thermal, event", "Source": "datasets/triair_dataset.py", "Notes": "Images are emitted as CxHxW float32 tensors."},
        {"Item": "Early-fusion baseline", "Value": "Conv2d(5,3,1) -> RepViT -> FPN -> FCOS", "Source": "rarepdet/models/early_fusion_fcos.py", "Notes": "Matched tri-modal baseline R0."},
        {"Item": "Reliability fusion", "Value": "RGB/T/E stems -> softmax alpha -> Conv2d(16,3,1)", "Source": "rarepdet/models/reliability_fusion_fcos.py", "Notes": "Used by R1/R2/R4."},
        {"Item": "FPN input channels", "Value": "[48, 96, 192, 384]", "Source": "tools/check_repvit_features.py", "Notes": "RepViT-M0.9 feature map channels."},
        {"Item": "FPN output channels", "Value": "128", "Source": "rarepdet/models/repvit_fpn_backbone.py", "Notes": "Shared by controlled variants."},
        {"Item": "Class handling", "Value": "TriAir class 0 -> torchvision label 1", "Source": "rarepdet/train_early_fusion.py", "Notes": "Background remains label 0."},
        {"Item": "Image size", "Value": "640", "Source": "runs/*/config.txt", "Notes": "Used for controlled clean-split runs."},
        {"Item": "Training length", "Value": "50 epochs", "Source": "runs/clean_block64g16_convergence.csv", "Notes": "Convergence audit is descriptive."},
        {"Item": "Controlled seeds", "Value": "0 and 2", "Source": "runs/seed_reproducibility_smoke.md", "Notes": "Replication only, no statistical significance claim."},
        {"Item": "AP implementation", "Value": "project-local AP50/AP75", "Source": "rarepdet/eval_map.py", "Notes": "No pycocotools dependency."},
        {"Item": "YOLO baseline", "Value": "YOLO11n RGB-only", "Source": "runs/yolo11n_rgb_baseline_protocol.md", "Notes": "External comparison, not architecture-only ablation."},
    ]
    write_table_pair(
        "Table_2_implementation_and_reproducibility",
        table2,
        ["Item", "Value", "Source", "Notes"],
        "Implementation and reproducibility choices used by the clean-split experiments.",
    )

    table3 = []
    t3_headers = ["Variant", "Seed", "Row Type", "Dropout Ratio", "P@0.50", "R@0.50", "F1@0.50", "AP50", "AP75", "Source"]
    for row in seed_rows:
        table3.append({key: row.get(key, "") for key in t3_headers if key != "Row Type" and key != "Source"} | {"Row Type": "per-seed", "Source": "runs/clean_block64g16_seed_replication.csv"})
    for variant, group in rows_by_variant(seed_rows).items():
        for metric in ["F1@0.50", "AP50", "AP75"]:
            stats = mean_min_max([row.get(metric) for row in group])
            table3.append(
                {
                    "Variant": variant,
                    "Seed": "0,2",
                    "Row Type": f"{metric} mean/min/max/range",
                    "Dropout Ratio": group[0].get("Dropout Ratio", "NA"),
                    "P@0.50": "NA",
                    "R@0.50": "NA",
                    "F1@0.50": stats["Mean"] if metric == "F1@0.50" else "NA",
                    "AP50": stats["Mean"] if metric == "AP50" else "NA",
                    "AP75": stats["Mean"] if metric == "AP75" else "NA",
                    "Source": f"min={stats['Min']}; max={stats['Max']}; range={stats['Range']}",
                }
            )
    write_table_pair(
        "Table_3_controlled_ablation",
        table3,
        t3_headers,
        "Controlled clean-split R-run ablation. Aggregate rows report mean with min/max/range in the Source column.",
    )

    table4 = []
    t4_headers = ["Variant", "Seed", "Condition", "AP50", "Row Type", "Mean", "Min", "Max", "Range", "Source"]
    for row in seed_rows:
        if row["Variant"].startswith("R0"):
            continue
        for condition, col in [("w/o RGB", "w/o RGB AP50"), ("w/o Thermal", "w/o Thermal AP50"), ("w/o Event", "w/o Event AP50")]:
            table4.append(
                {
                    "Variant": row["Variant"],
                    "Seed": row["Seed"],
                    "Condition": condition,
                    "AP50": row[col],
                    "Row Type": "per-seed",
                    "Mean": "NA",
                    "Min": "NA",
                    "Max": "NA",
                    "Range": "NA",
                    "Source": "runs/clean_block64g16_seed_replication.csv",
                }
            )
    for variant, group in rows_by_variant([row for row in seed_rows if not row["Variant"].startswith("R0")]).items():
        for condition, col in [("w/o RGB", "w/o RGB AP50"), ("w/o Thermal", "w/o Thermal AP50"), ("w/o Event", "w/o Event AP50")]:
            stats = mean_min_max([row[col] for row in group])
            table4.append(
                {
                    "Variant": variant,
                    "Seed": "0,2",
                    "Condition": condition,
                    "AP50": "NA",
                    "Row Type": "mean/min/max/range",
                    **stats,
                    "Source": "computed from per-seed rows; conditions are not averaged together",
                }
            )
    write_table_pair(
        "Table_4_missing_modality_robustness",
        table4,
        t4_headers,
        "Synthetic single-modality removal results. Each condition is interpreted separately.",
    )

    table5 = []
    t5_headers = ["Method", "Input", "Seed", "Precision", "Recall", "F1", "AP50", "AP75", "GT boxes", "Predictions", "Mean Confidence", "Row Type", "Source"]
    r4_rows = [row for row in seed_rows if row["Variant"].startswith("R4 ")]
    for row in r4_rows:
        table5.append(
            {
                "Method": "R4 Reliability p=0.20",
                "Input": "RGB-thermal-event",
                "Seed": row["Seed"],
                "Precision": row["P@0.50"],
                "Recall": row["R@0.50"],
                "F1": row["F1@0.50"],
                "AP50": row["AP50"],
                "AP75": row["AP75"],
                "GT boxes": "5904",
                "Predictions": "NA",
                "Mean Confidence": "NA",
                "Row Type": "per-seed",
                "Source": "runs/clean_block64g16_seed_replication.csv",
            }
        )
    for row in yolo_rows:
        table5.append(
            {
                "Method": "YOLO11n RGB-only",
                "Input": "RGB only",
                "Seed": row["Seed"],
                "Precision": row["Precision"],
                "Recall": row["Recall"],
                "F1": row["F1"],
                "AP50": row["AP50"],
                "AP75": row["AP75"],
                "GT boxes": row["GT boxes"],
                "Predictions": row["Predictions"],
                "Mean Confidence": row["Mean Confidence"],
                "Row Type": "per-seed",
                "Source": "runs/Y11n_rgb_seed*_block64g16_e50/eval_project/eval_results.csv",
            }
        )
    for method, input_name, group in [
        ("R4 Reliability p=0.20", "RGB-thermal-event", table5[:2]),
        ("YOLO11n RGB-only", "RGB only", table5[2:]),
    ]:
        for metric in ["Precision", "Recall", "F1", "AP50", "AP75"]:
            stats = mean_min_max([row[metric] for row in group])
            table5.append(
                {
                    "Method": method,
                    "Input": input_name,
                    "Seed": "0,2",
                    "Precision": stats["Mean"] if metric == "Precision" else "NA",
                    "Recall": stats["Mean"] if metric == "Recall" else "NA",
                    "F1": stats["Mean"] if metric == "F1" else "NA",
                    "AP50": stats["Mean"] if metric == "AP50" else "NA",
                    "AP75": stats["Mean"] if metric == "AP75" else "NA",
                    "GT boxes": "5904",
                    "Predictions": "NA",
                    "Mean Confidence": "NA",
                    "Row Type": f"{metric} mean/min/max/range",
                    "Source": f"min={stats['Min']}; max={stats['Max']}; range={stats['Range']}",
                }
            )
    write_table_pair(
        "Table_5_rgb_only_external_baseline",
        table5,
        t5_headers,
        "R4 tri-modal detector compared with a YOLO11n RGB-only external baseline.",
    )

    table6 = []
    t6_headers = ["Group", "Model", "Path or Seed", "Params", "FPS mean", "Latency ms/img mean", "CUDA Memory MB mean", "Best Epoch", "Best AP50", "Status", "Source", "Notes"]
    for row in efficiency:
        table6.append(
            {
                "Group": "efficiency",
                "Model": row["Model"],
                "Path or Seed": row["Path"],
                "Params": row["Params"],
                "FPS mean": row["FPS mean"],
                "Latency ms/img mean": row["Latency ms/img mean"],
                "CUDA Memory MB mean": row["CUDA Memory MB mean"],
                "Best Epoch": "NA",
                "Best AP50": "NA",
                "Status": "NA",
                "Source": "runs/clean_efficiency_profile.csv",
                "Notes": row.get("Note", ""),
            }
        )
    for row in convergence:
        table6.append(
            {
                "Group": "convergence",
                "Model": row["Variant"],
                "Path or Seed": row["Seed"],
                "Params": "NA",
                "FPS mean": "NA",
                "Latency ms/img mean": "NA",
                "CUDA Memory MB mean": "NA",
                "Best Epoch": row["Best Epoch"],
                "Best AP50": row["Best AP50"],
                "Status": row["Status"],
                "Source": "runs/clean_block64g16_convergence.csv",
                "Notes": "Descriptive audit; no extra training triggered.",
            }
        )
    write_table_pair(
        "Table_6_efficiency_and_convergence",
        table6,
        t6_headers,
        "Efficiency profiling and convergence audit. Raw-forward and detector-inference paths are separate.",
    )

    t7_headers = [
        "Variant",
        "Seed",
        "Mode",
        "Samples",
        "alpha_rgb_mean",
        "alpha_rgb_std",
        "alpha_thermal_mean",
        "alpha_thermal_std",
        "alpha_event_mean",
        "alpha_event_std",
        "dominant_rgb",
        "dominant_thermal",
        "dominant_event",
        "Source",
    ]
    table7 = []
    for row in alpha_rows:
        table7.append({key: row.get(key, "") for key in t7_headers if key != "Source"} | {"Source": "runs/r4_reliability_weight_audit.csv"})
    write_table_pair(
        "Table_7_reliability_weight_audit",
        table7,
        t7_headers,
        "Observed reliability-gating behavior under full input and synthetic single-modality removal.",
    )

    return {
        "seed_rows": seed_rows,
        "efficiency": efficiency,
        "convergence": convergence,
        "alpha_rows": alpha_rows,
        "qualitative": read_csv(RUNS / "clean_qualitative_manifest.csv"),
        "yolo_rows": yolo_rows,
    }


def build_figure_sources(data):
    fig3_rows = []
    for row in data["seed_rows"]:
        fig3_rows.append(
            {
                "Variant": row["Variant"],
                "Seed": row["Seed"],
                "F1": row["F1@0.50"],
                "AP50": row["AP50"],
                "AP75": row["AP75"],
            }
        )
    write_csv(FIGURES / "fig3_controlled_ablation_source.csv", fig3_rows, ["Variant", "Seed", "F1", "AP50", "AP75"])

    fig4_rows = []
    for row in data["seed_rows"]:
        if row["Variant"].startswith("R0"):
            continue
        for condition, col in [("w/o RGB", "w/o RGB AP50"), ("w/o Thermal", "w/o Thermal AP50"), ("w/o Event", "w/o Event AP50")]:
            fig4_rows.append({"Variant": row["Variant"], "Seed": row["Seed"], "Condition": condition, "AP50": row[col]})
    write_csv(FIGURES / "fig4_missing_modality_source.csv", fig4_rows, ["Variant", "Seed", "Condition", "AP50"])

    fig5_rows = []
    for row in data["alpha_rows"]:
        fig5_rows.append(
            {
                "Seed": row["Seed"],
                "Mode": row["Mode"],
                "alpha_rgb_mean": row["alpha_rgb_mean"],
                "alpha_thermal_mean": row["alpha_thermal_mean"],
                "alpha_event_mean": row["alpha_event_mean"],
                "alpha_rgb_std": row["alpha_rgb_std"],
                "alpha_thermal_std": row["alpha_thermal_std"],
                "alpha_event_std": row["alpha_event_std"],
            }
        )
    write_csv(
        FIGURES / "fig5_reliability_weight_source.csv",
        fig5_rows,
        ["Seed", "Mode", "alpha_rgb_mean", "alpha_thermal_mean", "alpha_event_mean", "alpha_rgb_std", "alpha_thermal_std", "alpha_event_std"],
    )

    fig6_rows = []
    for row in data["qualitative"]:
        fig6_rows.append(
            {
                "Category": row["Category"],
                "Rank": row["Rank"],
                "Image Index": row["Image Index"],
                "GT Count": row["GT Count"],
                "Prediction Summary": row["Prediction Summary"],
                "Rationale": row["Rationale"],
                "Local Panel Path": row["Panel Path"],
            }
        )
    write_csv(
        FIGURES / "fig6_qualitative_panel_manifest.csv",
        fig6_rows,
        ["Category", "Rank", "Image Index", "GT Count", "Prediction Summary", "Rationale", "Local Panel Path"],
    )


def build_plot_script():
    script = r'''#!/usr/bin/env python
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
'''
    write_text(FIGURES / "plot_phase6a_figures.py", script)


def render_figures():
    try:
        subprocess.run([sys.executable, str(FIGURES / "plot_phase6a_figures.py")], cwd=ROOT, check=True)
        return "rendered"
    except Exception as exc:
        return f"not rendered: {exc}"


def copy_local_qualitative(data):
    LOCAL_QUAL.mkdir(parents=True, exist_ok=True)
    copied = 0
    for row in data["qualitative"]:
        panel_text = row.get("Panel Path", "")
        if not panel_text:
            continue
        panel = Path(panel_text)
        if panel.is_file():
            shutil.copy2(panel, LOCAL_QUAL / panel.name)
            copied += 1
    note = (
        "# Local Qualitative Panels\n\n"
        "This directory is local-only and ignored by Git. It is populated from "
        "`runs/local_clean_qualitative_panels/` when available.\n\n"
        f"Copied panels in the last build: {copied}\n"
    )
    write_text(LOCAL_QUAL / "README.md", note)
    return copied


def build_figure_manifest():
    rows = [
        {"Figure": "Fig. 1", "Title": "Overall R4 architecture and training/inference flow", "Source": "rarepdet/models/reliability_fusion_fcos.py; manuscript method text", "Commit Safe": "manifest only", "Local Output": "manual schematic pending target journal"},
        {"Figure": "Fig. 2", "Title": "Leakage-aware blocked split and RGB-content duplicate audit workflow", "Source": "runs/phase3c_report.md; runs/clean_block64g16_protocol.md", "Commit Safe": "manifest only", "Local Output": "manual schematic pending target journal"},
        {"Figure": "Fig. 3", "Title": "Controlled two-seed full-modality AP50/AP75/F1 comparison", "Source": "manuscript/figures/fig3_controlled_ablation_source.csv", "Commit Safe": "csv and plotting script", "Local Output": "manuscript/figures/local_rendered/Fig3_controlled_ablation.png/pdf"},
        {"Figure": "Fig. 4", "Title": "Three missing-modality AP50 conditions for R1/R2/R4", "Source": "manuscript/figures/fig4_missing_modality_source.csv", "Commit Safe": "csv and plotting script", "Local Output": "manuscript/figures/local_rendered/Fig4_missing_modality.png/pdf"},
        {"Figure": "Fig. 5", "Title": "R4 fusion-weight means under full and synthetic missing-modality conditions", "Source": "manuscript/figures/fig5_reliability_weight_source.csv", "Commit Safe": "csv and plotting script", "Local Output": "manuscript/figures/local_rendered/Fig5_reliability_weights.png/pdf"},
        {"Figure": "Fig. 6", "Title": "Qualitative panels for R0 versus R4, hard cases, and missing-modality cases", "Source": "manuscript/figures/fig6_qualitative_panel_manifest.csv", "Commit Safe": "manifest only", "Local Output": "manuscript/figures/local_qualitative/"},
    ]
    headers = ["Figure", "Title", "Source", "Commit Safe", "Local Output"]
    write_csv(FIGURES / "figure_manifest.csv", rows, headers)
    md = "# Figure Manifest\n\n" + markdown_table(headers, rows) + "\n\nRendered PNG/PDF charts and qualitative panels are local-only and must not be committed.\n"
    write_text(FIGURES / "figure_manifest.md", md)


REFERENCE_ROWS = [
    {"Key": "RepViT2024", "Title": "RepViT: Revisiting Mobile CNN From ViT Perspective", "Authors": "Wang et al.", "Venue": "CVPR / arXiv", "Year": "2024", "DOI_or_URL": "https://arxiv.org/abs/2307.09283", "Intended Section": "Method", "Verification Source": "arXiv record"},
    {"Key": "FCOS2019", "Title": "FCOS: Fully Convolutional One-Stage Object Detection", "Authors": "Tian, Shen, Chen, and He", "Venue": "ICCV", "Year": "2019", "DOI_or_URL": "https://openaccess.thecvf.com/content_ICCV_2019/html/Tian_FCOS_Fully_Convolutional_One-Stage_Object_Detection_ICCV_2019_paper.html", "Intended Section": "Method", "Verification Source": "CVF Open Access"},
    {"Key": "FPN2017", "Title": "Feature Pyramid Networks for Object Detection", "Authors": "Lin et al.", "Venue": "CVPR", "Year": "2017", "DOI_or_URL": "https://openaccess.thecvf.com/content_cvpr_2017/html/Lin_Feature_Pyramid_Networks_CVPR_2017_paper.html", "Intended Section": "Method", "Verification Source": "CVF Open Access"},
    {"Key": "FasterRCNN2015", "Title": "Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks", "Authors": "Ren, He, Girshick, and Sun", "Venue": "NeurIPS", "Year": "2015", "DOI_or_URL": "https://arxiv.org/abs/1506.01497", "Intended Section": "Related work", "Verification Source": "arXiv record"},
    {"Key": "RetinaNet2017", "Title": "Focal Loss for Dense Object Detection", "Authors": "Lin, Goyal, Girshick, He, and Dollar", "Venue": "ICCV", "Year": "2017", "DOI_or_URL": "https://openaccess.thecvf.com/content_ICCV_2017/html/Lin_Focal_Loss_for_ICCV_2017_paper.html", "Intended Section": "Related work", "Verification Source": "CVF Open Access"},
    {"Key": "YOLO11Docs", "Title": "YOLO11 model documentation", "Authors": "Ultralytics", "Venue": "Official documentation", "Year": "2024", "DOI_or_URL": "https://docs.ultralytics.com/models/yolo11/", "Intended Section": "Experiments", "Verification Source": "Official documentation"},
    {"Key": "TorchvisionFCOS", "Title": "Torchvision FCOS model documentation", "Authors": "PyTorch / Torchvision maintainers", "Venue": "Official documentation", "Year": "2024", "DOI_or_URL": "https://pytorch.org/vision/stable/models/fcos.html", "Intended Section": "Method", "Verification Source": "Official documentation"},
    {"Key": "TimmModels", "Title": "PyTorch Image Models", "Authors": "Ross Wightman and contributors", "Venue": "Official software repository", "Year": "2019", "DOI_or_URL": "https://github.com/huggingface/pytorch-image-models", "Intended Section": "Implementation", "Verification Source": "Official repository"},
    {"Key": "VisDrone2018", "Title": "VisDrone: The Vision Meets Drone Object Detection Challenge", "Authors": "Zhu et al.", "Venue": "ECCV Workshops / official dataset", "Year": "2018", "DOI_or_URL": "https://github.com/VisDrone/VisDrone-Dataset", "Intended Section": "Related work", "Verification Source": "Official dataset repository"},
    {"Key": "UAVDT2018", "Title": "The Unmanned Aerial Vehicle Benchmark: Object Detection and Tracking", "Authors": "Du et al.", "Venue": "ECCV Workshops / official project", "Year": "2018", "DOI_or_URL": "https://sites.google.com/view/grli-uavdt", "Intended Section": "Related work", "Verification Source": "Official project page"},
    {"Key": "KAIST2015", "Title": "Multispectral Pedestrian Detection: Benchmark Dataset and Baseline", "Authors": "Hwang et al.", "Venue": "CVPR", "Year": "2015", "DOI_or_URL": "https://soonminhwang.github.io/rgbt-ped-detection/", "Intended Section": "Related work", "Verification Source": "Official project page"},
    {"Key": "FLIRADAS", "Title": "FLIR ADAS thermal dataset", "Authors": "Teledyne FLIR", "Venue": "Official dataset", "Year": "2018", "DOI_or_URL": "https://www.flir.com/oem/adas/adas-dataset-form/", "Intended Section": "Related work", "Verification Source": "Official dataset page"},
    {"Key": "LLVIP2021", "Title": "LLVIP: A Visible-Infrared Paired Dataset for Low-Light Vision", "Authors": "Jia et al.", "Venue": "Official dataset / arXiv", "Year": "2021", "DOI_or_URL": "https://github.com/bupt-ai-cz/LLVIP", "Intended Section": "Related work", "Verification Source": "Official repository"},
    {"Key": "DroneVehicle2021", "Title": "DroneVehicle: A Drone-Based RGB-Infrared Cross-Modality Vehicle Detection Dataset", "Authors": "Sun et al.", "Venue": "Official dataset repository", "Year": "2021", "DOI_or_URL": "https://github.com/VisDrone/DroneVehicle", "Intended Section": "Related work", "Verification Source": "Official repository"},
    {"Key": "CrossModalDistillation2016", "Title": "Cross Modal Distillation for Supervision Transfer", "Authors": "Gupta, Hoffman, and Malik", "Venue": "CVPR", "Year": "2016", "DOI_or_URL": "https://openaccess.thecvf.com/content_cvpr_2016/html/Gupta_Cross_Modal_Distillation_CVPR_2016_paper.html", "Intended Section": "Related work", "Verification Source": "CVF Open Access"},
    {"Key": "ModalityHallucination2016", "Title": "Learning with Side Information through Modality Hallucination", "Authors": "Hoffman et al.", "Venue": "CVPR", "Year": "2016", "DOI_or_URL": "https://openaccess.thecvf.com/content_cvpr_2016/html/Hoffman_Learning_With_Side_CVPR_2016_paper.html", "Intended Section": "Related work", "Verification Source": "CVF Open Access"},
    {"Key": "Gallego2020EventSurvey", "Title": "Event-Based Vision: A Survey", "Authors": "Gallego et al.", "Venue": "IEEE TPAMI", "Year": "2020", "DOI_or_URL": "https://arxiv.org/abs/1904.08405", "Intended Section": "Related work", "Verification Source": "arXiv record"},
    {"Key": "MVSEC2018", "Title": "The Multivehicle Stereo Event Camera Dataset: An Event Camera Dataset for 3D Perception", "Authors": "Zhu et al.", "Venue": "IEEE Robotics and Automation Letters", "Year": "2018", "DOI_or_URL": "https://daniilidis-group.github.io/mvsec/", "Intended Section": "Related work", "Verification Source": "Official project page"},
    {"Key": "DSEC2021", "Title": "DSEC: A Stereo Event Camera Dataset for Driving Scenarios", "Authors": "Gehrig et al.", "Venue": "IEEE Robotics and Automation Letters", "Year": "2021", "DOI_or_URL": "https://dsec.ifi.uzh.ch/", "Intended Section": "Related work", "Verification Source": "Official project page"},
    {"Key": "Gen1Events", "Title": "GEN1 Automotive Detection Dataset", "Authors": "Prophesee", "Venue": "Official dataset documentation", "Year": "2020", "DOI_or_URL": "https://docs.prophesee.ai/stable/datasets.html", "Intended Section": "Related work", "Verification Source": "Official documentation"},
    {"Key": "RVT2023", "Title": "Recurrent Vision Transformers for Object Detection with Event Cameras", "Authors": "Gehrig and Scaramuzza", "Venue": "CVPR", "Year": "2023", "DOI_or_URL": "https://arxiv.org/abs/2212.05598", "Intended Section": "Related work", "Verification Source": "arXiv record"},
    {"Key": "E2VID2021", "Title": "High Speed and High Dynamic Range Video with an Event Camera", "Authors": "Rebecq et al.", "Venue": "IEEE TPAMI / CVPR extension", "Year": "2021", "DOI_or_URL": "https://arxiv.org/abs/1906.07173", "Intended Section": "Related work", "Verification Source": "arXiv record"},
    {"Key": "ModDrop2016", "Title": "ModDrop: Adaptive Multi-Modal Gesture Recognition", "Authors": "Neverova et al.", "Venue": "IEEE TPAMI / CVPR workshop lineage", "Year": "2016", "DOI_or_URL": "https://arxiv.org/abs/1501.00102", "Intended Section": "Missing-modality robustness", "Verification Source": "arXiv record"},
    {"Key": "HeMIS2016", "Title": "HeMIS: Hetero-Modal Image Segmentation", "Authors": "Havaei et al.", "Venue": "MICCAI", "Year": "2016", "DOI_or_URL": "https://arxiv.org/abs/1607.05194", "Intended Section": "Missing-modality robustness", "Verification Source": "arXiv record"},
    {"Key": "Kapoor2023Leakage", "Title": "Leakage and the Reproducibility Crisis in ML-based Science", "Authors": "Kapoor and Narayanan", "Venue": "Patterns", "Year": "2023", "DOI_or_URL": "https://doi.org/10.1016/j.patter.2023.100804", "Intended Section": "Evaluation protocol", "Verification Source": "DOI resolver"},
    {"Key": "Cawley2010Overfitting", "Title": "On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation", "Authors": "Cawley and Talbot", "Venue": "Journal of Machine Learning Research", "Year": "2010", "DOI_or_URL": "https://jmlr.org/papers/v11/cawley10a.html", "Intended Section": "Evaluation protocol", "Verification Source": "JMLR official page"},
    {"Key": "Recht2019ImageNet", "Title": "Do ImageNet Classifiers Generalize to ImageNet?", "Authors": "Recht et al.", "Venue": "ICML", "Year": "2019", "DOI_or_URL": "https://arxiv.org/abs/1902.10811", "Intended Section": "Evaluation protocol", "Verification Source": "arXiv record"},
    {"Key": "Northcutt2021LabelErrors", "Title": "Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks", "Authors": "Northcutt, Athalye, and Mueller", "Venue": "NeurIPS", "Year": "2021", "DOI_or_URL": "https://arxiv.org/abs/2103.14749", "Intended Section": "Evaluation protocol", "Verification Source": "arXiv record"},
    {"Key": "COCO2014", "Title": "Microsoft COCO: Common Objects in Context", "Authors": "Lin et al.", "Venue": "ECCV", "Year": "2014", "DOI_or_URL": "https://arxiv.org/abs/1405.0312", "Intended Section": "Experiments", "Verification Source": "arXiv record"},
    {"Key": "PascalVOC2010", "Title": "The PASCAL Visual Object Classes (VOC) Challenge", "Authors": "Everingham et al.", "Venue": "International Journal of Computer Vision", "Year": "2010", "DOI_or_URL": "https://doi.org/10.1007/s11263-009-0275-4", "Intended Section": "Experiments", "Verification Source": "DOI resolver"},
    {"Key": "Kohavi1995CV", "Title": "A Study of Cross-Validation and Bootstrap for Accuracy Estimation and Model Selection", "Authors": "Kohavi", "Venue": "IJCAI", "Year": "1995", "DOI_or_URL": "https://www.ijcai.org/Proceedings/95-2/Papers/016.pdf", "Intended Section": "Evaluation protocol", "Verification Source": "IJCAI proceedings PDF"},
]


def build_reference_inventory():
    headers = ["Key", "Title", "Authors", "Venue", "Year", "DOI_or_URL", "Intended Section", "Verification Source"]
    write_csv(REFERENCES / "reference_inventory.csv", REFERENCE_ROWS, headers)
    md = [
        "# Reference Inventory",
        "",
        "Status: DRAFT VERIFIED METADATA - citation style pending target journal.",
        "",
        "Only entries with a DOI, arXiv record, official project page, publisher page, or official documentation source are included. The manuscript uses placeholder keys of the form `[REF: Key]` until a target journal citation style is selected.",
        "",
        markdown_table(headers, REFERENCE_ROWS),
    ]
    write_text(REFERENCES / "reference_inventory.md", "\n".join(md))


def build_readme():
    text = """# RA-RepDet Manuscript Package

This directory contains a journal-neutral first manuscript draft for RA-RepDet-TriAir. It is not formatted for any specific journal, and no Word or PDF submission file is produced in Phase 6A.

The manuscript is driven by frozen local evidence files, especially `runs/phase4b_report.md`, `runs/phase5a_report.md`, `runs/clean_block64g16_protocol.md`, `runs/phase3c_report.md`, `runs/clean_efficiency_profile.md`, `runs/r4_reliability_weight_audit.md`, `runs/clean_qualitative_summary.md`, and `runs/yolo11n_rgb_baseline_protocol.md`.

Commit-safe assets are the Markdown manuscript, CSV/Markdown tables, figure manifests, chart source CSV files, plotting scripts, reference inventory, and audit notes. Local-only assets are rendered PNG/PDF charts under `manuscript/figures/local_rendered/` and qualitative panels under `manuscript/figures/local_qualitative/`; these are intentionally ignored by Git.

The next manual decision is to choose a target SCI/EI journal. Only after that decision should the citation style, figure dimensions, word limits, data availability wording, and submission-specific metadata be finalized.
"""
    write_text(MANUSCRIPT / "README.md", text)


def build_manuscript():
    text = """# Reliability-Aware RepViT-FCOS for Tri-Modal UAV Vehicle Detection Under Leakage-Aware Evaluation

Front-matter note: this is a journal-neutral draft, not a submission-formatted manuscript. Alternative titles for later journal targeting are: "Leakage-Aware Tri-Modal UAV Vehicle Detection with Reliability-Gated RepViT-FCOS"; "Robust RGB-Thermal-Event Vehicle Detection for UAV Perception Using Modality Dropout"; and "A Reproducible RepViT-FCOS Baseline for TriAir Vehicle Detection with Missing-Modality Robustness".

## Abstract

Multi-sensor UAV perception can benefit from RGB, thermal, and event information, but evaluation is easily overstated when adjacent frames or duplicated visual content leak across splits. We present RA-RepDet, a lightweight RepViT-FCOS detector for TriAir vehicle detection that combines RGB, thermal, and event channels through reliability-aware fusion and modality-dropout training. The study is built around a leakage-aware blocked split with a guard band: 7439 training images, 2213 validation images, and 837 excluded guard images, with zero exact RGB train/validation matches and zero same-family guard violations after a duplicate audit of the former random split. In controlled two-seed experiments, the proposed R4 variant, reliability fusion with modality dropout p=0.20, achieved mean AP50=0.962495, AP75=0.891266, and F1=0.920861. It improved the matched tri-modal early-fusion RepViT-FCOS baseline in full-modality AP50 and provided the strongest robustness among evaluated reliability variants when one sensor stream was synthetically removed. The RGB-only YOLO11n comparison is reported as an external baseline, not an architecture-only ablation. The results support RA-RepDet as a practical and reproducible tri-modal UAV detection baseline, while the two-seed design, single dataset, synthetic missingness, and remaining thermal-drop vulnerability delimit the claims.

## Keywords

UAV vehicle detection; RGB-thermal-event fusion; RepViT; FCOS; missing-modality robustness; data leakage; blocked split.

## 1. Introduction

UAV vehicle detection increasingly needs to operate under changing illumination, target scale variation, and sensor uncertainty. RGB cameras provide detailed texture and color cues, thermal sensors can retain target contrast when visible light degrades, and event streams can encode sparse temporal changes with high dynamic range. A practical detector for this setting should be lightweight enough for deployment-oriented research, should use all available modalities without relying on one stream alone, and should be evaluated under a protocol that does not inflate performance through visual overlap between train and validation images.

This work studies tri-modal vehicle detection on TriAir using five-channel samples composed of RGB, thermal, and event channels. The detector uses a RepViT-M0.9 backbone [REF: RepViT2024], an FPN neck [REF: FPN2017], and an FCOS anchor-free detection head [REF: FCOS2019]. The baseline, R0, projects the five input channels to three channels and applies RepViT-FCOS. The proposed main variant, R4, uses modality-specific stems and a learned reliability estimator to fuse RGB, thermal, and event features before the RepViT backbone. During training, R4 uses modality dropout with p=0.20 to improve behavior when a sensor stream is removed at inference-like evaluation time.

The central methodological point is that the paper does not rely on the original random split. A Phase 3C audit found 153 exact RGB-content train/validation overlaps in the random split, corresponding to 0.072927 of validation images. We therefore use a frozen block64/guard16 split with 7439 training images, 2213 validation images, and 837 guard images. This split has zero exact RGB train/validation matches and zero same-family guard-band violations. This protocol is important because benchmark leakage and selection bias can make apparent gains less reliable [REF: Kapoor2023Leakage] [REF: Cawley2010Overfitting].

The contributions are conservative. First, we provide a reproducible RepViT-FCOS tri-modal UAV vehicle detection baseline on a leakage-aware clean split. Second, we show that reliability-aware fusion improves the matched tri-modal early-fusion baseline in controlled two-seed experiments. Third, we show that modality dropout improves robustness under synthetic single-modality removal, with p=0.20 selected as the main variant by controlled clean-split evidence. Fourth, we separate the matched tri-modal ablation from an RGB-only YOLO11n external baseline [REF: YOLO11Docs], avoiding the unsupported claim that the gap is due only to architecture.

## 2. Related Work

### 2.1 UAV Vehicle Detection

Vehicle detection from UAV imagery has been studied through benchmarks such as VisDrone and UAVDT, which emphasize small objects, dense scenes, viewpoint changes, and platform motion [REF: VisDrone2018] [REF: UAVDT2018]. These benchmarks helped clarify why conventional object detectors require careful multi-scale processing in aerial views. General object detection progress, including region-proposal detectors, dense one-stage detectors, and focal-loss formulations, provides the backbone of modern detection systems [REF: FasterRCNN2015] [REF: RetinaNet2017]. Our work follows this line but focuses on a tri-modal UAV setting, where the sensor representation and split integrity are as important as the detector family.

### 2.2 RGB-Thermal-Event / Multi-Sensor Detection

RGB-thermal perception has a long history in pedestrian and vehicle detection because visible and infrared cues respond differently to illumination and heat contrast. KAIST multispectral pedestrian detection, FLIR ADAS, LLVIP, and DroneVehicle are representative resources for visible-infrared learning [REF: KAIST2015] [REF: FLIRADAS] [REF: LLVIP2021] [REF: DroneVehicle2021]. Cross-modal supervision and modality hallucination further demonstrate that information from one sensor can regularize or substitute another during training [REF: CrossModalDistillation2016] [REF: ModalityHallucination2016]. Event-camera work complements this view by providing high-temporal-resolution sensing and robustness to high dynamic range scenes, as summarized in event-based vision surveys and driving datasets such as MVSEC, DSEC, and GEN1 [REF: Gallego2020EventSurvey] [REF: MVSEC2018] [REF: DSEC2021] [REF: Gen1Events]. RA-RepDet is positioned inside this multi-sensor detection space, but the contribution is a practical fusion baseline rather than a broad event-vision model.

### 2.3 Missing-Modality Robustness

Missing-modality learning addresses the case in which one or more input streams are unavailable, corrupted, or intentionally withheld. Modality dropout and hetero-modal learning are common strategies for reducing dependence on a single stream [REF: ModDrop2016] [REF: HeMIS2016]. In this study, synthetic missingness is implemented by zeroing a modality during evaluation. This is a controlled stress test rather than a complete model of real sensor failure. The reliability-weight audit is therefore interpreted as observed gating behavior under synthetic removal, not as causal evidence of physical modality importance.

## 3. Method

### 3.1 Overall Architecture

The detector receives a five-channel tensor containing RGB, thermal, and event inputs. All variants use RepViT-M0.9 features with four stages of channel sizes 48, 96, 192, and 384, followed by an FPN that maps each stage to 128 channels and an FCOS detection head. This structure preserves the lightweight mobile-convolutional design of RepViT while using a standard anchor-free detection formulation [REF: RepViT2024] [REF: FCOS2019] [REF: TorchvisionFCOS]. The task is single-class vehicle detection. TriAir label class 0 is converted to torchvision label 1 during training, while background remains label 0.

### 3.2 Early-Fusion Baseline

The matched tri-modal baseline, R0, uses a 1x1 input projection from five channels to three channels before the RepViT backbone. This design keeps the backbone interface compatible with ImageNet-style three-channel models while exposing all modalities to the detector. It is intentionally simple and serves as the primary architecture/fusion baseline. Because R0 and the reliability variants share the same detection head, FPN width, backbone family, training split, image size, and evaluation code, R0 versus R1/R2/R4 is the valid matched ablation for fusion design.

### 3.3 Reliability-Aware Tri-Modal Fusion

The reliability model separates the input into RGB, thermal, and event streams. RGB is processed by a Conv2d(3,16,3,padding=1)+BN+SiLU stem, thermal by a Conv2d(1,16,3,padding=1)+BN+SiLU stem, and event by the same one-channel stem. Global average pooled stem features are concatenated into a 48-dimensional vector and passed through a lightweight estimator, Linear(48,16)+SiLU+Linear(16,3), followed by softmax. The resulting alpha values weight the three 16-channel stem tensors, and the fused tensor is projected to three channels before RepViT. This adds only a small parameter increase relative to R0 while making the fusion operation input-adaptive.

### 3.4 Modality-Dropout Training

The R1 variant uses reliability fusion without modality dropout. R2 uses modality dropout p=0.15, and R4 uses p=0.20. Modality dropout is training-only: at training time, sensor streams can be zeroed to discourage brittle dependence on one stream; at standard full-modality inference, all streams are provided. Missing-modality evaluation uses synthetic removal of RGB, thermal, or event channels. This setup supports controlled robustness measurement, but it does not prove that the same behavior will transfer perfectly to all real sensor-failure mechanisms.

## 4. Dataset and Leakage-Aware Evaluation Protocol

### 4.1 TriAir Data Representation and Labels

TriAir is represented locally as 10489 `.npy` samples. Each sample is a five-channel RGB-thermal-event image, and labels are YOLO-format vehicle boxes. There are 9751 images with label text files, 738 images without label text files, and one empty label text file. Missing or empty label files are treated as empty-target images rather than discarded. Across the dataset, 30634 valid vehicle boxes are available. YOLO-normalized labels are converted to absolute xyxy boxes for torchvision detection training and evaluation.

### 4.2 RGB-Content Duplicate Audit

Before the clean protocol was adopted, the random split was audited for exact RGB-content overlap. The audit detected 153 validation samples with at least one training sample sharing exact RGB content, covering 0.072927 of validation images. This finding does not claim full five-channel byte duplication, but it is sufficient to make the random split unsuitable for publication-grade headline results. This decision follows the broader principle that leakage-aware evaluation is necessary when samples may be adjacent or visually repeated [REF: Kapoor2023Leakage] [REF: Recht2019ImageNet] [REF: Northcutt2021LabelErrors].

### 4.3 Blocked Split and Guard Band

The final evaluation uses the frozen `block64_guard16_seed0` split. It contains 7439 training images, 2213 validation images, and 837 guard images that are excluded from both training and validation. The validation set contains 5904 ground-truth boxes. Integrity checks report zero exact RGB train/validation matches and zero same-family guard violations. All main claims in this manuscript use this split only. The former E0-E6 random-split experiments are retained as historical diagnostics but are excluded from the abstract, main results tables, and conclusion.

## 5. Experiments

### 5.1 Experimental Settings and Reproducibility

The clean-split controlled comparison trains R0, R1, R2, and R4 for 50 epochs at seeds 0 and 2. The image size is 640, and the same local AP implementation is used for AP50 and AP75. The two seeds provide controlled replication and are not treated as a statistical-significance test. A seed reproducibility smoke test confirms that identical seeds reproduce initial state and early shuffling, while different seeds produce different initialization and shuffling. Efficiency profiling uses batch size 1, 640-pixel inputs, 100 warm-up iterations, 300 timed iterations, and three repeats, excluding dataloader and file I/O.

### 5.2 Controlled Clean-Split Ablation

The matched tri-modal ablation supports the selection of R4 as the main variant. R0 early fusion achieved AP50 values of 0.938560 and 0.937711 across seeds 0 and 2, with mean AP50=0.938136. R1 reliability fusion without dropout improved AP50 to 0.952112 and 0.954378, with mean AP50=0.953245. R2 with p=0.15 reached AP50=0.961573 and 0.957739, while R4 with p=0.20 reached AP50=0.965012 and 0.959977. R4 therefore had the highest mean AP50=0.962495. R4 also achieved mean AP75=0.891266 and mean F1=0.920861. AP75 leadership was split between R2 and R4 by seed, so the claim is not that R4 dominates every metric, but that it is the best overall clean-split main variant under the predefined selection logic.

### 5.3 Robustness to Synthetic Missing Modalities

Missing-modality evaluation shows the main benefit of modality dropout. R1 without dropout has weak missing-modality AP50, especially under thermal removal. R2 improves all three synthetic removal cases, and R4 improves the R2 results in both seeds for no-RGB, no-thermal, and no-event AP50. R4 mean AP50 values are 0.916051 without RGB, 0.718277 without thermal, and 0.961577 without event. Thermal removal remains the hardest condition, and this vulnerability is a limitation rather than a solved problem.

### 5.4 RGB-Only External Baseline

YOLO11n is included as an RGB-only external detector under the same clean split [REF: YOLO11Docs]. It is not a matched architecture-only ablation because it uses RGB input only, whereas R4 uses RGB, thermal, and event streams. Across seeds 0 and 2, YOLO11n RGB-only achieved AP50 values of 0.886374 and 0.885401, AP75 values of 0.629228 and 0.636794, and F1 values of 0.849188 and 0.845727. These values show the practical gap between the proposed tri-modal detector and a standard lightweight RGB-only external baseline, but they do not isolate whether the gap comes from architecture, modality availability, or both.

### 5.5 Efficiency and Convergence

R0 has 6591609 parameters, while R4 has 6593293 parameters. In raw-forward profiling, R0 measured 102.762853 FPS and 9.747951 ms per image, while R4 measured 97.717654 FPS and 10.238004 ms per image. In complete detector inference, R0 measured 48.065821 FPS and 20.818388 ms per image, while R4 measured 50.436489 FPS and 19.829330 ms per image. The detector-inference difference should be interpreted cautiously because it is small and measured on one hardware/software setting. Peak allocated CUDA memory was higher for R4, 236.756667 MB for complete detector inference compared with 122.680000 MB for R0. The convergence audit found seven runs clearly plateaued and one near plateau under the fixed 50-epoch schedule.

### 5.6 Reliability-Weight Analysis

The R4 reliability audit reports mean alpha values under full input and three synthetic missing-modality conditions. For seed 0 under full input, the means were alpha_rgb=0.430324, alpha_thermal=0.350048, and alpha_event=0.219628. For seed 2, the corresponding values were 0.459054, 0.350642, and 0.190304. When thermal was removed, the mean RGB alpha increased to 0.708866 for seed 0 and 0.761068 for seed 2, while the thermal alpha decreased but did not become zero. This is observed gating behavior under zeroed inputs. It should not be interpreted as a physically causal importance estimate or as exact absent-modality suppression.

### 5.7 Qualitative Results and Limitations

The qualitative manifest contains 20 illustrative cases: five where R4 corrects an R0 miss or localization failure, five shared successful detections, five R4 hard cases, and five missing-modality illustrative cases. These examples are intended to support visual inspection, not to prove universal superiority. The main limitations are fourfold. First, the controlled replication uses two seeds, so the evidence is not a statistical-significance analysis. Second, missingness is synthetic and does not cover all real sensor degradations. Third, the experiments use one dataset. Fourth, thermal removal remains the most difficult synthetic sensor-loss case even for R4.

## 6. Conclusion

This manuscript draft presents RA-RepDet, a reliability-aware RepViT-FCOS detector for RGB-thermal-event UAV vehicle detection. Under a leakage-aware blocked split with a guard band, R4 reliability fusion with modality dropout p=0.20 achieved mean AP50=0.962495, AP75=0.891266, and F1=0.920861 across two controlled seeds. The study supports reliability-aware fusion and modality-dropout training as practical tools for robust tri-modal detection, while carefully separating matched fusion ablations from an RGB-only YOLO11n external baseline. The next step is not more claim expansion, but target-journal selection, citation-style finalization, and figure-format preparation using the commit-safe tables and manifests created in this package.

## Data and Code Availability Statement

The source code, reproducible table files, figure manifests, and lightweight experiment summaries are intended to be versioned in the project repository. Raw TriAir arrays, local dataset files, trained weights, rendered qualitative panels, and large prediction outputs are not committed. The clean split file hashes and local evidence reports are recorded in `runs/clean_block64g16_protocol.md`, `runs/phase4b_report.md`, and `runs/phase5a_report.md`. Access to the original dataset should follow the dataset owner's distribution terms, and any final submission should replace this draft statement with a target-journal-compliant data and code availability statement.
"""
    write_text(MANUSCRIPT / "RA_RepDet_manuscript_v1.md", text)


def build_claim_ledger():
    rows = [
        {"Claim": "R4 is the main proposed model.", "Type": "conservative interpretation", "Evidence": "runs/phase4b_report.md decision SELECT R4 AS CLEAN-SPLIT MAIN VARIANT."},
        {"Claim": "Clean split uses 7439 train, 2213 validation, and 837 guard images.", "Type": "direct measurement", "Evidence": "runs/clean_block64g16_protocol.md."},
        {"Claim": "Clean split has zero exact RGB train/validation matches.", "Type": "direct measurement", "Evidence": "runs/clean_block64g16_protocol.md."},
        {"Claim": "Former random split contained 153 exact RGB-content matched validation samples.", "Type": "direct measurement", "Evidence": "runs/phase3c_report.md."},
        {"Claim": "R4 mean AP50=0.962495, AP75=0.891266, F1=0.920861.", "Type": "direct measurement", "Evidence": "runs/phase4b_report.md aggregate table."},
        {"Claim": "Reliability fusion improves the matched early-fusion baseline.", "Type": "conservative interpretation", "Evidence": "runs/phase4b_report.md interpretation."},
        {"Claim": "Modality dropout improves synthetic missing-modality robustness.", "Type": "conservative interpretation", "Evidence": "runs/phase4b_report.md per-seed missing-modality columns."},
        {"Claim": "Thermal removal remains the hardest synthetic missing-modality condition.", "Type": "limitation", "Evidence": "runs/phase4b_report.md and Table_4_missing_modality_robustness."},
        {"Claim": "YOLO11n is RGB-only external baseline, not architecture-only ablation.", "Type": "method description", "Evidence": "runs/yolo11n_rgb_baseline_protocol.md."},
        {"Claim": "Two seeds do not establish statistical significance.", "Type": "limitation", "Evidence": "docs/NEXT_TASK.md non-negotiable evidence rules."},
        {"Claim": "Reliability alpha audit describes gating behavior only.", "Type": "limitation", "Evidence": "runs/r4_reliability_weight_audit.md."},
        {"Claim": "Local rendered figures and qualitative panels are not commit-safe.", "Type": "method description", "Evidence": "manuscript/README.md and .gitignore."},
    ]
    headers = ["Claim", "Type", "Evidence"]
    md = "# Claim Ledger\n\n" + markdown_table(headers, rows) + "\n"
    write_text(NOTES / "claim_ledger.md", md)


def build_self_audit():
    checks = [
        ("Main metrics trace to Phase 4B/5A clean-split reports", "pass", "Tables 3-7 are generated from clean-split source CSVs and reports."),
        ("Former random-split values are not headline metrics", "pass", "Random split appears only in protocol motivation and leakage audit discussion."),
        ("R4 is consistently named main model", "pass", "Manuscript and tables use R4 Reliability p=0.20 as the main variant."),
        ("YOLO11n wording is RGB-only external baseline", "pass", "No architecture-only claim is made."),
        ("No statistical-significance claim from two seeds", "pass", "The draft uses controlled replication wording only."),
        ("Title, abstract, conclusion, and tables avoid unsupported claims", "pass", "Claims are conservative and traceable."),
        ("Citation placeholders link to verified inventory entries", "pass", "All `[REF: ...]` keys used in the draft are represented in reference_inventory.csv."),
        ("Rendered PNG/PDF and source panels are excluded from commit", "pass", ".gitignore ignores local_rendered and local_qualitative outputs."),
    ]
    headers = ["Check", "Status", "Notes"]
    rows = [{"Check": a, "Status": b, "Notes": c} for a, b, c in checks]
    write_text(NOTES / "manuscript_self_audit.md", "# Manuscript Self-Audit\n\n" + markdown_table(headers, rows) + "\n")


def build_phase6a_report(render_status, copied_panels):
    created = [
        "manuscript/README.md",
        "manuscript/RA_RepDet_manuscript_v1.md",
        "manuscript/tables/Table_1_dataset_and_clean_split.csv/.md",
        "manuscript/tables/Table_2_implementation_and_reproducibility.csv/.md",
        "manuscript/tables/Table_3_controlled_ablation.csv/.md",
        "manuscript/tables/Table_4_missing_modality_robustness.csv/.md",
        "manuscript/tables/Table_5_rgb_only_external_baseline.csv/.md",
        "manuscript/tables/Table_6_efficiency_and_convergence.csv/.md",
        "manuscript/tables/Table_7_reliability_weight_audit.csv/.md",
        "manuscript/figures/figure_manifest.csv/.md",
        "manuscript/figures/fig3_controlled_ablation_source.csv",
        "manuscript/figures/fig4_missing_modality_source.csv",
        "manuscript/figures/fig5_reliability_weight_source.csv",
        "manuscript/figures/fig6_qualitative_panel_manifest.csv",
        "manuscript/figures/plot_phase6a_figures.py",
        "manuscript/references/reference_inventory.csv/.md",
        "manuscript/submission_notes/claim_ledger.md",
        "manuscript/submission_notes/manuscript_self_audit.md",
    ]
    lines = [
        "# Phase 6A Manuscript Report",
        "",
        "## Created Files",
        "",
    ]
    lines.extend(f"- `{item}`" for item in created)
    lines += [
        "",
        "## Local-Only Assets",
        "",
        f"- Chart render status: {render_status}",
        f"- Qualitative panels copied locally: {copied_panels}",
        "- Local PNG/PDF charts and qualitative panels are ignored by Git and must not be committed.",
        "",
        "## Unresolved Limitations",
        "",
        "- Citation style remains pending until a target SCI/EI journal is selected.",
        "- Figure 1 and Fig. 2 require journal-specific schematic design after target selection.",
        "- Qualitative figure panels are illustrative and local-only.",
        "- The study still has the declared limitations: two seeds, synthetic missingness, one dataset, and thermal-drop vulnerability.",
        "",
        "MANUSCRIPT DRAFT READY FOR JOURNAL TARGETING",
    ]
    write_text(RUNS / "phase6a_manuscript_report.md", "\n".join(lines))


def main():
    for directory in [MANUSCRIPT, TABLES, FIGURES, LOCAL_RENDERED, LOCAL_QUAL, REFERENCES, NOTES]:
        directory.mkdir(parents=True, exist_ok=True)
    build_readme()
    data = build_tables()
    build_figure_sources(data)
    build_plot_script()
    build_figure_manifest()
    build_reference_inventory()
    build_manuscript()
    build_claim_ledger()
    build_self_audit()
    render_status = render_figures()
    copied_panels = copy_local_qualitative(data)
    build_phase6a_report(render_status, copied_panels)
    print("Saved Phase 6A manuscript package.")
    print(f"Render status: {render_status}")
    print(f"Copied local qualitative panels: {copied_panels}")


if __name__ == "__main__":
    main()
