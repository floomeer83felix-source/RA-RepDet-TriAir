"""Run the frozen, fail-closed V54 MM-UAV 200-step GPU verification pilot."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
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
from rarepdet.experimental.mmuav_feature_alignment_detector import MMUAVFeatureAlignmentDetector, VARIANTS


OUT = ROOT / "runs/v54_mmuav_gpu_pilot"
V53 = ROOT / "runs/v53_mmuav_feature_alignment_preflight"
TRAIN_MANIFEST = V53 / "manifests/train_rgb_supervised.txt"
DEVVAL_MANIFEST = V53 / "manifests/devval_rgb_supervised.txt"
LOCAL_CHECKPOINT = Path(r"D:\MM-UAV_v54_local\alignment_on_equal_step200.pt")
START_COMMIT = "e00f4f829445216fd778f0dc842623793a93b93f"
MAX_STEPS = 200
KEY_STEPS = {0, 1, 10, 50, 100, 150, 200}
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
TRAIN_FIELDS = [
    "step", "original_row_id", "loss_total", "loss_classifier", "loss_box_reg", "loss_centerness", "learning_rate",
    "global_gradient_norm", "ir_alignment_gradient_norm", "event_alignment_gradient_norm",
    "ir_theta_mean", "ir_theta_std", "ir_theta_min", "ir_theta_max", "ir_theta_max_abs_deviation",
    "ir_determinant_mean", "ir_grid_oob_fraction", "event_theta_mean", "event_theta_std", "event_theta_min",
    "event_theta_max", "event_theta_max_abs_deviation", "event_determinant_mean", "event_grid_oob_fraction",
    "finite", "cuda_allocated_bytes", "cuda_reserved_bytes", "data_time_sec", "forward_time_sec",
    "backward_time_sec", "optimizer_time_sec", "step_time_sec",
]


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
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True, warn_only=True)


def frozen_config() -> dict[str, object]:
    return {
        "frozen_at": NOW, "starting_commit": START_COMMIT, "primary_variant": "alignment_on_equal",
        "maximum_completed_optimizer_steps": MAX_STEPS, "seed": 0, "branch_input_size": [320, 320],
        "batch_size": 1, "train_manifest": str(TRAIN_MANIFEST), "devval_optimization": False,
        "feature_channels": 32, "fpn_out_channels": 128, "detector": "RepViT-M0.9-FPN-FCOS",
        "integration_stage": "aligned/equal-fused features -> 1x1 to 3 channels -> bilinear 320 -> existing RepViT-FPN-FCOS",
        "optimizer": "AdamW", "learning_rate": 1e-4, "weight_decay": 1e-4, "scheduler": "none",
        "precision": "float32", "amp_enabled": False, "gradient_clipping": "none", "augmentation": "none",
        "backbone_pretrained": False, "num_workers": 0, "checkpoint_local_only": str(LOCAL_CHECKPOINT),
        "smoke_variants": list(VARIANTS), "automatic_oom_fallback": False,
    }


def validate_contract() -> dict[str, object]:
    expected = json.loads((V53 / "manifest_hashes.json").read_text(encoding="utf-8"))
    observed = {"train_sha256": sha256(TRAIN_MANIFEST), "devval_sha256": sha256(DEVVAL_MANIFEST)}
    if observed["train_sha256"] != expected["train_rgb_supervised_sha256"] or observed["devval_sha256"] != expected["devval_rgb_supervised_sha256"]:
        raise RuntimeError(f"V53 manifest hash mismatch: {observed}")
    train = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=False)
    devval = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    if (len(train), len(devval)) != (7187, 1845):
        raise RuntimeError(f"V53 manifest count mismatch: {len(train)}, {len(devval)}")
    train_sequences = {row["sequence"] for row in train.rows}
    devval_sequences = {row["sequence"] for row in devval.rows}
    if train_sequences & devval_sequences:
        raise RuntimeError("Train/devval sequence leakage")
    return {"counts": {"train": len(train), "devval": len(devval), "total": len(train) + len(devval)},
            "hashes": observed, "sequence_overlap": 0}


def validate_protected_paths() -> dict[str, object]:
    changed = set(git("diff", "--name-only", START_COMMIT).splitlines())
    forbidden = sorted(path for path in changed if path.startswith("runs/v5") and not path.startswith("runs/v54_mmuav_gpu_pilot/"))
    forbidden += sorted(path for path in changed if path in {"rarepdet/train_early_fusion.py", "datasets/triair_dataset.py",
                                                              "main.tex", "main_sivp_snjnl.tex"} or
                        path.startswith("manuscript/") or path.startswith("submission/"))
    if forbidden:
        raise RuntimeError(f"Protected file changes detected: {forbidden}")
    files = ["datasets/mmuav_feature_alignment_dataset.py", "rarepdet/experimental/mmuav_feature_alignment.py",
             "rarepdet/experimental/mmuav_feature_alignment_model.py",
             "rarepdet/experimental/mmuav_feature_alignment_detector.py", "rarepdet/tools/run_v54_mmuav_gpu_pilot.py",
             "tests/test_v54_mmuav_gpu_pilot.py"]
    return {"starting_commit": START_COMMIT, "protected_changes": [],
            "source_hashes": {path: sha256(ROOT / path) for path in files}, "gpu_step_limit": MAX_STEPS}


def make_sample_order(dataset: MMUAVFeatureAlignmentDataset) -> list[int]:
    generator = torch.Generator(device="cpu").manual_seed(0)
    order = torch.randperm(len(dataset), generator=generator)[:MAX_STEPS].tolist()
    ids = [dataset.rows[index]["original_row_id"] for index in order]
    text = "\n".join(ids) + "\n"
    (OUT / "sample_order.txt").write_text(text, encoding="utf-8")
    order_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    (OUT / "sample_order_sha256.txt").write_text(order_hash + "\n", encoding="utf-8")
    return order


def target_to_device(sample: dict[str, object], device: torch.device) -> list[dict[str, torch.Tensor]]:
    target = sample["target_rgb"]
    if target["boxes"].numel() == 0:
        raise RuntimeError(f"Missing RGB target: {sample['original_row_id']}")
    return [{"boxes": target["boxes"].to(device), "labels": target["labels"].to(device)}]


def inputs_to_device(sample: dict[str, object], device: torch.device) -> tuple[torch.Tensor, ...]:
    return tuple(sample[key].unsqueeze(0).to(device, non_blocking=False) for key in ("rgb", "ir", "event"))


def norm_for(parameters) -> tuple[float, bool, int]:
    squares, count, finite = 0.0, 0, True
    for parameter in parameters:
        if parameter.grad is None:
            continue
        gradient = parameter.grad.detach().float()
        finite = finite and bool(torch.isfinite(gradient).all())
        squares += float(gradient.square().sum().cpu())
        count += 1
    return math.sqrt(squares), finite, count


def losses_are_finite(losses: dict[str, torch.Tensor]) -> bool:
    return bool(losses) and all(torch.isfinite(value).all() for value in losses.values())


def assert_step_allowed(completed: int) -> None:
    if completed >= MAX_STEPS:
        raise RuntimeError("Optimizer-step guard would exceed 200")


def synchronize() -> None:
    torch.cuda.synchronize()


def memory_snapshot(label: str) -> dict[str, object]:
    return {"label": label, "timestamp": datetime.now().isoformat(timespec="seconds"),
            "allocated_bytes": torch.cuda.memory_allocated(), "reserved_bytes": torch.cuda.memory_reserved(),
            "max_allocated_bytes": torch.cuda.max_memory_allocated(), "max_reserved_bytes": torch.cuda.max_memory_reserved()}


def nvidia_snapshot(label: str) -> str:
    output = subprocess.check_output(["nvidia-smi"], text=True, errors="replace")
    return f"===== {label} {datetime.now().isoformat(timespec='seconds')} =====\n{output}\n"


def smoke_matrix(dataset: MMUAVFeatureAlignmentDataset, device: torch.device) -> list[dict[str, object]]:
    sample = dataset[0]
    results = []
    for variant in VARIANTS:
        configure_seed(0)
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        model = MMUAVFeatureAlignmentDetector(variant=variant).to(device).train()
        inputs = inputs_to_device(sample, device)
        targets = target_to_device(sample, device)
        model.zero_grad(set_to_none=True)
        started = time.perf_counter()
        losses = model(*inputs, targets)
        total = sum(losses.values())
        if not losses_are_finite(losses) or not torch.isfinite(total):
            raise RuntimeError(f"Non-finite smoke loss: {variant}")
        total.backward()
        synchronize()
        global_norm, gradients_finite, gradient_tensors = norm_for(model.parameters())
        diagnostics = model.alignment_diagnostics()
        if not gradients_finite or not diagnostics["ir"]["finite"] or not diagnostics["event"]["finite"]:
            raise RuntimeError(f"Non-finite smoke gradients/alignment: {variant}")
        results.append({"variant": variant, "optimizer_steps": 0, "losses": {key: float(value.detach().cpu()) for key, value in losses.items()},
                        "loss_total": float(total.detach().cpu()), "global_gradient_norm": global_norm,
                        "gradient_tensors": gradient_tensors, "diagnostics": diagnostics,
                        "elapsed_sec": time.perf_counter() - started, "memory": memory_snapshot(variant), "status": "PASS"})
        del model, inputs, targets, losses, total
        torch.cuda.empty_cache()
    return results


def csv_writer(path: Path, fields: list[str]):
    handle = path.open("w", encoding="utf-8", newline="")
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    return handle, writer


def run_primary(dataset: MMUAVFeatureAlignmentDataset, order: list[int], device: torch.device,
                snapshots: list[str]) -> tuple[torch.nn.Module, dict[str, object]]:
    configure_seed(0)
    model = MMUAVFeatureAlignmentDetector("alignment_on_equal").to(device).train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    log_handle, log = csv_writer(OUT / "training_log.csv", TRAIN_FIELDS)
    memory_handle, memory = csv_writer(OUT / "memory_trace.csv", ["step", "allocated_bytes", "reserved_bytes", "max_allocated_bytes", "max_reserved_bytes"])
    alignment_rows = []
    losses_total, step_times = [], []
    completed = 0
    previous_end = time.perf_counter()
    try:
        for wanted_step, index in enumerate(order, start=1):
            assert_step_allowed(completed)
            step_started = time.perf_counter()
            sample = dataset[index]
            data_done = time.perf_counter()
            if sample["split"] != "train" or not str(sample["original_row_id"]).startswith("train:"):
                raise RuntimeError(f"Devval optimization leakage: {sample['original_row_id']}")
            inputs = inputs_to_device(sample, device)
            targets = target_to_device(sample, device)
            optimizer.zero_grad(set_to_none=True)
            forward_started = time.perf_counter()
            losses = model(*inputs, targets)
            total = sum(losses.values())
            synchronize()
            forward_done = time.perf_counter()
            if not losses_are_finite(losses) or not torch.isfinite(total):
                raise RuntimeError(f"Non-finite loss before step {wanted_step}")
            diagnostics = model.alignment_diagnostics()
            if wanted_step == 1:
                alignment_rows.append({"step": 0, **diagnostics})
            total.backward()
            synchronize()
            backward_done = time.perf_counter()
            global_norm, gradients_finite, _ = norm_for(model.parameters())
            ir_norm, ir_finite, _ = norm_for(model.feature_scaffold.ir_aligner.parameters())
            event_norm, event_finite, _ = norm_for(model.feature_scaffold.event_aligner.parameters())
            parameters_finite = all(torch.isfinite(parameter).all() for parameter in model.parameters())
            finite = gradients_finite and ir_finite and event_finite and parameters_finite and diagnostics["ir"]["finite"] and diagnostics["event"]["finite"]
            if not finite:
                raise RuntimeError(f"Non-finite gradient/parameter/alignment before step {wanted_step}")
            optimizer.step()
            completed += 1
            if completed != wanted_step:
                raise RuntimeError(f"Optimizer-step counter mismatch: {completed} != {wanted_step}")
            if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                raise RuntimeError(f"Non-finite parameter after step {completed}")
            synchronize()
            optimizer_done = time.perf_counter()
            row = {field: "" for field in TRAIN_FIELDS}
            loss_values = {key: float(value.detach().cpu()) for key, value in losses.items()}
            row.update({"step": completed, "original_row_id": sample["original_row_id"], "loss_total": float(total.detach().cpu()),
                        "loss_classifier": loss_values.get("classification", loss_values.get("loss_classifier", "")),
                        "loss_box_reg": loss_values.get("bbox_regression", loss_values.get("loss_box_reg", "")),
                        "loss_centerness": loss_values.get("bbox_ctrness", loss_values.get("loss_centerness", "")),
                        "learning_rate": optimizer.param_groups[0]["lr"], "global_gradient_norm": global_norm,
                        "ir_alignment_gradient_norm": ir_norm, "event_alignment_gradient_norm": event_norm, "finite": True,
                        "cuda_allocated_bytes": torch.cuda.memory_allocated(), "cuda_reserved_bytes": torch.cuda.memory_reserved(),
                        "data_time_sec": data_done - previous_end, "forward_time_sec": forward_done - forward_started,
                        "backward_time_sec": backward_done - forward_done, "optimizer_time_sec": optimizer_done - backward_done,
                        "step_time_sec": optimizer_done - step_started})
            for modality in ("ir", "event"):
                d = diagnostics[modality]
                for key in ("theta_mean", "theta_std", "theta_min", "theta_max", "theta_max_abs_deviation",
                            "determinant_mean", "grid_oob_fraction"):
                    row[f"{modality}_{key}"] = d[key]
            log.writerow(row)
            log_handle.flush()
            mem = memory_snapshot(f"step_{completed}")
            memory.writerow({"step": completed, **{key: mem[key] for key in ("allocated_bytes", "reserved_bytes", "max_allocated_bytes", "max_reserved_bytes")}})
            memory_handle.flush()
            losses_total.append(row["loss_total"])
            step_times.append(row["step_time_sec"])
            if completed in KEY_STEPS:
                with torch.no_grad():
                    model._feature_forward(*inputs)
                alignment_rows.append({"step": completed, **model.alignment_diagnostics()})
            if completed == 1:
                snapshots.append(nvidia_snapshot("after_warmup_step_1"))
            if completed == 150:
                snapshots.append(nvidia_snapshot("near_peak_step_150"))
            previous_end = optimizer_done
    finally:
        log_handle.close()
        memory_handle.close()
    write_json(OUT / "alignment_trace.json", alignment_rows)
    with (OUT / "alignment_trace.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["step", "modality", "theta_mean", "theta_std", "theta_min", "theta_max", "theta_max_abs_deviation",
                  "determinant_mean", "determinant_min", "determinant_max", "grid_oob_fraction", "finite"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for entry in alignment_rows:
            for modality in ("ir", "event"):
                writer.writerow({"step": entry["step"], "modality": modality, **entry[modality]})
    summary = {"completed_optimizer_steps": completed, "step_limit": MAX_STEPS, "all_finite": True,
               "loss_first": losses_total[0], "loss_last": losses_total[-1], "loss_min": min(losses_total),
               "loss_max": max(losses_total), "step_time_mean_sec": sum(step_times) / len(step_times),
               "step_time_min_sec": min(step_times), "step_time_max_sec": max(step_times),
               "peak_allocated_bytes": torch.cuda.max_memory_allocated(), "peak_reserved_bytes": torch.cuda.max_memory_reserved()}
    if completed != MAX_STEPS:
        raise RuntimeError(f"Primary pilot incomplete: {completed}/{MAX_STEPS}")
    return model, summary


def inference_smoke(model: torch.nn.Module, device: torch.device) -> dict[str, object]:
    dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    model.eval()
    records = []
    torch.cuda.reset_peak_memory_stats()
    with torch.no_grad():
        for index in range(4):
            sample = dataset[index]
            inputs = inputs_to_device(sample, device)
            started = time.perf_counter()
            outputs = model(*inputs)
            synchronize()
            output = outputs[0]
            finite = all(torch.isfinite(value).all() for value in output.values())
            if not finite:
                raise RuntimeError(f"Non-finite inference output: {sample['original_row_id']}")
            records.append({"original_row_id": sample["original_row_id"], "finite": True,
                            "boxes_shape": list(output["boxes"].shape), "scores_shape": list(output["scores"].shape),
                            "latency_sec": time.perf_counter() - started})
    return {"status": "PASS_EXECUTION_ONLY_NO_AP_AR", "sample_count": len(records), "records": records,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(), "peak_reserved_bytes": torch.cuda.max_memory_reserved()}


def save_local_checkpoint(model: torch.nn.Module, summary: dict[str, object]) -> dict[str, object]:
    LOCAL_CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state": model.state_dict(), "completed_optimizer_steps": MAX_STEPS,
                "variant": "alignment_on_equal", "accuracy_metrics": None}, LOCAL_CHECKPOINT)
    return {"produced": True, "local_path_not_committed": str(LOCAL_CHECKPOINT), "bytes": LOCAL_CHECKPOINT.stat().st_size,
            "sha256": sha256(LOCAL_CHECKPOINT), "completed_optimizer_steps": MAX_STEPS,
            "accuracy_metrics": None, "git_excluded": True}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    config = frozen_config()
    write_json(OUT / "pilot_config.json", config)
    contract = validate_contract()
    lock = validate_protected_paths()
    lock["manifest_contract"] = contract
    lock["config_sha256"] = sha256(OUT / "pilot_config.json")
    write_json(OUT / "source_lock_v54.json", lock)
    (OUT / "source_lock_v54.md").write_text(
        f"# V54 Source Lock\n\nStarting commit: `{START_COMMIT}`. V53 manifest hashes and counts reproduced. "
        "Production, V40-V53 evidence, V51 evidence, and manuscript changes: none before CUDA.\n", encoding="utf-8")
    dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=True)
    order = make_sample_order(dataset)
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v54_mmuav_gpu_pilot.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v54_mmuav_gpu_pilot.py\n", encoding="utf-8")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; V54 does not permit CPU fallback")
    device = torch.device("cuda:0")
    properties = torch.cuda.get_device_properties(device)
    environment = {"gpu": properties.name, "total_memory_bytes": properties.total_memory,
                   "torch_version": torch.__version__, "torch_cuda_runtime": torch.version.cuda,
                   "cudnn_version": torch.backends.cudnn.version(), "driver_nvidia_smi": subprocess.check_output(
                       ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"], text=True).strip()}
    snapshots = [nvidia_snapshot("before_launch")]
    smoke = smoke_matrix(dataset, device)
    write_json(OUT / "smoke_matrix.json", {"environment": environment, "variants": smoke})
    (OUT / "smoke_matrix.md").write_text(
        "# V54 CUDA Smoke Matrix\n\nAll four pre-registered interfaces completed finite forward/backward passes with zero optimizer steps. "
        "See `smoke_matrix.json` for loss, gradient, shape, theta, and memory records.\n", encoding="utf-8")
    model, summary = run_primary(dataset, order, device, snapshots)
    snapshots.append(nvidia_snapshot("after_completion"))
    (OUT / "nvidia_smi_snapshots.txt").write_text("\n".join(snapshots), encoding="utf-8")
    checkpoint = save_local_checkpoint(model, summary)
    write_json(OUT / "checkpoint_metadata.json", checkpoint)
    inference = inference_smoke(model, device)
    write_json(OUT / "postrun_inference_smoke.json", inference)
    summary.update({"environment": environment, "manifest_contract": contract, "checkpoint": checkpoint,
                    "postrun_inference_smoke": inference["status"], "ap_ar_computed": False,
                    "accuracy_claim": False, "gpu_optimizer_steps": MAX_STEPS})
    write_json(OUT / "training_summary.json", summary)
    (OUT / "training_summary.md").write_text(
        "# V54 Training Summary\n\nThis engineering pilot completed exactly 200 optimizer steps with finite losses, gradients, "
        "parameters, affine theta, and sampling grids. It produced no AP/AR or accuracy claim. See JSON/CSV logs for compact evidence.\n",
        encoding="utf-8")
    decision = {"decision": "V54_GPU_PILOT_PASS_READY_FOR_PAIRED_ALIGNMENT_ABLATION",
                "completed_optimizer_steps": MAX_STEPS, "pilot_only_not_accuracy_evidence": True,
                "ap_ar_computed": False, "protected_file_check_before_cuda": "PASS", "checkpoint_committed": False}
    write_json(OUT / "pilot_decision.json", decision)
    (OUT / "pilot_decision.md").write_text(
        "# V54 Pilot Decision\n\n`V54_GPU_PILOT_PASS_READY_FOR_PAIRED_ALIGNMENT_ABLATION`. This is an engineering and numerical-stability "
        "verdict only, not detector accuracy evidence.\n", encoding="utf-8")
    print(json.dumps({"decision": decision["decision"], **summary}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except torch.OutOfMemoryError as exc:
        raise SystemExit(f"V54_BLOCKED_OOM_OR_MEMORY: {exc}")
