#!/usr/bin/env python
"""Validate and render non-final SIVP quantitative figure candidates.

The render mode writes only local, Git-ignored review candidates under
``runs/local_candidate_figures/``. It never writes final Fig. 1-6 assets and
does not touch the SIVP LaTeX body.
"""

import argparse
import csv
import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


NUMERIC_TOKEN_RE = re.compile(r"(?<![A-Za-z])[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?(?![A-Za-z])")
WATERMARK = "CANDIDATE — NOT FINAL"

FIGURE_SOURCES = {
    "Fig. 3": {
        "source": Path("manuscript/figures/fig3_controlled_ablation_source.csv"),
        "target_candidate": "Fig3_controlled_ablation_candidate.pdf",
        "expected_headers": ["Variant", "Seed", "F1", "AP50", "AP75"],
        "expected_rows": 8,
        "expected_numeric_tokens": 40,
        "expected_sha256": "23e2984adac08ebd6584e1c8d56f82d3cdd0dfb9e5e32047d5064481076d21dc",
        "future_build_plan": {
            "plot_type": "three-panel grouped point comparison",
            "x_axis_grouping": "Variant on the x-axis, overlaid by seed 0 and seed 2",
            "y_axis_units": "F1@0.50, AP50, and AP75 in unitless [0, 1] metric units",
            "legend_entries": "seed 0; seed 2",
            "error_bar_policy": "No error bars, confidence intervals, p-values, or significance marks.",
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
        "expected_sha256": "aea82341ac37547ece40428e56bd3d98fabf299304a4b24067a7705eaf642fde",
        "future_build_plan": {
            "plot_type": "grouped point plot",
            "x_axis_grouping": "Synthetic removal condition on the x-axis, grouped by R1/R2/R4 and seed",
            "y_axis_units": "AP50 in unitless [0, 1] metric units",
            "legend_entries": "R1/R2/R4 colors and seed 0/2 markers",
            "error_bar_policy": "No statistical error bars or inferred confidence intervals.",
            "required_caption_text": "Missing-modality robustness.",
            "source_to_panel_mapping": "w/o RGB, w/o Thermal, and w/o Event map to the three x-axis groups.",
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
        "expected_sha256": "ef93dca475e9a1fa704856952951fbe47ebb701c9e559ea60abf46d861a1239c",
        "future_build_plan": {
            "plot_type": "two-panel grouped alpha-weight bar plot",
            "x_axis_grouping": "Input mode on the x-axis, one panel per seed",
            "y_axis_units": "Reliability alpha mean in unitless [0, 1] weights",
            "legend_entries": "alpha_rgb; alpha_thermal; alpha_event",
            "error_bar_policy": "Use only the provided std columns as explicitly labeled +/- std bars.",
            "required_caption_text": "Reliability-weight audit.",
            "source_to_panel_mapping": "Mean columns map to bars; std columns map only to labeled variability bars.",
        },
    },
}

FINAL_ASSET_DIRS = [
    Path("submission/sivp/figures"),
    Path("figures"),
    Path("manuscript/figures"),
]

REQUIRED_LOCAL_FILENAMES = {
    "Fig3_controlled_ablation_candidate.pdf",
    "Fig4_missing_modality_robustness_candidate.pdf",
    "Fig5_reliability_weight_audit_candidate.pdf",
    "candidate_render_manifest.json",
}


def relpath_for_git(root, path):
    return Path(path).resolve().relative_to(root).as_posix()


def is_relative_to(path, base):
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


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
    if sha256 != spec["expected_sha256"]:
        raise RuntimeError(
            f"{figure_id}: SHA256 mismatch for {spec['source']}; "
            f"expected {spec['expected_sha256']}, found {sha256}"
        )

    return {
        "figure_id": figure_id,
        "source": str(spec["source"]),
        "target_candidate": spec["target_candidate"],
        "headers": headers,
        "row_count": len(rows),
        "numerical_token_count": numeric_tokens,
        "sha256": sha256,
        "rows": rows,
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


def git_check_ignored(root, path):
    rel = relpath_for_git(root, path)
    result = subprocess.run(
        ["git", "check-ignore", "-q", "--", rel],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def validate_output_dir(root, output_dir):
    output = (root / output_dir).resolve() if not Path(output_dir).is_absolute() else Path(output_dir).resolve()
    local_root = (root / "runs/local_candidate_figures").resolve()
    if not is_relative_to(output, local_root):
        raise RuntimeError(f"output directory must resolve under {local_root}, found {output}")

    for final_dir in FINAL_ASSET_DIRS:
        final_root = (root / final_dir).resolve()
        if output == final_root or is_relative_to(output, final_root):
            raise RuntimeError(f"output directory cannot be inside final-asset directory {final_root}")

    expected_paths = [output / name for name in REQUIRED_LOCAL_FILENAMES]
    if output.exists():
        unexpected = [
            path.name
            for path in output.iterdir()
            if path.is_file() and path.name not in REQUIRED_LOCAL_FILENAMES and not path.name.endswith(".tmp")
        ]
        if unexpected:
            raise RuntimeError(f"output directory contains unexpected files: {', '.join(sorted(unexpected))}")

    for path in expected_paths:
        if not git_check_ignored(root, path):
            raise RuntimeError(f"candidate output path is not ignored by Git: {relpath_for_git(root, path)}")
    return output


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"non-numeric value in frozen CSV: {value!r}") from exc


def add_watermark_and_footer(fig, result):
    fig.text(
        0.5,
        0.52,
        WATERMARK,
        ha="center",
        va="center",
        fontsize=30,
        color="#b00020",
        alpha=0.16,
        rotation=18,
        weight="bold",
    )
    fig.text(
        0.01,
        0.012,
        f"{WATERMARK} | source: {result['source']} | sha256: {result['sha256']}",
        ha="left",
        va="bottom",
        fontsize=5.2,
        color="#333333",
    )


def save_pdf_atomic(fig, output_path):
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        fig.savefig(tmp_path, format="pdf", bbox_inches="tight")
        tmp_path.replace(output_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def render_fig3(result, output_path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    variants = ["R0 Early Fusion", "R1 Reliability p=0.00", "R2 Reliability p=0.15", "R4 Reliability p=0.20"]
    metrics = [("F1", "(a) F1@0.50"), ("AP50", "(b) AP50"), ("AP75", "(c) AP75")]
    seed_offsets = {"0": -0.07, "2": 0.07}
    seed_markers = {"0": "o", "2": "s"}
    fig, axes = plt.subplots(1, 3, figsize=(174 / 25.4, 78 / 25.4), sharey=False)
    row_map = {(row["Variant"], row["Seed"]): row for row in result["rows"]}

    for ax, (metric, title) in zip(axes, metrics):
        for x, variant in enumerate(variants):
            for seed in ("0", "2"):
                row = row_map[(variant, seed)]
                label = f"seed {seed}" if x == 0 else None
                ax.scatter(
                    x + seed_offsets[seed],
                    to_float(row[metric]),
                    marker=seed_markers[seed],
                    s=36,
                    edgecolor="#222222",
                    linewidth=0.5,
                    label=label,
                    zorder=3,
                )
        ax.set_title(title, fontsize=8)
        ax.set_xticks(range(len(variants)))
        ax.set_xticklabels(["R0\nEarly", "R1\np=0.00", "R2\np=0.15", "R4\np=0.20"], fontsize=6.6)
        ax.set_ylabel(metric if metric != "F1" else "F1@0.50", fontsize=7)
        ax.grid(axis="y", color="#dddddd", linewidth=0.6)
        ax.set_ylim(0.80, 0.99)
    axes[0].legend(loc="lower right", fontsize=6, frameon=False)
    fig.suptitle("Controlled clean-split ablation (source rows shown as seed points)", fontsize=9)
    add_watermark_and_footer(fig, result)
    fig.tight_layout(rect=(0, 0.06, 1, 0.90))
    save_pdf_atomic(fig, output_path)
    plt.close(fig)


def render_fig4(result, output_path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conditions = ["w/o RGB", "w/o Thermal", "w/o Event"]
    variants = ["R1 Reliability p=0.00", "R2 Reliability p=0.15", "R4 Reliability p=0.20"]
    variant_label = {
        "R1 Reliability p=0.00": "R1 p=0.00",
        "R2 Reliability p=0.15": "R2 p=0.15",
        "R4 Reliability p=0.20": "R4 p=0.20",
    }
    colors = {
        "R1 Reliability p=0.00": "#4c78a8",
        "R2 Reliability p=0.15": "#59a14f",
        "R4 Reliability p=0.20": "#e15759",
    }
    seed_offsets = {"0": -0.035, "2": 0.035}
    variant_offsets = {"R1 Reliability p=0.00": -0.22, "R2 Reliability p=0.15": 0.0, "R4 Reliability p=0.20": 0.22}
    seed_markers = {"0": "o", "2": "s"}

    fig, ax = plt.subplots(figsize=(174 / 25.4, 82 / 25.4))
    for row in result["rows"]:
        condition = row["Condition"]
        variant = row["Variant"]
        seed = row["Seed"]
        x = conditions.index(condition) + variant_offsets[variant] + seed_offsets[seed]
        ax.scatter(
            x,
            to_float(row["AP50"]),
            color=colors[variant],
            marker=seed_markers[seed],
            s=38,
            edgecolor="#222222",
            linewidth=0.45,
            zorder=3,
        )

    variant_handles = [
        plt.Line2D([0], [0], color=colors[variant], marker="o", linestyle="", label=variant_label[variant])
        for variant in variants
    ]
    seed_handles = [
        plt.Line2D([0], [0], color="#333333", marker=seed_markers[seed], linestyle="", label=f"seed {seed}")
        for seed in ("0", "2")
    ]
    ax.legend(handles=variant_handles + seed_handles, loc="lower right", fontsize=6.3, frameon=False, ncol=2)
    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels(conditions, fontsize=7)
    ax.set_ylabel("AP50", fontsize=8)
    ax.set_title("Missing-modality robustness (18 source rows shown once)", fontsize=9)
    ax.set_ylim(0.25, 1.0)
    ax.grid(axis="y", color="#dddddd", linewidth=0.6)
    add_watermark_and_footer(fig, result)
    fig.tight_layout(rect=(0, 0.06, 1, 0.94))
    save_pdf_atomic(fig, output_path)
    plt.close(fig)


def render_fig5(result, output_path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    modes = ["full", "no_rgb", "no_thermal", "no_event"]
    alpha_fields = [
        ("alpha_rgb_mean", "alpha_rgb_std", "alpha_rgb", "#4c78a8"),
        ("alpha_thermal_mean", "alpha_thermal_std", "alpha_thermal", "#f28e2b"),
        ("alpha_event_mean", "alpha_event_std", "alpha_event", "#59a14f"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(174 / 25.4, 82 / 25.4), sharey=True)
    width = 0.22
    offsets = [-width, 0.0, width]

    for ax, seed in zip(axes, ("0", "2")):
        seed_rows = {row["Mode"]: row for row in result["rows"] if row["Seed"] == seed}
        for offset, (mean_field, std_field, label, color) in zip(offsets, alpha_fields):
            values = [to_float(seed_rows[mode][mean_field]) for mode in modes]
            stds = [to_float(seed_rows[mode][std_field]) for mode in modes]
            xs = [index + offset for index in range(len(modes))]
            ax.bar(xs, values, width=width, color=color, label=label, alpha=0.86)
            ax.errorbar(xs, values, yerr=stds, fmt="none", ecolor="#222222", linewidth=0.7, capsize=2)
        ax.set_title(f"seed {seed}", fontsize=8)
        ax.set_xticks(range(len(modes)))
        ax.set_xticklabels(["full", "no\nrgb", "no\nthermal", "no\nevent"], fontsize=7)
        ax.set_ylim(0, 0.95)
        ax.grid(axis="y", color="#dddddd", linewidth=0.6)
        ax.text(0.02, 0.95, "+/- std shown", transform=ax.transAxes, ha="left", va="top", fontsize=6)

    axes[0].set_ylabel("Reliability alpha mean", fontsize=8)
    axes[1].legend(loc="upper right", fontsize=6, frameon=False)
    fig.suptitle("Reliability-weight audit (observed gating, not causal importance)", fontsize=9)
    add_watermark_and_footer(fig, result)
    fig.tight_layout(rect=(0, 0.06, 1, 0.90))
    save_pdf_atomic(fig, output_path)
    plt.close(fig)


def render_candidates(root, output_dir, results, argv):
    output = validate_output_dir(root, output_dir)
    output.mkdir(parents=True, exist_ok=True)

    renderers = {
        "Fig. 3": render_fig3,
        "Fig. 4": render_fig4,
        "Fig. 5": render_fig5,
    }
    generated = []
    for result in results:
        path = output / result["target_candidate"]
        renderers[result["figure_id"]](result, path)
        generated.append(
            {
                "figure_id": result["figure_id"],
                "filename": path.name,
                "path": relpath_for_git(root, path),
                "bytes": path.stat().st_size,
                "final_asset_status": "not_final",
            }
        )

    import matplotlib

    manifest = {
        "build_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "command_arguments": argv,
        "python_version": platform.python_version(),
        "matplotlib_version": matplotlib.__version__,
        "final_asset_status": "not_final",
        "source_validation": [
            {
                "figure_id": result["figure_id"],
                "source": result["source"],
                "sha256": result["sha256"],
                "headers": result["headers"],
                "row_count": result["row_count"],
                "numerical_token_count": result["numerical_token_count"],
            }
            for result in results
        ],
        "generated_candidates": generated,
        "local_only_policy": "Review candidates only; do not commit, rename as final assets, or insert into LaTeX.",
    }
    manifest_path = output / "candidate_render_manifest.json"
    tmp_manifest = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    try:
        tmp_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp_manifest.replace(manifest_path)
    finally:
        if tmp_manifest.exists():
            tmp_manifest.unlink()
    return manifest


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description="Validate or render non-final Fig. 3-5 candidates.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Validate frozen CSV sources without writing files.")
    mode.add_argument("--render-candidates", action="store_true", help="Render local, ignored, non-final candidate PDFs.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--output-dir", help="Required with --render-candidates; must be under runs/local_candidate_figures/.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    try:
        results = [read_and_validate(root, figure_id, spec) for figure_id, spec in FIGURE_SOURCES.items()]
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        if args.output_dir:
            print("ERROR: --output-dir is only valid with --render-candidates", file=sys.stderr)
            return 2
        print("RA-RepDet SIVP figure candidate dry run")
        print(f"root: {root}")
        print("mode: dry-run validation only")
        print("write_policy: no files are written; no PDF/PNG/SVG/JPG artwork is rendered")
        print("future_non_dry_run_policy: only local untracked *_candidate.pdf files may be written under runs/local_candidate_figures/")
        for result in results:
            print_result(result)
        print("RESULT: PASS")
        return 0

    if args.render_candidates:
        if not args.output_dir:
            print("ERROR: --output-dir is required with --render-candidates", file=sys.stderr)
            return 2
        try:
            manifest = render_candidates(root, args.output_dir, results, argv)
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print("RA-RepDet SIVP candidate render")
        print(f"root: {root}")
        print(f"output_dir: {args.output_dir}")
        for item in manifest["generated_candidates"]:
            print(f"  wrote {item['path']} ({item['bytes']} bytes, {item['final_asset_status']})")
        print(f"  wrote {Path(args.output_dir) / 'candidate_render_manifest.json'}")
        print("RESULT: PASS")
        return 0

    print("ERROR: unsupported mode", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
