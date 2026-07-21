"""Run the frozen V64 seed-1 paired bbox-activation confirmation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import os
import sys
from pathlib import Path

import torch
from torchvision.models.detection import fcos as fcos_module


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.v63_bbox_activation_detector import V63BBoxActivationDetector
from rarepdet.tools import run_v63_mmuav_bbox_activation_rescue as v63
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import configure_seed as configure_seed_original


OUT = ROOT / "runs/v64_mmuav_seed1_bbox_activation_confirmation"
LOCAL = Path(r"D:\MM-UAV_v64_local")
INIT_PATH = LOCAL / "seed1_common_init.pt"
START_COMMIT = "2d257de8dbc5164c3cd36b3d0b6dd1ef5c258c34"
AUTHORIZATION_BASE = "83bb9351a5d0a6115d81047482e23fef5eed26bb"
V63_OUT = ROOT / "runs/v63_mmuav_paired_bbox_activation_rescue"
VARIANTS = ("v64_seed1_equal_relu_control", "v64_seed1_equal_softplus_b1_t20")
ACTIVATION = {VARIANTS[0]: "relu", VARIANTS[1]: "softplus_b1_t20"}
TRACE_STEPS = v63.TRACE_STEPS
CONFIG_HASH = hashlib.sha256(json.dumps({
    **v63.base.common_config(), "seed": 1, "steps": 200, "trace_steps": TRACE_STEPS,
    "paired_activation": ["relu", "softplus(beta=1.0,threshold=20.0)"],
    "atomic_recovery": True, "fresh_initialization": "seed1_once",
}, sort_keys=True).encode()).hexdigest()
V63_HASHES = {
    "final_decision.json": "2985ac382639dca8da6b3303b9e0e3fdb74bc6b54485de7c140f3f8dbda818bd",
    "safety_audit.json": "90f2a837e480d8947616ea60401805843487cf47541e50837522e766f7871e18",
    "per_variant_training_log.csv": "4b6e0ba9f89fe0314dff58a3a1b6ef9eefe021974643a384fe7e00a00c593dc9",
    "source_lock_v63.json": "489db6a090c8b38c4aa36c72bf238d116743ded91916ff006785ab382762776a",
}


def sha256(path: Path) -> str:
    return v63.sha256(path)


def write_json(path: Path, value: object) -> None:
    v63.write_json(path, value)


def git(*args: str) -> str:
    return v63.git(*args)


def protected_paths() -> list[Path]:
    fixed = {
        "rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py",
        "main.tex", "main_sivp_snjnl.tex",
    }
    selected = []
    for relative in git("ls-files").splitlines():
        historical = any(relative.startswith(f"runs/v{version}_") for version in range(40, 64))
        if relative in fixed or relative.startswith("manuscript/") or relative.startswith("submission/") or historical:
            path = ROOT / relative
            if path.is_file():
                selected.append(path)
    return selected


def protected_fingerprint() -> dict[str, object]:
    return v63.v62._aggregate(protected_paths())


def verify_v63() -> dict[str, object]:
    checks = {name: sha256(V63_OUT / name) == expected for name, expected in V63_HASHES.items()}
    final = json.loads((V63_OUT / "final_decision.json").read_text(encoding="utf-8"))
    safety = json.loads((V63_OUT / "safety_audit.json").read_text(encoding="utf-8"))
    protocol = json.loads((V63_OUT / "protocol.json").read_text(encoding="utf-8"))
    checkpoints = final["checkpoint_metadata"]
    checks.update({
        "decision": final["decision"] == "V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200",
        "relu_collapse_step15": final["comparison"]["first_collapse_step"]["v63_equal_relu_control"] == 15,
        "softplus_never_collapsed": final["comparison"]["first_collapse_step"]["v63_equal_softplus_b1_t20"] is None,
        "softplus_all_preserved": all(row["state"] == "GEOMETRY_AND_GRADIENT_PRESERVED"
                                      for row in final["comparison"]["trace_classifications"]["v63_equal_softplus_b1_t20"]),
        "prefix": protocol["prefix"]["sha256"] == "6345848e3287bea04f5c89927be7a714a6eed549a6b73d352779a6192b5c86ec",
        "steps": safety["optimizer_steps"] == 400 and set(safety["per_variant_optimizer_steps"].values()) == {200},
        "backward": safety["probe_backward_calls"] == 104,
        "recovery": safety["verified_recovery_snapshots"] == 26 and safety["recovery_events"] == 0,
        "relu_checkpoint": checkpoints["v63_equal_relu_control"]["sha256"] ==
                           "ddd6b79e4695672c981f9083865f881c6b623ea818a3236e72acc691b148b2e6",
        "softplus_checkpoint": checkpoints["v63_equal_softplus_b1_t20"]["sha256"] ==
                               "6df9b915a2f520cbe1e51dc5ee962bd1e0b8fbb11465314377c9a3ba08a6269d",
        "no_full_eval": safety["full_devval_rows"] == 0 and not safety["ap_ar_computed"],
    })
    if not all(checks.values()):
        raise RuntimeError(f"V63 evidence mismatch: {checks}")
    return {"checks": checks, "file_sha256": {name: sha256(V63_OUT / name) for name in V63_HASHES}}


def source_lock(init_sha256: str) -> dict[str, object]:
    sources = [
        "rarepdet/tools/run_v64_mmuav_seed1_bbox_activation_confirmation.py",
        "tests/test_v64_mmuav_seed1_bbox_activation_confirmation.py",
        "rarepdet/tools/run_v63_mmuav_bbox_activation_rescue.py",
        "rarepdet/experimental/v63_bbox_activation_detector.py",
        "rarepdet/tools/run_v62_mmuav_clean_bbox_bias_pilot.py",
        "rarepdet/tools/run_v61_mmuav_bbox_bias_pilot.py",
        "rarepdet/experimental/v57_fusion_superset_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
    ]
    installed = Path(inspect.getsourcefile(fcos_module.FCOSRegressionHead) or "")
    lines, line = inspect.getsourcelines(fcos_module.FCOSRegressionHead.forward)
    relu_lines = [line + index for index, value in enumerate(lines) if "functional.relu(self.bbox_reg" in value]
    v63_lock = json.loads((V63_OUT / "source_lock_v63.json").read_text(encoding="utf-8"))
    if len(relu_lines) != 1 or relu_lines[0] != v63_lock["historical_relu_line"]:
        raise RuntimeError(f"V64 FCOS ReLU source mismatch: {relu_lines}")
    if sha256(installed) != v63_lock["installed_fcos_sha256"]:
        raise RuntimeError("Installed torchvision FCOS changed after V63")
    return {
        "starting_commit": START_COMMIT, "authorization_base": AUTHORIZATION_BASE,
        "source_hashes": {path: sha256(ROOT / path) for path in sources},
        "installed_fcos_path": str(installed), "installed_fcos_sha256": sha256(installed),
        "historical_relu_line": relu_lines[0],
        "historical_relu_expression": "nn.functional.relu(self.bbox_reg(bbox_feature))",
        "softplus_expression": "F.softplus(pre_activation, beta=1.0, threshold=20.0)",
        "shared_training_inference_head": True, "seed1_initialization_sha256": init_sha256,
    }


def _configure_runtime(init_sha256: str) -> None:
    v63.OUT = OUT
    v63.LOCAL = LOCAL
    v63.START_COMMIT = START_COMMIT
    v63.AUTHORIZATION_BASE = AUTHORIZATION_BASE
    v63.VARIANTS = VARIANTS
    v63.ACTIVATION = ACTIVATION
    v63.CONFIG_HASH = CONFIG_HASH
    v63._RECOVERY_LEDGER = {name: [] for name in VARIANTS}
    v63.base.INIT_SHA256 = init_sha256
    v63.configure_seed = lambda _ignored: configure_seed_original(1)
    v63.checkpoint_path = checkpoint_path


def checkpoint_path(variant: str) -> Path:
    return LOCAL / f"{variant}_final_step200.pt"


def generate_seed1_initialization() -> dict[str, object]:
    if INIT_PATH.exists():
        raise RuntimeError(f"Seed-1 initialization already exists; refusing regeneration: {INIT_PATH}")
    LOCAL.mkdir(parents=True, exist_ok=True)
    configure_seed_original(1)
    model = V63BBoxActivationDetector("relu")
    state = v63.base.clone_state(model.state_dict())
    if state[v63.base.BBOX_BIAS_KEY].tolist() != [0.0, 0.0, 0.0, 0.0]:
        raise RuntimeError("Fresh seed-1 bbox output bias is not historical zero")
    if not all(torch.isfinite(value).all() for value in state.values()):
        raise RuntimeError("Fresh seed-1 state contains non-finite tensors")
    parameter_keys = [name for name, _ in model.named_parameters()]
    buffer_keys = [name for name, _ in model.named_buffers()]
    tensor_contract = {name: {"shape": list(value.shape), "dtype": str(value.dtype),
                              "finite": bool(torch.isfinite(value).all())} for name, value in state.items()}
    payload = {"state_dict": state, "seed": 1, "constructor": "V63BBoxActivationDetector(relu)",
               "source_commit": START_COMMIT, "tensor_count": len(state),
               "parameter_keys": parameter_keys, "buffer_keys": buffer_keys,
               "tensor_contract": tensor_contract, "generation_count": 1}
    temporary = INIT_PATH.with_suffix(".pt.tmp")
    with temporary.open("wb") as handle:
        torch.save(payload, handle); handle.flush()
        try:
            os.fsync(handle.fileno())
        except OSError:
            pass
    os.replace(temporary, INIT_PATH)
    digest = sha256(INIT_PATH)
    loaded = torch.load(INIT_PATH, map_location="cpu", weights_only=False)
    control = V63BBoxActivationDetector("relu")
    softplus = V63BBoxActivationDetector("softplus_b1_t20")
    control_result = control.load_state_dict(loaded["state_dict"], strict=True)
    softplus_result = softplus.load_state_dict(loaded["state_dict"], strict=True)
    control_state, softplus_state = control.state_dict(), softplus.state_dict()
    checks = {
        "serialized_file_exists": INIT_PATH.is_file(),
        "generation_count_one": loaded["generation_count"] == 1,
        "seed_exact_one": loaded["seed"] == 1,
        "strict_reload_control": not control_result.missing_keys and not control_result.unexpected_keys,
        "strict_reload_softplus": not softplus_result.missing_keys and not softplus_result.unexpected_keys,
        "paired_keys_identical": list(control_state) == list(softplus_state),
        "paired_tensors_bit_identical": all(torch.equal(control_state[key], softplus_state[key]) for key in control_state),
        "round_trip_state_exact": all(torch.equal(state[key], loaded["state_dict"][key]) for key in state),
        "historical_zero_bbox_bias": loaded["state_dict"][v63.base.BBOX_BIAS_KEY].tolist() == [0.0] * 4,
        "all_finite": all(row["finite"] for row in loaded["tensor_contract"].values()),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Seed-1 initialization freeze failed: {checks}")
    return {"path_local_not_committed": str(INIT_PATH), "sha256": digest,
            "bytes": INIT_PATH.stat().st_size, "seed": 1, "generation_count": 1,
            "tensor_count": len(state), "parameter_count": len(parameter_keys), "buffer_count": len(buffer_keys),
            "parameter_keys": parameter_keys, "buffer_keys": buffer_keys,
            "tensor_contract": tensor_contract, "state_fingerprint": v63.base.tensor_dict_fingerprint(state),
            "checks": checks, "regeneration_allowed": False, "trained_checkpoint_used": False}


def load_frozen_initialization(expected_sha256: str) -> dict[str, torch.Tensor]:
    if not INIT_PATH.is_file() or sha256(INIT_PATH) != expected_sha256:
        raise RuntimeError("Frozen seed-1 initialization hash mismatch")
    payload = torch.load(INIT_PATH, map_location="cpu", weights_only=False)
    if payload.get("seed") != 1 or payload.get("generation_count") != 1:
        raise RuntimeError("Frozen seed-1 initialization metadata mismatch")
    state = payload["state_dict"]
    if len(state) != payload["tensor_count"] or not all(torch.isfinite(value).all() for value in state.values()):
        raise RuntimeError("Frozen seed-1 state contract mismatch")
    return state


def initial_states(expected_sha256: str) -> tuple[dict[str, dict[str, torch.Tensor]], dict[str, object]]:
    common = load_frozen_initialization(expected_sha256)
    control, softplus = v63.base.clone_state(common), v63.base.clone_state(common)
    differences = [key for key in control if not torch.equal(control[key], softplus[key])]
    if differences:
        raise RuntimeError(f"V64 paired state mismatch: {differences[:5]}")
    fingerprint = v63.base.tensor_dict_fingerprint(control)
    return {VARIANTS[0]: control, VARIANTS[1]: softplus}, {
        "changed_tensor_count": 0, "changed_element_count": 0, "state_dict_keys_identical": True,
        "state_tensors_bit_identical": True, "state_fingerprint": fingerprint,
        "historical_bbox_bias_unchanged": control[v63.base.BBOX_BIAS_KEY].tolist(),
        "sole_difference": "parameter-free bbox-distance activation",
        "softplus": {"beta": 1.0, "threshold": 20.0}, "seed": 1,
        "initialization_sha256": expected_sha256,
    }


def step0_identity(states, dataset, first_index) -> dict[str, object]:
    result = v63.step0_identity(states, dataset, first_index)
    models = [v63.build_model(name) for name in VARIANTS]
    for model, name in zip(models, VARIANTS):
        model.load_state_dict(states[name], strict=True); model.eval()
    sample = dataset[first_index]
    outputs = []
    with torch.no_grad():
        for model in models:
            model._feature_forward(*v63.inputs_to_device(sample, torch.device("cpu")))
            outputs.append({key: model.last_feature_outputs[key].clone() for key in
                            ("rgb_reference", "aligned_ir", "aligned_event", "fused",
                             "fusion_weights", "ir_theta", "event_theta")})
    alignment_checks = {key: torch.equal(outputs[0][key], outputs[1][key]) for key in outputs[0]}
    if not all(alignment_checks.values()):
        raise RuntimeError(f"V64 paired alignment output mismatch: {alignment_checks}")
    result["alignment_and_fusion_checks"] = alignment_checks
    result["all_alignment_and_fusion_bit_identical"] = True
    return result


def prepare() -> None:
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError("Unexpected V64 starting commit")
    if OUT.exists() or INIT_PATH.exists():
        raise RuntimeError("V64 output or seed-1 initialization already exists; refusing regeneration")
    OUT.mkdir(parents=True)
    v63_verification = verify_v63()
    if sha256(v63.base.TRAIN_MANIFEST) != v63.base.TRAIN_SHA256:
        raise RuntimeError("V64 train manifest mismatch")
    dev_manifest = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"
    if sha256(dev_manifest) != "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54":
        raise RuntimeError("V64 devval manifest mismatch")
    initialization = generate_seed1_initialization()
    init_sha = initialization["sha256"]
    _configure_runtime(init_sha)
    dataset = MMUAVFeatureAlignmentDataset(v63.base.TRAIN_MANIFEST, 320, validate_paths=True)
    subsets = v63.base.frozen_subsets()
    prefix = v63.prefix_200(dataset)
    if prefix["sha256"] != "6345848e3287bea04f5c89927be7a714a6eed549a6b73d352779a6192b5c86ec":
        raise RuntimeError("V64 first-200 prefix differs from V63")
    states, intervention = initial_states(init_sha)
    identity = step0_identity(states, dataset, prefix["indices"][0])
    devval_gate = v63.actual_devval_gate()
    configs = {name: {**v63.base.common_config(), "seed": 1, "name": name, "steps": 200,
                      "trace_steps": list(TRACE_STEPS), "bbox_activation": ACTIVATION[name],
                      "bbox_bias": states[name][v63.base.BBOX_BIAS_KEY].tolist(),
                      "fresh_seed1_initialization_sha256": init_sha,
                      "atomic_recovery_before_each_trace": True} for name in VARIANTS}
    protocol = {"prepared_at": v63.base.now(), "starting_commit": START_COMMIT,
                "authorization_base": AUTHORIZATION_BASE, "v63_verification": v63_verification,
                "train_rows": len(dataset), "train_sha256": v63.base.TRAIN_SHA256,
                "devval_sha256": sha256(dev_manifest), "prefix": prefix, "subsets": subsets,
                "seed1_initialization": initialization, "initialization": intervention,
                "step0_identity": identity, "actual_devval_gate": devval_gate,
                "configs": configs, "configuration_sha256": CONFIG_HASH,
                "run_order": list(VARIANTS), "steps_per_variant": 200,
                "optimizer_step_limit": 400, "probe_backward_limit": 104,
                "protected_baseline": protected_fingerprint()}
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v64.json", source_lock(init_sha))
    write_json(OUT / "v63_evidence_verification.json", v63_verification)
    write_json(OUT / "seed1_initialization_verification.json", initialization)
    write_json(OUT / "activation_intervention.json", {"control": "native torchvision ReLU",
               "intervention": "softplus", "beta": 1.0, "threshold": 20.0,
               "parameter_free": True, "same_regression_head_training_and_inference": True})
    write_json(OUT / "trace_schedule.json", {"steps": list(TRACE_STEPS), "count": 13,
               "gradient_rows_per_trace": 4, "total_backward_limit": 104})
    write_json(OUT / "per_variant_config.json", configs)
    write_json(OUT / "recovery_ledger.json", {"variants": v63._RECOVERY_LEDGER, "recovery_events": 0})
    (OUT / "protocol.md").write_text(
        "# V64 Seed-1 Bbox-Activation Confirmation\n\nOne fresh seed-1 state is frozen locally. "
        "The sole paired difference is native FCOS ReLU versus parameter-free Softplus(beta=1.0, threshold=20.0).\n",
        encoding="utf-8")
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v64_mmuav_seed1_bbox_activation_confirmation.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v64_mmuav_seed1_bbox_activation_confirmation.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v64_mmuav_seed1_bbox_activation_confirmation.py --run\n",
        encoding="utf-8")
    print(json.dumps({"status": "V64_PREPARED_CPU_ONLY", "seed1_initialization_sha256": init_sha,
                      "protocol": protocol}, indent=2))


def run() -> None:
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    init_sha = protocol["seed1_initialization"]["sha256"]
    _configure_runtime(init_sha)
    lock = json.loads((OUT / "source_lock_v64.json").read_text(encoding="utf-8"))
    if source_lock(init_sha) != lock:
        raise RuntimeError("V64 source changed after CPU lock")
    if verify_v63() != protocol["v63_verification"]:
        raise RuntimeError("V63 evidence changed before V64 CUDA")
    if protected_fingerprint() != protocol["protected_baseline"]:
        raise RuntimeError("Protected evidence changed before V64 CUDA")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for V64")
    states, intervention = initial_states(init_sha)
    if intervention != protocol["initialization"]:
        raise RuntimeError("V64 frozen paired initialization changed")
    order = protocol["prefix"]["indices"]
    if len(order) != 200 or len(set(order)) != 200:
        raise RuntimeError("V64 first-200 order invalid")
    train_dataset = MMUAVFeatureAlignmentDataset(v63.base.TRAIN_MANIFEST, 320, validate_paths=False)
    dev_dataset = MMUAVFeatureAlignmentDataset(
        ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt",
        320, validate_paths=False)
    device = torch.device("cuda:0")
    log_path = OUT / "per_variant_training_log.csv"
    if log_path.exists():
        raise RuntimeError("Refusing to overwrite V64 training log")
    summaries, trace_map, total_steps = {}, {}, 0
    v63._RECOVERY_LEDGER = {name: [] for name in VARIANTS}
    with log_path.open("w", encoding="utf-8", newline="") as handle:
        v63._LOG_HANDLE = handle
        writer = csv.DictWriter(handle, fieldnames=v63.LOG_FIELDS); writer.writeheader()
        for name in VARIANTS:
            v63._CURRENT_VARIANT = name
            summary, traces = v63.train_variant(name, states[name], order, train_dataset, dev_dataset,
                                                 protocol["subsets"], device, total_steps, writer)
            handle.flush(); summaries[name], trace_map[name] = summary, traces
            total_steps += summary["completed_optimizer_steps"]
    v63._LOG_HANDLE = None
    total_backward = sum(trace["gradient_probe"]["backward_calls"] for traces in trace_map.values() for trace in traces)
    if total_steps != 400 or total_backward != 104:
        raise RuntimeError(f"V64 budget mismatch: {total_steps}, {total_backward}")
    classifications = {name: [{"step": trace["step"], "state": v63.classify(trace)} for trace in traces]
                       for name, traces in trace_map.items()}
    first_collapse = {name: next((row["step"] for row in rows if row["state"] == "EARLY_BBOX_COLLAPSE"), None)
                      for name, rows in classifications.items()}
    first_preserved = {name: next((row["step"] for row in rows if row["state"] == "GEOMETRY_AND_GRADIENT_PRESERVED"), None)
                       for name, rows in classifications.items()}
    control_collapse, softplus_collapse = first_collapse[VARIANTS[0]], first_collapse[VARIANTS[1]]
    if control_collapse is None:
        decision = "V64_SEED1_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS"
    elif softplus_collapse is not None:
        decision = "V64_SEED1_RELU_AND_SOFTPLUS_BOTH_COLLAPSE"
    elif control_collapse <= 50 and classifications[VARIANTS[1]][-1]["state"] == "GEOMETRY_AND_GRADIENT_PRESERVED":
        decision = "V64_SEED1_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200"
    else:
        decision = "V64_SEED1_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_MIXED"
    geometry_output = {name: [{"step": trace["step"], "geometry": trace["geometry"],
                               "devval_geometry": trace["devval_geometry"],
                               "bbox_output_parameters": trace["bbox_output_parameters"]} for trace in traces]
                       for name, traces in trace_map.items()}
    gradient_output = {name: [{"step": trace["step"], "gradient_probe": trace["gradient_probe"],
                               "isolation": trace["isolation"]} for trace in traces]
                       for name, traces in trace_map.items()}
    derivative_summary = {name: [{"step": trace["step"], "levels": [{
        "level": level["level"], "all_mean": level["derivative_all_mean"],
        "all_exact_zero_fraction": level["derivative_all_exact_zero_fraction_mean"],
        "matched_mean": level["derivative_matched_mean"],
        "matched_exact_zero_fraction": level["derivative_matched_exact_zero_fraction_mean"]}
        for level in trace["geometry"]["levels"]]} for trace in traces] for name, traces in trace_map.items()}
    ledger = json.loads((OUT / "recovery_ledger.json").read_text(encoding="utf-8"))
    snapshots = [row for rows in ledger["variants"].values() for row in rows if row["event"] == "snapshot_verified"]
    safety = {"optimizer_steps": total_steps, "optimizer_step_limit": 400,
              "per_variant_optimizer_steps": {name: summaries[name]["completed_optimizer_steps"] for name in VARIANTS},
              "probe_backward_calls": total_backward, "probe_backward_limit": 104,
              "verified_recovery_snapshots": len(snapshots), "recovery_events": ledger["recovery_events"],
              "all_recovery_round_trips": all(all(row["round_trip_checks"].values()) for row in snapshots),
              "all_trace_isolation_checks": all(all(trace["isolation"].values()) for traces in trace_map.values() for trace in traces),
              "all_finite": all(summary["all_finite"] for summary in summaries.values()),
              "v63_evidence_unchanged": verify_v63() == protocol["v63_verification"],
              "seed1_initialization_unchanged": sha256(INIT_PATH) == init_sha,
              "protected_fingerprint_unchanged": protected_fingerprint() == protocol["protected_baseline"],
              "frozen_devval_rows_per_variant": 32, "full_devval_rows": 0, "ap_ar_computed": False,
              "threshold_selection": False, "tuning": False, "checkpoint_selection": False,
              "initialization_candidates_generated": 1}
    if len(snapshots) != 26 or not all((safety["all_recovery_round_trips"], safety["all_trace_isolation_checks"],
                                       safety["v63_evidence_unchanged"], safety["seed1_initialization_unchanged"],
                                       safety["protected_fingerprint_unchanged"], safety["all_finite"])):
        raise RuntimeError(f"V64 safety audit failed: {safety}")
    comparison = {"trace_classifications": classifications, "first_collapse_step": first_collapse,
                  "first_preserved_step": first_preserved, "selected_outcome": decision,
                  "independent_seed1_bounded_mechanistic_evidence_only": True}
    write_json(OUT / "per_variant_trace_geometry.json", geometry_output)
    write_json(OUT / "per_variant_trace_gradient.json", gradient_output)
    write_json(OUT / "activation_derivative_summary.json", derivative_summary)
    write_json(OUT / "per_variant_checkpoint_metadata.json", {name: summaries[name]["checkpoint"] for name in VARIANTS})
    write_json(OUT / "paired_trace_comparison.json", comparison)
    write_json(OUT / "memory_timing_summary.json", summaries)
    write_json(OUT / "safety_audit.json", safety)
    write_json(OUT / "final_decision.json", {"decision": decision, "comparison": comparison, "safety": safety,
               "seed1_initialization_sha256": init_sha,
               "checkpoint_metadata": {name: summaries[name]["checkpoint"] for name in VARIANTS}})
    (OUT / "handoff.md").write_text(
        f"# V64 Handoff\n\nDecision: `{decision}`. Independent seed-1 bounded mechanistic evidence only; "
        "no full run or AP/AR was authorized.\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "seed1_initialization_sha256": init_sha,
                      "first_collapse": first_collapse, "first_preserved": first_preserved,
                      "safety": safety}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(); group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only", action="store_true"); group.add_argument("--run", action="store_true")
    args = parser.parse_args(); prepare() if args.prepare_only else run()


if __name__ == "__main__":
    try:
        main()
    except torch.OutOfMemoryError as exc:
        raise SystemExit(f"V64_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY: {exc}")
