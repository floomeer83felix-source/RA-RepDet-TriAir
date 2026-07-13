#!/usr/bin/env python
"""Finalize, commit, and push a fully completed V50 queue."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = PROJECT_ROOT / "runs/v50_visdrone_seen"
USER_UNTRACKED_TOOL_FILES = (
    PROJECT_ROOT / "rarepdet/tools/eval_dronevehicle_modality_specific.py",
    PROJECT_ROOT / "rarepdet/tools/prepare_dronevehicle_modality_specific_eval.py",
)


def run(command):
    print(subprocess.list2cmdline([str(item) for item in command]), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def untracked(path):
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", str(path)],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    return bool(result.stdout.strip())


def preserve_user_files():
    temporary = Path(tempfile.mkdtemp(prefix="rarepdet_v50_preserve_"))
    moved = []
    for source in USER_UNTRACKED_TOOL_FILES:
        if source.is_file() and untracked(source):
            destination = temporary / source.name
            shutil.move(str(source), str(destination))
            moved.append((source, destination))
    return temporary, moved


def restore_user_files(temporary, moved):
    for source, saved in moved:
        if source.exists():
            raise RuntimeError(f"cannot restore over existing file: {source}")
        shutil.move(str(saved), str(source))
    temporary.rmdir()


def stage_v50_outputs():
    candidates = []
    for path in OUTPUT.rglob("*"):
        if not path.is_file() or "weights" in path.parts:
            continue
        if path.name in {"rgb_queue_launcher_stdout.log", "rgb_queue_launcher_stderr.log"}:
            continue
        if path.suffix.lower() in {".md", ".json", ".csv", ".txt", ".log"}:
            candidates.append(path.relative_to(PROJECT_ROOT).as_posix())
    if candidates:
        run(["git", "add", "-f", "--", *sorted(candidates)])
    run(
        [
            "git",
            "add",
            "--",
            "datasets/visdrone_seen_dataset.py",
            "rarepdet/models/rgb_fcos.py",
            "rarepdet/train_visdrone_rgb.py",
            "rarepdet/v50_coco.py",
            "rarepdet/tools/build_v50_reports.py",
            "rarepdet/tools/eval_v50_visdrone_seen.py",
            "rarepdet/tools/finalize_v50_task.py",
            "rarepdet/tools/preflight_v50_visdrone_seen.py",
            "rarepdet/tools/prepare_v50_visdrone_seen.py",
            "rarepdet/tools/run_v50_rgb_queue.py",
            "rarepdet/tools/scan_v50_claims.py",
            "rarepdet/tools/v50_handoff.py",
            "rarepdet/tools/generate_handoff.py",
            "rarepdet/tools/update_project_status.py",
            "tests/test_v50_visdrone_seen.py",
        ]
    )


def main():
    status = json.loads((OUTPUT / "rgb_run_status.json").read_text(encoding="utf-8"))
    if status.get("state") != "COMPLETE":
        raise RuntimeError("cannot finalize before the RGB queue is complete")
    for protocol in ("devval", "test"):
        if len(list((OUTPUT / f"raw/rgb/{protocol}").glob("*.json"))) != 3:
            raise RuntimeError(f"missing RGB {protocol} results")
    run([sys.executable, "rarepdet/tools/build_v50_reports.py"])
    run([sys.executable, "rarepdet/tools/scan_v50_claims.py"])
    from v50_handoff import write_v50_blocker

    write_v50_blocker(PROJECT_ROOT)
    stage_v50_outputs()
    temporary, moved = preserve_user_files()
    try:
        run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "rarepdet/tools/finish_task.ps1",
            ]
        )
    finally:
        restore_user_files(temporary, moved)


if __name__ == "__main__":
    main()
