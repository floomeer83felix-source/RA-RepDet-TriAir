"""Run the frozen V65 seed-0 Softplus full-train feasibility experiment."""

from __future__ import annotations

import argparse
import csv
from contextlib import redirect_stdout
import hashlib
import inspect
import io
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import torch
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
from torchvision.models.detection import fcos as fcos_module


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet import coco_metrics
from rarepdet.experimental.v63_bbox_activation_detector import V63BBoxActivationDetector
from rarepdet.tools import run_v61_mmuav_bbox_bias_pilot as base
from rarepdet.tools import run_v62_mmuav_clean_bbox_bias_pilot as v62
from rarepdet.tools import run_v63_mmuav_bbox_activation_rescue as v63
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import (
    configure_seed,
    gradient_norm,
    inputs_to_device,
    target_to_device,
)


OUT = ROOT / "runs/v65_mmuav_seed0_softplus_fulltrain_feasibility"
LOCAL = Path(r"D:\MM-UAV_v65_local")
INIT_PATH = LOCAL / "seed0_common_init.pt"
CHECKPOINT_PATH = LOCAL / "v65_seed0_equal_softplus_b1_t20_fulltrain_final_step7187.pt"
RECOVERY_PATH = LOCAL / "recovery" / "v65_seed0_equal_softplus_b1_t20_fulltrain_latest.pt"
START_COMMIT = "89cf93a3f0ac053a2a1f3ac217dbbc746a76ba72"
AUTHORIZATION_BASE = "402eabb23896f7908b6a3eccd4d394d3ce41d487"
VARIANT = "v65_seed0_equal_softplus_b1_t20_fulltrain"
ACTIVATION = "softplus_b1_t20"
DEVVAL_MANIFEST = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"
DEVVAL_SHA256 = "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54"
AUDIT_STEPS = (0, 15, 50, 200, 500, 1000, 2000, 4000, 6000, 7187)
PERIODIC_RECOVERY_STEPS = tuple(range(500, 7001, 500))
SNAPSHOT_STEPS = tuple(sorted(set(AUDIT_STEPS) | set(PERIODIC_RECOVERY_STEPS)))
STEPS = 7187
PROBE_BACKWARD_LIMIT = 40
V63_HASHES = {
    "final_decision.json": "2985ac382639dca8da6b3303b9e0e3fdb74bc6b54485de7c140f3f8dbda818bd",
    "safety_audit.json": "90f2a837e480d8947616ea60401805843487cf47541e50837522e766f7871e18",
    "per_variant_training_log.csv": "4b6e0ba9f89fe0314dff58a3a1b6ef9eefe021974643a384fe7e00a00c593dc9",
    "source_lock_v63.json": "489db6a090c8b38c4aa36c72bf238d116743ded91916ff006785ab382762776a",
}
V64_HASHES = {
    "final_decision.json": "8ecaf1422795e7d739753e58c5f04f2b10b49bfc70a316a7ad391ebea5c3abfc",
    "safety_audit.json": "148271855dd700934e56f3becb4557928abcb2f408dc64cc840e066edb8d01b3",
    "per_variant_training_log.csv": "f693f7ade0b358e5544e6f66d4f2d344aceeb06e927390fb8c95092cf5d72e21",
    "source_lock_v64.json": "da6084d6509cf5be2b9f84045b7c3055f2e1da8ed6f90ddd792f3a7baade5292",
}
CONFIG = {
    **base.common_config(),
    "name": VARIANT,
    "steps": STEPS,
    "bbox_activation": "softplus(beta=1.0, threshold=20.0)",
    "audit_steps": list(AUDIT_STEPS),
    "periodic_recovery_steps": list(PERIODIC_RECOVERY_STEPS),
    "full_devval_final_checkpoint_only": True,
    "score_threshold": 0.001,
    "nms_threshold": 0.6,
    "max_detections": 100,
}
CONFIG_HASH = hashlib.sha256(json.dumps(CONFIG, sort_keys=True).encode()).hexdigest()
LOG_FIELDS = v63.LOG_FIELDS


def sha256(path: Path) -> str:
    return base.sha256(path)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return base.git(*args)


def configure_helpers() -> None:
    v63.ACTIVATION[VARIANT] = ACTIVATION


def build_model() -> V63BBoxActivationDetector:
    return V63BBoxActivationDetector(ACTIVATION)


def protected_paths() -> list[Path]:
    fixed = {
        "rarepdet/train_early_fusion.py",
        "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py",
        "datasets/triair_dataset.py",
        "main.tex",
        "main_sivp_snjnl.tex",
    }
    selected = []
    for relative in git("ls-files").splitlines():
        historical = any(relative.startswith(f"runs/v{version}_") for version in range(40, 65))
        if relative in fixed or relative.startswith("manuscript/") or relative.startswith("submission/") or historical:
            path = ROOT / relative
            if path.is_file():
                selected.append(path)
    return selected


def protected_fingerprint() -> dict[str, object]:
    return v62._aggregate(protected_paths())


