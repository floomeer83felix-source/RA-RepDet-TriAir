"""Run the frozen V67 matched two-seed reliability-fusion benchmark."""

from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import math
import os
import shutil
import statistics
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torchvision.models.detection import fcos as fcos_module


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.v63_bbox_activation_detector import V63BBoxActivationDetector
from rarepdet.experimental.v67_reliability_softplus_detector import V67ReliabilitySoftplusDetector
from rarepdet.tools import run_v61_mmuav_bbox_bias_pilot as base
from rarepdet.tools import run_v62_mmuav_clean_bbox_bias_pilot as v62
from rarepdet.tools import run_v63_mmuav_bbox_activation_rescue as v63
from rarepdet.tools import run_v65_mmuav_seed0_softplus_fulltrain as v65
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import (
    configure_seed,
    gradient_norm,
    inputs_to_device,
    target_to_device,
)


OUT = ROOT / "runs/v67_mmuav_two_seed_reliability_softplus_benchmark"
LOCAL = Path(r"D:\MM-UAV_v67_local")
START_COMMIT = "2d79d722b93ef4206527e2bef531bafa370c4b95"
AUTHORIZATION_BASE = "70a54d92b8deb8cb9a0f748230731cddad641d9f"
SEEDS = (0, 1)
VARIANTS = {
    0: "v67_seed0_reliability_softplus_b1_t20_fulltrain",
    1: "v67_seed1_reliability_softplus_b1_t20_fulltrain",
}
INIT_SOURCES = {
    0: Path(r"D:\MM-UAV_v57_local\common_seed0_superset_init.pt"),
    1: Path(r"D:\MM-UAV_v64_local\seed1_common_init.pt"),
}
INIT_HASHES = {
    0: "846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9",
    1: "50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476",
}
V65_OUT = ROOT / "runs/v65_mmuav_seed0_softplus_fulltrain_feasibility"
V66_OUT = ROOT / "runs/v66_mmuav_seed1_softplus_fulltrain_confirmation"
EVIDENCE_HASHES = {
    "v65": {
        "final_decision.json": "977c35622147d72c08edc86ffbdd34cf05ab6ec0ab5fb0548acd9087d3d1bf9e",
        "safety_audit.json": "27b8534aaf3746a721d12b05d89e7f3d7573d244b935d01903d5a6355d5a00f2",
        "full_devval_metrics.json": "e6e5bde9db36c01ef052ac11339116d73916ee1a04749099ec9e077b1c9604ac",
    },
    "v66": {
        "final_decision.json": "08bca25ba87de913a8f2088de73b3df8443a177aa24ecb1dee017486e3cb4709",
        "safety_audit.json": "441a0e4d641f1fc8adda5ee453dc95553943cac240fcb48444a5327cd2e57687",
        "full_devval_metrics.json": "2a8510e2cdce7e65441fff5f5344d1de984e02ffd1ca5fc57f6bc4962511eb89",
    },
}
METRIC_KEYS = ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")
LOG_FIELDS = v65.LOG_FIELDS + (
    "fusion_rgb", "fusion_ir", "fusion_event", "fusion_entropy",
    "fusion_weight_sum", "fusion_dominant_modality", "fusion_dominant_fraction",
    "scorer_logit_rgb", "scorer_logit_ir", "scorer_logit_event",
    "fusion_departed_exact_uniform", "scorer_gradient_norm", "scorer_parameter_norm",
)
COMMON_CONFIG = {
    **v65.CONFIG,
    "fusion_behavior": "active_shared_image_conditioned_reliability",
    "run_order": [VARIANTS[seed] for seed in SEEDS],
    "steps_per_seed": v65.STEPS,
    "total_step_limit": v65.STEPS * 2,
    "probe_backward_limit": v65.PROBE_BACKWARD_LIMIT * 2,
    "modality_dropout": None,
    "sole_difference_from_v65_v66": "V57 reliability scorer output active instead of equal bypass",
}
CONFIG_HASH = hashlib.sha256(json.dumps(COMMON_CONFIG, sort_keys=True).encode()).hexdigest()


def sha256(path: Path) -> str:
    return v65.sha256(path)


def write_json(path: Path, value: object) -> None:
    v65.write_json(path, value)


def git(*args: str) -> str:
    return v65.git(*args)


def init_path(seed: int) -> Path:
    return LOCAL / f"seed{seed}_common_init.pt"


def checkpoint_path(seed: int) -> Path:
    return LOCAL / f"{VARIANTS[seed]}_final_step7187.pt"


def recovery_path(seed: int) -> Path:
    return LOCAL / "recovery" / f"{VARIANTS[seed]}_latest.pt"


def configure_helpers(seed: int) -> None:
    variant = VARIANTS[seed]
    v63.ACTIVATION[variant] = v65.ACTIVATION
    v63.build_model = lambda _variant: V67ReliabilitySoftplusDetector()
    v65.OUT = OUT
    v65.LOCAL = LOCAL
    v65.INIT_PATH = init_path(seed)
    v65.CHECKPOINT_PATH = checkpoint_path(seed)
    v65.RECOVERY_PATH = recovery_path(seed)
    v65.START_COMMIT = START_COMMIT
    v65.AUTHORIZATION_BASE = AUTHORIZATION_BASE
    v65.VARIANT = variant
    v65.CONFIG_HASH = CONFIG_HASH
    v65.build_model = lambda: V67ReliabilitySoftplusDetector()
    base.INIT_SHA256 = INIT_HASHES[seed]


