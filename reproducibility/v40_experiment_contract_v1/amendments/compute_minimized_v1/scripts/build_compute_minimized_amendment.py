#!/usr/bin/env python
"""Build the V40 compute-minimized contract amendment.

This amends launch scope only. It does not edit the original contract and does
not start training, metric evaluation, profiling, robustness, qualitative,
manuscript, or external-data work.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from datetime import datetime


AMEND_REL = Path("reproducibility/v40_experiment_contract_v1/amendments/compute_minimized_v1")
ORIGINAL_CONTRACT_REL = Path("reproducibility/v40_experiment_contract_v1/contract/v40_experiment_contract.json")
ORIGINAL_STATUS_REL = Path("reproducibility/v40_experiment_contract_v1/reports/V40_EXPERIMENT_CONTRACT_STATUS.json")
ORIGINAL_VALIDATION_REL = Path("reproducibility/v40_experiment_contract_v1/reports/v40_experiment_contract_validation.json")
ORIGINAL_OUTPUT_MANIFEST_REL = Path("reproducibility/v40_experiment_contract_v1/reports/output_sha256_manifest.csv")
TRAIN_MANIFEST_REL = Path("reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt")
VAL_MANIFEST_REL = Path("reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt")
V40_SPLIT_AUDIT_REL = Path("reproducibility/v40_expanded_adjacency_component_split_v2/audits/v40_split_audit_report.json")
V40_SPLIT_STATUS_REL = Path("reproducibility/v40_expanded_adjacency_component_split_v2/reports/V40_V2_EXPANDED_ADJACENCY_SPLIT_STATUS.json")

OUTPUT_ROOT = "runs/v40_expanded_adjacency_v2_compute_minimized"
STATUS_READY = "V40_COMPUTE_MINIMIZED_CONTRACT_READY"
STATUS_BLOCKED = "V40_COMPUTE_MINIMIZED_CONTRACT_BLOCKED"
PYTHON_EXE = r"C:\Users\xinnan\.conda\envs\pytorch\python.exe"

SOURCE_LOCK_INPUTS = [
    ("amendment_task", Path("docs/V40_COMPUTE_MINIMIZED_CONTRACT_AMENDMENT_TASK.md")),
    ("master_plan", Path("docs/PRE_MANUSCRIPT_V40_MASTER_PLAN.md")),
    ("compute_minimized_plan", Path("docs/V40_COMPUTE_MINIMIZED_EVIDENCE_PLAN.md")),
    ("original_contract_json", ORIGINAL_CONTRACT_REL),
    ("original_contract_status", ORIGINAL_STATUS_REL),
    ("original_contract_validation", ORIGINAL_VALIDATION_REL),
    ("original_contract_output_manifest", ORIGINAL_OUTPUT_MANIFEST_REL),
    ("train_manifest", TRAIN_MANIFEST_REL),
    ("validation_manifest", VAL_MANIFEST_REL),
    ("v40_split_audit", V40_SPLIT_AUDIT_REL),
    ("v40_split_status", V40_SPLIT_STATUS_REL),
    ("trainer", Path("rarepdet/train_early_fusion.py")),
    ("evaluator", Path("rarepdet/eval_map.py")),
    ("metrics", Path("rarepdet/metrics.py")),
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


def source_lock_rows(root: Path) -> list[dict]:
    rows = []
    for role, rel_path in SOURCE_LOCK_INPUTS:
        path = root / rel_path
        exists = path.is_file()
        rows.append(
            {
                "role": role,
                "path": rel_path.as_posix(),
                "exists": "yes" if exists else "no",
                "bytes": path.stat().st_size if exists else "NA",
                "sha256": sha256_file(path) if exists else "NA",
            }
        )
    for role, rel_path in [
        ("amendment_builder", AMEND_REL / "scripts" / "build_compute_minimized_amendment.py"),
        ("amendment_validator", AMEND_REL / "scripts" / "validate_compute_minimized_amendment.py"),
    ]:
        path = root / rel_path
        exists = path.is_file()
        rows.append(
            {
                "role": role,
                "path": rel_path.as_posix(),
                "exists": "yes" if exists else "no",
                "bytes": path.stat().st_size if exists else "NA",
                "sha256": sha256_file(path) if exists else "NA",
            }
        )
    return rows


def build_run_matrix(contract: dict) -> list[dict]:
    train = contract["manifests"]["train"]["path"]
    val = contract["manifests"]["validation"]["path"]
    epochs = contract["training_recipe"]["epochs"]
    img_size = contract["training_recipe"]["img_size"]
    batch_size = contract["training_recipe"]["batch_size"]
    lr = "1e-4"
    num_workers = contract["evaluation_recipe"]["num_workers"]
    runs = [
        ("matched_early_seed0", "matched early fusion", "early", 0, "0.00", "comparator"),
        ("matched_early_seed2", "matched early fusion", "early", 2, "0.00", "comparator"),
        ("reliability_p015_seed0", "pre-specified reliability-aware p=0.15", "reliability", 0, "0.15", "primary"),
        ("reliability_p015_seed2", "pre-specified reliability-aware p=0.15", "reliability", 2, "0.15", "primary"),
    ]
    return [
        {
            "run_id": run_id,
            "description": description,
            "model_type": model_type,
            "seed": seed,
            "modality_dropout": dropout,
            "role": role,
            "epochs": epochs,
            "img_size": img_size,
            "batch_size": batch_size,
            "lr": lr,
            "num_workers": num_workers,
            "train_manifest": train,
            "validation_manifest": val,
            "out_dir": f"{OUTPUT_ROOT}/{run_id}",
        }
        for run_id, description, model_type, seed, dropout, role in runs
    ]


def build_commands(root: Path, contract: dict, run_matrix: list[dict]) -> list[dict]:
    dataset_root = contract["dataset"]["root"]
    train_manifest = root / TRAIN_MANIFEST_REL
    val_manifest = root / VAL_MANIFEST_REL
    eval_recipe = contract["evaluation_recipe"]
    rows = []
    for run in run_matrix:
        train_parts = [
            PYTHON_EXE,
            "rarepdet/train_early_fusion.py",
            "--model",
            run["model_type"],
            "--data",
            dataset_root,
            "--train-split",
            str(train_manifest),
            "--val-split",
            str(val_manifest),
            "--epochs",
            str(run["epochs"]),
            "--batch-size",
            str(run["batch_size"]),
            "--img-size",
            str(run["img_size"]),
            "--device",
            "cuda",
            "--lr",
            run["lr"],
            "--num-workers",
            str(run["num_workers"]),
            "--modality-dropout",
            run["modality_dropout"],
            "--seed",
            str(run["seed"]),
            "--out",
            run["out_dir"],
        ]
        eval_parts = [
            PYTHON_EXE,
            "rarepdet/eval_map.py",
            "--model",
            run["model_type"],
            "--data",
            dataset_root,
            "--split-file",
            str(val_manifest),
            "--weights",
            f"{run['out_dir']}/weights/best.pt",
            "--img-size",
            str(eval_recipe["img_size"]),
            "--device",
            "cuda",
            "--batch-size",
            str(eval_recipe["batch_size"]),
            "--num-workers",
            str(eval_recipe["num_workers"]),
            "--detector-score-thr",
            str(eval_recipe["detector_score_thr"]),
            "--metric-score-thr",
            f"{eval_recipe['metric_score_thr']:.2f}",
            "--nms-thresh",
            str(eval_recipe["nms_thresh"]),
            "--detections-per-img",
            str(eval_recipe["detections_per_img"]),
            "--out",
            f"{run['out_dir']}/standardized_eval/eval_results.txt",
        ]
        rows.append(
            {
                "run_id": run["run_id"],
                "train_command_template": " ".join(train_parts),
                "standardized_evaluator_command_template": " ".join(eval_parts),
            }
        )
    return rows


def output_manifest(root: Path) -> list[dict]:
    amend_root = root / AMEND_REL
    rows = []
    for path in sorted(amend_root.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        rel = rel_to_root(path, root)
        if rel == (AMEND_REL / "reports" / "output_sha256_manifest.csv").as_posix():
            continue
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def build_payload(root: Path) -> dict:
    generated_at = datetime.now().isoformat(timespec="seconds")
    original = json.loads((root / ORIGINAL_CONTRACT_REL).read_text(encoding="utf-8"))
    original_status = json.loads((root / ORIGINAL_STATUS_REL).read_text(encoding="utf-8"))
    original_validation = json.loads((root / ORIGINAL_VALIDATION_REL).read_text(encoding="utf-8"))
    v40_status = json.loads((root / V40_SPLIT_STATUS_REL).read_text(encoding="utf-8"))
    source_rows = source_lock_rows(root)
    run_matrix = build_run_matrix(original)
    commands = build_commands(root, original, run_matrix)

    ready = (
        original.get("status") == "V40_EXPERIMENT_CONTRACT_PASS"
        and original_status.get("status") == "V40_EXPERIMENT_CONTRACT_PASS"
        and original_validation.get("summary", {}).get("status") == "PASS"
        and v40_status.get("status") == "V40_V2_READY_FOR_FROZEN_RERUN"
        and len(run_matrix) == 4
        and {row["run_id"] for row in run_matrix}
        == {"matched_early_seed0", "matched_early_seed2", "reliability_p015_seed0", "reliability_p015_seed2"}
        and not (root / OUTPUT_ROOT).exists()
    )
    status = STATUS_READY if ready else STATUS_BLOCKED
    input_commit = git_output(root, ["rev-parse", "HEAD"])

    amendment = {
        "schema_version": "v40_compute_minimized_contract_amendment_v1",
        "status": status,
        "generated_at": generated_at,
        "input_commit": input_commit,
        "output_commit": "PENDING_FINAL_COMMIT_RECORDED_IN_GIT_HISTORY_AND_FINAL_RESPONSE",
        "original_contract_status": original.get("status"),
        "original_contract_preserved_as": "archival evidence",
        "supersedes_for_launch_scope": ORIGINAL_CONTRACT_REL.as_posix(),
        "launch_scope_status": "compute-minimized four-run V40-v2 plan",
        "evidence_scope": "validation-only evidence on the V40 v2 expanded-adjacency component-disjoint split",
        "pre_specification": "Reliability-aware p=0.15 is pre-specified from archived development evidence before any V40 result is viewed. It is not selected or optimized on V40.",
        "paper_comparison": "matched early fusion versus the pre-specified reliability-aware p=0.15 configuration",
        "replaced_selection_rule": "No V40 dropout selection is performed. The paper comparison is limited to matched early fusion versus the pre-specified reliability-aware p=0.15 configuration.",
        "forbidden_v40_runs": ["reliability p=0.00", "reliability p=0.20"],
        "output_root": OUTPUT_ROOT,
        "run_ids": [row["run_id"] for row in run_matrix],
        "manifest_hashes": {
            "train": original["manifests"]["train"]["sha256"],
            "validation": original["manifests"]["validation"]["sha256"],
        },
        "evaluator_hash": original["model_source"]["relevant_file_hashes"]["rarepdet/eval_map.py"],
        "trainer_hash": original["model_source"]["relevant_file_hashes"]["rarepdet/train_early_fusion.py"],
        "training_recipe": original["training_recipe"],
        "evaluation_recipe": original["evaluation_recipe"],
        "no_forbidden_work": {
            "training_started": False,
            "metric_evaluation_started": False,
            "result_recorded": False,
            "checkpoint_created": False,
            "loss_or_validation_iteration_run": False,
            "profiling_started": False,
            "robustness_started": False,
            "qualitative_started": False,
            "manuscript_changed": False,
            "external_data_used": False,
            "dronevehicle_changed": False,
        },
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
    }
    return {
        "amendment": amendment,
        "run_matrix": run_matrix,
        "commands": commands,
        "source_rows": source_rows,
    }


def write_markdown(root: Path, payload: dict) -> None:
    amend = payload["amendment"]
    amend_root = root / AMEND_REL
    lines = [
        "# V40 Compute-Minimized Contract Amendment",
        "",
        f"- Status: `{amend['status']}`",
        f"- Generated: `{amend['generated_at']}`",
        f"- Input commit: `{amend['input_commit']}`",
        f"- Output commit: `{amend['output_commit']}`",
        f"- Original contract: `{amend['supersedes_for_launch_scope']}`",
        f"- Original contract disposition: `{amend['original_contract_preserved_as']}`",
        f"- New output root: `{amend['output_root']}`",
        "",
        "## Launch Scope",
        "",
        "This amendment supersedes the older eight-run dropout sweep only for launch scope.",
        "The original contract remains archival evidence for recipe, source, manifest, and smoke-test locks.",
        "",
        "| Run ID | Model | Seed | Dropout | Role |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["run_matrix"]:
        lines.append(f"| `{row['run_id']}` | `{row['model_type']}` | `{row['seed']}` | `{row['modality_dropout']}` | `{row['role']}` |")
    lines.extend(
        [
            "",
            "## Pre-Specification",
            "",
            amend["pre_specification"],
            "",
            "## Replaced Selection Rule",
            "",
            amend["replaced_selection_rule"],
            "",
            "Do not run p=0.00 or p=0.20 for this V40 compute-minimized launch scope.",
            "",
            "## No Work Started",
            "",
        ]
    )
    lines.extend(f"- `{key}`: `{value}`" for key, value in amend["no_forbidden_work"].items())
    (amend_root / "contract" / "V40_COMPUTE_MINIMIZED_CONTRACT_AMENDMENT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    status_lines = [
        "# V40 Compute-Minimized Contract Status",
        "",
        f"- Status: `{amend['status']}`",
        f"- Input commit: `{amend['input_commit']}`",
        f"- Output commit: `{amend['output_commit']}`",
        f"- Run count: `{len(payload['run_matrix'])}`",
        f"- Output root: `{amend['output_root']}`",
        f"- Training started: `{amend['no_forbidden_work']['training_started']}`",
        f"- Metric evaluation started: `{amend['no_forbidden_work']['metric_evaluation_started']}`",
        f"- Manuscript changed: `{amend['no_forbidden_work']['manuscript_changed']}`",
        f"- External data used: `{amend['no_forbidden_work']['external_data_used']}`",
    ]
    (amend_root / "reports" / "V40_COMPUTE_MINIMIZED_CONTRACT_STATUS.md").write_text("\n".join(status_lines) + "\n", encoding="utf-8")

    lock_lines = [
        "# V40 Compute-Minimized Source Lock",
        "",
        f"- Input commit: `{amend['input_commit']}`",
        f"- Source rows: `{len(payload['source_rows'])}`",
        "",
        "See `input_lock_manifest.csv` for locked paths and SHA-256 values.",
    ]
    (amend_root / "source_lock" / "input_lock.md").write_text("\n".join(lock_lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the compute-minimized V40 contract amendment.")
    parser.add_argument("--root", default=str(project_root_from_script()), type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    amend_root = root / AMEND_REL
    for subdir in ["contract", "source_lock", "reports"]:
        (amend_root / subdir).mkdir(parents=True, exist_ok=True)

    payload = build_payload(root)
    write_json(amend_root / "contract" / "v40_compute_minimized_contract_amendment.json", payload["amendment"])
    write_csv(
        amend_root / "contract" / "v40_compute_minimized_run_matrix.csv",
        payload["run_matrix"],
        ["run_id", "description", "model_type", "seed", "modality_dropout", "role", "epochs", "img_size", "batch_size", "lr", "num_workers", "train_manifest", "validation_manifest", "out_dir"],
    )
    write_csv(amend_root / "contract" / "v40_compute_minimized_command_templates.csv", payload["commands"], ["run_id", "train_command_template", "standardized_evaluator_command_template"])
    write_csv(amend_root / "source_lock" / "input_lock_manifest.csv", payload["source_rows"], ["role", "path", "exists", "bytes", "sha256"])
    payload["amendment"]["source_lock_manifest_sha256"] = sha256_file(amend_root / "source_lock" / "input_lock_manifest.csv")
    write_json(amend_root / "contract" / "v40_compute_minimized_contract_amendment.json", payload["amendment"])
    write_json(amend_root / "reports" / "V40_COMPUTE_MINIMIZED_CONTRACT_STATUS.json", payload["amendment"])
    write_markdown(root, payload)
    write_csv(amend_root / "reports" / "output_sha256_manifest.csv", output_manifest(root), ["path", "bytes", "sha256"])
    print(json.dumps({"status": payload["amendment"]["status"], "amendment_root": str(amend_root)}, indent=2))
    return 0 if payload["amendment"]["status"] == STATUS_READY else 2


if __name__ == "__main__":
    raise SystemExit(main())
