"""Freeze the V84 published-comparator audit without vendoring third-party code."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path


EXPECTED_COMMIT = "8f4e31ed64f1f2fe019d4706670fc4560c0b2e23"
EXPECTED_REMOTE = "https://github.com/radlab-sketch/trimodal-uav-det.git"


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evidence(repo: Path, relative: str, needles: tuple[str, ...]) -> list[dict[str, object]]:
    rows = []
    for number, line in enumerate((repo / relative).read_text(encoding="utf-8").splitlines(), 1):
        if any(needle in line for needle in needles):
            rows.append({"path": relative, "line": number, "text": line.strip()})
    return rows


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(r"E:\v84_comparator_trimodal_uav_det"))
    parser.add_argument(
        "--out", type=Path,
        default=Path("runs/v84_jei_critical_closure/published_comparator"),
    )
    args = parser.parse_args()
    source = args.source.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    commit = git(source, "rev-parse", "HEAD")
    remote = git(source, "remote", "get-url", "origin")
    if commit != EXPECTED_COMMIT or remote != EXPECTED_REMOTE:
        raise RuntimeError(f"Comparator source lock mismatch: {remote}@{commit}")

    tracked = git(source, "ls-files").splitlines()
    inventory = []
    for relative in tracked:
        path = source / relative
        inventory.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)})
    with (out / "source_inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("path", "bytes", "sha256"))
        writer.writeheader()
        writer.writerows(inventory)

    license_files = [name for name in tracked if Path(name).name.lower().startswith(("license", "copying"))]
    source_lock = {
        "repository": remote,
        "commit": commit,
        "tracked_files": len(inventory),
        "tracked_bytes": sum(row["bytes"] for row in inventory),
        "license_or_copying_files": license_files,
        "source_vendored_into_ra_repdet": False,
    }
    write_json(out / "source_lock.json", source_lock)

    audit_evidence = []
    audit_evidence += evidence(source, "trimodaldet/data/dataset.py", (
        "have corresponding non-empty labels", "train_test_split(", "test_size=test_size",
    ))
    audit_evidence += evidence(source, "README.md", (
        "Automatic 80/20", "--epochs 15 --batch-size 2", "MIT License",
    ))
    audit_evidence += evidence(source, "trimodaldet/config.py", (
        "self.num_epochs", "self.batch_size", "self.learning_rate",
    ))
    audit_evidence += evidence(source, "trimodaldet/training/trainer.py", (
        "torch.save", "self.config.model_path",
    ))
    audit = {
        "candidate": "Tri-Modal Fusion Transformers for UAV-based Object Detection (TriModalDet)",
        "modalities": ["RGB", "thermal", "event"],
        "official_source_lock": source_lock,
        "observations": {
            "dataset_contract": "NPY plus YOLO labels; valid samples require a corresponding non-empty label.",
            "split_contract": "Implementation creates its own random 80/20 train/test split.",
            "training_recipe": "README recipe states 15 epochs, batch size 2, SGD, and lr 0.005; code defaults differ for batch size and lr.",
            "checkpoint_contract": "The primary trainer saves one configured final model path; it does not expose the frozen V84 devval-selection interface.",
            "license_contract": "README says MIT License, but the pinned tree contains no LICENSE or COPYING file with grant text.",
        },
        "evidence": audit_evidence,
    }
    write_json(out / "protocol_audit.json", audit)

    decision = {
        "status": "DOCUMENTED_STOP",
        "same_component_disjoint_split": False,
        "same_standardized_coco_evaluator": False,
        "training_started": False,
        "metrics_reported": False,
        "reasons": [
            "The official loader replaces the frozen component-disjoint split with an internal random 80/20 split and drops empty-label samples.",
            "The official training/evaluation path does not implement the V84 standardized COCO evaluator and frozen checkpoint-selection contract.",
            "Adapting both contracts would require a substantial unvalidated harness rather than reproduction of the pinned official implementation.",
            "The pinned repository has no LICENSE/COPYING grant text; the README-only license label is insufficient for vendoring or modifying the code in this repository.",
        ],
        "scientific_boundary": "No numerical comparison is made against the paper's published metrics because its split/evaluator contract differs.",
        "locked_holdout_accessed": False,
    }
    write_json(out / "stop_decision.json", decision)
    (out / "STOP_DECISION.md").write_text(
        "# V84 Published Comparator Stop Decision\n\n"
        f"Candidate: TriModalDet, official source `{remote}` pinned at `{commit}`.\n\n"
        "Status: **DOCUMENTED STOP**. No training or evaluation was started.\n\n"
        "The pinned official loader performs an internal random 80/20 split and retains only samples with "
        "non-empty labels. Its primary path also lacks the frozen component-disjoint manifest interface, "
        "the V84 standardized COCO evaluator, and the frozen development-validation checkpoint-selection "
        "contract. Replacing those parts would be a substantial new adaptation, not a direct reproduction. "
        "In addition, the tree has no LICENSE/COPYING grant text, although the README labels the project MIT.\n\n"
        "Therefore V84 reports no cross-protocol number and does not invent a comparison. The source inventory, "
        "hashes, and line-level protocol evidence are archived beside this decision. The locked holdout was not accessed.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
