"""Run the frozen V63 paired FCOS bbox-activation rescue pilot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torchvision.models.detection import fcos as fcos_module
from torchvision.ops import boxes as box_ops


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.v63_bbox_activation_detector import V63BBoxActivationDetector
from rarepdet.tools import run_v61_mmuav_bbox_bias_pilot as base
from rarepdet.tools import run_v62_mmuav_clean_bbox_bias_pilot as v62
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import (
    configure_seed,
    gradient_norm,
    inputs_to_device,
    target_to_device,
)


OUT = ROOT / "runs/v63_mmuav_paired_bbox_activation_rescue"
LOCAL = Path(r"D:\MM-UAV_v63_local")
START_COMMIT = "08783ed02856403d5cb0171f728f6244cef4bcd6"
AUTHORIZATION_BASE = "286508ff34d4cd0ac494d803e5a146a686318f14"
V62_OUT = ROOT / "runs/v62_mmuav_clean_bbox_bias_paired_rerun"
VARIANTS = ("v63_equal_relu_control", "v63_equal_softplus_b1_t20")
ACTIVATION = {VARIANTS[0]: "relu", VARIANTS[1]: "softplus_b1_t20"}
TRACE_STEPS = (0, 1, 2, 3, 5, 10, 15, 20, 30, 50, 100, 150, 200)
STEPS_PER_VARIANT = 200
TOTAL_STEP_LIMIT = 400
PROBE_BACKWARD_LIMIT = 104
FAILED_ROW_ID = "devval:00005919"
V62_HASHES = {
    "final_decision.json": "6228e9ad27756facdf80a6aab05c44c2b69eeb2c87f8cab9e7bd275b6c2e2c0a",
    "safety_audit.json": "e844eefc263c781228815bdbba0f1b81fbbad013edd8afd0703b7154f5822b74",
    "per_variant_training_log.csv": "664128138115b74774e5e04e4e7b3429821661ec63c73fa7a6a931f451d47e40",
}
LOG_FIELDS = base.LOG_FIELDS + (
    "regression_tower_gradient_norm", "detector_head_gradient_norm",
    "bbox_weight_norm_after", "bbox_weight_min_after", "bbox_weight_max_after",
    "bbox_bias_min_after", "bbox_bias_max_after",
)
CONFIG_HASH = hashlib.sha256(json.dumps({
    **base.common_config(), "steps": 200, "trace_steps": TRACE_STEPS,
    "paired_activation": ["relu", "softplus(beta=1.0,threshold=20.0)"],
    "atomic_recovery": True,
}, sort_keys=True).encode()).hexdigest()

_CURRENT_VARIANT = ""
_LOG_HANDLE = None
_RECOVERY_LEDGER: dict[str, list[dict[str, object]]] = {name: [] for name in VARIANTS}


def sha256(path: Path) -> str:
    return base.sha256(path)


def write_json(path: Path, value: object) -> None:
    base.write_json(path, value)


def git(*args: str) -> str:
    return base.git(*args)


def build_model(variant: str) -> V63BBoxActivationDetector:
    return V63BBoxActivationDetector(ACTIVATION[variant])


def protected_paths() -> list[Path]:
    fixed = {
        "rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py",
        "main.tex", "main_sivp_snjnl.tex",
    }
    selected = []
    for relative in git("ls-files").splitlines():
        historical = any(relative.startswith(f"runs/v{version}_") for version in range(40, 63))
        if relative in fixed or relative.startswith("manuscript/") or relative.startswith("submission/") or historical:
            path = ROOT / relative
            if path.is_file():
                selected.append(path)
    return selected


def protected_fingerprint() -> dict[str, object]:
    return v62._aggregate(protected_paths())


def source_lock() -> dict[str, object]:
    sources = [
        "rarepdet/tools/run_v63_mmuav_bbox_activation_rescue.py",
        "rarepdet/experimental/v63_bbox_activation_detector.py",
        "tests/test_v63_mmuav_bbox_activation_rescue.py",
        "rarepdet/tools/run_v62_mmuav_clean_bbox_bias_pilot.py",
        "rarepdet/tools/run_v61_mmuav_bbox_bias_pilot.py",
        "rarepdet/tools/run_v57_mmuav_paired_fusion.py",
        "rarepdet/experimental/v57_fusion_superset_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
    ]
    installed = Path(inspect.getsourcefile(fcos_module.FCOSRegressionHead) or "")
    lines, line = inspect.getsourcelines(fcos_module.FCOSRegressionHead.forward)
    relu_lines = [line + index for index, value in enumerate(lines) if "functional.relu(self.bbox_reg" in value]
    if len(relu_lines) != 1:
        raise RuntimeError(f"Historical FCOS ReLU source lock mismatch: {relu_lines}")
    return {
        "starting_commit": START_COMMIT, "authorization_base": AUTHORIZATION_BASE,
        "source_hashes": {path: sha256(ROOT / path) for path in sources},
        "installed_fcos_path": str(installed), "installed_fcos_sha256": sha256(installed),
        "historical_relu_line": relu_lines[0],
        "historical_relu_expression": "nn.functional.relu(self.bbox_reg(bbox_feature))",
        "softplus_expression": "F.softplus(pre_activation, beta=1.0, threshold=20.0)",
        "shared_training_inference_head": True,
    }


def verify_v62() -> dict[str, object]:
    checks = {name: sha256(V62_OUT / name) == expected for name, expected in V62_HASHES.items()}
    final = json.loads((V62_OUT / "final_decision.json").read_text(encoding="utf-8"))
    safety = json.loads((V62_OUT / "safety_audit.json").read_text(encoding="utf-8"))
    checks.update({
        "decision": final["decision"] == "V62_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE",
        "first_collapse_both_step20": set(final["comparison"]["first_collapse_step"].values()) == {20},
        "optimizer_steps": safety["optimizer_steps"] == 1000,
        "backward_calls": safety["probe_backward_calls"] == 96,
        "snapshots": safety["verified_recovery_snapshots"] == 24 and safety["recovery_events"] == 0,
        "no_full_eval": safety["full_devval_rows"] == 0 and not safety["ap_ar_computed"],
    })
    if not all(checks.values()):
        raise RuntimeError(f"V62 evidence mismatch: {checks}")
    return {"checks": checks, "file_sha256": {name: sha256(V62_OUT / name) for name in V62_HASHES}}


def initial_states() -> tuple[dict[str, dict[str, torch.Tensor]], dict[str, object]]:
    common = base.load_common_state()
    control = base.clone_state(common)
    intervention = base.clone_state(common)
    differences = [key for key in control if not torch.equal(control[key], intervention[key])]
    if differences:
        raise RuntimeError(f"V63 step-0 state mismatch: {differences[:5]}")
    fingerprint = base.tensor_dict_fingerprint(control)
    return {VARIANTS[0]: control, VARIANTS[1]: intervention}, {
        "changed_tensor_count": 0, "changed_element_count": 0,
        "state_dict_keys_identical": list(control) == list(intervention),
        "state_tensors_bit_identical": True, "state_fingerprint": fingerprint,
        "historical_bbox_bias_unchanged": control[base.BBOX_BIAS_KEY].tolist(),
        "sole_difference": "parameter-free bbox-distance activation",
        "softplus": {"beta": 1.0, "threshold": 20.0},
    }


def prefix_200(dataset: MMUAVFeatureAlignmentDataset) -> dict[str, object]:
    if sha256(base.ORDER_PATH) != base.ORDER_SHA256:
        raise RuntimeError("Historical V57 order hash mismatch")
    order = json.loads(base.ORDER_INDICES_PATH.read_text(encoding="utf-8"))
    ids = base.ORDER_PATH.read_text(encoding="utf-8").splitlines()
    if len(order) != 7187 or len(set(order)) != 7187 or len(ids) != 7187:
        raise RuntimeError("Historical V57 order structure mismatch")
    if any(dataset.rows[index]["original_row_id"] != row_id for index, row_id in zip(order, ids)):
        raise RuntimeError("Historical V57 order identity mismatch")
    indices, row_ids = order[:200], ids[:200]
    payload = ("\n".join(row_ids) + "\n").encode()
    (OUT / "train_prefix_200.txt").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (OUT / "train_prefix_200_sha256.txt").write_text(digest + "\n", encoding="utf-8")
    return {"rows": 200, "unique_rows": len(set(row_ids)), "indices": indices, "sha256": digest,
            "historical_order_sha256": base.ORDER_SHA256}


def derivative(pre: torch.Tensor, activation: str) -> torch.Tensor:
    if activation == "relu":
        return (pre > 0).to(pre.dtype)
    return torch.sigmoid(pre)


def derivative_stats(values: torch.Tensor) -> dict[str, object]:
    stats = base.tensor_stats(values)
    if values.numel() == 0:
        stats.update({"minimum": 0.0, "maximum": 0.0, "mean": 0.0, "std": 0.0,
                      "negative_count": 0, "zero_count": 0, "positive_count": 0,
                      "quantiles": {key: 0.0 for key in ("0.0", "0.01", "0.05", "0.25", "0.5", "0.75", "0.95", "0.99", "1.0")}})
    stats["exact_zero_fraction"] = float((values == 0).float().mean().cpu()) if values.numel() else 0.0
    return stats


def matched_anchor_mask(targets, anchors, counts, radius: float) -> torch.Tensor:
    target = targets[0]
    anchors_image = anchors[0]
    if target["boxes"].numel() == 0:
        return torch.zeros(len(anchors_image), dtype=torch.bool, device=anchors_image.device)
    boxes = target["boxes"]
    centers = (boxes[:, :2] + boxes[:, 2:]) / 2
    anchor_centers = (anchors_image[:, :2] + anchors_image[:, 2:]) / 2
    sizes = anchors_image[:, 2] - anchors_image[:, 0]
    pairwise = (anchor_centers[:, None, :] - centers[None, :, :]).abs().max(dim=2).values < radius * sizes[:, None]
    x, y = anchor_centers.unsqueeze(2).unbind(dim=1)
    x0, y0, x1, y1 = boxes.unsqueeze(0).unbind(dim=2)
    distances = torch.stack([x - x0, y - y0, x1 - x, y1 - y], dim=2)
    pairwise &= distances.min(dim=2).values > 0
    lower = sizes * 4
    lower[:counts[0]] = 0
    upper = sizes * 8
    upper[-counts[-1]:] = float("inf")
    maximum = distances.max(dim=2).values
    pairwise &= (maximum > lower[:, None]) & (maximum < upper[:, None])
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    scores = pairwise.float() * (1e8 - areas[None, :])
    return scores.max(dim=1).values >= 1e-5


def trace_target_to_device(sample: dict[str, object], device: torch.device):
    return v62.trace_target_to_device(sample, device)


def geometry_row(model, sample, device, activation: str) -> dict[str, object]:
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
    counts = [feature.shape[-2] * feature.shape[-1] for feature in feature_list]
    anchors_full = detector.anchor_generator(images, feature_list)
    losses = detector.compute_loss(transformed_targets, head, anchors_full, counts)
    mask = matched_anchor_mask(transformed_targets, anchors_full, counts, detector.center_sampling_radius)
    anchors = list(anchors_full[0].split(counts))
    masks = list(mask.split(counts))
    regressions = list(head["bbox_regression"][0].split(counts))
    logits = list(head["cls_logits"][0].split(counts))
    ctrness = list(head["bbox_ctrness"][0].split(counts))
    levels = []
    for level, (captured, post, cls, ctr, anchor, level_mask) in enumerate(
            zip(captures, regressions, logits, ctrness, anchors, masks)):
        pre = captured.permute(0, 2, 3, 1).reshape(-1, 4)
        local = derivative(pre, activation)
        decoded = detector.box_coder.decode(post, anchor)
        clipped = box_ops.clip_boxes_to_image(decoded, images.image_sizes[0])
        raw_width, raw_height = decoded[:, 2] - decoded[:, 0], decoded[:, 3] - decoded[:, 1]
        width, height = clipped[:, 2] - clipped[:, 0], clipped[:, 3] - clipped[:, 1]
        finite = torch.isfinite(clipped).all(dim=1)
        valid = finite & (width > 0) & (height > 0)
        levels.append({
            "level": level, "pre_activation": base.tensor_stats(pre), "post_activation": base.tensor_stats(post),
            "post_positive_fraction": float((post > 0).float().mean().cpu()),
            "all_zero_location_fraction": float((post == 0).all(dim=1).float().mean().cpu()),
            "activation_derivative_all": derivative_stats(local),
            "activation_derivative_matched": derivative_stats(local[level_mask]),
            "decoded_width_before_clip": base.tensor_stats(raw_width),
            "decoded_height_before_clip": base.tensor_stats(raw_height),
            "decoded_width_after_clip": base.tensor_stats(width),
            "decoded_height_after_clip": base.tensor_stats(height),
            "geometry_counts": {"decoded": int(decoded.shape[0]), "valid": int(valid.sum().cpu()),
                                "degenerate": int((finite & ~valid).sum().cpu()),
                                "nonfinite": int((~finite).sum().cpu()),
                                "clipped": int((decoded != clipped).any(dim=1).sum().cpu()),
                                "out_of_image": int(((decoded[:, 2] <= 0) | (decoded[:, 3] <= 0) |
                                                     (decoded[:, 0] >= images.image_sizes[0][1]) |
                                                     (decoded[:, 1] >= images.image_sizes[0][0])).sum().cpu())},
            "classification_logit": base.tensor_stats(cls), "centerness_logit": base.tensor_stats(ctr),
        })
    return {"row_id": sample["original_row_id"], "split": sample["split"],
            "target_boxes": int(targets[0]["boxes"].shape[0]), "matched_anchor_count": int(mask.sum().cpu()),
            "losses": {key: float(value.detach().cpu()) for key, value in losses.items()}, "levels": levels}


def aggregate_geometry(records: list[dict[str, object]]) -> dict[str, object]:
    result = {"rows": len(records), "row_ids": [row["row_id"] for row in records], "levels": []}
    for level in range(4):
        items = [row["levels"][level] for row in records]
        result["levels"].append({
            "level": level,
            "geometry_counts": {key: sum(item["geometry_counts"][key] for item in items)
                                for key in ("decoded", "valid", "degenerate", "nonfinite", "clipped", "out_of_image")},
            "pre_activation": {"minimum": min(item["pre_activation"]["minimum"] for item in items),
                               "maximum": max(item["pre_activation"]["maximum"] for item in items),
                               "mean": float(np.mean([item["pre_activation"]["mean"] for item in items])),
                               "std_mean": float(np.mean([item["pre_activation"]["std"] for item in items])),
                               "negative_fraction_mean": float(np.mean([item["pre_activation"]["negative_count"] /
                                                                        item["pre_activation"]["count"] for item in items])),
                               "zero_fraction_mean": float(np.mean([item["pre_activation"]["zero_count"] /
                                                                    item["pre_activation"]["count"] for item in items])),
                               "positive_fraction_mean": float(np.mean([item["pre_activation"]["positive_count"] /
                                                                        item["pre_activation"]["count"] for item in items]))},
            "pre_activation_quantile_means": {key: float(np.mean([
                item["pre_activation"]["quantiles"][key] for item in items]))
                for key in items[0]["pre_activation"]["quantiles"]},
            "post_activation_quantile_means": {key: float(np.mean([
                item["post_activation"]["quantiles"][key] for item in items]))
                for key in items[0]["post_activation"]["quantiles"]},
            "width_after_clip_quantile_means": {key: float(np.mean([
                item["decoded_width_after_clip"]["quantiles"][key] for item in items]))
                for key in items[0]["decoded_width_after_clip"]["quantiles"]},
            "height_after_clip_quantile_means": {key: float(np.mean([
                item["decoded_height_after_clip"]["quantiles"][key] for item in items]))
                for key in items[0]["decoded_height_after_clip"]["quantiles"]},
            "post_positive_fraction_mean": float(np.mean([item["post_positive_fraction"] for item in items])),
            "all_zero_location_fraction_mean": float(np.mean([item["all_zero_location_fraction"] for item in items])),
            "derivative_all_mean": float(np.mean([item["activation_derivative_all"]["mean"] for item in items])),
            "derivative_all_exact_zero_fraction_mean": float(np.mean([
                item["activation_derivative_all"]["exact_zero_fraction"] for item in items])),
            "derivative_matched_mean": float(np.mean([item["activation_derivative_matched"]["mean"] for item in items])),
            "derivative_matched_exact_zero_fraction_mean": float(np.mean([
                item["activation_derivative_matched"]["exact_zero_fraction"] for item in items])),
        })
    result["aggregate_counts"] = {key: sum(level["geometry_counts"][key] for level in result["levels"])
                                  for key in ("decoded", "valid", "degenerate", "nonfinite", "clipped", "out_of_image")}
    result["losses"] = {key: {"min": min(row["losses"][key] for row in records),
                                    "max": max(row["losses"][key] for row in records),
                                    "mean": float(np.mean([row["losses"][key] for row in records]))}
                        for key in ("classification", "bbox_regression", "bbox_ctrness")}
    matched = [row["matched_anchor_count"] for row in records]
    result["matched_anchors"] = {"min": min(matched), "max": max(matched), "sum": sum(matched),
                                  "mean": float(np.mean(matched))}
    return result


def module_grad_summary(module: torch.nn.Module) -> dict[str, object]:
    values = [parameter.grad.detach().float().flatten() for parameter in module.parameters() if parameter.grad is not None]
    if not values:
        return {"norm": 0.0, "nonzero_fraction": 0.0, "finite": True}
    flat = torch.cat(values)
    return {"norm": float(flat.double().norm().cpu()),
            "nonzero_fraction": float((flat != 0).float().mean().cpu()),
            "finite": bool(torch.isfinite(flat).all())}


def install_loss_capture(model, capture: dict[str, object]) -> None:
    original = model.detector.compute_loss
    def wrapped(targets, head_outputs, anchors, counts):
        mask = matched_anchor_mask(targets, anchors, counts, model.detector.center_sampling_radius)
        capture["matched_anchor_count"] = int(mask.sum().cpu())
        capture["matched_mask"] = mask.detach()
        return original(targets, head_outputs, anchors, counts)
    model.detector.compute_loss = wrapped


def gradient_probe(state, indices, dataset, device, variant: str) -> dict[str, object]:
    model = build_model(variant)
    model.load_state_dict(state, strict=True)
    before_parameters, before_buffers = base.parameter_hash(model), base.buffer_hash(model)
    model.to(device).train()
    capture: dict[str, object] = {}
    install_loss_capture(model, capture)
    pre_captures: list[torch.Tensor] = []
    hook = model.detector.head.regression_head.bbox_reg.register_forward_hook(
        lambda _module, _inputs, output: pre_captures.append(output.detach()))
    rows = []
    for index in indices:
        model.zero_grad(set_to_none=True); capture.clear(); pre_captures.clear()
        sample = dataset[index]
        losses = model(*inputs_to_device(sample, device), target_to_device(sample, device))
        total = sum(losses.values()); total.backward()
        pre = torch.cat([value.permute(0, 2, 3, 1).reshape(-1, 4) for value in pre_captures])
        local = derivative(pre, ACTIVATION[variant])
        mask = capture["matched_mask"]
        bbox = model.detector.head.regression_head.bbox_reg
        tower = model.detector.head.regression_head.conv
        bbox_summary, tower_summary = module_grad_summary(bbox), module_grad_summary(tower)
        rows.append({
            "index": index, "row_id": sample["original_row_id"],
            "target_box_count": int(sample["target_rgb"]["boxes"].shape[0]),
            "matched_anchor_count": int(capture["matched_anchor_count"]),
            "losses": {key: float(value.detach().cpu()) for key, value in losses.items()},
            "loss_total": float(total.detach().cpu()), "bbox_pre_activation": base.tensor_stats(pre),
            "bbox_post_activation_positive_fraction": float(((pre > 0) if ACTIVATION[variant] == "relu" else
                                                               (torch.nn.functional.softplus(pre) > 0)).float().mean().cpu()),
            "activation_derivative_all": derivative_stats(local),
            "activation_derivative_matched": derivative_stats(local[mask]),
            "bbox_weight_gradient_norm": 0.0 if bbox.weight.grad is None else float(bbox.weight.grad.double().norm().cpu()),
            "bbox_bias_gradient_norm": 0.0 if bbox.bias.grad is None else float(bbox.bias.grad.double().norm().cpu()),
            "bbox_gradient_nonzero_fraction": bbox_summary["nonzero_fraction"],
            "bbox_gradient_finite": bbox_summary["finite"],
            "regression_tower_gradient": tower_summary,
        })
    hook.remove()
    result = {"backward_calls": len(rows), "rows": rows,
              "parameters_unchanged": base.parameter_hash(model) == before_parameters,
              "parameter_hash_before": before_parameters, "parameter_hash_after": base.parameter_hash(model),
              "buffer_hash_before": before_buffers, "buffer_hash_after": base.buffer_hash(model),
              "ephemeral_buffers_changed": base.buffer_hash(model) != before_buffers}
    del model
    torch.cuda.empty_cache()
    return result


def optimizer_state_hash(state: dict[str, object]) -> str:
    return v62.optimizer_state_hash(state)


def atomic_snapshot(model, optimizer, completed_step, variant, log_path, log_info, ledger, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    rng = base.rng_snapshot()
    payload = {"model_state": base.clone_state(model.state_dict()), "optimizer_state": optimizer.state_dict(),
               "rng_state": rng, "completed_optimizer_steps": completed_step,
               "next_sample_order_position": completed_step, "variant": variant,
               "source_commit": START_COMMIT, "configuration_sha256": CONFIG_HASH,
               "initialization_sha256": base.INIT_SHA256, "trace_step": completed_step,
               "training_log": log_info, "trace_ledger_completion_state": list(ledger)}
    temporary = destination.with_suffix(".pt.tmp")
    with temporary.open("wb") as handle:
        torch.save(payload, handle); handle.flush()
        try: os.fsync(handle.fileno())
        except OSError: pass
    os.replace(temporary, destination)
    loaded = torch.load(destination, map_location="cpu", weights_only=False)
    checks = {
        "model": base.tensor_dict_fingerprint(loaded["model_state"]) == base.tensor_dict_fingerprint(payload["model_state"]),
        "optimizer": optimizer_state_hash(loaded["optimizer_state"]) == optimizer_state_hash(payload["optimizer_state"]),
        "rng": base.rng_digest(loaded["rng_state"]) == base.rng_digest(rng),
        "step": loaded["completed_optimizer_steps"] == completed_step,
        "next_order": loaded["next_sample_order_position"] == completed_step,
        "variant": loaded["variant"] == variant, "log": loaded["training_log"] == log_info,
        "ledger": loaded["trace_ledger_completion_state"] == ledger,
    }
    if not all(checks.values()):
        raise RuntimeError(f"V63 recovery round-trip failure: {checks}")
    return {"variant": variant, "trace_step": completed_step, "path_local_not_committed": str(destination),
            "bytes": destination.stat().st_size, "sha256": sha256(destination),
            "round_trip_checks": checks, "log_row_count": log_info["row_count"],
            "log_sha256": log_info["sha256"], "recovery_used": False}


def trace_state(model, optimizer, step, train_dataset, dev_dataset, subsets, device, variant):
    if _LOG_HANDLE is None:
        raise RuntimeError("V63 log/recovery context missing")
    log_path = OUT / "per_variant_training_log.csv"
    log_info = v62.log_contract(_LOG_HANDLE, log_path)
    ledger = _RECOVERY_LEDGER[variant]
    snapshot = atomic_snapshot(model, optimizer, step, variant, log_path, log_info, ledger,
                               LOCAL / "recovery" / f"{variant}_latest.pt")
    ledger.append({"event": "snapshot_verified", **snapshot})
    write_json(OUT / "recovery_ledger.json", {"variants": _RECOVERY_LEDGER, "recovery_events": 0})
    parameter_before, buffer_before = base.parameter_hash(model), base.buffer_hash(model)
    optimizer_before = base.optimizer_hash(optimizer)
    rng_before = base.rng_snapshot(); rng_hash = base.rng_digest(rng_before)
    was_training = model.training; model.eval()
    with torch.no_grad():
        train_records = [geometry_row(model, train_dataset[index], device, ACTIVATION[variant])
                         for index in subsets["train_indices"]]
        geometry = aggregate_geometry(train_records)
        dev_geometry = None
        if step == 200:
            dev_records = [geometry_row(model, dev_dataset[index], device, ACTIVATION[variant])
                           for index in subsets["devval_indices"]]
            dev_geometry = aggregate_geometry(dev_records)
    if was_training: model.train()
    state = base.clone_state(model.state_dict())
    probe = gradient_probe(state, subsets["gradient_indices"], train_dataset, device, variant)
    base.restore_rng(rng_before)
    unchanged = {"training_parameters": base.parameter_hash(model) == parameter_before,
                 "training_buffers": base.buffer_hash(model) == buffer_before,
                 "optimizer": base.optimizer_hash(optimizer) == optimizer_before,
                 "rng": base.rng_digest(base.rng_snapshot()) == rng_hash}
    if not all(unchanged.values()):
        raise RuntimeError(f"V63 trace mutated persistent state at step {step}: {unchanged}")
    bbox = model.detector.head.regression_head.bbox_reg
    parameters = {"weight": base.tensor_stats(bbox.weight, False),
                  "weight_norm": float(bbox.weight.detach().norm().cpu()),
                  "bias": base.tensor_stats(bbox.bias, False), "bias_values": bbox.bias.detach().cpu().tolist(),
                  "bias_norm": float(bbox.bias.detach().norm().cpu())}
    result = {"step": step, "geometry": geometry, "devval_geometry": dev_geometry,
              "gradient_probe": probe, "bbox_output_parameters": parameters,
              "isolation": unchanged, "rng_hash_before": rng_hash,
              "rng_hash_after": base.rng_digest(base.rng_snapshot())}
    ledger.append({"event": "trace_complete", "variant": variant, "trace_step": step})
    write_json(OUT / "recovery_ledger.json", {"variants": _RECOVERY_LEDGER, "recovery_events": 0})
    return result


def checkpoint_path(variant: str) -> Path:
    return LOCAL / f"{variant}_final_step200.pt"


def train_variant(name, initial, order, train_dataset, dev_dataset, subsets, device, total_before, writer):
    if total_before + STEPS_PER_VARIANT > TOTAL_STEP_LIMIT:
        raise RuntimeError("V63 optimizer-step limit exceeded")
    configure_seed(0)
    model = build_model(name).to(device)
    model.load_state_dict(initial, strict=True)
    loaded = {key: value.detach().cpu() for key, value in model.state_dict().items()}
    if base.tensor_dict_fingerprint(loaded) != base.tensor_dict_fingerprint(initial):
        raise RuntimeError(f"Initial state mismatch: {name}")
    scorer_initial = base.clone_state(model.feature_scaffold.reliability_scorer.state_dict())
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    capture: dict[str, object] = {}; install_loss_capture(model, capture)
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    traces = [trace_state(model, optimizer, 0, train_dataset, dev_dataset, subsets, device, name)]
    completed = 0; step_times = []; started_variant = time.perf_counter(); previous_end = started_variant
    for expected_step, index in enumerate(order, 1):
        if completed >= STEPS_PER_VARIANT or total_before + completed >= TOTAL_STEP_LIMIT:
            raise RuntimeError("V63 optimizer-step guard exceeded")
        started = time.perf_counter(); sample = train_dataset[index]; data_done = time.perf_counter()
        inputs, targets = inputs_to_device(sample, device), target_to_device(sample, device)
        optimizer.zero_grad(set_to_none=True); capture.clear(); forward_started = time.perf_counter()
        losses = model(*inputs, targets); total = sum(losses.values())
        torch.cuda.synchronize(); forward_done = time.perf_counter()
        if not losses or not all(torch.isfinite(value).all() for value in losses.values()):
            raise RuntimeError(f"Non-finite loss: {name} step {expected_step}")
        total.backward(); torch.cuda.synchronize(); backward_done = time.perf_counter()
        global_norm, global_finite = gradient_norm(model.parameters())
        bbox = model.detector.head.regression_head.bbox_reg
        bbox_summary = module_grad_summary(bbox)
        tower_summary = module_grad_summary(model.detector.head.regression_head.conv)
        head_summary = module_grad_summary(model.detector.head)
        weight_grad = 0.0 if bbox.weight.grad is None else float(bbox.weight.grad.double().norm().cpu())
        bias_grad = 0.0 if bbox.bias.grad is None else float(bbox.bias.grad.double().norm().cpu())
        scorer_has_gradient = any(parameter.grad is not None for parameter in model.feature_scaffold.reliability_scorer.parameters())
        if scorer_has_gradient or not global_finite or not all((bbox_summary["finite"], tower_summary["finite"], head_summary["finite"])):
            raise RuntimeError(f"Gradient/scorer contract failure: {name} step {expected_step}")
        optimizer.step(); completed += 1
        if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
            raise RuntimeError(f"Non-finite parameter: {name} step {expected_step}")
        torch.cuda.synchronize(); optimizer_done = time.perf_counter()
        values = {key: float(value.detach().cpu()) for key, value in losses.items()}
        bias_values = bbox.bias.detach().cpu().tolist(); weight = bbox.weight.detach()
        row = {"variant": name, "step": completed, "original_row_id": sample["original_row_id"],
               "target_box_count": int(sample["target_rgb"]["boxes"].shape[0]),
               "valid_target_count": int(((sample["target_rgb"]["boxes"][:, 2:] - sample["target_rgb"]["boxes"][:, :2]) > 0).all(dim=1).sum()),
               "matched_anchor_count": int(capture["matched_anchor_count"]), "loss_total": float(total.detach().cpu()),
               "loss_classifier": values["classification"], "loss_box_reg": values["bbox_regression"],
               "loss_centerness": values["bbox_ctrness"], "learning_rate": 1e-4,
               "global_gradient_norm": global_norm, "bbox_weight_gradient_norm": weight_grad,
               "bbox_bias_gradient_norm": bias_grad, "bbox_gradient_nonzero_fraction": bbox_summary["nonzero_fraction"],
               "bbox_bias_0": bias_values[0], "bbox_bias_1": bias_values[1],
               "bbox_bias_2": bias_values[2], "bbox_bias_3": bias_values[3], "finite": True,
               "cuda_allocated_bytes": torch.cuda.memory_allocated(), "cuda_reserved_bytes": torch.cuda.memory_reserved(),
               "data_time_sec": data_done - previous_end, "forward_time_sec": forward_done - forward_started,
               "backward_time_sec": backward_done - forward_done, "optimizer_time_sec": optimizer_done - backward_done,
               "step_time_sec": optimizer_done - started, "regression_tower_gradient_norm": tower_summary["norm"],
               "detector_head_gradient_norm": head_summary["norm"], "bbox_weight_norm_after": float(weight.norm().cpu()),
               "bbox_weight_min_after": float(weight.min().cpu()), "bbox_weight_max_after": float(weight.max().cpu()),
               "bbox_bias_min_after": min(bias_values), "bbox_bias_max_after": max(bias_values)}
        writer.writerow(row); step_times.append(row["step_time_sec"])
        if completed in TRACE_STEPS:
            traces.append(trace_state(model, optimizer, completed, train_dataset, dev_dataset, subsets, device, name))
            print(f"V63_TRACE_COMPLETE variant={name} step={completed} valid={traces[-1]['geometry']['aggregate_counts']['valid']}", flush=True)
        previous_end = optimizer_done
    if completed != 200 or [trace["step"] for trace in traces] != list(TRACE_STEPS):
        raise RuntimeError(f"Incomplete V63 trace/training: {name}")
    scorer_final = model.feature_scaffold.reliability_scorer.state_dict()
    if not all(torch.equal(scorer_final[key].detach().cpu(), value) for key, value in scorer_initial.items()):
        raise RuntimeError(f"Dormant scorer changed: {name}")
    LOCAL.mkdir(parents=True, exist_ok=True); checkpoint = checkpoint_path(name)
    if checkpoint.exists():
        raise RuntimeError(f"Refusing to overwrite V63 checkpoint: {checkpoint}")
    torch.save({"model_state": model.state_dict(), "variant": name, "completed_optimizer_steps": completed,
                "common_init_sha256": base.INIT_SHA256,
                "prefix_sha256": (OUT / "train_prefix_200_sha256.txt").read_text().strip()}, checkpoint)
    metadata = {"path_local_not_committed": str(checkpoint), "sha256": sha256(checkpoint),
                "bytes": checkpoint.stat().st_size, "completed_optimizer_steps": completed,
                "selection_metric": None, "common_init_sha256": base.INIT_SHA256,
                "final_state_fingerprint": base.tensor_dict_fingerprint({key: value.detach().cpu() for key, value in model.state_dict().items()})}
    summary = {"variant": name, "completed_optimizer_steps": completed, "all_finite": True,
               "elapsed_seconds": time.perf_counter() - started_variant,
               "step_time_mean_sec": float(np.mean(step_times)), "step_time_min_sec": min(step_times),
               "step_time_max_sec": max(step_times), "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
               "peak_reserved_bytes": torch.cuda.max_memory_reserved(), "dormant_scorer_unchanged": True,
               "checkpoint": metadata}
    del optimizer, model; torch.cuda.empty_cache()
    return summary, traces


def classify(trace: dict[str, object]) -> str:
    valid = trace["geometry"]["aggregate_counts"]["valid"]
    rows = trace["gradient_probe"]["rows"]
    all_zero = all(row["bbox_weight_gradient_norm"] == 0.0 and row["bbox_bias_gradient_norm"] == 0.0 for row in rows)
    any_nonzero = any(row["bbox_weight_gradient_norm"] > 0.0 or row["bbox_bias_gradient_norm"] > 0.0 for row in rows)
    if valid == 0 and all_zero: return "EARLY_BBOX_COLLAPSE"
    if valid > 0 and any_nonzero: return "GEOMETRY_AND_GRADIENT_PRESERVED"
    return "NEITHER_PREREGISTERED_STATE"


def actual_devval_gate() -> dict[str, object]:
    manifest = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"
    dataset = MMUAVFeatureAlignmentDataset(manifest, 320, validate_paths=False)
    index, sample = v62.actual_failed_devval_sample(dataset)
    moved = trace_target_to_device(sample, torch.device("cpu"))[0]
    rejected = False
    try: target_to_device(sample, torch.device("cpu"))
    except RuntimeError as exc: rejected = "Invalid optimization sample" in str(exc)
    exact = torch.equal(moved["boxes"], sample["target_rgb"]["boxes"]) and torch.equal(moved["labels"], sample["target_rgb"]["labels"])
    if sample["original_row_id"] != FAILED_ROW_ID or not exact or not rejected:
        raise RuntimeError("V63 actual devval target gate failed")
    return {"row_id": FAILED_ROW_ID, "index": index, "trace_path_exact": exact,
            "historical_optimization_guard_rejects": rejected}


def step0_identity(states, dataset, first_index) -> dict[str, object]:
    configure_seed(0)
    models = [build_model(name) for name in VARIANTS]
    for model, name in zip(models, VARIANTS): model.load_state_dict(states[name], strict=True); model.eval()
    sample = dataset[first_index]; outputs = []
    with torch.no_grad():
        for model in models:
            pre: list[torch.Tensor] = []
            hook = model.detector.head.regression_head.bbox_reg.register_forward_hook(
                lambda _module, _inputs, output, store=pre: store.append(output.detach().clone()))
            detector_image = model._feature_forward(*inputs_to_device(sample, torch.device("cpu")))
            images, _ = model.detector.transform(list(detector_image), None)
            features = model.detector.backbone(images.tensors)
            feature_list = list(features.values()) if isinstance(features, dict) else [features]
            head = model.detector.head(feature_list); hook.remove()
            outputs.append({"pre": pre, "cls": head["cls_logits"], "ctr": head["bbox_ctrness"],
                            "post": head["bbox_regression"], "fused": model.last_feature_outputs["fused"].clone()})
    checks = {"state": all(torch.equal(states[VARIANTS[0]][key], states[VARIANTS[1]][key]) for key in states[VARIANTS[0]]),
              "pre_activation": all(torch.equal(a, b) for a, b in zip(outputs[0]["pre"], outputs[1]["pre"])),
              "classification": torch.equal(outputs[0]["cls"], outputs[1]["cls"]),
              "centerness": torch.equal(outputs[0]["ctr"], outputs[1]["ctr"]),
              "fused_features": torch.equal(outputs[0]["fused"], outputs[1]["fused"]),
              "post_activation_differs": not torch.equal(outputs[0]["post"], outputs[1]["post"])}
    if not all(checks.values()): raise RuntimeError(f"V63 step-0 paired identity failed: {checks}")
    return {"row_id": sample["original_row_id"], "checks": checks,
            "pre_activation_tensor_count": len(outputs[0]["pre"]),
            "state_fingerprint": base.tensor_dict_fingerprint(states[VARIANTS[0]])}


def prepare() -> None:
    if git("rev-parse", "HEAD") != START_COMMIT: raise RuntimeError("Unexpected V63 starting commit")
    if (OUT / "per_variant_training_log.csv").exists(): raise RuntimeError("V63 CUDA output already exists")
    OUT.mkdir(parents=True, exist_ok=True)
    v62_verification = verify_v62()
    if sha256(base.TRAIN_MANIFEST) != base.TRAIN_SHA256: raise RuntimeError("Train manifest mismatch")
    dataset = MMUAVFeatureAlignmentDataset(base.TRAIN_MANIFEST, 320, validate_paths=True)
    subsets = base.frozen_subsets(); prefix = prefix_200(dataset); states, intervention = initial_states()
    identity = step0_identity(states, dataset, prefix["indices"][0]); devval_gate = actual_devval_gate()
    configs = {name: {**base.common_config(), "name": name, "steps": 200,
                      "trace_steps": list(TRACE_STEPS), "bbox_activation": ACTIVATION[name],
                      "bbox_bias": states[name][base.BBOX_BIAS_KEY].tolist(),
                      "atomic_recovery_before_each_trace": True} for name in VARIANTS}
    protocol = {"prepared_at": base.now(), "starting_commit": START_COMMIT,
                "authorization_base": AUTHORIZATION_BASE, "v62_verification": v62_verification,
                "train_rows": len(dataset), "train_sha256": base.TRAIN_SHA256, "prefix": prefix,
                "subsets": subsets, "common_init_sha256": base.INIT_SHA256,
                "initialization": intervention, "step0_identity": identity, "actual_devval_gate": devval_gate,
                "configs": configs, "configuration_sha256": CONFIG_HASH, "run_order": list(VARIANTS),
                "steps_per_variant": 200, "optimizer_step_limit": 400, "probe_backward_limit": 104,
                "protected_baseline": protected_fingerprint()}
    write_json(OUT / "protocol.json", protocol); write_json(OUT / "source_lock_v63.json", source_lock())
    write_json(OUT / "v62_evidence_verification.json", v62_verification)
    write_json(OUT / "initialization_verification.json", {"common_init_path_local_not_committed": str(base.COMMON_INIT),
               "common_init_sha256": base.INIT_SHA256, **intervention, "step0_identity": identity})
    write_json(OUT / "activation_intervention.json", {"control": "native torchvision ReLU",
               "intervention": "softplus", "beta": 1.0, "threshold": 20.0,
               "parameter_free": True, "same_regression_head_training_and_inference": True})
    write_json(OUT / "trace_schedule.json", {"steps": list(TRACE_STEPS), "count": 13,
               "gradient_rows_per_trace": 4, "total_backward_limit": 104})
    write_json(OUT / "per_variant_config.json", configs)
    write_json(OUT / "recovery_ledger.json", {"variants": _RECOVERY_LEDGER, "recovery_events": 0})
    (OUT / "protocol.md").write_text("# V63 Paired Bbox-Activation Rescue\n\nThe sole paired difference is native FCOS ReLU versus parameter-free Softplus(beta=1.0, threshold=20.0).\n", encoding="utf-8")
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v63_mmuav_bbox_activation_rescue.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v63_mmuav_bbox_activation_rescue.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v63_mmuav_bbox_activation_rescue.py --run\n",
        encoding="utf-8")
    print(json.dumps({"status": "V63_PREPARED_CPU_ONLY", "protocol": protocol}, indent=2))


def run() -> None:
    global _CURRENT_VARIANT, _LOG_HANDLE, _RECOVERY_LEDGER
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    lock = json.loads((OUT / "source_lock_v63.json").read_text(encoding="utf-8"))
    if source_lock() != lock: raise RuntimeError("V63 source changed after CPU lock")
    if verify_v62() != protocol["v62_verification"]: raise RuntimeError("V62 evidence changed before CUDA")
    if protected_fingerprint() != protocol["protected_baseline"]: raise RuntimeError("Protected evidence changed before CUDA")
    if not torch.cuda.is_available(): raise RuntimeError("CUDA unavailable for V63")
    states, intervention = initial_states()
    if intervention != protocol["initialization"]: raise RuntimeError("V63 paired initialization changed")
    order = protocol["prefix"]["indices"]
    if len(order) != 200 or len(set(order)) != 200: raise RuntimeError("V63 prefix invalid")
    train_dataset = MMUAVFeatureAlignmentDataset(base.TRAIN_MANIFEST, 320, validate_paths=False)
    dev_dataset = MMUAVFeatureAlignmentDataset(ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt", 320, validate_paths=False)
    device = torch.device("cuda:0"); log_path = OUT / "per_variant_training_log.csv"
    if log_path.exists(): raise RuntimeError("Refusing to overwrite V63 training log")
    summaries, trace_map, total_steps = {}, {}, 0
    _RECOVERY_LEDGER = {name: [] for name in VARIANTS}
    with log_path.open("w", encoding="utf-8", newline="") as handle:
        _LOG_HANDLE = handle; writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS); writer.writeheader()
        for name in VARIANTS:
            _CURRENT_VARIANT = name
            summary, traces = train_variant(name, states[name], order, train_dataset, dev_dataset,
                                             protocol["subsets"], device, total_steps, writer)
            handle.flush(); summaries[name], trace_map[name] = summary, traces
            total_steps += summary["completed_optimizer_steps"]
    _LOG_HANDLE = None
    total_backward = sum(trace["gradient_probe"]["backward_calls"] for traces in trace_map.values() for trace in traces)
    if total_steps != 400 or total_backward != 104: raise RuntimeError(f"V63 budget mismatch: {total_steps}, {total_backward}")
    classifications = {name: [{"step": trace["step"], "state": classify(trace)} for trace in traces]
                       for name, traces in trace_map.items()}
    first_collapse = {name: next((row["step"] for row in rows if row["state"] == "EARLY_BBOX_COLLAPSE"), None)
                      for name, rows in classifications.items()}
    first_preserved = {name: next((row["step"] for row in rows if row["state"] == "GEOMETRY_AND_GRADIENT_PRESERVED"), None)
                       for name, rows in classifications.items()}
    control_collapse, softplus_collapse = first_collapse[VARIANTS[0]], first_collapse[VARIANTS[1]]
    if control_collapse is None:
        decision = "V63_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS"
    elif softplus_collapse is not None:
        decision = "V63_RELU_AND_SOFTPLUS_BOTH_COLLAPSE"
    elif control_collapse <= 50 and classifications[VARIANTS[1]][-1]["state"] == "GEOMETRY_AND_GRADIENT_PRESERVED":
        decision = "V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200"
    else:
        decision = "V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_MIXED"
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
              "v62_evidence_unchanged": verify_v62() == protocol["v62_verification"],
              "protected_fingerprint_unchanged": protected_fingerprint() == protocol["protected_baseline"],
              "frozen_devval_rows_per_variant": 32, "full_devval_rows": 0, "ap_ar_computed": False,
              "threshold_selection": False, "tuning": False, "checkpoint_selection": False}
    if len(snapshots) != 26 or not all((safety["all_recovery_round_trips"], safety["all_trace_isolation_checks"],
                                       safety["v62_evidence_unchanged"], safety["protected_fingerprint_unchanged"],
                                       safety["all_finite"])):
        raise RuntimeError(f"V63 safety audit failed: {safety}")
    comparison = {"trace_classifications": classifications, "first_collapse_step": first_collapse,
                  "first_preserved_step": first_preserved, "selected_outcome": decision,
                  "single_seed_early_mechanistic_evidence_only": True}
    write_json(OUT / "per_variant_trace_geometry.json", geometry_output)
    write_json(OUT / "per_variant_trace_gradient.json", gradient_output)
    write_json(OUT / "activation_derivative_summary.json", derivative_summary)
    write_json(OUT / "per_variant_checkpoint_metadata.json", {name: summaries[name]["checkpoint"] for name in VARIANTS})
    write_json(OUT / "paired_trace_comparison.json", comparison)
    write_json(OUT / "memory_timing_summary.json", summaries); write_json(OUT / "safety_audit.json", safety)
    write_json(OUT / "final_decision.json", {"decision": decision, "comparison": comparison, "safety": safety,
               "checkpoint_metadata": {name: summaries[name]["checkpoint"] for name in VARIANTS}})
    (OUT / "handoff.md").write_text(f"# V63 Handoff\n\nDecision: `{decision}`. Single-seed early mechanistic evidence only; no full run or AP/AR was authorized.\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "first_collapse": first_collapse,
                      "first_preserved": first_preserved, "safety": safety}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(); group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only", action="store_true"); group.add_argument("--run", action="store_true")
    args = parser.parse_args(); prepare() if args.prepare_only else run()


if __name__ == "__main__":
    try: main()
    except torch.OutOfMemoryError as exc:
        raise SystemExit(f"V63_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY: {exc}")
