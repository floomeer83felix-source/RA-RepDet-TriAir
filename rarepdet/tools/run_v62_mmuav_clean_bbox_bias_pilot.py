"""Run the V62 clean paired bbox-bias pilot with corrected traces and recovery."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

import torch
from torchvision.ops import boxes as box_ops


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.v57_fusion_superset_detector import V57FusionSupersetDetector
from rarepdet.tools import run_v61_mmuav_bbox_bias_pilot as base
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import inputs_to_device, target_to_device


OUT = ROOT / "runs/v62_mmuav_clean_bbox_bias_paired_rerun"
LOCAL = Path(r"D:\MM-UAV_v62_local")
START_COMMIT = "2e1ecb33280a9e928d9ee7fa574188e29d315660"
AUTHORIZATION_BASE = "e60568bb68d789555099b2fb8ae6bfeefbba33bc"
VARIANTS = ("v62_equal_control_instrumented", "v62_equal_bbox_bias_p001")
V61_OUT = ROOT / "runs/v61_mmuav_early_bbox_collapse_prevention"
V61_LOG_SHA256 = "a96e0260079cbd05fd62fcc184a6908476490c42ecebe9b44373af4aebfd0965"
FAILED_ROW_ID = "devval:00005919"
CONFIG_HASH = hashlib.sha256(json.dumps({**base.common_config(), "atomic_recovery": True}, sort_keys=True).encode()).hexdigest()

_ORIGINAL_TRACE_STATE = base.trace_state
_CURRENT_VARIANT = ""
_LOG_HANDLE = None
_RECOVERY_LEDGER: dict[str, list[dict[str, object]]] = {name: [] for name in VARIANTS}


def configure_base() -> None:
    base.OUT = OUT
    base.LOCAL = LOCAL
    base.START_COMMIT = START_COMMIT
    base.AUTHORIZATION_BASE = AUTHORIZATION_BASE
    base.VARIANTS = VARIANTS
    base.protected_paths = protected_paths
    base.aggregate_fingerprint = aggregate_fingerprint
    base.source_lock = source_lock
    base.geometry_row = geometry_row
    base.trace_state = trace_state_with_recovery


def sha256(path: Path) -> str:
    return base.sha256(path)


def write_json(path: Path, value: object) -> None:
    base.write_json(path, value)


def git(*args: str) -> str:
    return base.git(*args)


def protected_paths() -> list[Path]:
    fixed = {
        "rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py",
        "main.tex", "main_sivp_snjnl.tex",
    }
    selected = []
    for relative in git("ls-files").splitlines():
        historical = any(relative.startswith(f"runs/v{version}_") for version in range(40, 62))
        if relative in fixed or relative.startswith("manuscript/") or relative.startswith("submission/") or historical:
            path = ROOT / relative
            if path.is_file():
                selected.append(path)
    return selected


def aggregate_fingerprint(paths: list[Path]) -> dict[str, object]:
    return base.aggregate_fingerprint.__wrapped__(paths) if hasattr(base.aggregate_fingerprint, "__wrapped__") else _aggregate(paths)


def _aggregate(paths: list[Path]) -> dict[str, object]:
    digest = hashlib.sha256()
    total = 0
    for path in sorted(paths, key=lambda item: item.as_posix().lower()):
        relative = path.relative_to(ROOT).as_posix()
        file_hash = sha256(path)
        digest.update(relative.encode() + b"\0" + file_hash.encode() + b"\n")
        total += path.stat().st_size
    return {"file_count": len(paths), "total_bytes": total, "aggregate_sha256": digest.hexdigest()}


def source_lock() -> dict[str, object]:
    sources = [
        "rarepdet/tools/run_v62_mmuav_clean_bbox_bias_pilot.py",
        "tests/test_v62_mmuav_clean_bbox_bias_pilot.py",
        "rarepdet/tools/run_v61_mmuav_bbox_bias_pilot.py",
        "rarepdet/tools/run_v57_mmuav_paired_fusion.py",
        "rarepdet/tools/run_v60_bbox_collapse_provenance_audit.py",
        "rarepdet/experimental/v57_fusion_superset_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
    ]
    installed = Path(__import__("inspect").getsourcefile(base.fcos_module.FCOS) or "")
    return {"starting_commit": START_COMMIT, "authorization_base": AUTHORIZATION_BASE,
            "source_hashes": {path: sha256(ROOT / path) for path in sources},
            "installed_fcos_path": str(installed), "installed_fcos_sha256": sha256(installed),
            "trace_target_mover": "v62_local_split_agnostic_boxes_labels_only",
            "optimization_target_mover": "historical_train_only_unchanged"}


def verify_v61() -> dict[str, object]:
    paths = {
        "failure_report.json": V61_OUT / "failure_report.json",
        "final_decision.json": V61_OUT / "final_decision.json",
        "safety_audit.json": V61_OUT / "safety_audit.json",
        "per_variant_training_log.csv": V61_OUT / "per_variant_training_log.csv",
        "runner_output.txt": V61_OUT / "runner_output.txt",
    }
    failure = json.loads(paths["failure_report.json"].read_text(encoding="utf-8"))
    final = json.loads(paths["final_decision.json"].read_text(encoding="utf-8"))
    safety = json.loads(paths["safety_audit.json"].read_text(encoding="utf-8"))
    checks = {
        "decision": final["decision"] == "V61_BLOCKED_TRAINING_OR_TRACE_INCOMPLETE",
        "failed_row": failure["failed_row_id"] == FAILED_ROW_ID,
        "failed_step": failure["failed_trace_step"] == 500,
        "steps": (failure["control_steps"], failure["intervention_steps"]) == (500, 0),
        "backward": failure["diagnostic_backward_calls"] == 44,
        "no_recovery": not failure["checkpoint_or_recovery_snapshot"],
        "log_hash": sha256(paths["per_variant_training_log.csv"]) == V61_LOG_SHA256,
        "safety": safety["optimizer_steps"] == 500 and safety["run_complete"] is False,
    }
    if not all(checks.values()):
        raise RuntimeError(f"V61 blocked evidence mismatch: {checks}")
    return {"checks": checks, "file_sha256": {name: sha256(path) for name, path in paths.items()}}


def trace_target_to_device(sample: dict[str, object], device: torch.device) -> list[dict[str, torch.Tensor]]:
    """Move RGB trace targets without making an optimization-eligibility decision."""
    target = sample["target_rgb"]
    boxes, labels = target["boxes"], target["labels"]
    if boxes.ndim != 2 or boxes.shape[-1] != 4 or labels.ndim != 1 or len(labels) != len(boxes):
        raise RuntimeError(f"Invalid trace target structure: {sample['original_row_id']}")
    return [{"boxes": boxes.to(device), "labels": labels.to(device)}]


def geometry_row(model: V57FusionSupersetDetector, sample: dict[str, object], device: torch.device) -> dict[str, object]:
    captures: list[torch.Tensor] = []
    hook = model.detector.head.regression_head.bbox_reg.register_forward_hook(
        lambda _module, _inputs, output: captures.append(output.detach()))
    detector_image = model._feature_forward(*inputs_to_device(sample, device))
    detector = model.detector
    targets = trace_target_to_device(sample, device)
    images, transformed_targets = detector.transform(list(detector_image), targets)
    features = detector.backbone(images.tensors)
    if isinstance(features, torch.Tensor):
        features = {"0": features}
    feature_list = list(features.values())
    head = detector.head(feature_list)
    hook.remove()
    if len(captures) != len(feature_list):
        raise RuntimeError("V62 bbox pre-ReLU capture mismatch")
    counts = [feature.shape[-2] * feature.shape[-1] for feature in feature_list]
    anchors_full = detector.anchor_generator(images, feature_list)
    losses = detector.compute_loss(transformed_targets, head, anchors_full, counts)
    matched = base.matched_anchor_count(transformed_targets, anchors_full, counts, detector.center_sampling_radius)
    anchors = list(anchors_full[0].split(counts))
    regressions = list(head["bbox_regression"][0].split(counts))
    logits = list(head["cls_logits"][0].split(counts))
    ctrness = list(head["bbox_ctrness"][0].split(counts))
    levels = []
    for level, (captured, post, cls, ctr, anchor) in enumerate(zip(captures, regressions, logits, ctrness, anchors)):
        pre = captured.permute(0, 2, 3, 1).reshape(-1, 4)
        decoded = detector.box_coder.decode(post, anchor)
        clipped = box_ops.clip_boxes_to_image(decoded, images.image_sizes[0])
        raw_width = decoded[:, 2] - decoded[:, 0]
        raw_height = decoded[:, 3] - decoded[:, 1]
        width = clipped[:, 2] - clipped[:, 0]
        height = clipped[:, 3] - clipped[:, 1]
        finite = torch.isfinite(clipped).all(dim=1)
        valid = finite & (width > 0) & (height > 0)
        changed = (decoded != clipped).any(dim=1)
        combined = torch.sqrt(torch.sigmoid(cls) * torch.sigmoid(ctr))
        levels.append({
            "level": level, "pre_relu": base.tensor_stats(pre), "post_relu": base.tensor_stats(post),
            "post_relu_positive_fraction": float((post > 0).float().mean().cpu()),
            "all_zero_location_fraction": float((post == 0).all(dim=1).float().mean().cpu()),
            "decoded_width_before_clip": base.tensor_stats(raw_width),
            "decoded_height_before_clip": base.tensor_stats(raw_height),
            "decoded_width_after_clip": base.tensor_stats(width),
            "decoded_height_after_clip": base.tensor_stats(height),
            "geometry_counts": {"decoded": int(decoded.shape[0]), "valid": int(valid.sum().cpu()),
                                "degenerate": int((finite & ~valid).sum().cpu()),
                                "nonfinite": int((~finite).sum().cpu()), "clipped": int(changed.sum().cpu())},
            "classification_logit": base.tensor_stats(cls), "centerness_logit": base.tensor_stats(ctr),
            "combined_score": base.tensor_stats(combined),
        })
    return {"row_id": sample["original_row_id"], "split": sample["split"],
            "target_boxes": int(targets[0]["boxes"].shape[0]), "matched_anchor_count": matched,
            "losses": {key: float(value.detach().cpu()) for key, value in losses.items()}, "levels": levels}


def optimizer_state_hash(state: dict[str, object]) -> str:
    digest = hashlib.sha256()

    def update(value) -> None:
        if isinstance(value, torch.Tensor):
            digest.update(str((tuple(value.shape), value.dtype)).encode())
            digest.update(value.detach().cpu().contiguous().numpy().tobytes())
        elif isinstance(value, dict):
            for key in sorted(value, key=lambda item: str(item)):
                digest.update(str(key).encode()); update(value[key])
        elif isinstance(value, (list, tuple)):
            for item in value: update(item)
        else:
            digest.update(repr(value).encode())

    update(state)
    return digest.hexdigest()


def log_contract(handle, path: Path) -> dict[str, object]:
    handle.flush()
    try:
        os.fsync(handle.fileno())
    except OSError:
        pass
    with path.open(encoding="utf-8", newline="") as reader:
        rows = max(0, sum(1 for _ in reader) - 1)
    return {"row_count": rows, "sha256": sha256(path)}


def rng_equal(left: dict[str, object], right: dict[str, object]) -> bool:
    return base.rng_digest(left) == base.rng_digest(right)


def atomic_recovery_snapshot(model, optimizer, completed_step: int, next_order_position: int,
                             variant: str, log_path: Path, log_info: dict[str, object],
                             trace_ledger: list[dict[str, object]], destination: Path) -> dict[str, object]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    rng = base.rng_snapshot()
    model_state = base.clone_state(model.state_dict())
    optimizer_state = optimizer.state_dict()
    payload = {
        "model_state": model_state, "optimizer_state": optimizer_state, "rng_state": rng,
        "completed_optimizer_steps": completed_step, "next_sample_order_position": next_order_position,
        "variant": variant, "source_commit": START_COMMIT, "configuration_sha256": CONFIG_HASH,
        "initialization_sha256": base.INIT_SHA256, "trace_step": completed_step,
        "training_log": log_info, "trace_ledger_completion_state": list(trace_ledger),
    }
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    with temporary.open("wb") as handle:
        torch.save(payload, handle)
        handle.flush()
        try:
            os.fsync(handle.fileno())
        except OSError:
            pass
    os.replace(temporary, destination)
    loaded = torch.load(destination, map_location="cpu", weights_only=False)
    checks = {
        "model": base.tensor_dict_fingerprint(loaded["model_state"]) == base.tensor_dict_fingerprint(model_state),
        "optimizer": optimizer_state_hash(loaded["optimizer_state"]) == optimizer_state_hash(optimizer_state),
        "rng": rng_equal(loaded["rng_state"], rng),
        "step": loaded["completed_optimizer_steps"] == completed_step,
        "next_order": loaded["next_sample_order_position"] == next_order_position,
        "variant": loaded["variant"] == variant,
        "log": loaded["training_log"] == log_info,
        "ledger": loaded["trace_ledger_completion_state"] == trace_ledger,
    }
    if not all(checks.values()):
        raise RuntimeError(f"V62 recovery snapshot round-trip failure: {checks}")
    return {"variant": variant, "trace_step": completed_step, "path_local_not_committed": str(destination),
            "bytes": destination.stat().st_size, "sha256": sha256(destination),
            "round_trip_checks": checks, "log_row_count": log_info["row_count"],
            "log_sha256": log_info["sha256"], "recovery_used": False}


def trace_state_with_recovery(model, optimizer, state_step: int, train_dataset, dev_dataset, subsets, device):
    if not _CURRENT_VARIANT or _LOG_HANDLE is None:
        raise RuntimeError("V62 recovery context is not installed")
    log_path = OUT / "per_variant_training_log.csv"
    info = log_contract(_LOG_HANDLE, log_path)
    ledger = _RECOVERY_LEDGER[_CURRENT_VARIANT]
    destination = LOCAL / "recovery" / f"{_CURRENT_VARIANT}_latest.pt"
    snapshot = atomic_recovery_snapshot(model, optimizer, state_step, state_step, _CURRENT_VARIANT,
                                        log_path, info, ledger, destination)
    ledger.append({"event": "snapshot_verified", **snapshot})
    write_json(OUT / "recovery_ledger.json", {"variants": _RECOVERY_LEDGER, "recovery_events": 0})
    result = _ORIGINAL_TRACE_STATE(model, optimizer, state_step, train_dataset, dev_dataset, subsets, device)
    ledger.append({"event": "trace_complete", "variant": _CURRENT_VARIANT, "trace_step": state_step})
    write_json(OUT / "recovery_ledger.json", {"variants": _RECOVERY_LEDGER, "recovery_events": 0})
    return result


def actual_failed_devval_sample(dataset: MMUAVFeatureAlignmentDataset) -> tuple[int, dict[str, object]]:
    for index, row in enumerate(dataset.rows):
        if row["original_row_id"] == FAILED_ROW_ID:
            return index, dataset[index]
    raise RuntimeError(f"Frozen failed row missing: {FAILED_ROW_ID}")


def verify_trace_fix() -> dict[str, object]:
    dev_manifest = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"
    dataset = MMUAVFeatureAlignmentDataset(dev_manifest, 320, validate_paths=False)
    index, sample = actual_failed_devval_sample(dataset)
    moved = trace_target_to_device(sample, torch.device("cpu"))[0]
    preserved = (torch.equal(moved["boxes"], sample["target_rgb"]["boxes"]) and
                 torch.equal(moved["labels"], sample["target_rgb"]["labels"]) and
                 moved["boxes"].dtype == sample["target_rgb"]["boxes"].dtype and
                 moved["labels"].dtype == sample["target_rgb"]["labels"].dtype)
    optimization_rejected = False
    try:
        target_to_device(sample, torch.device("cpu"))
    except RuntimeError as exc:
        optimization_rejected = "Invalid optimization sample" in str(exc)
    if not preserved or not optimization_rejected:
        raise RuntimeError("V62 trace-fix preflight failed")
    return {"failed_row_id": FAILED_ROW_ID, "devval_index": index, "trace_mover_accepted": True,
            "boxes_labels_exact": preserved, "row_identity_preserved": sample["original_row_id"] == FAILED_ROW_ID,
            "historical_optimization_helper_still_rejects": optimization_rejected,
            "coordinate_or_label_rewrite": False}


def prepare() -> None:
    configure_base()
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError("Unexpected V62 starting commit")
    if OUT.exists():
        raise RuntimeError("V62 output already exists")
    OUT.mkdir(parents=True)
    v61 = verify_v61()
    trace_fix = verify_trace_fix()
    if sha256(base.TRAIN_MANIFEST) != base.TRAIN_SHA256:
        raise RuntimeError("V62 train manifest mismatch")
    dataset = MMUAVFeatureAlignmentDataset(base.TRAIN_MANIFEST, 320, validate_paths=True)
    subsets = base.frozen_subsets()
    prefix = base.prefix_500(dataset)
    common = base.load_common_state()
    states, intervention = base.initial_states(common)
    configs = {
        VARIANTS[0]: {**base.common_config(), "name": VARIANTS[0], "initial_bbox_bias": [0.0] * 4,
                      "atomic_recovery_before_each_trace": True},
        VARIANTS[1]: {**base.common_config(), "name": VARIANTS[1], "initial_bbox_bias": [0.01] * 4,
                      "atomic_recovery_before_each_trace": True},
    }
    protected = _aggregate(protected_paths())
    protocol = {"prepared_at": base.now(), "starting_commit": START_COMMIT,
                "authorization_base": AUTHORIZATION_BASE, "v61_verification": v61,
                "trace_target_fix": trace_fix, "train_rows": len(dataset), "train_sha256": base.TRAIN_SHA256,
                "prefix": prefix, "subsets": subsets, "common_init_sha256": base.INIT_SHA256,
                "control_initial_fingerprint": base.tensor_dict_fingerprint(states[VARIANTS[0]]),
                "intervention_initial_fingerprint": base.tensor_dict_fingerprint(states[VARIANTS[1]]),
                "intervention": intervention, "configs": configs, "configuration_sha256": CONFIG_HASH,
                "run_order": list(VARIANTS), "steps_per_variant": 500, "optimizer_step_limit": 1000,
                "probe_backward_limit": 96, "protected_baseline": protected}
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v62.json", {**source_lock(), **protocol})
    write_json(OUT / "v61_blocked_evidence_verification.json", v61)
    write_json(OUT / "trace_target_transfer_fix.json", trace_fix)
    write_json(OUT / "initialization_verification.json", {
        "common_init_path_local_not_committed": str(base.COMMON_INIT), "common_init_sha256": base.INIT_SHA256,
        "tensor_count": len(common), "strict_load_both": True, "v61_trained_state_reused": False,
        "paired_difference_only_bbox_bias": True, "intervention": intervention})
    write_json(OUT / "intervention_delta.json", intervention)
    write_json(OUT / "trace_schedule.json", {"steps": list(base.TRACE_STEPS), "count": 12,
                                               "gradient_rows_per_trace": 4, "total_backward_limit": 96})
    write_json(OUT / "per_variant_config.json", configs)
    write_json(OUT / "recovery_ledger.json", {"variants": _RECOVERY_LEDGER, "recovery_events": 0})
    (OUT / "protocol.md").write_text(
        "# V62 Clean Bbox-Bias Paired Rerun\n\nV61 remains immutable. V62 uses a trace-only split-agnostic target "
        "mover and atomically verifies a local recovery snapshot before every scheduled trace.\n", encoding="utf-8")
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v62_mmuav_clean_bbox_bias_pilot.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v62_mmuav_clean_bbox_bias_pilot.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v62_mmuav_clean_bbox_bias_pilot.py --run\n",
        encoding="utf-8")
    print(json.dumps({"status": "V62_PREPARED_CPU_ONLY", "protocol": protocol}, indent=2))


def run() -> None:
    global _CURRENT_VARIANT, _LOG_HANDLE, _RECOVERY_LEDGER
    configure_base()
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    lock = json.loads((OUT / "source_lock_v62.json").read_text(encoding="utf-8"))
    if source_lock()["source_hashes"] != lock["source_hashes"]:
        raise RuntimeError("V62 source changed after CPU lock")
    if verify_v61() != protocol["v61_verification"]:
        raise RuntimeError("V61 evidence changed before V62 CUDA")
    if _aggregate(protected_paths()) != protocol["protected_baseline"]:
        raise RuntimeError("Protected evidence changed before V62 CUDA")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for V62")
    common = base.load_common_state()
    states, intervention = base.initial_states(common)
    if intervention != protocol["intervention"]:
        raise RuntimeError("V62 intervention mismatch")
    order = protocol["prefix"]["indices"]
    train_dataset = MMUAVFeatureAlignmentDataset(base.TRAIN_MANIFEST, 320, validate_paths=False)
    dev_dataset = MMUAVFeatureAlignmentDataset(
        ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt", 320,
        validate_paths=False)
    device = torch.device("cuda:0")
    log_path = OUT / "per_variant_training_log.csv"
    if log_path.exists():
        raise RuntimeError("Refusing to overwrite V62 training log")
    summaries, trace_map = {}, {}
    total_steps = 0
    _RECOVERY_LEDGER = {name: [] for name in VARIANTS}
    with log_path.open("w", encoding="utf-8", newline="") as handle:
        _LOG_HANDLE = handle
        writer = csv.DictWriter(handle, fieldnames=base.LOG_FIELDS); writer.writeheader()
        for name in VARIANTS:
            _CURRENT_VARIANT = name
            summary, traces = base.train_variant(name, states[name], order, train_dataset, dev_dataset,
                                                 protocol["subsets"], device, total_steps, writer)
            handle.flush()
            summaries[name], trace_map[name] = summary, traces
            total_steps += summary["completed_optimizer_steps"]
    _LOG_HANDLE = None
    total_backward = sum(trace["gradient_probe"]["backward_calls"] for traces in trace_map.values() for trace in traces)
    if total_steps != 1000 or total_backward != 96:
        raise RuntimeError(f"V62 budget mismatch: {total_steps}, {total_backward}")
    geometry_output = {name: [{"step": trace["step"], "geometry": trace["geometry"],
                               "devval_geometry": trace["devval_geometry"],
                               "bbox_output_parameters": trace["bbox_output_parameters"]} for trace in traces]
                       for name, traces in trace_map.items()}
    gradient_output = {name: [{"step": trace["step"], "gradient_probe": trace["gradient_probe"],
                               "isolation": trace["isolation"], "rng_hash_before": trace["rng_hash_before"],
                               "rng_hash_after": trace["rng_hash_after"]} for trace in traces]
                       for name, traces in trace_map.items()}
    classifications = {name: [{"step": trace["step"], "state": base.trace_classification(trace)} for trace in traces]
                       for name, traces in trace_map.items()}
    first_collapse = {name: next((row["step"] for row in rows if row["state"] == "EARLY_BBOX_COLLAPSE"), None)
                      for name, rows in classifications.items()}
    first_preserved = {name: next((row["step"] for row in rows if row["state"] == "GEOMETRY_AND_GRADIENT_PRESERVED"), None)
                       for name, rows in classifications.items()}
    control_collapsed = first_collapse[VARIANTS[0]] is not None
    intervention_collapsed = first_collapse[VARIANTS[1]] is not None
    intervention_step500 = classifications[VARIANTS[1]][-1]["state"]
    if control_collapsed and not intervention_collapsed and intervention_step500 == "GEOMETRY_AND_GRADIENT_PRESERVED":
        decision = "V62_CONTROL_COLLAPSE_REPRODUCED_POSITIVE_BIAS_PREVENTS_THROUGH_STEP500"
    elif control_collapsed and intervention_collapsed:
        decision = "V62_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE"
    elif control_collapsed:
        decision = "V62_CONTROL_COLLAPSE_REPRODUCED_INTERVENTION_RESULT_MIXED"
    else:
        decision = "V62_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_500_STEPS"
    checkpoints = {name: summaries[name]["checkpoint"] for name in VARIANTS}
    comparison = {"trace_classifications": classifications, "first_collapse_step": first_collapse,
                  "first_preserved_step": first_preserved, "selected_outcome": decision,
                  "single_seed_early_engineering_evidence_only": True}
    ledger = json.loads((OUT / "recovery_ledger.json").read_text(encoding="utf-8"))
    snapshots = [row for rows in ledger["variants"].values() for row in rows if row["event"] == "snapshot_verified"]
    safety = {"optimizer_steps": total_steps, "optimizer_step_limit": 1000,
              "per_variant_optimizer_steps": {name: summaries[name]["completed_optimizer_steps"] for name in VARIANTS},
              "probe_backward_calls": total_backward, "probe_backward_limit": 96,
              "verified_recovery_snapshots": len(snapshots), "recovery_events": ledger["recovery_events"],
              "all_recovery_round_trips": all(all(row["round_trip_checks"].values()) for row in snapshots),
              "all_trace_isolation_checks": all(all(trace["isolation"].values()) for traces in trace_map.values() for trace in traces),
              "all_finite": all(summary["all_finite"] for summary in summaries.values()),
              "v61_evidence_unchanged": verify_v61() == protocol["v61_verification"],
              "protected_fingerprint_unchanged": _aggregate(protected_paths()) == protocol["protected_baseline"],
              "frozen_devval_rows_per_variant": 32, "full_devval_rows": 0, "ap_ar_computed": False,
              "threshold_selection": False, "tuning": False, "checkpoint_selection": False}
    if len(snapshots) != 24 or not all((safety["all_recovery_round_trips"], safety["all_trace_isolation_checks"],
                                       safety["v61_evidence_unchanged"], safety["protected_fingerprint_unchanged"])):
        raise RuntimeError(f"V62 safety audit failed: {safety}")
    write_json(OUT / "per_variant_trace_geometry.json", geometry_output)
    write_json(OUT / "per_variant_trace_gradient.json", gradient_output)
    write_json(OUT / "per_variant_checkpoint_metadata.json", checkpoints)
    write_json(OUT / "paired_trace_comparison.json", comparison)
    write_json(OUT / "memory_timing_summary.json", summaries)
    write_json(OUT / "safety_audit.json", safety)
    write_json(OUT / "final_decision.json", {"decision": decision, "comparison": comparison,
                                               "safety": safety, "checkpoint_metadata": checkpoints})
    (OUT / "handoff.md").write_text(
        f"# V62 Handoff\n\nDecision: `{decision}`. This is single-seed early engineering evidence only; no AP/AR "
        "or full training was authorized.\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "first_collapse": first_collapse,
                      "first_preserved": first_preserved, "safety": safety}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only", action="store_true")
    group.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.prepare_only:
        prepare()
    else:
        run()


configure_base()


if __name__ == "__main__":
    try:
        main()
    except torch.OutOfMemoryError as exc:
        raise SystemExit(f"V62_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY: {exc}")
