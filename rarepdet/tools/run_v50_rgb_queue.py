#!/usr/bin/env python
"""Run the three V50 RGB seeds sequentially, evaluate, and finalize."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import traceback


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = PROJECT_ROOT / "runs/v50_visdrone_seen"
STATUS_PATH = OUTPUT / "rgb_run_status.json"
SEEDS = (0, 1, 2)


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


def initial_status():
    return {
        "state": "RUNNING",
        "started_at": now(),
        "updated_at": now(),
        "protocol": {
            "epochs": 50,
            "img_size": 640,
            "batch_size": 4,
            "learning_rate": 0.0001,
            "checkpoint_selection": "highest devval canonical COCO AP50; first exact tie wins",
            "test_access": "after all three checkpoints are frozen",
        },
        "zero_shot_state": "COMPLETE",
        "runs": [
            {"seed": seed, "state": "PENDING", "checkpoint_sha256": None} for seed in SEEDS
        ],
        "test_accessed": False,
    }


def load_status():
    return json.loads(STATUS_PATH.read_text(encoding="utf-8")) if STATUS_PATH.is_file() else initial_status()


def update(status, **values):
    status.update(values)
    status["updated_at"] = now()
    atomic_json(STATUS_PATH, status)


def command_for_training(seed):
    return [
        sys.executable,
        str(PROJECT_ROOT / "rarepdet/train_visdrone_rgb.py"),
        "--data",
        r"D:\datasets\visdrone_seen",
        "--train-manifest",
        str(OUTPUT / "manifests/train.txt"),
        "--train-annotations",
        str(OUTPUT / "converted_annotations/train.json"),
        "--val-manifest",
        str(OUTPUT / "manifests/devval.txt"),
        "--val-annotations",
        str(OUTPUT / "converted_annotations/devval.json"),
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
        "--seed",
        str(seed),
        "--detector-score-thr",
        "0.001",
        "--nms-thresh",
        "0.6",
        "--detections-per-img",
        "100",
        "--out",
        str(OUTPUT / f"rgb_training/seed{seed}"),
    ]


def command_for_eval(seed, protocol):
    return [
        sys.executable,
        str(PROJECT_ROOT / "rarepdet/tools/eval_v50_visdrone_seen.py"),
        "--run-id",
        f"rgb_seed{seed}",
        "--protocol",
        protocol,
        "--variant",
        "rgb_baseline",
        "--model",
        "rgb",
        "--seed",
        str(seed),
        "--data",
        r"D:\datasets\visdrone_seen",
        "--manifest",
        str(OUTPUT / f"manifests/{protocol}.txt"),
        "--annotations",
        str(OUTPUT / f"converted_annotations/{protocol}.json"),
        "--weights",
        str(OUTPUT / f"rgb_training/seed{seed}/weights/best.pt"),
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
        "--nms-thresh",
        "0.6",
        "--detections-per-img",
        "100",
        "--out-json",
        str(OUTPUT / f"raw/rgb/{protocol}/rgb_seed{seed}.json"),
    ]


def run(command, handle):
    rendered = subprocess.list2cmdline([str(item) for item in command])
    handle.write(f"COMMAND {now()} {rendered}\n")
    handle.flush()
    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        stdout=handle,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if process.returncode != 0:
        raise RuntimeError(f"command failed ({process.returncode}): {rendered}")


def write_commands():
    lines = []
    for seed in SEEDS:
        lines.append("TRAIN " + subprocess.list2cmdline(command_for_training(seed)))
    lines.append("# Test commands execute only after all three best checkpoints are frozen.")
    for protocol in ("devval", "test"):
        for seed in SEEDS:
            lines.append(protocol.upper() + " " + subprocess.list2cmdline(command_for_eval(seed, protocol)))
    (OUTPUT / "rgb_train_commands.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def complete_training(seed):
    directory = OUTPUT / f"rgb_training/seed{seed}"
    log = directory / "train_log.txt"
    best = directory / "weights/best.pt"
    return best.is_file() and log.is_file() and "Training complete." in log.read_text(
        encoding="utf-8", errors="replace"
    )


def main():
    if not (OUTPUT / "source_lock_v50.json").is_file():
        raise FileNotFoundError("V50 source lock is required before training")
    if len(list((OUTPUT / "raw/zero_shot/test").glob("*.json"))) != 6:
        raise RuntimeError("six frozen-checkpoint test records are required before the RGB queue")
    write_commands()
    status = load_status()
    if status.get("state") == "COMPLETE":
        return
    if status.get("state") == "BLOCKED_TEST_ACCESS_ORDER_VIOLATION" or status.get(
        "protocol_violation_preserved"
    ):
        raise RuntimeError(
            "V50 is blocked by a test-access-order violation; this frozen task has "
            "no continuation override"
        )
    update(status, state="RUNNING")
    log_path = OUTPUT / "rgb_queue.log"
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            for seed in SEEDS:
                record = status["runs"][seed]
                if not complete_training(seed):
                    record["state"] = "TRAINING"
                    record["started_at"] = now()
                    update(status)
                    run(command_for_training(seed), handle)
                best = OUTPUT / f"rgb_training/seed{seed}/weights/best.pt"
                record["state"] = "CHECKPOINT_FROZEN"
                record["completed_at"] = now()
                record["checkpoint_sha256"] = sha256(best)
                update(status)

            update(status, state="CHECKPOINTS_FROZEN")
            for seed in SEEDS:
                path = OUTPUT / f"raw/rgb/devval/rgb_seed{seed}.json"
                if not path.is_file():
                    run(command_for_eval(seed, "devval"), handle)
            update(status, state="DEVVAL_COMPLETE")

            # This is the first allowed RGB-baseline test access point.
            update(status, state="TEST_RUNNING", test_accessed=True, test_accessed_at=now())
            for seed in SEEDS:
                path = OUTPUT / f"raw/rgb/test/rgb_seed{seed}.json"
                if not path.is_file():
                    run(command_for_eval(seed, "test"), handle)
            for record in status["runs"]:
                record["state"] = "COMPLETE"
            update(status, state="RESULTS_COMPLETE")

            run(
                [sys.executable, str(PROJECT_ROOT / "rarepdet/tools/build_v50_reports.py")],
                handle,
            )
            run(
                [sys.executable, str(PROJECT_ROOT / "rarepdet/tools/scan_v50_claims.py")],
                handle,
            )
            update(status, state="COMPLETE", completed_at=now())
            handle.write(f"QUEUE COMPLETE {now()}\n")
            handle.flush()
        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "rarepdet/tools/finalize_v50_task.py")],
            cwd=PROJECT_ROOT,
            check=True,
        )
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
