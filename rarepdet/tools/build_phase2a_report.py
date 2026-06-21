#!/usr/bin/env python
"""Build the consolidated Phase 2A report."""

from pathlib import Path

from phase2a_common import PROJECT_ROOT, markdown_table, read_csv


def section_from_csv(title, path, headers=None):
    rows = read_csv(path)
    if headers is None and rows:
        headers = list(rows[0].keys())
    headers = headers or []
    lines = [f"## {title}", ""]
    if rows:
        lines.extend(markdown_table(headers, rows))
    else:
        lines.append("NA")
    lines.append("")
    return lines


def main():
    out_path = PROJECT_ROOT / "runs" / "phase2a_report.md"
    lines = [
        "# Phase 2A Report",
        "",
        "Scope: post-processing only. E0/E1/E2 were not retrained, and detector/Dataset source files were not modified.",
        "",
    ]
    lines.extend(
        section_from_csv(
            "Paper Main Results At Score Threshold 0.50",
            "runs/phase2a_main_results.csv",
            [
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
            ],
        )
    )
    lines.extend(section_from_csv("E0 Phase 2A Profile", "runs/phase2a_profile_e0/profile_results.csv"))
    lines.extend(section_from_csv("E2 Phase 2A Profile", "runs/phase2a_profile_e2/profile_results.csv"))
    lines.extend(section_from_csv("Brightness-Proxy Grouped Evaluation", "runs/phase2a_brightness_proxy/brightness_proxy_results.csv"))
    lines.extend(section_from_csv("Reliability Alpha Statistics", "runs/phase2a_alpha/alpha_mode_summary.csv"))
    lines.extend(
        [
            "## Notes",
            "",
            "- Brightness-proxy groups are RGB mean-intensity terciles, not day/night labels.",
            "- Precision, Recall, and F1 in the main table use score threshold 0.50.",
            "- AP50/AP75 are score-ranked AP values from the same completed checkpoints.",
            "- Raw forward profiling measures the model backbone/FPN path on a fixed random tensor.",
            "- Detector inference profiling measures full torchvision FCOS inference on a fixed random tensor.",
            "",
        ]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