def verify_prior_evidence() -> dict[str, object]:
    records = {}
    for version, expected, decision in (
        (63, V63_HASHES, "V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200"),
        (64, V64_HASHES, "V64_SEED1_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS"),
    ):
        directory = ROOT / (
            "runs/v63_mmuav_paired_bbox_activation_rescue"
            if version == 63 else "runs/v64_mmuav_seed1_bbox_activation_confirmation"
        )
        hashes = {name: sha256(directory / name) for name in expected}
        final = json.loads((directory / "final_decision.json").read_text(encoding="utf-8"))
        safety = json.loads((directory / "safety_audit.json").read_text(encoding="utf-8"))
        checks = {
            "file_hashes": hashes == expected,
            "decision": final["decision"] == decision,
            "all_finite": safety["all_finite"],
            "protected_unchanged": safety["protected_fingerprint_unchanged"],
            "no_full_devval": safety["full_devval_rows"] == 0,
            "no_ap_ar": not safety["ap_ar_computed"],
        }
        if not all(checks.values()):
            raise RuntimeError(f"V{version} evidence mismatch: {checks}")
        records[f"v{version}"] = {"checks": checks, "file_sha256": hashes, "decision": decision}
    return records


def source_lock() -> dict[str, object]:
    sources = [
        "rarepdet/tools/run_v65_mmuav_seed0_softplus_fulltrain.py",
        "tests/test_v65_mmuav_seed0_softplus_fulltrain.py",
        "rarepdet/tools/run_v63_mmuav_bbox_activation_rescue.py",
        "rarepdet/tools/run_v62_mmuav_clean_bbox_bias_pilot.py",
        "rarepdet/tools/run_v61_mmuav_bbox_bias_pilot.py",
        "rarepdet/experimental/v63_bbox_activation_detector.py",
        "rarepdet/experimental/v57_fusion_superset_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
        "rarepdet/coco_metrics.py",
    ]
    installed = Path(inspect.getsourcefile(fcos_module.FCOSRegressionHead) or "")
    lines, first_line = inspect.getsourcelines(fcos_module.FCOSRegressionHead.forward)
    relu_lines = [first_line + index for index, value in enumerate(lines) if "functional.relu(self.bbox_reg" in value]
    if len(relu_lines) != 1:
        raise RuntimeError(f"Installed FCOS activation source mismatch: {relu_lines}")
    return {
        "starting_commit": START_COMMIT,
        "authorization_base": AUTHORIZATION_BASE,
        "source_hashes": {name: sha256(ROOT / name) for name in sources},
        "installed_fcos_path": str(installed),
        "installed_fcos_sha256": sha256(installed),
        "historical_relu_line": relu_lines[0],
        "historical_relu_expression": "nn.functional.relu(self.bbox_reg(bbox_feature))",
        "softplus_expression": "F.softplus(pre_activation, beta=1.0, threshold=20.0)",
        "softplus_beta": 1.0,
        "softplus_threshold": 20.0,
        "shared_training_inference_head": True,
        "coco_metrics_sha256": sha256(ROOT / "rarepdet/coco_metrics.py"),
    }


def materialize_order(dataset: MMUAVFeatureAlignmentDataset) -> dict[str, object]:
    if sha256(base.ORDER_PATH) != base.ORDER_SHA256:
        raise RuntimeError("Historical V57 order hash mismatch")
    order = json.loads(base.ORDER_INDICES_PATH.read_text(encoding="utf-8"))
    row_ids = base.ORDER_PATH.read_text(encoding="utf-8").splitlines()
    if len(order) != STEPS or len(set(order)) != STEPS or len(row_ids) != STEPS or len(set(row_ids)) != STEPS:
        raise RuntimeError("Historical V57 full-order structure mismatch")
    if any(dataset.rows[index]["original_row_id"] != row_id for index, row_id in zip(order, row_ids)):
        raise RuntimeError("Historical V57 full-order identity mismatch")
    payload = ("\n".join(row_ids) + "\n").encode()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != base.ORDER_SHA256:
        raise RuntimeError("Materialized full-order hash mismatch")
    (OUT / "full_train_order_sha256.txt").write_text(digest + "\n", encoding="utf-8")
    return {"rows": len(order), "unique_rows": len(set(order)), "indices": order, "sha256": digest}


def freeze_initialization() -> tuple[dict[str, torch.Tensor], dict[str, object]]:
    if not base.COMMON_INIT.is_file() or sha256(base.COMMON_INIT) != base.INIT_SHA256:
        raise RuntimeError("Historical seed-0 initialization artifact mismatch")
    LOCAL.mkdir(parents=True, exist_ok=True)
    if INIT_PATH.exists():
        if sha256(INIT_PATH) != base.INIT_SHA256:
            raise RuntimeError("Existing V65 initialization does not match the frozen seed-0 artifact")
    else:
        shutil.copy2(base.COMMON_INIT, INIT_PATH)
    if sha256(INIT_PATH) != base.INIT_SHA256:
        raise RuntimeError("V65 initialization serialization hash mismatch")
    payload = torch.load(INIT_PATH, map_location="cpu", weights_only=False)
    state = payload["state_dict"]
    model = build_model()
    loaded = model.load_state_dict(state, strict=True)
    model_state = model.state_dict()
    checks = {
        "historical_artifact_sha256": sha256(base.COMMON_INIT) == base.INIT_SHA256,
        "v65_serialized_sha256": sha256(INIT_PATH) == base.INIT_SHA256,
        "strict_reload": not loaded.missing_keys and not loaded.unexpected_keys,
        "tensor_count": len(state) == 791,
        "round_trip_bit_identical": all(torch.equal(state[key], model_state[key]) for key in state),
        "all_finite": all(torch.isfinite(value).all() for value in state.values()),
        "historical_zero_bbox_bias": state[base.BBOX_BIAS_KEY].tolist() == [0.0] * 4,
    }
    if not all(checks.values()):
        raise RuntimeError(f"V65 initialization gate failed: {checks}")
    record = {
        "source_path_local_not_committed": str(base.COMMON_INIT),
        "v65_path_local_not_committed": str(INIT_PATH),
        "sha256": base.INIT_SHA256,
        "bytes": INIT_PATH.stat().st_size,
        "seed": 0,
        "tensor_count": len(state),
        "state_fingerprint": base.tensor_dict_fingerprint(state),
        "trained_checkpoint_used": False,
        "checks": checks,
    }
    return base.clone_state(state), record


