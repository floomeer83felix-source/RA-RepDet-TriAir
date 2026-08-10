"""Build the V84 MM-UAV reproducibility package from frozen V53/V73/V75 evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


TRAIN_SHA256 = "e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a"
DEVVAL_SHA256 = "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54"
V73 = Path("runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark")
V75 = Path("runs/v75_v73_corrected_seed_level_evidence_integration")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_manifest(path: Path, expected_hash: str, expected_rows: int) -> list[dict[str, str]]:
    if sha256(path) != expected_hash:
        raise RuntimeError(f"Frozen manifest hash mismatch: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != expected_rows:
        raise RuntimeError(f"Frozen manifest row count mismatch: {path}")
    return rows


def sequence_summary(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    counts = Counter(row["sequence"] for row in rows)
    return [{"sequence_id": key, "rows": counts[key]} for key in sorted(counts)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--train-manifest", type=Path,
        default=Path("runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt"),
    )
    parser.add_argument(
        "--devval-manifest", type=Path,
        default=Path("runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"),
    )
    parser.add_argument(
        "--out", type=Path,
        default=Path("runs/v84_jei_critical_closure/mm_uav_reproducibility"),
    )
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    train = read_manifest(args.train_manifest, TRAIN_SHA256, 7187)
    devval = read_manifest(args.devval_manifest, DEVVAL_SHA256, 1845)
    train_sequences = {row["sequence"] for row in train}
    devval_sequences = {row["sequence"] for row in devval}
    overlap = sorted(train_sequences & devval_sequences)
    if overlap:
        raise RuntimeError(f"Sequence leakage in frozen manifests: {overlap}")

    manifest_summary = {
        "train": {
            "path": args.train_manifest.as_posix(), "sha256": TRAIN_SHA256, "rows": len(train),
            "sequences": sequence_summary(train),
        },
        "devval": {
            "path": args.devval_manifest.as_posix(), "sha256": DEVVAL_SHA256, "rows": len(devval),
            "sequences": sequence_summary(devval), "previously_exposed": True,
        },
        "sequence_overlap": overlap,
        "selection": "Rows with rgb_annotation_rows > 0 from the frozen V53 synchronized inventory.",
        "excluded_not_negatives": {
            "ir_only_rows": 106,
            "unlabeled_rows": 35898,
            "interpretation": "Excluded from RGB-supervised training/evaluation; not treated as negative images.",
        },
    }
    write_json(out / "sequence_manifest_summary.json", manifest_summary)

    transfer_payload = load_json(V73 / "transfer_map_per_run.json")
    transfer_runs = transfer_payload["runs"]
    initialized = [row for row in transfer_runs if row["source"] is not None]
    fractions = sorted({round(float(row["transferred_parameter_fraction"]), 12) for row in initialized})
    if len(fractions) != 1:
        raise RuntimeError(f"Inconsistent initialized transfer fractions: {fractions}")
    representative = initialized[0]
    unmatched_groups = Counter(key.split(".")[1] if key.startswith("detector.") else key.split(".")[0]
                               for key in representative["unmatched_destination"])
    transfer_summary = {
        "authoritative_source": (V73 / "transfer_map_per_run.json").as_posix(),
        "authoritative_source_sha256": sha256(V73 / "transfer_map_per_run.json"),
        "initialized_runs": len(initialized),
        "rule": "Copy only source tensors whose names begin with backbone.repvit., backbone.fpn., or head.; prepend detector.; require an exact destination name and exact tensor shape.",
        "transferred_numel": representative["transferred_numel"],
        "destination_numel": representative["destination_numel"],
        "fraction_exact": representative["transferred_parameter_fraction"],
        "fraction_percent_rounded": round(100 * representative["transferred_parameter_fraction"], 2),
        "interpretation": "99.20% is the fraction of destination parameter/buffer elements initialized by exact name-and-shape-compatible TriAir tensors; it is not a sample match rate or an architecture identity claim.",
        "not_transferred": {
            "destination_keys": representative["unmatched_destination"],
            "destination_key_group_counts": dict(sorted(unmatched_groups.items())),
            "source_tensors_skipped": representative["skipped_source"],
            "reason": "MM-UAV-specific input projection and feature-alignment/reliability scaffold are destination-only; source tensors outside the shared RepViT/FPN/FCOS prefixes or without exact compatibility are skipped.",
        },
        "tensor_repair_or_seed_substitution": False,
    }
    write_json(out / "parameter_transfer_audit.json", transfer_summary)

    protocol = load_json(V73 / "protocol.json")
    corrected = load_json(V75 / "corrected_per_run_metrics.json")
    corrected_records = corrected["records"]
    if len(corrected_records) != 9:
        raise RuntimeError("Expected the frozen V75 nine-run corrected result table")
    write_json(out / "training_evaluation_protocol.json", {
        "authoritative_results": (V75 / "corrected_per_run_metrics.json").as_posix(),
        "authoritative_results_sha256": sha256(V75 / "corrected_per_run_metrics.json"),
        "seeds": [0, 1, 2],
        "methods": ["scratch_equal", "triair_init_equal", "triair_init_reliability"],
        "runs": len(corrected_records),
        "training": protocol,
        "checkpoint_selection": "Final checkpoint after exactly 10 epochs; no development-validation inference during training.",
        "evaluation": "One evaluation on the previously exposed development-validation split after final checkpoint creation.",
        "claim_boundary": "Supervised target-domain training with exposed devval, not blind zero-shot or external-test evidence.",
        "locked_holdout_accessed": False,
    })

    (out / "ANNOTATION_AND_GEOMETRY.md").write_text(
        "# MM-UAV Annotation and Geometry Contract\n\n"
        "Each manifest row identifies one synchronized RGB, infrared, and event frame. Only rows with at least "
        "one RGB annotation are included. The 106 IR-only and 35,898 unlabeled inventory rows are excluded and "
        "are not interpreted as negatives. Train and devval contain 7,187 and 1,845 rows, respectively, with no "
        "sequence overlap. Exact sequence IDs and row counts are in `sequence_manifest_summary.json`.\n\n"
        "Provider tracking rows are parsed at the manifest frame index. Columns are frame index, track ID, x, y, "
        "width, and height; positive-width/height boxes are converted from xywh to xyxy. The foreground category "
        "is the provider drone class, and track IDs are retained as metadata.\n\n"
        "RGB, infrared, and event images are loaded independently and independently letterboxed to 640x640. "
        "This preprocessing is not geometric registration. Detection boxes remain in the RGB coordinate system "
        "and are transformed only with the RGB letterbox scale and padding. The model uses modality-specific "
        "feature extraction followed by learned feature alignment; it does not concatenate unregistered raw channels.\n",
        encoding="utf-8",
    )
    (out / "HANDOFF.md").write_text(
        "# V84 MM-UAV Reproducibility Handoff\n\n"
        "Status: complete from frozen V53/V73/V75 evidence; no new training was run.\n\n"
        "The package freezes exact manifest hashes and sequence membership, frame selection, annotation conversion, "
        "independent geometry preprocessing, the exact name/shape transfer rule, the meaning and exclusions of the "
        "reported 99.20% compatibility, three-seed training settings, final-checkpoint evaluation, and the supervised "
        "exposed-devval claim boundary. No locked-holdout resource was accessed.\n",
        encoding="utf-8",
    )
    evidence_files = [
        V73 / "data_manifest_lock.json", V73 / "protocol.json", V73 / "transfer_map_per_run.json",
        V73 / "alignment_and_fusion_diagnostics.json", V75 / "corrected_per_run_metrics.json",
        Path("datasets/mmuav_feature_alignment_dataset.py"),
        Path("rarepdet/tools/prepare_v53_mmuav_feature_alignment.py"),
        Path("rarepdet/tools/run_v73_mmuav_transfer_benchmark.py"),
    ]
    write_json(out / "evidence_index.json", {
        "inputs": [{"path": path.as_posix(), "sha256": sha256(path)} for path in evidence_files],
        "generated_by": "rarepdet/tools/build_v84_mmuav_reproducibility.py",
    })


if __name__ == "__main__":
    main()
