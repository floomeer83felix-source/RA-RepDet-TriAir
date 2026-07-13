#!/usr/bin/env python
"""Finalize a fully completed V48 queue, preserve user files, then finish and push."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v48_complete_ablation"
USER_UNTRACKED_TOOL_FILES = (
    PROJECT_ROOT / "rarepdet" / "tools" / "eval_dronevehicle_modality_specific.py",
    PROJECT_ROOT / "rarepdet" / "tools" / "prepare_dronevehicle_modality_specific_eval.py",
)


def run(command):
    print(subprocess.list2cmdline([str(item) for item in command]), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def untracked(path):
    result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", str(path)], cwd=PROJECT_ROOT, text=True, stdout=subprocess.PIPE, check=True)
    return bool(result.stdout.strip())


def preserve_user_files():
    temporary = Path(tempfile.mkdtemp(prefix="rarepdet_v48_preserve_"))
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


def stage_v48_outputs():
    candidates = []
    for path in OUTPUT_DIR.rglob("*"):
        if not path.is_file() or "weights" in path.parts or path.suffix.lower() in {".pt", ".pth", ".ckpt", ".tmp", ".pid"}:
            continue
        if path.suffix.lower() in {".md", ".json", ".csv", ".txt", ".log"}:
            candidates.append(path.relative_to(PROJECT_ROOT).as_posix())
    if candidates:
        run(["git", "add", "-f", "--", *sorted(candidates)])
    run(["git", "add", "--", "tests/test_v48_ablation_fusion.py"])


def main():
    run([sys.executable, "rarepdet/tools/build_v48_summary.py"])
    execution = json.loads((OUTPUT_DIR / "run_status.json").read_text(encoding="utf-8"))
    if execution["completed_fresh_runs"] != execution["required_fresh_runs"]:
        raise RuntimeError("cannot finalize V48 before all fresh runs complete")
    run([sys.executable, "rarepdet/tools/profile_v48_models.py", "--models", "early,reliability,ra_static_equal,ra_stems_project", "--device", "cuda", "--img-size", "640", "--batch-size", "1", "--warmup", "10", "--iterations", "30"])
    run([sys.executable, "rarepdet/tools/scan_v48_claims.py"])
    run([sys.executable, "rarepdet/tools/run_v48_preflight.py"])
    stage_v48_outputs()
    temporary, moved = preserve_user_files()
    try:
        run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "rarepdet/tools/finish_task.ps1"])
    finally:
        restore_user_files(temporary, moved)


if __name__ == "__main__":
    main()
