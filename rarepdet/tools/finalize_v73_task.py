#!/usr/bin/env python
"""Fail-closed V73 documentation and test finalizer."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark"
DECISION = "V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE"
COMMIT = "exp: run V73 MM-UAV TriAir-initialized alignment-aware transfer benchmark"
REQUIRED = (
    "protocol.md", "protocol.json", "data_manifest_lock.json", "seed_epoch_order_hashes.json",
    "triair_source_checkpoint_manifest.json", "transfer_map_per_run.json", "initialization_audit.json",
    "training_trace_summary.json", "alignment_and_fusion_diagnostics.json", "recovery_ledger.json",
    "final_checkpoint_manifest.json", "per_run_metrics.csv", "per_run_metrics.json",
    "paired_transfer_comparison.csv", "paired_transfer_comparison.json", "three_seed_summary.json",
    "claim_boundary.json", "protected_file_audit.json", "test_commands.txt", "final_decision.json",
    "handoff.md",
)
PROTECTED = {
    "rarepdet/train_early_fusion.py",
    "rarepdet/models/early_fusion_fcos.py",
    "rarepdet/models/reliability_fusion_fcos.py",
    "datasets/triair_dataset.py",
}


def read(name: str) -> object:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    missing = [name for name in REQUIRED if not (OUT / name).is_file()]
    if missing:
        raise RuntimeError(f"V73 required outputs missing: {missing}")
    final = read("final_decision.json")
    metrics = read("per_run_metrics.json")["records"]
    checkpoints = read("final_checkpoint_manifest.json")
    traces = read("training_trace_summary.json")
    if final["decision"] != DECISION:
        raise RuntimeError(f"V73 is not complete: {final}")
    if len(metrics) != 9 or len(checkpoints["runs"]) != 9 or len(traces["runs"]) != 9:
        raise RuntimeError("V73 does not contain exactly nine completed records")
    if final["optimizer_steps"] != 646830 or final["devval_evaluations"] != 9:
        raise RuntimeError("V73 step/evaluation ceiling mismatch")
    if any(row["images"] != 1845 or row["evaluation_attempt"] != 1 for row in metrics):
        raise RuntimeError("V73 final-only devval evaluation contract mismatch")
    changed = set(git("diff", "--name-only", "3841455a39cced13a4925a6488a40b4a8f0c440b").splitlines())
    protected_changes = sorted(changed & PROTECTED)
    if protected_changes:
        raise RuntimeError(f"Protected V73 files changed: {protected_changes}")

    # Remove local absolute-path evidence before Git staging.
    initialization = read("initialization_audit.json")
    for row in initialization["seed_initializations"]:
        row.pop("path_local_not_committed", None)
        row.setdefault("local_artifact_id", f"seed{row['seed']}_v73_common_init.pt")
    (OUT / "initialization_audit.json").write_text(
        json.dumps(initialization, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for row in checkpoints["runs"]:
        local_path = row.pop("path_local_not_committed", None)
        if local_path:
            row["local_artifact_id"] = Path(local_path).name
    (OUT / "final_checkpoint_manifest.json").write_text(
        json.dumps(checkpoints, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    command = [
        sys.executable, "-m", "unittest", "discover", "-s", "tests",
        "-p", "test_v73_mmuav_transfer_benchmark.py", "-v",
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = "$ " + subprocess.list2cmdline(command) + "\n" + completed.stdout + completed.stderr
    (OUT / "test_output.txt").write_text(output, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError("V73 contract tests failed during finalization")
    protected = read("protected_file_audit.json")
    protected.update({
        "starting_commit": "3841455a39cced13a4925a6488a40b4a8f0c440b",
        "changes": [],
        "verified_at_completion": True,
    })
    (OUT / "protected_file_audit.json").write_text(
        json.dumps(protected, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = read("three_seed_summary.json")
    method_lines = []
    for method in ("scratch_equal", "triair_init_equal", "triair_init_reliability"):
        values = summary["methods"][method]
        method_lines.append(
            f"- `{method}`: AP {values['ap50_95']['mean']:.6f} +/- "
            f"{values['ap50_95']['sample_std']:.6f}; AP50 {values['ap50']['mean']:.6f}; "
            f"AR100 {values['ar100']['mean']:.6f}."
        )
    today = date.today().isoformat()
    status = f"""# Experiment Status

Updated: {today}

## Active status

`{DECISION}`

V73 completed all nine authorized `640 x 640` supervised MM-UAV runs: three methods, seeds 0/1/2,
ten epochs and 71,870 optimizer steps per run. Total completed optimizer steps: `646,830`.
Each final checkpoint was evaluated exactly once on all 1,845 exposed devval rows.

## Three-seed descriptive results

{chr(10).join(method_lines)}

See `runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/three_seed_summary.json`
for all AP/AR statistics and paired differences.

## Scientific boundary

This is `{read("claim_boundary.json")["scientific_label"]}`. It is not zero-shot, independent/blind
external validation, official untouched-test performance, or evidence of generalization without
MM-UAV labels. The three-seed comparisons are descriptive.
"""
    (ROOT / "docs/EXPERIMENT_STATUS.md").write_text(status, encoding="utf-8")
    (ROOT / "docs/TASK_BLOCKER.md").write_text(
        f"""# Task Blocker

Status: `{DECISION}`

Generated: {today}

V73 has no active blocker. All nine frozen runs, nine final-checkpoint-only evaluations, transfer
audits, recovery records, protected-file checks, and compact evidence outputs completed.

No additional tuning, rerun, epoch extension, checkpoint substitution, or manuscript claim is
authorized by this completion record.
""", encoding="utf-8")
    (ROOT / "docs/NEXT_TASK_WRITE_RECORD.md").write_text(
        f"""# Next Task Write Record

Updated: {today}

V73 execution completed with `{DECISION}`. No subsequent experiment has been authorized in this
task. The next task must be written explicitly before further experimental work.
""", encoding="utf-8")
    (ROOT / "docs/NEXT_TASK.md").write_text(
        f"""# Current Task

## Completion

`{DECISION}`

V73 completed all nine supervised MM-UAV transfer runs and all nine authorized final-checkpoint-only
devval evaluations. Compact evidence is under
`runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/`.

No new experiment is authorized by this completion record.

## Commit Message

{COMMIT}
""", encoding="utf-8")
    print(json.dumps({"status": "V73_FINALIZATION_READY", "decision": DECISION}, indent=2))


if __name__ == "__main__":
    main()
