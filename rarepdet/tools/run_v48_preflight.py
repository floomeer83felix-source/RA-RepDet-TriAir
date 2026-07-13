#!/usr/bin/env python
"""Run source-lock, model, metric, profiling, and submission checks for V48."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v48_complete_ablation"
PYTHON_FILES = (
    "rarepdet/coco_metrics.py", "rarepdet/train_early_fusion.py", "rarepdet/eval_map.py",
    "rarepdet/models/early_fusion_fcos.py", "rarepdet/models/repvit_fpn_backbone.py", "rarepdet/models/ablation_fusion_fcos.py",
    "rarepdet/tools/eval_coco_map.py", "rarepdet/tools/create_v48_source_lock.py", "rarepdet/tools/profile_v48_models.py",
    "rarepdet/tools/run_v48_training.py", "rarepdet/tools/build_v48_summary.py", "rarepdet/tools/scan_v48_claims.py",
    "rarepdet/tools/run_v48_preflight.py", "rarepdet/tools/run_v48_queue.py", "rarepdet/tools/finalize_v48_task.py",
    "rarepdet/tools/v48_handoff.py", "rarepdet/tools/generate_handoff.py", "rarepdet/tools/update_project_status.py",
    "tests/test_v48_ablation_fusion.py", "datasets/triair_dataset.py",
)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_text(command):
    return subprocess.list2cmdline([str(item) for item in command])


def run(command):
    process = subprocess.run(command, cwd=PROJECT_ROOT, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout


def internal_checks():
    lock = json.loads((OUTPUT_DIR / "source_lock_v48.json").read_text(encoding="utf-8"))
    checks = []
    for role, record in lock["manifests"].items():
        observed = sha256(PROJECT_ROOT / record["path"])
        if observed != record["sha256"]:
            raise RuntimeError(f"manifest hash changed for {role}")
        checks.append(f"PASS manifest {role} sha256={observed}")
    for path_text, expected in lock["code_sha256"].items():
        observed = sha256(PROJECT_ROOT / path_text)
        if observed != expected:
            raise RuntimeError(f"source-locked code changed: {path_text}")
        checks.append(f"PASS source lock {path_text}")
    if any(OUTPUT_DIR.glob("raw/guard/**/*")):
        raise RuntimeError("unexpected V48 guard output")
    checks.append("PASS no V48 guard output")
    summary = json.loads((OUTPUT_DIR / "causal_ablation_summary.json").read_text(encoding="utf-8"))
    if summary["guard_used_for_training_or_selection"]:
        raise RuntimeError("V48 summary reports guard use")
    checks.append("PASS summary reports guard_used=false")
    review = (OUTPUT_DIR / "claim_scan_review.md").read_text(encoding="utf-8")
    if "Result: `PASS`" not in review:
        raise RuntimeError("claim scan did not pass")
    checks.append("PASS claim scan")
    return checks


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    commands = [
        (True, [sys.executable, "-m", "py_compile", *PYTHON_FILES]),
        (True, [sys.executable, "tests/test_v48_ablation_fusion.py"]),
        (True, [sys.executable, "rarepdet/tools/smoke_test_coco_metrics.py"]),
        (True, [sys.executable, "rarepdet/tools/build_v48_summary.py"]),
        (True, [sys.executable, "rarepdet/tools/scan_v48_claims.py"]),
        (True, [sys.executable, "rarepdet/tools/profile_v48_models.py", "--models", "ra_static_equal", "--img-size", "64", "--batch-size", "1", "--device", "cpu", "--warmup", "0", "--iterations", "1", "--out-dir", "runs/v48_complete_ablation/preflight_profile_smoke"]),
        (False, [sys.executable, "scripts/preflight_submission.py", "--allow-placeholders"]),
        (True, ["git", "diff", "--check"]),
    ]
    (OUTPUT_DIR / "preflight_commands.txt").write_text("\n".join(command_text(command) for _, command in commands) + "\n", encoding="utf-8")
    output = [f"generated_at: {datetime.now().astimezone().isoformat(timespec='seconds')}", ""]
    failed = False
    for blocking, command in commands:
        code, text = run(command)
        output.extend([f"===== COMMAND: {command_text(command)} =====", f"return_code: {code}", text.rstrip()])
        if code != 0 and not blocking:
            output.extend(["classification: NONBLOCKING_EXISTING_SUBMISSION_PREFLIGHT_FAILURE", "reason: V48 is forbidden from changing frozen manuscript, bibliography, or submission files.", ""])
            continue
        output.append("")
        if code != 0:
            failed = True
            break
    if not failed:
        try:
            output.extend(["===== INTERNAL CHECKS =====", *internal_checks(), ""])
        except Exception as exc:
            failed = True
            output.extend(["===== INTERNAL CHECKS =====", f"FAIL {exc}", ""])
    output.append(f"FINAL_STATUS: {'FAIL' if failed else 'PASS'}")
    (OUTPUT_DIR / "preflight_outputs.txt").write_text("\n".join(output) + "\n", encoding="utf-8")
    print(output[-1])
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
