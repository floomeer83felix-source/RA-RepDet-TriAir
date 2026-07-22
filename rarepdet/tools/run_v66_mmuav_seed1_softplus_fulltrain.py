"""Run the frozen V66 seed-1 Softplus full-train confirmation."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import os
import shutil
import statistics
import sys
from pathlib import Path

import torch
from torchvision.models.detection import fcos as fcos_module


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.v63_bbox_activation_detector import V63BBoxActivationDetector
from rarepdet.tools import run_v61_mmuav_bbox_bias_pilot as base
from rarepdet.tools import run_v62_mmuav_clean_bbox_bias_pilot as v62
from rarepdet.tools import run_v63_mmuav_bbox_activation_rescue as v63
from rarepdet.tools import run_v65_mmuav_seed0_softplus_fulltrain as v65
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import configure_seed as configure_seed_original


OUT = ROOT / "runs/v66_mmuav_seed1_softplus_fulltrain_confirmation"
LOCAL = Path(r"D:\MM-UAV_v66_local")
SOURCE_INIT = Path(r"D:\MM-UAV_v64_local\seed1_common_init.pt")
INIT_PATH = LOCAL / "seed1_common_init.pt"
CHECKPOINT_PATH = LOCAL / "v66_seed1_equal_softplus_b1_t20_fulltrain_final_step7187.pt"
RECOVERY_PATH = LOCAL / "recovery" / "v66_seed1_equal_softplus_b1_t20_fulltrain_latest.pt"
START_COMMIT = "72f4c936dfe1b7d1007aba56c9fe503c494e73f9"
AUTHORIZATION_BASE = "33609052b798a89fb8d3a1ab9351f8497e8f95d1"
VARIANT = "v66_seed1_equal_softplus_b1_t20_fulltrain"
INIT_SHA256 = "50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476"
V65_OUT = ROOT / "runs/v65_mmuav_seed0_softplus_fulltrain_feasibility"
V65_HASHES = {
    "final_decision.json": "977c35622147d72c08edc86ffbdd34cf05ab6ec0ab5fb0548acd9087d3d1bf9e",
    "safety_audit.json": "27b8534aaf3746a721d12b05d89e7f3d7573d244b935d01903d5a6355d5a00f2",
    "training_log.csv": "1edc3b773d90ae5cabd4b27e4f32376aea4003c1c8dc23e43133c46a3c357f16",
    "source_lock_v65.json": "47e183cf1a56edd400227b9c448cacbdeed337c9e7d203a514ec91dc0c53dd03",
    "full_devval_metrics.json": "e6e5bde9db36c01ef052ac11339116d73916ee1a04749099ec9e077b1c9604ac",
    "geometry_audits.json": "9b626cefec3c9d9b4c1521d69ba0c7d352fb2e9b55f3a9d233e6fef77be71e7f",
}
METRIC_KEYS = ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")
CONFIG = {
    **v65.CONFIG,
    "seed": 1,
    "name": VARIANT,
    "initialization_sha256": INIT_SHA256,
    "sole_difference_from_v65": "frozen seed-1 initialization state",
}
CONFIG_HASH = hashlib.sha256(json.dumps(CONFIG, sort_keys=True).encode()).hexdigest()


def sha256(path: Path) -> str:
    return v65.sha256(path)


def write_json(path: Path, value: object) -> None:
    v65.write_json(path, value)


def git(*args: str) -> str:
    return v65.git(*args)


def configure_runtime() -> None:
    v65.OUT = OUT
    v65.LOCAL = LOCAL
    v65.INIT_PATH = INIT_PATH
    v65.CHECKPOINT_PATH = CHECKPOINT_PATH
    v65.RECOVERY_PATH = RECOVERY_PATH
    v65.START_COMMIT = START_COMMIT
    v65.AUTHORIZATION_BASE = AUTHORIZATION_BASE
    v65.VARIANT = VARIANT
    v65.CONFIG = CONFIG
    v65.CONFIG_HASH = CONFIG_HASH
    base.INIT_SHA256 = INIT_SHA256
    v65.configure_seed = lambda _seed: configure_seed_original(1)
    v63.ACTIVATION[VARIANT] = v65.ACTIVATION


def build_model() -> V63BBoxActivationDetector:
    return V63BBoxActivationDetector(v65.ACTIVATION)


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
        historical = any(relative.startswith(f"runs/v{version}_") for version in range(40, 66))
        if relative in fixed or relative.startswith("manuscript/") or relative.startswith("submission/") or historical:
            path = ROOT / relative
            if path.is_file():
                selected.append(path)
    return selected


def protected_fingerprint() -> dict[str, object]:
    return v62._aggregate(protected_paths())


def verify_v65() -> dict[str, object]:
    hashes = {name: sha256(V65_OUT / name) for name in V65_HASHES}
    final = json.loads((V65_OUT / "final_decision.json").read_text(encoding="utf-8"))
    safety = json.loads((V65_OUT / "safety_audit.json").read_text(encoding="utf-8"))
    metrics = json.loads((V65_OUT / "full_devval_metrics.json").read_text(encoding="utf-8"))
    geometry = json.loads((V65_OUT / "geometry_audits.json").read_text(encoding="utf-8"))
    expected_metrics = {
        "ap50_95": 0.036304392782128436,
        "ap50": 0.14934166830177412,
        "ap75": 0.0035733839300669244,
        "ar1": 0.05014292520247737,
        "ar10": 0.07536922343973321,
        "ar100": 0.08153882801333968,
    }
    checks = {
        "file_hashes": hashes == V65_HASHES,
        "decision": final["decision"] == "V65_FULLTRAIN_COMPLETE_NONZERO_AP",
        "optimizer_steps": safety["optimizer_steps"] == 7187 and safety["unique_training_rows"] == 7187,
        "backward_calls": safety["probe_backward_calls"] == 40,
        "recovery": safety["verified_recovery_snapshots"] == 19 and safety["recovery_events"] == 0,
        "evaluation": safety["evaluation_attempts"] == 1 and safety["full_devval_rows"] == 1845,
        "metrics": all(metrics[key] == value for key, value in expected_metrics.items()),
        "audits_preserved": all(row["state"] == "GEOMETRY_AND_GRADIENT_PRESERVED" for row in final["trace_classifications"]),
        "final_geometry": geometry[-1]["geometry"]["aggregate_counts"]["valid"] == 272000
        and geometry[-1]["devval_geometry"]["aggregate_counts"]["valid"] == 272000,
        "safety": all((safety["all_finite"], safety["all_recovery_round_trips"],
                       safety["all_audit_isolation_checks"], safety["protected_fingerprint_unchanged"])),
        "no_selection_or_rerun": not any((safety["threshold_selection"], safety["tuning"],
                                           safety["checkpoint_selection"], safety["reruns"])),
    }
    if not all(checks.values()):
        raise RuntimeError(f"V65 evidence mismatch: {checks}")
    return {"checks": checks, "file_sha256": hashes, "metrics": expected_metrics,
            "completion_commit": AUTHORIZATION_BASE}


def source_lock() -> dict[str, object]:
    sources = [
        "rarepdet/tools/run_v66_mmuav_seed1_softplus_fulltrain.py",
        "tests/test_v66_mmuav_seed1_softplus_fulltrain.py",
        "rarepdet/tools/run_v65_mmuav_seed0_softplus_fulltrain.py",
        "tests/test_v65_mmuav_seed0_softplus_fulltrain.py",
        "rarepdet/tools/run_v63_mmuav_bbox_activation_rescue.py",
        "rarepdet/experimental/v63_bbox_activation_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
        "rarepdet/coco_metrics.py",
    ]
    installed = Path(inspect.getsourcefile(fcos_module.FCOSRegressionHead) or "")
    lines, first_line = inspect.getsourcelines(fcos_module.FCOSRegressionHead.forward)
    relu_lines = [first_line + index for index, value in enumerate(lines) if "functional.relu(self.bbox_reg" in value]
    if len(relu_lines) != 1:
        raise RuntimeError(f"Installed FCOS activation source mismatch: {relu_lines}")
    v65_lock = json.loads((V65_OUT / "source_lock_v65.json").read_text(encoding="utf-8"))
    return {
        "starting_commit": START_COMMIT,
        "authorization_base": AUTHORIZATION_BASE,
        "source_hashes": {name: sha256(ROOT / name) for name in sources},
        "installed_fcos_path": str(installed),
        "installed_fcos_sha256": sha256(installed),
        "historical_relu_line": relu_lines[0],
        "softplus_expression": "F.softplus(pre_activation, beta=1.0, threshold=20.0)",
        "softplus_beta": 1.0,
        "softplus_threshold": 20.0,
        "shared_training_inference_head": True,
        "coco_metrics_sha256": sha256(ROOT / "rarepdet/coco_metrics.py"),
        "v65_installed_fcos_sha256": v65_lock["installed_fcos_sha256"],
        "v65_coco_metrics_sha256": v65_lock["coco_metrics_sha256"],
        "v65_runner_sha256": sha256(ROOT / "rarepdet/tools/run_v65_mmuav_seed0_softplus_fulltrain.py"),
        "sole_runtime_difference_from_v65": "seed and frozen initialization state",
    }


def freeze_initialization() -> tuple[dict[str, torch.Tensor], dict[str, object]]:
    if not SOURCE_INIT.is_file() or sha256(SOURCE_INIT) != INIT_SHA256:
        raise RuntimeError("Frozen V64 seed-1 initialization mismatch")
    LOCAL.mkdir(parents=True, exist_ok=True)
    if INIT_PATH.exists():
        if sha256(INIT_PATH) != INIT_SHA256:
            raise RuntimeError("Existing V66 initialization mismatch")
    else:
        shutil.copy2(SOURCE_INIT, INIT_PATH)
    payload = torch.load(INIT_PATH, map_location="cpu", weights_only=False)
    state = payload["state_dict"]
    model = build_model()
    loaded = model.load_state_dict(state, strict=True)
    checks = {
        "source_sha256": sha256(SOURCE_INIT) == INIT_SHA256,
        "v66_serialized_sha256": sha256(INIT_PATH) == INIT_SHA256,
        "payload_seed_one": payload.get("seed") == 1,
        "generation_count_one": payload.get("generation_count") == 1,
        "strict_reload": not loaded.missing_keys and not loaded.unexpected_keys,
        "tensor_count": len(state) == 791,
        "round_trip_bit_identical": all(torch.equal(state[key], model.state_dict()[key]) for key in state),
        "all_finite": all(torch.isfinite(value).all() for value in state.values()),
        "historical_zero_bbox_bias": state[base.BBOX_BIAS_KEY].tolist() == [0.0] * 4,
    }
    if not all(checks.values()):
        raise RuntimeError(f"V66 seed-1 initialization gate failed: {checks}")
    return base.clone_state(state), {
        "source_path_local_not_committed": str(SOURCE_INIT),
        "v66_path_local_not_committed": str(INIT_PATH),
        "sha256": INIT_SHA256,
        "bytes": INIT_PATH.stat().st_size,
        "seed": 1,
        "generation_count": 1,
        "tensor_count": len(state),
        "state_fingerprint": base.tensor_dict_fingerprint(state),
        "trained_checkpoint_used": False,
        "alternative_candidates_generated": 0,
        "checks": checks,
    }


def prepare() -> None:
    configure_runtime()
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError("Unexpected V66 starting commit")
    if OUT.exists():
        existing = {path.name for path in OUT.iterdir()}
        if not existing.issubset({"full_train_order_sha256.txt"}):
            raise RuntimeError(f"V66 output contains non-retry artifacts: {sorted(existing)}")
    if LOCAL.exists():
        existing_local = {path.name for path in LOCAL.iterdir()}
        if not existing_local.issubset({INIT_PATH.name}) or (INIT_PATH.exists() and sha256(INIT_PATH) != INIT_SHA256):
            raise RuntimeError(f"V66 local directory contains non-retry artifacts: {sorted(existing_local)}")
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = verify_v65()
    if sha256(base.TRAIN_MANIFEST) != base.TRAIN_SHA256 or sha256(v65.DEVVAL_MANIFEST) != v65.DEVVAL_SHA256:
        raise RuntimeError("V66 manifest hash mismatch")
    train_dataset = MMUAVFeatureAlignmentDataset(base.TRAIN_MANIFEST, 320, validate_paths=True)
    dev_dataset = MMUAVFeatureAlignmentDataset(v65.DEVVAL_MANIFEST, 320, validate_paths=True)
    if (len(train_dataset), len(dev_dataset)) != (7187, 1845):
        raise RuntimeError("V66 manifest row-count mismatch")
    order = v65.materialize_order(train_dataset)
    subsets = base.frozen_subsets()
    state, initialization = freeze_initialization()
    step0 = v65.step0_contract(state, train_dataset, order["indices"][0])
    devval_gate = v63.actual_devval_gate()
    evaluator_fixture = v65.evaluator_micro_fixture()
    lock = source_lock()
    protocol = {
        "prepared_at": base.now(), "starting_commit": START_COMMIT,
        "authorization_base": AUTHORIZATION_BASE, "v65_evidence": evidence,
        "train_manifest": {"path": str(base.TRAIN_MANIFEST), "rows": len(train_dataset), "sha256": base.TRAIN_SHA256},
        "devval_manifest": {"path": str(v65.DEVVAL_MANIFEST), "rows": len(dev_dataset), "sha256": v65.DEVVAL_SHA256},
        "full_order": order, "subsets": subsets, "initialization": initialization,
        "step0_contract": step0, "actual_devval_gate": devval_gate,
        "evaluator_micro_fixture": evaluator_fixture, "config": CONFIG,
        "configuration_sha256": CONFIG_HASH, "optimizer_step_limit": v65.STEPS,
        "probe_backward_limit": v65.PROBE_BACKWARD_LIMIT,
        "protected_baseline": protected_fingerprint(),
    }
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v66.json", lock)
    write_json(OUT / "v65_evidence_verification.json", evidence)
    write_json(OUT / "seed1_initialization_verification.json", initialization)
    write_json(OUT / "audit_schedule.json", {
        "audit_steps": list(v65.AUDIT_STEPS), "periodic_recovery_steps": list(v65.PERIODIC_RECOVERY_STEPS),
        "snapshot_steps": list(v65.SNAPSHOT_STEPS), "gradient_rows_per_audit": 4,
        "diagnostic_backward_limit": v65.PROBE_BACKWARD_LIMIT,
    })
    write_json(OUT / "training_config.json", CONFIG)
    write_json(OUT / "full_devval_evaluator_contract.json", {
        "identical_to_v65": True, "final_checkpoint_only": True, "evaluation_attempt_limit": 1,
        "score_threshold": 0.001, "nms_threshold": 0.6, "max_detections": [1, 10, 100],
        "iou_thresholds": list(v65.coco_metrics.COCO_IOU_THRESHOLDS),
        "recall_threshold_count": len(v65.coco_metrics.COCO_RECALL_THRESHOLDS),
        "backend": "pycocotools.cocoeval.COCOeval", "source_sha256": lock["coco_metrics_sha256"],
        "micro_fixture": evaluator_fixture,
    })
    write_json(OUT / "recovery_ledger.json", {"variant": VARIANT, "events": [], "recovery_events": 0})
    (OUT / "protocol.md").write_text(
        "# V66 Seed-1 Full-Train Confirmation\n\nThe V65 protocol is repeated once with the exact frozen V64 seed-1 initialization.\n",
        encoding="utf-8",
    )
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v66_mmuav_seed1_softplus_fulltrain.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v66_mmuav_seed1_softplus_fulltrain.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v66_mmuav_seed1_softplus_fulltrain.py --run\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "V66_PREPARED_CPU_ONLY", "seed1_initialization_sha256": INIT_SHA256,
                      "train_rows": len(train_dataset), "devval_rows": len(dev_dataset)}, indent=2))


def two_seed_summary(v66_metrics: dict[str, object]) -> dict[str, object]:
    v65_metrics = json.loads((V65_OUT / "full_devval_metrics.json").read_text(encoding="utf-8"))
    summary = {}
    for key in METRIC_KEYS:
        values = [float(v65_metrics[key]), float(v66_metrics[key])]
        summary[key] = {
            "v65_seed0": values[0], "v66_seed1": values[1],
            "mean": statistics.mean(values), "sample_std": statistics.stdev(values),
            "minimum": min(values), "maximum": max(values),
            "absolute_seed_difference": abs(values[1] - values[0]),
        }
    return {"descriptive_only": True, "seeds": [0, 1], "n": 2,
            "selection_or_rerun_trigger": False, "metrics": summary}


def run() -> None:
    configure_runtime()
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    lock = json.loads((OUT / "source_lock_v66.json").read_text(encoding="utf-8"))
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError("V66 starting commit changed before CUDA")
    if source_lock() != lock:
        raise RuntimeError("V66 source changed after CPU lock")
    if verify_v65() != protocol["v65_evidence"]:
        raise RuntimeError("V65 evidence changed before V66 CUDA")
    if protected_fingerprint() != protocol["protected_baseline"]:
        raise RuntimeError("Protected fingerprint changed before V66 CUDA")
    if sha256(INIT_PATH) != INIT_SHA256:
        raise RuntimeError("V66 seed-1 initialization changed before CUDA")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for V66")
    summary, audits, ledger = v65.train(protocol, torch.device("cuda:0"))
    total_backward = sum(audit["gradient_probe"]["backward_calls"] for audit in audits)
    if total_backward != v65.PROBE_BACKWARD_LIMIT:
        raise RuntimeError(f"V66 diagnostic backward budget mismatch: {total_backward}")
    metrics, prediction_safety = v65.evaluate_final_checkpoint(protocol, torch.device("cuda:0"))
    classifications = [{"step": audit["step"], "state": v65.classify(audit)} for audit in audits]
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
        "optimizer_steps": summary["completed_optimizer_steps"], "optimizer_step_limit": v65.STEPS,
        "unique_training_rows": v65.STEPS, "full_order_sha256": base.ORDER_SHA256,
        "probe_backward_calls": total_backward, "probe_backward_limit": v65.PROBE_BACKWARD_LIMIT,
        "verified_recovery_snapshots": len(snapshots), "expected_recovery_snapshots": len(v65.SNAPSHOT_STEPS),
        "recovery_events": 0, "all_recovery_round_trips": all(all(row["round_trip_checks"].values()) for row in snapshots),
        "all_audit_isolation_checks": all(all(audit["isolation"].values()) for audit in audits),
        "all_finite": summary["all_finite"] and prediction_safety["all_predictions_finite"],
        "v65_evidence_unchanged": verify_v65() == protocol["v65_evidence"],
        "initialization_unchanged": sha256(INIT_PATH) == INIT_SHA256,
        "protected_fingerprint_unchanged": protected_fingerprint() == protocol["protected_baseline"],
        "full_devval_rows": metrics["images"], "evaluation_attempts": 1, "final_checkpoint_only": True,
        "ap_ar_computed": True, "threshold_selection": False, "tuning": False,
        "checkpoint_selection": False, "extra_variants": 0, "extra_seeds": 0, "reruns": 0,
    }
    required = (
        safety["optimizer_steps"] == v65.STEPS, safety["probe_backward_calls"] == v65.PROBE_BACKWARD_LIMIT,
        safety["verified_recovery_snapshots"] == len(v65.SNAPSHOT_STEPS), safety["all_recovery_round_trips"],
        safety["all_audit_isolation_checks"], safety["all_finite"], safety["v65_evidence_unchanged"],
        safety["initialization_unchanged"], safety["protected_fingerprint_unchanged"], safety["full_devval_rows"] == 1845,
    )
    if not all(required):
        raise RuntimeError(f"V66 post-run safety audit failed: {safety}")
    seed_summary = two_seed_summary(metrics)
    decision = "V66_SEED1_FULLTRAIN_COMPLETE_NONZERO_AP" if metrics["ap50_95"] > 0.0 else "V66_SEED1_FULLTRAIN_COMPLETE_ZERO_AP"
    write_json(OUT / "geometry_audits.json", geometry_output)
    write_json(OUT / "gradient_audits.json", gradient_output)
    write_json(OUT / "activation_derivative_summary.json", derivative_output)
    write_json(OUT / "final_checkpoint_metadata.json", summary["checkpoint"])
    write_json(OUT / "two_seed_equal_fusion_summary.json", seed_summary)
    write_json(OUT / "memory_timing_summary.json", {"training": summary, "evaluation": {
        "elapsed_seconds": metrics["inference_seconds"], "fps": metrics["fps"],
        "peak_allocated_bytes": metrics["peak_allocated_bytes"], "peak_reserved_bytes": metrics["peak_reserved_bytes"],
    }})
    write_json(OUT / "safety_audit.json", safety)
    write_json(OUT / "final_decision.json", {"decision": decision, "trace_classifications": classifications,
               "full_devval_metrics": {key: metrics[key] for key in METRIC_KEYS},
               "two_seed_summary": seed_summary, "checkpoint": summary["checkpoint"], "safety": safety})
    (OUT / "handoff.md").write_text(
        f"# V66 Handoff\n\nDecision: `{decision}`. This is a descriptive two-seed equal-fusion Softplus baseline; no superiority claim is authorized.\n",
        encoding="utf-8",
    )
    print(json.dumps({"decision": decision, "metrics": {key: metrics[key] for key in METRIC_KEYS},
                      "two_seed_summary": seed_summary, "safety": safety}, indent=2))


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
        raise SystemExit(f"V66_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY: {exc}")