def load_initialization() -> dict[str, torch.Tensor]:
    if not INIT_PATH.is_file() or sha256(INIT_PATH) != base.INIT_SHA256:
        raise RuntimeError("Frozen V65 seed-0 initialization mismatch")
    payload = torch.load(INIT_PATH, map_location="cpu", weights_only=False)
    state = payload["state_dict"]
    if len(state) != 791 or not all(torch.isfinite(value).all() for value in state.values()):
        raise RuntimeError("Frozen V65 initialization tensor contract mismatch")
    return state


def step0_contract(state: dict[str, torch.Tensor], dataset: MMUAVFeatureAlignmentDataset, first_index: int) -> dict[str, object]:
    configure_helpers()
    states = {v63.VARIANTS[0]: base.clone_state(state), v63.VARIANTS[1]: base.clone_state(state)}
    identity = v63.step0_identity(states, dataset, first_index)
    model = build_model()
    model.load_state_dict(state, strict=True)
    model.eval()
    sample = dataset[first_index]
    with torch.no_grad():
        model._feature_forward(*inputs_to_device(sample, torch.device("cpu")))
    feature_checks = {
        key: bool(torch.isfinite(model.last_feature_outputs[key]).all())
        for key in ("rgb_reference", "aligned_ir", "aligned_event", "fused", "fusion_weights", "ir_theta", "event_theta")
    }
    if not all(identity["checks"].values()) or not all(feature_checks.values()):
        raise RuntimeError("V65 step-0 identity contract failed")
    return {
        "v63_seed0_identity": identity,
        "feature_outputs_all_finite": feature_checks,
        "state_fingerprint": base.tensor_dict_fingerprint(state),
        "sole_difference_from_historical_v57": "parameter-free bbox-distance Softplus",
    }


def full_coco_metrics(predictions, targets) -> dict[str, object]:
    dataset, detections = coco_metrics._build_coco_inputs(
        predictions, targets, foreground_label=1, score_thresh=0.0, max_detections=100
    )
    quiet = io.StringIO()
    with redirect_stdout(quiet):
        ground_truth = COCO()
        ground_truth.dataset = dataset
        ground_truth.createIndex()
        detection_api = ground_truth.loadRes(detections) if detections else coco_metrics._empty_detection_api(dataset)
        evaluator = COCOeval(ground_truth, detection_api, iouType="bbox")
        evaluator.params.imgIds = [image["id"] for image in dataset["images"]]
        evaluator.params.catIds = [1]
        evaluator.params.iouThrs = np.asarray(coco_metrics.COCO_IOU_THRESHOLDS, dtype=np.float64)
        evaluator.params.recThrs = np.asarray(coco_metrics.COCO_RECALL_THRESHOLDS, dtype=np.float64)
        evaluator.params.maxDets = [1, 10, 100]
        evaluator.evaluate()
        evaluator.accumulate()
    precision = evaluator.eval["precision"][:, :, 0, 0, 2]
    ap_by_iou = {
        f"{threshold:.2f}": coco_metrics._mean_valid(precision[index])
        for index, threshold in enumerate(coco_metrics.COCO_IOU_THRESHOLDS)
    }
    recall = evaluator.eval["recall"][:, 0, 0, :]
    return {
        "ap50_95": float(np.mean(list(ap_by_iou.values()))),
        "ap50": ap_by_iou["0.50"],
        "ap75": ap_by_iou["0.75"],
        "ap_by_iou": ap_by_iou,
        "ar1": coco_metrics._mean_valid(recall[:, 0]),
        "ar10": coco_metrics._mean_valid(recall[:, 1]),
        "ar100": coco_metrics._mean_valid(recall[:, 2]),
        "images": len(dataset["images"]),
        "gt_boxes": len(dataset["annotations"]),
        "detections": len(detections),
        "iou_thresholds": list(coco_metrics.COCO_IOU_THRESHOLDS),
        "recall_thresholds": len(coco_metrics.COCO_RECALL_THRESHOLDS),
        "max_detections": [1, 10, 100],
        "backend": "pycocotools.cocoeval.COCOeval",
    }


def evaluator_micro_fixture() -> dict[str, object]:
    prediction = {"boxes": torch.tensor([[1.0, 2.0, 11.0, 12.0]]), "scores": torch.tensor([0.9]), "labels": torch.tensor([1])}
    target = {"boxes": torch.tensor([[1.0, 2.0, 11.0, 12.0]]), "labels": torch.tensor([1])}
    first = full_coco_metrics([prediction], [target])
    second = full_coco_metrics([prediction], [target])
    keys = ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")
    checks = {
        "deterministic": first == second,
        "schema_complete": all(key in first for key in keys),
        "perfect_metrics": all(abs(first[key] - 1.0) <= 1e-12 for key in keys),
        "finite": all(math.isfinite(first[key]) for key in keys),
    }
    if not all(checks.values()):
        raise RuntimeError(f"V65 evaluator micro-fixture failed: {checks}")
    return {"synthetic_only": True, "metrics": first, "checks": checks}


