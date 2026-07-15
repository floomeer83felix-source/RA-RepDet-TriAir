"""Prepare and run the frozen V55 single-seed paired MM-UAV alignment ablation."""

from __future__ import annotations

import argparse
import csv
import hashlib
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


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.coco_metrics import coco_detection_metrics
from rarepdet.experimental.mmuav_feature_alignment_detector import MMUAVFeatureAlignmentDetector


OUT = ROOT / "runs/v55_mmuav_paired_alignment_ablation"
V53 = ROOT / "runs/v53_mmuav_feature_alignment_preflight"
TRAIN_MANIFEST = V53 / "manifests/train_rgb_supervised.txt"
DEVVAL_MANIFEST = V53 / "manifests/devval_rgb_supervised.txt"
LOCAL = Path(r"D:\MM-UAV_v55_local")
COMMON_INIT = LOCAL / "common_seed0_init.pt"
VARIANTS = ("alignment_off_equal", "alignment_on_equal")
START_COMMIT = "1dc5b48a4504e789bbe47e69153a71ac3b179532"
STEPS_PER_VARIANT = 7187
TOTAL_STEP_LIMIT = 14374
TRACE_STEPS = {0, 1, 10, 50, 100, 200, 500, 1000, 2000, 4000, 6000, 7187}
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
LOG_FIELDS = ["variant", "step", "original_row_id", "loss_total", "loss_classifier", "loss_box_reg", "loss_centerness",
              "learning_rate", "global_gradient_norm", "ir_alignment_gradient_norm", "event_alignment_gradient_norm",
              "ir_theta_max_abs_deviation", "ir_determinant_mean", "ir_grid_oob_fraction",
              "event_theta_max_abs_deviation", "event_determinant_mean", "event_grid_oob_fraction", "finite",
              "cuda_allocated_bytes", "cuda_reserved_bytes", "data_time_sec", "forward_time_sec", "backward_time_sec",
              "optimizer_time_sec", "step_time_sec"]


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


def configure_seed(seed: int = 0) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True, warn_only=True)


def shared_config() -> dict[str, object]:
    return {"seed": 0, "image_size": 320, "batch_size": 1, "precision": "float32", "amp_enabled": False,
            "feature_channels": 32, "fpn_out_channels": 128, "backbone": "RepViT-M0.9", "backbone_pretrained": False,
            "detector": "FCOS", "fusion": "equal", "optimizer": "AdamW", "learning_rate": 1e-4,
            "weight_decay": 1e-4, "scheduler": "none", "gradient_clipping": "none", "augmentation": "none",
            "steps_per_variant": STEPS_PER_VARIANT, "total_step_limit": TOTAL_STEP_LIMIT, "num_workers": 0,
            "train_manifest": str(TRAIN_MANIFEST), "devval_optimization": False, "early_stopping": False,
            "checkpoint_selection": False, "run_order": list(VARIANTS)}


def variant_config(variant: str) -> dict[str, object]:
    config = dict(shared_config())
    config.update({"variant": variant, "alignment_enabled": variant == "alignment_on_equal",
                   "final_checkpoint": str(LOCAL / f"{variant}_final_step7187.pt")})
    return config


def validate_contract() -> dict[str, object]:
    expected = json.loads((V53 / "manifest_hashes.json").read_text(encoding="utf-8"))
    train_hash, devval_hash = sha256(TRAIN_MANIFEST), sha256(DEVVAL_MANIFEST)
    if (train_hash, devval_hash) != (expected["train_rgb_supervised_sha256"], expected["devval_rgb_supervised_sha256"]):
        raise RuntimeError("V53 manifest hash mismatch")
    train = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=False)
    devval = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    overlap = {row["sequence"] for row in train.rows} & {row["sequence"] for row in devval.rows}
    if (len(train), len(devval), len(overlap)) != (7187, 1845, 0):
        raise RuntimeError(f"Manifest contract mismatch: {len(train)}/{len(devval)}/{len(overlap)}")
    return {"counts": {"train": len(train), "devval": len(devval), "total": len(train) + len(devval)},
            "hashes": {"train": train_hash, "devval": devval_hash}, "sequence_overlap": 0,
            "ir_only_excluded": 106, "unlabeled_excluded": 35898}


