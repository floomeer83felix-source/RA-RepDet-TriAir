#!/usr/bin/env python
"""Run the feasible V46 seed0 causal ablations and dev-val evaluation."""

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v46_coco_ablation"
TRAIN_SCRIPT = PROJECT_ROOT / "rarepdet" / "train_early_fusion.py"
EVAL_SCRIPT = PROJECT_ROOT / "rarepdet" / "tools" / "eval_coco_map.py"
TRAIN_SPLIT = PROJECT_ROOT / "reproducibility" / "v40_expanded_adjacency_component_split_v2" / "manifests" / "v40_expanded_adjacency_component_disjoint_train.txt"
DEVVAL_SPLIT = PROJECT_ROOT / "reproducibility" / "v40_expanded_adjacency_component_split_v2" / "manifests" / "v40_expanded_adjacency_component_disjoint_val.txt"
DATASET_ROOT = r"D:\download\triair"

VARIANTS = [
    {
        "run_id": "ra_no_moddrop_seed0",
        "variant": "ra_no_moddrop",
        "model": "reliability",
        "dropout": 0.00,
    },
    {
        "run_id": "early_moddrop_seed0",
        "variant": "early_moddrop",
        "model": "early",
        "dropout": 0.15,
    },
]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def train_command(spec):
    run_dir = OUTPUT_DIR / "local_training" / spec["run_id"]
    return run_dir, [
        sys.executable,
        str(TRAIN_SCRIPT),
        "--model",
        spec["model"],
        "--data",
        DATASET_ROOT,
        "--train-split",
        str(TRAIN_SPLIT),
        "--val-split",
        str(DEVVAL_SPLIT),
        "--epochs",
        "50",
        "--batch-size",
        "4",
        "--img-size",
        "640",
        "--device",
        "cuda",
        "--lr",
        "1e-4",
        "--num-workers",
        "0",
        "--modality-dropout",
        f"{spec['dropout']:.2f}",
        "--seed",
        "0",
        "--out",
        str(run_dir),
    ]


def eval_command(spec, checkpoint):
    output_path = OUTPUT_DIR / "raw" / "ablation_devval" / f"{spec['run_id']}.json"
    return output_path, [
        sys.executable,
        str(EVAL_SCRIPT),
        "--run-id",
        spec["run_id"],
        "--protocol",
        "ablation_devval",
        "--variant",
        spec["variant"],
        "--model",
        spec["model"],
        "--seed",
        "0",
        "--modality-dropout",
        f"{spec['dropout']:.2f}",
        "--data",
        DATASET_ROOT,
        "--split-file",
        str(DEVVAL_SPLIT),
        "--weights",
        str(checkpoint),
        "--img-size",
        "640",
        "--device",
        "cuda",
        "--batch-size",
        "4",
        "--num-workers",
        "0",
        "--detector-score-thr",
        "0.001",
        "--metric-score-thr",
        "0.50",
        "--nms-thresh",
        "0.6",
        "--detections-per-img",
        "100",
        "--out-json",
        str(output_path),
    ]


def training_complete(run_dir):
    log_path = run_dir / "train_log.txt"
    checkpoint = run_dir / "weights" / "best.pt"
    if not log_path.is_file() or not checkpoint.is_file():
        return False
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    return log_text.rstrip().endswith("Training complete.") and log_text.count(" validation ") == 50


def eval_complete(output_path, checkpoint):
    if not output_path.is_file():
        return False
    try:
        result = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return result.get("checkpoint_sha256") == sha256(checkpoint)


def emit(message, handle):
    print(message, flush=True)
    handle.write(message + "\n")
    handle.flush()


def run_command(command, label, handle):
    command_text = subprocess.list2cmdline(command)
    emit(f"START {label}: {now()}", handle)
    emit(f"COMMAND {command_text}", handle)
    environment = dict(os.environ)
    environment["PYTHONUNBUFFERED"] = "1"
    start = time.time()
    process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )
    for line in process.stdout:
        emit(f"[{label}] {line.rstrip()}", handle)
    return_code = process.wait()
    elapsed = time.time() - start
    emit(f"END {label} return_code={return_code} elapsed_seconds={elapsed:.3f}: {now()}", handle)
    if return_code != 0:
        raise SystemExit(return_code)
    return elapsed, command_text


