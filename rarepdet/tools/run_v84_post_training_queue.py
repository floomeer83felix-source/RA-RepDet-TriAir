"""Wait for V84 P1, then run the resumable P2-P4 GPU/CPU analyses."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/v84_jei_critical_closure/post_training_queue"
P1_SUMMARY = ROOT / "runs/v84_jei_critical_closure/rgb_thermal_baseline/summary.json"
P1_PID = ROOT / "runs/v84_jei_critical_closure/rgb_thermal_baseline/queue.pid"
COMMANDS = (
    ("P2_CHANNEL_REMOVAL", ROOT / "rarepdet/tools/run_v84_channel_removal_2x2.py"),
    ("P3_GATE_QUALITY", ROOT / "rarepdet/tools/run_v84_gate_quality_analysis.py"),
    ("P4_COMPONENT_BOOTSTRAP", ROOT / "rarepdet/tools/run_v84_component_cluster_bootstrap.py"),
)


def write_status(payload: dict[str, object]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    payload["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    temporary = (OUT / "run_status.json.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(OUT / "run_status.json")


def p1_complete() -> bool:
    if not P1_SUMMARY.is_file():
        return False
    return json.loads(P1_SUMMARY.read_text(encoding="utf-8")).get("status") == "V84_RGB_THERMAL_3_SEED_COMPLETE"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    log_path = OUT / "queue.log"
    while not p1_complete():
        write_status({"state": "WAITING_FOR_P1", "next": COMMANDS[0][0],
                      "locked_holdout_accessed": False})
        time.sleep(60)
    completed = []
    for phase, script in COMMANDS:
        write_status({"state": "RUNNING", "phase": phase, "completed": completed,
                      "locked_holdout_accessed": False})
        command = [sys.executable, str(script)]
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(subprocess.list2cmdline(command) + "\n"); handle.flush()
            result = subprocess.run(command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, text=True)
        if result.returncode != 0:
            write_status({"state": "FAILED", "phase": phase, "completed": completed,
                          "returncode": result.returncode, "log": str(log_path),
                          "locked_holdout_accessed": False})
            raise SystemExit(result.returncode)
        completed.append(phase)
    write_status({"state": "COMPLETE", "completed": completed, "locked_holdout_accessed": False})


if __name__ == "__main__":
    main()
