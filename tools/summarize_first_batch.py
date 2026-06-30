#!/usr/bin/env python
"""Summarize E0/E1/E2 RarePDet eval_results.txt files."""

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]


METHODS = [
    ("E0 Early Fusion", PROJECT_ROOT / "runs" / "E0_early_repvit_fcos_e50" / "eval" / "eval_results.txt"),
    ("E1 Reliability Fusion", PROJECT_ROOT / "runs" / "E1_reliability_repvit_fcos_e50" / "eval" / "eval_results.txt"),
    (
        "E2 Reliability + Dropout 0.15",
        PROJECT_ROOT / "runs" / "E2_reliability_dropout015_repvit_fcos_e50" / "eval" / "eval_results.txt",
    ),
]


def parse_eval(path):
    if not path.is_file():
        raise FileNotFoundError(f"Missing eval result file: {path}")
    text = path.read_text(encoding="utf-8")
    values = {}
    for key in ("Precision", "Recall", "AP50", "AP75", "GT boxes", "Predictions", "Mean Confidence"):
        match = re.search(rf"^{re.escape(key)}:\s*([0-9.]+)", text, flags=re.MULTILINE)
        if not match:
            raise ValueError(f"Could not parse '{key}' from {path}")
        value = match.group(1)
        values[key] = int(value) if key in ("GT boxes", "Predictions") else float(value)
    return values


def main():
    rows = []
    for method, path in METHODS:
        values = parse_eval(path)
        rows.append((method, values))

    best_ap50 = max(rows, key=lambda item: item[1]["AP50"])
    best_recall = max(rows, key=lambda item: item[1]["Recall"])
    e0 = rows[0][1]
    e1 = rows[1][1]
    e2 = rows[2][1]
    e1_vs_e0 = "提升" if e1["AP50"] > e0["AP50"] else "下降或持平"
    e2_vs_e1 = "提升" if e2["AP50"] > e1["AP50"] else "下降或持平"

    lines = [
        "Method | Precision | Recall | AP50 | AP75 | GT boxes | Predictions | Mean Confidence",
        "--- | ---: | ---: | ---: | ---: | ---: | ---: | ---:",
    ]
    for method, values in rows:
        lines.append(
            f"{method} | {values['Precision']:.6f} | {values['Recall']:.6f} | "
            f"{values['AP50']:.6f} | {values['AP75']:.6f} | {values['GT boxes']} | "
            f"{values['Predictions']} | {values['Mean Confidence']:.6f}"
        )

    lines.extend(
        [
            "",
            f"AP50 最高: {best_ap50[0]} ({best_ap50[1]['AP50']:.6f})",
            f"Recall 最高: {best_recall[0]} ({best_recall[1]['Recall']:.6f})",
            f"E1 相比 E0: {e1_vs_e0} (AP50 {e0['AP50']:.6f} -> {e1['AP50']:.6f})",
            f"E2 相比 E1: {e2_vs_e1} (AP50 {e1['AP50']:.6f} -> {e2['AP50']:.6f})",
            "下一步建议: 需要做 missing-modality test，用于验证 reliability fusion 在 RGB/Thermal/Event 缺失或退化时是否更稳健。",
        ]
    )

    out_path = PROJECT_ROOT / "runs" / "summary_first_batch.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved summary to: {out_path}")


if __name__ == "__main__":
    main()