def protected_paths() -> list[Path]:
    fixed = {
        "rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py",
        "main.tex", "main_sivp_snjnl.tex",
    }
    selected = []
    for relative in git("ls-files").splitlines():
        historical = any(relative.startswith(f"runs/v{version}_") for version in range(40, 67))
        if relative in fixed or relative.startswith("manuscript/") or relative.startswith("submission/") or historical:
            path = ROOT / relative
            if path.is_file():
                selected.append(path)
    return selected


def protected_fingerprint() -> dict[str, object]:
    return v62._aggregate(protected_paths())


def verify_prior_evidence() -> dict[str, object]:
    expected_decisions = {
        "v65": "V65_FULLTRAIN_COMPLETE_NONZERO_AP",
        "v66": "V66_SEED1_FULLTRAIN_COMPLETE_NONZERO_AP",
    }
    directories = {"v65": V65_OUT, "v66": V66_OUT}
    records = {}
    for key in ("v65", "v66"):
        directory = directories[key]
        hashes = {name: sha256(directory / name) for name in EVIDENCE_HASHES[key]}
        final = json.loads((directory / "final_decision.json").read_text(encoding="utf-8"))
        safety = json.loads((directory / "safety_audit.json").read_text(encoding="utf-8"))
        metrics = json.loads((directory / "full_devval_metrics.json").read_text(encoding="utf-8"))
        checks = {
            "hashes": hashes == EVIDENCE_HASHES[key],
            "decision": final["decision"] == expected_decisions[key],
            "steps": safety["optimizer_steps"] == 7187 and safety["unique_training_rows"] == 7187,
            "probes": safety["probe_backward_calls"] == 40,
            "snapshots": safety["verified_recovery_snapshots"] == 19 and safety["recovery_events"] == 0,
            "evaluation": safety["evaluation_attempts"] == 1 and safety["full_devval_rows"] == 1845,
            "audits": all(row["state"] == "GEOMETRY_AND_GRADIENT_PRESERVED" for row in final["trace_classifications"]),
            "finite": safety["all_finite"],
            "no_selection": not any((safety["threshold_selection"], safety["tuning"],
                                      safety["checkpoint_selection"], safety["reruns"])),
        }
        if not all(checks.values()):
            raise RuntimeError(f"{key.upper()} evidence mismatch: {checks}")
        records[key] = {"checks": checks, "file_sha256": hashes,
                        "metrics": {metric: metrics[metric] for metric in METRIC_KEYS}}
    return records


def source_lock() -> dict[str, object]:
    sources = [
        "rarepdet/tools/run_v67_mmuav_two_seed_reliability_softplus.py",
        "rarepdet/experimental/v67_reliability_softplus_detector.py",
        "tests/test_v67_mmuav_two_seed_reliability_softplus.py",
        "rarepdet/tools/run_v65_mmuav_seed0_softplus_fulltrain.py",
        "rarepdet/experimental/v63_bbox_activation_detector.py",
        "rarepdet/experimental/v57_fusion_superset_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py", "rarepdet/coco_metrics.py",
    ]
    installed = Path(inspect.getsourcefile(fcos_module.FCOSRegressionHead) or "")
    lines, first = inspect.getsourcelines(fcos_module.FCOSRegressionHead.forward)
    relu_lines = [first + index for index, line in enumerate(lines) if "functional.relu(self.bbox_reg" in line]
    if len(relu_lines) != 1:
        raise RuntimeError(f"FCOS source mismatch: {relu_lines}")
    return {
        "starting_commit": START_COMMIT, "authorization_base": AUTHORIZATION_BASE,
        "source_hashes": {name: sha256(ROOT / name) for name in sources},
        "installed_fcos_path": str(installed), "installed_fcos_sha256": sha256(installed),
        "historical_relu_line": relu_lines[0],
        "softplus_expression": "F.softplus(pre_activation, beta=1.0, threshold=20.0)",
        "coco_metrics_sha256": sha256(ROOT / "rarepdet/coco_metrics.py"),
        "v57_superset_sha256": sha256(ROOT / "rarepdet/experimental/v57_fusion_superset_detector.py"),
        "sole_behavior_switch": "alignment_on_reliability_superset versus alignment_on_equal_superset",
    }


def freeze_initializations() -> tuple[dict[int, dict[str, torch.Tensor]], dict[str, object]]:
    LOCAL.mkdir(parents=True, exist_ok=True)
    states, records = {}, {}
    for seed in SEEDS:
        source, destination, expected = INIT_SOURCES[seed], init_path(seed), INIT_HASHES[seed]
        if not source.is_file() or sha256(source) != expected:
            raise RuntimeError(f"Seed-{seed} initialization source mismatch")
        if destination.exists():
            if sha256(destination) != expected:
                raise RuntimeError(f"Existing V67 seed-{seed} initialization mismatch")
        else:
            shutil.copy2(source, destination)
        payload = torch.load(destination, map_location="cpu", weights_only=False)
        state = payload["state_dict"]
        equal, reliability = V63BBoxActivationDetector("softplus_b1_t20"), V67ReliabilitySoftplusDetector()
        equal_result = equal.load_state_dict(state, strict=True)
        reliability_result = reliability.load_state_dict(state, strict=True)
        checks = {
            "sha256": sha256(destination) == expected,
            "strict_equal": not equal_result.missing_keys and not equal_result.unexpected_keys,
            "strict_reliability": not reliability_result.missing_keys and not reliability_result.unexpected_keys,
            "state_keys_identical": list(equal.state_dict()) == list(reliability.state_dict()),
            "state_tensors_identical": all(torch.equal(equal.state_dict()[key], reliability.state_dict()[key]) for key in equal.state_dict()),
            "tensor_count": len(state) == 791,
            "finite": all(torch.isfinite(value).all() for value in state.values()),
            "final_scorer_zero": torch.equal(state["feature_scaffold.reliability_scorer.4.weight"],
                                               torch.zeros_like(state["feature_scaffold.reliability_scorer.4.weight"]))
            and torch.equal(state["feature_scaffold.reliability_scorer.4.bias"],
                            torch.zeros_like(state["feature_scaffold.reliability_scorer.4.bias"])),
        }
        if not all(checks.values()):
            raise RuntimeError(f"Seed-{seed} initialization checks failed: {checks}")
        states[seed] = base.clone_state(state)
        records[str(seed)] = {"source_path_local_not_committed": str(source),
                              "v67_path_local_not_committed": str(destination),
                              "sha256": expected, "bytes": destination.stat().st_size,
                              "state_fingerprint": base.tensor_dict_fingerprint(state),
                              "trained_checkpoint_used": False, "checks": checks}
    return states, records