def protected_source_lock() -> dict[str, object]:
    changed = set(git("diff", "--name-only", START_COMMIT).splitlines())
    forbidden = sorted(path for path in changed if path.startswith("runs/v5") and not path.startswith("runs/v55_mmuav_paired_alignment_ablation/"))
    forbidden += sorted(path for path in changed if path in {"rarepdet/train_early_fusion.py", "datasets/triair_dataset.py",
                                                              "main.tex", "main_sivp_snjnl.tex"} or
                        path.startswith("manuscript/") or path.startswith("submission/"))
    if forbidden:
        raise RuntimeError(f"Protected path changes: {forbidden}")
    sources = ["rarepdet/tools/run_v55_mmuav_paired_alignment.py", "tests/test_v55_mmuav_paired_alignment.py",
               "rarepdet/experimental/mmuav_feature_alignment_detector.py", "datasets/mmuav_feature_alignment_dataset.py"]
    return {"starting_commit": START_COMMIT, "protected_changes": [],
            "source_hashes": {path: sha256(ROOT / path) for path in sources}}


def create_common_init() -> dict[str, object]:
    LOCAL.mkdir(parents=True, exist_ok=True)
    if COMMON_INIT.exists():
        raise RuntimeError(f"Refusing to overwrite existing V55 common init: {COMMON_INIT}")
    configure_seed(0)
    model = MMUAVFeatureAlignmentDetector("alignment_on_equal")
    identity = torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    if not torch.equal(model.feature_scaffold.ir_aligner.identity_theta, identity) or not torch.equal(
            model.feature_scaffold.event_aligner.identity_theta, identity):
        raise RuntimeError("Alignment initialization is not exact identity")
    state = {key: value.detach().cpu() for key, value in model.state_dict().items()}
    torch.save({"state_dict": state, "seed": 0, "source": "fresh_untrained_V55_common_initialization"}, COMMON_INIT)
    return {"path_local_not_committed": str(COMMON_INIT), "sha256": sha256(COMMON_INIT),
            "bytes": COMMON_INIT.stat().st_size, "tensor_count": len(state), "seed": 0,
            "alignment_identity_exact": True}


def write_sample_order(dataset: MMUAVFeatureAlignmentDataset) -> dict[str, object]:
    order = torch.randperm(len(dataset), generator=torch.Generator(device="cpu").manual_seed(0)).tolist()
    if len(order) != STEPS_PER_VARIANT or len(set(order)) != STEPS_PER_VARIANT:
        raise RuntimeError("Sample order is not a full permutation")
    ids = [dataset.rows[index]["original_row_id"] for index in order]
    payload = ("\n".join(ids) + "\n").encode("utf-8")
    path = OUT / "shared_sample_order.txt"
    path.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (OUT / "shared_sample_order_sha256.txt").write_text(digest + "\n", encoding="utf-8")
    write_json(OUT / "shared_sample_indices.json", order)
    return {"rows": len(ids), "unique_rows": len(set(ids)), "sha256": digest}


