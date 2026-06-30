#!/usr/bin/env python
"""Build the Phase 3C conclusion report from lightweight audit outputs."""

import argparse
import csv
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.tools.split_audit_common import RUNS_DIR, markdown_table  # noqa: E402


def read_csv(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric(rows, name, default="NA"):
    for row in rows:
        if row.get("Metric") == name:
            return row.get("Value", default)
    return default


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def recommended_candidate(rows):
    for row in rows:
        if str(row.get("recommended", "")).lower() == "yes":
            return row
    return None


def model_subset_rows(rows):
    return [row for row in rows if row.get("model") and row.get("model") != "subset_only"]


def ranking_statement(rows):
    useful = model_subset_rows(rows)
    by_subset = {}
    for row in useful:
        by_subset.setdefault(row.get("subset"), []).append(row)
    statements = []
    for subset, subset_rows in sorted(by_subset.items()):
        ranked = []
        for row in subset_rows:
            ap50 = to_float(row.get("ap50"))
            if ap50 is not None:
                ranked.append((ap50, row))
        if not ranked:
            statements.append(f"- {subset}: NA.")
            continue
        ranked.sort(key=lambda item: item[0], reverse=True)
        best = ranked[0][1]
        second = ranked[1][1] if len(ranked) > 1 else None
        if second:
            gap = ranked[0][0] - ranked[1][0]
            statements.append(
                f"- {subset}: {best.get('model')} leads AP50 by {gap:.6f} over {second.get('model')}."
            )
        else:
            statements.append(f"- {subset}: only {best.get('model')} is available.")
    return statements


def main():
    parser = argparse.ArgumentParser(description="Build Phase 3C report.")
    parser.add_argument("--out", default="runs")
    args = parser.parse_args()

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = PROJECT_ROOT / out_dir

    rgb_summary = read_csv(out_dir / "rgb_cross_split_duplicate_summary.csv")
    blocked_rows = read_csv(out_dir / "blocked_split_proposal_summary.csv")
    strata_rows = read_csv(out_dir / "rgb_separation_strata_summary.csv")
    rec = recommended_candidate(blocked_rows)

    matched_val = metric(rgb_summary, "exact_rgb_matched_val_images")
    matched_val_frac = metric(rgb_summary, "exact_rgb_matched_val_fraction")
    matched_train = metric(rgb_summary, "exact_rgb_matched_train_images")
    matched_train_frac = metric(rgb_summary, "exact_rgb_matched_train_fraction")
    group_count = metric(rgb_summary, "cross_split_rgb_groups")
    interpretation = metric(rgb_summary, "interpretation_label")
    has_rgb_duplicates = to_float(matched_val) is not None and to_float(matched_val) > 0

    if has_rgb_duplicates:
        benchmark_statement = (
            "The current random split should not be treated as a publication-grade independent benchmark, "
            "because exact RGB-content train/validation overlap exists even though full five-channel byte duplicates were not claimed."
        )
        next_action = (
            "Do not begin manuscript drafting or final 100-epoch runs on the current random split. "
            "Use the blocked-split recommendation for the next retraining phase."
        )
    else:
        benchmark_statement = (
            "No exact RGB-content duplicates were found, but the Phase 3B adjacent-frame diagnostics still justify conservative split wording."
        )
        next_action = "Proceed only after reviewing the blocked-split diagnostics and closest-pair evidence."

    if rec:
        blocked_statement = (
            f"Recommended candidate: `{rec['candidate']}` with block size {rec['block_size']} and guard band {rec['guard_band']}. "
            f"It has {rec['exact_rgb_matched_val_images']} exact RGB matched validation samples, "
            f"{rec['id_guard_violations']} same-family guard violations, "
            f"{rec['val_images']} validation images, and {rec['val_gt_boxes']} validation GT boxes."
        )
        next_action += " Retrain only E2 (p=0.15) and E4 (p=0.20) on this candidate in the next phase."
    else:
        blocked_statement = (
            "No candidate met the zero exact RGB-content criterion. Increase block size/guarding before any clean-split retraining."
        )

    lines = [
        "# Phase 3C Report",
        "",
        "## 1. Exact RGB-Content Cross-Split Duplicates",
        "",
        f"- Interpretation label: **{interpretation}**",
        f"- Matched validation samples: {matched_val} ({matched_val_frac})",
        f"- Matched train samples: {matched_train} ({matched_train_frac})",
        f"- Cross-split RGB-content groups: {group_count}",
        "- This is an RGB-channel content audit only; it is not a full multimodal byte-duplication claim.",
        "",
        "## 2. Publication-Grade Benchmark Suitability",
        "",
        benchmark_statement,
        "",
        "## 3. Blocked-Split Candidate Recommendation",
        "",
        blocked_statement,
        "",
        "## 4. E2/E4 Ranking Across RGB-Separation Strata",
        "",
        "The strata are diagnostics only. The higher-RGB-separation subset is not a clean independent test set.",
        "",
    ]
    lines.extend(ranking_statement(strata_rows))
    lines.extend(
        [
            "",
            "## 5. Next Safe Action",
            "",
            next_action,
            "",
            "Keep E2 as the accuracy-first variant and E4 as the robustness-first variant until a clean blocked-split comparison is available.",
            "",
            "## Key Tables",
            "",
            "### RGB Duplicate Summary",
            "",
        ]
    )
    lines.extend(markdown_table(["Metric", "Value", "Notes"], rgb_summary))
    lines.extend(["", "### Blocked Split Candidates", ""])
    lines.extend(
        markdown_table(
            [
                "candidate",
                "block_size",
                "guard_band",
                "train_images",
                "val_images",
                "guard_images",
                "val_share_all_images",
                "exact_rgb_matched_val_images",
                "id_guard_violations",
                "val_gt_boxes",
                "recommended",
            ],
            blocked_rows,
        )
    )
    lines.extend(["", "### RGB Separation Strata Evaluation", ""])
    lines.extend(
        markdown_table(
            ["subset", "model", "image_count", "gt_boxes", "precision", "recall", "f1", "ap50", "ap75", "predictions"],
            strata_rows,
        )
    )
    lines.append("")
    (out_dir / "phase3c_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {out_dir / 'phase3c_report.md'}")


if __name__ == "__main__":
    main()
