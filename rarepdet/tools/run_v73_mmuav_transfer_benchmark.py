#!/usr/bin/env python
"""Prepare, train, resume, and evaluate the frozen V73 nine-run benchmark."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.v73_alignment_transfer_detector import V73AlignmentTransferDetector
from rarepdet.models.early_fusion_fcos import build_detector
from rarepdet.tools import run_v71_mmuav_existing_devval_zero_shot as v71
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import configure_seed, inputs_to_device, target_to_device
from rarepdet.tools.run_v65_mmuav_seed0_softplus_fulltrain import full_coco_metrics


OUT = ROOT / "runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark"
LOCAL = Path(os.environ.get("V73_LOCAL_ROOT", r"D:\MM-UAV_v73_local"))
CHECKPOINT_REPO = Path(os.environ.get("V73_CHECKPOINT_REPO", r"E:\RepViT-main"))
TRAIN_MANIFEST = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt"
DEVVAL_MANIFEST = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"
STARTING_COMMIT = "3841455a39cced13a4925a6488a40b4a8f0c440b"
TRAIN_SHA256 = "e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a"
DEVVAL_SHA256 = "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54"
SEEDS = (0, 1, 2)
METHODS = ("scratch_equal", "triair_init_equal", "triair_init_reliability")
RUN_ORDER = tuple((seed, method) for seed in SEEDS for method in METHODS)
EPOCHS = 10
ROWS_PER_EPOCH = 7187
STEPS_PER_RUN = EPOCHS * ROWS_PER_EPOCH
TOTAL_STEPS = len(RUN_ORDER) * STEPS_PER_RUN
AUDIT_STEPS = {0, 50, 200, 1000, 5000, 10000, 20000, 40000, 60000, 71870}
METRICS = ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")
SCIENTIFIC_LABEL = "MM-UAV supervised cross-dataset transfer benchmark with learned feature alignment"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bytes_sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def tensor_sha256(value: torch.Tensor) -> str:
    tensor = value.detach().cpu().contiguous()
    digest = hashlib.sha256(f"{tensor.dtype}|{tuple(tensor.shape)}|".encode())
    digest.update(tensor.reshape(-1).view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def state_sha256(state: dict[str, torch.Tensor]) -> str:
    digest = hashlib.sha256()
    for key in sorted(state):
        digest.update(key.encode())
        digest.update(bytes.fromhex(tensor_sha256(state[key])))
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def run_id(seed: int, method: str) -> str:
    return f"v73_seed{seed}_{method}"


def fusion_mode(method: str) -> str:
    return "reliability" if method == "triair_init_reliability" else "equal"


def local_init(seed: int) -> Path:
    return LOCAL / "initializations" / f"seed{seed}_v73_common_init.pt"


def local_checkpoint(seed: int, method: str) -> Path:
    return LOCAL / "checkpoints" / f"{run_id(seed, method)}_final_step{STEPS_PER_RUN}.pt"


def local_recovery(seed: int, method: str) -> Path:
    return LOCAL / "recovery" / f"{run_id(seed, method)}_latest.pt"


def local_trace(seed: int, method: str) -> Path:
    return LOCAL / "traces" / f"{run_id(seed, method)}.jsonl"


def local_audits(seed: int, method: str) -> Path:
    return LOCAL / "audits" / f"{run_id(seed, method)}.json"


def source_item(seed: int, method: str) -> dict[str, object]:
    expected = "matched_early" if method == "triair_init_equal" else "reliability_p015"
    matches = [item for item in v71.CHECKPOINTS if item["seed"] == seed and item["method"] == expected]
    if len(matches) != 1:
        raise RuntimeError(f"Missing unique TriAir source for seed={seed}, method={method}")
    return matches[0]


def source_path(seed: int, method: str) -> Path:
    return CHECKPOINT_REPO / str(source_item(seed, method)["relative_path"])


def lr_for_step(step: int) -> float:
    if not 1 <= step <= STEPS_PER_RUN:
        raise ValueError(f"Invalid optimizer step: {step}")
    if step <= 500:
        return 1e-4 * step / 500.0
    progress = (step - 500) / (STEPS_PER_RUN - 500)
    return 1e-6 + 0.5 * (1e-4 - 1e-6) * (1.0 + math.cos(math.pi * progress))


def rng_state() -> dict[str, object]:
    return {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state(),
        "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
    }


def restore_rng(state: dict[str, object]) -> None:
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])
    if torch.cuda.is_available():
        torch.cuda.set_rng_state_all(state["cuda"])


def epoch_orders(seed: int, dataset: MMUAVFeatureAlignmentDataset) -> list[list[int]]:
    orders = []
    for epoch in range(EPOCHS):
        generator = torch.Generator(device="cpu").manual_seed(seed * 100_003 + epoch)
        order = torch.randperm(len(dataset), generator=generator).tolist()
        if len(order) != ROWS_PER_EPOCH or len(set(order)) != ROWS_PER_EPOCH:
            raise RuntimeError("Epoch order is not a complete permutation")
        orders.append(order)
    return orders


def order_record(seed: int, epoch: int, order: list[int], dataset: MMUAVFeatureAlignmentDataset) -> dict[str, object]:
    row_ids = [dataset.rows[index]["original_row_id"] for index in order]
    payload = ("\n".join(row_ids) + "\n").encode()
    return {
        "seed": seed,
        "epoch": epoch + 1,
        "rows": len(row_ids),
        "unique_rows": len(set(row_ids)),
        "row_id_order_sha256": bytes_sha256(payload),
        "index_order_sha256": bytes_sha256(np.asarray(order, dtype=np.int32).tobytes()),
    }


def freeze_common_initialization(seed: int) -> dict[str, object]:
    path = local_init(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    configure_seed(seed)
    model = V73AlignmentTransferDetector("equal")
    state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    if path.exists():
        payload = torch.load(path, map_location="cpu", weights_only=False)
        if payload["seed"] != seed or state_sha256(payload["state_dict"]) != state_sha256(state):
            raise RuntimeError(f"Existing seed-{seed} V73 initialization does not reproduce")
    else:
        torch.save({"seed": seed, "model_class": type(model).__name__, "state_dict": state}, path)
    reliability = V73AlignmentTransferDetector("reliability")
    result = reliability.load_state_dict(state, strict=True)
    final_weight = state["feature_scaffold.reliability_scorer.4.weight"]
    final_bias = state["feature_scaffold.reliability_scorer.4.bias"]
    return {
        "seed": seed,
        "local_artifact_id": f"seed{seed}_v73_common_init.pt",
        "file_sha256": sha256(path),
        "state_sha256": state_sha256(state),
        "bytes": path.stat().st_size,
        "tensor_count": len(state),
        "equal_and_reliability_strict_compatible": not result.missing_keys and not result.unexpected_keys,
        "reliability_final_layer_exact_zero": bool(torch.count_nonzero(final_weight) == 0 and
                                                    torch.count_nonzero(final_bias) == 0),
        "all_finite": all(torch.isfinite(value).all() for value in state.values()),
    }


def strict_verify_sources() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return v71.verify_checkpoints(CHECKPOINT_REPO)


def build_transfer(seed: int, method: str) -> tuple[dict[str, torch.Tensor], dict[str, object]]:
    common_payload = torch.load(local_init(seed), map_location="cpu", weights_only=False)
    destination = {key: value.clone() for key, value in common_payload["state_dict"].items()}
    if method == "scratch_equal":
        return destination, {
            "run_id": run_id(seed, method),
            "source": None,
            "transferred": [],
            "skipped_source": [],
            "unmatched_destination": sorted(destination),
            "transferred_numel": 0,
            "destination_numel": sum(value.numel() for value in destination.values()),
            "transferred_parameter_fraction": 0.0,
        }
    item = source_item(seed, method)
    path = source_path(seed, method)
    if sha256(path) != item["sha256"]:
        raise RuntimeError(f"TriAir source hash mismatch: {item['opaque_id']}")
    payload = torch.load(path, map_location="cpu", weights_only=False)
    source = payload["model_state"]
    original = build_detector(item["model_type"], img_size=640)
    strict = original.load_state_dict(source, strict=True)
    if strict.missing_keys or strict.unexpected_keys:
        raise RuntimeError(f"TriAir strict-load failure: {item['opaque_id']}")
    transferred = []
    used_source = set()
    shared_prefixes = ("backbone.repvit.", "backbone.fpn.", "head.")
    for source_key, source_value in source.items():
        if not source_key.startswith(shared_prefixes):
            continue
        destination_key = "detector." + source_key
        if destination_key not in destination or destination[destination_key].shape != source_value.shape:
            continue
        destination[destination_key] = source_value.detach().cpu().clone()
        used_source.add(source_key)
        transferred.append({
            "source_key": source_key,
            "destination_key": destination_key,
            "shape": list(source_value.shape),
            "numel": source_value.numel(),
            "source_tensor_sha256": tensor_sha256(source_value),
            "destination_tensor_sha256": tensor_sha256(destination[destination_key]),
        })
    skipped_source = [{
        "source_key": key,
        "shape": list(value.shape),
        "numel": value.numel(),
        "reason": "outside_shared_repvit_fpn_fcos_or_not_exact_shape_compatible",
    } for key, value in source.items() if key not in used_source]
    used_destination = {row["destination_key"] for row in transferred}
    unmatched_destination = sorted(key for key in destination if key not in used_destination)
    transferred_numel = sum(row["numel"] for row in transferred)
    destination_numel = sum(value.numel() for value in destination.values())
    if not transferred or any(row["source_tensor_sha256"] != row["destination_tensor_sha256"] for row in transferred):
        raise RuntimeError(f"Non-reproducible V73 transfer map: {run_id(seed, method)}")
    return destination, {
        "run_id": run_id(seed, method),
        "source": {
            "opaque_id": item["opaque_id"],
            "filename": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "model_class": type(original).__module__ + "." + type(original).__name__,
            "seed": seed,
            "strict_original_load": True,
        },
        "transferred": transferred,
        "skipped_source": skipped_source,
        "unmatched_destination": unmatched_destination,
        "transferred_numel": transferred_numel,
        "destination_numel": destination_numel,
        "transferred_parameter_fraction": transferred_numel / destination_numel,
        "partial_architecture_compatible_initialization": True,
        "tensor_repair_reshaping_interpolation_averaging_or_seed_substitution": False,
    }


def prepare() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    if git("rev-parse", "HEAD") != STARTING_COMMIT:
        raise RuntimeError("V73 preparation must begin at the frozen authorization commit")
    if sha256(TRAIN_MANIFEST) != TRAIN_SHA256 or sha256(DEVVAL_MANIFEST) != DEVVAL_SHA256:
        raise RuntimeError("Frozen MM-UAV manifest hash mismatch")
    train = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 640, validate_paths=True)
    devval = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 640, validate_paths=True)
    if (len(train), len(devval)) != (7187, 1845):
        raise RuntimeError("Frozen MM-UAV manifest row-count mismatch")
    source_manifest, source_verification = strict_verify_sources()
    init_records = [freeze_common_initialization(seed) for seed in SEEDS]
    order_records = []
    order_payload = {}
    for seed in SEEDS:
        orders = epoch_orders(seed, train)
        order_payload[str(seed)] = orders
        order_records.extend(order_record(seed, epoch, order, train) for epoch, order in enumerate(orders))
    write_json(LOCAL / "epoch_orders.json", order_payload)
    transfer_records = []
    for seed, method in RUN_ORDER:
        _, transfer = build_transfer(seed, method)
        transfer_records.append(transfer)
    write_json(OUT / "data_manifest_lock.json", {
        "train": {"rows": len(train), "sha256": TRAIN_SHA256},
        "devval": {"rows": len(devval), "sha256": DEVVAL_SHA256, "previously_exposed": True},
        "sequence_overlap": len({row["sequence"] for row in train.rows} &
                                {row["sequence"] for row in devval.rows}),
        "manifest_order_preserved": True,
    })
    write_json(OUT / "seed_epoch_order_hashes.json", {"records": order_records})
    write_json(OUT / "triair_source_checkpoint_manifest.json", {
        "entries": source_manifest,
        "verification": source_verification,
    })
    write_json(OUT / "transfer_map_per_run.json", {"runs": transfer_records})
    write_json(OUT / "initialization_audit.json", {"seed_initializations": init_records})
    protocol = {
        "task": "V73_MMUAV_TRIAIR_INITIALIZED_ALIGNMENT_AWARE_TRANSFER_BENCHMARK",
        "scientific_label": SCIENTIFIC_LABEL,
        "starting_commit": STARTING_COMMIT,
        "run_order": [run_id(seed, method) for seed, method in RUN_ORDER],
        "image_size": 640,
        "batch_size": 1,
        "epochs": EPOCHS,
        "steps_per_epoch": ROWS_PER_EPOCH,
        "steps_per_run": STEPS_PER_RUN,
        "total_optimizer_steps": TOTAL_STEPS,
        "optimizer": {"name": "AdamW", "lr": 1e-4, "weight_decay": 1e-4},
        "scheduler": {"warmup_steps": 500, "warmup": "linear", "decay": "cosine", "final_lr": 1e-6},
        "amp": False,
        "gradient_accumulation": False,
        "gradient_clipping": False,
        "workers": 0,
        "augmentation": False,
        "devval_during_training": False,
        "audit_steps": sorted(AUDIT_STEPS),
    }
    write_json(OUT / "protocol.json", protocol)
    (OUT / "protocol.md").write_text(
        "# V73 Protocol\n\nNine supervised MM-UAV runs use one frozen 640px alignment-aware contract. "
        "Each seed shares ten deterministic epoch orders and one common initialization across its three "
        "variants. Only exact shared RepViT/FPN/FCOS tensors are transferred from the six authoritative "
        "TriAir checkpoints. Devval is evaluated once per final checkpoint.\n", encoding="utf-8")
    write_json(OUT / "recovery_ledger.json", {"events": [], "recovery_events": 0})
    write_json(OUT / "training_trace_summary.json", {"status": "PREPARED", "runs": []})
    write_json(OUT / "alignment_and_fusion_diagnostics.json", {"status": "PREPARED", "runs": []})
    write_json(OUT / "final_checkpoint_manifest.json", {"status": "PENDING", "runs": []})
    write_json(OUT / "claim_boundary.json", {
        "scientific_label": SCIENTIFIC_LABEL,
        "supervised_target_domain_training": True,
        "zero_shot_or_independent_blind_external_test": False,
        "official_untouched_test": False,
        "statistical_significance_claim": False,
    })
    write_json(OUT / "protected_file_audit.json", {
        "protected_files": [
            "rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
            "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py",
        ],
        "changes": [],
    })
    (OUT / "test_commands.txt").write_text(
        f"{sys.executable} rarepdet/tools/run_v73_mmuav_transfer_benchmark.py --prepare\n"
        f"{sys.executable} -m unittest discover -s tests -p test_v73_mmuav_transfer_benchmark.py -v\n"
        f"{sys.executable} rarepdet/tools/run_v73_mmuav_transfer_benchmark.py --timing-steps 10\n"
        f"{sys.executable} rarepdet/tools/run_v73_mmuav_transfer_benchmark.py --run-all\n",
        encoding="utf-8")
    print(json.dumps({"status": "V73_PREPARED", "runs": 9, "steps": TOTAL_STEPS}, indent=2))


def load_run_state(seed: int, method: str) -> dict[str, torch.Tensor]:
    state, _ = build_transfer(seed, method)
    return state


def parameter_norm(parameters) -> tuple[float, bool]:
    total = 0.0
    finite = True
    for parameter in parameters:
        value = parameter.detach().float()
        finite = finite and bool(torch.isfinite(value).all())
        total += float(value.square().sum().cpu())
    return math.sqrt(total), finite


def gradient_norm(parameters) -> tuple[float, bool]:
    total = 0.0
    finite = True
    for parameter in parameters:
        if parameter.grad is not None:
            value = parameter.grad.detach().float()
            finite = finite and bool(torch.isfinite(value).all())
            total += float(value.square().sum().cpu())
    return math.sqrt(total), finite


def audit(model: V73AlignmentTransferDetector, sample: dict[str, object], losses: dict[str, torch.Tensor],
          step: int) -> dict[str, object]:
    alignment_parameters = list(model.feature_scaffold.ir_aligner.parameters()) + \
        list(model.feature_scaffold.event_aligner.parameters())
    scorer_parameters = list(model.feature_scaffold.reliability_scorer.parameters())
    alignment_parameter_norm, alignment_parameters_finite = parameter_norm(alignment_parameters)
    alignment_gradient_norm, alignment_gradients_finite = gradient_norm(alignment_parameters)
    scorer_parameter_norm, scorer_parameters_finite = parameter_norm(scorer_parameters)
    scorer_gradient_norm, scorer_gradients_finite = gradient_norm(scorer_parameters)
    diagnostics = model.alignment_diagnostics()
    fusion = model.fusion_diagnostics()
    target = sample["target_rgb"]["boxes"]
    return {
        "step": step,
        "losses": {key: float(value.detach().cpu()) for key, value in losses.items()},
        "losses_finite": all(torch.isfinite(value).all() for value in losses.values()),
        "parameters_finite": all(torch.isfinite(value).all() for value in model.state_dict().values()),
        "alignment_parameter_norm": alignment_parameter_norm,
        "alignment_gradient_norm": alignment_gradient_norm,
        "alignment_parameters_finite": alignment_parameters_finite,
        "alignment_gradients_finite": alignment_gradients_finite,
        "scorer_parameter_norm": scorer_parameter_norm,
        "scorer_gradient_norm": scorer_gradient_norm,
        "scorer_parameters_finite": scorer_parameters_finite,
        "scorer_gradients_finite": scorer_gradients_finite,
        "activation_counts": model.activation_counts(),
        "feature_alignment": diagnostics,
        "fusion": fusion,
        "decoded_target_geometry": {
            "box_count": int(target.shape[0]),
            "finite": bool(torch.isfinite(target).all()),
            "valid": bool(((target[:, 2:] - target[:, :2]) > 0).all()),
            "min": float(target.min()),
            "max": float(target.max()),
        },
    }


def save_recovery(model: V73AlignmentTransferDetector, optimizer: torch.optim.Optimizer, seed: int,
                  method: str, completed_steps: int, elapsed_seconds: float) -> dict[str, object]:
    path = local_recovery(seed, method)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    payload = {
        "run_id": run_id(seed, method),
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "scheduler_step": completed_steps,
        "completed_steps": completed_steps,
        "completed_epochs": completed_steps // ROWS_PER_EPOCH,
        "rng_state": rng_state(),
        "elapsed_seconds": elapsed_seconds,
        "order_file_sha256": sha256(LOCAL / "epoch_orders.json"),
    }
    torch.save(payload, temporary)
    os.replace(temporary, path)
    return {
        "event": "epoch_recovery_checkpoint",
        "run_id": run_id(seed, method),
        "step": completed_steps,
        "epoch": completed_steps // ROWS_PER_EPOCH,
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def append_ledger(event: dict[str, object]) -> None:
    ledger = read_json(OUT / "recovery_ledger.json")
    ledger["events"].append(event)
    if event["event"] == "resumed":
        ledger["recovery_events"] += 1
    write_json(OUT / "recovery_ledger.json", ledger)


def train_one(seed: int, method: str, device: torch.device) -> dict[str, object]:
    name = run_id(seed, method)
    final_path = local_checkpoint(seed, method)
    if final_path.exists():
        payload = torch.load(final_path, map_location="cpu", weights_only=False)
        if payload["completed_steps"] != STEPS_PER_RUN:
            raise RuntimeError(f"Incomplete final checkpoint: {name}")
        summary = dict(payload["summary"])
        summary["checkpoint_sha256"] = sha256(final_path)
        summary["checkpoint_bytes"] = final_path.stat().st_size
        return summary
    dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 640, validate_paths=False)
    orders = read_json(LOCAL / "epoch_orders.json")[str(seed)]
    configure_seed(seed)
    model = V73AlignmentTransferDetector(fusion_mode(method)).to(device)
    model.load_state_dict(load_run_state(seed, method), strict=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    completed = 0
    prior_elapsed = 0.0
    recovery = local_recovery(seed, method)
    if recovery.exists():
        payload = torch.load(recovery, map_location="cpu", weights_only=False)
        if payload["run_id"] != name or payload["order_file_sha256"] != sha256(LOCAL / "epoch_orders.json"):
            raise RuntimeError(f"Recovery contract mismatch: {name}")
        model.load_state_dict(payload["model_state"], strict=True)
        optimizer.load_state_dict(payload["optimizer_state"])
        completed = int(payload["completed_steps"])
        prior_elapsed = float(payload["elapsed_seconds"])
        restore_rng(payload["rng_state"])
        append_ledger({"event": "resumed", "run_id": name, "step": completed})
    model.train()
    trace_path = local_trace(seed, method)
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if completed else "w"
    audit_path = local_audits(seed, method)
    audits = read_json(audit_path)["audits"] if completed and audit_path.exists() else []
    if completed and not audit_path.exists():
        raise RuntimeError(f"Recovery exists without incremental audits: {name}")
    step_times = []
    started = time.perf_counter()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    with trace_path.open(mode, encoding="utf-8") as trace:
        if completed == 0:
            sample = dataset[orders[0][0]]
            optimizer.zero_grad(set_to_none=True)
            losses = model(*inputs_to_device(sample, device), target_to_device(sample, device))
            sum(losses.values()).backward()
            audits.append(audit(model, sample, losses, 0))
            write_json(audit_path, {"audits": audits})
            optimizer.zero_grad(set_to_none=True)
        for step in range(completed + 1, STEPS_PER_RUN + 1):
            epoch = (step - 1) // ROWS_PER_EPOCH
            offset = (step - 1) % ROWS_PER_EPOCH
            sample = dataset[orders[epoch][offset]]
            lr = lr_for_step(step)
            for group in optimizer.param_groups:
                group["lr"] = lr
            optimizer.zero_grad(set_to_none=True)
            step_started = time.perf_counter()
            losses = model(*inputs_to_device(sample, device), target_to_device(sample, device))
            total = sum(losses.values())
            if not torch.isfinite(total):
                raise RuntimeError(f"Non-finite loss at {name} step {step}")
            total.backward()
            if not all(torch.isfinite(parameter.grad).all() for parameter in model.parameters()
                       if parameter.grad is not None):
                raise RuntimeError(f"Non-finite gradient at {name} step {step}")
            if step in AUDIT_STEPS:
                audits.append(audit(model, sample, losses, step))
                write_json(audit_path, {"audits": audits})
            optimizer.step()
            if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                raise RuntimeError(f"Non-finite parameter at {name} step {step}")
            torch.cuda.synchronize()
            elapsed = time.perf_counter() - step_started
            step_times.append(elapsed)
            if step in AUDIT_STEPS or step % ROWS_PER_EPOCH == 0:
                trace.write(json.dumps({
                    "step": step,
                    "epoch": epoch + 1,
                    "offset": offset,
                    "original_row_id": sample["original_row_id"],
                    "lr": lr,
                    "loss_total": float(total.detach().cpu()),
                    "losses": {key: float(value.detach().cpu()) for key, value in losses.items()},
                    "step_seconds": elapsed,
                }, sort_keys=True) + "\n")
                trace.flush()
            if step % ROWS_PER_EPOCH == 0:
                event = save_recovery(model, optimizer, seed, method, step,
                                      prior_elapsed + time.perf_counter() - started)
                append_ledger(event)
                print(f"V73_EPOCH_COMPLETE run={name} epoch={epoch + 1}/10 step={step}", flush=True)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_state = {key: value.detach().cpu() for key, value in model.state_dict().items()}
    summary = {
        "run_id": name,
        "seed": seed,
        "method": method,
        "completed_optimizer_steps": STEPS_PER_RUN,
        "completed_epochs": EPOCHS,
        "all_finite": True,
        "elapsed_seconds": prior_elapsed + time.perf_counter() - started,
        "mean_step_seconds_current_session": statistics.fmean(step_times),
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "audit_steps": [row["step"] for row in audits],
        "devval_inference_before_final": False,
        "final_state_sha256": state_sha256(final_state),
    }
    torch.save({
        "run_id": name,
        "seed": seed,
        "method": method,
        "model_state": final_state,
        "completed_steps": STEPS_PER_RUN,
        "summary": summary,
    }, final_path)
    summary["checkpoint_sha256"] = sha256(final_path)
    summary["checkpoint_bytes"] = final_path.stat().st_size
    write_json(audit_path, {"audits": audits})
    del model, optimizer
    torch.cuda.empty_cache()
    return summary


def timing(steps: int) -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    device = torch.device("cuda:0")
    dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 640, validate_paths=False)
    model = V73AlignmentTransferDetector("reliability").to(device)
    model.load_state_dict(load_run_state(0, "triair_init_reliability"), strict=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    model.train()
    measurements = []
    for step in range(steps + 2):
        sample = dataset[step]
        optimizer.zero_grad(set_to_none=True)
        started = time.perf_counter()
        losses = model(*inputs_to_device(sample, device), target_to_device(sample, device))
        sum(losses.values()).backward()
        optimizer.step()
        torch.cuda.synchronize()
        if step >= 2:
            measurements.append(time.perf_counter() - started)
    mean = statistics.fmean(measurements)
    result = {
        "timing_steps": steps,
        "mean_step_seconds": mean,
        "estimated_total_gpu_days": mean * TOTAL_STEPS / 86400,
        "estimated_per_run_hours": mean * STEPS_PER_RUN / 3600,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "protocol_mutation": False,
        "timing_model": "seed0_triair_init_reliability",
    }
    write_json(OUT / "gpu_timing_gate.json", result)
    print(json.dumps(result, indent=2))


def evaluate_one(seed: int, method: str, device: torch.device) -> dict[str, object]:
    name = run_id(seed, method)
    marker = LOCAL / "evaluation_markers" / f"{name}.json"
    result_path = LOCAL / "evaluation_results" / f"{name}.json"
    if result_path.exists():
        return read_json(result_path)
    if marker.exists():
        raise RuntimeError(f"Prior incomplete evaluation attempt forbids rerun: {name}")
    checkpoint = local_checkpoint(seed, method)
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if payload["completed_steps"] != STEPS_PER_RUN:
        raise RuntimeError(f"Final checkpoint incomplete: {name}")
    marker.parent.mkdir(parents=True, exist_ok=True)
    write_json(marker, {"attempt": 1, "checkpoint_sha256": sha256(checkpoint), "rows": 1845})
    model = V73AlignmentTransferDetector(fusion_mode(method)).to(device)
    model.load_state_dict(payload["model_state"], strict=True)
    model.detector.score_thresh = 0.001
    model.detector.nms_thresh = 0.6
    model.detector.detections_per_img = 100
    model.eval()
    dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 640, validate_paths=False)
    predictions, targets = [], []
    images_with_predictions = 0
    valid_boxes = 0
    fusion_rows = []
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    with torch.no_grad():
        for index in range(len(dataset)):
            sample = dataset[index]
            output = model(*inputs_to_device(sample, device))[0]
            boxes = output["boxes"]
            finite = torch.isfinite(boxes).all(dim=1)
            valid = finite & (boxes[:, 2] > boxes[:, 0]) & (boxes[:, 3] > boxes[:, 1])
            if not bool(finite.all() and valid.all()):
                raise RuntimeError(f"Invalid decoded prediction: {name}, row {index}")
            valid_boxes += int(valid.sum())
            images_with_predictions += int(boxes.shape[0] > 0)
            predictions.append({key: value.detach().cpu() for key, value in output.items()})
            target = sample["target_rgb"]
            targets.append({"boxes": target["boxes"].cpu(), "labels": target["labels"].cpu()})
            if method == "triair_init_reliability":
                fusion_rows.append(model.fusion_diagnostics())
    torch.cuda.synchronize()
    metrics = full_coco_metrics(predictions, targets)
    elapsed = time.perf_counter() - started
    result = {
        "run_id": name,
        "seed": seed,
        "method": method,
        **{key: metrics[key] for key in METRICS},
        "prediction_count": metrics["detections"],
        "image_coverage": images_with_predictions,
        "images": metrics["images"],
        "finite_valid_decoded_boxes": valid_boxes,
        "wall_clock_seconds": elapsed,
        "peak_gpu_memory_bytes": torch.cuda.max_memory_allocated(),
        "evaluation_attempt": 1,
        "final_checkpoint_only": True,
        "checkpoint_sha256": sha256(checkpoint),
        "fusion_diagnostics": fusion_rows,
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(result_path, result)
    return result


def summarize(training: list[dict[str, object]], results: list[dict[str, object]]) -> None:
    compact_results = [{key: value for key, value in row.items() if key != "fusion_diagnostics"} for row in results]
    write_json(OUT / "per_run_metrics.json", {"records": compact_results})
    with (OUT / "per_run_metrics.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["run_id", "seed", "method", *METRICS, "prediction_count", "image_coverage",
                  "wall_clock_seconds", "peak_gpu_memory_bytes", "checkpoint_sha256"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(compact_results)
    by_run = {row["run_id"]: row for row in results}
    comparison_rows = []
    comparison_specs = (
        ("triair_init_equal_minus_scratch_equal", "triair_init_equal", "scratch_equal"),
        ("triair_init_reliability_minus_triair_init_equal", "triair_init_reliability", "triair_init_equal"),
        ("triair_init_reliability_minus_scratch_equal", "triair_init_reliability", "scratch_equal"),
    )
    for seed in SEEDS:
        for label, left, right in comparison_specs:
            row = {"seed": seed, "comparison": label}
            for metric in METRICS:
                row[metric] = by_run[run_id(seed, left)][metric] - by_run[run_id(seed, right)][metric]
            comparison_rows.append(row)
    write_json(OUT / "paired_transfer_comparison.json", {"records": comparison_rows})
    with (OUT / "paired_transfer_comparison.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["seed", "comparison", *METRICS])
        writer.writeheader()
        writer.writerows(comparison_rows)
    summaries = {"methods": {}, "paired_differences": {}}
    for method in METHODS:
        rows = [row for row in results if row["method"] == method]
        summaries["methods"][method] = {}
        for metric in METRICS:
            values = [row[metric] for row in rows]
            summaries["methods"][method][metric] = {
                "mean": statistics.fmean(values), "sample_std": statistics.stdev(values),
                "min": min(values), "max": max(values), "range": max(values) - min(values),
            }
    for label, _, _ in comparison_specs:
        rows = [row for row in comparison_rows if row["comparison"] == label]
        summaries["paired_differences"][label] = {}
        for metric in METRICS:
            values = [row[metric] for row in rows]
            summaries["paired_differences"][label][metric] = {
                "mean": statistics.fmean(values), "sample_std": statistics.stdev(values),
                "min": min(values), "max": max(values), "range": max(values) - min(values),
            }
    write_json(OUT / "three_seed_summary.json", summaries)
    transfer = read_json(OUT / "transfer_map_per_run.json")
    write_json(OUT / "training_trace_summary.json", {"status": "COMPLETE", "runs": training})
    fusion_compact = []
    for row in results:
        if row["method"] != "triair_init_reliability":
            continue
        diagnostics = row["fusion_diagnostics"]
        modality_means = {
            modality: statistics.fmean(item["per_modality"][modality]["mean"] for item in diagnostics)
            for modality in ("rgb", "ir", "event")
        }
        fusion_compact.append({
            "run_id": row["run_id"],
            "mean_weights": modality_means,
            "mean_entropy": statistics.fmean(item["entropy_mean"] for item in diagnostics),
            "mean_dominant_fraction": statistics.fmean(item["dominance_fraction_mean"] for item in diagnostics),
            "departed_from_uniform": any(item["departed_from_exact_uniform"] for item in diagnostics),
        })
    write_json(OUT / "alignment_and_fusion_diagnostics.json", {
        "status": "COMPLETE",
        "reliability_runs": fusion_compact,
    })
    checkpoint_rows = [{
        "run_id": row["run_id"],
        "local_artifact_id": local_checkpoint(row["seed"], row["method"]).name,
        "sha256": row["checkpoint_sha256"],
        "bytes": row["checkpoint_bytes"],
        "completed_optimizer_steps": row["completed_optimizer_steps"],
    } for row in training]
    write_json(OUT / "final_checkpoint_manifest.json", {"status": "COMPLETE", "runs": checkpoint_rows})
    write_json(OUT / "final_decision.json", {
        "decision": "V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE",
        "scientific_label": SCIENTIFIC_LABEL,
        "optimizer_steps": sum(row["completed_optimizer_steps"] for row in training),
        "devval_evaluations": len(results),
        "transfer_coverage": [{
            "run_id": row["run_id"],
            "transferred_parameter_fraction": row["transferred_parameter_fraction"],
        } for row in transfer["runs"]],
    })
    (OUT / "handoff.md").write_text(
        "# V73 Handoff\n\nDecision: `V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE`.\n\n"
        "Nine frozen 10-epoch supervised MM-UAV runs and nine final-checkpoint-only devval evaluations "
        "completed. Interpret all three-seed comparisons descriptively under the exposed-devval claim boundary.\n",
        encoding="utf-8")


def run_all() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    device = torch.device("cuda:0")
    training = []
    for seed, method in RUN_ORDER:
        training.append(train_one(seed, method, device))
    results = []
    for seed, method in RUN_ORDER:
        results.append(evaluate_one(seed, method, device))
    summarize(training, results)
    print(json.dumps({"decision": "V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE"}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--timing-steps", type=int)
    group.add_argument("--run-all", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.timing_steps is not None:
        if args.timing_steps <= 0:
            raise ValueError("timing steps must be positive")
        timing(args.timing_steps)
    else:
        run_all()


if __name__ == "__main__":
    main()