def _capture_detector_outputs(model, inputs):
    captured = {}
    modules = {
        "bbox_pre_activation": model.detector.head.regression_head.bbox_reg,
        "classification_logits": model.detector.head.classification_head.cls_logits,
        "centerness_logits": model.detector.head.regression_head.bbox_ctrness,
    }
    hooks = [module.register_forward_hook(lambda _m, _i, output, key=key: captured.setdefault(key, []).append(output.detach().clone()))
             for key, module in modules.items()]
    try:
        output = model(*inputs)[0]
    finally:
        for hook in hooks:
            hook.remove()
    return captured, {key: value.detach().clone() for key, value in output.items()}


def step0_identity_and_gradient(states, dataset, first_index: int) -> dict[str, object]:
    sample = dataset[first_index]
    inputs = inputs_to_device(sample, torch.device("cpu"))
    target = target_to_device(sample, torch.device("cpu"))
    records = {}
    for seed in SEEDS:
        equal, reliability = V63BBoxActivationDetector("softplus_b1_t20"), V67ReliabilitySoftplusDetector()
        equal.load_state_dict(states[seed], strict=True); reliability.load_state_dict(states[seed], strict=True)
        equal.eval(); reliability.eval()
        with torch.no_grad():
            equal_captured, equal_prediction = _capture_detector_outputs(equal, inputs)
            reliability_captured, reliability_prediction = _capture_detector_outputs(reliability, inputs)
        feature_keys = ("rgb_reference", "aligned_ir", "aligned_event", "fused", "ir_theta", "event_theta")
        weights = reliability.last_feature_outputs["fusion_weights"]
        uniform = torch.full_like(weights, 1.0 / 3.0)
        checks = {
            "exact_uniform_weights": torch.equal(weights, uniform),
            "features_identical": all(torch.equal(equal.last_feature_outputs[key], reliability.last_feature_outputs[key]) for key in feature_keys),
            "captured_output_keys_identical": equal_captured.keys() == reliability_captured.keys(),
            "captured_output_counts_identical": all(
                len(equal_captured[key]) == len(reliability_captured[key]) for key in equal_captured
            ),
            "captured_outputs_identical": all(
                torch.equal(left, right)
                for key in equal_captured
                for left, right in zip(equal_captured[key], reliability_captured[key])
            ),
            "decoded_prediction_keys_identical": equal_prediction.keys() == reliability_prediction.keys(),
            "decoded_predictions_identical": all(
                torch.equal(equal_prediction[key], reliability_prediction[key]) for key in equal_prediction
            ),
        }
        configure_seed(seed); equal_train = V63BBoxActivationDetector("softplus_b1_t20")
        equal_train.load_state_dict(states[seed], strict=True); equal_train.train()
        equal_losses = equal_train(*inputs, target)
        configure_seed(seed); reliability_train = V67ReliabilitySoftplusDetector()
        reliability_train.load_state_dict(states[seed], strict=True); reliability_train.train()
        reliability_losses = reliability_train(*inputs, target)
        checks["losses_identical"] = all(torch.equal(equal_losses[key], reliability_losses[key]) for key in equal_losses)
        sum(reliability_losses.values()).backward()
        scorer = reliability_train.feature_scaffold.reliability_scorer
        gradients = [parameter.grad for parameter in scorer.parameters()]
        checks["scorer_gradients_present"] = all(gradient is not None for gradient in gradients)
        checks["scorer_gradients_finite"] = all(torch.isfinite(gradient).all() for gradient in gradients if gradient is not None)
        checks["scorer_gradient_nonzero"] = any(bool((gradient != 0).any()) for gradient in gradients if gradient is not None)
        if not all(checks.values()):
            raise RuntimeError(f"V67 seed-{seed} step-0/scorer gate failed: {checks}")
        records[str(seed)] = {"checks": checks, "weights": weights.tolist(),
                              "scorer_gradient_norm": float(torch.sqrt(sum((gradient.double() ** 2).sum() for gradient in gradients)).cpu())}
    return records


