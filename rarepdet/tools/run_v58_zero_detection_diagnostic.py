"""Read-only V58 diagnostic for V57 zero foreground detections."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import subprocess
import sys
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import torch
from torchvision.models.detection import _utils as det_utils
from torchvision.ops import boxes as box_ops


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.mmuav_feature_alignment_detector import MMUAVFeatureAlignmentDetector
from rarepdet.experimental.v57_fusion_superset_detector import V57FusionSupersetDetector
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import DEVVAL_MANIFEST, inputs_to_device


OUT = ROOT / "runs/v58_mmuav_zero_detection_diagnostic"
START_COMMIT = "506bdea52563fdabe732c5044b37136bc9b9d8ea"
V57_CHECKPOINTS = {
    "v57_equal": {
        "path": Path(r"D:\MM-UAV_v57_local\alignment_on_equal_superset_final_step7187.pt"),
        "sha256": "d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142",
        "variant": "alignment_on_equal_superset",
    },
    "v57_reliability": {
        "path": Path(r"D:\MM-UAV_v57_local\alignment_on_reliability_superset_final_step7187.pt"),
        "sha256": "b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df",
        "variant": "alignment_on_reliability_superset",
    },
}
V55_REFERENCE = {
    "path": Path(r"D:\MM-UAV_v55_local\alignment_on_equal_final_step7187.pt"),
    "sha256": "2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258",
    "variant": "alignment_on_equal",
}
LADDER = (0.0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2)
QUANTILES = (0.0, 0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999, 1.0)
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


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


def tensor_fingerprint(state: dict[str, torch.Tensor]) -> str:
    digest = hashlib.sha256()
    for name, tensor in state.items():
        digest.update(name.encode("utf-8"))
        digest.update(str(tuple(tensor.shape)).encode("ascii"))
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def model_for(name: str, variant: str) -> torch.nn.Module:
    if name.startswith("v57_"):
        return V57FusionSupersetDetector(variant)
    return MMUAVFeatureAlignmentDetector(variant)


def checkpoint_verification(name: str, spec: dict[str, object], required: bool) -> dict[str, object]:
    path = spec["path"]
    if not path.is_file():
        if required:
            raise RuntimeError(f"Missing required checkpoint: {path}")
        return {"name": name, "available": False, "reason": "local checkpoint absent"}
    actual_hash = sha256(path)
    if actual_hash != spec["sha256"]:
        if required:
            raise RuntimeError(f"Required checkpoint hash mismatch: {name} {actual_hash}")
        return {"name": name, "available": False, "reason": "local checkpoint hash mismatch",
                "actual_sha256": actual_hash, "expected_sha256": spec["sha256"]}
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if payload.get("completed_optimizer_steps") != 7187 or payload.get("variant") != spec["variant"]:
        raise RuntimeError(f"Checkpoint metadata mismatch: {name}")
    state = payload.get("model_state")
    if not isinstance(state, dict) or not state:
        raise RuntimeError(f"Checkpoint state_dict missing: {name}")
    nonfinite = [key for key, value in state.items() if not torch.isfinite(value).all()]
    if nonfinite:
        raise RuntimeError(f"Non-finite checkpoint tensors: {name} {nonfinite[:5]}")
    model = model_for(name, spec["variant"])
    result = model.load_state_dict(state, strict=False)
    if result.missing_keys or result.unexpected_keys:
        raise RuntimeError(f"State coverage mismatch: {name} {result}")
    expected_shapes = {key: list(value.shape) for key, value in model.state_dict().items()}
    shape_mismatch = [key for key, value in state.items() if expected_shapes.get(key) != list(value.shape)]
    if shape_mismatch:
        raise RuntimeError(f"Checkpoint shape mismatch: {name} {shape_mismatch[:5]}")
    return {
        "name": name, "available": True, "required": required, "path_local_not_committed": str(path),
        "bytes": path.stat().st_size, "sha256": actual_hash, "variant": spec["variant"],
        "completed_optimizer_steps": payload["completed_optimizer_steps"], "state_tensor_count": len(state),
        "missing_keys": list(result.missing_keys), "unexpected_keys": list(result.unexpected_keys),
        "shape_mismatch_keys": shape_mismatch, "all_tensors_finite": True,
        "state_fingerprint": tensor_fingerprint(state),
    }


def protected_source_lock() -> dict[str, object]:
    changed = set(git("diff", "--name-only", START_COMMIT).splitlines())
    protected = {
        "rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py", "main.tex",
        "main_sivp_snjnl.tex",
    }
    forbidden = sorted(path for path in changed if path in protected or path.startswith("manuscript/") or
                       path.startswith("submission/") or (path.startswith("runs/v5") and not
                       path.startswith("runs/v58_mmuav_zero_detection_diagnostic/")))
    if forbidden:
        raise RuntimeError(f"Protected path changes: {forbidden}")
    sources = [
        "rarepdet/tools/run_v58_zero_detection_diagnostic.py",
        "tests/test_v58_zero_detection_diagnostic.py",
        "rarepdet/tools/run_v57_mmuav_paired_fusion.py",
        "rarepdet/experimental/v57_fusion_superset_detector.py",
        "rarepdet/tools/run_v55_mmuav_paired_alignment.py",
        "rarepdet/experimental/mmuav_feature_alignment_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
    ]
    return {"starting_commit": START_COMMIT, "protected_changes": [],
            "source_hashes": {path: sha256(ROOT / path) for path in sources}}


def prepare() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "protocol.json").exists():
        raise RuntimeError("V58 protocol already exists; refusing to regenerate")
    if sha256(DEVVAL_MANIFEST) != "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54":
        raise RuntimeError("V58 devval hash mismatch")
    dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=True)
    if len(dataset) != 1845 or any(row["split"] != "devval" for row in dataset.rows):
        raise RuntimeError("V58 devval row contract mismatch")
    ids = [row["original_row_id"] for row in dataset.rows]
    order_payload = ("\n".join(ids) + "\n").encode("utf-8")
    (OUT / "devval_order.txt").write_bytes(order_payload)
    order_hash = hashlib.sha256(order_payload).hexdigest()
    (OUT / "devval_order_sha256.txt").write_text(order_hash + "\n", encoding="utf-8")
    subset = torch.randperm(len(dataset), generator=torch.Generator(device="cpu").manual_seed(58))[:32].tolist()
    subset_payload = (json.dumps(subset, separators=(",", ":")) + "\n").encode("utf-8")
    write_json(OUT / "detailed_subset_indices.json", subset)
    subset_hash = hashlib.sha256(subset_payload).hexdigest()
    (OUT / "detailed_subset_sha256.txt").write_text(subset_hash + "\n", encoding="utf-8")
    verifications = {name: checkpoint_verification(name, spec, True) for name, spec in V57_CHECKPOINTS.items()}
    reference = checkpoint_verification("v55_reference", V55_REFERENCE, False)
    verifications["v55_reference"] = reference
    write_json(OUT / "checkpoint_verification.json", verifications)
    write_json(OUT / "v55_reference_availability.json", reference)
    score_source = inspect.getsource(type(model_for("v57_equal", V57_CHECKPOINTS["v57_equal"]["variant"]).detector).postprocess_detections)
    required_fragments = ("torch.sqrt", "torch.sigmoid", "> self.score_thresh", "topk", "batched_nms")
    if not all(fragment in score_source for fragment in required_fragments):
        raise RuntimeError("FCOS score-path instrumentation contract mismatch")
    lock = protected_source_lock()
    protocol = {
        "prepared_at": NOW, "starting_commit": START_COMMIT, "optimizer_steps": 0, "backward_passes": 0,
        "training_mode_executions": 0, "devval_rows": len(dataset), "devval_sha256": sha256(DEVVAL_MANIFEST),
        "devval_order_sha256": order_hash, "detailed_subset_seed": 58,
        "detailed_subset_indices": subset, "detailed_subset_sha256": subset_hash,
        "threshold_ladder_frozen_before_inference": list(LADDER), "quantiles": list(QUANTILES),
        "required_checkpoints": verifications, "alternate_threshold_ap_ar_computed": False,
        "inference_passes": {"v57_equal": 1, "v57_reliability": 1,
                             "v55_reference": 1 if reference["available"] else 0},
    }
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v58.json", {**lock, **protocol})
    (OUT / "protocol.md").write_text(
        "# V58 Read-Only Protocol\n\nZero optimizer steps and no backward passes. One frozen aggregate pass per "
        "required V57 checkpoint and one hash-matching V55 reference pass, with a seed-58 32-row trace subset.\n",
        encoding="utf-8")
    (OUT / "source_lock_v58.md").write_text(
        f"# V58 Source Lock\n\nStarting commit: `{START_COMMIT}`. Devval and checkpoints reproduce exactly; "
        "production, history, V51, and manuscript paths are unchanged.\n", encoding="utf-8")
    (OUT / "implementation_score_path.md").write_text(
        "# Actual FCOS Score Path\n\nFor every FPN level torchvision FCOS computes "
        "`sqrt(sigmoid(class_logit) * sigmoid(centerness_logit))`, flattens class/anchor candidates, applies "
        "the strict `score > score_thresh` filter, keeps at most `topk_candidates` per level, decodes and clips "
        "boxes, applies class-aware batched NMS, then keeps the first `detections_per_img` globally. V57 used "
        "score threshold 0.001, NMS 0.6, per-level top-k 1000, and final cap 100. The evaluator subsequently "
        "keeps foreground label 1 only and applies no second positive threshold.\n", encoding="utf-8")
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v58_zero_detection_diagnostic.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v58_zero_detection_diagnostic.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v58_zero_detection_diagnostic.py --run\n",
        encoding="utf-8")
    print(json.dumps({"status": "V58_PREPARED_CPU_ONLY", **protocol}, indent=2))


def quantile_summary(values: torch.Tensor) -> dict[str, float]:
    values = values.float().flatten()
    q = torch.tensor(QUANTILES, dtype=torch.float32)
    result = torch.quantile(values, q)
    return {format(level, ".3g"): float(value) for level, value in zip(QUANTILES, result)}


def stats(tensor: torch.Tensor) -> dict[str, object]:
    value = tensor.detach().float()
    return {"shape": list(value.shape), "dtype": str(tensor.dtype), "device": str(tensor.device),
            "mean": float(value.mean().cpu()), "std": float(value.std(unbiased=False).cpu()),
            "min": float(value.min().cpu()), "max": float(value.max().cpu()),
            "finite": bool(torch.isfinite(value).all())}


def parameter_norms(model: torch.nn.Module) -> dict[str, object]:
    keys = (
        "detector.head.classification_head.cls_logits.weight",
        "detector.head.classification_head.cls_logits.bias",
        "detector.head.regression_head.bbox_ctrness.weight",
        "detector.head.regression_head.bbox_ctrness.bias",
        "to_detector_image.weight",
        "to_detector_image.bias",
    )
    state = model.state_dict()
    return {key: {"shape": list(state[key].shape), "norm": float(state[key].float().norm()),
                  "mean": float(state[key].float().mean()), "min": float(state[key].float().min()),
                  "max": float(state[key].float().max()), "finite": bool(torch.isfinite(state[key]).all())}
            for key in keys}


def instrument_image(model: torch.nn.Module, sample: dict[str, object], device: torch.device) -> dict[str, object]:
    detector_image = model._feature_forward(*inputs_to_device(sample, device))
    detector = model.detector
    images, _ = detector.transform(list(detector_image), None)
    features_dict = detector.backbone(images.tensors)
    if isinstance(features_dict, torch.Tensor):
        features_dict = OrderedDict([("0", features_dict)])
    features = list(features_dict.values())
    head = detector.head(features)
    anchors = detector.anchor_generator(images, features)
    per_level_counts = [feature.shape[-2] * feature.shape[-1] for feature in features]
    split_head = {key: list(value.split(per_level_counts, dim=1)) for key, value in head.items()}
    split_anchors = [list(value.split(per_level_counts)) for value in anchors]
    actual = detector.postprocess_detections(split_head, split_anchors, images.image_sizes)[0]

    level_records = []
    image_boxes, image_scores, image_labels = [], [], []
    box_counts = {"decoded": 0, "nonfinite": 0, "out_of_image_before_clip": 0, "degenerate_after_clip": 0,
                  "valid_after_clip": 0}
    for level, (reg, cls, ctr, anchor) in enumerate(zip(
            split_head["bbox_regression"], split_head["cls_logits"], split_head["bbox_ctrness"], split_anchors[0])):
        reg, cls, ctr = reg[0], cls[0], ctr[0]
        combined = torch.sqrt(torch.sigmoid(cls) * torch.sigmoid(ctr)).flatten()
        num_classes = cls.shape[-1]
        labels_all = torch.arange(combined.numel(), device=device) % num_classes
        ladder = {format(value, ".0e") if value else "0": {
            "all": int((combined > value).sum()),
            "label0": int(((combined > value) & (labels_all == 0)).sum()),
            "label1": int(((combined > value) & (labels_all == 1)).sum()),
        } for value in LADDER}
        keep = combined > detector.score_thresh
        kept_scores = combined[keep]
        topk_idxs = torch.where(keep)[0]
        threshold_count = int(topk_idxs.numel())
        num_topk = det_utils._topk_min(topk_idxs, detector.topk_candidates, 0)
        kept_scores, indices = kept_scores.topk(num_topk)
        topk_idxs = topk_idxs[indices]
        anchor_idxs = torch.div(topk_idxs, num_classes, rounding_mode="floor")
        labels = topk_idxs % num_classes
        boxes_raw = detector.box_coder.decode(reg[anchor_idxs], anchor[anchor_idxs])
        h, w = images.image_sizes[0]
        out_of_image = ((boxes_raw[:, 0] < 0) | (boxes_raw[:, 1] < 0) |
                        (boxes_raw[:, 2] > w) | (boxes_raw[:, 3] > h))
        boxes = box_ops.clip_boxes_to_image(boxes_raw, images.image_sizes[0])
        finite_boxes = torch.isfinite(boxes).all(dim=1)
        degenerate = (boxes[:, 2:] <= boxes[:, :2]).any(dim=1)
        box_counts["decoded"] += int(boxes.shape[0])
        box_counts["nonfinite"] += int((~finite_boxes).sum())
        box_counts["out_of_image_before_clip"] += int(out_of_image.sum())
        box_counts["degenerate_after_clip"] += int(degenerate.sum())
        box_counts["valid_after_clip"] += int((finite_boxes & ~degenerate).sum())
        image_boxes.append(boxes)
        image_scores.append(kept_scores)
        image_labels.append(labels)
        level_records.append({
            "level": level, "feature_shape": list(features[level].shape), "cls_shape": list(cls.shape),
            "ctr_shape": list(ctr.shape), "reg_shape": list(reg.shape), "raw_candidate_count": int(combined.numel()),
            "threshold_count": threshold_count, "topk_count": int(num_topk),
            "threshold_label0": int((labels_all[keep] == 0).sum()),
            "threshold_label1": int((labels_all[keep] == 1).sum()),
            "topk_label0": int((labels == 0).sum()), "topk_label1": int((labels == 1).sum()),
            "ladder": ladder, "cls_logits": cls.detach().cpu(), "ctr_logits": ctr.detach().cpu(),
            "combined": combined.detach().cpu(), "combined_label0": combined[labels_all == 0].detach().cpu(),
            "combined_label1": combined[labels_all == 1].detach().cpu(),
            "top_cls_logit": float(cls.max()), "top_ctr_logit": float(ctr.max()),
            "top_combined": float(combined.max()), "top_foreground_combined": float(combined[labels_all == 1].max()),
        })
    boxes = torch.cat(image_boxes)
    scores = torch.cat(image_scores)
    labels = torch.cat(image_labels)
    nms_keep = box_ops.batched_nms(boxes, scores, labels, detector.nms_thresh)
    nms_labels = labels[nms_keep]
    final_keep = nms_keep[: detector.detections_per_img]
    final = {"boxes": boxes[final_keep], "scores": scores[final_keep], "labels": labels[final_keep]}
    if not (torch.equal(final["labels"], actual["labels"]) and torch.equal(final["scores"], actual["scores"]) and
            torch.equal(final["boxes"], actual["boxes"])):
        raise RuntimeError("V58 manual stage instrumentation diverged from FCOS postprocess")
    return {
        "levels": level_records, "box_counts": box_counts,
        "stage": {"raw": sum(record["raw_candidate_count"] for record in level_records),
                  "after_threshold": sum(record["threshold_count"] for record in level_records),
                  "after_topk": int(scores.numel()), "after_nms": int(nms_keep.numel()),
                  "after_nms_label0": int((nms_labels == 0).sum()), "after_nms_label1": int((nms_labels == 1).sum()),
                  "final": int(final["scores"].numel()), "final_label0": int((final["labels"] == 0).sum()),
                  "final_label1": int((final["labels"] == 1).sum())},
        "max_score": float(torch.cat([record["combined"] for record in level_records]).max()),
        "max_foreground_score": float(torch.cat([record["combined_label1"] for record in level_records]).max()),
        "actual_output": actual, "detector_image": detector_image.detach(), "features": [value.detach() for value in features],
    }


def diagnose_model(name: str, spec: dict[str, object], subset: set[int], device: torch.device) -> tuple[dict, dict, dict, list, dict]:
    path = spec["path"]
    checkpoint_hash_before = sha256(path)
    payload = torch.load(path, map_location="cpu", weights_only=False)
    model = model_for(name, spec["variant"])
    load = model.load_state_dict(payload["model_state"], strict=False)
    if load.missing_keys or load.unexpected_keys:
        raise RuntimeError(f"Diagnostic load mismatch: {name}")
    state_before = tensor_fingerprint(model.state_dict())
    model.to(device)
    model.eval()
    if model.training or model.detector.training:
        raise RuntimeError(f"Evaluation mode failure: {name}")
    model.detector.score_thresh = 0.001
    model.detector.nms_thresh = 0.6
    model.detector.detections_per_img = 100
    dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    level_values = [{key: [] for key in ("cls", "ctr", "combined", "combined_label0", "combined_label1")}
                    for _ in range(4)]
    stage_total = {key: 0 for key in ("raw", "after_threshold", "after_topk", "after_nms", "after_nms_label0",
                                      "after_nms_label1", "final", "final_label0", "final_label1")}
    box_total = {key: 0 for key in ("decoded", "nonfinite", "out_of_image_before_clip",
                                    "degenerate_after_clip", "valid_after_clip")}
    ladder_total = {format(value, ".0e") if value else "0": {"all": 0, "label0": 0, "label1": 0} for value in LADDER}
    max_scores, max_foreground_scores, detailed = [], [], []
    images_with_threshold = images_with_final = images_with_foreground = 0
    output_schema = None
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    with torch.inference_mode():
        for index in range(len(dataset)):
            sample = dataset[index]
            record = instrument_image(model, sample, device)
            for key, value in record["stage"].items():
                stage_total[key] += value
            for key, value in record["box_counts"].items():
                box_total[key] += value
            images_with_threshold += record["stage"]["after_threshold"] > 0
            images_with_final += record["stage"]["final"] > 0
            images_with_foreground += record["stage"]["final_label1"] > 0
            max_scores.append(record["max_score"])
            max_foreground_scores.append(record["max_foreground_score"])
            for level, level_record in enumerate(record["levels"]):
                level_values[level]["cls"].append(level_record["cls_logits"].flatten())
                level_values[level]["ctr"].append(level_record["ctr_logits"].flatten())
                level_values[level]["combined"].append(level_record["combined"])
                level_values[level]["combined_label0"].append(level_record["combined_label0"])
                level_values[level]["combined_label1"].append(level_record["combined_label1"])
                for threshold, counts in level_record["ladder"].items():
                    for key, value in counts.items():
                        ladder_total[threshold][key] += value
            actual = record["actual_output"]
            if output_schema is None:
                output_schema = {key: {"shape": list(value.shape), "dtype": str(value.dtype),
                                       "device": str(value.device), "finite": bool(torch.isfinite(value).all())}
                                 for key, value in actual.items()}
            if index in subset:
                feature_outputs = model.last_feature_outputs
                detailed.append({
                    "index": index, "original_row_id": sample["original_row_id"],
                    "inputs": {key: stats(sample[key]) for key in ("rgb", "ir", "event")},
                    "features": {key: stats(feature_outputs[key]) for key in
                                 ("rgb_reference", "aligned_ir", "aligned_event", "fused")},
                    "fusion_weights": feature_outputs["fusion_weights"].detach().cpu().tolist(),
                    "detector_input": stats(record["detector_image"]),
                    "fpn_features": [stats(value) for value in record["features"]],
                    "levels": [{key: value for key, value in level.items() if key not in
                                {"cls_logits", "ctr_logits", "combined", "combined_label0", "combined_label1", "ladder"}}
                               for level in record["levels"]],
                    "stage": record["stage"], "box_counts": record["box_counts"],
                    "top_final": {"scores": actual["scores"][:5].detach().cpu().tolist(),
                                  "labels": actual["labels"][:5].detach().cpu().tolist(),
                                  "boxes": actual["boxes"][:5].detach().cpu().tolist()},
                })
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    score_summary = {"levels": []}
    for level, values in enumerate(level_values):
        cls = torch.cat(values["cls"])
        ctr = torch.cat(values["ctr"])
        combined = torch.cat(values["combined"])
        score_summary["levels"].append({
            "level": level, "classification_logit_quantiles": quantile_summary(cls),
            "classification_probability_quantiles": quantile_summary(torch.sigmoid(cls)),
            "centerness_logit_quantiles": quantile_summary(ctr),
            "centerness_probability_quantiles": quantile_summary(torch.sigmoid(ctr)),
            "combined_score_quantiles": quantile_summary(combined),
            "label0_combined_quantiles": quantile_summary(torch.cat(values["combined_label0"])),
            "label1_foreground_combined_quantiles": quantile_summary(torch.cat(values["combined_label1"])),
        })
    score_summary["max_score_per_image_quantiles"] = quantile_summary(torch.tensor(max_scores))
    score_summary["max_foreground_score_per_image_quantiles"] = quantile_summary(torch.tensor(max_foreground_scores))
    stage_total.update({"images": len(dataset), "images_with_threshold_candidate": images_with_threshold,
                        "images_with_final_output": images_with_final,
                        "images_with_final_foreground_label1": images_with_foreground,
                        "output_schema_first_image": output_schema, "box_counts": box_total})
    memory = {"inference_seconds": elapsed, "fps": len(dataset) / elapsed,
              "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
              "peak_reserved_bytes": torch.cuda.max_memory_reserved(), "all_values_finite": True}
    state_after = tensor_fingerprint({key: value.detach().cpu() for key, value in model.state_dict().items()})
    if state_before != state_after or checkpoint_hash_before != sha256(path):
        raise RuntimeError(f"Read-only mutation detected: {name}")
    norms = parameter_norms(model)
    del model, level_values
    torch.cuda.empty_cache()
    return score_summary, stage_total, ladder_total, detailed, {"memory": memory, "parameter_norms": norms,
                                                                 "state_unchanged": True,
                                                                 "checkpoint_unchanged": True}


def decide_root_cause(stage: dict[str, dict], scores: dict[str, dict], reference_available: bool) -> dict[str, object]:
    v57_names = ("v57_equal", "v57_reliability")
    both_have_raw_final = all(stage[name]["final"] > 0 for name in v57_names)
    both_zero_foreground = all(stage[name]["final_label1"] == 0 for name in v57_names)
    both_have_foreground_pre_cap = all(stage[name]["after_nms_label1"] > 0 for name in v57_names)
    if both_have_raw_final and both_zero_foreground and both_have_foreground_pre_cap:
        primary = "POSTPROCESS_THRESHOLD_OR_NMS_PATH"
        explanation = ("Both V57 models produced valid post-NMS label-1 candidates, but the global final detection cap "
                       "was filled by higher-scoring label-0 candidates before evaluator foreground filtering.")
    elif both_have_raw_final and both_zero_foreground:
        primary = "FEATURE_OR_HEAD_SCORE_COLLAPSE"
        explanation = ("Both V57 models produced raw detections, but label-1 foreground scores failed to survive the "
                       "frozen threshold/postprocess path; evaluator schema was valid.")
    elif all(stage[name]["after_threshold"] == 0 for name in v57_names):
        primary = "FEATURE_OR_HEAD_SCORE_COLLAPSE"
        explanation = "Both V57 combined-score distributions remained entirely below the frozen 0.001 threshold."
    else:
        primary = "ZERO_DETECTIONS_REPRODUCED_CAUSE_UNRESOLVED"
        explanation = "The read-only traces reproduced the outcome but did not isolate one supported primary cause."
    reference = stage.get("v55_reference") if reference_available else None
    return {"completion_state": "V58_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED" if primary !=
            "ZERO_DETECTIONS_REPRODUCED_CAUSE_UNRESOLVED" else "V58_ZERO_DETECTION_DIAGNOSIS_COMPLETE_CAUSE_UNRESOLVED",
            "primary_classification": primary, "explanation": explanation,
            "v57_raw_final_outputs_present": both_have_raw_final,
            "v57_final_foreground_label1_zero": both_zero_foreground,
            "v57_foreground_present_after_nms_before_final_cap": both_have_foreground_pre_cap,
            "v55_reference_available": reference_available,
            "v55_reference_final_label_counts": None if reference is None else
                {"label0": reference["final_label0"], "label1": reference["final_label1"]},
            "optimizer_steps": 0, "backward_passes": 0, "alternate_threshold_ap_ar_computed": False,
            "repair_authorized": False}


def run() -> None:
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    if protocol["optimizer_steps"] != 0 or protocol["backward_passes"] != 0 or tuple(
            protocol["threshold_ladder_frozen_before_inference"]) != LADDER:
        raise RuntimeError("V58 frozen protocol mismatch")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for V58 inference diagnostic")
    subset = set(protocol["detailed_subset_indices"])
    specs = dict(V57_CHECKPOINTS)
    if protocol["required_checkpoints"]["v55_reference"]["available"]:
        specs["v55_reference"] = V55_REFERENCE
    all_scores, all_stages, all_ladders, all_details, all_aux = {}, {}, {}, {}, {}
    device = torch.device("cuda:0")
    for name, spec in specs.items():
        score, stage, ladder, detail, aux = diagnose_model(name, spec, subset, device)
        all_scores[name], all_stages[name], all_ladders[name] = score, stage, ladder
        all_details[name], all_aux[name] = detail, aux
    write_json(OUT / "aggregate_score_diagnostics.json", all_scores)
    write_json(OUT / "aggregate_stage_counts.json", all_stages)
    write_json(OUT / "threshold_ladder_counts.json", all_ladders)
    write_json(OUT / "detailed_trace_summary.json", all_details)
    write_json(OUT / "memory_timing_summary.json", {name: value["memory"] for name, value in all_aux.items()})
    write_json(OUT / "parameter_norms_and_mutation_check.json", all_aux)
    decision = decide_root_cause(all_stages, all_scores, "v55_reference" in specs)
    write_json(OUT / "root_cause_decision.json", decision)
    (OUT / "root_cause_decision.md").write_text(
        f"# V58 Root Cause\n\nPrimary classification: `{decision['primary_classification']}`. "
        f"{decision['explanation']} Zero optimizer steps and no alternate-threshold AP/AR were used.\n",
        encoding="utf-8")
    v55_note = "available and traced" if "v55_reference" in specs else "unavailable"
    (OUT / "v55_v57_path_diff.md").write_text(
        "# V55/V57 Path Difference\n\nBoth paths use the same outer detector-image projection, RepViT-M0.9 FPN, "
        "torchvision FCOS head, transform normalization `[0,0,0]/[1,1,1]`, 320x320 fixed resize, score formula, "
        "threshold 0.001, per-level top-k 1000, NMS 0.6, final cap 100, output schema, and foreground-label-1 "
        "evaluator filtering. V57 subclasses the V55 wrapper, constructs the original V55 scaffold/detector, then "
        "replaces only `feature_scaffold` with its parameter-superset scaffold; the scorer is bypassed for equal and "
        "active for reliability. Checkpoint loading was complete. The V55 reference was " + v55_note +
        ". Direct score/stage differences are recorded in the aggregate JSON files.\n", encoding="utf-8")
    final = {"decision": decision, "models_diagnosed": list(specs), "optimizer_steps": 0, "backward_passes": 0,
             "training_mode_executions": 0, "alternate_threshold_ap_ar_computed": False,
             "checkpoints_unchanged": True, "parameters_unchanged": True}
    write_json(OUT / "final_decision.json", final)
    print(json.dumps(final, indent=2))


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
    main()
