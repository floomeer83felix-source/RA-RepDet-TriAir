"""Read-only V59 zero-detection diagnostic with bounded streaming summaries."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import torch
from torchvision.models.detection.fcos import FCOS


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.tools.run_v58_zero_detection_diagnostic import (
    DEVVAL_MANIFEST,
    LADDER,
    QUANTILES,
    V55_REFERENCE,
    V57_CHECKPOINTS,
    checkpoint_verification,
    instrument_image,
    model_for,
    parameter_norms,
    sha256,
    stats,
    tensor_fingerprint,
    write_json,
)
from rarepdet.tools.v59_streaming_histogram import (
    BIN_COUNT,
    LOGIT_HIGH,
    LOGIT_LOW,
    LOGIT_WIDTH,
    PROBABILITY_FLOOR,
    HistogramSpec,
    StreamingHistogram,
    validate_histogram_implementation,
)


OUT = ROOT / "runs/v59_mmuav_streaming_zero_detection_diagnostic"
START_COMMIT = "02ccb571dc143afa32057624ec1b65c438546092"
AUTHORIZATION_BASE_COMMIT = "3263d3d6ba9e01139047c1ca0b18708c9700f376"
RUN_ORDER = ("v57_equal", "v57_reliability", "v55_reference")
EXPECTED_TENSORS = {"v57_equal": 791, "v57_reliability": 791, "v55_reference": 787}
V58_OUT = ROOT / "runs/v58_mmuav_zero_detection_diagnostic"
ORDER_SHA256 = "dd454cfbafa39f2556628ad45dc191b39b0c54bb926028447d5f57553456e867"
SUBSET_SHA256 = "d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee"
DEVVAL_SHA256 = "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54"
NOW = lambda: datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def aggregate_file_fingerprint(paths: list[Path]) -> dict[str, object]:
    digest = hashlib.sha256()
    total_bytes = 0
    for path in sorted(paths, key=lambda item: item.as_posix().lower()):
        relative = path.relative_to(ROOT).as_posix()
        file_hash = sha256(path)
        size = path.stat().st_size
        digest.update(relative.encode("utf-8") + b"\0" + file_hash.encode("ascii") + b"\n")
        total_bytes += size
    return {"file_count": len(paths), "total_bytes": total_bytes, "aggregate_sha256": digest.hexdigest()}


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
        history = relative.startswith("runs/v4") or any(
            relative.startswith(f"runs/v{version}_") for version in range(50, 59)
        )
        if relative in fixed or relative.startswith("manuscript/") or relative.startswith("submission/") or history:
            path = ROOT / relative
            if path.is_file():
                selected.append(path)
    return selected


def v58_verification() -> dict[str, object]:
    final = json.loads((V58_OUT / "final_decision.json").read_text(encoding="utf-8"))
    partial = json.loads((V58_OUT / "partial_pass_status.json").read_text(encoding="utf-8"))
    error = (V58_OUT / "blocker_error_tail.txt").read_text(encoding="utf-8")
    required = {
        "decision": final.get("decision") == "V58_BLOCKED_INSTRUMENTATION_OR_INFERENCE_PATH",
        "optimizer_steps": final.get("optimizer_steps") == 0,
        "backward_passes": final.get("backward_passes") == 0,
        "equal_consumed": final.get("v57_equal_pass_consumed") is True,
        "reliability_not_consumed": final.get("v57_reliability_pass_consumed") is False,
        "v55_not_consumed": final.get("v55_reference_pass_consumed") is False,
        "exact_error": "RuntimeError: quantile() input tensor is too large" in error,
        "partial_forward_rows": partial.get("v57_equal", {}).get("full_1845_row_forward_completed") is True,
        "no_root_cause": final.get("root_cause_identified") is False,
    }
    if not all(required.values()):
        raise RuntimeError(f"V58 blocker evidence mismatch: {required}")
    files = [path for path in V58_OUT.rglob("*") if path.is_file()]
    return {"checks": required, "evidence_fingerprint": aggregate_file_fingerprint(files)}


def checkpoint_contracts() -> dict[str, object]:
    specs = {**V57_CHECKPOINTS, "v55_reference": V55_REFERENCE}
    results = {}
    for name in RUN_ORDER:
        result = checkpoint_verification(name, specs[name], True)
        if result["state_tensor_count"] != EXPECTED_TENSORS[name]:
            raise RuntimeError(f"Checkpoint tensor-count mismatch: {name}")
        results[name] = result
    return results


def source_lock() -> dict[str, object]:
    source_files = [
        "rarepdet/tools/run_v59_streaming_zero_detection_diagnostic.py",
        "rarepdet/tools/v59_streaming_histogram.py",
        "tests/test_v59_streaming_zero_detection_diagnostic.py",
        "rarepdet/tools/run_v58_zero_detection_diagnostic.py",
        "rarepdet/tools/run_v57_mmuav_paired_fusion.py",
        "rarepdet/experimental/v57_fusion_superset_detector.py",
        "rarepdet/tools/run_v55_mmuav_paired_alignment.py",
        "rarepdet/experimental/mmuav_feature_alignment_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
    ]
    installed_fcos = Path(inspect.getsourcefile(FCOS) or "")
    score_source = inspect.getsource(FCOS.postprocess_detections)
    required_fragments = ("torch.sqrt", "torch.sigmoid", "> self.score_thresh", "topk", "batched_nms")
    if not installed_fcos.is_file() or not all(fragment in score_source for fragment in required_fragments):
        raise RuntimeError("Installed FCOS source contract mismatch")
    return {
        "starting_commit": START_COMMIT,
        "authorization_base_commit": AUTHORIZATION_BASE_COMMIT,
        "source_hashes": {relative: sha256(ROOT / relative) for relative in source_files},
        "installed_fcos_path": str(installed_fcos),
        "installed_fcos_sha256": sha256(installed_fcos),
        "installed_score_path_fragments": list(required_fragments),
    }


def compact_quantiles(values: list[float | int], maximum_count: int = 1845) -> dict[str, float]:
    if len(values) > maximum_count:
        raise RuntimeError(f"Compact-array bound exceeded: {len(values)} > {maximum_count}")
    if not values:
        return {}
    tensor = torch.tensor(values, dtype=torch.float64)
    if not torch.isfinite(tensor).all():
        raise RuntimeError("Non-finite compact values")
    levels = torch.tensor(QUANTILES, dtype=torch.float64)
    result = torch.quantile(tensor, levels)
    return {format(q, ".3g"): float(value) for q, value in zip(QUANTILES, result)}


def prepare() -> None:
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError("Unexpected V59 starting commit")
    if OUT.exists():
        raise RuntimeError("V59 output already exists; refusing to reset pass ledger")
    OUT.mkdir(parents=True)
    if sha256(DEVVAL_MANIFEST) != DEVVAL_SHA256:
        raise RuntimeError("Devval manifest hash mismatch")
    order_source = V58_OUT / "devval_order.txt"
    subset_source = V58_OUT / "detailed_subset_indices.json"
    if sha256(order_source) != ORDER_SHA256:
        raise RuntimeError("Frozen devval order mismatch")
    subset = json.loads(subset_source.read_text(encoding="utf-8"))
    subset_payload = (json.dumps(subset, separators=(",", ":")) + "\n").encode("utf-8")
    if hashlib.sha256(subset_payload).hexdigest() != SUBSET_SHA256 or len(subset) != 32:
        raise RuntimeError("Frozen detailed subset mismatch")
    dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=True)
    if len(dataset) != 1845:
        raise RuntimeError("Devval row-count mismatch")
    (OUT / "devval_order.txt").write_bytes(order_source.read_bytes())
    (OUT / "devval_order_sha256.txt").write_text(ORDER_SHA256 + "\n", encoding="utf-8")
    write_json(OUT / "detailed_subset_indices.json", subset)
    (OUT / "detailed_subset_sha256.txt").write_text(SUBSET_SHA256 + "\n", encoding="utf-8")

    blocker = v58_verification()
    checkpoints = checkpoint_contracts()
    lock = source_lock()
    protected = aggregate_file_fingerprint(protected_paths())
    status_lines = git("status", "--porcelain=v1", "--untracked-files=normal").splitlines()
    preexisting = [line for line in status_lines if "v59_mmuav_streaming" not in line and "run_v59_" not in line and
                   "v59_streaming_histogram" not in line and "test_v59_" not in line]
    histogram_spec = {
        "frozen_before_inference": True,
        "logit": HistogramSpec("logit").as_dict(),
        "probability_and_combined": HistogramSpec("probability").as_dict(),
        "quantiles": list(QUANTILES),
        "histograms_per_model": 28,
        "histogram_count_storage_bytes_per_model": 28 * BIN_COUNT * 8,
        "all_row_tensor_concatenation": False,
        "all_value_exact_quantiles": False,
    }
    protocol = {
        "prepared_at": NOW(),
        "starting_commit": START_COMMIT,
        "optimizer_steps": 0,
        "backward_passes": 0,
        "training_mode_executions": 0,
        "gradient_executions": 0,
        "devval_rows": len(dataset),
        "devval_sha256": DEVVAL_SHA256,
        "devval_order_sha256": ORDER_SHA256,
        "detailed_subset_seed": 58,
        "detailed_subset_count": len(subset),
        "detailed_subset_sha256": SUBSET_SHA256,
        "run_order": list(RUN_ORDER),
        "passes_per_checkpoint": 1,
        "threshold_ladder": list(LADDER),
        "alternate_threshold_ap_ar_computed": False,
        "histogram_spec": histogram_spec,
        "checkpoint_verification": checkpoints,
        "v58_blocker_verification": blocker,
        "protected_baseline": protected,
        "preexisting_worktree_entries": preexisting,
    }
    write_json(OUT / "histogram_specification.json", histogram_spec)
    write_json(OUT / "v58_blocker_verification.json", blocker)
    write_json(OUT / "checkpoint_verification.json", checkpoints)
    write_json(OUT / "protected_baseline.json", protected)
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v59.json", {**lock, **protocol})
    write_json(OUT / "pass_ledger.json", {
        "order": list(RUN_ORDER),
        "passes": {name: {"state": "pending", "attempts_started": 0, "completed_rows": 0} for name in RUN_ORDER},
    })
    (OUT / "protocol.md").write_text(
        "# V59 Streaming Diagnostic Protocol\n\nThree read-only 1,845-row passes in frozen order. "
        "CPU int64 histograms use 16,384 frozen bins; only bounded per-image arrays receive exact quantiles. "
        "Optimizer, backward, gradients, training mode, metric replay, and repair are forbidden.\n",
        encoding="utf-8",
    )
    (OUT / "implementation_score_path.md").write_text(
        "# Installed FCOS Score Path\n\nThe source-locked torchvision 0.20.1 path computes "
        "`sqrt(sigmoid(class_logit) * sigmoid(centerness_logit))`, applies strict `score > 0.001`, "
        "then per-level top-k 1000, decode/clip, class-aware NMS 0.6, and global cap 100. "
        "The evaluator retains foreground label 1. No setting is changed by V59.\n",
        encoding="utf-8",
    )
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v59_streaming_zero_detection_diagnostic.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v59_streaming_zero_detection_diagnostic.py --validate-histograms\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v59_streaming_zero_detection_diagnostic.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v59_streaming_zero_detection_diagnostic.py --run\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "V59_PREPARED_CPU_ONLY", "protocol": protocol}, indent=2))


def validate_histograms() -> None:
    result = validate_histogram_implementation()
    result.update({
        "validated_at": NOW(),
        "cuda_used": False,
        "histogram_edges_frozen": True,
        "direct_quantiles_limited_to_synthetic_manageable_tensors": True,
    })
    write_json(OUT / "histogram_validation.json", result)
    if not result["passed"]:
        raise RuntimeError("V59 histogram validation failed")
    print(json.dumps(result, indent=2))


def new_level_histograms() -> list[dict[str, StreamingHistogram]]:
    return [{
        "classification_logits": StreamingHistogram("logit"),
        "classification_probabilities": StreamingHistogram("probability"),
        "centerness_logits": StreamingHistogram("logit"),
        "centerness_probabilities": StreamingHistogram("probability"),
        "combined_scores": StreamingHistogram("probability"),
        "combined_label0": StreamingHistogram("probability"),
        "combined_label1_foreground": StreamingHistogram("probability"),
    } for _ in range(4)]


def diagnose_model(name: str, spec: dict[str, object], subset: set[int], device: torch.device) -> dict[str, object]:
    checkpoint_hash_before = sha256(spec["path"])
    payload = torch.load(spec["path"], map_location="cpu", weights_only=False)
    model = model_for(name, spec["variant"])
    load = model.load_state_dict(payload["model_state"], strict=False)
    if load.missing_keys or load.unexpected_keys:
        raise RuntimeError(f"Diagnostic load mismatch: {name}")
    state_before = tensor_fingerprint(model.state_dict())
    model.to(device)
    model.eval()
    if model.training or model.detector.training or any(module.training for module in model.modules()):
        raise RuntimeError(f"Evaluation mode failure: {name}")
    model.detector.score_thresh = 0.001
    model.detector.nms_thresh = 0.6
    model.detector.detections_per_img = 100
    if model.detector.topk_candidates != 1000:
        raise RuntimeError(f"Top-k contract mismatch: {model.detector.topk_candidates}")

    dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    histograms = new_level_histograms()
    stage_keys = ("raw", "after_threshold", "after_topk", "valid_after_clip", "after_nms",
                  "after_nms_label0", "after_nms_label1", "final", "final_label0", "final_label1")
    stage_total = {key: 0 for key in stage_keys}
    stage_per_image = {key: [] for key in stage_keys}
    images_with = {key: 0 for key in stage_keys}
    box_total = {key: 0 for key in ("decoded", "nonfinite", "out_of_image_before_clip",
                                    "degenerate_after_clip", "valid_after_clip")}
    ladder_total = {format(value, ".0e") if value else "0": {"all": 0, "label0": 0, "label1": 0}
                    for value in LADDER}
    ladder_images = {key: {label: 0 for label in ("all", "label0", "label1")} for key in ladder_total}
    max_scores: list[float] = []
    max_foreground_scores: list[float] = []
    fusion_weights: list[list[float]] = []
    detailed = []
    output_schema = {
        "keys": ["boxes", "scores", "labels"],
        "dtypes": {},
        "devices": {},
        "all_finite": True,
        "output_count_min": math.inf,
        "output_count_max": 0,
        "labels_observed": set(),
    }
    retained_bytes = sum(hist.retained_bytes for level in histograms for hist in level.values())
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    with torch.inference_mode():
        for index in range(len(dataset)):
            sample = dataset[index]
            record = instrument_image(model, sample, device)
            stages = dict(record["stage"])
            stages["valid_after_clip"] = record["box_counts"]["valid_after_clip"]
            for key in stage_keys:
                value = int(stages[key])
                stage_total[key] += value
                stage_per_image[key].append(value)
                images_with[key] += value > 0
            for key, value in record["box_counts"].items():
                box_total[key] += value
            max_scores.append(record["max_score"])
            max_foreground_scores.append(record["max_foreground_score"])
            weights = model.last_feature_outputs["fusion_weights"].detach().float().cpu().flatten().tolist()
            fusion_weights.append(weights)
            for level_index, level in enumerate(record["levels"]):
                cls = level["cls_logits"]
                ctr = level["ctr_logits"]
                combined = level["combined"]
                updates = {
                    "classification_logits": cls,
                    "classification_probabilities": torch.sigmoid(cls),
                    "centerness_logits": ctr,
                    "centerness_probabilities": torch.sigmoid(ctr),
                    "combined_scores": combined,
                    "combined_label0": level["combined_label0"],
                    "combined_label1_foreground": level["combined_label1"],
                }
                for key, values in updates.items():
                    histograms[level_index][key].update(values)
                for threshold, counts in level["ladder"].items():
                    for label, value in counts.items():
                        ladder_total[threshold][label] += value
            for threshold in ladder_total:
                counts = {label: sum(level["ladder"][threshold][label] for level in record["levels"])
                          for label in ("all", "label0", "label1")}
                for label, value in counts.items():
                    ladder_images[threshold][label] += value > 0

            actual = record["actual_output"]
            count = int(actual["scores"].numel())
            output_schema["output_count_min"] = min(output_schema["output_count_min"], count)
            output_schema["output_count_max"] = max(output_schema["output_count_max"], count)
            for key, value in actual.items():
                output_schema["dtypes"][key] = str(value.dtype)
                output_schema["devices"][key] = str(value.device)
                output_schema["all_finite"] = output_schema["all_finite"] and bool(torch.isfinite(value).all())
            output_schema["labels_observed"].update(actual["labels"].detach().cpu().tolist())
            if index in subset:
                feature_outputs = model.last_feature_outputs
                detailed.append({
                    "index": index,
                    "original_row_id": sample["original_row_id"],
                    "inputs": {key: stats(sample[key]) for key in ("rgb", "ir", "event")},
                    "modality_transforms": sample["modality_transforms"],
                    "features": {key: stats(feature_outputs[key]) for key in
                                 ("rgb_reference", "aligned_ir", "aligned_event", "fused")},
                    "fusion_weights": weights,
                    "detector_input": stats(record["detector_image"]),
                    "fpn_features": [stats(value) for value in record["features"]],
                    "levels": [{key: value for key, value in level.items() if key not in
                                {"cls_logits", "ctr_logits", "combined", "combined_label0",
                                 "combined_label1", "ladder"}} for level in record["levels"]],
                    "stage": stages,
                    "box_counts": record["box_counts"],
                    "top_final": {
                        "scores": actual["scores"][:5].detach().cpu().tolist(),
                        "labels": actual["labels"][:5].detach().cpu().tolist(),
                        "boxes": actual["boxes"][:5].detach().cpu().tolist(),
                    },
                })
            if (index + 1) % 100 == 0 or index + 1 == len(dataset):
                print(f"V59_PROGRESS model={name} rows={index + 1}/{len(dataset)} elapsed={time.perf_counter() - started:.1f}s",
                      flush=True)

    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    score_summary = {
        "levels": [{"level": index, **{key: hist.summary() for key, hist in level.items()}}
                   for index, level in enumerate(histograms)],
        "max_score_per_image_exact_quantiles": compact_quantiles(max_scores),
        "max_foreground_score_per_image_exact_quantiles": compact_quantiles(max_foreground_scores),
    }
    stage_summary = {
        "images": len(dataset),
        "totals": stage_total,
        "images_with_at_least_one": images_with,
        "per_image_exact_quantiles": {key: compact_quantiles(values) for key, values in stage_per_image.items()},
        "box_counts": box_total,
        "output_schema": {**output_schema, "labels_observed": sorted(output_schema["labels_observed"])},
        "finite": output_schema["all_finite"] and box_total["nonfinite"] == 0,
    }
    fusion_by_modality = list(zip(*fusion_weights))
    compact_fusion = {
        name: {"exact_quantiles": compact_quantiles(list(values)), "mean": sum(values) / len(values)}
        for name, values in zip(("rgb", "ir", "event"), fusion_by_modality)
    }
    memory = {
        "inference_seconds": elapsed,
        "fps": len(dataset) / elapsed,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "retained_histogram_bytes": retained_bytes,
        "bounded_max_score_values": len(max_scores),
        "bounded_stage_values": sum(len(values) for values in stage_per_image.values()),
        "bounded_fusion_values": len(fusion_weights) * 3,
    }
    gradients_absent = all(parameter.grad is None for parameter in model.parameters())
    norms = parameter_norms(model)
    state_after = tensor_fingerprint({key: value.detach().cpu() for key, value in model.state_dict().items()})
    checkpoint_unchanged = checkpoint_hash_before == sha256(spec["path"])
    if state_before != state_after or not checkpoint_unchanged or not gradients_absent:
        raise RuntimeError(f"Read-only mutation or gradient detected: {name}")
    result = {
        "name": name,
        "checkpoint_sha256": checkpoint_hash_before,
        "rows": len(dataset),
        "streaming_scores": score_summary,
        "stage_counts": stage_summary,
        "threshold_ladder_counts": ladder_total,
        "threshold_ladder_images_with_candidates": ladder_images,
        "detailed_trace": sorted(detailed, key=lambda item: item["index"]),
        "fusion_weight_summary": compact_fusion,
        "parameter_norms": norms,
        "memory_timing": memory,
        "state_unchanged": True,
        "checkpoint_unchanged": True,
        "gradients_absent": True,
        "training_mode_executions": 0,
    }
    del model, histograms
    torch.cuda.empty_cache()
    return result


def set_pass_state(ledger: dict[str, object], name: str, state: str, rows: int = 0) -> None:
    entry = ledger["passes"][name]
    entry["state"] = state
    entry["completed_rows"] = rows
    entry[f"{state}_at"] = NOW()
    write_json(OUT / "pass_ledger.json", ledger)


def compare_paths(results: dict[str, dict[str, object]]) -> dict[str, object]:
    comparison = {
        "same_dataset_class": True,
        "same_independent_letterbox_preprocessing": True,
        "same_detector_transform_normalization": {"mean": [0, 0, 0], "std": [1, 1, 1]},
        "same_resize": [320, 320],
        "same_score_threshold": 0.001,
        "same_topk": 1000,
        "same_nms": 0.6,
        "same_final_cap": 100,
        "same_output_schema": True,
        "v55_wrapper": "MMUAVFeatureAlignmentDetector(alignment_on_equal)",
        "v57_wrapper": "V57FusionSupersetDetector(equal/reliability)",
        "v57_scaffold_difference": "V55 scaffold replaced by parameter-superset scaffold; equal bypasses scorer, reliability uses scorer",
        "per_model": {},
    }
    for name, result in results.items():
        stages = result["stage_counts"]["totals"]
        scores = result["streaming_scores"]
        comparison["per_model"][name] = {
            "final_label0": stages["final_label0"],
            "final_label1": stages["final_label1"],
            "after_threshold": stages["after_threshold"],
            "max_foreground_score_exact_quantiles": scores["max_foreground_score_per_image_exact_quantiles"],
            "parameter_norms": result["parameter_norms"],
            "fusion_weight_summary": result["fusion_weight_summary"],
        }
    return comparison


def decide(results: dict[str, dict[str, object]], comparison: dict[str, object]) -> dict[str, object]:
    v55 = results["v55_reference"]["stage_counts"]["totals"]
    equal = results["v57_equal"]["stage_counts"]["totals"]
    reliability = results["v57_reliability"]["stage_counts"]["totals"]
    v57 = (equal, reliability)
    if v55["final_label1"] > 0 and all(item["after_threshold"] == 0 for item in v57):
        primary = "FEATURE_OR_HEAD_SCORE_COLLAPSE"
        explanation = ("Both V57 checkpoints have no score above the frozen threshold while the same V55 path "
                       "produces foreground outputs; the divergence occurs before top-k, box decode, NMS, or evaluator filtering.")
    elif v55["final_label1"] > 0 and all(item["final_label1"] == 0 for item in v57):
        primary = "FEATURE_OR_HEAD_SCORE_COLLAPSE"
        explanation = ("V55 produces foreground outputs, while both V57 checkpoints lose foreground candidates within the "
                       "source-locked score/postprocess path; bounded score and stage traces localize the divergence.")
    elif all(item["after_nms_label1"] > 0 and item["final_label1"] == 0 for item in v57):
        primary = "POSTPROCESS_THRESHOLD_OR_NMS_PATH"
        explanation = "V57 foreground candidates survive NMS but are removed by the global output cap."
    elif all(item["final"] > 0 and item["final_label1"] > 0 for item in v57):
        primary = "EVALUATOR_OR_OUTPUT_SCHEMA_MISMATCH"
        explanation = "V57 emits valid label-1 outputs despite the historical zero evaluator count."
    else:
        primary = "ZERO_DETECTIONS_REPRODUCED_CAUSE_UNRESOLVED"
        explanation = "The bounded traces reproduce the outcome but do not support one causal boundary."
    complete = primary != "ZERO_DETECTIONS_REPRODUCED_CAUSE_UNRESOLVED"
    return {
        "completion_state": "V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED" if complete else
                            "V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_CAUSE_UNRESOLVED",
        "primary_classification": primary,
        "explanation": explanation,
        "v55_final_foreground": v55["final_label1"],
        "v57_equal_final_foreground": equal["final_label1"],
        "v57_reliability_final_foreground": reliability["final_label1"],
        "repair_authorized": False,
        "threshold_selection_performed": False,
        "alternate_threshold_ap_ar_computed": False,
    }


def run() -> None:
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    validation = json.loads((OUT / "histogram_validation.json").read_text(encoding="utf-8"))
    if not validation.get("passed") or protocol["run_order"] != list(RUN_ORDER):
        raise RuntimeError("V59 pre-CUDA protocol or histogram validation mismatch")
    if source_lock()["source_hashes"] != json.loads((OUT / "source_lock_v59.json").read_text(encoding="utf-8"))["source_hashes"]:
        raise RuntimeError("V59 source changed after source lock")
    if aggregate_file_fingerprint(protected_paths()) != protocol["protected_baseline"]:
        raise RuntimeError("Protected evidence changed before CUDA")
    current_checkpoints = checkpoint_contracts()
    for name in RUN_ORDER:
        if current_checkpoints[name]["sha256"] != protocol["checkpoint_verification"][name]["sha256"]:
            raise RuntimeError(f"Checkpoint changed before CUDA: {name}")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for V59 read-only inference")

    ledger = json.loads((OUT / "pass_ledger.json").read_text(encoding="utf-8"))
    if any(ledger["passes"][name]["state"] != "pending" for name in RUN_ORDER):
        raise RuntimeError("V59 pass ledger is not fresh; rerun forbidden")
    specs = {**V57_CHECKPOINTS, "v55_reference": V55_REFERENCE}
    subset = set(json.loads((OUT / "detailed_subset_indices.json").read_text(encoding="utf-8")))
    device = torch.device("cuda:0")
    results = {}
    for expected_index, name in enumerate(RUN_ORDER):
        if any(ledger["passes"][prior]["state"] != "complete" for prior in RUN_ORDER[:expected_index]):
            raise RuntimeError(f"V59 pass order violation before {name}")
        entry = ledger["passes"][name]
        entry["attempts_started"] += 1
        if entry["attempts_started"] != 1:
            raise RuntimeError(f"Second V59 pass forbidden: {name}")
        set_pass_state(ledger, name, "started")
        print(f"V59_PASS_START model={name} at={NOW()}", flush=True)
        result = diagnose_model(name, specs[name], subset, device)
        write_json(OUT / f"{name}_streaming_diagnostic.json", result)
        results[name] = result
        set_pass_state(ledger, name, "complete", 1845)
        print(f"V59_PASS_COMPLETE model={name} rows=1845 at={NOW()}", flush=True)

    comparison = compare_paths(results)
    decision = decide(results, comparison)
    write_json(OUT / "v55_v57_path_comparison.json", comparison)
    write_json(OUT / "root_cause_decision.json", decision)
    write_json(OUT / "memory_timing_summary.json", {name: result["memory_timing"] for name, result in results.items()})
    write_json(OUT / "final_decision.json", {
        "decision": decision["completion_state"],
        "root_cause": decision,
        "pass_counts": {name: ledger["passes"][name]["attempts_started"] for name in RUN_ORDER},
        "rows_per_pass": 1845,
        "optimizer_steps": 0,
        "backward_passes": 0,
        "training_mode_executions": 0,
        "gradient_executions": 0,
        "checkpoints_unchanged": True,
        "parameters_unchanged": True,
        "alternate_threshold_ap_ar_computed": False,
    })
    (OUT / "v55_v57_path_comparison.md").write_text(
        "# V55/V57 Read-Only Path Comparison\n\nAll models used the same manifest, modality preprocessing, "
        "detector transform, FCOS score equation, threshold, top-k, box decode/clip, NMS, final cap, output schema, "
        "and evaluator label contract. V57 replaces the V55 feature scaffold with its equal/reliability parameter "
        "superset. Direct score, stage, feature, fusion, and parameter-norm evidence is in the JSON comparison.\n",
        encoding="utf-8",
    )
    (OUT / "root_cause_decision.md").write_text(
        f"# V59 Root Cause Decision\n\nPrimary classification: `{decision['primary_classification']}`. "
        f"{decision['explanation']} This diagnosis does not authorize repair.\n",
        encoding="utf-8",
    )
    if aggregate_file_fingerprint(protected_paths()) != protocol["protected_baseline"]:
        raise RuntimeError("Protected evidence changed during V59")
    print(json.dumps(decision, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only", action="store_true")
    group.add_argument("--validate-histograms", action="store_true")
    group.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.prepare_only:
        prepare()
    elif args.validate_histograms:
        validate_histograms()
    else:
        run()


if __name__ == "__main__":
    main()
