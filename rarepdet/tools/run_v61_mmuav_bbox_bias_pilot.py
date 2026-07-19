"""Run the frozen V61 paired early bbox-collapse prevention pilot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import math
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import torch
from torchvision.models.detection import fcos as fcos_module
from torchvision.ops import boxes as box_ops


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.v57_fusion_superset_detector import V57FusionSupersetDetector
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import (
    configure_seed,
    gradient_norm,
    inputs_to_device,
    target_to_device,
)
from rarepdet.tools.run_v60_bbox_collapse_provenance_audit import (
    buffer_hash,
    compact_quantiles,
    parameter_hash,
    tensor_dict_fingerprint,
    tensor_stats,
)


OUT = ROOT / "runs/v61_mmuav_early_bbox_collapse_prevention"
LOCAL = Path(r"D:\MM-UAV_v61_local")
START_COMMIT = "ac036f9723b5c8f82b6817e41a742d3125ad04b5"
AUTHORIZATION_BASE = "8e3ac7151c9b70edd4631cfd6aabfdc359a1cc95"
TRAIN_MANIFEST = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt"
ORDER_PATH = ROOT / "runs/v57_mmuav_paired_fusion_ablation/shared_sample_order.txt"
ORDER_INDICES_PATH = ROOT / "runs/v57_mmuav_paired_fusion_ablation/shared_sample_indices.json"
COMMON_INIT = Path(r"D:\MM-UAV_v57_local\common_seed0_superset_init.pt")
V60_OUT = ROOT / "runs/v60_mmuav_bbox_collapse_provenance_audit"
TRAIN_SHA256 = "e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a"
ORDER_SHA256 = "27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b"
INIT_SHA256 = "846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9"
TRAIN_SUBSET_SHA256 = "d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c"
GRADIENT_SUBSET_SHA256 = "bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166"
DEVVAL_SUBSET_SHA256 = "d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee"
BBOX_BIAS_KEY = "detector.head.regression_head.bbox_reg.bias"
VARIANTS = ("v57_equal_control_instrumented", "v57_equal_bbox_bias_p001")
TRACE_STEPS = (0, 1, 2, 5, 10, 20, 50, 100, 200, 300, 400, 500)
STEPS_PER_VARIANT = 500
TOTAL_STEP_LIMIT = 1000
PROBE_BACKWARD_LIMIT = 96
LOG_FIELDS = (
    "variant", "step", "original_row_id", "target_box_count", "valid_target_count", "matched_anchor_count",
    "loss_total", "loss_classifier", "loss_box_reg", "loss_centerness", "learning_rate",
    "global_gradient_norm", "bbox_weight_gradient_norm", "bbox_bias_gradient_norm",
    "bbox_gradient_nonzero_fraction", "bbox_bias_0", "bbox_bias_1", "bbox_bias_2", "bbox_bias_3",
    "finite", "cuda_allocated_bytes", "cuda_reserved_bytes", "data_time_sec", "forward_time_sec",
    "backward_time_sec", "optimizer_time_sec", "step_time_sec",
)


def now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def protected_paths() -> list[Path]:
    fixed = {
        "rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py",
        "main.tex", "main_sivp_snjnl.tex",
    }
    selected = []
    for relative in git("ls-files").splitlines():
        historical = any(relative.startswith(f"runs/v{version}_") for version in range(40, 61))
        if relative in fixed or relative.startswith("manuscript/") or relative.startswith("submission/") or historical:
            path = ROOT / relative
            if path.is_file():
                selected.append(path)
    return selected


def aggregate_fingerprint(paths: list[Path]) -> dict[str, object]:
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
        "rarepdet/tools/run_v61_mmuav_bbox_bias_pilot.py",
        "tests/test_v61_mmuav_bbox_bias_pilot.py",
        "rarepdet/tools/run_v57_mmuav_paired_fusion.py",
        "rarepdet/tools/run_v60_bbox_collapse_provenance_audit.py",
        "rarepdet/experimental/v57_fusion_superset_detector.py",
        "rarepdet/experimental/mmuav_feature_alignment_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
    ]
    installed = Path(inspect.getsourcefile(fcos_module.FCOS) or "")
    return {
        "starting_commit": START_COMMIT,
        "authorization_base_commit": AUTHORIZATION_BASE,
        "source_hashes": {path: sha256(ROOT / path) for path in sources},
        "installed_fcos_path": str(installed),
        "installed_fcos_sha256": sha256(installed),
        "bbox_activation": "torch.nn.functional.relu",
        "bbox_loss": "generalized_box_iou_loss",
    }


def verify_v60() -> dict[str, object]:
    final_path = V60_OUT / "final_decision.json"
    init_path = V60_OUT / "initialization_reconstruction.json"
    safety_path = V60_OUT / "safety_audit.json"
    final = json.loads(final_path.read_text(encoding="utf-8"))
    initialization = json.loads(init_path.read_text(encoding="utf-8"))
    safety = json.loads(safety_path.read_text(encoding="utf-8"))
    checks = {
        "decision": final["decision"] == "V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_CAUSE_UNRESOLVED",
        "classification": final["root_cause"]["primary_classification"] == "V57_BBOX_COLLAPSE_PROVENANCE_UNRESOLVED",
        "initial_usable": final["root_cause"]["initial_geometry_usable"] is True,
        "initial_bbox_identical": initialization["initial_bbox_head_v55_v57_bit_identical"] is True,
        "zero_optimizer": safety["optimizer_constructions"] == 0 and safety["optimizer_steps"] == 0,
        "twenty_backward": safety["backward_calls"] == 20,
        "immutable": safety["all_parameters_unchanged"] and safety["all_checkpoints_unchanged"],
    }
    if not all(checks.values()):
        raise RuntimeError(f"V60 evidence mismatch: {checks}")
    return {"checks": checks, "file_sha256": {
        "final_decision.json": sha256(final_path),
        "initialization_reconstruction.json": sha256(init_path),
        "safety_audit.json": sha256(safety_path),
    }}


def load_common_state() -> dict[str, torch.Tensor]:
    if not COMMON_INIT.is_file() or sha256(COMMON_INIT) != INIT_SHA256:
        raise RuntimeError("V57 common initialization contract mismatch")
    payload = torch.load(COMMON_INIT, map_location="cpu", weights_only=False)
    state = payload["state_dict"]
    if len(state) != 791 or not all(torch.isfinite(value).all() for value in state.values()):
        raise RuntimeError("V57 common initialization tensor contract mismatch")
    return state


def clone_state(state: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    return {name: value.detach().cpu().clone() for name, value in state.items()}


def initial_states(common: dict[str, torch.Tensor]) -> tuple[dict[str, dict[str, torch.Tensor]], dict[str, object]]:
    control = clone_state(common)
    intervention = clone_state(common)
    bias = intervention[BBOX_BIAS_KEY]
    before = bias.clone()
    if tuple(bias.shape) != (4,) or not torch.equal(bias, torch.zeros_like(bias)):
        raise RuntimeError("Historical bbox output bias is not exact four-element zero")
    bias.fill_(0.01)
    differences = [name for name in control if not torch.equal(control[name], intervention[name])]
    if differences != [BBOX_BIAS_KEY]:
        raise RuntimeError(f"Unexpected initial paired differences: {differences}")
    changed_elements = int((control[BBOX_BIAS_KEY] != intervention[BBOX_BIAS_KEY]).sum())
    if changed_elements != 4 or not torch.equal(bias, torch.full_like(bias, 0.01)):
        raise RuntimeError("V61 intervention is not exact +0.01 on four elements")
    states = {VARIANTS[0]: control, VARIANTS[1]: intervention}
    delta = {
        "parameter_name": BBOX_BIAS_KEY,
        "before": before.tolist(), "after": bias.tolist(),
        "delta": (bias - before).tolist(), "changed_tensor_count": 1,
        "changed_element_count": changed_elements,
        "control_state_fingerprint": tensor_dict_fingerprint(control),
        "intervention_state_fingerprint": tensor_dict_fingerprint(intervention),
        "all_other_tensors_bit_identical": True,
        "bias_sweep": False,
    }
    return states, delta


def frozen_subsets() -> dict[str, object]:
    train_indices = json.loads((V60_OUT / "train_audit_subset_indices.json").read_text(encoding="utf-8"))
    gradient_indices = json.loads((V60_OUT / "gradient_probe_subset_indices.json").read_text(encoding="utf-8"))
    devval_indices = json.loads(
        (ROOT / "runs/v59_mmuav_streaming_zero_detection_diagnostic/detailed_subset_indices.json").read_text(
            encoding="utf-8"))
    checks = {
        "train": (V60_OUT / "train_audit_subset_sha256.txt").read_text().strip() == TRAIN_SUBSET_SHA256,
        "gradient": (V60_OUT / "gradient_probe_subset_sha256.txt").read_text().strip() == GRADIENT_SUBSET_SHA256,
        "gradient_first_four": gradient_indices == train_indices[:4],
        "devval_compact_hash": hashlib.sha256(
            (json.dumps(devval_indices, separators=(",", ":")) + "\n").encode()).hexdigest() == DEVVAL_SUBSET_SHA256,
    }
    if not all(checks.values()) or (len(train_indices), len(gradient_indices), len(devval_indices)) != (32, 4, 32):
        raise RuntimeError(f"Frozen subset mismatch: {checks}")
    return {"train_indices": train_indices, "gradient_indices": gradient_indices,
            "devval_indices": devval_indices, "checks": checks,
            "train_sha256": TRAIN_SUBSET_SHA256, "gradient_sha256": GRADIENT_SUBSET_SHA256,
            "devval_sha256": DEVVAL_SUBSET_SHA256}


def prefix_500(dataset: MMUAVFeatureAlignmentDataset) -> dict[str, object]:
    if sha256(ORDER_PATH) != ORDER_SHA256:
        raise RuntimeError("Historical V57 order hash mismatch")
    order = json.loads(ORDER_INDICES_PATH.read_text(encoding="utf-8"))
    ids = ORDER_PATH.read_text(encoding="utf-8").splitlines()
    if len(order) != 7187 or len(ids) != 7187 or len(set(order)) != 7187:
        raise RuntimeError("Historical V57 order structure mismatch")
    if any(dataset.rows[index]["original_row_id"] != row_id for index, row_id in zip(order, ids)):
        raise RuntimeError("Historical V57 order ID/index mismatch")
    prefix_indices, prefix_ids = order[:500], ids[:500]
    payload = ("\n".join(prefix_ids) + "\n").encode()
    (OUT / "train_prefix_500.txt").write_bytes(payload)
    write_json(OUT / "train_prefix_500_indices.json", prefix_indices)
    digest = hashlib.sha256(payload).hexdigest()
    (OUT / "train_prefix_500_sha256.txt").write_text(digest + "\n", encoding="utf-8")
    return {"rows": 500, "unique_rows": len(set(prefix_ids)), "indices": prefix_indices,
            "sha256": digest, "historical_order_sha256": ORDER_SHA256}


def common_config() -> dict[str, object]:
    return {
        "seed": 0, "variant": "alignment_on_equal_superset", "image_size": 320, "batch_size": 1,
        "precision": "float32", "amp_enabled": False, "feature_channels": 32, "fpn_out_channels": 128,
        "backbone": "RepViT-M0.9", "backbone_pretrained": False, "detector": "FCOS",
        "alignment_enabled": True, "fusion_weights": [1 / 3, 1 / 3, 1 / 3],
        "reliability_scorer_present": True, "reliability_scorer_active": False,
        "optimizer": "AdamW", "learning_rate": 1e-4, "weight_decay": 1e-4,
        "scheduler": None, "gradient_clipping": None, "augmentation": None, "num_workers": 0,
        "steps": 500, "trace_steps": list(TRACE_STEPS), "full_devval": False, "ap_ar": False,
        "threshold_selection": False, "checkpoint_selection": False, "early_stopping": False,
    }


def prepare() -> None:
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError("Unexpected V61 starting commit")
    if OUT.exists():
        raise RuntimeError("V61 output already exists")
    OUT.mkdir(parents=True)
    if sha256(TRAIN_MANIFEST) != TRAIN_SHA256:
        raise RuntimeError("Train manifest hash mismatch")
    dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=True)
    if len(dataset) != 7187:
        raise RuntimeError("Train manifest row mismatch")
    v60 = verify_v60()
    subsets = frozen_subsets()
    prefix = prefix_500(dataset)
    common = load_common_state()
    states, intervention = initial_states(common)
    for name, state in states.items():
        model = V57FusionSupersetDetector("alignment_on_equal_superset")
        loaded = model.load_state_dict(state, strict=False)
        if loaded.missing_keys or loaded.unexpected_keys or model.feature_scaffold.reliability_active:
            raise RuntimeError(f"V61 model/config contract mismatch: {name}")
    config = common_config()
    configs = {
        VARIANTS[0]: {**config, "name": VARIANTS[0], "initial_bbox_bias": [0.0] * 4},
        VARIANTS[1]: {**config, "name": VARIANTS[1], "initial_bbox_bias": [0.01] * 4},
    }
    protected = aggregate_fingerprint(protected_paths())
    lock = source_lock()
    protocol = {
        "prepared_at": now(), "starting_commit": START_COMMIT, "authorization_base": AUTHORIZATION_BASE,
        "train_rows": len(dataset), "train_sha256": TRAIN_SHA256, "prefix": prefix, "subsets": subsets,
        "v60_verification": v60, "common_init_sha256": INIT_SHA256,
        "control_initial_fingerprint": tensor_dict_fingerprint(states[VARIANTS[0]]),
        "intervention_initial_fingerprint": tensor_dict_fingerprint(states[VARIANTS[1]]),
        "intervention": intervention, "configs": configs, "run_order": list(VARIANTS),
        "steps_per_variant": STEPS_PER_VARIANT, "optimizer_step_limit": TOTAL_STEP_LIMIT,
        "probe_backward_limit": PROBE_BACKWARD_LIMIT, "protected_baseline": protected,
    }
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v61.json", {**lock, **protocol})
    write_json(OUT / "v60_evidence_verification.json", v60)
    write_json(OUT / "initialization_verification.json", {
        "common_init_path_local_not_committed": str(COMMON_INIT), "common_init_sha256": INIT_SHA256,
        "tensor_count": len(common), "all_finite": True, "strict_load_both": True,
        "paired_difference_only_bbox_bias": True, "intervention": intervention,
    })
    write_json(OUT / "intervention_delta.json", intervention)
    write_json(OUT / "trace_schedule.json", {"steps": list(TRACE_STEPS), "count": len(TRACE_STEPS),
                                               "gradient_rows_per_trace": 4, "total_backward_limit": 96})
    write_json(OUT / "per_variant_config.json", configs)
    (OUT / "protocol.md").write_text(
        "# V61 Early Bbox-Collapse Prevention Pilot\n\nTwo equal-fusion seed-0 runs use the same frozen 500-row "
        "prefix. The sole paired difference is a one-time four-element bbox output bias of +0.01.\n",
        encoding="utf-8")
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v61_mmuav_bbox_bias_pilot.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v61_mmuav_bbox_bias_pilot.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v61_mmuav_bbox_bias_pilot.py --run\n",
        encoding="utf-8")
    print(json.dumps({"status": "V61_PREPARED_CPU_ONLY", "protocol": protocol}, indent=2))


def matched_anchor_count(targets, anchors, counts, radius: float) -> int:
    total = 0
    for anchors_image, target in zip(anchors, targets):
        if target["boxes"].numel() == 0:
            continue
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
        values, _ = scores.max(dim=1)
        total += int((values >= 1e-5).sum())
    return total


def install_loss_capture(model: V57FusionSupersetDetector, capture: dict[str, object]):
    original = model.detector.compute_loss

    def wrapped(targets, head_outputs, anchors, counts):
        capture["matched_anchor_count"] = matched_anchor_count(
            targets, anchors, counts, model.detector.center_sampling_radius)
        return original(targets, head_outputs, anchors, counts)

    model.detector.compute_loss = wrapped


def geometry_row(model: V57FusionSupersetDetector, sample: dict[str, object], device: torch.device) -> dict[str, object]:
    captures: list[torch.Tensor] = []
    hook = model.detector.head.regression_head.bbox_reg.register_forward_hook(
        lambda _module, _inputs, output: captures.append(output.detach()))
    detector_image = model._feature_forward(*inputs_to_device(sample, device))
    detector = model.detector
    targets = target_to_device(sample, device)
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
    matched = matched_anchor_count(transformed_targets, anchors_full, counts, detector.center_sampling_radius)
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
            "level": level, "pre_relu": tensor_stats(pre), "post_relu": tensor_stats(post),
            "post_relu_positive_fraction": float((post > 0).float().mean().cpu()),
            "all_zero_location_fraction": float((post == 0).all(dim=1).float().mean().cpu()),
            "decoded_width_before_clip": tensor_stats(raw_width), "decoded_height_before_clip": tensor_stats(raw_height),
            "decoded_width_after_clip": tensor_stats(width), "decoded_height_after_clip": tensor_stats(height),
            "geometry_counts": {"decoded": int(decoded.shape[0]), "valid": int(valid.sum().cpu()),
                                "degenerate": int((finite & ~valid).sum().cpu()),
                                "nonfinite": int((~finite).sum().cpu()), "clipped": int(changed.sum().cpu())},
            "classification_logit": tensor_stats(cls), "centerness_logit": tensor_stats(ctr),
            "combined_score": tensor_stats(combined),
        })
    return {"row_id": sample["original_row_id"], "target_boxes": int(targets[0]["boxes"].shape[0]),
            "matched_anchor_count": matched,
            "losses": {key: float(value.detach().cpu()) for key, value in losses.items()}, "levels": levels}


def aggregate_geometry(records: list[dict[str, object]]) -> dict[str, object]:
    result = {"rows": len(records), "row_ids": [row["row_id"] for row in records], "levels": []}
    for level in range(4):
        items = [record["levels"][level] for record in records]
        result["levels"].append({
            "level": level,
            "geometry_counts": {key: sum(item["geometry_counts"][key] for item in items)
                                for key in ("decoded", "valid", "degenerate", "nonfinite", "clipped")},
            "pre_relu_negative_fraction_mean": float(np.mean([
                item["pre_relu"]["negative_count"] / item["pre_relu"]["count"] for item in items])),
            "pre_relu_zero_fraction_mean": float(np.mean([
                item["pre_relu"]["zero_count"] / item["pre_relu"]["count"] for item in items])),
            "pre_relu_positive_fraction_mean": float(np.mean([
                item["pre_relu"]["positive_count"] / item["pre_relu"]["count"] for item in items])),
            "post_relu_positive_fraction_mean": float(np.mean([item["post_relu_positive_fraction"] for item in items])),
            "all_zero_location_fraction_mean": float(np.mean([item["all_zero_location_fraction"] for item in items])),
            "pre_relu_min_quantiles": compact_quantiles(torch.tensor([item["pre_relu"]["minimum"] for item in items])),
            "pre_relu_max_quantiles": compact_quantiles(torch.tensor([item["pre_relu"]["maximum"] for item in items])),
            "width_median_quantiles": compact_quantiles(torch.tensor([
                item["decoded_width_after_clip"]["quantiles"]["0.5"] for item in items])),
            "height_median_quantiles": compact_quantiles(torch.tensor([
                item["decoded_height_after_clip"]["quantiles"]["0.5"] for item in items])),
            "combined_score_max_quantiles": compact_quantiles(torch.tensor([
                item["combined_score"]["maximum"] for item in items])),
        })
    result["aggregate_counts"] = {key: sum(level["geometry_counts"][key] for level in result["levels"])
                                  for key in ("decoded", "valid", "degenerate", "nonfinite", "clipped")}
    result["losses"] = {key: {"min": min(row["losses"][key] for row in records),
                                    "max": max(row["losses"][key] for row in records),
                                    "mean": float(np.mean([row["losses"][key] for row in records]))}
                        for key in ("classification", "bbox_regression", "bbox_ctrness")}
    matched = [row["matched_anchor_count"] for row in records]
    result["matched_anchors"] = {"min": min(matched), "max": max(matched), "sum": sum(matched),
                                  "mean": float(np.mean(matched))}
    return result


def rng_snapshot() -> dict[str, object]:
    return {"python": random.getstate(), "numpy": np.random.get_state(), "torch": torch.get_rng_state().clone(),
            "cuda": [state.clone() for state in torch.cuda.get_rng_state_all()]}


def rng_digest(snapshot: dict[str, object]) -> str:
    digest = hashlib.sha256(repr(snapshot["python"]).encode())
    numpy_state = snapshot["numpy"]
    digest.update(str(numpy_state[0]).encode())
    digest.update(numpy_state[1].tobytes())
    digest.update(repr(numpy_state[2:]).encode())
    digest.update(snapshot["torch"].numpy().tobytes())
    for state in snapshot["cuda"]:
        digest.update(state.cpu().numpy().tobytes())
    return digest.hexdigest()


def restore_rng(snapshot: dict[str, object]) -> None:
    random.setstate(snapshot["python"])
    np.random.set_state(snapshot["numpy"])
    torch.set_rng_state(snapshot["torch"])
    torch.cuda.set_rng_state_all(snapshot["cuda"])


def optimizer_hash(optimizer: torch.optim.Optimizer) -> str:
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

    update(optimizer.state_dict())
    return digest.hexdigest()


def bbox_grad_summary(module: torch.nn.Module) -> dict[str, object]:
    tensors = [parameter.grad.detach().float().flatten() for parameter in module.parameters()
               if parameter.grad is not None]
    if not tensors:
        return {"norm": 0.0, "nonzero_fraction": 0.0, "finite": True}
    flat = torch.cat(tensors)
    return {"norm": float(flat.double().norm().cpu()),
            "nonzero_fraction": float((flat != 0).float().mean().cpu()),
            "finite": bool(torch.isfinite(flat).all())}


def gradient_probe(state: dict[str, torch.Tensor], indices: list[int], dataset, device) -> dict[str, object]:
    model = V57FusionSupersetDetector("alignment_on_equal_superset")
    model.load_state_dict(state, strict=True)
    before_parameters = parameter_hash(model)
    before_buffers = buffer_hash(model)
    model.to(device).train()
    loss_capture: dict[str, object] = {}
    install_loss_capture(model, loss_capture)
    captures: list[torch.Tensor] = []
    hook = model.detector.head.regression_head.bbox_reg.register_forward_hook(
        lambda _module, _inputs, output: captures.append(output.detach()))
    rows = []
    for index in indices:
        model.zero_grad(set_to_none=True)
        captures.clear(); loss_capture.clear()
        sample = dataset[index]
        losses = model(*inputs_to_device(sample, device), target_to_device(sample, device))
        total = sum(losses.values())
        total.backward()
        pre = torch.cat([value.flatten() for value in captures])
        bbox = model.detector.head.regression_head.bbox_reg
        weight = bbox_grad_summary(torch.nn.ModuleList([bbox]))
        weight_only = bbox.weight.grad
        bias_only = bbox.bias.grad
        rows.append({
            "index": index, "row_id": sample["original_row_id"],
            "target_box_count": int(sample["target_rgb"]["boxes"].shape[0]),
            "matched_anchor_count": int(loss_capture["matched_anchor_count"]),
            "losses": {key: float(value.detach().cpu()) for key, value in losses.items()},
            "loss_total": float(total.detach().cpu()), "bbox_pre_relu": tensor_stats(pre),
            "bbox_post_relu_positive_fraction": float((pre > 0).float().mean().cpu()),
            "bbox_weight_gradient_norm": 0.0 if weight_only is None else float(weight_only.detach().double().norm().cpu()),
            "bbox_bias_gradient_norm": 0.0 if bias_only is None else float(bias_only.detach().double().norm().cpu()),
            "bbox_gradient_nonzero_fraction": weight["nonzero_fraction"], "bbox_gradient_finite": weight["finite"],
        })
    hook.remove()
    after_parameters = parameter_hash(model)
    after_buffers = buffer_hash(model)
    if before_parameters != after_parameters:
        raise RuntimeError("No-step probe changed parameters")
    result = {"backward_calls": len(rows), "rows": rows, "parameters_unchanged": True,
              "parameter_hash_before": before_parameters, "parameter_hash_after": after_parameters,
              "buffer_hash_before": before_buffers, "buffer_hash_after": after_buffers,
              "ephemeral_buffers_changed": before_buffers != after_buffers}
    del model
    torch.cuda.empty_cache()
    return result


def trace_state(model, optimizer, state_step: int, train_dataset, dev_dataset, subsets, device) -> dict[str, object]:
    train_parameter_before = parameter_hash(model)
    train_buffer_before = buffer_hash(model)
    optimizer_before = optimizer_hash(optimizer)
    rng_before = rng_snapshot()
    rng_before_hash = rng_digest(rng_before)
    was_training = model.training
    model.eval()
    with torch.no_grad():
        records = [geometry_row(model, train_dataset[index], device) for index in subsets["train_indices"]]
        geometry = aggregate_geometry(records)
        dev_geometry = None
        if state_step == 500:
            dev_records = [geometry_row(model, dev_dataset[index], device) for index in subsets["devval_indices"]]
            dev_geometry = aggregate_geometry(dev_records)
    if was_training:
        model.train()
    state = clone_state(model.state_dict())
    probe = gradient_probe(state, subsets["gradient_indices"], train_dataset, device)
    restore_rng(rng_before)
    rng_after_hash = rng_digest(rng_snapshot())
    unchanged = {
        "training_parameters": parameter_hash(model) == train_parameter_before,
        "training_buffers": buffer_hash(model) == train_buffer_before,
        "optimizer": optimizer_hash(optimizer) == optimizer_before,
        "rng": rng_after_hash == rng_before_hash,
    }
    if not all(unchanged.values()):
        raise RuntimeError(f"Trace mutated persistent training state at step {state_step}: {unchanged}")
    bbox = model.detector.head.regression_head.bbox_reg
    parameter = {"weight": tensor_stats(bbox.weight, False), "weight_norm": float(bbox.weight.detach().norm().cpu()),
                 "bias": tensor_stats(bbox.bias, False), "bias_values": bbox.bias.detach().cpu().tolist(),
                 "bias_norm": float(bbox.bias.detach().norm().cpu())}
    return {"step": state_step, "geometry": geometry, "devval_geometry": dev_geometry,
            "gradient_probe": probe, "bbox_output_parameters": parameter,
            "isolation": unchanged, "rng_hash_before": rng_before_hash, "rng_hash_after": rng_after_hash}


def checkpoint_path(variant: str) -> Path:
    return LOCAL / f"{variant}_final_step500.pt"


def train_variant(name: str, initial: dict[str, torch.Tensor], order: list[int], train_dataset, dev_dataset,
                  subsets, device, total_before: int, writer) -> tuple[dict[str, object], list[dict[str, object]]]:
    if total_before + STEPS_PER_VARIANT > TOTAL_STEP_LIMIT:
        raise RuntimeError("V61 total optimizer-step limit exceeded")
    configure_seed(0)
    model = V57FusionSupersetDetector("alignment_on_equal_superset").to(device)
    model.load_state_dict(initial, strict=True)
    if tensor_dict_fingerprint({key: value.detach().cpu() for key, value in model.state_dict().items()}) != tensor_dict_fingerprint(initial):
        raise RuntimeError(f"Initial state mismatch: {name}")
    scorer_initial = clone_state(model.feature_scaffold.reliability_scorer.state_dict())
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    loss_capture: dict[str, object] = {}
    install_loss_capture(model, loss_capture)
    pre_captures: list[torch.Tensor] = []
    hook = model.detector.head.regression_head.bbox_reg.register_forward_hook(
        lambda _module, _inputs, output: pre_captures.append(output.detach()))
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    traces = [trace_state(model, optimizer, 0, train_dataset, dev_dataset, subsets, device)]
    completed = 0
    step_times = []
    started_variant = time.perf_counter()
    previous_end = started_variant
    for expected_step, index in enumerate(order, 1):
        if completed >= STEPS_PER_VARIANT or total_before + completed >= TOTAL_STEP_LIMIT:
            raise RuntimeError("V61 optimizer-step guard exceeded")
        started = time.perf_counter()
        sample = train_dataset[index]
        data_done = time.perf_counter()
        inputs = inputs_to_device(sample, device)
        targets = target_to_device(sample, device)
        optimizer.zero_grad(set_to_none=True); pre_captures.clear(); loss_capture.clear()
        forward_started = time.perf_counter()
        losses = model(*inputs, targets)
        total = sum(losses.values())
        torch.cuda.synchronize(); forward_done = time.perf_counter()
        if not losses or not all(torch.isfinite(value).all() for value in losses.values()):
            raise RuntimeError(f"Non-finite loss: {name} step {expected_step}")
        total.backward(); torch.cuda.synchronize(); backward_done = time.perf_counter()
        global_norm, global_finite = gradient_norm(model.parameters())
        bbox = model.detector.head.regression_head.bbox_reg
        bbox_summary = bbox_grad_summary(torch.nn.ModuleList([bbox]))
        weight_norm = 0.0 if bbox.weight.grad is None else float(bbox.weight.grad.detach().double().norm().cpu())
        bias_norm = 0.0 if bbox.bias.grad is None else float(bbox.bias.grad.detach().double().norm().cpu())
        scorer_has_gradient = any(parameter.grad is not None for parameter in model.feature_scaffold.reliability_scorer.parameters())
        if scorer_has_gradient or not global_finite or not bbox_summary["finite"]:
            raise RuntimeError(f"Gradient/dormant-scorer contract failure: {name} step {expected_step}")
        optimizer.step(); completed += 1
        if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
            raise RuntimeError(f"Non-finite parameter: {name} step {expected_step}")
        torch.cuda.synchronize(); optimizer_done = time.perf_counter()
        values = {key: float(value.detach().cpu()) for key, value in losses.items()}
        bias_values = bbox.bias.detach().cpu().tolist()
        row = {
            "variant": name, "step": completed, "original_row_id": sample["original_row_id"],
            "target_box_count": int(sample["target_rgb"]["boxes"].shape[0]),
            "valid_target_count": int(((sample["target_rgb"]["boxes"][:, 2:] - sample["target_rgb"]["boxes"][:, :2]) > 0).all(dim=1).sum()),
            "matched_anchor_count": int(loss_capture["matched_anchor_count"]),
            "loss_total": float(total.detach().cpu()), "loss_classifier": values["classification"],
            "loss_box_reg": values["bbox_regression"], "loss_centerness": values["bbox_ctrness"],
            "learning_rate": 1e-4, "global_gradient_norm": global_norm,
            "bbox_weight_gradient_norm": weight_norm, "bbox_bias_gradient_norm": bias_norm,
            "bbox_gradient_nonzero_fraction": bbox_summary["nonzero_fraction"],
            "bbox_bias_0": bias_values[0], "bbox_bias_1": bias_values[1],
            "bbox_bias_2": bias_values[2], "bbox_bias_3": bias_values[3], "finite": True,
            "cuda_allocated_bytes": torch.cuda.memory_allocated(), "cuda_reserved_bytes": torch.cuda.memory_reserved(),
            "data_time_sec": data_done - previous_end, "forward_time_sec": forward_done - forward_started,
            "backward_time_sec": backward_done - forward_done, "optimizer_time_sec": optimizer_done - backward_done,
            "step_time_sec": optimizer_done - started,
        }
        writer.writerow(row); step_times.append(row["step_time_sec"])
        if completed in TRACE_STEPS:
            traces.append(trace_state(model, optimizer, completed, train_dataset, dev_dataset, subsets, device))
            print(f"V61_TRACE_COMPLETE variant={name} step={completed} valid={traces[-1]['geometry']['aggregate_counts']['valid']}", flush=True)
        previous_end = optimizer_done
    hook.remove()
    if completed != 500 or [trace["step"] for trace in traces] != list(TRACE_STEPS):
        raise RuntimeError(f"Incomplete V61 trace/training: {name}")
    scorer_final = model.feature_scaffold.reliability_scorer.state_dict()
    scorer_unchanged = all(torch.equal(scorer_final[key].detach().cpu(), value) for key, value in scorer_initial.items())
    if not scorer_unchanged:
        raise RuntimeError(f"Dormant scorer changed: {name}")
    LOCAL.mkdir(parents=True, exist_ok=True)
    checkpoint = checkpoint_path(name)
    if checkpoint.exists():
        raise RuntimeError(f"Refusing to overwrite V61 checkpoint: {checkpoint}")
    torch.save({"model_state": model.state_dict(), "variant": name, "completed_optimizer_steps": completed,
                "common_init_sha256": INIT_SHA256, "prefix_sha256": (OUT / "train_prefix_500_sha256.txt").read_text().strip()}, checkpoint)
    metadata = {"path_local_not_committed": str(checkpoint), "sha256": sha256(checkpoint),
                "bytes": checkpoint.stat().st_size, "completed_optimizer_steps": completed,
                "selection_metric": None, "common_init_sha256": INIT_SHA256,
                "final_state_fingerprint": tensor_dict_fingerprint({key: value.detach().cpu() for key, value in model.state_dict().items()})}
    summary = {"variant": name, "completed_optimizer_steps": completed, "all_finite": True,
               "elapsed_seconds": time.perf_counter() - started_variant,
               "step_time_mean_sec": float(np.mean(step_times)), "step_time_min_sec": min(step_times),
               "step_time_max_sec": max(step_times), "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
               "peak_reserved_bytes": torch.cuda.max_memory_reserved(), "dormant_scorer_unchanged": True,
               "checkpoint": metadata}
    del optimizer, model
    torch.cuda.empty_cache()
    return summary, traces


def trace_classification(trace: dict[str, object]) -> str:
    valid = trace["geometry"]["aggregate_counts"]["valid"]
    rows = trace["gradient_probe"]["rows"]
    all_zero_grad = all(row["bbox_weight_gradient_norm"] == 0.0 and row["bbox_bias_gradient_norm"] == 0.0 for row in rows)
    any_nonzero_grad = any(row["bbox_weight_gradient_norm"] > 0.0 or row["bbox_bias_gradient_norm"] > 0.0 for row in rows)
    if valid == 0 and all_zero_grad:
        return "EARLY_BBOX_COLLAPSE"
    if valid > 0 and any_nonzero_grad:
        return "GEOMETRY_AND_GRADIENT_PRESERVED"
    return "NEITHER_PREREGISTERED_STATE"


def run() -> None:
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    lock = json.loads((OUT / "source_lock_v61.json").read_text(encoding="utf-8"))
    if source_lock()["source_hashes"] != lock["source_hashes"]:
        raise RuntimeError("V61 source changed after CPU lock")
    if aggregate_fingerprint(protected_paths()) != protocol["protected_baseline"]:
        raise RuntimeError("Protected evidence changed before V61 CUDA")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for V61")
    common = load_common_state()
    states, intervention = initial_states(common)
    if intervention != protocol["intervention"]:
        raise RuntimeError("V61 intervention changed after preparation")
    order = protocol["prefix"]["indices"]
    if len(order) != 500 or len(set(order)) != 500:
        raise RuntimeError("V61 prefix invalid")
    subsets = protocol["subsets"]
    train_dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=False)
    dev_dataset = MMUAVFeatureAlignmentDataset(
        ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt", 320,
        validate_paths=False)
    device = torch.device("cuda:0")
    log_path = OUT / "per_variant_training_log.csv"
    if log_path.exists():
        raise RuntimeError("Refusing to overwrite V61 training log")
    summaries, trace_map = {}, {}
    total_steps = 0
    with log_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS); writer.writeheader()
        for name in VARIANTS:
            summary, traces = train_variant(name, states[name], order, train_dataset, dev_dataset,
                                             subsets, device, total_steps, writer)
            handle.flush()
            summaries[name], trace_map[name] = summary, traces
            total_steps += summary["completed_optimizer_steps"]
    total_backward = sum(trace["gradient_probe"]["backward_calls"] for traces in trace_map.values() for trace in traces)
    if total_steps != TOTAL_STEP_LIMIT or total_backward != PROBE_BACKWARD_LIMIT:
        raise RuntimeError(f"V61 budget mismatch: steps={total_steps}, backward={total_backward}")
    geometry_output = {name: [{"step": trace["step"], "geometry": trace["geometry"],
                               "devval_geometry": trace["devval_geometry"],
                               "bbox_output_parameters": trace["bbox_output_parameters"]} for trace in traces]
                       for name, traces in trace_map.items()}
    gradient_output = {name: [{"step": trace["step"], "gradient_probe": trace["gradient_probe"],
                               "isolation": trace["isolation"], "rng_hash_before": trace["rng_hash_before"],
                               "rng_hash_after": trace["rng_hash_after"]} for trace in traces]
                       for name, traces in trace_map.items()}
    classifications = {name: [{"step": trace["step"], "state": trace_classification(trace)} for trace in traces]
                       for name, traces in trace_map.items()}
    first_collapse = {name: next((row["step"] for row in rows if row["state"] == "EARLY_BBOX_COLLAPSE"), None)
                      for name, rows in classifications.items()}
    first_preserved = {name: next((row["step"] for row in rows if row["state"] == "GEOMETRY_AND_GRADIENT_PRESERVED"), None)
                       for name, rows in classifications.items()}
    control_collapsed = first_collapse[VARIANTS[0]] is not None
    intervention_collapsed = first_collapse[VARIANTS[1]] is not None
    intervention_step500 = classifications[VARIANTS[1]][-1]["state"]
    if control_collapsed and not intervention_collapsed and intervention_step500 == "GEOMETRY_AND_GRADIENT_PRESERVED":
        decision = "V61_CONTROL_COLLAPSE_REPRODUCED_POSITIVE_BIAS_PREVENTS_THROUGH_STEP500"
    elif control_collapsed and intervention_collapsed:
        decision = "V61_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE"
    elif control_collapsed:
        decision = "V61_CONTROL_COLLAPSE_REPRODUCED_INTERVENTION_RESULT_MIXED"
    else:
        decision = "V61_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_500_STEPS"
    checkpoints = {name: summaries[name]["checkpoint"] for name in VARIANTS}
    comparison = {"trace_classifications": classifications, "first_collapse_step": first_collapse,
                  "first_preserved_step": first_preserved, "selected_outcome": decision,
                  "single_seed_early_engineering_evidence_only": True}
    safety = {"optimizer_steps": total_steps, "optimizer_step_limit": TOTAL_STEP_LIMIT,
              "per_variant_optimizer_steps": {name: summaries[name]["completed_optimizer_steps"] for name in VARIANTS},
              "probe_backward_calls": total_backward, "probe_backward_limit": PROBE_BACKWARD_LIMIT,
              "all_trace_isolation_checks": all(all(trace["isolation"].values()) for traces in trace_map.values() for trace in traces),
              "all_finite": all(summary["all_finite"] for summary in summaries.values()),
              "protected_fingerprint_unchanged": aggregate_fingerprint(protected_paths()) == protocol["protected_baseline"],
              "full_devval_rows": 0, "ap_ar_computed": False, "threshold_selection": False,
              "tuning": False, "reruns": 0, "checkpoint_selection": False}
    if not safety["all_trace_isolation_checks"] or not safety["protected_fingerprint_unchanged"]:
        raise RuntimeError(f"V61 safety audit failure: {safety}")
    write_json(OUT / "per_variant_trace_geometry.json", geometry_output)
    write_json(OUT / "per_variant_trace_gradient.json", gradient_output)
    write_json(OUT / "per_variant_checkpoint_metadata.json", checkpoints)
    write_json(OUT / "paired_trace_comparison.json", comparison)
    write_json(OUT / "memory_timing_summary.json", summaries)
    write_json(OUT / "safety_audit.json", safety)
    write_json(OUT / "final_decision.json", {"decision": decision, "comparison": comparison,
                                               "safety": safety, "checkpoint_metadata": checkpoints})
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


if __name__ == "__main__":
    try:
        main()
    except torch.OutOfMemoryError as exc:
        raise SystemExit(f"V61_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY: {exc}")
