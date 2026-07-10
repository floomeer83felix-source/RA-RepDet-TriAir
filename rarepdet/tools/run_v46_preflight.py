#!/usr/bin/env python
"""Run and record the final V46 code and evidence preflight."""

import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v46_coco_ablation"

PYTHON_FILES = [
    "rarepdet/coco_metrics.py",
    "rarepdet/tools/eval_coco_map.py",
    "rarepdet/tools/smoke_test_coco_metrics.py",
    "rarepdet/tools/create_v46_source_lock.py",
    "rarepdet/tools/run_v46_fixed_coco.py",
    "rarepdet/tools/build_v46_coco_summary.py",
    "rarepdet/tools/run_v46_ablation_seed0.py",
    "rarepdet/tools/build_v46_ablation_summary.py",
    "rarepdet/tools/scan_v46_claims.py",
    "rarepdet/tools/v46_handoff.py",
    "rarepdet/tools/write_v46_blocker.py",
    "rarepdet/tools/finalize_v46_task.py",
    "rarepdet/tools/generate_handoff.py",
    "rarepdet/tools/update_project_status.py",
    "rarepdet/tools/run_v46_preflight.py",
]

REQUIRED_OUTPUTS = [
    "source_lock_v46.md",
    "source_lock_v46.json",
    "coco_devval_per_run.csv",
    "coco_guard_per_run.csv",
    "coco_devval_paired_deltas.csv",
    "coco_guard_paired_deltas.csv",
    "coco_metric_summary.md",
    "coco_metric_summary.json",
    "ablation_train_commands.txt",
    "ablation_devval_per_run.csv",
    "ablation_devval_summary.md",
    "ablation_devval_summary.json",
    "ablation_claim_boundary.md",
    "v46_claim_scan.txt",
    "v46_claim_scan_review.md",
]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_text(command):
    return subprocess.list2cmdline([str(item) for item in command])


def run_command(command):
    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return process.returncode, process.stdout


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_project_metric_reproduction():
    expected_path = (
        PROJECT_ROOT
        / "runs"
        / "v41_q1_upgrade"
        / "interim_devval"
        / "three_seed_interim_devval_summary.csv"
    )
    with expected_path.open("r", encoding="utf-8-sig", newline="") as handle:
        expected_rows = list(csv.DictReader(handle))
    expected = {row["run_id"]: row for row in expected_rows}
    differences = []
    for path in sorted((OUTPUT_DIR / "raw" / "coco" / "devval").glob("*.json")):
        result = load_json(path)
        row = expected[result["run_id"]]
        ap50_delta = float(result["project_ap50"]) - float(row["ap50"])
        ap75_delta = float(result["project_ap75"]) - float(row["ap75"])
        differences.append((result["run_id"], ap50_delta, ap75_delta))
        if abs(ap50_delta) > 1e-12 or abs(ap75_delta) > 1e-12:
            raise RuntimeError(
                f"project metric reproduction failed for {result['run_id']}: {ap50_delta}, {ap75_delta}"
            )
    return differences