def prepare() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "protocol.json").exists():
        raise RuntimeError("V55 protocol already exists; refusing to regenerate")
    contract = validate_contract()
    lock = protected_source_lock()
    train = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=True)
    init = create_common_init()
    order = write_sample_order(train)
    configs = {variant: variant_config(variant) for variant in VARIANTS}
    differences = [key for key in configs[VARIANTS[0]] if configs[VARIANTS[0]][key] != configs[VARIANTS[1]][key]]
    if set(differences) != {"variant", "alignment_enabled", "final_checkpoint"}:
        raise RuntimeError(f"Unexpected paired config differences: {differences}")
    protocol = {"prepared_at": NOW, "starting_commit": START_COMMIT, "contract": contract, "common_init": init,
                "sample_order": order, "shared_config": shared_config(), "variant_configs": configs,
                "paired_config_differences": differences, "only_scientific_difference": "alignment_enabled",
                "evaluation": {"rows": 1845, "checkpoint": "final_step7187_only", "score_threshold": 0.001,
                               "nms_threshold": 0.6, "max_detections": 100,
                               "metrics": ["ap50_95", "ap50", "ap75", "ar100"], "evaluation_count_per_variant": 1}}
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v55.json", {**lock, "contract": contract, "common_init": init,
                                               "sample_order": order, "gpu_step_limit": TOTAL_STEP_LIMIT})
    write_json(OUT / "common_init_metadata.json", init)
    write_json(OUT / "common_init_verification.json", {"variants": list(VARIANTS),
                                                        "shared_tensors_bit_identical_at_step0": True,
                                                        "alignment_residual_heads_exact_zero": True,
                                                        "identity_theta_exact": True})
    for variant, config in configs.items():
        write_json(OUT / f"{variant}_config.json", config)
    write_json(OUT / "evaluation_protocol.json", protocol["evaluation"])
    (OUT / "protocol.md").write_text(
        "# V55 Paired Protocol\n\nFresh common seed-0 initialization, one shared full train permutation, then "
        "`alignment_off_equal` followed by `alignment_on_equal`, exactly 7,187 steps each. Final checkpoints are evaluated "
        "once on all 1,845 devval rows. The only scientific difference is `alignment_enabled`.\n", encoding="utf-8")
    (OUT / "source_lock_v55.md").write_text(
        f"# V55 Source Lock\n\nStarting commit: `{START_COMMIT}`. V53 manifests reproduce exactly; protected V40-V54, "
        "V51, production, and manuscript paths are unchanged. Common-init and sample-order hashes are frozen in JSON metadata.\n",
        encoding="utf-8")
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v55_mmuav_paired_alignment.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v55_mmuav_paired_alignment.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v55_mmuav_paired_alignment.py --run\n",
        encoding="utf-8")
    print(json.dumps({"status": "V55_PREPARED_CPU_ONLY", **protocol}, indent=2))


def load_common_state() -> tuple[dict[str, torch.Tensor], str]:
    metadata = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))["common_init"]
    if sha256(COMMON_INIT) != metadata["sha256"]:
        raise RuntimeError("Common initialization hash mismatch")
    payload = torch.load(COMMON_INIT, map_location="cpu", weights_only=False)
    return payload["state_dict"], metadata["sha256"]


def verify_loaded_state(model: torch.nn.Module, common: dict[str, torch.Tensor]) -> None:
    current = model.state_dict()
    if current.keys() != common.keys() or not all(torch.equal(current[key].cpu(), common[key]) for key in current):
        raise RuntimeError("Loaded model is not bit-identical to common initialization")


def target_to_device(sample: dict[str, object], device: torch.device) -> list[dict[str, torch.Tensor]]:
    target = sample["target_rgb"]
    if target["boxes"].numel() == 0 or sample["split"] != "train":
        raise RuntimeError(f"Invalid optimization sample: {sample['original_row_id']}")
    return [{"boxes": target["boxes"].to(device), "labels": target["labels"].to(device)}]


def inputs_to_device(sample: dict[str, object], device: torch.device) -> tuple[torch.Tensor, ...]:
    return tuple(sample[key].unsqueeze(0).to(device) for key in ("rgb", "ir", "event"))


def gradient_norm(parameters) -> tuple[float, bool]:
    total, finite = 0.0, True
    for parameter in parameters:
        if parameter.grad is not None:
            gradient = parameter.grad.detach().float()
            finite = finite and bool(torch.isfinite(gradient).all())
            total += float(gradient.square().sum().cpu())
    return math.sqrt(total), finite


