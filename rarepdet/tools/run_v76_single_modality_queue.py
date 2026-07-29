#!/usr/bin/env python
"""Run the frozen nine-run V76 single-modality queue and standardized evaluations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "runs" / "v76_triair_single_modality_ablation"
MODES = ("rgb", "thermal", "event")
SEEDS = (0, 1, 2)
TRAIN_SPLIT = PROJECT_ROOT / "reproducibility" / "v40_expanded_adjacency_component_split_v2" / "manifests" / "v40_expanded_adjacency_component_disjoint_train.txt"
VAL_SPLIT = PROJECT_ROOT / "reproducibility" / "v40_expanded_adjacency_component_split_v2" / "manifests" / "v40_expanded_adjacency_component_disjoint_val.txt"


def run(command: list[str]) -> None:
    print(subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if not TRAIN_SPLIT.is_file() or not VAL_SPLIT.is_file():
        raise FileNotFoundError("Frozen V40 train/validation manifests are required.")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "protocol.json").write_text(json.dumps({"status": "V76_SINGLE_MODALITY_QUEUE_FROZEN", "modes": list(MODES), "seeds": list(SEEDS), "runs": 9, "epochs": 50, "batch_size": 4, "img_size": 640, "lr": 1e-4, "checkpoint_selection": "highest development-validation project-local AP50", "final_metric": "one standardized COCO evaluation of each retained checkpoint", "guard_used": False, "tuning": False}, indent=2) + "\n", encoding="utf-8")

    for mode in MODES:
        for seed in SEEDS:
            run_id = f"{mode}_seed{seed}"
            run_dir = OUT / "training" / run_id
            status_path = run_dir / "run_status.json"
            result_path = OUT / "raw" / f"{run_id}.json"
            if args.resume and status_path.is_file():
                status = json.loads(status_path.read_text(encoding="utf-8"))
                if status.get("state") == "COMPLETE" and result_path.is_file():
                    print(f"skip complete run: {run_id}")
                    continue
            run([sys.executable, "rarepdet/tools/train_v76_single_modality.py", "--input-mode", mode, "--seed", str(seed), "--data", args.data, "--train-split", str(TRAIN_SPLIT), "--val-split", str(VAL_SPLIT), "--epochs", "50", "--batch-size", "4", "--img-size", "640", "--lr", "1e-4", "--num-workers", "0", "--device", args.device, "--out", str(run_dir)])
            run([sys.executable, "rarepdet/tools/eval_v76_single_modality.py", "--input-mode", mode, "--seed", str(seed), "--data", args.data, "--split-file", str(VAL_SPLIT), "--weights", str(run_dir / "weights" / "best.pt"), "--out-json", str(result_path), "--img-size", "640", "--batch-size", "4", "--num-workers", "0", "--device", args.device])
    run([sys.executable, "rarepdet/tools/build_v76_single_modality_summary.py"])


if __name__ == "__main__":
    main()
