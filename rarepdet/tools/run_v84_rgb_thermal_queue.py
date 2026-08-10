#!/usr/bin/env python
"""Run the frozen three-seed V84 RGB+thermal training and evaluation queue."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/v84_jei_critical_closure/rgb_thermal_baseline"
TRAIN = ROOT / "rarepdet/tools/train_v84_rgb_thermal.py"
EVAL = ROOT / "rarepdet/tools/eval_v84_rgb_thermal.py"
TRAIN_SPLIT = ROOT / "reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt"
VAL_SPLIT = ROOT / "reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(subprocess.list2cmdline(command) + "\n")
        handle.flush()
        process = subprocess.Popen(command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, text=True)
        if process.wait() != 0:
            raise RuntimeError(f"command failed; see {log_path}")


def summarize() -> None:
    rows = []
    for seed in (0, 1, 2):
        result = json.loads((OUT / "raw" / f"rgbt_seed{seed}.json").read_text(encoding="utf-8"))
        rows.append({key: result[key] for key in ("run_id", "seed", "checkpoint_epoch", "checkpoint_sha256", "split_sha256", "ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")})
    with (OUT / "per_run.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metrics = ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")
    summary = {metric: {"mean": statistics.mean(float(row[metric]) for row in rows), "sample_std": statistics.stdev(float(row[metric]) for row in rows)} for metric in metrics}
    payload = {"status": "V84_RGB_THERMAL_3_SEED_COMPLETE", "protocol": {"epochs": 50, "batch_size": 4, "img_size": 640, "optimizer": "AdamW", "lr": 1e-4, "checkpoint_selection": "highest development-validation project-local AP50", "standardized_coco_evaluation": "once per retained checkpoint", "train_split_sha256": sha256(TRAIN_SPLIT), "devval_split_sha256": sha256(VAL_SPLIT), "guard_used": False}, "per_run": rows, "summary": summary}
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# V84 RGB+Thermal Baseline", "", "Status: `V84_RGB_THERMAL_3_SEED_COMPLETE`", "", "| Metric | Mean +/- sample SD |", "| --- | ---: |"]
    lines.extend(f"| {metric} | {value['mean']:.4f} +/- {value['sample_std']:.4f} |" for metric, value in summary.items())
    lines.extend(["", "No locked holdout access occurred."])
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    preflight = json.loads((ROOT / "runs/v84_jei_critical_closure/preflight/checkpoint_inventory.json").read_text(encoding="utf-8"))
    splits = json.loads((ROOT / "runs/v84_jei_critical_closure/preflight/split_identity.json").read_text(encoding="utf-8"))
    if preflight["status"] != "PASS" or splits["status"] != "PASS":
        raise RuntimeError("V84 preflight must pass before P1")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "protocol.json").write_text(json.dumps({"status": "FROZEN", "input_mode": "rgbt", "seeds": [0, 1, 2], "epochs": 50, "batch_size": 4, "img_size": 640, "optimizer": "AdamW", "lr": 1e-4, "weight_decay": 1e-4, "checkpoint_selection": "highest development-validation project-local AP50", "guard_used": False}, indent=2) + "\n", encoding="utf-8")
    queue_log = OUT / "queue.log"
    for seed in (0, 1, 2):
        run_dir = OUT / "training" / f"rgbt_seed{seed}"
        result = OUT / "raw" / f"rgbt_seed{seed}.json"
        status_path = run_dir / "run_status.json"
        if args.resume and status_path.is_file() and result.is_file() and json.loads(status_path.read_text(encoding="utf-8")).get("state") == "COMPLETE":
            continue
        run([sys.executable, str(TRAIN), "--seed", str(seed), "--data", args.data, "--train-split", str(TRAIN_SPLIT), "--val-split", str(VAL_SPLIT), "--device", args.device, "--out", str(run_dir)], queue_log)
        run([sys.executable, str(EVAL), "--seed", str(seed), "--data", args.data, "--split-file", str(VAL_SPLIT), "--weights", str(run_dir / "weights/best.pt"), "--out-json", str(result), "--device", args.device], queue_log)
    summarize()


if __name__ == "__main__":
    main()