def fusion_summary(weights: torch.Tensor, logits: torch.Tensor) -> dict[str, object]:
    weights = weights.float().cpu(); logits = logits.float().cpu()
    entropy = -(weights.clamp_min(1e-12) * weights.clamp_min(1e-12).log()).sum(dim=1)
    maximum, modality = weights.max(dim=1); names = ("rgb", "ir", "event")
    return {
        "samples": int(weights.shape[0]),
        "per_modality": {names[index]: {"mean": float(weights[:, index].mean()),
            "std": float(weights[:, index].std(unbiased=False)), "min": float(weights[:, index].min()),
            "max": float(weights[:, index].max())} for index in range(3)},
        "weight_sum_max_abs_error": float((weights.sum(dim=1) - 1).abs().max()),
        "entropy_mean": float(entropy.mean()), "entropy_min": float(entropy.min()), "entropy_max": float(entropy.max()),
        "dominance_fraction_mean": float(maximum.mean()),
        "dominant_modality_counts": {name: int((modality == index).sum()) for index, name in enumerate(names)},
        "logits": {"minimum": float(logits.min()), "maximum": float(logits.max()),
                   "mean": float(logits.mean()), "std": float(logits.std(unbiased=False))},
        "departed_from_exact_uniform": not torch.equal(weights, torch.full_like(weights, 1.0 / 3.0)),
        "finite": bool(torch.isfinite(weights).all() and torch.isfinite(logits).all()),
    }


def collect_fusion(model, dataset, indices, device) -> dict[str, object]:
    was_training = model.training; model.eval(); weights, logits = [], []
    with torch.no_grad():
        for index in indices:
            sample = dataset[index]
            model._feature_forward(*inputs_to_device(sample, device))
            features = model.last_feature_outputs
            weights.append(features["fusion_weights"].detach().cpu())
            logits.append(torch.cat([model.feature_scaffold.reliability_scorer(features[key])
                                     for key in ("rgb_reference", "aligned_ir", "aligned_event")], dim=1).detach().cpu())
    if was_training: model.train()
    result = fusion_summary(torch.cat(weights), torch.cat(logits))
    if not result["finite"] or result["weight_sum_max_abs_error"] > 1e-6:
        raise RuntimeError("V67 fusion audit failed")
    return result


def scorer_norms(model) -> tuple[float, float, bool]:
    parameters = list(model.feature_scaffold.reliability_scorer.parameters())
    parameter_norm = float(torch.sqrt(sum((parameter.detach().double() ** 2).sum() for parameter in parameters)).cpu())
    gradients = [parameter.grad for parameter in parameters if parameter.grad is not None]
    finite = bool(gradients) and all(torch.isfinite(gradient).all() for gradient in gradients)
    gradient_norm = float(torch.sqrt(sum((gradient.detach().double() ** 2).sum() for gradient in gradients)).cpu()) if gradients else 0.0
    return parameter_norm, gradient_norm, finite


def prepare() -> None:
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError("Unexpected V67 starting commit")
    if OUT.exists() or LOCAL.exists():
        raise RuntimeError("V67 output/local directory already exists; refusing overwrite")
    OUT.mkdir(parents=True); evidence = verify_prior_evidence()
    if sha256(base.TRAIN_MANIFEST) != base.TRAIN_SHA256 or sha256(v65.DEVVAL_MANIFEST) != v65.DEVVAL_SHA256:
        raise RuntimeError("V67 manifest mismatch")
    train_dataset = MMUAVFeatureAlignmentDataset(base.TRAIN_MANIFEST, 320, validate_paths=True)
    dev_dataset = MMUAVFeatureAlignmentDataset(v65.DEVVAL_MANIFEST, 320, validate_paths=True)
    if (len(train_dataset), len(dev_dataset)) != (7187, 1845):
        raise RuntimeError("V67 row-count mismatch")
    configure_helpers(0); order = v65.materialize_order(train_dataset); subsets = base.frozen_subsets()
    states, initialization = freeze_initializations()
    identity = step0_identity_and_gradient(states, train_dataset, order["indices"][0])
    evaluator_fixture = v65.evaluator_micro_fixture(); devval_gate = v63.actual_devval_gate(); lock = source_lock()
    protocol = {
        "prepared_at": base.now(), "starting_commit": START_COMMIT, "authorization_base": AUTHORIZATION_BASE,
        "prior_evidence": evidence, "train_rows": len(train_dataset), "devval_rows": len(dev_dataset),
        "train_sha256": base.TRAIN_SHA256, "devval_sha256": v65.DEVVAL_SHA256,
        "full_order": order, "subsets": subsets, "initializations": initialization,
        "step0_identity_and_scorer_gradient_gate": identity, "actual_devval_gate": devval_gate,
        "evaluator_micro_fixture": evaluator_fixture, "config": COMMON_CONFIG,
        "configuration_sha256": CONFIG_HASH, "run_order": [VARIANTS[seed] for seed in SEEDS],
        "total_optimizer_step_limit": v65.STEPS * 2, "total_probe_backward_limit": v65.PROBE_BACKWARD_LIMIT * 2,
        "protected_baseline": protected_fingerprint(),
    }
    write_json(OUT / "protocol.json", protocol); write_json(OUT / "source_lock_v67.json", lock)
    write_json(OUT / "prior_evidence_verification.json", evidence)
    write_json(OUT / "initialization_verification.json", initialization)
    write_json(OUT / "step0_state_scorer_verification.json", identity)
    write_json(OUT / "audit_schedule.json", {"per_seed": list(v65.AUDIT_STEPS),
        "snapshot_steps_per_seed": list(v65.SNAPSHOT_STEPS), "total_backward_limit": 80})
    write_json(OUT / "per_seed_config.json", {str(seed): {**COMMON_CONFIG, "seed": seed,
        "variant": VARIANTS[seed], "initialization_sha256": INIT_HASHES[seed]} for seed in SEEDS})
    write_json(OUT / "evaluator_contract.json", {"identical_to_v65_v66": True, "final_checkpoint_only": True,
        "evaluation_attempts_per_seed": 1, "score_threshold": 0.001, "nms_threshold": 0.6,
        "max_detections": [1, 10, 100], "source_sha256": lock["coco_metrics_sha256"],
        "micro_fixture": evaluator_fixture})
    write_json(OUT / "recovery_ledger.json", {"seeds": {str(seed): [] for seed in SEEDS}, "recovery_events": 0})
    (OUT / "protocol.md").write_text("# V67 Matched Reliability Benchmark\n\nTwo frozen seeds, active V57 reliability scorer, exact V65/V66 Softplus protocol.\n", encoding="utf-8")
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v67_mmuav_two_seed_reliability_softplus.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v67_mmuav_two_seed_reliability_softplus.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v67_mmuav_two_seed_reliability_softplus.py --run\n", encoding="utf-8")
    print(json.dumps({"status": "V67_PREPARED_CPU_ONLY", "seeds": list(SEEDS),
                      "initialization_sha256": INIT_HASHES}, indent=2))