def prepare() -> None:
    configure_helpers()
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError("Unexpected V65 starting commit")
    if OUT.exists():
        existing = {path.name for path in OUT.iterdir()}
        if not existing.issubset({"full_train_order_sha256.txt"}):
            raise RuntimeError(f"V65 output directory already contains non-retry artifacts: {sorted(existing)}")
    if LOCAL.exists():
        existing_local = {path.name for path in LOCAL.iterdir()}
        if not existing_local.issubset({INIT_PATH.name}) or (INIT_PATH.exists() and sha256(INIT_PATH) != base.INIT_SHA256):
            raise RuntimeError(f"V65 local directory already contains non-retry artifacts: {sorted(existing_local)}")
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = verify_prior_evidence()
    if sha256(base.TRAIN_MANIFEST) != base.TRAIN_SHA256 or sha256(DEVVAL_MANIFEST) != DEVVAL_SHA256:
        raise RuntimeError("V65 manifest hash mismatch")
    train_dataset = MMUAVFeatureAlignmentDataset(base.TRAIN_MANIFEST, 320, validate_paths=True)
    dev_dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=True)
    if (len(train_dataset), len(dev_dataset)) != (7187, 1845):
        raise RuntimeError("V65 manifest row-count mismatch")
    order = materialize_order(train_dataset)
    subsets = base.frozen_subsets()
    state, initialization = freeze_initialization()
    step0 = step0_contract(state, train_dataset, order["indices"][0])
    devval_gate = v63.actual_devval_gate()
    evaluator_fixture = evaluator_micro_fixture()
    lock = source_lock()
    protocol = {
        "prepared_at": base.now(),
        "starting_commit": START_COMMIT,
        "authorization_base": AUTHORIZATION_BASE,
        "prior_evidence": evidence,
        "train_manifest": {"path": str(base.TRAIN_MANIFEST), "rows": len(train_dataset), "sha256": base.TRAIN_SHA256},
        "devval_manifest": {"path": str(DEVVAL_MANIFEST), "rows": len(dev_dataset), "sha256": DEVVAL_SHA256},
        "full_order": order,
        "subsets": subsets,
        "initialization": initialization,
        "step0_contract": step0,
        "actual_devval_gate": devval_gate,
        "evaluator_micro_fixture": evaluator_fixture,
        "config": CONFIG,
        "configuration_sha256": CONFIG_HASH,
        "optimizer_step_limit": STEPS,
        "probe_backward_limit": PROBE_BACKWARD_LIMIT,
        "protected_baseline": protected_fingerprint(),
    }
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v65.json", lock)
    write_json(OUT / "v63_v64_evidence_verification.json", evidence)
    write_json(OUT / "initialization_verification.json", initialization)
    write_json(OUT / "audit_schedule.json", {
        "audit_steps": list(AUDIT_STEPS),
        "periodic_recovery_steps": list(PERIODIC_RECOVERY_STEPS),
        "snapshot_steps": list(SNAPSHOT_STEPS),
        "gradient_rows_per_audit": 4,
        "diagnostic_backward_limit": PROBE_BACKWARD_LIMIT,
    })
    write_json(OUT / "training_config.json", CONFIG)
    write_json(OUT / "full_devval_evaluator_contract.json", {
        "final_checkpoint_only": True,
        "evaluation_attempt_limit": 1,
        "score_threshold": 0.001,
        "nms_threshold": 0.6,
        "max_detections": [1, 10, 100],
        "iou_thresholds": list(coco_metrics.COCO_IOU_THRESHOLDS),
        "recall_threshold_count": len(coco_metrics.COCO_RECALL_THRESHOLDS),
        "backend": "pycocotools.cocoeval.COCOeval",
        "source_sha256": lock["coco_metrics_sha256"],
        "micro_fixture": evaluator_fixture,
    })
    write_json(OUT / "recovery_ledger.json", {"variant": VARIANT, "events": [], "recovery_events": 0})
    (OUT / "protocol.md").write_text(
        "# V65 Full-Train Feasibility\n\nOne frozen seed-0 equal-fusion Softplus model, one 7,187-row pass, and one final-checkpoint-only full-devval evaluation.\n",
        encoding="utf-8",
    )
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v65_mmuav_seed0_softplus_fulltrain.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v65_mmuav_seed0_softplus_fulltrain.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v65_mmuav_seed0_softplus_fulltrain.py --run\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "V65_PREPARED_CPU_ONLY", "initialization_sha256": base.INIT_SHA256,
                      "train_rows": len(train_dataset), "devval_rows": len(dev_dataset)}, indent=2))


def log_contract(handle, path: Path) -> dict[str, object]:
    handle.flush()
    try:
        os.fsync(handle.fileno())
    except OSError:
        pass
    with path.open("r", encoding="utf-8") as reader:
        row_count = max(sum(1 for _ in reader) - 1, 0)
    return {"row_count": row_count, "sha256": sha256(path), "bytes": path.stat().st_size}


