#!/usr/bin/env python
"""Run the source-locked V51 Route-B GPU queue after explicit authorization."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import traceback


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = PROJECT_ROOT / "runs/v51_visdrone_recovery"
STATUS_PATH = OUTPUT / "cv_run_status.json"
SEEDS = (0, 1, 2)
FOLDS = (0, 1, 2)


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


def load_status():
    return json.loads(STATUS_PATH.read_text(encoding="utf-8"))


def update(status, **values):
    status.update(values)
    status["updated_at"] = now()
    atomic_json(STATUS_PATH, status)


def verify_source_lock():
    lock = json.loads((OUTPUT / "source_lock_v51.json").read_text(encoding="utf-8"))
    failures = []
    for relative, expected in lock["frozen_hashes"].items():
        path = Path(relative)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        actual = sha256(path) if path.is_file() else None
        if actual != expected:
            failures.append({"path": relative, "expected": expected, "actual": actual})
    if failures:
        raise RuntimeError(f"V51 source-lock verification failed: {failures}")
    return lock


def training_command(fold, seed):
    return [
        sys.executable,
        str(PROJECT_ROOT / "rarepdet/train_visdrone_rgb.py"),
        "--data", r"D:\datasets\visdrone_seen",
        "--train-manifest", str(OUTPUT / f"folds/fold_{fold}_train.txt"),
        "--train-annotations", str(OUTPUT / f"converted_annotations/fold_{fold}_train.json"),
        "--val-manifest", str(OUTPUT / f"folds/fold_{fold}_val.txt"),
        "--val-annotations", str(OUTPUT / f"converted_annotations/fold_{fold}_val.json"),
        "--epochs", "50", "--batch-size", "4", "--img-size", "640",
        "--device", "cuda", "--lr", "1e-4", "--num-workers", "0",
        "--seed", str(seed), "--detector-score-thr", "0.001",
        "--nms-thresh", "0.6", "--detections-per-img", "100",
        "--out", str(OUTPUT / f"cv_training/fold{fold}/seed{seed}"),
    ]


def evaluation_command(fold, seed, variant, model, weights, output):
    return [
        sys.executable,
        str(PROJECT_ROOT / "rarepdet/tools/eval_v51_visdrone_recovery.py"),
        "--run-id", output.stem,
        "--fold", str(fold),
        "--variant", variant,
        "--model", model,
        "--seed", str(seed),
        "--data", r"D:\datasets\visdrone_seen",
        "--manifest", str(OUTPUT / f"folds/fold_{fold}_val.txt"),
        "--annotations", str(OUTPUT / f"converted_annotations/fold_{fold}_val.json"),
        "--weights", str(weights),
        "--img-size", "640", "--device", "cuda", "--batch-size", "4",
        "--num-workers", "0", "--detector-score-thr", "0.001",
        "--nms-thresh", "0.6", "--detections-per-img", "100",
        "--out-json", str(output),
    ]


def run(command, handle):
    rendered = subprocess.list2cmdline([str(item) for item in command])
    handle.write(f"COMMAND {now()} {rendered}\n")
    handle.flush()
    process = subprocess.run(
        command, cwd=PROJECT_ROOT, stdout=handle, stderr=subprocess.STDOUT, text=True
    )
    if process.returncode:
        raise RuntimeError(f"command failed ({process.returncode}): {rendered}")


def training_complete(fold, seed):
    directory = OUTPUT / f"cv_training/fold{fold}/seed{seed}"
    log = directory / "train_log.txt"
    return (
        (directory / "weights/best.pt").is_file()
        and log.is_file()
        and "Training complete." in log.read_text(encoding="utf-8", errors="replace")
    )


def append_evaluation_log(result_path):
    result = json.loads(result_path.read_text(encoding="utf-8"))
    event = {
        "at": now(),
        "run_id": result["run_id"],
        "fold": result["fold"],
        "variant": result["variant"],
        "manifest_sha256": result["manifest_sha256"],
        "annotations_sha256": result["annotations_sha256"],
        "checkpoint_sha256": result["checkpoint_sha256"],
        "result_sha256": sha256(result_path),
    }
    with (OUTPUT / "fold_evaluation_log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-gpu-authorized", action="store_true")
    args = parser.parse_args()
    if not args.confirm_gpu_authorized:
        raise SystemExit("GPU queue is locked; explicit --confirm-gpu-authorized is required")
    lock = verify_source_lock()
    status = load_status()
    update(status, state="RUNNING", gpu_authorized_at=now())
    log_path = OUTPUT / "cv_queue.log"
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            for fold in FOLDS:
                for seed in SEEDS:
                    record = next(
                        item for item in status["runs"]
                        if int(item["fold"]) == fold and int(item["seed"]) == seed
                    )
                    if not training_complete(fold, seed):
                        record.update(state="TRAINING", started_at=now())
                        update(status)
                        run(training_command(fold, seed), handle)
                    best = OUTPUT / f"cv_training/fold{fold}/seed{seed}/weights/best.pt"
                    record.update(
                        state="CHECKPOINT_FROZEN",
                        completed_at=now(),
                        checkpoint_sha256=sha256(best),
                    )
                    update(status)
                    result = OUTPUT / f"raw/rgb/fold{fold}/rgb_fold{fold}_seed{seed}.json"
                    if not result.is_file():
                        run(evaluation_command(fold, seed, "rgb_baseline", "rgb", best, result), handle)
                        append_evaluation_log(result)

            update(status, state="RGB_CV_COMPLETE_ZERO_SHOT_RUNNING")
            for fold in FOLDS:
                for seed in SEEDS:
                    for variant, model, key in (
                        ("matched_early", "early", f"matched_early_seed{seed}"),
                        ("ra_full_p015", "reliability", f"reliability_p015_seed{seed}"),
                    ):
                        checkpoint = PROJECT_ROOT / lock["frozen_triair_checkpoints"][key]["path"]
                        result = OUTPUT / f"raw/zero_shot/fold{fold}/{variant}_seed{seed}.json"
                        if not result.is_file():
                            run(evaluation_command(fold, seed, variant, model, checkpoint, result), handle)
                            append_evaluation_log(result)
            run([sys.executable, str(PROJECT_ROOT / "rarepdet/tools/build_v51_cv_reports.py")], handle)
            for record in status["runs"]:
                record["state"] = "COMPLETE"
            update(status, state="COMPLETE", completed_at=now())
            handle.write(f"QUEUE COMPLETE {now()}\n")
    except Exception as exc:
        update(
            status,
            state="FAILED",
            error=repr(exc),
            traceback=traceback.format_exc().splitlines()[-50:],
        )
        raise


if __name__ == "__main__":
    main()
