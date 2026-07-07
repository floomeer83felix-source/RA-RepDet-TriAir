#!/usr/bin/env python
"""Execute the authorized V40 compute-minimized four-run matrix.

The script runs only the four command templates locked by the
compute-minimized amendment, then writes lightweight evidence files. It does
not run robustness, profiling, bootstrap, qualitative, manuscript, DroneVehicle,
or finish-task workflows.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
from datetime import datetime


AMEND_REL = Path("reproducibility/v40_experiment_contract_v1/amendments/compute_minimized_v1")
AMEND_JSON = AMEND_REL / "contract" / "v40_compute_minimized_contract_amendment.json"
RUN_MATRIX_CSV = AMEND_REL / "contract" / "v40_compute_minimized_run_matrix.csv"
COMMANDS_CSV = AMEND_REL / "contract" / "v40_compute_minimized_command_templates.csv"
ORIGINAL_ENV_JSON = Path("reproducibility/v40_experiment_contract_v1/contract/v40_environment.json")
TRAIN_MANIFEST = Path("reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt")
VAL_MANIFEST = Path("reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt")
OUTPUT_ROOT = Path("runs/v40_expanded_adjacency_v2_compute_minimized")
STATUS_COMPLETE = "V40_FOUR_RUN_EXECUTION_COMPLETE"
STATUS_INCOMPLETE = "V40_FOUR_RUN_EXECUTION_INCOMPLETE"

EXPECTED_RUN_IDS = [
    "matched_early_seed0",
    "matched_early_seed2",
    "reliability_p015_seed0",
    "reliability_p015_seed2",
]

METRIC_FIELDS = ["precision", "recall", "f1", "ap50", "ap75"]


def project_root_from_script() -> Path:
    return Path(__file__).resolve().parents[5]


ROOT = project_root_from_script()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"NA ({exc})"


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def runtime_environment() -> dict:
    env = {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
    }
    try:
        import numpy
        import timm
        import torch
        import torchvision

        env.update(
            {
                "numpy": numpy.__version__,
                "pytorch": torch.__version__,
                "torchvision": torchvision.__version__,
                "timm": getattr(timm, "__version__", "NA"),
                "torch_cuda": str(torch.version.cuda),
                "cuda_available": str(torch.cuda.is_available()),
                "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NA",
                "cudnn_version": str(torch.backends.cudnn.version()),
            }
        )
    except Exception as exc:
        env["torch_stack_probe_error"] = f"{type(exc).__name__}: {exc}"
    try:
        smi = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        env["nvidia_smi"] = smi
    except Exception as exc:
        env["nvidia_smi"] = f"NA ({exc})"
    return env


def compare_environment(actual: dict, frozen: dict) -> dict:
    keys = ["python", "pytorch", "torchvision", "timm", "torch_cuda", "cuda_available", "gpu", "numpy"]
    comparisons = {}
    for key in keys:
        comparisons[key] = {
            "actual": actual.get(key),
            "frozen": frozen.get(key),
            "match": str(actual.get(key)) == str(frozen.get(key)),
        }
    if "nvidia_smi" in actual and "nvidia_smi" in frozen:
        comparisons["nvidia_smi"] = {
            "actual": actual.get("nvidia_smi"),
            "frozen": frozen.get("nvidia_smi"),
            "match": str(actual.get("nvidia_smi")) == str(frozen.get("nvidia_smi")),
        }
    ok = all(item["match"] for item in comparisons.values())
    return {"status": "PASS" if ok else "BLOCKED", "comparisons": comparisons}


def validate_scope(amendment: dict, run_matrix: list[dict], commands: dict[str, dict]) -> list[str]:
    blockers = []
    run_ids = [row["run_id"] for row in run_matrix]
    if amendment.get("status") != "V40_COMPUTE_MINIMIZED_CONTRACT_READY":
        blockers.append(f"Amendment status is {amendment.get('status')}")
    if run_ids != EXPECTED_RUN_IDS:
        blockers.append(f"Run IDs differ from authorized list: {run_ids}")
    if sorted(commands) != sorted(EXPECTED_RUN_IDS):
        blockers.append(f"Command template run IDs differ from authorized list: {sorted(commands)}")
    for row in run_matrix:
        if row["run_id"].startswith("reliability_p000") or row["run_id"].startswith("reliability_p020"):
            blockers.append(f"Forbidden run ID in matrix: {row['run_id']}")
        if row["model_type"] == "reliability" and row["modality_dropout"] != "0.15":
            blockers.append(f"Forbidden reliability dropout for {row['run_id']}: {row['modality_dropout']}")
        if row["model_type"] == "early" and row["modality_dropout"] != "0.00":
            blockers.append(f"Unexpected early dropout for {row['run_id']}: {row['modality_dropout']}")
    command_blob = "\n".join(
        item["train_command_template"] + "\n" + item["standardized_evaluator_command_template"]
        for item in commands.values()
    )
    forbidden_tokens = ["reliability_p000", "reliability_p020", "eval_missing_modality", "profile_", "DroneVehicle", "finish_task.ps1"]
    for token in forbidden_tokens:
        if token in command_blob:
            blockers.append(f"Forbidden token in command templates: {token}")
    return blockers


def run_command(command: str, stdout_path: Path, stderr_path: Path) -> dict:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    started = now()
    start_seconds = time.time()
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        out.write("$ " + command + "\n\n")
        out.flush()
        proc = subprocess.Popen(command, cwd=ROOT, shell=True, stdout=out, stderr=err)
        code = proc.wait()
        elapsed = time.time() - start_seconds
        out.write(f"\nreturncode: {code}\nruntime_seconds: {elapsed:.3f}\n")
    return {
        "command": command,
        "returncode": code,
        "started_at": started,
        "ended_at": now(),
        "runtime_seconds": elapsed,
        "stdout": rel(stdout_path),
        "stderr": rel(stderr_path),
    }


def parse_eval_csv(path: Path) -> dict:
    rows = read_csv(path)
    if len(rows) != 1:
        raise RuntimeError(f"Expected one evaluator row in {path}, found {len(rows)}")
    row = rows[0]
    for key in ["precision", "recall", "f1", "ap50", "ap75", "mean_confidence", "fps", "runtime_seconds"]:
        if key in row:
            row[key] = float(row[key])
    for key in ["images", "gt_boxes", "predictions", "detections_per_img"]:
        if key in row:
            row[key] = int(float(row[key]))
    return row


def log_contains_complete(run_dir: Path) -> tuple[bool, bool]:
    log_path = run_dir / "train_log.txt"
    if not log_path.is_file():
        return False, False
    text = log_path.read_text(encoding="utf-8", errors="replace")
    return "epoch 50/50" in text, "Training complete." in text


def summarize_group(rows: list[dict], model_key: str) -> list[dict]:
    group_rows = [row for row in rows if row["model_group"] == model_key]
    out = []
    for metric in METRIC_FIELDS:
        values = [float(row[metric]) for row in group_rows]
        mean = sum(values) / len(values)
        min_value = min(values)
        max_value = max(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        out.append(
            {
                "model_group": model_key,
                "metric": metric,
                "mean": mean,
                "min": min_value,
                "max": max_value,
                "range": max_value - min_value,
                "std": math.sqrt(variance),
                "seed0": next(row[metric] for row in group_rows if row["seed"] == "0"),
                "seed2": next(row[metric] for row in group_rows if row["seed"] == "2"),
            }
        )
    return out


def write_summary(per_run_rows: list[dict]) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    per_run_fields = [
        "run_id",
        "model_group",
        "model",
        "seed",
        "precision",
        "recall",
        "f1",
        "ap50",
        "ap75",
        "gt_boxes",
        "predictions",
        "checkpoint_sha256",
        "eval_results_txt",
        "eval_results_json",
    ]
    aggregate_rows = summarize_group(per_run_rows, "matched_early") + summarize_group(per_run_rows, "reliability_p015")
    summary_rows = []
    for row in per_run_rows:
        out = {key: row.get(key, "") for key in per_run_fields}
        out["row_type"] = "per_run"
        summary_rows.append(out)
    for row in aggregate_rows:
        summary_rows.append(
            {
                "row_type": "aggregate",
                "run_id": "",
                "model_group": row["model_group"],
                "model": "",
                "seed": "",
                "precision": row["mean"] if row["metric"] == "precision" else "",
                "recall": row["mean"] if row["metric"] == "recall" else "",
                "f1": row["mean"] if row["metric"] == "f1" else "",
                "ap50": row["mean"] if row["metric"] == "ap50" else "",
                "ap75": row["mean"] if row["metric"] == "ap75" else "",
                "gt_boxes": "",
                "predictions": "",
                "checkpoint_sha256": "",
                "eval_results_txt": f"metric={row['metric']}; range={row['range']}; std={row['std']}",
                "eval_results_json": "",
            }
        )
    write_csv(OUTPUT_ROOT / "v40_four_run_summary.csv", summary_rows, ["row_type", *per_run_fields])

    payload = {
        "status": STATUS_COMPLETE,
        "generated_at": now(),
        "git_commit": git_output(["rev-parse", "HEAD"]),
        "interpretation_guardrail": "p=0.15 was pre-specified before V40 results; no V40 dropout selection or sweep was performed.",
        "per_run": per_run_rows,
        "aggregates": aggregate_rows,
    }
    write_json(OUTPUT_ROOT / "v40_four_run_summary.json", payload)
    lines = [
        "# V40 Four-Run Summary",
        "",
        f"- Status: `{STATUS_COMPLETE}`",
        "- Interpretation guardrail: p=0.15 was pre-specified before V40 results; no V40 dropout selection or sweep was performed.",
        "",
        "## Per-Run Metrics",
        "",
        "| Run | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Checkpoint SHA-256 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in per_run_rows:
        lines.append(
            f"| `{row['run_id']}` | {row['precision']:.6f} | {row['recall']:.6f} | {row['f1']:.6f} | "
            f"{row['ap50']:.6f} | {row['ap75']:.6f} | {row['gt_boxes']} | {row['predictions']} | `{row['checkpoint_sha256']}` |"
        )
    lines.extend(["", "## Two-Run Aggregates", "", "| Model group | Metric | Mean | Min | Max | Range | Std |", "| --- | --- | --- | --- | --- | --- | --- |"])
    for row in aggregate_rows:
        lines.append(
            f"| `{row['model_group']}` | `{row['metric']}` | {row['mean']:.6f} | {row['min']:.6f} | "
            f"{row['max']:.6f} | {row['range']:.6f} | {row['std']:.6f} |"
        )
    (OUTPUT_ROOT / "v40_four_run_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def execute() -> int:
    amendment = json.loads((ROOT / AMEND_JSON).read_text(encoding="utf-8"))
    run_matrix = read_csv(ROOT / RUN_MATRIX_CSV)
    commands = {row["run_id"]: row for row in read_csv(ROOT / COMMANDS_CSV)}
    frozen_env = json.loads((ROOT / ORIGINAL_ENV_JSON).read_text(encoding="utf-8"))
    actual_env = runtime_environment()
    env_compare = compare_environment(actual_env, frozen_env)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    write_json(
        OUTPUT_ROOT / "execution_preflight.json",
        {
            "generated_at": now(),
            "git_commit": git_output(["rev-parse", "HEAD"]),
            "git_status_short": git_output(["status", "--short"]),
            "actual_environment": actual_env,
            "frozen_environment": frozen_env,
            "environment_comparison": env_compare,
            "amendment_status": amendment.get("status"),
            "authorized_run_ids": EXPECTED_RUN_IDS,
        },
    )

    blockers = validate_scope(amendment, run_matrix, commands)
    if env_compare["status"] != "PASS":
        blockers.append("Actual launch environment does not match frozen training environment.")
    if sha256_file(ROOT / TRAIN_MANIFEST) != amendment["manifest_hashes"]["train"]:
        blockers.append("Train manifest hash mismatch.")
    if sha256_file(ROOT / VAL_MANIFEST) != amendment["manifest_hashes"]["validation"]:
        blockers.append("Validation manifest hash mismatch.")
    if sha256_file(ROOT / "rarepdet/train_early_fusion.py") != amendment["trainer_hash"]:
        blockers.append("Trainer hash mismatch.")
    if sha256_file(ROOT / "rarepdet/eval_map.py") != amendment["evaluator_hash"]:
        blockers.append("Evaluator hash mismatch.")

    if blockers:
        write_json(
            OUTPUT_ROOT / "V40_FOUR_RUN_EXECUTION_STATUS.json",
            {
                "status": STATUS_INCOMPLETE,
                "generated_at": now(),
                "blockers": blockers,
                "training_started": False,
            },
        )
        return 2

    per_run_rows = []
    for run in run_matrix:
        run_id = run["run_id"]
        run_dir = ROOT / OUTPUT_ROOT / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        env_path = run_dir / "launch_environment.json"
        hashes_path = run_dir / "manifest_and_code_hashes.json"
        config_path = run_dir / "config.json"
        logs_dir = run_dir / "execution_logs"

        preflight = {
            "status": "PASS",
            "run_id": run_id,
            "generated_at": now(),
            "train_manifest_sha256": sha256_file(ROOT / TRAIN_MANIFEST),
            "validation_manifest_sha256": sha256_file(ROOT / VAL_MANIFEST),
            "trainer_sha256": sha256_file(ROOT / "rarepdet/train_early_fusion.py"),
            "evaluator_sha256": sha256_file(ROOT / "rarepdet/eval_map.py"),
            "expected_train_manifest_sha256": amendment["manifest_hashes"]["train"],
            "expected_validation_manifest_sha256": amendment["manifest_hashes"]["validation"],
            "expected_trainer_sha256": amendment["trainer_hash"],
            "expected_evaluator_sha256": amendment["evaluator_hash"],
        }
        write_json(env_path, {"actual_environment": actual_env, "frozen_environment": frozen_env, "comparison": env_compare})
        write_json(hashes_path, preflight)
        write_json(
            config_path,
            {
                "run": run,
                "train_command_template": commands[run_id]["train_command_template"],
                "standardized_evaluator_command_template": commands[run_id]["standardized_evaluator_command_template"],
                "contract_amendment": rel(ROOT / AMEND_JSON),
                "no_v40_dropout_selection": True,
                "p015_pre_specified_before_v40_results": True,
            },
        )

        training_result = run_command(
            commands[run_id]["train_command_template"],
            logs_dir / "training_stdout.log",
            logs_dir / "training_stderr.log",
        )
        epoch_50_seen, training_complete_seen = log_contains_complete(run_dir)
        best_checkpoint = run_dir / "weights" / "best.pt"
        last_checkpoint = run_dir / "weights" / "last.pt"
        checkpoint_ok = best_checkpoint.is_file() and last_checkpoint.is_file()
        training_status = {
            "status": "PASS" if training_result["returncode"] == 0 and epoch_50_seen and training_complete_seen and checkpoint_ok else "FAIL",
            "run_id": run_id,
            "training_result": training_result,
            "epoch_50_seen_in_train_log": epoch_50_seen,
            "training_complete_seen_in_train_log": training_complete_seen,
            "best_checkpoint": rel(best_checkpoint),
            "last_checkpoint": rel(last_checkpoint),
            "best_checkpoint_exists": best_checkpoint.is_file(),
            "last_checkpoint_exists": last_checkpoint.is_file(),
        }
        write_json(run_dir / "training_status.json", training_status)
        if training_status["status"] != "PASS":
            write_json(
                OUTPUT_ROOT / "V40_FOUR_RUN_EXECUTION_STATUS.json",
                {"status": STATUS_INCOMPLETE, "generated_at": now(), "failed_run": run_id, "reason": training_status},
            )
            return 2

        checkpoint_sha = sha256_file(best_checkpoint)
        (run_dir / "checkpoint_sha256.txt").write_text(checkpoint_sha + "\n", encoding="utf-8")

        eval_result = run_command(
            commands[run_id]["standardized_evaluator_command_template"],
            logs_dir / "standardized_eval_stdout.log",
            logs_dir / "standardized_eval_stderr.log",
        )
        eval_dir = run_dir / "standardized_eval"
        eval_txt = eval_dir / "eval_results.txt"
        eval_csv = eval_dir / "eval_results.csv"
        if eval_result["returncode"] != 0 or not eval_txt.is_file() or not eval_csv.is_file():
            write_json(
                OUTPUT_ROOT / "V40_FOUR_RUN_EXECUTION_STATUS.json",
                {"status": STATUS_INCOMPLETE, "generated_at": now(), "failed_run": run_id, "reason": eval_result},
            )
            return 2
        metrics = parse_eval_csv(eval_csv)
        write_json(eval_dir / "eval_results.json", metrics)
        summary = {
            "run_id": run_id,
            "model_group": "matched_early" if run["model_type"] == "early" else "reliability_p015",
            "model": metrics["model"],
            "seed": str(metrics["seed"]),
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "ap50": metrics["ap50"],
            "ap75": metrics["ap75"],
            "gt_boxes": metrics["gt_boxes"],
            "predictions": metrics["predictions"],
            "checkpoint_sha256": checkpoint_sha,
            "standard_evaluator_path": "rarepdet/eval_map.py",
            "standard_evaluator_sha256": amendment["evaluator_hash"],
            "eval_results_txt": rel(eval_txt),
            "eval_results_json": rel(eval_dir / "eval_results.json"),
            "eval_results_csv": rel(eval_csv),
        }
        write_json(run_dir / "metrics_summary.json", summary)
        per_run_rows.append(summary)

    write_summary(per_run_rows)
    write_json(
        OUTPUT_ROOT / "V40_FOUR_RUN_EXECUTION_STATUS.json",
        {
            "status": STATUS_COMPLETE,
            "generated_at": now(),
            "run_ids": EXPECTED_RUN_IDS,
            "training_started": True,
            "standardized_evaluation_completed": True,
            "prohibited_work": {
                "p000_training": False,
                "p020_training": False,
                "robustness": False,
                "profiling": False,
                "bootstrap": False,
                "qualitative": False,
                "manuscript": False,
                "dronevehicle": False,
                "finish_task": False,
            },
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(execute())