def train_seed(seed, initial, order, train_dataset, dev_dataset, subsets, device, all_ledgers):
    configure_helpers(seed); variant = VARIANTS[seed]; configure_seed(seed)
    model = V67ReliabilitySoftplusDetector().to(device); model.load_state_dict(initial, strict=True)
    if base.tensor_dict_fingerprint({key: value.detach().cpu() for key, value in model.state_dict().items()}) != base.tensor_dict_fingerprint(initial):
        raise RuntimeError(f"V67 seed-{seed} initial state mismatch")
    model.train(); optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    capture = {}; v63.install_loss_capture(model, capture)
    log_path = OUT / f"seed{seed}_training_log.csv"
    if log_path.exists() or checkpoint_path(seed).exists():
        raise RuntimeError(f"Refusing overwrite for V67 seed {seed}")
    audits, ledger, step_times, completed = [], all_ledgers[str(seed)], [], 0
    first_departure = None; scorer_gradient_seen = False; started_run = time.perf_counter(); previous_end = started_run
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    with log_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS); writer.writeheader()
        snapshot = v65.atomic_snapshot(model, optimizer, 0, v65.log_contract(handle, log_path), ledger); ledger.append(snapshot)
        audit = v65.audit_state(model, optimizer, 0, train_dataset, dev_dataset, subsets, device)
        audit["fusion"] = collect_fusion(model, train_dataset, subsets["train_indices"], device); audits.append(audit)
        ledger.append({"event": "audit_complete", "step": 0, "state": v65.classify(audit)})
        for expected_step, index in enumerate(order, 1):
            started = time.perf_counter(); sample = train_dataset[index]; data_done = time.perf_counter()
            inputs, targets = inputs_to_device(sample, device), target_to_device(sample, device)
            optimizer.zero_grad(set_to_none=True); capture.clear(); forward_started = time.perf_counter()
            losses = model(*inputs, targets); total = sum(losses.values()); torch.cuda.synchronize(); forward_done = time.perf_counter()
            if not losses or not all(torch.isfinite(value).all() for value in losses.values()):
                raise RuntimeError(f"Non-finite V67 loss seed={seed} step={expected_step}")
            fusion = model.fusion_diagnostics(); weights = model.last_feature_outputs["fusion_weights"].detach()[0]
            feature_outputs = model.last_feature_outputs
            scorer_logits = torch.cat([
                model.feature_scaffold.reliability_scorer(feature_outputs[key])
                for key in ("rgb_reference", "aligned_ir", "aligned_event")
            ], dim=1).detach()[0]
            total.backward(); torch.cuda.synchronize(); backward_done = time.perf_counter()
            global_norm, global_finite = gradient_norm(model.parameters())
            bbox = model.detector.head.regression_head.bbox_reg
            bbox_summary = v63.module_grad_summary(bbox); tower_summary = v63.module_grad_summary(model.detector.head.regression_head.conv)
            head_summary = v63.module_grad_summary(model.detector.head); scorer_parameter_norm, scorer_gradient_norm, scorer_finite = scorer_norms(model)
            if not global_finite or not scorer_finite or not all((bbox_summary["finite"], tower_summary["finite"], head_summary["finite"])):
                raise RuntimeError(f"V67 gradient contract failure seed={seed} step={expected_step}")
            scorer_gradient_seen = scorer_gradient_seen or scorer_gradient_norm > 0
            optimizer.step(); completed += 1
            if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                raise RuntimeError(f"Non-finite V67 parameter seed={seed} step={expected_step}")
            torch.cuda.synchronize(); optimizer_done = time.perf_counter()
            if fusion["departed_from_exact_uniform"] and first_departure is None: first_departure = completed
            values = {key: float(value.detach().cpu()) for key, value in losses.items()}; bias_values = bbox.bias.detach().cpu().tolist(); weight = bbox.weight.detach()
            weight_grad = 0.0 if bbox.weight.grad is None else float(bbox.weight.grad.double().norm().cpu())
            bias_grad = 0.0 if bbox.bias.grad is None else float(bbox.bias.grad.double().norm().cpu())
            entropy = float(-(weights.clamp_min(1e-12) * weights.clamp_min(1e-12).log()).sum().cpu())
            row = {"variant": variant, "step": completed, "original_row_id": sample["original_row_id"],
                "target_box_count": int(sample["target_rgb"]["boxes"].shape[0]),
                "valid_target_count": int(((sample["target_rgb"]["boxes"][:, 2:] - sample["target_rgb"]["boxes"][:, :2]) > 0).all(dim=1).sum()),
                "matched_anchor_count": int(capture["matched_anchor_count"]), "loss_total": float(total.detach().cpu()),
                "loss_classifier": values["classification"], "loss_box_reg": values["bbox_regression"], "loss_centerness": values["bbox_ctrness"],
                "learning_rate": 1e-4, "global_gradient_norm": global_norm, "bbox_weight_gradient_norm": weight_grad,
                "bbox_bias_gradient_norm": bias_grad, "bbox_gradient_nonzero_fraction": bbox_summary["nonzero_fraction"],
                "bbox_bias_0": bias_values[0], "bbox_bias_1": bias_values[1], "bbox_bias_2": bias_values[2], "bbox_bias_3": bias_values[3],
                "finite": True, "cuda_allocated_bytes": torch.cuda.memory_allocated(), "cuda_reserved_bytes": torch.cuda.memory_reserved(),
                "data_time_sec": data_done - previous_end, "forward_time_sec": forward_done - forward_started,
                "backward_time_sec": backward_done - forward_done, "optimizer_time_sec": optimizer_done - backward_done,
                "step_time_sec": optimizer_done - started, "regression_tower_gradient_norm": tower_summary["norm"],
                "detector_head_gradient_norm": head_summary["norm"], "bbox_weight_norm_after": float(weight.norm().cpu()),
                "bbox_weight_min_after": float(weight.min().cpu()), "bbox_weight_max_after": float(weight.max().cpu()),
                "bbox_bias_min_after": min(bias_values), "bbox_bias_max_after": max(bias_values),
                "fusion_rgb": float(weights[0].cpu()), "fusion_ir": float(weights[1].cpu()), "fusion_event": float(weights[2].cpu()),
                "fusion_entropy": entropy, "fusion_departed_exact_uniform": fusion["departed_from_exact_uniform"],
                "fusion_weight_sum": float(weights.sum().cpu()),
                "fusion_dominant_modality": ("rgb", "ir", "event")[int(weights.argmax().cpu())],
                "fusion_dominant_fraction": float(weights.max().cpu()),
                "scorer_logit_rgb": float(scorer_logits[0].cpu()),
                "scorer_logit_ir": float(scorer_logits[1].cpu()),
                "scorer_logit_event": float(scorer_logits[2].cpu()),
                "scorer_gradient_norm": scorer_gradient_norm, "scorer_parameter_norm": scorer_parameter_norm}
            writer.writerow(row); step_times.append(row["step_time_sec"])
            if completed in v65.SNAPSHOT_STEPS:
                snapshot = v65.atomic_snapshot(model, optimizer, completed, v65.log_contract(handle, log_path), ledger); ledger.append(snapshot)
                write_json(OUT / "recovery_ledger.json", {"seeds": all_ledgers, "recovery_events": 0})
            if completed in v65.AUDIT_STEPS:
                audit = v65.audit_state(model, optimizer, completed, train_dataset, dev_dataset, subsets, device)
                audit["fusion"] = collect_fusion(model, train_dataset, subsets["train_indices"], device); audits.append(audit)
                state = v65.classify(audit); ledger.append({"event": "audit_complete", "step": completed, "state": state})
                print(f"V67_AUDIT_COMPLETE seed={seed} step={completed} state={state} valid={audit['geometry']['aggregate_counts']['valid']}", flush=True)
                if len(audits) >= 2 and v65.classify(audits[-1]) == v65.classify(audits[-2]) == "EARLY_BBOX_COLLAPSE":
                    raise RuntimeError("V67_RELIABILITY_BBOX_COLLAPSE")
            previous_end = optimizer_done
    if completed != v65.STEPS or [audit["step"] for audit in audits] != list(v65.AUDIT_STEPS) or not scorer_gradient_seen:
        raise RuntimeError(f"V67 seed-{seed} training contract incomplete")
    checkpoint_path(seed).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state": model.state_dict(), "variant": variant, "seed": seed,
        "completed_optimizer_steps": completed, "common_init_sha256": INIT_HASHES[seed],
        "full_order_sha256": base.ORDER_SHA256, "configuration_sha256": CONFIG_HASH}, checkpoint_path(seed))
    checkpoint = {"path_local_not_committed": str(checkpoint_path(seed)), "sha256": sha256(checkpoint_path(seed)),
        "bytes": checkpoint_path(seed).stat().st_size, "completed_optimizer_steps": completed,
        "selection_metric": None, "common_init_sha256": INIT_HASHES[seed],
        "final_state_fingerprint": base.tensor_dict_fingerprint({key: value.detach().cpu() for key, value in model.state_dict().items()})}
    summary = {"seed": seed, "variant": variant, "completed_optimizer_steps": completed, "all_finite": True,
        "elapsed_seconds": time.perf_counter() - started_run, "step_time_mean_sec": float(np.mean(step_times)),
        "step_time_min_sec": min(step_times), "step_time_max_sec": max(step_times),
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(), "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "scorer_gradient_seen": scorer_gradient_seen, "first_exact_uniform_departure_step": first_departure,
        "checkpoint": checkpoint}
    del optimizer, model; torch.cuda.empty_cache(); return summary, audits