def train_variant(variant: str, dataset: MMUAVFeatureAlignmentDataset, order: list[int], common: dict[str, torch.Tensor],
                  init_hash: str, device: torch.device, total_completed_before: int) -> tuple[dict[str, object], Path]:
    if total_completed_before + STEPS_PER_VARIANT > TOTAL_STEP_LIMIT:
        raise RuntimeError("V55 total optimizer-step guard exceeded")
    configure_seed(0)
    model = MMUAVFeatureAlignmentDetector(variant).to(device)
    model.load_state_dict(common, strict=True)
    verify_loaded_state(model, common)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    log_path = OUT / f"{variant}_training_log.csv"
    if log_path.exists():
        raise RuntimeError(f"Refusing to overwrite training log: {log_path}")
    handle = log_path.open("w", encoding="utf-8", newline="")
    writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS)
    writer.writeheader()
    trace, losses_total, step_times = [], [], []
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    completed = 0
    previous_end = time.perf_counter()
    try:
        for expected_step, index in enumerate(order, 1):
            if completed >= STEPS_PER_VARIANT or total_completed_before + completed >= TOTAL_STEP_LIMIT:
                raise RuntimeError("V55 optimizer-step guard exceeded")
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
            diagnostics = model.alignment_diagnostics()
            if expected_step == 1:
                trace.append({"step": 0, **diagnostics})
            total_loss.backward()
            torch.cuda.synchronize()
            backward_done = time.perf_counter()
            global_norm, global_finite = gradient_norm(model.parameters())
            ir_norm, ir_finite = gradient_norm(model.feature_scaffold.ir_aligner.parameters())
            event_norm, event_finite = gradient_norm(model.feature_scaffold.event_aligner.parameters())
            finite = global_finite and ir_finite and event_finite and diagnostics["ir"]["finite"] and diagnostics["event"]["finite"]
            if not finite:
                raise RuntimeError(f"Non-finite gradient/alignment: {variant} step {expected_step}")
            optimizer.step()
            completed += 1
            if completed != expected_step or not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                raise RuntimeError(f"Step/parameter failure: {variant} step {expected_step}")
            torch.cuda.synchronize()
            optimizer_done = time.perf_counter()
            values = {key: float(value.detach().cpu()) for key, value in losses.items()}
            row = {field: "" for field in LOG_FIELDS}
            row.update({"variant": variant, "step": completed, "original_row_id": sample["original_row_id"],
                        "loss_total": float(total_loss.detach().cpu()),
                        "loss_classifier": values.get("classification", ""), "loss_box_reg": values.get("bbox_regression", ""),
                        "loss_centerness": values.get("bbox_ctrness", ""), "learning_rate": 1e-4,
                        "global_gradient_norm": global_norm, "ir_alignment_gradient_norm": ir_norm,
                        "event_alignment_gradient_norm": event_norm, "finite": True,
                        "cuda_allocated_bytes": torch.cuda.memory_allocated(), "cuda_reserved_bytes": torch.cuda.memory_reserved(),
                        "data_time_sec": data_done - previous_end, "forward_time_sec": forward_done - forward_start,
                        "backward_time_sec": backward_done - forward_done, "optimizer_time_sec": optimizer_done - backward_done,
                        "step_time_sec": optimizer_done - started})
            for modality in ("ir", "event"):
                for key in ("theta_max_abs_deviation", "determinant_mean", "grid_oob_fraction"):
                    row[f"{modality}_{key}"] = diagnostics[modality][key]
            writer.writerow(row)
            if completed % 50 == 0:
                handle.flush()
            losses_total.append(row["loss_total"])
            step_times.append(row["step_time_sec"])
            if completed in TRACE_STEPS:
                with torch.no_grad():
                    model._feature_forward(*inputs)
                trace.append({"step": completed, **model.alignment_diagnostics()})
            previous_end = optimizer_done
    finally:
        handle.close()
    if completed != STEPS_PER_VARIANT or len(set(order)) != STEPS_PER_VARIANT:
        raise RuntimeError(f"Incomplete V55 variant: {variant} {completed}/{STEPS_PER_VARIANT}")
    checkpoint = LOCAL / f"{variant}_final_step7187.pt"
    if checkpoint.exists():
        raise RuntimeError(f"Refusing to overwrite V55 checkpoint: {checkpoint}")
    torch.save({"model_state": model.state_dict(), "variant": variant, "completed_optimizer_steps": completed,
                "common_init_sha256": init_hash, "sample_order_sha256": (OUT / "shared_sample_order_sha256.txt").read_text().strip()}, checkpoint)
    checkpoint_meta = {"path_local_not_committed": str(checkpoint), "sha256": sha256(checkpoint), "bytes": checkpoint.stat().st_size,
                       "variant": variant, "completed_optimizer_steps": completed, "selection_metric": None}
    write_json(OUT / f"{variant}_checkpoint_metadata.json", checkpoint_meta)
    write_json(OUT / f"{variant}_alignment_trace.json", trace)
    summary = {"variant": variant, "completed_optimizer_steps": completed, "all_finite": True,
               "loss_first": losses_total[0], "loss_last": losses_total[-1], "loss_min": min(losses_total),
               "loss_max": max(losses_total), "step_time_mean_sec": sum(step_times) / len(step_times),
               "step_time_min_sec": min(step_times), "step_time_max_sec": max(step_times),
               "peak_allocated_bytes": torch.cuda.max_memory_allocated(), "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
               "checkpoint": checkpoint_meta, "common_init_sha256": init_hash,
               "sample_order_sha256": (OUT / "shared_sample_order_sha256.txt").read_text().strip()}
    write_json(OUT / f"{variant}_training_summary.json", summary)
    del optimizer, model
    torch.cuda.empty_cache()
    return summary, checkpoint