def atomic_snapshot(model, optimizer, completed_step: int, log_info: dict[str, object], ledger: list[dict[str, object]]) -> dict[str, object]:
    RECOVERY_PATH.parent.mkdir(parents=True, exist_ok=True)
    rng = base.rng_snapshot()
    payload = {
        "model_state": base.clone_state(model.state_dict()),
        "optimizer_state": optimizer.state_dict(),
        "rng_state": rng,
        "completed_optimizer_steps": completed_step,
        "next_sample_order_position": completed_step,
        "variant": VARIANT,
        "source_commit": START_COMMIT,
        "configuration_sha256": CONFIG_HASH,
        "initialization_sha256": base.INIT_SHA256,
        "training_log": log_info,
        "ledger_before_snapshot": list(ledger),
    }
    temporary = RECOVERY_PATH.with_suffix(".pt.tmp")
    with temporary.open("wb") as handle:
        torch.save(payload, handle)
        handle.flush()
        try:
            os.fsync(handle.fileno())
        except OSError:
            pass
    os.replace(temporary, RECOVERY_PATH)
    loaded = torch.load(RECOVERY_PATH, map_location="cpu", weights_only=False)
    checks = {
        "model": base.tensor_dict_fingerprint(loaded["model_state"]) == base.tensor_dict_fingerprint(payload["model_state"]),
        "optimizer": v63.optimizer_state_hash(loaded["optimizer_state"]) == v63.optimizer_state_hash(payload["optimizer_state"]),
        "rng": base.rng_digest(loaded["rng_state"]) == base.rng_digest(rng),
        "step": loaded["completed_optimizer_steps"] == completed_step,
        "next_order": loaded["next_sample_order_position"] == completed_step,
        "variant": loaded["variant"] == VARIANT,
        "log": loaded["training_log"] == log_info,
        "ledger": loaded["ledger_before_snapshot"] == ledger,
    }
    if not all(checks.values()):
        raise RuntimeError(f"V65 recovery round-trip failed: {checks}")
    return {
        "event": "snapshot_verified",
        "step": completed_step,
        "path_local_not_committed": str(RECOVERY_PATH),
        "sha256": sha256(RECOVERY_PATH),
        "bytes": RECOVERY_PATH.stat().st_size,
        "log_row_count": log_info["row_count"],
        "log_sha256": log_info["sha256"],
        "round_trip_checks": checks,
        "recovery_used": False,
    }


def audit_state(model, optimizer, step, train_dataset, dev_dataset, subsets, device) -> dict[str, object]:
    parameter_before = base.parameter_hash(model)
    buffer_before = base.buffer_hash(model)
    optimizer_before = base.optimizer_hash(optimizer)
    rng_before = base.rng_snapshot()
    rng_hash = base.rng_digest(rng_before)
    was_training = model.training
    model.eval()
    with torch.no_grad():
        train_records = [v63.geometry_row(model, train_dataset[index], device, ACTIVATION) for index in subsets["train_indices"]]
        geometry = v63.aggregate_geometry(train_records)
        dev_geometry = None
        if step == STEPS:
            dev_records = [v63.geometry_row(model, dev_dataset[index], device, ACTIVATION) for index in subsets["devval_indices"]]
            dev_geometry = v63.aggregate_geometry(dev_records)
    if was_training:
        model.train()
    state = base.clone_state(model.state_dict())
    probe = v63.gradient_probe(state, subsets["gradient_indices"], train_dataset, device, VARIANT)
    base.restore_rng(rng_before)
    isolation = {
        "training_parameters": base.parameter_hash(model) == parameter_before,
        "training_buffers": base.buffer_hash(model) == buffer_before,
        "optimizer": base.optimizer_hash(optimizer) == optimizer_before,
        "rng": base.rng_digest(base.rng_snapshot()) == rng_hash,
    }
    if not all(isolation.values()):
        raise RuntimeError(f"V65 audit mutated persistent state at step {step}: {isolation}")
    bbox = model.detector.head.regression_head.bbox_reg
    return {
        "step": step,
        "geometry": geometry,
        "devval_geometry": dev_geometry,
        "gradient_probe": probe,
        "bbox_output_parameters": {
            "weight": base.tensor_stats(bbox.weight, False),
            "weight_norm": float(bbox.weight.detach().norm().cpu()),
            "bias": base.tensor_stats(bbox.bias, False),
            "bias_values": bbox.bias.detach().cpu().tolist(),
            "bias_norm": float(bbox.bias.detach().norm().cpu()),
        },
        "isolation": isolation,
        "rng_hash_before": rng_hash,
        "rng_hash_after": base.rng_digest(base.rng_snapshot()),
    }


def classify(audit: dict[str, object]) -> str:
    return v63.classify(audit)


