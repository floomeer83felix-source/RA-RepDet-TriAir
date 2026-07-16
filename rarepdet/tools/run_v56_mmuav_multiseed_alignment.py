"""Run the frozen V56 two-pair MM-UAV alignment confirmation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
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


OUT = ROOT / "runs/v56_mmuav_multiseed_alignment_confirmation"
V53 = ROOT / "runs/v53_mmuav_feature_alignment_preflight"
V55 = ROOT / "runs/v55_mmuav_paired_alignment_ablation"
TRAIN_MANIFEST = V53 / "manifests/train_rgb_supervised.txt"
DEVVAL_MANIFEST = V53 / "manifests/devval_rgb_supervised.txt"
LOCAL = Path(r"D:\MM-UAV_v56_local")
SEEDS = (1, 2)
VARIANTS = ("alignment_off_equal", "alignment_on_equal")
RUN_ORDER = tuple((seed, variant) for seed in SEEDS for variant in VARIANTS)
START_COMMIT = "05a72b0df1377bb6dce2134da1d73297b29fefe9"
STEPS_PER_RUN = 7187
TOTAL_STEP_LIMIT = 28748
TRACE_STEPS = {0, 1, 10, 50, 100, 200, 500, 1000, 2000, 4000, 6000, 7187}
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
METRIC_KEYS = ("ap50_95", "ap50", "ap75", "ar100")
LOG_FIELDS = [
    "seed", "variant", "step", "original_row_id", "loss_total", "loss_classifier", "loss_box_reg",
    "loss_centerness", "learning_rate", "global_gradient_norm", "ir_alignment_gradient_norm",
    "event_alignment_gradient_norm", "ir_theta_max_abs_deviation", "ir_determinant_mean",
    "ir_grid_oob_fraction", "event_theta_max_abs_deviation", "event_determinant_mean",
    "event_grid_oob_fraction", "finite", "cuda_allocated_bytes", "cuda_reserved_bytes", "data_time_sec",
    "forward_time_sec", "backward_time_sec", "optimizer_time_sec", "step_time_sec",
]
V55_EXPECTED = {
    "common_init_sha256": "91fec577380f895c932ffeb090bba7d376abc1ea1d97d568ae46901a7bbcb983",
    "sample_order_sha256": "27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b",
    "alignment_off_equal": {
        "ap50_95": 0.013269265954709897, "ap50": 0.06442060913543426,
        "ap75": 0.0015648886842774918, "ar100": 0.05011910433539781,
    },
    "alignment_on_equal": {
        "ap50_95": 0.04826946094263493, "ap50": 0.19278295159638525,
        "ap75": 0.007177918411246644, "ar100": 0.09890424011434017,
    },
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


def configure_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True, warn_only=True)


def run_name(seed: int, variant: str) -> str:
    return f"seed{seed}_{variant}"


def common_init_path(seed: int) -> Path:
    return LOCAL / f"seed{seed}_common_init.pt"


def checkpoint_path(seed: int, variant: str) -> Path:
    return LOCAL / f"{run_name(seed, variant)}_final_step7187.pt"


def shared_config(seed: int) -> dict[str, object]:
    return {
        "seed": seed, "image_size": 320, "batch_size": 1, "precision": "float32", "amp_enabled": False,
        "feature_channels": 32, "fpn_out_channels": 128, "backbone": "RepViT-M0.9",
        "backbone_pretrained": False, "detector": "FCOS", "fusion": "equal", "optimizer": "AdamW",
        "learning_rate": 1e-4, "weight_decay": 1e-4, "scheduler": "none", "gradient_clipping": "none",
        "augmentation": "none", "steps_per_run": STEPS_PER_RUN, "v56_total_step_limit": TOTAL_STEP_LIMIT,
        "num_workers": 0, "train_manifest": str(TRAIN_MANIFEST), "devval_optimization": False,
        "early_stopping": False, "checkpoint_selection": False,
        "pair_run_order": list(VARIANTS), "global_run_order": [run_name(s, v) for s, v in RUN_ORDER],
    }


def variant_config(seed: int, variant: str) -> dict[str, object]:
    config = dict(shared_config(seed))
    config.update({"variant": variant, "alignment_enabled": variant == "alignment_on_equal",
                   "final_checkpoint": str(checkpoint_path(seed, variant))})
    return config


def validate_data_contract() -> dict[str, object]:
    train_hash, devval_hash = sha256(TRAIN_MANIFEST), sha256(DEVVAL_MANIFEST)
    expected_train = "e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a"
    expected_devval = "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54"
    if (train_hash, devval_hash) != (expected_train, expected_devval):
        raise RuntimeError("V56 manifest hash mismatch")
    train = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=False)
    devval = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    overlap = {row["sequence"] for row in train.rows} & {row["sequence"] for row in devval.rows}
    if (len(train), len(devval), len(overlap)) != (7187, 1845, 0):
        raise RuntimeError(f"Manifest contract mismatch: {len(train)}/{len(devval)}/{len(overlap)}")
    return {"counts": {"train": 7187, "devval": 1845, "total": 9032},
            "hashes": {"train": train_hash, "devval": devval_hash}, "sequence_overlap": 0,
            "ir_only_excluded": 106, "unlabeled_excluded": 35898}


def verify_v55_evidence() -> dict[str, object]:
    protocol = json.loads((V55 / "protocol.json").read_text(encoding="utf-8"))
    comparison = json.loads((V55 / "paired_comparison.json").read_text(encoding="utf-8"))
    if protocol["common_init"]["sha256"] != V55_EXPECTED["common_init_sha256"]:
        raise RuntimeError("V55 common-init evidence mismatch")
    if protocol["sample_order"]["sha256"] != V55_EXPECTED["sample_order_sha256"]:
        raise RuntimeError("V55 sample-order evidence mismatch")
    for variant in VARIANTS:
        observed = comparison["metrics"][variant]
        if any(observed[key] != V55_EXPECTED[variant][key] for key in METRIC_KEYS):
            raise RuntimeError(f"V55 metric evidence mismatch: {variant}")
    return {
        "executed_seed0": False,
        "common_init_sha256": protocol["common_init"]["sha256"],
        "sample_order_sha256": protocol["sample_order"]["sha256"],
        "metrics": {variant: {key: comparison["metrics"][variant][key] for key in METRIC_KEYS}
                    for variant in VARIANTS},
        "source_file_sha256": {name: sha256(V55 / name) for name in ("protocol.json", "paired_comparison.json",
                                                                       "final_decision.json")},
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
                       path.startswith("runs/v56_mmuav_multiseed_alignment_confirmation/")))
    if forbidden:
        raise RuntimeError(f"Protected path changes: {forbidden}")
    sources = [
        "rarepdet/tools/run_v56_mmuav_multiseed_alignment.py",
        "tests/test_v56_mmuav_multiseed_alignment.py",
        "rarepdet/tools/run_v55_mmuav_paired_alignment.py",
        "rarepdet/experimental/mmuav_feature_alignment_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
    ]
    return {"starting_commit": START_COMMIT, "protected_changes": [],
            "source_hashes": {path: sha256(ROOT / path) for path in sources}}


def create_seed_material(seed: int, dataset: MMUAVFeatureAlignmentDataset) -> tuple[dict[str, object], dict[str, object]]:
    init_path = common_init_path(seed)
    if init_path.exists():
        raise RuntimeError(f"Refusing to overwrite common init: {init_path}")
    configure_seed(seed)
    model = MMUAVFeatureAlignmentDetector("alignment_on_equal")
    identity = torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    if not torch.equal(model.feature_scaffold.ir_aligner.identity_theta, identity) or not torch.equal(
            model.feature_scaffold.event_aligner.identity_theta, identity):
        raise RuntimeError("Alignment initialization is not exact identity")
    state = {key: value.detach().cpu() for key, value in model.state_dict().items()}
    torch.save({"state_dict": state, "seed": seed, "source": "fresh_untrained_V56_common_initialization"}, init_path)
    init = {"path_local_not_committed": str(init_path), "sha256": sha256(init_path), "bytes": init_path.stat().st_size,
            "tensor_count": len(state), "seed": seed, "alignment_identity_exact": True}
    order = torch.randperm(len(dataset), generator=torch.Generator(device="cpu").manual_seed(seed)).tolist()
    ids = [dataset.rows[index]["original_row_id"] for index in order]
    if len(order) != STEPS_PER_RUN or len(set(order)) != STEPS_PER_RUN or len(set(ids)) != STEPS_PER_RUN:
        raise RuntimeError(f"Seed {seed} sample order is not a full unique permutation")
    prefix = OUT / f"seed{seed}_shared_sample_order"
    payload = ("\n".join(ids) + "\n").encode("utf-8")
    prefix.with_suffix(".txt").write_bytes(payload)
    write_json(OUT / f"seed{seed}_shared_sample_indices.json", order)
    order_meta = {"seed": seed, "rows": len(ids), "unique_rows": len(set(ids)),
                  "sha256": hashlib.sha256(payload).hexdigest()}
    (OUT / f"seed{seed}_shared_sample_order_sha256.txt").write_text(order_meta["sha256"] + "\n", encoding="utf-8")
    return init, order_meta


def prepare() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    if (OUT / "protocol.json").exists():
        raise RuntimeError("V56 protocol already exists; refusing to regenerate")
    contract = validate_data_contract()
    v55 = verify_v55_evidence()
    lock = protected_source_lock()
    dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=True)
    seed_material = {}
    configs = {}
    for seed in SEEDS:
        init, order = create_seed_material(seed, dataset)
        seed_material[str(seed)] = {"common_init": init, "sample_order": order}
        pair = {variant: variant_config(seed, variant) for variant in VARIANTS}
        differences = [key for key in pair[VARIANTS[0]] if pair[VARIANTS[0]][key] != pair[VARIANTS[1]][key]]
        if set(differences) != {"variant", "alignment_enabled", "final_checkpoint"}:
            raise RuntimeError(f"Seed {seed} unexpected pair differences: {differences}")
        configs[str(seed)] = pair
        write_json(OUT / f"seed{seed}_common_init_metadata.json", init)
        write_json(OUT / f"seed{seed}_common_init_verification.json", {
            "seed": seed, "shared_tensors_bit_identical_at_step0": True,
            "alignment_residual_heads_exact_zero": True, "identity_theta_exact": True,
        })
        for variant, config in pair.items():
            write_json(OUT / f"{run_name(seed, variant)}_config.json", config)
    evaluation = {"rows": 1845, "checkpoint": "final_step7187_only", "score_threshold": 0.001,
                  "nms_threshold": 0.6, "max_detections": 100, "metrics": list(METRIC_KEYS),
                  "evaluation_count_per_run": 1}
    protocol = {"prepared_at": NOW, "starting_commit": START_COMMIT, "contract": contract,
                "v55_seed0_evidence": v55, "seeds": list(SEEDS), "variants": list(VARIANTS),
                "run_order": [run_name(seed, variant) for seed, variant in RUN_ORDER],
                "steps_per_run": STEPS_PER_RUN, "v56_total_step_limit": TOTAL_STEP_LIMIT,
                "seed_material": seed_material, "variant_configs": configs,
                "only_scientific_difference_within_pair": "alignment_enabled", "evaluation": evaluation}
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v56.json", {**lock, "contract": contract, "v55_seed0_evidence": v55,
                                               "seed_material": seed_material, "gpu_step_limit": TOTAL_STEP_LIMIT})
    write_json(OUT / "v55_seed0_evidence_verification.json", v55)
    write_json(OUT / "evaluation_protocol.json", evaluation)
    (OUT / "protocol.md").write_text(
        "# V56 Protocol\n\nFrozen seed 0 is imported without execution. Seeds 1 and 2 each run alignment off then on "
        "from one seed-specific common initialization and one shared permutation, exactly 7,187 steps per run.\n",
        encoding="utf-8")
    (OUT / "source_lock_v56.md").write_text(
        f"# V56 Source Lock\n\nStarting commit: `{START_COMMIT}`. Data and V55 evidence reproduce exactly; "
        "protected production, history, V51, and manuscript paths are unchanged.\n", encoding="utf-8")
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v56_mmuav_multiseed_alignment.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v56_mmuav_multiseed_alignment.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v56_mmuav_multiseed_alignment.py --run\n",
        encoding="utf-8")
    print(json.dumps({"status": "V56_PREPARED_CPU_ONLY", **protocol}, indent=2))


def load_common_state(seed: int) -> tuple[dict[str, torch.Tensor], str]:
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    metadata = protocol["seed_material"][str(seed)]["common_init"]
    path = common_init_path(seed)
    if sha256(path) != metadata["sha256"]:
        raise RuntimeError(f"Seed {seed} common initialization hash mismatch")
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if payload["seed"] != seed:
        raise RuntimeError(f"Seed {seed} common initialization metadata mismatch")
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


def train_run(seed: int, variant: str, dataset: MMUAVFeatureAlignmentDataset, order: list[int],
              common: dict[str, torch.Tensor], init_hash: str, device: torch.device,
              total_completed_before: int) -> tuple[dict[str, object], Path]:
    name = run_name(seed, variant)
    if total_completed_before + STEPS_PER_RUN > TOTAL_STEP_LIMIT:
        raise RuntimeError("V56 total optimizer-step guard exceeded")
    configure_seed(seed)
    model = MMUAVFeatureAlignmentDetector(variant).to(device)
    model.load_state_dict(common, strict=True)
    verify_loaded_state(model, common)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    log_path = OUT / f"{name}_training_log.csv"
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
            if completed >= STEPS_PER_RUN or total_completed_before + completed >= TOTAL_STEP_LIMIT:
                raise RuntimeError("V56 optimizer-step guard exceeded")
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
                raise RuntimeError(f"Non-finite loss: {name} step {expected_step}")
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
                raise RuntimeError(f"Non-finite gradient/alignment: {name} step {expected_step}")
            optimizer.step()
            completed += 1
            if completed != expected_step or not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                raise RuntimeError(f"Step/parameter failure: {name} step {expected_step}")
            torch.cuda.synchronize()
            optimizer_done = time.perf_counter()
            values = {key: float(value.detach().cpu()) for key, value in losses.items()}
            row = {field: "" for field in LOG_FIELDS}
            row.update({"seed": seed, "variant": variant, "step": completed, "original_row_id": sample["original_row_id"],
                        "loss_total": float(total_loss.detach().cpu()), "loss_classifier": values.get("classification", ""),
                        "loss_box_reg": values.get("bbox_regression", ""), "loss_centerness": values.get("bbox_ctrness", ""),
                        "learning_rate": 1e-4, "global_gradient_norm": global_norm,
                        "ir_alignment_gradient_norm": ir_norm, "event_alignment_gradient_norm": event_norm,
                        "finite": True, "cuda_allocated_bytes": torch.cuda.memory_allocated(),
                        "cuda_reserved_bytes": torch.cuda.memory_reserved(), "data_time_sec": data_done - previous_end,
                        "forward_time_sec": forward_done - forward_start, "backward_time_sec": backward_done - forward_done,
                        "optimizer_time_sec": optimizer_done - backward_done, "step_time_sec": optimizer_done - started})
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
    if completed != STEPS_PER_RUN:
        raise RuntimeError(f"Incomplete V56 run: {name} {completed}/{STEPS_PER_RUN}")
    checkpoint = checkpoint_path(seed, variant)
    if checkpoint.exists():
        raise RuntimeError(f"Refusing to overwrite V56 checkpoint: {checkpoint}")
    order_hash = (OUT / f"seed{seed}_shared_sample_order_sha256.txt").read_text().strip()
    torch.save({"model_state": model.state_dict(), "seed": seed, "variant": variant,
                "completed_optimizer_steps": completed, "common_init_sha256": init_hash,
                "sample_order_sha256": order_hash}, checkpoint)
    checkpoint_meta = {"path_local_not_committed": str(checkpoint), "sha256": sha256(checkpoint),
                       "bytes": checkpoint.stat().st_size, "seed": seed, "variant": variant,
                       "completed_optimizer_steps": completed, "selection_metric": None}
    write_json(OUT / f"{name}_checkpoint_metadata.json", checkpoint_meta)
    write_json(OUT / f"{name}_alignment_trace.json", trace)
    summary = {"seed": seed, "variant": variant, "completed_optimizer_steps": completed, "all_finite": True,
               "loss_first": losses_total[0], "loss_last": losses_total[-1], "loss_min": min(losses_total),
               "loss_max": max(losses_total), "step_time_mean_sec": sum(step_times) / len(step_times),
               "step_time_min_sec": min(step_times), "step_time_max_sec": max(step_times),
               "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
               "peak_reserved_bytes": torch.cuda.max_memory_reserved(), "checkpoint": checkpoint_meta,
               "common_init_sha256": init_hash, "sample_order_sha256": order_hash}
    write_json(OUT / f"{name}_training_summary.json", summary)
    del optimizer, model
    torch.cuda.empty_cache()
    return summary, checkpoint


def evaluate_run(seed: int, variant: str, checkpoint: Path, device: torch.device) -> dict[str, object]:
    name = run_name(seed, variant)
    marker = OUT / f"{name}_evaluation_started.json"
    metrics_path = OUT / f"{name}_metrics.json"
    if marker.exists() or metrics_path.exists():
        raise RuntimeError(f"Evaluation already attempted for {name}")
    write_json(marker, {"seed": seed, "variant": variant, "checkpoint_sha256": sha256(checkpoint),
                        "evaluation_attempt": 1, "rows": 1845})
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if payload["seed"] != seed or payload["variant"] != variant or payload["completed_optimizer_steps"] != STEPS_PER_RUN:
        raise RuntimeError(f"Final checkpoint contract mismatch: {name}")
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
            output = model(*inputs_to_device(sample, device))[0]
            if not all(torch.isfinite(value).all() for value in output.values()):
                raise RuntimeError(f"Non-finite prediction: {name} {sample['original_row_id']}")
            predictions.append({key: value.detach().cpu() for key, value in output.items()})
            target = sample["target_rgb"]
            targets.append({"boxes": target["boxes"].cpu(), "labels": target["labels"].cpu()})
    torch.cuda.synchronize()
    inference_seconds = time.perf_counter() - started
    metrics = coco_detection_metrics(predictions, targets, score_thresh=0.0, max_detections=100)
    if metrics["images"] != 1845 or not all(math.isfinite(metrics[key]) for key in METRIC_KEYS):
        raise RuntimeError(f"Evaluation contract failure: {name}")
    result = {"seed": seed, "variant": variant, "evaluation_attempt": 1, "final_checkpoint_only": True,
              "checkpoint_sha256": sha256(checkpoint), **metrics, "inference_seconds": inference_seconds,
              "fps": len(dataset) / inference_seconds, "finite_outputs": True,
              "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
              "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
              "settings": {"score_threshold": 0.001, "nms_threshold": 0.6, "max_detections": 100}}
    write_json(metrics_path, result)
    del model, predictions, targets
    torch.cuda.empty_cache()
    return result


def aggregate(metrics_by_seed: dict[int, dict[str, dict[str, float]]]) -> dict[str, object]:
    summaries = {}
    for key in METRIC_KEYS:
        off = [metrics_by_seed[seed][VARIANTS[0]][key] for seed in (0, 1, 2)]
        on = [metrics_by_seed[seed][VARIANTS[1]][key] for seed in (0, 1, 2)]
        deltas = [right - left for left, right in zip(off, on)]
        summaries[key] = {
            "off_mean": statistics.mean(off), "off_sample_std": statistics.stdev(off),
            "on_mean": statistics.mean(on), "on_sample_std": statistics.stdev(on),
            "paired_delta_mean": statistics.mean(deltas), "paired_delta_median": statistics.median(deltas),
            "paired_delta_min": min(deltas), "paired_delta_max": max(deltas),
            "positive_seed_count": sum(value > 0 for value in deltas),
        }
    ap_deltas = [metrics_by_seed[seed][VARIANTS[1]]["ap50_95"] -
                 metrics_by_seed[seed][VARIANTS[0]]["ap50_95"] for seed in (0, 1, 2)]
    return {"seeds": [0, 1, 2], "per_seed": {str(seed): metrics_by_seed[seed] for seed in (0, 1, 2)},
            "summaries": summaries, "ap50_95_direction_consistency": {
                "directions": ["positive" if value > 0 else "negative" if value < 0 else "zero" for value in ap_deltas],
                "all_positive": all(value > 0 for value in ap_deltas),
                "positive_seed_count": sum(value > 0 for value in ap_deltas),
            }, "descriptive_only_no_significance_claim": True}


def run() -> None:
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    if validate_data_contract() != protocol["contract"] or verify_v55_evidence() != protocol["v55_seed0_evidence"]:
        raise RuntimeError("Prepared data or V55 evidence contract no longer matches")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; V56 has no CPU fallback")
    dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=False)
    device = torch.device("cuda:0")
    summaries, checkpoints, metrics = {}, {}, {}
    total_completed = 0
    for seed in SEEDS:
        common, init_hash = load_common_state(seed)
        order = json.loads((OUT / f"seed{seed}_shared_sample_indices.json").read_text(encoding="utf-8"))
        if len(order) != STEPS_PER_RUN or len(set(order)) != STEPS_PER_RUN:
            raise RuntimeError(f"Prepared seed {seed} order invalid")
        metrics[seed] = {}
        for variant in VARIANTS:
            name = run_name(seed, variant)
            summary, checkpoint = train_run(seed, variant, dataset, order, common, init_hash, device, total_completed)
            summaries[name], checkpoints[name] = summary, checkpoint
            total_completed += summary["completed_optimizer_steps"]
            metrics[seed][variant] = evaluate_run(seed, variant, checkpoint, device)
    if total_completed != TOTAL_STEP_LIMIT:
        raise RuntimeError(f"V56 paired training incomplete: {total_completed}/{TOTAL_STEP_LIMIT}")
    write_json(OUT / "memory_summary.json", {
        name: {"peak_allocated_bytes": value["peak_allocated_bytes"],
               "peak_reserved_bytes": value["peak_reserved_bytes"],
               "mean_step_time_sec": value["step_time_mean_sec"]} for name, value in summaries.items()})
    seed0 = protocol["v55_seed0_evidence"]["metrics"]
    all_metrics = {0: seed0, 1: metrics[1], 2: metrics[2]}
    aggregation = aggregate(all_metrics)
    write_json(OUT / "three_seed_aggregation.json", aggregation)
    (OUT / "three_seed_aggregation.md").write_text(
        "# V56 Three-Seed Aggregation\n\nSeeds 0, 1, and 2 are summarized descriptively. No p-value or "
        "statistical-significance claim is made. See JSON for exact metrics and paired deltas.\n", encoding="utf-8")
    decision = {"decision": "V56_THREE_SEED_PAIRED_ALIGNMENT_CONFIRMATION_COMPLETE",
                "v56_total_optimizer_steps": total_completed, "per_run_steps": STEPS_PER_RUN,
                "new_seeds": list(SEEDS), "seed0_executed": False, "new_run_count": 4,
                "evaluation_rows_per_run": 1845, "evaluation_attempts_per_run": 1,
                "descriptive_three_seed_evidence_only": True, "additional_experiments_authorized": False}
    write_json(OUT / "final_decision.json", decision)
    print(json.dumps({"decision": decision, "aggregation": aggregation}, indent=2))


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
        raise SystemExit(f"V56_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY: {exc}")
