#!/usr/bin/env python
"""Run the V48 source-locked jobs in paired GPU batches and finalize on success."""

from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v48_complete_ablation"
RUNNER = PROJECT_ROOT / "rarepdet" / "tools" / "run_v48_training.py"
BATCHES = (
    ("ra_static_equal_seed0", "ra_stems_project_seed0"),
    ("ra_no_moddrop_seed1", "early_moddrop_seed1"),
    ("ra_static_equal_seed1", "ra_stems_project_seed1"),
    ("ra_no_moddrop_seed2", "early_moddrop_seed2"),
    ("ra_static_equal_seed2", "ra_stems_project_seed2"),
)


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def complete(run_id):
    path = OUTPUT_DIR / "training" / run_id / "run_status.json"
    return path.is_file() and json.loads(path.read_text(encoding="utf-8")).get("state") == "COMPLETE"


def refresh():
    for script in ("build_v48_summary.py", "scan_v48_claims.py", "run_v48_preflight.py"):
        command = [sys.executable, str(PROJECT_ROOT / "rarepdet" / "tools" / script)]
        process = subprocess.run(command, cwd=PROJECT_ROOT, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(process.stdout, end="", flush=True)
        if process.returncode != 0:
            raise RuntimeError(f"refresh failed: {script}")


def main():
    if not (OUTPUT_DIR / "source_lock_v48.json").is_file():
        raise FileNotFoundError("run create_v48_source_lock.py and V48 preflight before starting the queue")
    queue_log = OUTPUT_DIR / "queue_stdout_stderr.log"
    with queue_log.open("a", encoding="utf-8") as handle:
        for batch_index, batch in enumerate(BATCHES, start=1):
            pending = [run_id for run_id in batch if not complete(run_id)]
            if not pending:
                handle.write(f"SKIP batch {batch_index} complete {now()}\n")
                continue
            handle.write(f"START batch {batch_index}: {pending} {now()}\n")
            handle.flush()
            processes = []
            for run_id in pending:
                command = [sys.executable, str(RUNNER), "--run-id", run_id]
                processes.append((run_id, subprocess.Popen(command, cwd=PROJECT_ROOT, stdout=handle, stderr=subprocess.STDOUT, text=True)))
            failed = []
            for run_id, process in processes:
                return_code = process.wait()
                handle.write(f"END batch {batch_index} run={run_id} return_code={return_code} {now()}\n")
                if return_code != 0:
                    failed.append(run_id)
            handle.flush()
            refresh()
            if failed:
                raise RuntimeError(f"V48 queue stopped after failed runs: {failed}")
    refresh()
    summary = json.loads((OUTPUT_DIR / "run_status.json").read_text(encoding="utf-8"))
    if summary["completed_fresh_runs"] != summary["required_fresh_runs"]:
        raise RuntimeError("queue ended without all required V48 fresh runs")
    finalizer = [sys.executable, str(PROJECT_ROOT / "rarepdet" / "tools" / "finalize_v48_task.py")]
    raise SystemExit(subprocess.call(finalizer, cwd=PROJECT_ROOT))


if __name__ == "__main__":
    main()