def evaluate_seed(seed, device):
    configure_helpers(seed); marker = OUT / f"seed{seed}_evaluation_started.json"; metrics_path = OUT / f"seed{seed}_full_devval_metrics.json"
    if marker.exists() or metrics_path.exists(): raise RuntimeError(f"Seed-{seed} evaluation already attempted")
    checkpoint_sha = sha256(checkpoint_path(seed)); write_json(marker, {"seed": seed, "attempt": 1, "rows": 1845,
        "checkpoint_sha256": checkpoint_sha, "final_checkpoint_only": True})
    payload = torch.load(checkpoint_path(seed), map_location="cpu", weights_only=False)
    if payload["seed"] != seed or payload["completed_optimizer_steps"] != v65.STEPS: raise RuntimeError("V67 checkpoint contract mismatch")
    model = V67ReliabilitySoftplusDetector().to(device); model.load_state_dict(payload["model_state"], strict=True)
    model.detector.score_thresh = 0.001; model.detector.nms_thresh = 0.6; model.detector.detections_per_img = 100; model.eval()
    dataset = MMUAVFeatureAlignmentDataset(v65.DEVVAL_MANIFEST, 320, validate_paths=False)
    predictions, targets, weights, logits = [], [], [], []; zero_predictions = 0; started = time.perf_counter()
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    with torch.no_grad():
        for index in range(len(dataset)):
            sample = dataset[index]; output = model(*inputs_to_device(sample, device))[0]
            if not all(torch.isfinite(value).all() for value in output.values()): raise RuntimeError(f"Non-finite V67 prediction seed={seed}")
            zero_predictions += int(output["boxes"].shape[0] == 0)
            features = model.last_feature_outputs; weights.append(features["fusion_weights"].detach().cpu())
            logits.append(torch.cat([model.feature_scaffold.reliability_scorer(features[key])
                for key in ("rgb_reference", "aligned_ir", "aligned_event")], dim=1).detach().cpu())
            predictions.append({key: value.detach().cpu() for key, value in output.items()})
            target = sample["target_rgb"]; targets.append({"boxes": target["boxes"].cpu(), "labels": target["labels"].cpu()})
    torch.cuda.synchronize(); elapsed = time.perf_counter() - started; metrics = v65.full_coco_metrics(predictions, targets)
    if metrics["images"] != 1845 or not all(math.isfinite(metrics[key]) for key in METRIC_KEYS): raise RuntimeError("V67 metric contract failed")
    fusion = fusion_summary(torch.cat(weights), torch.cat(logits)); metrics.update({"seed": seed, "evaluation_attempt": 1,
        "final_checkpoint_only": True, "checkpoint_sha256": checkpoint_sha, "inference_seconds": elapsed,
        "fps": len(dataset) / elapsed, "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(), "settings": {"score_threshold": 0.001,
        "nms_threshold": 0.6, "max_detections": 100}, "fusion_diagnostics": fusion})
    safety = {"seed": seed, "evaluated_images": len(dataset), "ground_truth_boxes": metrics["gt_boxes"],
        "prediction_count": metrics["detections"], "zero_prediction_images": zero_predictions,
        "non_finite_prediction_images": 0, "all_predictions_finite": True}
    write_json(metrics_path, metrics); write_json(OUT / f"seed{seed}_prediction_safety.json", safety)
    del model, predictions, targets, weights, logits; torch.cuda.empty_cache(); return metrics, safety