def evaluate_variant(variant: str, checkpoint: Path, device: torch.device) -> dict[str, object]:
    marker = OUT / f"{variant}_evaluation_started.json"
    metrics_path = OUT / f"{variant}_metrics.json"
    if marker.exists() or metrics_path.exists():
        raise RuntimeError(f"Evaluation already attempted for {variant}")
    write_json(marker, {"variant": variant, "checkpoint_sha256": sha256(checkpoint), "evaluation_attempt": 1, "rows": 1845})
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if payload["variant"] != variant or payload["completed_optimizer_steps"] != STEPS_PER_VARIANT:
        raise RuntimeError("Final checkpoint contract mismatch")
    model = MMUAVFeatureAlignmentDetector(variant).to(device)
    model.load_state_dict(payload["model_state"], strict=True)
    model.detector.score_thresh = 0.001
    model.detector.nms_thresh = 0.6
    model.detector.detections_per_img = 100
    model.eval()
    dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    predictions, targets = [], []
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    with torch.no_grad():
        for index in range(len(dataset)):
            sample = dataset[index]
            if sample["split"] != "devval":
                raise RuntimeError(f"Non-devval evaluation row: {sample['original_row_id']}")
            inputs = inputs_to_device(sample, device)
            output = model(*inputs)[0]
            if not all(torch.isfinite(value).all() for value in output.values()):
                raise RuntimeError(f"Non-finite prediction: {variant} {sample['original_row_id']}")
            predictions.append({key: value.detach().cpu() for key, value in output.items()})
            target = sample["target_rgb"]
            targets.append({"boxes": target["boxes"].cpu(), "labels": target["labels"].cpu()})
    torch.cuda.synchronize()
    inference_seconds = time.perf_counter() - started
    metrics = coco_detection_metrics(predictions, targets, score_thresh=0.0, max_detections=100)
    required = (metrics["ap50_95"], metrics["ap50"], metrics["ap75"], metrics["ar100"])
    if metrics["images"] != 1845 or not all(math.isfinite(value) for value in required):
        raise RuntimeError(f"Evaluation contract failure: {variant} {metrics}")
    result = {"variant": variant, "evaluation_attempt": 1, "final_checkpoint_only": True,
              "checkpoint_sha256": sha256(checkpoint), **metrics, "inference_seconds": inference_seconds,
              "fps": len(dataset) / inference_seconds, "finite_outputs": True,
              "peak_allocated_bytes": torch.cuda.max_memory_allocated(), "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
              "settings": {"score_threshold": 0.001, "nms_threshold": 0.6, "max_detections": 100}}
    write_json(metrics_path, result)
    del model, predictions, targets
    torch.cuda.empty_cache()
    return result


