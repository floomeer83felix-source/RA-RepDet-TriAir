#!/usr/bin/env python
"""Run one source-locked V48 training/evaluation job on development-validation only."""

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v48_complete_ablation"
TRAIN_SCRIPT = PROJECT_ROOT / "rarepdet" / "train_early_fusion.py"
EVAL_SCRIPT = PROJECT_ROOT / "rarepdet" / "tools" / "eval_coco_map.py"
TRAIN_SPLIT = PROJECT_ROOT / "reproducibility" / "v40_expanded_adjacency_component_split_v2" / "manifests" / "v40_expanded_adjacency_component_disjoint_train.txt"
DEVVAL_SPLIT = PROJECT_ROOT / "reproducibility" / "v40_expanded_adjacency_component_split_v2" / "manifests" / "v40_expanded_adjacency_component_disjoint_val.txt"
DATASET_ROOT = r"D:\download\triair"
SPECS = {
    "ra_no_moddrop_seed1": ("ra_no_moddrop", "reliability", 0.00, 1),
    "ra_no_moddrop_seed2": ("ra_no_moddrop", "reliability", 0.00, 2),
    "early_moddrop_seed1": ("early_moddrop", "early", 0.15, 1),
    "early_moddrop_seed2": ("early_moddrop", "early", 0.15, 2),
    "ra_static_equal_seed0": ("ra_static_equal", "ra_static_equal", 0.00, 0),
    "ra_static_equal_seed1": ("ra_static_equal", "ra_static_equal", 0.00, 1),
    "ra_static_equal_seed2": ("ra_static_equal", "ra_static_equal", 0.00, 2),
    "ra_stems_project_seed0": ("ra_stems_project", "ra_stems_project", 0.00, 0),
    "ra_stems_project_seed1": ("ra_stems_project", "ra_stems_project", 0.00, 1),
    "ra_stems_project_seed2": ("ra_stems_project", "ra_stems_project", 0.00, 2),
}


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def command_text(command):
    return subprocess.list2cmdline([str(item) for item in command])


def train_command(run_id, variant, model, dropout, seed):
    run_dir = OUTPUT_DIR / "training" / run_id
    return run_dir, [
        sys.executable, str(TRAIN_SCRIPT), "--model", model, "--data", DATASET_ROOT,
        "--train-split", str(TRAIN_SPLIT), "--val-split", str(DEVVAL_SPLIT),
        "--epochs", "50", "--batch-size", "4", "--img-size", "640", "--device", "cuda",
        "--lr", "1e-4", "--num-workers", "0", "--modality-dropout", f"{dropout:.2f}",
        "--seed", str(seed), "--out", str(run_dir),
    ]


def eval_command(run_id, variant, model, dropout, seed, checkpoint):
    result = OUTPUT_DIR / "raw" / "devval" / f"{run_id}.json"
    return result, [
        sys.executable, str(EVAL_SCRIPT), "--run-id", run_id, "--protocol", "ablation_devval",
        "--variant", variant, "--model", model, "--seed", str(seed), "--modality-dropout", f"{dropout:.2f}",
        "--data", DATASET_ROOT, "--split-file", str(DEVVAL_SPLIT), "--weights", str(checkpoint),
        "--img-size", "640", "--device", "cuda", "--batch-size", "4", "--num-workers", "0",
        "--detector-score-thr", "0.001", "--metric-score-thr", "0.50", "--nms-thresh", "0.6",
        "--detections-per-img", "100", "--out-json", str(result),
    ]


def invoke(command, label, log_path):
    environment = dict(os.environ)
    environment["PYTHONUNBUFFERED"] = "1"
    start = time.time()
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"START {label} {now()}\nCOMMAND {command_text(command)}\n")
        handle.flush()
        process = subprocess.Popen(command, cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", env=environment)
        for line in process.stdout:
            print(f"[{label}] {line.rstrip()}", flush=True)
            handle.write(line)
        return_code = process.wait()
        elapsed = time.time() - start
        handle.write(f"END {label} return_code={return_code} elapsed_seconds={elapsed:.3f} {now()}\n")
    if return_code != 0:
        raise RuntimeError(f"{label} failed with return code {return_code}")
    return elapsed


def verify_source_lock():
    lock_path = OUTPUT_DIR / "source_lock_v48.json"
    if not lock_path.is_file():
        raise FileNotFoundError("V48 source lock must be created before training")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    for path_text, expected in lock["code_sha256"].items():
        observed = sha256(PROJECT_ROOT / path_text)
        if observed != expected:
            raise RuntimeError(f"source lock changed after training authorization: {path_text}")
    if "forbidden" not in lock["guard_policy"].lower():
        raise RuntimeError("source lock does not contain the locked-holdout prohibition")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, choices=sorted(SPECS))
    args = parser.parse_args()
    verify_source_lock()
    variant, model, dropout, seed = SPECS[args.run_id]
    run_dir, train = train_command(args.run_id, variant, model, dropout, seed)
    checkpoint = run_dir / "weights" / "best.pt"
    result_path, evaluate = eval_command(args.run_id, variant, model, dropout, seed, checkpoint)
    run_dir.mkdir(parents=True, exist_ok=True)
    status_path = run_dir / "run_status.json"
    log_path = run_dir / "runner_stdout_stderr.log"
    status = {
        "run_id": args.run_id, "variant": variant, "model": model, "modality_dropout": dropout, "seed": seed,
        "state": "RUNNING", "started_at": now(), "guard_used": False,
        "checkpoint_selection_rule": "highest development-validation project-local AP50",
        "train_command": command_text(train), "eval_command": command_text(evaluate),
    }
    atomic_json(status_path, status)
    (run_dir / "command.txt").write_text(f"TRAIN {status['train_command']}\nEVAL  {status['eval_command']}\n", encoding="utf-8")
    try:
        training_seconds = invoke(train, f"train/{args.run_id}", log_path)
        if not checkpoint.is_file():
            raise RuntimeError(f"best checkpoint is missing: {checkpoint}")
        selected = torch.load(checkpoint, map_location="cpu", weights_only=False)
        evaluation_seconds = invoke(evaluate, f"eval/{args.run_id}", log_path)
        result = json.loads(result_path.read_text(encoding="utf-8"))
        checkpoint_hash = sha256(checkpoint)
        if result.get("checkpoint_sha256") != checkpoint_hash:
            raise RuntimeError("evaluation checkpoint hash does not match selected checkpoint")
        status.update(
            state="COMPLETE", completed_at=now(), training_runtime_seconds=training_seconds,
            evaluation_runtime_seconds=evaluation_seconds, checkpoint=str(checkpoint), checkpoint_sha256=checkpoint_hash,
            selected_epoch=int(selected["epoch"]), selected_metrics=selected.get("metrics", {}),
            devval_result=str(result_path),
        )
    except Exception as exc:
        status.update(state="FAILED", failed_at=now(), error=str(exc))
        atomic_json(status_path, status)
        raise
    atomic_json(status_path, status)
    print(json.dumps({"run_id": args.run_id, "state": status["state"], "selected_epoch": status["selected_epoch"]}, indent=2))


if __name__ == "__main__":
    main()