def train(protocol: dict[str, object], device: torch.device) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    order = protocol["full_order"]["indices"]
    if len(order) != STEPS or len(set(order)) != STEPS:
        raise RuntimeError("V65 run order invalid")
    train_dataset = MMUAVFeatureAlignmentDataset(base.TRAIN_MANIFEST, 320, validate_paths=False)
    dev_dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    configure_seed(0)
    model = build_model().to(device)
    initial = load_initialization()
    model.load_state_dict(initial, strict=True)
    loaded = {key: value.detach().cpu() for key, value in model.state_dict().items()}
    if base.tensor_dict_fingerprint(loaded) != protocol["initialization"]["state_fingerprint"]:
        raise RuntimeError("V65 CUDA model initialization mismatch")
    scorer_initial = base.clone_state(model.feature_scaffold.reliability_scorer.state_dict())
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    capture: dict[str, object] = {}
    v63.install_loss_capture(model, capture)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    log_path = OUT / "training_log.csv"
    if log_path.exists() or CHECKPOINT_PATH.exists():
        raise RuntimeError("Refusing to overwrite V65 training artifacts")
    audits: list[dict[str, object]] = []
    ledger: list[dict[str, object]] = []
    step_times = []
    completed = 0
    started_run = time.perf_counter()
    previous_end = started_run
    with log_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS)
        writer.writeheader()
        snapshot = atomic_snapshot(model, optimizer, 0, log_contract(handle, log_path), ledger)
        ledger.append(snapshot)
        write_json(OUT / "recovery_ledger.json", {"variant": VARIANT, "events": ledger, "recovery_events": 0})
        audits.append(audit_state(model, optimizer, 0, train_dataset, dev_dataset, protocol["subsets"], device))
        ledger.append({"event": "audit_complete", "step": 0, "state": classify(audits[-1])})
        for expected_step, index in enumerate(order, 1):
            if completed >= STEPS:
                raise RuntimeError("V65 optimizer-step ceiling exceeded")
            started = time.perf_counter()
            sample = train_dataset[index]
            data_done = time.perf_counter()
            inputs = inputs_to_device(sample, device)
            targets = target_to_device(sample, device)
            optimizer.zero_grad(set_to_none=True)
            capture.clear()
            forward_started = time.perf_counter()
            losses = model(*inputs, targets)
            total = sum(losses.values())
            torch.cuda.synchronize()
            forward_done = time.perf_counter()
            if not losses or not all(torch.isfinite(value).all() for value in losses.values()):
                raise RuntimeError(f"Non-finite V65 loss at step {expected_step}")
            total.backward()
            torch.cuda.synchronize()
            backward_done = time.perf_counter()
            global_norm, global_finite = gradient_norm(model.parameters())
            bbox = model.detector.head.regression_head.bbox_reg
            bbox_summary = v63.module_grad_summary(bbox)
            tower_summary = v63.module_grad_summary(model.detector.head.regression_head.conv)
            head_summary = v63.module_grad_summary(model.detector.head)
            weight_grad = 0.0 if bbox.weight.grad is None else float(bbox.weight.grad.double().norm().cpu())
            bias_grad = 0.0 if bbox.bias.grad is None else float(bbox.bias.grad.double().norm().cpu())
            scorer_has_gradient = any(parameter.grad is not None for parameter in model.feature_scaffold.reliability_scorer.parameters())
            if scorer_has_gradient or not global_finite or not all((bbox_summary["finite"], tower_summary["finite"], head_summary["finite"])):
                raise RuntimeError(f"V65 gradient/scorer contract failure at step {expected_step}")
            optimizer.step()
            completed += 1
            if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                raise RuntimeError(f"Non-finite V65 parameter at step {expected_step}")
            torch.cuda.synchronize()
            optimizer_done = time.perf_counter()
            values = {key: float(value.detach().cpu()) for key, value in losses.items()}
            bias_values = bbox.bias.detach().cpu().tolist()
            weight = bbox.weight.detach()
            row = {
                "variant": VARIANT, "step": completed, "original_row_id": sample["original_row_id"],
                "target_box_count": int(sample["target_rgb"]["boxes"].shape[0]),
                "valid_target_count": int(((sample["target_rgb"]["boxes"][:, 2:] - sample["target_rgb"]["boxes"][:, :2]) > 0).all(dim=1).sum()),
                "matched_anchor_count": int(capture["matched_anchor_count"]), "loss_total": float(total.detach().cpu()),
                "loss_classifier": values["classification"], "loss_box_reg": values["bbox_regression"],
                "loss_centerness": values["bbox_ctrness"], "learning_rate": 1e-4,
                "global_gradient_norm": global_norm, "bbox_weight_gradient_norm": weight_grad,
                "bbox_bias_gradient_norm": bias_grad, "bbox_gradient_nonzero_fraction": bbox_summary["nonzero_fraction"],
                "bbox_bias_0": bias_values[0], "bbox_bias_1": bias_values[1], "bbox_bias_2": bias_values[2], "bbox_bias_3": bias_values[3],
                "finite": True, "cuda_allocated_bytes": torch.cuda.memory_allocated(),
                "cuda_reserved_bytes": torch.cuda.memory_reserved(), "data_time_sec": data_done - previous_end,
                "forward_time_sec": forward_done - forward_started, "backward_time_sec": backward_done - forward_done,
                "optimizer_time_sec": optimizer_done - backward_done, "step_time_sec": optimizer_done - started,
                "regression_tower_gradient_norm": tower_summary["norm"], "detector_head_gradient_norm": head_summary["norm"],
                "bbox_weight_norm_after": float(weight.norm().cpu()), "bbox_weight_min_after": float(weight.min().cpu()),
                "bbox_weight_max_after": float(weight.max().cpu()), "bbox_bias_min_after": min(bias_values),
                "bbox_bias_max_after": max(bias_values),
            }
            writer.writerow(row)
            step_times.append(row["step_time_sec"])
            if completed in SNAPSHOT_STEPS:
                snapshot = atomic_snapshot(model, optimizer, completed, log_contract(handle, log_path), ledger)
                ledger.append(snapshot)
                write_json(OUT / "recovery_ledger.json", {"variant": VARIANT, "events": ledger, "recovery_events": 0})
            if completed in AUDIT_STEPS:
                audit = audit_state(model, optimizer, completed, train_dataset, dev_dataset, protocol["subsets"], device)
                audits.append(audit)
                state = classify(audit)
                ledger.append({"event": "audit_complete", "step": completed, "state": state})
                write_json(OUT / "recovery_ledger.json", {"variant": VARIANT, "events": ledger, "recovery_events": 0})
                print(f"V65_AUDIT_COMPLETE step={completed} state={state} valid={audit['geometry']['aggregate_counts']['valid']}", flush=True)
                if len(audits) >= 2 and classify(audits[-1]) == classify(audits[-2]) == "EARLY_BBOX_COLLAPSE":
                    raise RuntimeError("V65_FULLTRAIN_BBOX_COLLAPSE")
            previous_end = optimizer_done
    if completed != STEPS or [audit["step"] for audit in audits] != list(AUDIT_STEPS):
        raise RuntimeError("V65 training/audit schedule incomplete")
    scorer_final = model.feature_scaffold.reliability_scorer.state_dict()
    if not all(torch.equal(scorer_final[key].detach().cpu(), value) for key, value in scorer_initial.items()):
        raise RuntimeError("V65 dormant reliability scorer changed")
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "model_state": model.state_dict(), "variant": VARIANT, "completed_optimizer_steps": completed,
        "common_init_sha256": base.INIT_SHA256, "full_order_sha256": base.ORDER_SHA256,
        "configuration_sha256": CONFIG_HASH,
    }, CHECKPOINT_PATH)
    checkpoint = {
        "path_local_not_committed": str(CHECKPOINT_PATH), "sha256": sha256(CHECKPOINT_PATH),
        "bytes": CHECKPOINT_PATH.stat().st_size, "completed_optimizer_steps": completed,
        "selection_metric": None, "common_init_sha256": base.INIT_SHA256,
        "final_state_fingerprint": base.tensor_dict_fingerprint({key: value.detach().cpu() for key, value in model.state_dict().items()}),
    }
    summary = {
        "variant": VARIANT, "completed_optimizer_steps": completed, "all_finite": True,
        "elapsed_seconds": time.perf_counter() - started_run, "step_time_mean_sec": float(np.mean(step_times)),
        "step_time_min_sec": min(step_times), "step_time_max_sec": max(step_times),
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(), "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "dormant_scorer_unchanged": True, "checkpoint": checkpoint,
    }
    del optimizer, model
    torch.cuda.empty_cache()
    return summary, audits, ledger