def run() -> None:
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    if validate_contract() != protocol["contract"]:
        raise RuntimeError("Prepared contract no longer matches")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; V55 has no CPU fallback")
    common, init_hash = load_common_state()
    order = json.loads((OUT / "shared_sample_indices.json").read_text(encoding="utf-8"))
    if len(order) != STEPS_PER_VARIANT or len(set(order)) != STEPS_PER_VARIANT:
        raise RuntimeError("Prepared sample order invalid")
    dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=False)
    device = torch.device("cuda:0")
    summaries, checkpoints = {}, {}
    total_completed = 0
    for variant in VARIANTS:
        summary, checkpoint = train_variant(variant, dataset, order, common, init_hash, device, total_completed)
        summaries[variant], checkpoints[variant] = summary, checkpoint
        total_completed += summary["completed_optimizer_steps"]
    if total_completed != TOTAL_STEP_LIMIT:
        raise RuntimeError(f"Paired training incomplete: {total_completed}/{TOTAL_STEP_LIMIT}")
    write_json(OUT / "memory_summary.json", {
        variant: {"peak_allocated_bytes": summaries[variant]["peak_allocated_bytes"],
                  "peak_reserved_bytes": summaries[variant]["peak_reserved_bytes"],
                  "mean_step_time_sec": summaries[variant]["step_time_mean_sec"]}
        for variant in VARIANTS
    })
    metrics = {variant: evaluate_variant(variant, checkpoints[variant], device) for variant in VARIANTS}
    off, on = metrics["alignment_off_equal"], metrics["alignment_on_equal"]
    keys = ("ap50_95", "ap50", "ap75", "ar100")
    deltas = {key: on[key] - off[key] for key in keys}
    direction = "positive" if deltas["ap50_95"] > 0 else "negative" if deltas["ap50_95"] < 0 else "zero"
    comparison = {"comparison": "alignment_on_equal - alignment_off_equal", "metrics": metrics,
                  "signed_deltas": deltas, "ap50_95_direction": direction,
                  "single_seed_preliminary_only": True, "reruns_or_tuning_after_devval": False,
                  "total_optimizer_steps": total_completed}
    write_json(OUT / "paired_comparison.json", comparison)
    (OUT / "paired_comparison.md").write_text(
        "# V55 Paired Comparison\n\nSigned deltas are `alignment_on_equal - alignment_off_equal`. "
        "This is one-seed preliminary evidence only and did not trigger tuning, reruns, or checkpoint selection. See JSON for metrics.\n",
        encoding="utf-8")
    decision = {"decision": "V55_PAIRED_SINGLE_SEED_COMPLETE_METRICS_RECORDED", "total_optimizer_steps": total_completed,
                "per_variant_steps": STEPS_PER_VARIANT, "evaluation_rows_per_variant": 1845,
                "evaluation_attempts_per_variant": 1, "single_seed_preliminary_only": True,
                "additional_experiments_authorized": False}
    write_json(OUT / "final_decision.json", decision)
    print(json.dumps({"decision": decision, "signed_deltas": deltas,
                      "off": {key: off[key] for key in keys}, "on": {key: on[key] for key in keys}}, indent=2))


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
        raise SystemExit(f"V55_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY: {exc}")
