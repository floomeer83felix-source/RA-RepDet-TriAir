#!/usr/bin/env python
"""Validate the V40 compute-minimized contract amendment."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime


AMEND_REL = Path("reproducibility/v40_experiment_contract_v1/amendments/compute_minimized_v1")
ORIGINAL_CONTRACT_REL = Path("reproducibility/v40_experiment_contract_v1/contract/v40_experiment_contract.json")
TRAIN_MANIFEST_REL = Path("reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt")
VAL_MANIFEST_REL = Path("reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt")

AMEND_JSON_REL = AMEND_REL / "contract" / "v40_compute_minimized_contract_amendment.json"
RUN_MATRIX_REL = AMEND_REL / "contract" / "v40_compute_minimized_run_matrix.csv"
COMMANDS_REL = AMEND_REL / "contract" / "v40_compute_minimized_command_templates.csv"
SOURCE_LOCK_REL = AMEND_REL / "source_lock" / "input_lock_manifest.csv"
STATUS_JSON_REL = AMEND_REL / "reports" / "V40_COMPUTE_MINIMIZED_CONTRACT_STATUS.json"
OUTPUT_MANIFEST_REL = AMEND_REL / "reports" / "output_sha256_manifest.csv"

STATUS_READY = "V40_COMPUTE_MINIMIZED_CONTRACT_READY"
STATUS_BLOCKED = "V40_COMPUTE_MINIMIZED_CONTRACT_BLOCKED"
EXPECTED_RUN_IDS = ["matched_early_seed0", "matched_early_seed2", "reliability_p015_seed0", "reliability_p015_seed2"]
OUTPUT_ROOT = Path("runs/v40_expanded_adjacency_v2_compute_minimized")
DISALLOWED_TOKENS = [
    "reliability_p000",
    "reliability_p020",
    "p=0.00",
    "p=0.20",
    "runs/v40_expanded_adjacency/",
    "eval_missing_modality",
    "profile_",
    "DroneVehicle",
    "finish_task.ps1",
]
DISALLOWED_PROSE_PHRASES = [
    "leakage-free",
    "independent test",
    "held-out test",
    "verified temporal metadata",
    "sequence label",
    "real sensor-failure robustness",
]


def project_root_from_script() -> Path:
    return Path(__file__).resolve().parents[5]


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


def add(checks: list[dict], name: str, observed, expected, ok: bool) -> None:
    checks.append({"check": name, "observed": observed, "expected": expected, "status": "PASS" if ok else "FAIL"})


def manifest_count(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#"))


def output_manifest(root: Path) -> list[dict]:
    amend_root = root / AMEND_REL
    rows = []
    for path in sorted(amend_root.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        rel = rel_to_root(path, root)
        if rel == OUTPUT_MANIFEST_REL.as_posix():
            continue
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def command_blob(commands: list[dict]) -> str:
    return "\n".join(row["train_command_template"] + "\n" + row["standardized_evaluator_command_template"] for row in commands)


def validate(root: Path) -> tuple[str, list[dict], dict]:
    checks: list[dict] = []
    amendment = json.loads((root / AMEND_JSON_REL).read_text(encoding="utf-8"))
    status = json.loads((root / STATUS_JSON_REL).read_text(encoding="utf-8"))
    original = json.loads((root / ORIGINAL_CONTRACT_REL).read_text(encoding="utf-8"))
    run_matrix = read_csv(root / RUN_MATRIX_REL)
    commands = read_csv(root / COMMANDS_REL)
    source_rows = read_csv(root / SOURCE_LOCK_REL)

    add(checks, "amendment_status", amendment.get("status"), STATUS_READY, amendment.get("status") == STATUS_READY)
    add(checks, "status_report_status", status.get("status"), STATUS_READY, status.get("status") == STATUS_READY)
    add(checks, "original_contract_preserved_as_archival", amendment.get("original_contract_preserved_as"), "archival evidence", amendment.get("original_contract_preserved_as") == "archival evidence")
    add(checks, "run_count", len(run_matrix), 4, len(run_matrix) == 4)
    add(checks, "exact_run_ids", ",".join(row["run_id"] for row in run_matrix), ",".join(EXPECTED_RUN_IDS), [row["run_id"] for row in run_matrix] == EXPECTED_RUN_IDS)
    add(checks, "seeds", ",".join(sorted({row["seed"] for row in run_matrix})), "0,2", sorted({row["seed"] for row in run_matrix}) == ["0", "2"])

    model_dropout = sorted({(row["model_type"], row["modality_dropout"]) for row in run_matrix})
    add(checks, "model_dropout_scope", str(model_dropout), "[('early', '0.00'), ('reliability', '0.15')]", model_dropout == [("early", "0.00"), ("reliability", "0.15")])
    add(checks, "command_template_count", len(commands), 4, len(commands) == 4)
    add(checks, "train_manifest_hash_matches_original", sha256_file(root / TRAIN_MANIFEST_REL), original["manifests"]["train"]["sha256"], sha256_file(root / TRAIN_MANIFEST_REL) == original["manifests"]["train"]["sha256"])
    add(checks, "validation_manifest_hash_matches_original", sha256_file(root / VAL_MANIFEST_REL), original["manifests"]["validation"]["sha256"], sha256_file(root / VAL_MANIFEST_REL) == original["manifests"]["validation"]["sha256"])
    add(checks, "train_manifest_count", manifest_count(root / TRAIN_MANIFEST_REL), 7439, manifest_count(root / TRAIN_MANIFEST_REL) == 7439)
    add(checks, "validation_manifest_count", manifest_count(root / VAL_MANIFEST_REL), 2213, manifest_count(root / VAL_MANIFEST_REL) == 2213)
    add(checks, "evaluator_hash_matches_original", sha256_file(root / "rarepdet/eval_map.py"), amendment["evaluator_hash"], sha256_file(root / "rarepdet/eval_map.py") == amendment["evaluator_hash"])
    add(checks, "trainer_hash_matches_original", sha256_file(root / "rarepdet/train_early_fusion.py"), amendment["trainer_hash"], sha256_file(root / "rarepdet/train_early_fusion.py") == amendment["trainer_hash"])

    for row in run_matrix:
        add(checks, f"{row['run_id']}_epochs", row["epochs"], original["training_recipe"]["epochs"], int(row["epochs"]) == int(original["training_recipe"]["epochs"]))
        add(checks, f"{row['run_id']}_img_size", row["img_size"], original["training_recipe"]["img_size"], int(row["img_size"]) == int(original["training_recipe"]["img_size"]))
        add(checks, f"{row['run_id']}_batch_size", row["batch_size"], original["training_recipe"]["batch_size"], int(row["batch_size"]) == int(original["training_recipe"]["batch_size"]))
        add(checks, f"{row['run_id']}_train_manifest", row["train_manifest"], original["manifests"]["train"]["path"], row["train_manifest"] == original["manifests"]["train"]["path"])
        add(checks, f"{row['run_id']}_validation_manifest", row["validation_manifest"], original["manifests"]["validation"]["path"], row["validation_manifest"] == original["manifests"]["validation"]["path"])

    blob = command_blob(commands)
    required_tokens = [
        "--epochs 50",
        "--batch-size 4",
        "--img-size 640",
        "--lr 1e-4",
        "--detector-score-thr 0.001",
        "--metric-score-thr 0.50",
        "--nms-thresh 0.6",
        "--detections-per-img 100",
        OUTPUT_ROOT.as_posix(),
    ]
    normalized_blob = blob.replace("\\", "/")
    for token in required_tokens:
        add(checks, f"commands_contain_{token}", str(token in normalized_blob), "True", token in normalized_blob)
    for token in DISALLOWED_TOKENS:
        add(checks, f"commands_exclude_{token}", str(token in normalized_blob), "False", token not in normalized_blob)

    source_failures = []
    for row in source_rows:
        path = root / row["path"]
        if row["exists"] != "yes" or not path.is_file() or sha256_file(path) != row["sha256"]:
            source_failures.append(row["path"])
    add(checks, "source_lock_hashes_current", ",".join(source_failures) if source_failures else "all_match", "all_match", not source_failures)

    flags = amendment.get("no_forbidden_work", {})
    add(checks, "no_forbidden_work_flags_false", json.dumps(flags, sort_keys=True), "all_false", all(value is False for value in flags.values()))
    output_path = root / OUTPUT_ROOT
    created_artifacts = []
    if output_path.exists():
        created_artifacts = [rel_to_root(path, root) for path in output_path.rglob("*") if path.is_file()]
    add(checks, "planned_output_root_has_no_artifacts", ",".join(created_artifacts) if created_artifacts else "none", "none", not created_artifacts)

    prose_hits = []
    for path in (root / AMEND_REL).rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".csv"}:
            continue
        if path.name == "output_sha256_manifest.csv":
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for phrase in DISALLOWED_PROSE_PHRASES:
            if phrase in text:
                prose_hits.append(f"{rel_to_root(path, root)}::{phrase}")
    add(checks, "master_plan_disallowed_phrases_absent", ";".join(prose_hits) if prose_hits else "none", "none", not prose_hits)

    overall = "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL"
    summary = {
        "status": overall,
        "amendment_status": STATUS_READY if overall == "PASS" else STATUS_BLOCKED,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_commit": git_output(root, ["rev-parse", "HEAD"]),
        "output_commit": "PENDING_FINAL_COMMIT_RECORDED_IN_GIT_HISTORY_AND_FINAL_RESPONSE",
        "checks_total": len(checks),
        "checks_failed": sum(1 for row in checks if row["status"] != "PASS"),
        "run_count": len(run_matrix),
        "run_ids": [row["run_id"] for row in run_matrix],
        "train_manifest_sha256": original["manifests"]["train"]["sha256"],
        "validation_manifest_sha256": original["manifests"]["validation"]["sha256"],
    }
    return overall, checks, summary


def write_reports(root: Path, overall: str, checks: list[dict], summary: dict) -> None:
    reports = root / AMEND_REL / "reports"
    write_csv(reports / "v40_compute_minimized_contract_validation.csv", checks, ["check", "observed", "expected", "status"])
    write_json(reports / "v40_compute_minimized_contract_validation.json", {"summary": summary, "checks": checks})
    lines = [
        "# V40 Compute-Minimized Contract Validation",
        "",
        f"- Status: `{overall}`",
        f"- Amendment status: `{summary['amendment_status']}`",
        f"- Input commit: `{summary['input_commit']}`",
        f"- Output commit: `{summary['output_commit']}`",
        f"- Checks failed: `{summary['checks_failed']}` / `{summary['checks_total']}`",
        "",
        "| Check | Observed | Expected | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in checks:
        lines.append(f"| {row['check']} | `{row['observed']}` | `{row['expected']}` | `{row['status']}` |")
    (reports / "v40_compute_minimized_contract_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_csv(root / OUTPUT_MANIFEST_REL, output_manifest(root), ["path", "bytes", "sha256"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the compute-minimized V40 contract amendment.")
    parser.add_argument("--root", default=str(project_root_from_script()), type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    overall, checks, summary = validate(root)
    write_reports(root, overall, checks, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if overall == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