def validate_evidence():
    source_lock = load_json(OUTPUT_DIR / "source_lock_v46.json")
    checks = []

    for path_text in PYTHON_FILES:
        path = PROJECT_ROOT / path_text
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if line.endswith((" ", "\t")):
                raise RuntimeError(f"trailing whitespace: {path_text}:{line_number}")
        checks.append(f"PASS Python whitespace check {path_text}")

    for role, record in source_lock["manifests"].items():
        observed = sha256(PROJECT_ROOT / record["path"])
        if observed != record["sha256"]:
            raise RuntimeError(f"manifest hash changed for {role}")
        checks.append(f"PASS manifest {role} sha256={observed}")

    for record in source_lock["fixed_checkpoints"]:
        observed = sha256(PROJECT_ROOT / record["path"])
        if observed != record["sha256"]:
            raise RuntimeError(f"fixed checkpoint hash changed for {record['run_id']}")
        checks.append(f"PASS fixed checkpoint {record['run_id']} sha256={observed}")

    for path_text, expected_hash in source_lock["code_sha256"].items():
        observed = sha256(PROJECT_ROOT / path_text)
        if observed != expected_hash:
            raise RuntimeError(f"source-locked code changed after execution: {path_text}")
        checks.append(f"PASS code {path_text} sha256={observed}")

    for output_name in REQUIRED_OUTPUTS:
        path = OUTPUT_DIR / output_name
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"missing or empty required output: {path}")
        checks.append(f"PASS required output {output_name} bytes={path.stat().st_size}")

    fixed_results = list((OUTPUT_DIR / "raw" / "coco").glob("*/*.json"))
    if len(fixed_results) != 12:
        raise RuntimeError(f"expected 12 fixed COCO results, found {len(fixed_results)}")
    checks.append("PASS fixed COCO result count=12")

    ablation_results = list((OUTPUT_DIR / "raw" / "ablation_devval").glob("*.json"))
    if len(ablation_results) != 2:
        raise RuntimeError(f"expected 2 seed0 ablation results, found {len(ablation_results)}")
    checks.append("PASS fresh seed0 ablation result count=2")

    forbidden_guard_outputs = list(OUTPUT_DIR.glob("ablation_guard_*")) + list(
        (OUTPUT_DIR / "raw").glob("ablation_guard/**/*")
    )
    if forbidden_guard_outputs:
        raise RuntimeError(f"unexpected ablation guard outputs: {forbidden_guard_outputs}")
    checks.append("PASS no ablation guard evaluation outputs")

    execution_status = load_json(OUTPUT_DIR / "ablation_execution_status.json")
    if execution_status["status"] != "SEED0_FEASIBLE_ABLATIONS_COMPLETE":
        raise RuntimeError("fresh seed0 ablation runner is incomplete")
    if execution_status["guard_used"]:
        raise RuntimeError("ablation execution status reports guard use")
    checks.append("PASS ablation execution complete with guard_used=false")

    coco_summary = load_json(OUTPUT_DIR / "coco_metric_summary.json")
    if coco_summary["status"] != "V46_FIXED_COCO_EVALUATION_COMPLETE":
        raise RuntimeError("COCO summary status is incomplete")
    ablation_summary = load_json(OUTPUT_DIR / "ablation_devval_summary.json")
    if ablation_summary["status"] != "V46_CAUSAL_ABLATION_SEED0_PARTIAL_COMPLETE":
        raise RuntimeError("ablation summary status is unexpected")
    checks.append("PASS summary status values")

    review = (OUTPUT_DIR / "v46_claim_scan_review.md").read_text(encoding="utf-8")
    if "Result: `PASS`" not in review or "Unresolved affirmative matches: 0" not in review:
        raise RuntimeError("claim scan did not pass")
    checks.append("PASS claim scan unresolved affirmative matches=0")

    blocker = (PROJECT_ROOT / "docs" / "TASK_BLOCKER.md").read_text(encoding="utf-8")
    if "V46_PARTIAL_COMPLETION_GPU_TIME_AND_ALLOWED_SCOPE_BLOCKER" not in blocker:
        raise RuntimeError("V46 partial-completion blocker status is missing")
    checks.append("PASS V46 partial-completion blocker recorded")

    metric_differences = validate_project_metric_reproduction()
    for run_id, ap50_delta, ap75_delta in metric_differences:
        checks.append(
            f"PASS project metric reproduction {run_id} ap50_delta={ap50_delta:.3e} ap75_delta={ap75_delta:.3e}"
        )

    return checks


def main():
    commands = [
        [sys.executable, "-m", "py_compile", *PYTHON_FILES],
        [sys.executable, "rarepdet/tools/smoke_test_coco_metrics.py"],
        [sys.executable, "rarepdet/tools/build_v46_coco_summary.py"],
        [sys.executable, "rarepdet/tools/build_v46_ablation_summary.py"],
        [sys.executable, "rarepdet/tools/scan_v46_claims.py"],
        ["git", "diff", "--check"],
    ]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "preflight_commands.txt").write_text(
        "\n".join(command_text(command) for command in commands) + "\n",
        encoding="utf-8",
    )

    output_lines = [
        f"generated_at: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
    ]
    failed = False
    for command in commands:
        text = command_text(command)
        return_code, output = run_command(command)
        output_lines.extend(
            [
                f"===== COMMAND: {text} =====",
                f"return_code: {return_code}",
                output.rstrip(),
                "",
            ]
        )
        if return_code != 0:
            failed = True
            break

    if not failed:
        try:
            checks = validate_evidence()
            output_lines.extend(["===== INTERNAL EVIDENCE CHECKS =====", *checks, ""])
        except Exception as exc:
            failed = True
            output_lines.extend(["===== INTERNAL EVIDENCE CHECKS =====", f"FAIL {exc}", ""])

    output_lines.append(f"FINAL_STATUS: {'FAIL' if failed else 'PASS'}")
    (OUTPUT_DIR / "preflight_outputs.txt").write_text(
        "\n".join(output_lines) + "\n", encoding="utf-8"
    )
    print(output_lines[-1])
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
