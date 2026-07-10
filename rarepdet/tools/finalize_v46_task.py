#!/usr/bin/env python
"""Wait for V46 seed0 runs, finalize evidence, and invoke finish_task."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v46_coco_ablation"
STATUS_PATH = OUTPUT_DIR / "ablation_execution_status.json"
FINALIZER_LOG = OUTPUT_DIR / "finalizer.log"

USER_UNTRACKED_TOOL_FILES = [
    PROJECT_ROOT / "rarepdet" / "tools" / "eval_dronevehicle_modality_specific.py",
    PROJECT_ROOT / "rarepdet" / "tools" / "prepare_dronevehicle_modality_specific_eval.py",
]

ALLOWED_STATUS_PATHS = {
    "docs/EXPERIMENT_STATUS.md",
    "docs/TASK_BLOCKER.md",
    "rarepdet/coco_metrics.py",
    "rarepdet/tools/build_v46_ablation_summary.py",
    "rarepdet/tools/build_v46_coco_summary.py",
    "rarepdet/tools/create_v46_source_lock.py",
    "rarepdet/tools/eval_coco_map.py",
    "rarepdet/tools/finalize_v46_task.py",
    "rarepdet/tools/generate_handoff.py",
    "rarepdet/tools/run_v46_ablation_seed0.py",
    "rarepdet/tools/run_v46_fixed_coco.py",
    "rarepdet/tools/run_v46_preflight.py",
    "rarepdet/tools/scan_v46_claims.py",
    "rarepdet/tools/smoke_test_coco_metrics.py",
    "rarepdet/tools/update_project_status.py",
    "rarepdet/tools/v46_handoff.py",
    "rarepdet/tools/write_v46_blocker.py",
    "runs/handoff_latest.json",
    "runs/handoff_latest.md",
}

ALLOWED_STATUS_PREFIXES = (
    "runs/v46_coco_ablation/",
    "runs/v41_q1_upgrade/seed1/",
)


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def emit(message):
    line = f"[{now()}] {message}"
    print(line, flush=True)
    with FINALIZER_LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run(command, label, check=True):
    emit(f"START {label}: {subprocess.list2cmdline([str(item) for item in command])}")
    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    for line in process.stdout.splitlines():
        emit(f"[{label}] {line}")
    emit(f"END {label} return_code={process.returncode}")
    if check and process.returncode != 0:
        raise RuntimeError(f"{label} failed with return code {process.returncode}")
    return process


def process_exists(pid):
    process = subprocess.run(
        ["powershell", "-NoProfile", "-Command", f"if (Get-Process -Id {pid} -ErrorAction SilentlyContinue) {{ exit 0 }} else {{ exit 1 }}"],
        cwd=PROJECT_ROOT,
    )
    return process.returncode == 0


def wait_for_ablation(runner_pid, timeout_hours):
    deadline = time.time() + timeout_hours * 3600.0
    last_reported_epochs = None
    while time.time() < deadline:
        status = {}
        if STATUS_PATH.is_file():
            try:
                status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                status = {}
        if status.get("status") == "SEED0_FEASIBLE_ABLATIONS_COMPLETE":
            emit("ablation runner reported SEED0_FEASIBLE_ABLATIONS_COMPLETE")
            return
        if not process_exists(runner_pid):
            raise RuntimeError(
                f"ablation runner PID {runner_pid} exited before reporting completion; status={status.get('status')}"
            )

        epoch_counts = []
        for run_id in ("ra_no_moddrop_seed0", "early_moddrop_seed0"):
            log_path = OUTPUT_DIR / "local_training" / run_id / "train_log.txt"
            count = 0
            if log_path.is_file():
                count = sum(
                    1
                    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines()
                    if line.startswith("epoch ") and " validation " in line
                )
            epoch_counts.append((run_id, count))
        if epoch_counts != last_reported_epochs:
            emit("training progress: " + ", ".join(f"{run_id}={count}/50" for run_id, count in epoch_counts))
            last_reported_epochs = epoch_counts
        time.sleep(60)
    raise TimeoutError(f"V46 ablation did not complete within {timeout_hours} hours")


def stage_v46_outputs():
    files = []
    for path in OUTPUT_DIR.iterdir():
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".csv", ".txt"}:
            files.append(path)
    raw_dir = OUTPUT_DIR / "raw"
    if raw_dir.is_dir():
        for path in raw_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".csv", ".txt"}:
                files.append(path)
    if not files:
        raise RuntimeError("no V46 outputs found to stage")
    run(["git", "add", "-f", "--", *files], "stage-v46-outputs")


def status_paths():
    process = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        raise RuntimeError(process.stderr.decode("utf-8", errors="replace"))
    entries = process.stdout.decode("utf-8", errors="replace").split("\0")
    paths = []
    for entry in entries:
        if not entry:
            continue
        path = entry[3:].replace("\\", "/")
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return paths


def assert_scoped_worktree():
    known_user_files = {
        path.relative_to(PROJECT_ROOT).as_posix() for path in USER_UNTRACKED_TOOL_FILES
    }
    unexpected = []
    for path in status_paths():
        if path in ALLOWED_STATUS_PATHS or path in known_user_files:
            continue
        if path.startswith(ALLOWED_STATUS_PREFIXES):
            continue
        unexpected.append(path)
    if unexpected:
        raise RuntimeError(
            "unexpected worktree changes appeared during V46; refusing broad finish_task staging: "
            + ", ".join(sorted(unexpected))
        )
    emit("worktree scope gate passed")


def is_untracked(path):
    if not path.exists():
        return False
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path.relative_to(PROJECT_ROOT))],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode != 0


def preserve_user_untracked_files():
    preserve_root = Path(tempfile.gettempdir()).resolve() / f"rarepdet_v46_preserve_{os.getpid()}"
    preserve_root.mkdir(parents=True, exist_ok=False)
    moved = []
    for source in USER_UNTRACKED_TOOL_FILES:
        source_resolved = source.resolve()
        if PROJECT_ROOT.resolve() not in source_resolved.parents:
            raise RuntimeError(f"refusing to move path outside project root: {source}")
        if not is_untracked(source):
            continue
        destination = preserve_root / source.name
        if preserve_root not in destination.resolve().parents:
            raise RuntimeError(f"invalid preservation target: {destination}")
        shutil.move(str(source), str(destination))
        moved.append((source, destination))
        emit(f"temporarily preserved untracked user file: {source}")
    return preserve_root, moved


def restore_user_untracked_files(preserve_root, moved):
    for original, saved in moved:
        if original.exists():
            raise RuntimeError(f"cannot restore over existing path: {original}")
        shutil.move(str(saved), str(original))
        emit(f"restored untracked user file: {original}")
    if preserve_root.exists():
        preserve_root.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner-pid", type=int, required=True)
    parser.add_argument("--timeout-hours", type=float, default=24.0)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    emit(f"finalizer start; runner_pid={args.runner_pid}")
    wait_for_ablation(args.runner_pid, args.timeout_hours)

    python = sys.executable
    run([python, "rarepdet/tools/build_v46_ablation_summary.py"], "build-ablation-summary")
    run([python, "rarepdet/tools/scan_v46_claims.py"], "claim-scan-initial")
    run([python, "rarepdet/tools/write_v46_blocker.py"], "write-blocker")
    run([python, "rarepdet/tools/run_v46_preflight.py"], "preflight")
    run([python, "rarepdet/tools/generate_handoff.py"], "generate-handoff")
    run([python, "rarepdet/tools/update_project_status.py"], "update-status")

    assert_scoped_worktree()
    stage_v46_outputs()
    preserve_root, moved = preserve_user_untracked_files()
    try:
        run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "rarepdet/tools/finish_task.ps1",
            ],
            "finish-task",
        )
    finally:
        restore_user_untracked_files(preserve_root, moved)

    head = run(["git", "rev-parse", "HEAD"], "read-final-head").stdout.strip()
    remote = run(
        ["git", "ls-remote", "research", "refs/heads/research/ra-repdet-triair"],
        "read-remote-head",
    ).stdout.strip().split()[0]
    if head != remote:
        raise RuntimeError(f"push verification mismatch: local={head} remote={remote}")
    emit(f"FINALIZER_SUCCESS commit={head}")


if __name__ == "__main__":
    main()
