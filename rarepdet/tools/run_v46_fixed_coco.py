#!/usr/bin/env python
"""Run the twelve source-locked V46 fixed-checkpoint COCO evaluations."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v46_coco_ablation"
EVALUATOR = PROJECT_ROOT / "rarepdet" / "tools" / "eval_coco_map.py"
DATASET_ROOT = r"D:\download\triair"

RUNS = [
    ("matched_early_seed0", "matched_early", "early", 0, 0.00, "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt"),
    ("matched_early_seed1", "matched_early", "early", 1, 0.00, "runs/v41_q1_upgrade/seed1/matched_early_seed1/weights/best.pt"),
    ("matched_early_seed2", "matched_early", "early", 2, 0.00, "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed2/weights/best.pt"),
    ("reliability_p015_seed0", "ra_full_p015", "reliability", 0, 0.15, "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt"),
    ("reliability_p015_seed1", "ra_full_p015", "reliability", 1, 0.15, "runs/v41_q1_upgrade/seed1/reliability_p015_seed1/weights/best.pt"),
    ("reliability_p015_seed2", "ra_full_p015", "reliability", 2, 0.15, "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed2/weights/best.pt"),
]

PROTOCOLS = [
    (
        "devval",
        "reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt",
    ),
    ("guard", "runs/component_disjoint_v40/guard.txt"),
]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def result_is_current(output_path, checkpoint_path, split_path):
    if not output_path.is_file():
        return False
    try:
        result = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        result.get("checkpoint_sha256") == sha256(checkpoint_path)
        and result.get("split_sha256") == sha256(split_path)
        and result.get("coco_backend") == "pycocotools.cocoeval.COCOeval"
    )


def command_for(protocol, split_path, run):
    run_id, variant, model, seed, dropout, checkpoint_text = run
    output_path = OUTPUT_DIR / "raw" / "coco" / protocol / f"{run_id}.json"
    return output_path, [
        sys.executable,
        str(EVALUATOR),
        "--run-id",
        run_id,
        "--protocol",
        protocol,
        "--variant",
        variant,
        "--model",
        model,
        "--seed",
        str(seed),
        "--modality-dropout",
        f"{dropout:.2f}",
        "--data",
        DATASET_ROOT,
        "--split-file",
        str(split_path),
        "--weights",
        str(PROJECT_ROOT / checkpoint_text),
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


def emit(message, log_handle):
    print(message, flush=True)
    log_handle.write(message + "\n")
    log_handle.flush()


def main():
    source_lock = OUTPUT_DIR / "source_lock_v46.json"
    if not source_lock.is_file():
        raise FileNotFoundError("V46 source lock must exist before evaluation")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    commands_path = OUTPUT_DIR / "coco_eval_commands.txt"
    execution_log_path = OUTPUT_DIR / "coco_eval_execution.log"
    command_lines = []

    with execution_log_path.open("a", encoding="utf-8") as execution_log:
        emit(f"runner_start: {datetime.now().astimezone().isoformat(timespec='seconds')}", execution_log)
        for protocol, split_text in PROTOCOLS:
            split_path = PROJECT_ROOT / split_text
            for run in RUNS:
                output_path, command = command_for(protocol, split_path, run)
                checkpoint_path = PROJECT_ROOT / run[5]
                command_text = subprocess.list2cmdline(command)
                command_lines.append(command_text)
                if result_is_current(output_path, checkpoint_path, split_path):
                    emit(f"SKIP current result: {protocol}/{run[0]}", execution_log)
                    continue

                output_path.parent.mkdir(parents=True, exist_ok=True)
                emit(f"START {protocol}/{run[0]}: {datetime.now().astimezone().isoformat(timespec='seconds')}", execution_log)
                emit(f"COMMAND {command_text}", execution_log)
                process = subprocess.Popen(
                    command,
                    cwd=PROJECT_ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                for line in process.stdout:
                    emit(f"[{protocol}/{run[0]}] {line.rstrip()}", execution_log)
                return_code = process.wait()
                emit(f"END {protocol}/{run[0]} return_code={return_code}: {datetime.now().astimezone().isoformat(timespec='seconds')}", execution_log)
                if return_code != 0:
                    raise SystemExit(return_code)

        emit(f"runner_end: {datetime.now().astimezone().isoformat(timespec='seconds')}", execution_log)

    commands_path.write_text("\n".join(command_lines) + "\n", encoding="utf-8")
    print(f"saved: {commands_path}")
    print(f"saved: {execution_log_path}")


if __name__ == "__main__":
    main()