def evaluate_final_checkpoint(protocol: dict[str, object], device: torch.device) -> tuple[dict[str, object], dict[str, object]]:
    marker = OUT / "full_devval_evaluation_started.json"
    metrics_path = OUT / "full_devval_metrics.json"
    if marker.exists() or metrics_path.exists():
        raise RuntimeError("V65 full-devval evaluation was already attempted")
    checkpoint_sha = sha256(CHECKPOINT_PATH)
    write_json(marker, {"evaluation_attempt": 1, "rows": 1845, "checkpoint_sha256": checkpoint_sha,
                        "final_checkpoint_only": True})
    payload = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
    if payload["completed_optimizer_steps"] != STEPS or payload["configuration_sha256"] != CONFIG_HASH:
        raise RuntimeError("V65 final checkpoint contract mismatch")
    model = build_model().to(device)
    model.load_state_dict(payload["model_state"], strict=True)
    model.detector.score_thresh = 0.001
    model.detector.nms_thresh = 0.6
    model.detector.detections_per_img = 100
    model.eval()
    dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    predictions, targets = [], []
    zero_prediction_images = 0
    nonfinite_predictions = 0
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    with torch.no_grad():
        for index in range(len(dataset)):
            sample = dataset[index]
            output = model(*inputs_to_device(sample, device))[0]
            finite = all(torch.isfinite(value).all() for value in output.values())
            if not finite:
                nonfinite_predictions += 1
                raise RuntimeError(f"Non-finite V65 prediction: {sample['original_row_id']}")
            if output["boxes"].shape[0] == 0:
                zero_prediction_images += 1
            predictions.append({key: value.detach().cpu() for key, value in output.items()})
            target = sample["target_rgb"]
            targets.append({"boxes": target["boxes"].cpu(), "labels": target["labels"].cpu()})
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    metrics = full_coco_metrics(predictions, targets)
    metric_keys = ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")
    if metrics["images"] != 1845 or not all(math.isfinite(metrics[key]) for key in metric_keys):
        raise RuntimeError("V65 full-devval metric contract failed")
    metrics.update({
        "evaluation_attempt": 1, "final_checkpoint_only": True, "checkpoint_sha256": checkpoint_sha,
        "inference_seconds": elapsed, "fps": len(dataset) / elapsed,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "settings": {"score_threshold": 0.001, "nms_threshold": 0.6, "max_detections": 100},
    })
    safety = {
        "evaluated_images": len(dataset), "ground_truth_boxes": metrics["gt_boxes"],
        "prediction_count": metrics["detections"], "zero_prediction_images": zero_prediction_images,
        "non_finite_prediction_images": nonfinite_predictions, "all_predictions_finite": nonfinite_predictions == 0,
    }
    write_json(metrics_path, metrics)
    write_json(OUT / "prediction_safety_summary.json", safety)
    del model, predictions, targets
    torch.cuda.empty_cache()
    return metrics, safety


