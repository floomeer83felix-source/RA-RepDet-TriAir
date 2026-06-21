#!/usr/bin/env python
"""Generate PowerShell commands for follow-up RarePDet experiments."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYTHON = r"C:\Users\xinnan\.conda\envs\pytorch\python.exe"
DATA = r"D:\download\triair"
TRAIN = r"D:\download\triair\splits\train.txt"
VAL = r"D:\download\triair\splits\val.txt"


def train_cmd(model, epochs, out, dropout=0.0):
    return (
        f'& "{PYTHON}" rarepdet\\train_early_fusion.py --model {model} --data {DATA} '
        f"--train-split {TRAIN} --val-split {VAL} --epochs {epochs} --batch-size 4 "
        f"--img-size 640 --device cuda --lr 1e-4 --num-workers 0 "
        f"--modality-dropout {dropout} --out {out}"
    )


def missing_cmd(model, weights, out):
    return (
        f'& "{PYTHON}" rarepdet\\tools\\eval_missing_modality.py --model {model} --data {DATA} '
        f"--split-file {VAL} --weights {weights} --img-size 640 --device cuda "
        f"--batch-size 4 --score-thr 0.001 --out {out}"
    )


def main():
    lines = [
        "# RarePDet follow-up experiment commands",
        "# Generated only; this file does not execute experiments by itself.",
        "",
        "# A. Dropout ratio ablation",
    ]
    for ratio in (0.05, 0.10, 0.20, 0.30):
        tag = str(ratio).replace(".", "")
        lines.append(f"# reliability + dropout {ratio:.2f}")
        lines.append(train_cmd("reliability", 50, f"runs\\E_dropout{tag}_reliability_repvit_fcos_e50", ratio))
        lines.append("")

    lines.extend(
        [
            "# B. Backbone scale ablation",
            "# TODO: current train_early_fusion.py does not expose a --backbone/--timm-model argument.",
            "# TODO: add a non-disruptive model_name argument after current E0/E1/E2 jobs finish, then run:",
            "# repvit_m0_9, repvit_m1_0, repvit_m1_1",
            "",
            "# C. Epoch extension",
            "# E0 early 100 epoch",
            train_cmd("early", 100, "runs\\E0_early_repvit_fcos_e100", 0.0),
            "",
            "# E1 reliability 100 epoch",
            train_cmd("reliability", 100, "runs\\E1_reliability_repvit_fcos_e100", 0.0),
            "",
            "# E2 reliability dropout 0.15 100 epoch",
            train_cmd("reliability", 100, "runs\\E2_reliability_dropout015_repvit_fcos_e100", 0.15),
            "",
            "# D. Missing modality evaluation commands",
            "# E0 missing-modality eval",
            missing_cmd(
                "early",
                r"runs\E0_early_repvit_fcos_e50\weights\best.pt",
                r"runs\E0_early_repvit_fcos_e50\missing_modality",
            ),
            "",
            "# E1 missing-modality eval",
            missing_cmd(
                "reliability",
                r"runs\E1_reliability_repvit_fcos_e50\weights\best.pt",
                r"runs\E1_reliability_repvit_fcos_e50\missing_modality",
            ),
            "",
            "# E2 missing-modality eval",
            missing_cmd(
                "reliability",
                r"runs\E2_reliability_dropout015_repvit_fcos_e50\weights\best.pt",
                r"runs\E2_reliability_dropout015_repvit_fcos_e50\missing_modality",
            ),
            "",
        ]
    )

    out_dir = PROJECT_ROOT / "runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    ps1 = out_dir / "next_experiment_commands.ps1"
    txt = out_dir / "next_experiment_commands.txt"
    content = "\n".join(lines)
    ps1.write_text(content + "\n", encoding="utf-8")
    txt.write_text(content + "\n", encoding="utf-8")
    print(f"Saved: {ps1}")
    print(f"Saved: {txt}")


if __name__ == "__main__":
    main()
