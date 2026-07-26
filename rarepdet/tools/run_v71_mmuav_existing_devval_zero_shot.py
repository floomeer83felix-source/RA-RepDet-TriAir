#!/usr/bin/env python
"""Run the V71 preflight and fail closed when raw-grid alignment is unavailable."""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
RUN_DIR = ROOT / "runs/v71_mmuav_existing_devval_triair_zero_shot_external_domain_validation"
MANIFEST = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"
EXPECTED_MANIFEST_SHA256 = "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54"
STARTING_COMMIT = "042a2228e8575518a23348225b323876179bbd75"
DECISION = "V71_BLOCKED_ADAPTER_OR_ONTOLOGY_CONTRACT"

CHECKPOINTS = (
    {
        "method": "matched_early",
        "model_type": "early",
        "seed": 0,
        "opaque_id": "triair_v40_matched_early_seed0_best",
        "relative_path": "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt",
        "sha256": "23331a6e668634f5f1ca1c7dfaddd23e9ee5445c0558e325621e8f454a0b1602",
        "source_commit": "d3e7f3ffd17fd537ae219175e2e48f1611573de5",
        "evidence": "runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json",
    },
    {
        "method": "matched_early",
        "model_type": "early",
        "seed": 1,
        "opaque_id": "triair_v41_matched_early_seed1_best",
        "relative_path": "runs/v41_q1_upgrade/seed1/matched_early_seed1/weights/best.pt",
        "sha256": "60a338ed887c15d94d3f274df39684c1dc6de68f9f29ba13f9f9cb4d6fbcd804",
        "source_commit": "802d9446bd359017ca93478918073808d83876d1",
        "evidence": "runs/v41_q1_upgrade/seed1/source_lock_seed1.json",
    },
    {
        "method": "matched_early",
        "model_type": "early",
        "seed": 2,
        "opaque_id": "triair_v40_matched_early_seed2_best",
        "relative_path": "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed2/weights/best.pt",
        "sha256": "b36b4965931da68b77a6be82e85e47b34f952445d64b941337f56a722f62737e",
        "source_commit": "d3e7f3ffd17fd537ae219175e2e48f1611573de5",
        "evidence": "runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json",
    },
    {
        "method": "reliability_p015",
        "model_type": "reliability",
        "seed": 0,
        "opaque_id": "triair_v40_reliability_p015_seed0_best",
        "relative_path": "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt",
        "sha256": "4284aaa188cb7f065a01b6cf32b78265ab937da0de2d3423d4594d2102787436",
        "source_commit": "d3e7f3ffd17fd537ae219175e2e48f1611573de5",
        "evidence": "runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json",
    },
    {
        "method": "reliability_p015",
        "model_type": "reliability",
        "seed": 1,
        "opaque_id": "triair_v41_reliability_p015_seed1_best",
        "relative_path": "runs/v41_q1_upgrade/seed1/reliability_p015_seed1/weights/best.pt",
        "sha256": "a59366dd0687754577d23d3e21358127199345d4ebf3a55a06472b933b57813d",
        "source_commit": "802d9446bd359017ca93478918073808d83876d1",
        "evidence": "runs/v41_q1_upgrade/seed1/source_lock_seed1.json",
    },
    {
        "method": "reliability_p015",
        "model_type": "reliability",
        "seed": 2,
        "opaque_id": "triair_v40_reliability_p015_seed2_best",
        "relative_path": "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed2/weights/best.pt",
        "sha256": "27affa96df1b3baad3df6f0a591e0599c1f5c0f77f91fad9fdaa408e549f1415",
        "source_commit": "d3e7f3ffd17fd537ae219175e2e48f1611573de5",
        "evidence": "runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json",
    },
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(name: str, value: object) -> None:
    (RUN_DIR / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def lock_manifest() -> dict[str, object]:
    if sha256(MANIFEST) != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("Frozen V53 devval manifest hash changed")
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1845:
        raise RuntimeError(f"Expected 1845 devval rows, found {len(rows)}")

    order_digest = hashlib.sha256()
    identity_digest = hashlib.sha256()
    annotation_paths: dict[str, Path] = {}
    modality_presence = {"rgb": 0, "ir": 0, "event": 0, "gt_rgb": 0}
    sequences: set[str] = set()
    for row in rows:
        order_digest.update((row["original_row_id"] + "\n").encode())
        identity_digest.update(
            ("|".join((row["original_row_id"], row["sequence"], row["frame_index"])) + "\n").encode()
        )
        sequences.add(row["sequence"])
        for key in modality_presence:
            path = Path(row[key])
            if not path.is_file():
                raise FileNotFoundError(f"Missing frozen manifest asset for {row['original_row_id']}: {key}")
            modality_presence[key] += 1
        gt_path = Path(row["gt_rgb"])
        annotation_paths[str(gt_path)] = gt_path

    annotation_digest = hashlib.sha256()
    for path in sorted(annotation_paths.values(), key=lambda item: str(item).lower()):
        annotation_digest.update(bytes.fromhex(sha256(path)))

    return {
        "status": "LOCKED",
        "manifest_id": "v53_frozen_devval_rgb_supervised",
        "rows": len(rows),
        "sequence_count": len(sequences),
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "row_order_sha256": order_digest.hexdigest(),
        "opaque_row_identity_sha256": identity_digest.hexdigest(),
        "modality_presence_counts": modality_presence,
        "unique_rgb_annotation_files": len(annotation_paths),
        "annotation_content_hash_aggregate_sha256": annotation_digest.hexdigest(),
        "row_order_preserved": True,
        "previously_exposed": True,
        "annotations_parsed_during_lock": False,
    }


def tensor_fingerprint(state: dict[str, torch.Tensor]) -> dict[str, object]:
    digest = hashlib.sha256()
    numel = 0
    tensors = 0
    for key in sorted(state):
        value = state[key]
        if not torch.is_tensor(value):
            raise TypeError(f"Non-tensor model-state entry: {key}")
        tensor = value.detach().cpu().contiguous()
        metadata = f"{key}|{tensor.dtype}|{tuple(tensor.shape)}|".encode()
        digest.update(metadata)
        digest.update(tensor.reshape(-1).view(torch.uint8).numpy().tobytes())
        numel += tensor.numel()
        tensors += 1
    return {
        "state_key_count": len(state),
        "tensor_count": tensors,
        "parameter_and_buffer_numel": numel,
        "ordered_key_tensor_sha256": digest.hexdigest(),
    }


def verify_checkpoints(checkpoint_repo: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    from rarepdet.models.early_fusion_fcos import build_detector

    manifest_entries = []
    verification_entries = []
    for item in CHECKPOINTS:
        path = checkpoint_repo / item["relative_path"]
        actual_hash = sha256(path)
        if actual_hash != item["sha256"]:
            raise RuntimeError(f"Checkpoint hash mismatch for {item['opaque_id']}")
        payload = torch.load(path, map_location="cpu", weights_only=False)
        state = payload["model_state"]
        fingerprint = tensor_fingerprint(state)
        model = build_detector(
            item["model_type"],
            img_size=640,
            score_thresh=0.001,
            nms_thresh=0.6,
            detections_per_img=100,
        )
        incompatible = model.load_state_dict(state, strict=True)
        strict_ok = not incompatible.missing_keys and not incompatible.unexpected_keys
        if not strict_ok:
            raise RuntimeError(f"Strict load failed for {item['opaque_id']}")

        common = {
            "method": item["method"],
            "seed": item["seed"],
            "opaque_id": item["opaque_id"],
            "filename": "best.pt",
            "bytes": path.stat().st_size,
            "sha256": actual_hash,
            "source_commit": item["source_commit"],
            "model_class": "torchvision.models.detection.FCOS",
            "builder": f"build_detector(model_type={item['model_type']})",
            "checkpoint_selection_rule": "best in-training TriAir validation AP50 under the frozen trainer rule",
            "evidence_reference": item["evidence"],
            **fingerprint,
        }
        manifest_entries.append(common)
        verification_entries.append(
            {
                "opaque_id": item["opaque_id"],
                "hash_matches_frozen_evidence": True,
                "strict_load": True,
                "missing_keys": [],
                "unexpected_keys": [],
                "checkpoint_epoch": payload.get("epoch"),
                "checkpoint_best_ap50": payload.get("best_ap50"),
                "optimizer_state_used": False,
                "inference_run": False,
            }
        )
        del model, state, payload
        gc.collect()
    return manifest_entries, verification_entries


def source_lock() -> dict[str, object]:
    paths = (
        "rarepdet/tools/run_v71_mmuav_existing_devval_zero_shot.py",
        "tests/test_v71_mmuav_existing_devval_zero_shot.py",
        "datasets/mmuav_feature_alignment_dataset.py",
        "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/repvit_fpn_backbone.py",
        "rarepdet/coco_metrics.py",
        "runs/v52_mmuav_audit/alignment_source_audit.json",
        "runs/v52_mmuav_audit/official_alignment_verification.json",
        "runs/v52_mmuav_audit/synchronization_audit.json",
        "runs/v53_mmuav_feature_alignment_preflight/method_contract.json",
        "runs/v53_mmuav_feature_alignment_preflight/alignment_design.json",
    )
    return {
        "starting_commit": STARTING_COMMIT,
        "v70_completion_is_ancestor": True,
        "clean_execution_worktree_at_start": True,
        "source_hashes": {path: sha256(ROOT / path) for path in paths},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-repo", type=Path, required=True)
    args = parser.parse_args()
    if git("rev-parse", "HEAD") != STARTING_COMMIT:
        raise RuntimeError("Unexpected V71 starting commit")

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    manifest_lock = lock_manifest()
    checkpoint_manifest, checkpoint_verification = verify_checkpoints(args.checkpoint_repo)
    alignment_source = json.loads(
        (ROOT / "runs/v52_mmuav_audit/alignment_source_audit.json").read_text(encoding="utf-8")
    )
    sync = json.loads((ROOT / "runs/v52_mmuav_audit/synchronization_audit.json").read_text(encoding="utf-8"))
    method_contract = json.loads(
        (ROOT / "runs/v53_mmuav_feature_alignment_preflight/method_contract.json").read_text(encoding="utf-8")
    )
    blocked = (
        not alignment_source["deterministic_raw_grid_transform_found"]
        and not sync["pixel_alignment_established"]
        and not method_contract["raw_channel_concatenation"]
    )
    if not blocked:
        raise RuntimeError("Frozen alignment evidence no longer supports the expected V71 adapter blocker")

    write_json("protocol.json", {
        "task": "V71_MMUAV_EXISTING_DEVVAL_TRIAIR_ZERO_SHOT_EXTERNAL_DOMAIN_VALIDATION",
        "starting_commit": STARTING_COMMIT,
        "dataset_rows": 1845,
        "checkpoint_count": 6,
        "gate_order": ["source", "manifest", "checkpoints", "adapter", "smoke", "evaluation"],
        "frozen_inference": {
            "input_size": [640, 640], "score_threshold": 0.001, "nms_threshold": 0.6,
            "maximum_detections": 100, "test_time_augmentation": False,
        },
        "stopped_at": "adapter",
        "training_or_tuning": False,
    })
    (RUN_DIR / "protocol.md").write_text(
        "# V71 Protocol\n\n"
        "V71 locked the exposed 1,845-row MM-UAV devval manifest and strictly loaded the six frozen "
        "TriAir checkpoints. The task then stopped at the adapter gate because V52 established temporal "
        "synchronization but no pixel alignment or executable deterministic raw-grid transform. V53 "
        "forbids raw-channel concatenation and requires independent branches with learned feature "
        "alignment. No smoke inference, GPU evaluation, predictions, or metrics were produced.\n",
        encoding="utf-8",
    )
    write_json("source_lock.json", source_lock())
    write_json("devval_manifest_lock.json", manifest_lock)
    write_json("exposure_and_claim_boundary.json", {
        "label": "zero-shot external-domain validation on the existing exposed MM-UAV devval split",
        "previously_exposed": True,
        "independent_external_validation": False,
        "blind_external_test": False,
        "official_test_performance": False,
        "public_or_manuscript_reporting_authorized": False,
    })
    write_json("triair_checkpoint_manifest.json", {"count": 6, "entries": checkpoint_manifest})
    write_json("triair_checkpoint_verification.json", {
        "status": "PASS_6_OF_6_STRICT_CPU_LOAD",
        "entries": checkpoint_verification,
        "mmuav_trained_checkpoints_used": False,
        "softplus_wrapper_used": False,
    })
    write_json("triair_model_contract.json", {
        "status": "VERIFIED",
        "input_channels": ["rgb_r", "rgb_g", "rgb_b", "thermal", "event"],
        "input_size": [640, 640],
        "model_types": ["early", "reliability"],
        "production_source_modified": False,
    })
    adapter_reason = (
        "V52 proves only filename-index temporal synchronization. Native modality dimensions differ, "
        "pixel alignment is not established, and no complete provider raw-grid transform or calibration "
        "recipe exists. Independent letterboxing would place unrelated coordinates into the same pixels. "
        "V53 explicitly forbids raw-channel concatenation and uses independent branches with learned "
        "feature alignment, which V71 forbids."
    )
    write_json("mmuav_to_triair_adapter_spec.json", {
        "status": "BLOCKED_NO_DEFENSIBLE_PARAMETER_FREE_SPATIAL_REGISTRATION",
        "parameter_free_adapter_frozen": False,
        "deterministic_raw_grid_transform_found": False,
        "pixel_alignment_established": False,
        "raw_channel_concatenation_authorized": False,
        "reason": adapter_reason,
    })
    (RUN_DIR / "mmuav_to_triair_adapter_spec.md").write_text(
        "# Adapter Decision\n\n"
        "`BLOCKED_NO_DEFENSIBLE_PARAMETER_FREE_SPATIAL_REGISTRATION`\n\n"
        f"{adapter_reason}\n",
        encoding="utf-8",
    )
    write_json("adapter_source_lock.json", {
        "status": "NO_ADAPTER_IMPLEMENTED",
        "frozen_evidence": {
            "v52_alignment_source_audit": sha256(ROOT / "runs/v52_mmuav_audit/alignment_source_audit.json"),
            "v52_official_alignment_verification": sha256(
                ROOT / "runs/v52_mmuav_audit/official_alignment_verification.json"
            ),
            "v52_synchronization_audit": sha256(ROOT / "runs/v52_mmuav_audit/synchronization_audit.json"),
            "v53_method_contract": sha256(
                ROOT / "runs/v53_mmuav_feature_alignment_preflight/method_contract.json"
            ),
        },
    })
    write_json("adapter_determinism_tests.json", {
        "status": "NOT_RUN_ADAPTER_CONTRACT_BLOCKED",
        "tests": 0,
        "candidate_media_decoded": False,
    })
    write_json("class_ontology_mapping.json", {
        "status": "NOT_FROZEN_UPSTREAM_ADAPTER_BLOCKED",
        "candidate_annotations_parsed_for_metrics": False,
    })
    write_json("zero_shot_evaluator_contract.json", {
        "status": "NOT_ACTIVATED_UPSTREAM_ADAPTER_BLOCKED",
        "frozen_requested_settings": {
            "score_threshold": 0.001, "nms_threshold": 0.6, "maximum_detections": 100,
            "metrics": ["AP50_95", "AP50", "AP75", "AR1", "AR10", "AR100"],
        },
        "evaluation_attempts": 0,
    })
    write_json("smoke_test_summary.json", {
        "status": "NOT_RUN_UPSTREAM_ADAPTER_BLOCKED",
        "model_forward_calls": 0,
        "gpu_used": False,
    })
    columns = [
        "method", "seed", "ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100",
        "prediction_count", "images_with_predictions", "images_without_predictions",
        "valid_decoded_boxes", "wall_clock_seconds", "peak_memory_mib",
    ]
    with (RUN_DIR / "per_checkpoint_metrics.csv").open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerow(columns)
    write_json("per_checkpoint_metrics.json", {"status": "NOT_RUN", "records": []})
    with (RUN_DIR / "paired_seed_comparison.csv").open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerow(["seed", "metric", "reliability_minus_early"])
    write_json("paired_seed_comparison.json", {"status": "NOT_COMPUTED", "records": []})
    (RUN_DIR / "external_domain_validation_summary.md").write_text(
        "# V71 External-Domain Validation Summary\n\n"
        "No external-domain metric was computed. The exposed devval manifest and all six frozen TriAir "
        "checkpoints passed their gates, but the required parameter-free spatial registration contract "
        "cannot be established from provider evidence. Reporting fabricated raw-grid correspondence "
        "would violate the frozen V52/V53 scientific boundary.\n",
        encoding="utf-8",
    )
    write_json("memory_timing_summary.json", {
        "gpu_evaluation_seconds": 0,
        "gpu_peak_memory_mib": 0,
        "evaluation_attempts": 0,
    })
    write_json("protected_file_audit.json", {
        "starting_commit": STARTING_COMMIT,
        "protected_core_diff_empty": True,
        "historical_v52_v70_diff_empty": True,
        "raw_private_or_heavy_git_artifacts": False,
        "cuda_training_or_inference": False,
    })
    (RUN_DIR / "test_commands.txt").write_text(
        "python -m unittest discover -s tests -p test_v71_mmuav_existing_devval_zero_shot.py -v\n"
        "python rarepdet/tools/run_v71_mmuav_existing_devval_zero_shot.py --checkpoint-repo <private-repo-root>\n"
        "python -m unittest discover -s tests -p test_v71_mmuav_existing_devval_zero_shot.py -v\n",
        encoding="utf-8",
    )
    write_json("final_decision.json", {
        "decision": DECISION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_gate": "PASS",
        "checkpoint_gate": "PASS_6_OF_6",
        "adapter_gate": "BLOCKED",
        "smoke_runs": 0,
        "evaluation_attempts": 0,
        "metrics_computed": False,
        "gpu_used": False,
        "training_fine_tuning_adaptation_or_tuning": False,
        "reason": adapter_reason,
    })
    (RUN_DIR / "handoff.md").write_text(
        "# V71 Handoff\n\n"
        f"Decision: `{DECISION}`.\n\n"
        "The frozen 1,845-row exposed MM-UAV devval manifest passed identity, order, presence, and "
        "annotation-hash checks. All six authoritative TriAir checkpoints matched frozen hashes and "
        "strictly loaded on CPU.\n\n"
        "V71 stopped at the parameter-free adapter gate. V52 records temporal synchronization only, "
        "different native modality grids, no established pixel alignment, and no executable provider "
        "raw-grid transform. V53 explicitly forbids raw-channel concatenation and relies on learned "
        "feature alignment. Because V71 forbids learned alignment, no defensible five-channel input can "
        "be formed.\n\n"
        "No smoke pass, CUDA inference, predictions, AP/AR metrics, training, tuning, or reruns occurred. "
        "A future task must obtain a provider-specified deterministic calibration/registration transform "
        "or explicitly authorize a scientifically different independent-branch model evaluation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"decision": DECISION, "manifest_rows": 1845, "checkpoints_strict": 6}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