def write_command_plan():
    lines = [
        "V46 feasible seed0 ablation commands",
        "====================================",
        "Selection rule: best checkpoint by development-validation project-local AP50 inside train_early_fusion.py.",
        "Guard use: none for ablation training, checkpoint selection, or run continuation.",
        "",
    ]
    for spec in VARIANTS:
        run_dir, train = train_command(spec)
        checkpoint = run_dir / "weights" / "best.pt"
        _, evaluate = eval_command(spec, checkpoint)
        lines.extend(
            [
                f"[{spec['run_id']}]",
                f"TRAIN {subprocess.list2cmdline(train)}",
                f"EVAL  {subprocess.list2cmdline(evaluate)}",
                "",
            ]
        )
    lines.extend(
        [
            "[ra_static_equal] SKIPPED: requires a new architecture/model-loading path outside the V46 allowed-file list and changes to protected training-core model plumbing.",
            "[ra_stems_concat_or_project] SKIPPED: requires a new architecture/model-loading path outside the V46 allowed-file list and changes to protected training-core model plumbing.",
        ]
    )
    (OUTPUT_DIR / "ablation_train_commands.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    if not (OUTPUT_DIR / "source_lock_v46.json").is_file():
        raise FileNotFoundError("V46 source lock must exist before training")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_command_plan()
    execution_log_path = OUTPUT_DIR / "ablation_execution.log"
    status_path = OUTPUT_DIR / "ablation_execution_status.json"
    status = {
        "status": "RUNNING",
        "started_at": now(),
        "selection_rule": "best development-validation project-local AP50",
        "guard_used": False,
        "runs": [],
    }
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    with execution_log_path.open("a", encoding="utf-8") as handle:
        emit(f"ablation_runner_start: {status['started_at']}", handle)
        for spec in VARIANTS:
            run_dir, train = train_command(spec)
            checkpoint = run_dir / "weights" / "best.pt"
            record = {
                **spec,
                "run_dir": str(run_dir),
                "train_command": subprocess.list2cmdline(train),
                "train_skipped_as_complete": False,
            }
            if training_complete(run_dir):
                record["train_skipped_as_complete"] = True
                record["train_elapsed_seconds"] = None
                emit(f"SKIP completed training: {spec['run_id']}", handle)
            else:
                elapsed, _ = run_command(train, f"train/{spec['run_id']}", handle)
                record["train_elapsed_seconds"] = elapsed
            if not training_complete(run_dir):
                raise RuntimeError(f"training completion check failed: {spec['run_id']}")
            record["checkpoint"] = str(checkpoint)
            record["checkpoint_sha256"] = sha256(checkpoint)

            output_path, evaluate = eval_command(spec, checkpoint)
            record["eval_command"] = subprocess.list2cmdline(evaluate)
            record["eval_skipped_as_complete"] = False
            if eval_complete(output_path, checkpoint):
                record["eval_skipped_as_complete"] = True
                record["eval_elapsed_seconds"] = None
                emit(f"SKIP completed evaluation: {spec['run_id']}", handle)
            else:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                elapsed, _ = run_command(evaluate, f"eval/{spec['run_id']}", handle)
                record["eval_elapsed_seconds"] = elapsed
            if not eval_complete(output_path, checkpoint):
                raise RuntimeError(f"evaluation completion check failed: {spec['run_id']}")
            record["eval_result"] = str(output_path)
            record["completed_at"] = now()
            status["runs"].append(record)
            status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

        status["status"] = "SEED0_FEASIBLE_ABLATIONS_COMPLETE"
        status["completed_at"] = now()
        status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        emit(f"ablation_runner_end: {status['completed_at']}", handle)


if __name__ == "__main__":
    main()
