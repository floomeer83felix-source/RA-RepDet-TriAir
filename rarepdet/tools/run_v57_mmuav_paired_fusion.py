"""Prepare and run the frozen V57 paired MM-UAV fusion ablation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.coco_metrics import coco_detection_metrics
from rarepdet.experimental.v57_fusion_superset_detector import VARIANTS, V57FusionSupersetDetector
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import (
    DEVVAL_MANIFEST,
    TRAIN_MANIFEST,
    configure_seed,
    gradient_norm,
    inputs_to_device,
    target_to_device,
    validate_data_contract,
)


OUT = ROOT / "runs/v57_mmuav_paired_fusion_ablation"
V56 = ROOT / "runs/v56_mmuav_multiseed_alignment_confirmation"
LOCAL = Path(r"D:\MM-UAV_v57_local")
COMMON_INIT = LOCAL / "common_seed0_superset_init.pt"
START_COMMIT = "6b767d0c23ca9b918edaed601ae999c9d9b0d6ee"
STEPS_PER_VARIANT = 7187
TOTAL_STEP_LIMIT = 14374
TRACE_STEPS = {0, 1, 10, 50, 100, 200, 500, 1000, 2000, 4000, 6000, 7187}
METRIC_KEYS = ("ap50_95", "ap50", "ap75", "ar100")
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
LOG_FIELDS = [
    "variant", "step", "original_row_id", "loss_total", "loss_classifier", "loss_box_reg",
    "loss_centerness", "learning_rate", "global_gradient_norm", "reliability_scorer_gradient_norm",
    "active_gradient_parameter_count", "rgb_weight", "ir_weight", "event_weight", "weight_sum_error",
    "fusion_entropy", "dominance_fraction", "ir_theta_max_abs_deviation", "ir_determinant_mean",
    "ir_grid_oob_fraction", "event_theta_max_abs_deviation", "event_determinant_mean",
    "event_grid_oob_fraction", "finite", "cuda_allocated_bytes", "cuda_reserved_bytes", "data_time_sec",
    "forward_time_sec", "backward_time_sec", "optimizer_time_sec", "step_time_sec",
]
V56_EXPECTED = {
    "ap50_95_off_mean": 0.024852009216029355,
    "ap50_95_on_mean": 0.0418382404232167,
    "ap50_95_paired_delta_mean": 0.01698623120718734,
    "direction_counts": {"ap50_95": 3, "ap50": 3, "ap75": 1, "ar100": 3},
}


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


def checkpoint_path(variant: str) -> Path:
    return LOCAL / f"{variant}_final_step7187.pt"


def shared_config() -> dict[str, object]:
    return {
        "seed": 0, "image_size": 320, "batch_size": 1, "precision": "float32", "amp_enabled": False,
        "feature_channels": 32, "fpn_out_channels": 128, "backbone": "RepViT-M0.9",
        "backbone_pretrained": False, "detector": "FCOS", "alignment_enabled": True,
        "optimizer": "AdamW", "learning_rate": 1e-4, "weight_decay": 1e-4, "scheduler": "none",
        "gradient_clipping": "none", "augmentation": "none", "steps_per_variant": STEPS_PER_VARIANT,
        "total_step_limit": TOTAL_STEP_LIMIT, "num_workers": 0, "train_manifest": str(TRAIN_MANIFEST),
        "devval_optimization": False, "early_stopping": False, "checkpoint_selection": False,
        "run_order": list(VARIANTS), "superset_reliability_scorer_present": True,
    }


def variant_config(variant: str) -> dict[str, object]:
    config = dict(shared_config())
    config.update({"variant": variant, "fusion_behavior": "equal_bypass" if variant == VARIANTS[0] else
                   "reliability_active", "final_checkpoint": str(checkpoint_path(variant))})
    return config


def verify_v56_evidence() -> dict[str, object]:
    aggregation_path = V56 / "three_seed_aggregation.json"
    decision_path = V56 / "final_decision.json"
    protocol_path = V56 / "protocol.json"
    aggregation = json.loads(aggregation_path.read_text(encoding="utf-8"))
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    summary = aggregation["summaries"]["ap50_95"]
    observed = {
        "ap50_95_off_mean": summary["off_mean"],
        "ap50_95_on_mean": summary["on_mean"],
        "ap50_95_paired_delta_mean": summary["paired_delta_mean"],
        "direction_counts": {key: aggregation["summaries"][key]["positive_seed_count"] for key in METRIC_KEYS},
    }
    if observed != V56_EXPECTED or not aggregation["ap50_95_direction_consistency"]["all_positive"]:
        raise RuntimeError(f"V56 evidence mismatch: {observed}")
    if decision["decision"] != "V56_THREE_SEED_PAIRED_ALIGNMENT_CONFIRMATION_COMPLETE":
        raise RuntimeError("V56 completion decision mismatch")
    return {"executed_v55_or_v56": False, **observed, "source_file_sha256": {
        "three_seed_aggregation.json": sha256(aggregation_path),
        "final_decision.json": sha256(decision_path),
        "protocol.json": sha256(protocol_path),
    }}


def protected_source_lock() -> dict[str, object]:
    changed = set(git("diff", "--name-only", START_COMMIT).splitlines())
    protected = {
        "rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py", "main.tex",
        "main_sivp_snjnl.tex",
    }
    forbidden = sorted(path for path in changed if path in protected or path.startswith("manuscript/") or
                       path.startswith("submission/") or (path.startswith("runs/v5") and not
                       path.startswith("runs/v57_mmuav_paired_fusion_ablation/")))
    if forbidden:
        raise RuntimeError(f"Protected path changes: {forbidden}")
    sources = [
        "rarepdet/experimental/v57_fusion_superset_detector.py",
        "rarepdet/tools/run_v57_mmuav_paired_fusion.py",
        "tests/test_v57_mmuav_paired_fusion.py",
        "rarepdet/tools/run_v56_mmuav_multiseed_alignment.py",
        "rarepdet/experimental/mmuav_feature_alignment_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
    ]
    return {"starting_commit": START_COMMIT, "protected_changes": [],
            "source_hashes": {path: sha256(ROOT / path) for path in sources}}


def parameter_signature(model: torch.nn.Module) -> dict[str, list[int]]:
    return {name: list(parameter.shape) for name, parameter in model.named_parameters()}


def create_common_init() -> dict[str, object]:
    if COMMON_INIT.exists():
        raise RuntimeError(f"Refusing to overwrite V57 common init: {COMMON_INIT}")
    configure_seed(0)
    model = V57FusionSupersetDetector(VARIANTS[1])
    identity = torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    if not torch.equal(model.feature_scaffold.ir_aligner.identity_theta, identity) or not torch.equal(
            model.feature_scaffold.event_aligner.identity_theta, identity):
        raise RuntimeError("Alignment initialization is not exact identity")
    final = model.feature_scaffold.reliability_scorer[-1]
    if not torch.equal(final.weight, torch.zeros_like(final.weight)) or not torch.equal(
            final.bias, torch.zeros_like(final.bias)):
        raise RuntimeError("Reliability scorer final layer is not exact zero")
    sample = torch.zeros(1, 3, 320, 320), torch.zeros(1, 1, 320, 320), torch.zeros(1, 1, 320, 320)
    model.eval()
    with torch.no_grad():
        model._feature_forward(*sample)
    weights = model.last_feature_outputs["fusion_weights"]
    uniform = torch.full_like(weights, 1.0 / 3.0)
    if not torch.equal(weights, uniform):
        raise RuntimeError("Reliability scorer does not initialize to exact uniform weights")
    state = {key: value.detach().cpu() for key, value in model.state_dict().items()}
    torch.save({"state_dict": state, "seed": 0, "source": "fresh_untrained_V57_fusion_superset"}, COMMON_INIT)
    total_parameters = sum(parameter.numel() for parameter in model.parameters())
    scorer_parameters = sum(parameter.numel() for parameter in model.feature_scaffold.reliability_scorer.parameters())
    return {"path_local_not_committed": str(COMMON_INIT), "sha256": sha256(COMMON_INIT),
            "bytes": COMMON_INIT.stat().st_size, "tensor_count": len(state), "seed": 0,
            "alignment_identity_exact": True, "reliability_final_layer_exact_zero": True,
            "initial_weights_exact_uniform": True, "total_parameter_count": total_parameters,
            "reliability_scorer_parameter_count": scorer_parameters,
            "parameter_signature_sha256": hashlib.sha256(json.dumps(parameter_signature(model), sort_keys=True).encode()).hexdigest()}


def write_sample_order(dataset: MMUAVFeatureAlignmentDataset) -> dict[str, object]:
    order = torch.randperm(len(dataset), generator=torch.Generator(device="cpu").manual_seed(0)).tolist()
    ids = [dataset.rows[index]["original_row_id"] for index in order]
    if len(order) != STEPS_PER_VARIANT or len(set(order)) != STEPS_PER_VARIANT or len(set(ids)) != STEPS_PER_VARIANT:
        raise RuntimeError("V57 sample order is not a full unique permutation")
    payload = ("\n".join(ids) + "\n").encode("utf-8")
    (OUT / "shared_sample_order.txt").write_bytes(payload)
    write_json(OUT / "shared_sample_indices.json", order)
    digest = hashlib.sha256(payload).hexdigest()
    (OUT / "shared_sample_order_sha256.txt").write_text(digest + "\n", encoding="utf-8")
    return {"rows": len(ids), "unique_rows": len(set(ids)), "sha256": digest}


def prepare() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    if (OUT / "protocol.json").exists():
        raise RuntimeError("V57 protocol already exists; refusing to regenerate")
    contract = validate_data_contract()
    v56 = verify_v56_evidence()
    lock = protected_source_lock()
    dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=True)
    init = create_common_init()
    order = write_sample_order(dataset)
    models = [V57FusionSupersetDetector(variant) for variant in VARIANTS]
    signatures = [parameter_signature(model) for model in models]
    if signatures[0] != signatures[1]:
        raise RuntimeError("V57 superset parameter names/shapes differ")
    configs = {variant: variant_config(variant) for variant in VARIANTS}
    differences = [key for key in configs[VARIANTS[0]] if configs[VARIANTS[0]][key] != configs[VARIANTS[1]][key]]
    if set(differences) != {"variant", "fusion_behavior", "final_checkpoint"}:
        raise RuntimeError(f"Unexpected paired config differences: {differences}")
    evaluation = {"rows": 1845, "checkpoint": "final_step7187_only", "score_threshold": 0.001,
                  "nms_threshold": 0.6, "max_detections": 100, "metrics": list(METRIC_KEYS),
                  "evaluation_count_per_variant": 1}
    protocol = {"prepared_at": NOW, "starting_commit": START_COMMIT, "contract": contract,
                "v56_evidence": v56, "common_init": init, "sample_order": order,
                "variant_configs": configs, "paired_config_differences": differences,
                "superset_parameter_names_shapes_identical": True,
                "only_scientific_difference": "fusion scorer output bypassed or used", "evaluation": evaluation}
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v57.json", {**lock, "contract": contract, "v56_evidence": v56,
                                               "common_init": init, "sample_order": order,
                                               "gpu_step_limit": TOTAL_STEP_LIMIT})
    write_json(OUT / "v56_evidence_verification.json", v56)
    write_json(OUT / "common_init_metadata.json", init)
    write_json(OUT / "common_init_verification.json", {
        "variants": list(VARIANTS), "parameter_names_shapes_identical": True,
        "shared_tensors_bit_identical_at_step0": True, "alignment_enabled_both": True,
        "alignment_residual_heads_exact_zero": True, "identity_theta_exact": True,
        "reliability_final_layer_exact_zero": True, "initial_weights_exact_uniform": True,
    })
    for variant, config in configs.items():
        write_json(OUT / f"{variant}_config.json", config)
    write_json(OUT / "evaluation_protocol.json", evaluation)
    (OUT / "protocol.md").write_text(
        "# V57 Paired Fusion Protocol\n\nOne V57-only superset initialization and one shared seed-0 permutation. "
        "Alignment stays enabled; equal bypasses the scorer and reliability uses it. Each run has 7,187 steps.\n",
        encoding="utf-8")
    (OUT / "source_lock_v57.md").write_text(
        f"# V57 Source Lock\n\nStarting commit: `{START_COMMIT}`. Data and V56 evidence reproduce exactly; "
        "protected production, history, V51, and manuscript paths are unchanged.\n", encoding="utf-8")
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v57_mmuav_paired_fusion.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v57_mmuav_paired_fusion.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v57_mmuav_paired_fusion.py --run\n",
        encoding="utf-8")
    print(json.dumps({"status": "V57_PREPARED_CPU_ONLY", **protocol}, indent=2))


def load_common_state() -> tuple[dict[str, torch.Tensor], str]:
    metadata = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))["common_init"]
    if sha256(COMMON_INIT) != metadata["sha256"]:
        raise RuntimeError("V57 common initialization hash mismatch")
    payload = torch.load(COMMON_INIT, map_location="cpu", weights_only=False)
    return payload["state_dict"], metadata["sha256"]


def validate_fusion(model: V57FusionSupersetDetector, variant: str, require_initial_uniform: bool = False) -> dict[str, object]:
    diagnostics = model.fusion_diagnostics()
    weights = model.last_feature_outputs["fusion_weights"].detach()
    uniform = torch.full_like(weights, 1.0 / 3.0)
    if not diagnostics["finite"] or bool((weights < 0).any()) or bool((weights > 1).any()):
        raise RuntimeError(f"Invalid fusion weights: {variant}")
    if diagnostics["weight_sum_max_abs_error"] > 1e-6:
        raise RuntimeError(f"Fusion normalization failure: {variant}")
    if variant == VARIANTS[0] and not torch.equal(weights, uniform):
        raise RuntimeError("Equal fusion departed from exact uniform")
    if require_initial_uniform and not torch.equal(weights, uniform):
        raise RuntimeError("Reliability fusion did not start exact uniform")
    return diagnostics


def active_gradient_parameter_count(model: torch.nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.grad is not None)


def train_variant(variant: str, dataset: MMUAVFeatureAlignmentDataset, order: list[int],
                  common: dict[str, torch.Tensor], init_hash: str, device: torch.device,
                  total_completed_before: int) -> tuple[dict[str, object], Path]:
    if total_completed_before + STEPS_PER_VARIANT > TOTAL_STEP_LIMIT:
        raise RuntimeError("V57 total optimizer-step guard exceeded")
    configure_seed(0)
    model = V57FusionSupersetDetector(variant).to(device)
    model.load_state_dict(common, strict=True)
    current = model.state_dict()
    if current.keys() != common.keys() or not all(torch.equal(current[key].cpu(), common[key]) for key in current):
        raise RuntimeError("V57 model is not bit-identical to common initialization")
    scorer_initial = {name: value.detach().cpu().clone() for name, value in
                      model.feature_scaffold.reliability_scorer.state_dict().items()}
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    log_path = OUT / f"{variant}_training_log.csv"
    if log_path.exists():
        raise RuntimeError(f"Refusing to overwrite training log: {log_path}")
    handle = log_path.open("w", encoding="utf-8", newline="")
    writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS)
    writer.writeheader()
    alignment_trace, fusion_trace, losses_total, step_times = [], [], [], []
    scorer_ever_had_gradient = False
    reliability_departed = False
    first_active_count = None
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    completed = 0
    previous_end = time.perf_counter()
    try:
        for expected_step, index in enumerate(order, 1):
            if completed >= STEPS_PER_VARIANT or total_completed_before + completed >= TOTAL_STEP_LIMIT:
                raise RuntimeError("V57 optimizer-step guard exceeded")
            started = time.perf_counter()
            sample = dataset[index]
            data_done = time.perf_counter()
            inputs = inputs_to_device(sample, device)
            targets = target_to_device(sample, device)
            optimizer.zero_grad(set_to_none=True)
            forward_start = time.perf_counter()
            losses = model(*inputs, targets)
            total_loss = sum(losses.values())
            torch.cuda.synchronize()
            forward_done = time.perf_counter()
            if not losses or not all(torch.isfinite(value).all() for value in losses.values()):
                raise RuntimeError(f"Non-finite loss: {variant} step {expected_step}")
            alignment = model.alignment_diagnostics()
            fusion = validate_fusion(model, variant, require_initial_uniform=expected_step == 1)
            if expected_step == 1:
                alignment_trace.append({"step": 0, **alignment})
                fusion_trace.append({"step": 0, "reliability_scorer_gradient_norm": 0.0, **fusion})
            total_loss.backward()
            torch.cuda.synchronize()
            backward_done = time.perf_counter()
            global_norm, global_finite = gradient_norm(model.parameters())
            scorer_norm, scorer_finite = gradient_norm(model.feature_scaffold.reliability_scorer.parameters())
            scorer_has_gradient = any(parameter.grad is not None for parameter in
                                      model.feature_scaffold.reliability_scorer.parameters())
            scorer_ever_had_gradient = scorer_ever_had_gradient or scorer_has_gradient
            if variant == VARIANTS[0] and (scorer_has_gradient or scorer_norm != 0.0):
                raise RuntimeError("Equal variant dormant scorer received a gradient")
            active_count = active_gradient_parameter_count(model)
            if first_active_count is None:
                first_active_count = active_count
            finite = global_finite and scorer_finite and alignment["ir"]["finite"] and alignment["event"]["finite"]
            if not finite:
                raise RuntimeError(f"Non-finite gradient/alignment: {variant} step {expected_step}")
            optimizer.step()
            completed += 1
            if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                raise RuntimeError(f"Non-finite parameter: {variant} step {expected_step}")
            torch.cuda.synchronize()
            optimizer_done = time.perf_counter()
            values = {key: float(value.detach().cpu()) for key, value in losses.items()}
            weights = model.last_feature_outputs["fusion_weights"].detach().float()[0]
            row = {field: "" for field in LOG_FIELDS}
            row.update({"variant": variant, "step": completed, "original_row_id": sample["original_row_id"],
                        "loss_total": float(total_loss.detach().cpu()), "loss_classifier": values.get("classification", ""),
                        "loss_box_reg": values.get("bbox_regression", ""), "loss_centerness": values.get("bbox_ctrness", ""),
                        "learning_rate": 1e-4, "global_gradient_norm": global_norm,
                        "reliability_scorer_gradient_norm": scorer_norm,
                        "active_gradient_parameter_count": active_count, "rgb_weight": float(weights[0].cpu()),
                        "ir_weight": float(weights[1].cpu()), "event_weight": float(weights[2].cpu()),
                        "weight_sum_error": fusion["weight_sum_max_abs_error"],
                        "fusion_entropy": fusion["entropy_mean"], "dominance_fraction": fusion["dominance_fraction_mean"],
                        "finite": True, "cuda_allocated_bytes": torch.cuda.memory_allocated(),
                        "cuda_reserved_bytes": torch.cuda.memory_reserved(), "data_time_sec": data_done - previous_end,
                        "forward_time_sec": forward_done - forward_start, "backward_time_sec": backward_done - forward_done,
                        "optimizer_time_sec": optimizer_done - backward_done, "step_time_sec": optimizer_done - started})
            for modality in ("ir", "event"):
                for key in ("theta_max_abs_deviation", "determinant_mean", "grid_oob_fraction"):
                    row[f"{modality}_{key}"] = alignment[modality][key]
            writer.writerow(row)
            if completed % 50 == 0:
                handle.flush()
            losses_total.append(row["loss_total"])
            step_times.append(row["step_time_sec"])
            if completed in TRACE_STEPS:
                with torch.no_grad():
                    model._feature_forward(*inputs)
                post_alignment = model.alignment_diagnostics()
                post_fusion = validate_fusion(model, variant)
                reliability_departed = reliability_departed or post_fusion["departed_from_exact_uniform"]
                alignment_trace.append({"step": completed, **post_alignment})
                fusion_trace.append({"step": completed, "reliability_scorer_gradient_norm": scorer_norm, **post_fusion})
            previous_end = optimizer_done
    finally:
        handle.close()
    if completed != STEPS_PER_VARIANT:
        raise RuntimeError(f"Incomplete V57 variant: {variant} {completed}/{STEPS_PER_VARIANT}")
    scorer_final = model.feature_scaffold.reliability_scorer.state_dict()
    scorer_unchanged = all(torch.equal(scorer_final[name].detach().cpu(), value) for name, value in scorer_initial.items())
    if variant == VARIANTS[0] and (not scorer_unchanged or scorer_ever_had_gradient):
        raise RuntimeError("Equal variant scorer was not dormant")
    if variant == VARIANTS[1] and (not scorer_ever_had_gradient or not reliability_departed):
        raise RuntimeError("Reliability scorer did not become active")
    checkpoint = checkpoint_path(variant)
    if checkpoint.exists():
        raise RuntimeError(f"Refusing to overwrite V57 checkpoint: {checkpoint}")
    order_hash = (OUT / "shared_sample_order_sha256.txt").read_text().strip()
    torch.save({"model_state": model.state_dict(), "variant": variant, "completed_optimizer_steps": completed,
                "common_init_sha256": init_hash, "sample_order_sha256": order_hash}, checkpoint)
    checkpoint_meta = {"path_local_not_committed": str(checkpoint), "sha256": sha256(checkpoint),
                       "bytes": checkpoint.stat().st_size, "variant": variant,
                       "completed_optimizer_steps": completed, "selection_metric": None}
    write_json(OUT / f"{variant}_checkpoint_metadata.json", checkpoint_meta)
    write_json(OUT / f"{variant}_alignment_trace.json", alignment_trace)
    write_json(OUT / f"{variant}_fusion_weight_trace.json", fusion_trace)
    total_parameter_count = sum(parameter.numel() for parameter in model.parameters())
    summary = {"variant": variant, "completed_optimizer_steps": completed, "all_finite": True,
               "loss_first": losses_total[0], "loss_last": losses_total[-1], "loss_min": min(losses_total),
               "loss_max": max(losses_total), "step_time_mean_sec": sum(step_times) / len(step_times),
               "step_time_min_sec": min(step_times), "step_time_max_sec": max(step_times),
               "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
               "peak_reserved_bytes": torch.cuda.max_memory_reserved(), "checkpoint": checkpoint_meta,
               "common_init_sha256": init_hash, "sample_order_sha256": order_hash,
               "total_parameter_count": total_parameter_count,
               "active_gradient_parameter_count_step1": first_active_count,
               "dormant_scorer_unchanged": scorer_unchanged,
               "scorer_ever_had_gradient": scorer_ever_had_gradient,
               "reliability_weights_departed_from_uniform": reliability_departed}
    write_json(OUT / f"{variant}_training_summary.json", summary)
    del optimizer, model
    torch.cuda.empty_cache()
    return summary, checkpoint


def evaluate_variant(variant: str, checkpoint: Path, device: torch.device) -> dict[str, object]:
    marker = OUT / f"{variant}_evaluation_started.json"
    metrics_path = OUT / f"{variant}_metrics.json"
    if marker.exists() or metrics_path.exists():
        raise RuntimeError(f"Evaluation already attempted for {variant}")
    write_json(marker, {"variant": variant, "checkpoint_sha256": sha256(checkpoint),
                        "evaluation_attempt": 1, "rows": 1845})
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model = V57FusionSupersetDetector(variant).to(device)
    model.load_state_dict(payload["model_state"], strict=True)
    model.detector.score_thresh = 0.001
    model.detector.nms_thresh = 0.6
    model.detector.detections_per_img = 100
    model.eval()
    dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    predictions, targets = [], []
    fusion_accumulator = []
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    with torch.no_grad():
        for index in range(len(dataset)):
            sample = dataset[index]
            output = model(*inputs_to_device(sample, device))[0]
            if not all(torch.isfinite(value).all() for value in output.values()):
                raise RuntimeError(f"Non-finite prediction: {variant} {sample['original_row_id']}")
            fusion = validate_fusion(model, variant)
            fusion_accumulator.append(model.last_feature_outputs["fusion_weights"].detach().cpu()[0])
            predictions.append({key: value.detach().cpu() for key, value in output.items()})
            target = sample["target_rgb"]
            targets.append({"boxes": target["boxes"].cpu(), "labels": target["labels"].cpu()})
    torch.cuda.synchronize()
    inference_seconds = time.perf_counter() - started
    metrics = coco_detection_metrics(predictions, targets, score_thresh=0.0, max_detections=100)
    if metrics["images"] != 1845 or not all(math.isfinite(metrics[key]) for key in METRIC_KEYS):
        raise RuntimeError(f"Evaluation contract failure: {variant}")
    weights = torch.stack(fusion_accumulator).float()
    entropy = -(weights.clamp_min(1e-12) * weights.clamp_min(1e-12).log()).sum(dim=1)
    maximum, modality = weights.max(dim=1)
    names = ("rgb", "ir", "event")
    evaluation_fusion = {
        "per_modality": {names[i]: {"mean": float(weights[:, i].mean()), "std": float(weights[:, i].std(unbiased=False)),
                                     "min": float(weights[:, i].min()), "max": float(weights[:, i].max())} for i in range(3)},
        "weight_sum_max_abs_error": float((weights.sum(dim=1) - 1).abs().max()),
        "entropy_mean": float(entropy.mean()), "entropy_min": float(entropy.min()), "entropy_max": float(entropy.max()),
        "dominance_fraction_mean": float(maximum.mean()),
        "dominant_modality_counts": {name: sum(names[index] == name for index in modality.tolist()) for name in names},
    }
    result = {"variant": variant, "evaluation_attempt": 1, "final_checkpoint_only": True,
              "checkpoint_sha256": sha256(checkpoint), **metrics, "inference_seconds": inference_seconds,
              "fps": len(dataset) / inference_seconds, "finite_outputs": True,
              "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
              "peak_reserved_bytes": torch.cuda.max_memory_reserved(), "fusion_diagnostics": evaluation_fusion,
              "settings": {"score_threshold": 0.001, "nms_threshold": 0.6, "max_detections": 100}}
    write_json(metrics_path, result)
    del model, predictions, targets, fusion_accumulator
    torch.cuda.empty_cache()
    return result


def run() -> None:
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    if validate_data_contract() != protocol["contract"] or verify_v56_evidence() != protocol["v56_evidence"]:
        raise RuntimeError("Prepared data or V56 evidence contract no longer matches")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; V57 has no CPU fallback")
    common, init_hash = load_common_state()
    order = json.loads((OUT / "shared_sample_indices.json").read_text(encoding="utf-8"))
    if len(order) != STEPS_PER_VARIANT or len(set(order)) != STEPS_PER_VARIANT:
        raise RuntimeError("Prepared V57 sample order invalid")
    dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=False)
    device = torch.device("cuda:0")
    summaries, checkpoints, metrics = {}, {}, {}
    total_completed = 0
    for variant in VARIANTS:
        summary, checkpoint = train_variant(variant, dataset, order, common, init_hash, device, total_completed)
        summaries[variant], checkpoints[variant] = summary, checkpoint
        total_completed += summary["completed_optimizer_steps"]
        metrics[variant] = evaluate_variant(variant, checkpoint, device)
    if total_completed != TOTAL_STEP_LIMIT:
        raise RuntimeError(f"V57 paired training incomplete: {total_completed}/{TOTAL_STEP_LIMIT}")
    write_json(OUT / "memory_summary.json", {
        variant: {"peak_allocated_bytes": summaries[variant]["peak_allocated_bytes"],
                  "peak_reserved_bytes": summaries[variant]["peak_reserved_bytes"],
                  "mean_step_time_sec": summaries[variant]["step_time_mean_sec"]} for variant in VARIANTS})
    equal, reliability = metrics[VARIANTS[0]], metrics[VARIANTS[1]]
    deltas = {key: reliability[key] - equal[key] for key in METRIC_KEYS}
    comparison = {"comparison": "reliability - equal", "metrics": metrics, "signed_deltas": deltas,
                  "ap50_95_direction": "positive" if deltas["ap50_95"] > 0 else "negative" if deltas["ap50_95"] < 0 else "zero",
                  "single_seed_preliminary_only": True, "reruns_or_tuning_after_devval": False,
                  "total_optimizer_steps": total_completed}
    write_json(OUT / "paired_comparison.json", comparison)
    (OUT / "paired_comparison.md").write_text(
        "# V57 Paired Fusion Comparison\n\nSigned deltas are reliability minus equal. This is single-seed "
        "preliminary internal evidence and did not trigger tuning, reruns, or checkpoint selection.\n", encoding="utf-8")
    decision = {"decision": "V57_PAIRED_SINGLE_SEED_FUSION_ABLATION_COMPLETE",
                "total_optimizer_steps": total_completed, "per_variant_steps": STEPS_PER_VARIANT,
                "evaluation_rows_per_variant": 1845, "evaluation_attempts_per_variant": 1,
                "alignment_enabled_both": True, "single_seed_preliminary_only": True,
                "additional_experiments_authorized": False}
    write_json(OUT / "final_decision.json", decision)
    print(json.dumps({"decision": decision, "signed_deltas": deltas,
                      "equal": {key: equal[key] for key in METRIC_KEYS},
                      "reliability": {key: reliability[key] for key in METRIC_KEYS},
                      "reliability_fusion": reliability["fusion_diagnostics"]}, indent=2))


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
        raise SystemExit(f"V57_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY: {exc}")
