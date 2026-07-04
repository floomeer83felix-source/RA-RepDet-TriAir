#!/usr/bin/env python
"""Dry-run validator for future non-final SIVP figure candidates.

This task intentionally implements dry-run validation only. A future non-dry
run, if separately approved, may write only local untracked files named
``*_candidate.*`` into a user-provided output directory outside the Git-tracked
final figure asset path. It must not create final ``Fig1``-``Fig6`` assets.
"""

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path


NUMERIC_TOKEN_RE = re.compile(r"(?<![A-Za-z])[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?(?![A-Za-z])")

FIGURE_SOURCES = {
    "Fig. 3": {
        "source": Path("manuscript/figures/fig3_controlled_ablation_source.csv"),
        "target_candidate": "Fig3_controlled_ablation_candidate.pdf",
        "expected_headers": ["Variant", "Seed", "F1", "AP50", "AP75"],
        "expected_rows": 8,
        "expected_numeric_tokens": 40,
        "future_build_plan": {
            "plot_type": "three-panel grouped point/bar comparison",
            "x_axis_grouping": "Variant on the x-axis, grouped or overlaid by seed 0 and seed 2",
            "y_axis_units": "F1@0.50, AP50, and AP75 in unitless [0, 1] metric units",
            "legend_entries": "seed 0; seed 2; optional mean marker if explicitly labeled as two-seed mean",
            "error_bar_policy": "No statistical error bars; optional min-max whisker may be shown only as the two-seed range.",
            "required_caption_text": "Controlled two-seed full-modality AP50/AP75/F1 comparison.",
            "source_to_panel_mapping": "F1 -> panel A; AP50 -> panel B; AP75 -> panel C.",
        },
    },
    "Fig. 4": {
        "source": Path("manuscript/figures/fig4_missing_modality_source.csv"),
        "target_candidate": "Fig4_missing_modality_robustness_candidate.pdf",
        "expected_headers": ["Variant", "Seed", "Condition", "AP50"],
        "expected_rows": 18,
        "expected_numeric_tokens": 55,
        "future_build_plan": {
            "plot_type": "grouped bar or grouped point plot",
            "x_axis_grouping": "Synthetic removal condition on the x-axis, grouped by R1/R2/R4 and seed",
            "y_axis_units": "AP50 in unitless [0, 1] metric units",
            "legend_entries": "R1 seed 0/2; R2 seed 0/2; R4 seed 0/2, or variant means with seed points overlaid",
            "error_bar_policy": "No statistical error bars; optional min-max whisker may be shown only as the two-seed range.",
            "required_caption_text": "Missing-modality robustness.",
            "source_to_panel_mapping": "w/o RGB, w/o Thermal, and w/o Event conditions map to the three x-axis groups or panels.",
        },
    },
    "Fig. 5": {
        "source": Path("manuscript/figures/fig5_reliability_weight_source.csv"),
        "target_candidate": "Fig5_reliability_weight_audit_candidate.pdf",
        "expected_headers": [
            "Seed",
            "Mode",
            "alpha_rgb_mean",
            "alpha_thermal_mean",
            "alpha_event_mean",
            "alpha_rgb_std",
            "alpha_thermal_std",
            "alpha_event_std",
        ],
        "expected_rows": 8,
        "expected_numeric_tokens": 56,
        "future_build_plan": {
            "plot_type": "grouped alpha-weight audit plot",
            "x_axis_grouping": "Input mode on the x-axis, faceted or grouped by seed",
            "y_axis_units": "Reliability alpha mean in unitless [0, 1] weights",
            "legend_entries": "alpha_rgb; alpha_thermal; alpha_event",
            "error_bar_policy": "Use only the provided std columns if variability bars are shown; do not infer confidence intervals.",
            "required_caption_text": "Reliability-weight audit.",
            "source_to_panel_mapping": "mean columns map to bar or point height; std columns map only to explicitly labeled variability bars.",
        },
    },
}


def read_and_validate(root, figure_id, spec):
    path = root / spec["source"]
    try:
        text = path.read_text(encoding="utf-8-sig")
        data = path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"{figure_id}: cannot read {path}: {exc}") from exc

    reader = csv.DictReader(text.splitlines())
    headers = reader.fieldnames or []
    rows = list(reader)
    numeric_tokens = len(NUMERIC_TOKEN_RE.findall(text))
    sha256 = hashlib.sha256(data).hexdigest()

    if headers != spec["expected_headers"]:
        raise RuntimeError(
            f"{figure_id}: header mismatch for {spec['source']}; "
            f"expected {spec['expected_headers']}, found {headers}"
        )
    if len(rows) != spec["expected_rows"]:
        raise RuntimeError(
            f"{figure_id}: row-count mismatch for {spec['source']}; "
            f"expected {spec['expected_rows']}, found {len(rows)}"
        )
    if numeric_tokens != spec["expected_numeric_tokens"]:
        raise RuntimeError(
            f"{figure_id}: numerical-token-count mismatch for {spec['source']}; "
            f"expected {spec['expected_numeric_tokens']}, found {numeric_tokens}"
        )

    return {
        "figure_id": figure_id,
        "source": str(spec["source"]),
        "target_candidate": spec["target_candidate"],
        "headers": headers,
        "row_count": len(rows),
        "numerical_token_count": numeric_tokens,
        "sha256": sha256,
        "future_build_plan": spec["future_build_plan"],
    }


def print_result(result):
    print(f"{result['figure_id']}")
    print(f"  source: {result['source']}")
    print(f"  target candidate filename: {result['target_candidate']}")
    print(f"  headers: {', '.join(result['headers'])}")
    print(f"  row_count: {result['row_count']}")
    print(f"  numerical_token_count: {result['numerical_token_count']}")
    print(f"  sha256: {result['sha256']}")
    print("  future build plan:")
    for key, value in result["future_build_plan"].items():
        print(f"    {key}: {value}")


def main():
    parser = argparse.ArgumentParser(description="Validate frozen Fig. 3-5 sources without rendering artwork.")
    parser.add_argument("--dry-run", action="store_true", required=True, help="Required; no artwork or files are written.")
    parser.add_argument("--root", default=".", help="Repository root.")
    args = parser.parse_args()

    if not args.dry_run:
        print("Only --dry-run mode is implemented for this source-lock task.", file=sys.stderr)
        return 2

    root = Path(args.root).resolve()
    print("RA-RepDet SIVP figure candidate dry run")
    print(f"root: {root}")
    print("mode: dry-run validation only")
    print("write_policy: no files are written; no PDF/PNG/SVG/JPG artwork is rendered")
    print(
        "future_non_dry_run_policy: only local untracked *_candidate.* files may be written "
        "to a user-provided output directory outside the Git-tracked final asset path"
    )

    try:
        results = [read_and_validate(root, figure_id, spec) for figure_id, spec in FIGURE_SOURCES.items()]
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for result in results:
        print_result(result)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
