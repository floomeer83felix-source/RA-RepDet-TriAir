#!/usr/bin/env python
"""Verify authoritative V81 weights and benchmark exact-identity detectors."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import json
from math import ceil
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

import torch
import torchvision


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.experimental.v76_single_modality_detector import (
    INPUT_CHANNELS,
    build_v76_single_modality_detector,
)
from rarepdet.models.early_fusion_fcos import build_detector


V81_REGISTRY = PROJECT_ROOT / "runs/v81_single_modality_retraining_reconciliation/checkpoint_manifest.json"
V48_REGISTRY = PROJECT_ROOT / "runs/v48_complete_ablation/causal_ablation_summary.json"
DEFAULT_OUT = PROJECT_ROOT / "runs/v83_post_v81_weight_evidence"
EXPECTED_SPLIT_SHA256 = "722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f"
EXPECTED_MODEL_CFG = {
    "experiment": "V76_TRIAIR_SINGLE_MODALITY_ABLATION",
    "model_name": "repvit_m0_9.dist_300e_in1k",
    "img_size": 640,
    "num_classes": 2,
    "fpn_out_channels": 128,
}
FUSION_VARIANTS = {"matched_early": "early", "ra_full_p015": "reliability"}


def resolve(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(values: list[float], fraction: float) -> float:
    return sorted(values)[max(0, ceil(len(values) * fraction) - 1)]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)


def locate_v81_weight(entry: dict) -> Path:
    archived = resolve(entry["weights"])
    if archived.is_file():
        return archived
    local = (
        PROJECT_ROOT
        / "runs/v76_triair_single_modality_ablation/training"
        / entry["run_id"]
        / "weights/best.pt"
    )
    return local


def check_v81_entry(entry: dict) -> tuple[dict, dict | None]:
    path = locate_v81_weight(entry)
    record = {
        "run_id": entry["run_id"],
        "input_mode": entry["input_mode"],
        "seed": entry["seed"],
        "checkpoint": str(path),
        "exists": path.is_file(),
        "expected_sha256": entry["checkpoint_sha256"],
        "expected_epoch": entry["checkpoint_epoch"],
        "expected_split_sha256": entry["split_sha256"],
        "checks": {},
    }
    if not path.is_file():
        record["status"] = "FAIL"
        record["checks"]["exists"] = False
        return record, None

    actual_hash = sha256(path)
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    cfg = checkpoint.get("model_cfg", {})
    train_args = checkpoint.get("train_args", {})
    expected_cfg = {
        **EXPECTED_MODEL_CFG,
        "input_mode": entry["input_mode"],
        "in_chans": INPUT_CHANNELS[entry["input_mode"]],
    }
    checks = {
        "exists": True,
        "sha256": actual_hash == entry["checkpoint_sha256"],
        "split_sha256": entry["split_sha256"] == EXPECTED_SPLIT_SHA256,
        "epoch": checkpoint.get("epoch") == entry["checkpoint_epoch"],
        "input_mode": cfg.get("input_mode") == entry["input_mode"],
        "seed": train_args.get("seed") == entry["seed"],
        "model_configuration": all(cfg.get(key) == value for key, value in expected_cfg.items()),
        "model_state_present": isinstance(checkpoint.get("model_state"), dict),
    }
    record.update(
        actual_sha256=actual_hash,
        actual_epoch=checkpoint.get("epoch"),
        actual_model_cfg=cfg,
        actual_train_seed=train_args.get("seed"),
        checks=checks,
        status="PASS" if all(checks.values()) else "FAIL",
    )
    return record, checkpoint


def v81_preflight(out_dir: Path) -> list[dict]:
    registry = json.loads(V81_REGISTRY.read_text(encoding="utf-8"))
    entries = registry.get("entries", [])
    records = []
    benchmark_entries = []
    seen = set()
    for entry in entries:
        record, _ = check_v81_entry(entry)
        records.append(record)
        seen.add(entry["run_id"])
        if record["status"] == "PASS":
            benchmark_entries.append({**entry, "checkpoint": record["checkpoint"], "family": "single_modality"})
        print(f"V81 preflight {entry['run_id']}: {record['status']}", flush=True)

    expected_ids = {f"{mode}_seed{seed}" for mode in INPUT_CHANNELS for seed in (0, 1, 2)}
    complete = len(records) == 9 and seen == expected_ids and all(item["status"] == "PASS" for item in records)
    payload = {
        "status": "PASS" if complete else "FAIL",
        "task": "V83_POST_V81_WEIGHT_EVIDENCE",
        "registry": str(V81_REGISTRY.relative_to(PROJECT_ROOT)),
        "expected_count": 9,
        "verified_count": sum(item["status"] == "PASS" for item in records),
        "expected_split_sha256": EXPECTED_SPLIT_SHA256,
        "records": records,
        "downstream_authorized": complete,
        "holdout_accessed": False,
    }
    write_json(out_dir / "weight_preflight.json", payload)
    if not complete:
        raise RuntimeError(f"V83 V81 identity preflight failed; see {out_dir / 'weight_preflight.json'}")
    return benchmark_entries


def fusion_preflight(out_dir: Path) -> list[dict]:
    registry = json.loads(V48_REGISTRY.read_text(encoding="utf-8"))
    candidates = [row for row in registry["per_run"] if row.get("variant") in FUSION_VARIANTS]
    records = []
    accepted = []
    for entry in candidates:
        path = resolve(entry["weights"])
        checks = {"exists": path.is_file()}
        actual_hash = sha256(path) if path.is_file() else None
        checks["sha256"] = actual_hash == entry["checkpoint_sha256"]
        checkpoint = torch.load(path, map_location="cpu", weights_only=False) if all(checks.values()) else None
        cfg = checkpoint.get("model_cfg", {}) if checkpoint else {}
        train_args = checkpoint.get("train_args", {}) if checkpoint else {}
        expected_model = FUSION_VARIANTS[entry["variant"]]
        checks.update(
            model_type=cfg.get("model_type") == expected_model,
            input_channels=cfg.get("in_chans") == 5,
            image_size=cfg.get("img_size") == 640,
            seed=train_args.get("seed") == entry["seed"],
            selected_epoch=checkpoint is not None and checkpoint.get("epoch") == entry["selected_epoch"],
            model_state_present=checkpoint is not None and isinstance(checkpoint.get("model_state"), dict),
        )
        status = "PASS" if all(checks.values()) else "EXCLUDED"
        records.append(
            {
                "run_id": entry["run_id"],
                "variant": entry["variant"],
                "model_type": expected_model,
                "seed": entry["seed"],
                "checkpoint": str(path),
                "expected_sha256": entry["checkpoint_sha256"],
                "actual_sha256": actual_hash,
                "checks": checks,
                "status": status,
            }
        )
        if status == "PASS":
            accepted.append(
                {
                    "run_id": entry["run_id"],
                    "variant": entry["variant"],
                    "model_type": expected_model,
                    "seed": entry["seed"],
                    "checkpoint": str(path),
                    "checkpoint_sha256": actual_hash,
                    "family": "multimodal_fusion",
                }
            )
        print(f"fusion preflight {entry['run_id']}: {status}", flush=True)
    write_json(
        out_dir / "fusion_weight_preflight.json",
        {
            "status": "PASS" if len(accepted) == 6 else "PARTIAL_OR_UNAVAILABLE",
            "source_registry": str(V48_REGISTRY.relative_to(PROJECT_ROOT)),
            "candidate_count": len(candidates),
            "verified_count": len(accepted),
            "records": records,
            "holdout_accessed": False,
        },
    )
    return accepted


def build_model(entry: dict, device: torch.device) -> tuple[torch.nn.Module, int]:
    checkpoint = torch.load(entry["checkpoint"], map_location="cpu", weights_only=False)
    cfg = checkpoint["model_cfg"]
    if entry["family"] == "single_modality":
        mode = entry["input_mode"]
        model = build_v76_single_modality_detector(
            mode,
            model_name=cfg["model_name"],
            img_size=640,
            num_classes=cfg["num_classes"],
            fpn_out_channels=cfg["fpn_out_channels"],
            score_thresh=0.2,
            nms_thresh=0.6,
            detections_per_img=100,
        )
        channels = INPUT_CHANNELS[mode]
    else:
        model = build_detector(
            model_type=entry["model_type"],
            model_name=cfg["model_name"],
            img_size=640,
            num_classes=cfg["num_classes"],
            fpn_out_channels=cfg["fpn_out_channels"],
            score_thresh=0.2,
            nms_thresh=0.6,
            detections_per_img=100,
        )
        channels = 5
    model.load_state_dict(checkpoint["model_state"], strict=True)
    return model.to(device).eval(), channels


def operator_flops(model: torch.nn.Module, inputs: list[torch.Tensor], device: torch.device) -> int:
    activities = [torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA]
    torch.cuda.synchronize(device)
    with torch.inference_mode(), torch.profiler.profile(activities=activities, with_flops=True) as profiler:
        model(inputs)
        torch.cuda.synchronize(device)
    return sum(int(event.flops) for event in profiler.key_averages())


def measure(model, inputs, device, warmup: int, iterations: int) -> dict:
    with torch.inference_mode():
        for _ in range(warmup):
            model(inputs)
        torch.cuda.synchronize(device)
        torch.cuda.reset_peak_memory_stats(device)
        latencies = []
        for _ in range(iterations):
            torch.cuda.synchronize(device)
            started = time.perf_counter()
            model(inputs)
            torch.cuda.synchronize(device)
            latencies.append((time.perf_counter() - started) * 1000.0)
    mean_ms = statistics.mean(latencies)
    return {
        "mean_latency_ms": mean_ms,
        "median_latency_ms": statistics.median(latencies),
        "p95_latency_ms": percentile(latencies, 0.95),
        "throughput_fps": 1000.0 / mean_ms,
        "peak_allocated_memory_mib": torch.cuda.max_memory_allocated(device) / (1024**2),
        "peak_reserved_memory_mib": torch.cuda.max_memory_reserved(device) / (1024**2),
    }


def nvidia_environment() -> dict:
    command = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total",
        "--format=csv,noheader,nounits",
    ]
    try:
        name, driver, memory = [part.strip() for part in subprocess.check_output(command, text=True).splitlines()[0].split(",")]
        return {"gpu_name": name, "driver_version": driver, "gpu_memory_mib": int(memory)}
    except (OSError, subprocess.SubprocessError, ValueError):
        return {"gpu_name": torch.cuda.get_device_name(0), "driver_version": None, "gpu_memory_mib": None}


def group_summary(rows: list[dict]) -> list[dict]:
    summaries = []
    group_names = sorted({row["group"] for row in rows})
    metrics = (
        "mean_latency_ms",
        "median_latency_ms",
        "p95_latency_ms",
        "throughput_fps",
        "peak_allocated_memory_mib",
        "peak_reserved_memory_mib",
    )
    for group in group_names:
        selected = [row for row in rows if row["group"] == group]
        item = {"group": group, "count": len(selected), "seeds": [row["seed"] for row in selected]}
        for metric in metrics:
            values = [float(row[metric]) for row in selected]
            item[f"{metric}_mean"] = statistics.mean(values)
            item[f"{metric}_sample_std"] = statistics.stdev(values) if len(values) > 1 else 0.0
        item["total_params"] = selected[0]["total_params"]
        item["operator_flops"] = selected[0]["operator_flops"]
        item["derived_macs"] = selected[0]["derived_macs"]
        summaries.append(item)
    return summaries


def write_markdown(path: Path, payload: dict) -> None:
    lines = [
        "# V83 Post-V81 Efficiency Summary",
        "",
        f"Status: `{payload['status']}`",
        "",
        "Synthetic label-free full-detector inference; RTX 3090; batch 1; 640x640; FP32; 50 warm-up and 200 measured iterations; CUDA synchronized around every timed inference.",
        "",
        "| Group | N | Params | FLOPs | Mean ms (mean +/- SD) | Median ms | P95 ms | FPS | Peak allocated MiB | Peak reserved MiB |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["group_summary"]:
        lines.append(
            f"| {row['group']} | {row['count']} | {row['total_params']} | {row['operator_flops']} | "
            f"{row['mean_latency_ms_mean']:.4f} +/- {row['mean_latency_ms_sample_std']:.4f} | "
            f"{row['median_latency_ms_mean']:.4f} | {row['p95_latency_ms_mean']:.4f} | "
            f"{row['throughput_fps_mean']:.4f} | {row['peak_allocated_memory_mib_mean']:.2f} | "
            f"{row['peak_reserved_memory_mib_mean']:.2f} |"
        )
    lines.extend(
        [
            "",
            "FLOPs are the sum reported by `torch.profiler` for one full detector call; derived MACs are FLOPs/2 and inherit profiler operator-coverage limitations.",
            "Runtime variation across seeds is an execution repeat, not statistical accuracy evidence. No dataset, validation labels, or locked holdout were accessed.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--warmup", type=int, default=50)
    parser.add_argument("--iterations", type=int, default=200)
    parser.add_argument("--preflight-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.warmup < 50 or args.iterations < 200:
        raise ValueError("V83 requires at least 50 warm-up and 200 measured iterations")
    out_dir = resolve(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    single_entries = v81_preflight(out_dir)
    fusion_entries = fusion_preflight(out_dir)
    if args.preflight_only:
        print("V83 preflight complete", flush=True)
        return

    device = torch.device(args.device)
    if device.type != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("V83 primary efficiency benchmark requires CUDA")
    if torch.cuda.get_device_name(0) != "NVIDIA GeForce RTX 3090":
        raise RuntimeError(f"V83 requires NVIDIA GeForce RTX 3090, found {torch.cuda.get_device_name(0)}")
    torch.set_grad_enabled(False)
    rows = []
    entries = single_entries + fusion_entries
    for index, entry in enumerate(entries, start=1):
        torch.manual_seed(8300 + index)
        torch.cuda.manual_seed_all(8300 + index)
        model, channels = build_model(entry, device)
        inputs = [torch.randn(channels, 640, 640, device=device, dtype=torch.float32)]
        total_params = sum(parameter.numel() for parameter in model.parameters())
        trainable_params = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
        flops = operator_flops(model, inputs, device)
        timing = measure(model, inputs, device, args.warmup, args.iterations)
        group = entry.get("input_mode", entry.get("variant"))
        row = {
            "run_id": entry["run_id"],
            "family": entry["family"],
            "group": group,
            "seed": entry["seed"],
            "input_channels": channels,
            "input_shape": f"1x{channels}x640x640",
            "precision": "float32",
            "total_params": total_params,
            "trainable_params": trainable_params,
            "operator_flops": flops,
            "derived_macs": flops / 2.0,
            **timing,
            "checkpoint": entry["checkpoint"],
            "checkpoint_sha256": entry["checkpoint_sha256"],
            "warmup_iterations": args.warmup,
            "measured_iterations": args.iterations,
        }
        rows.append(row)
        print(
            f"benchmark {index}/{len(entries)} {entry['run_id']}: "
            f"{row['mean_latency_ms']:.4f} ms, {row['throughput_fps']:.2f} FPS",
            flush=True,
        )
        del model, inputs
        torch.cuda.empty_cache()

    git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()
    environment = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "pytorch": torch.__version__,
        "torchvision": torchvision.__version__,
        "cuda_runtime": str(torch.version.cuda),
        "cudnn": torch.backends.cudnn.version(),
        "device": str(device),
        **nvidia_environment(),
        "git_commit": git_commit,
    }
    payload = {
        "status": "V83_WEIGHT_PREFLIGHT_AND_EFFICIENCY_COMPLETE",
        "procedure": {
            "input_size": [640, 640],
            "batch_size": 1,
            "precision": "FP32",
            "amp": False,
            "tensorrt": False,
            "torch_compile": False,
            "warmup_iterations": args.warmup,
            "measured_iterations": args.iterations,
            "synchronization": "CUDA synchronization before and after every measured full-detector call",
            "dataloader_time_included": False,
            "synthetic_inputs": True,
            "score_threshold": 0.2,
            "nms_threshold": 0.6,
            "detections_per_image": 100,
            "flop_backend": "torch.profiler with_flops=True; full detector call",
        },
        "environment": environment,
        "checkpoint_count": len(rows),
        "single_modality_count": len(single_entries),
        "fusion_count": len(fusion_entries),
        "per_run": rows,
        "group_summary": group_summary(rows),
        "holdout_accessed": False,
        "training_performed": False,
    }
    efficiency_dir = out_dir / "efficiency"
    write_json(efficiency_dir / "runtime_environment.json", environment)
    write_csv(efficiency_dir / "per_run.csv", rows)
    write_json(efficiency_dir / "summary.json", payload)
    write_markdown(efficiency_dir / "summary.md", payload)
    write_json(
        out_dir / "final_decision.json",
        {
            "status": payload["status"],
            "v81_preflight": "9/9 PASS",
            "single_modality_benchmarks": len(single_entries),
            "verified_fusion_benchmarks": len(fusion_entries),
            "holdout_accessed": False,
            "manuscript_changed": False,
            "next_gate": "Review efficiency evidence before any V82 manuscript revision",
        },
    )


if __name__ == "__main__":
    main()