def run() -> None:
    configure_helpers()
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    lock = json.loads((OUT / "source_lock_v65.json").read_text(encoding="utf-8"))
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError("V65 starting commit changed before CUDA")
    if source_lock() != lock:
        raise RuntimeError("V65 source changed after CPU lock")
    if verify_prior_evidence() != protocol["prior_evidence"]:
        raise RuntimeError("V63/V64 evidence changed before CUDA")
    if protected_fingerprint() != protocol["protected_baseline"]:
        raise RuntimeError("Protected fingerprint changed before CUDA")
    if sha256(INIT_PATH) != base.INIT_SHA256:
        raise RuntimeError("V65 initialization changed before CUDA")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for V65")
    device = torch.device("cuda:0")
    summary, audits, ledger = train(protocol, device)
    total_backward = sum(audit["gradient_probe"]["backward_calls"] for audit in audits)
    if total_backward != PROBE_BACKWARD_LIMIT:
        raise RuntimeError(f"V65 diagnostic backward budget mismatch: {total_backward}")
    metrics, prediction_safety = evaluate_final_checkpoint(protocol, device)
    classifications = [{"step": audit["step"], "state": classify(audit)} for audit in audits]
    geometry_output = [{"step": audit["step"], "geometry": audit["geometry"],
                        "devval_geometry": audit["devval_geometry"],
                        "bbox_output_parameters": audit["bbox_output_parameters"]} for audit in audits]
    gradient_output = [{"step": audit["step"], "gradient_probe": audit["gradient_probe"],
                        "isolation": audit["isolation"]} for audit in audits]
    derivative_output = [{"step": audit["step"], "levels": [{
        "level": level["level"], "all_mean": level["derivative_all_mean"],
        "all_exact_zero_fraction": level["derivative_all_exact_zero_fraction_mean"],
        "matched_mean": level["derivative_matched_mean"],
        "matched_exact_zero_fraction": level["derivative_matched_exact_zero_fraction_mean"],
    } for level in audit["geometry"]["levels"]]} for audit in audits]
    snapshots = [event for event in ledger if event["event"] == "snapshot_verified"]
    safety = {
        "optimizer_steps": summary["completed_optimizer_steps"], "optimizer_step_limit": STEPS,
        "unique_training_rows": STEPS, "full_order_sha256": base.ORDER_SHA256,
        "probe_backward_calls": total_backward, "probe_backward_limit": PROBE_BACKWARD_LIMIT,
        "verified_recovery_snapshots": len(snapshots), "expected_recovery_snapshots": len(SNAPSHOT_STEPS),
        "recovery_events": 0, "all_recovery_round_trips": all(all(row["round_trip_checks"].values()) for row in snapshots),
        "all_audit_isolation_checks": all(all(audit["isolation"].values()) for audit in audits),
        "all_finite": summary["all_finite"] and prediction_safety["all_predictions_finite"],
        "prior_evidence_unchanged": verify_prior_evidence() == protocol["prior_evidence"],
        "initialization_unchanged": sha256(INIT_PATH) == base.INIT_SHA256,
        "protected_fingerprint_unchanged": protected_fingerprint() == protocol["protected_baseline"],
        "full_devval_rows": metrics["images"], "evaluation_attempts": 1, "final_checkpoint_only": True,
        "ap_ar_computed": True, "threshold_selection": False, "tuning": False,
        "checkpoint_selection": False, "extra_variants": 0, "extra_seeds": 0, "reruns": 0,
    }
    required = (
        safety["optimizer_steps"] == STEPS,
        safety["probe_backward_calls"] == PROBE_BACKWARD_LIMIT,
        safety["verified_recovery_snapshots"] == len(SNAPSHOT_STEPS),
        safety["all_recovery_round_trips"], safety["all_audit_isolation_checks"], safety["all_finite"],
        safety["prior_evidence_unchanged"], safety["initialization_unchanged"],
        safety["protected_fingerprint_unchanged"], safety["full_devval_rows"] == 1845,
    )
    if not all(required):
        raise RuntimeError(f"V65 post-run safety audit failed: {safety}")
    decision = "V65_FULLTRAIN_COMPLETE_NONZERO_AP" if metrics["ap50_95"] > 0.0 else "V65_FULLTRAIN_COMPLETE_ZERO_AP"
    write_json(OUT / "geometry_audits.json", geometry_output)
    write_json(OUT / "gradient_audits.json", gradient_output)
    write_json(OUT / "activation_derivative_summary.json", derivative_output)
    write_json(OUT / "final_checkpoint_metadata.json", summary["checkpoint"])
    write_json(OUT / "memory_timing_summary.json", {"training": summary, "evaluation": {
        "elapsed_seconds": metrics["inference_seconds"], "fps": metrics["fps"],
        "peak_allocated_bytes": metrics["peak_allocated_bytes"], "peak_reserved_bytes": metrics["peak_reserved_bytes"],
    }})
    write_json(OUT / "safety_audit.json", safety)
    write_json(OUT / "final_decision.json", {"decision": decision, "trace_classifications": classifications,
               "full_devval_metrics": {key: metrics[key] for key in ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")},
               "checkpoint": summary["checkpoint"], "safety": safety})
    (OUT / "handoff.md").write_text(
        f"# V65 Handoff\n\nDecision: `{decision}`. One seed-0 equal-fusion Softplus run and one final-checkpoint-only devval evaluation; no comparative claim is authorized.\n",
        encoding="utf-8",
    )
    print(json.dumps({"decision": decision, "metrics": {key: metrics[key] for key in
                      ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")}, "safety": safety}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only", action="store_true")
    group.add_argument("--run", action="store_true")
    args = parser.parse_args()
    prepare() if args.prepare_only else run()


if __name__ == "__main__":
    try:
        main()
    except torch.OutOfMemoryError as exc:
        raise SystemExit(f"V65_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY: {exc}")
