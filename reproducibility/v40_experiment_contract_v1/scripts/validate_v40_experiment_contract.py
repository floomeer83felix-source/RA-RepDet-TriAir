#!/usr/bin/env python
"""Validate the frozen V40 v2 experiment contract bundle."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime


CONTRACT_REL = Path("reproducibility/v40_experiment_contract_v1")
TRAIN_MANIFEST_REL = Path("reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt")
VAL_MANIFEST_REL = Path("reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt")
STATUS_JSON_REL = CONTRACT_REL / "reports" / "V40_EXPERIMENT_CONTRACT_STATUS.json"
CONTRACT_JSON_REL = CONTRACT_REL / "contract" / "v40_experiment_contract.json"
SOURCE_LOCK_REL = CONTRACT_REL / "source_lock" / "input_lock_manifest.csv"
RUN_MATRIX_REL = CONTRACT_REL / "contract" / "v40_run_matrix.csv"
COMMANDS_REL = CONTRACT_REL / "contract" / "v40_training_command_templates.csv"
LABEL_COUNTS_REL = CONTRACT_REL / "contract" / "v40_label_counts.json"
LABEL_FREE_SMOKE_REL = CONTRACT_REL / "smoke_tests" / "label_free_config_smoke.json"
MODEL_FORWARD_SMOKE_REL = CONTRACT_REL / "smoke_tests" / "model_forward_smoke.json"
OUTPUT_MANIFEST_REL = CONTRACT_REL / "reports" / "output_sha256_manifest.csv"

DISALLOWED_PROSE_PHRASES = [
    "leakage-free",
    "independent test",
    "held-out test",
    "verified temporal metadata",
    "sequence label",
    "real sensor-failure robustness",
]


def project_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_to_root(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def git_output(root: Path, args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"NA ({exc})"


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def manifest_line_count(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#"))


def add_check(checks: list[dict], name: str, observed, expected, ok: bool, severity: str = "required") -> None:
    checks.append(
        {
            "check": name,
            "observed": observed,
            "expected": expected,
            "status": "PASS" if ok else "FAIL",
            "severity": severity,
        }
    )


def update_output_manifest(root: Path) -> None:
    contract_root = root / CONTRACT_REL
    rows = []
    for path in sorted(contract_root.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        rel = rel_to_root(path, root)
        if rel == OUTPUT_MANIFEST_REL.as_posix():
            continue
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    write_csv(root / OUTPUT_MANIFEST_REL, rows, ["path", "bytes", "sha256"])


def validate(root: Path) -> tuple[str, list[dict], dict]:
    checks: list[dict] = []
    contract = json.loads((root / CONTRACT_JSON_REL).read_text(encoding="utf-8"))
    status = json.loads((root / STATUS_JSON_REL).read_text(encoding="utf-8"))
    label_counts = json.loads((root / LABEL_COUNTS_REL).read_text(encoding="utf-8"))
    label_free = json.loads((root / LABEL_FREE_SMOKE_REL).read_text(encoding="utf-8"))
    forward = json.loads((root / MODEL_FORWARD_SMOKE_REL).read_text(encoding="utf-8"))
    run_matrix = read_csv(root / RUN_MATRIX_REL)
    commands = read_csv(root / COMMANDS_REL)
    source_rows = read_csv(root / SOURCE_LOCK_REL)

    add_check(checks, "contract_status", contract.get("status"), "V40_EXPERIMENT_CONTRACT_PASS", contract.get("status") == "V40_EXPERIMENT_CONTRACT_PASS")
    add_check(checks, "status_report_status", status.get("status"), "V40_EXPERIMENT_CONTRACT_PASS", status.get("status") == "V40_EXPERIMENT_CONTRACT_PASS")
    add_check(checks, "gate0_status", contract.get("gate0_status"), "V40_V2_READY_FOR_FROZEN_RERUN", contract.get("gate0_status") == "V40_V2_READY_FOR_FROZEN_RERUN")
    add_check(checks, "label_free_smoke", label_free.get("status"), "PASS", label_free.get("status") == "PASS")
    add_check(checks, "model_forward_smoke", forward.get("status"), "PASS", forward.get("status") == "PASS")

    add_check(checks, "train_manifest_line_count", manifest_line_count(root / TRAIN_MANIFEST_REL), 7439, manifest_line_count(root / TRAIN_MANIFEST_REL) == 7439)
    add_check(checks, "validation_manifest_line_count", manifest_line_count(root / VAL_MANIFEST_REL), 2213, manifest_line_count(root / VAL_MANIFEST_REL) == 2213)
    add_check(checks, "contract_train_manifest_sha", contract["manifests"]["train"]["sha256"], sha256_file(root / TRAIN_MANIFEST_REL), contract["manifests"]["train"]["sha256"] == sha256_file(root / TRAIN_MANIFEST_REL))
    add_check(checks, "contract_validation_manifest_sha", contract["manifests"]["validation"]["sha256"], sha256_file(root / VAL_MANIFEST_REL), contract["manifests"]["validation"]["sha256"] == sha256_file(root / VAL_MANIFEST_REL))
    add_check(checks, "validation_gt_boxes", label_counts["validation"]["gt_boxes"], 5867, int(label_counts["validation"]["gt_boxes"]) == 5867)
    add_check(checks, "run_matrix_count", len(run_matrix), 8, len(run_matrix) == 8)
    add_check(checks, "command_template_count", len(commands), 8, len(commands) == 8)

    seeds = sorted({row["seed"] for row in run_matrix})
    add_check(checks, "run_seeds", ",".join(seeds), "0,2", seeds == ["0", "2"])
    model_dropout_pairs = sorted({(row["model_type"], row["modality_dropout"]) for row in run_matrix})
    expected_pairs = sorted({("early", "0.00"), ("reliability", "0.00"), ("reliability", "0.15"), ("reliability", "0.20")})
    add_check(checks, "model_dropout_pairs", str(model_dropout_pairs), str(expected_pairs), model_dropout_pairs == expected_pairs)

    command_blob = "\n".join(row["train_command_template"] + "\n" + row["standardized_evaluator_command_template"] for row in commands)
    required_tokens = [
        TRAIN_MANIFEST_REL.as_posix().replace("/", "\\"),
        VAL_MANIFEST_REL.as_posix().replace("/", "\\"),
        "--epochs 50",
        "--batch-size 4",
        "--img-size 640",
        "--lr 1e-4",
        "--detector-score-thr 0.001",
        "--metric-score-thr 0.50",
        "--nms-thresh 0.6",
        "--detections-per-img 100",
    ]
    for token in required_tokens:
        add_check(checks, f"command_contains_{token}", str(token in command_blob), "True", token in command_blob)
    forbidden_tokens = ["v40_expanded_adjacency_component_split_v1", "v40_guard", "finish_task.ps1", "eval_missing_modality", "profile_", "DroneVehicle"]
    for token in forbidden_tokens:
        add_check(checks, f"command_excludes_{token}", str(token in command_blob), "False", token not in command_blob)

    source_failures = []
    for row in source_rows:
        path = root / row["path"]
        if row["exists"] != "yes" or not path.is_file() or sha256_file(path) != row["sha256"]:
            source_failures.append(row["path"])
    add_check(checks, "source_hashes_current", ",".join(source_failures) if source_failures else "all_match", "all_match", not source_failures)

    prose_files = []
    for path in (root / CONTRACT_REL).rglob("*"):
        if path.suffix.lower() in {".md", ".json", ".csv"} and path.name != "output_sha256_manifest.csv":
            prose_files.append(path)
    phrase_hits = []
    for path in prose_files:
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for phrase in DISALLOWED_PROSE_PHRASES:
            if phrase in text:
                phrase_hits.append(f"{rel_to_root(path, root)}::{phrase}")
    add_check(checks, "master_plan_disallowed_phrases_absent", "; ".join(phrase_hits) if phrase_hits else "none", "none", not phrase_hits)

    unchanged_flags = {
        "training_started": status.get("training_started") is False,
        "metric_evaluation_started": status.get("metric_evaluation_started") is False,
        "profiling_started": status.get("profiling_started") is False,
        "robustness_started": status.get("robustness_started") is False,
        "manuscript_changed": status.get("manuscript_changed") is False,
        "dronevehicle_changed": status.get("dronevehicle_changed") is False,
        "raw_data_changed": status.get("raw_data_changed") is False,
        "labels_changed": status.get("labels_changed") is False,
        "model_or_training_core_changed": status.get("model_or_training_core_changed") is False,
    }
    add_check(checks, "no_forbidden_work_started_or_changed", json.dumps(unchanged_flags, sort_keys=True), "all_true", all(unchanged_flags.values()))

    overall = "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL"
    summary = {
        "status": overall,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_commit": git_output(root, ["rev-parse", "HEAD"]),
        "output_commit": "PENDING_FINAL_COMMIT_RECORDED_IN_GIT_HISTORY_AND_FINAL_RESPONSE",
        "checks_total": len(checks),
        "checks_failed": sum(1 for row in checks if row["status"] != "PASS"),
        "contract_status": contract.get("status"),
        "train_count": label_counts["train"]["entries"],
        "validation_count": label_counts["validation"]["entries"],
        "validation_gt_boxes": label_counts["validation"]["gt_boxes"],
    }
    return overall, checks, summary


def write_validation_reports(root: Path, overall: str, checks: list[dict], summary: dict) -> None:
    reports = root / CONTRACT_REL / "reports"
    write_csv(reports / "v40_experiment_contract_validation.csv", checks, ["check", "observed", "expected", "status", "severity"])
    write_json(reports / "v40_experiment_contract_validation.json", {"summary": summary, "checks": checks})
    lines = [
        "# V40 Experiment Contract Validation",
        "",
        f"- Status: `{overall}`",
        f"- Generated: `{summary['generated_at']}`",
        f"- Input commit: `{summary['input_commit']}`",
        f"- Output commit: `{summary['output_commit']}`",
        f"- Checks failed: `{summary['checks_failed']}` / `{summary['checks_total']}`",
        "",
        "| Check | Observed | Expected | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in checks:
        lines.append(f"| {row['check']} | `{row['observed']}` | `{row['expected']}` | `{row['status']}` |")
    (reports / "v40_experiment_contract_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    update_output_manifest(root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the V40 v2 experiment contract bundle.")
    parser.add_argument("--root", default=str(project_root_from_script()), type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    overall, checks, summary = validate(root)
    write_validation_reports(root, overall, checks, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if overall == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