def matched_summary(prior, reliability):
    per_seed, reliability_stats, delta_stats = {}, {}, {}
    for seed, baseline_key in ((0, "v65"), (1, "v66")):
        per_seed[str(seed)] = {key: {"equal": prior[baseline_key]["metrics"][key],
            "reliability": reliability[seed][key],
            "reliability_minus_equal": reliability[seed][key] - prior[baseline_key]["metrics"][key]} for key in METRIC_KEYS}
    for key in METRIC_KEYS:
        values = [reliability[seed][key] for seed in SEEDS]
        deltas = [per_seed[str(seed)][key]["reliability_minus_equal"] for seed in SEEDS]
        reliability_stats[key] = {"mean": statistics.mean(values), "sample_std": statistics.stdev(values),
            "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)}
        delta_stats[key] = {"mean": statistics.mean(deltas), "minimum": min(deltas),
            "maximum": max(deltas), "range": max(deltas) - min(deltas)}
    return {"descriptive_only": True, "n": 2, "per_seed": per_seed,
        "reliability_two_seed": reliability_stats, "matched_delta_two_seed": delta_stats,
        "no_independent_test": True, "no_significance_claim": True, "selection_or_rerun_trigger": False,
        "fusion_diagnostics": {str(seed): reliability[seed]["fusion_diagnostics"] for seed in SEEDS}}


def run() -> None:
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8")); lock = json.loads((OUT / "source_lock_v67.json").read_text(encoding="utf-8"))
    if git("rev-parse", "HEAD") != START_COMMIT or source_lock() != lock: raise RuntimeError("V67 source/start lock mismatch")
    if verify_prior_evidence() != protocol["prior_evidence"] or protected_fingerprint() != protocol["protected_baseline"]: raise RuntimeError("V67 evidence/protected mismatch")
    if not torch.cuda.is_available(): raise RuntimeError("CUDA unavailable for V67")
    states = {seed: torch.load(init_path(seed), map_location="cpu", weights_only=False)["state_dict"] for seed in SEEDS}
    if any(sha256(init_path(seed)) != INIT_HASHES[seed] for seed in SEEDS): raise RuntimeError("V67 initialization changed")
    train_dataset = MMUAVFeatureAlignmentDataset(base.TRAIN_MANIFEST, 320, validate_paths=False)
    dev_dataset = MMUAVFeatureAlignmentDataset(v65.DEVVAL_MANIFEST, 320, validate_paths=False)
    order = protocol["full_order"]["indices"]; ledgers = {str(seed): [] for seed in SEEDS}; device = torch.device("cuda:0")
    summaries, audit_map, metrics, predictions = {}, {}, {}, {}
    for seed in SEEDS:
        summaries[seed], audit_map[seed] = train_seed(seed, states[seed], order, train_dataset, dev_dataset,
                                                      protocol["subsets"], device, ledgers)
        metrics[seed], predictions[seed] = evaluate_seed(seed, device)
    total_steps = sum(summary["completed_optimizer_steps"] for summary in summaries.values())
    total_backward = sum(audit["gradient_probe"]["backward_calls"] for audits in audit_map.values() for audit in audits)
    snapshots = [event for events in ledgers.values() for event in events if event["event"] == "snapshot_verified"]
    safety = {"optimizer_steps": total_steps, "optimizer_step_limit": 14374,
        "per_seed_steps": {str(seed): summaries[seed]["completed_optimizer_steps"] for seed in SEEDS},
        "probe_backward_calls": total_backward, "probe_backward_limit": 80,
        "verified_recovery_snapshots": len(snapshots), "expected_recovery_snapshots": 38,
        "recovery_events": 0, "all_recovery_round_trips": all(all(row["round_trip_checks"].values()) for row in snapshots),
        "all_audit_isolation_checks": all(all(audit["isolation"].values()) for audits in audit_map.values() for audit in audits),
        "all_finite": all(summary["all_finite"] for summary in summaries.values()) and all(row["all_predictions_finite"] for row in predictions.values()),
        "prior_evidence_unchanged": verify_prior_evidence() == protocol["prior_evidence"],
        "initializations_unchanged": all(sha256(init_path(seed)) == INIT_HASHES[seed] for seed in SEEDS),
        "protected_fingerprint_unchanged": protected_fingerprint() == protocol["protected_baseline"],
        "full_devval_rows_per_seed": 1845, "evaluation_attempts_per_seed": 1, "final_checkpoint_only": True,
        "threshold_selection": False, "tuning": False, "checkpoint_selection": False,
        "extra_variants": 0, "extra_seeds": 0, "reruns": 0}
    if not all((total_steps == 14374, total_backward == 80, len(snapshots) == 38,
        safety["all_recovery_round_trips"], safety["all_audit_isolation_checks"], safety["all_finite"],
        safety["prior_evidence_unchanged"], safety["initializations_unchanged"], safety["protected_fingerprint_unchanged"])):
        raise RuntimeError(f"V67 safety audit failed: {safety}")
    comparison = matched_summary(protocol["prior_evidence"], metrics)
    write_json(OUT / "per_seed_geometry_audits.json", {str(seed): [{"step": audit["step"], "geometry": audit["geometry"],
        "devval_geometry": audit["devval_geometry"], "bbox_output_parameters": audit["bbox_output_parameters"],
        "fusion": audit["fusion"]} for audit in audit_map[seed]] for seed in SEEDS})
    write_json(OUT / "per_seed_gradient_audits.json", {str(seed): [{"step": audit["step"],
        "gradient_probe": audit["gradient_probe"], "isolation": audit["isolation"]} for audit in audit_map[seed]] for seed in SEEDS})
    write_json(OUT / "fusion_weight_diagnostics.json", {str(seed): {"audits": [{"step": audit["step"], **audit["fusion"]} for audit in audit_map[seed]],
        "full_devval": metrics[seed]["fusion_diagnostics"], "first_exact_uniform_departure_step": summaries[seed]["first_exact_uniform_departure_step"]} for seed in SEEDS})
    write_json(OUT / "per_seed_checkpoint_metadata.json", {str(seed): summaries[seed]["checkpoint"] for seed in SEEDS})
    write_json(OUT / "memory_timing_summary.json", {str(seed): summaries[seed] for seed in SEEDS})
    write_json(OUT / "matched_comparison_summary.json", comparison); write_json(OUT / "safety_audit.json", safety)
    classifications = {str(seed): [{"step": audit["step"], "state": v65.classify(audit)} for audit in audit_map[seed]] for seed in SEEDS}
    decision = "V67_TWO_SEED_RELIABILITY_FULLTRAIN_COMPLETE"
    write_json(OUT / "final_decision.json", {"decision": decision, "classifications": classifications,
        "metrics": {str(seed): {key: metrics[seed][key] for key in METRIC_KEYS} for seed in SEEDS},
        "comparison": comparison, "safety": safety})
    (OUT / "handoff.md").write_text(f"# V67 Handoff\n\nDecision: `{decision}`. Matched n=2 devval comparison only; no independent-test or significance claim.\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "metrics": {str(seed): {key: metrics[seed][key] for key in METRIC_KEYS} for seed in SEEDS},
                      "matched_deltas": comparison["matched_delta_two_seed"], "safety": safety}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(); group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only", action="store_true"); group.add_argument("--run", action="store_true")
    args = parser.parse_args(); prepare() if args.prepare_only else run()


if __name__ == "__main__":
    try: main()
    except torch.OutOfMemoryError as exc: raise SystemExit(f"V67_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY: {exc}")
