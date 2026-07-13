#!/usr/bin/env python
"""Reproducible full-detector efficiency profiling for V48 fusion variants."""

import argparse
import csv
from datetime import datetime
import hashlib
import json
from math import ceil
from pathlib import Path
import platform
import statistics
import sys
import time

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.models.early_fusion_fcos import build_detector


DEFAULT_WEIGHTS = {
    "early": "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt",
    "reliability": "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt",
}


def resolve(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(values, fraction):
    if not values:
        return None
    return sorted(values)[max(0, ceil(len(values) * fraction) - 1)]


def count_params(model):
    return (
        sum(parameter.numel() for parameter in model.parameters()),
        sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad),
    )


def load_model(model_type, img_size, score_threshold, device, weights_override=None):
    weights_path = resolve(weights_override or DEFAULT_WEIGHTS.get(model_type, "")) if (weights_override or DEFAULT_WEIGHTS.get(model_type)) else None
    model_kwargs = {
        "model_type": model_type,
        "img_size": img_size,
        "score_thresh": score_threshold,
        "nms_thresh": 0.6,
        "detections_per_img": 100,
    }
    checkpoint_hash = "NA"
    if weights_path is not None:
        if not weights_path.is_file():
            raise FileNotFoundError(weights_path)
        checkpoint = torch.load(weights_path, map_location="cpu", weights_only=False)
        cfg = checkpoint.get("model_cfg", {})
        checkpoint_type = cfg.get("model_type", model_type)
        if checkpoint_type != model_type:
            raise RuntimeError(f"checkpoint model type {checkpoint_type} does not match requested {model_type}")
        model_kwargs.update(
            model_name=cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
            num_classes=cfg.get("num_classes", 2),
            fpn_out_channels=cfg.get("fpn_out_channels", 128),
        )
        model = build_detector(**model_kwargs)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        checkpoint_hash = sha256(weights_path)
    else:
        model = build_detector(**model_kwargs)
    return model.to(device).eval(), weights_path, checkpoint_hash


def operator_flops(model, detector_inputs, device):
    activities = [torch.profiler.ProfilerActivity.CPU]
    if device.type == "cuda":
        activities.append(torch.profiler.ProfilerActivity.CUDA)
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    with torch.no_grad(), torch.profiler.profile(activities=activities, with_flops=True) as profiler:
        _ = model(detector_inputs)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
    return sum(int(event.flops) for event in profiler.key_averages())


def latency_and_memory(model, detector_inputs, device, warmup, iterations):
    with torch.no_grad():
        for _ in range(warmup):
            _ = model(detector_inputs)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
            torch.cuda.reset_peak_memory_stats(device)

        latencies = []
        for _ in range(iterations):
            if device.type == "cuda":
                torch.cuda.synchronize(device)
            start = time.perf_counter()
            _ = model(detector_inputs)
            if device.type == "cuda":
                torch.cuda.synchronize(device)
            latencies.append((time.perf_counter() - start) * 1000.0)

    peak_memory_mib = (
        torch.cuda.max_memory_allocated(device) / (1024 ** 2) if device.type == "cuda" else None
    )
    mean_ms = statistics.mean(latencies)
    return {
        "mean_latency_ms": mean_ms,
        "median_latency_ms": statistics.median(latencies),
        "p95_latency_ms": percentile(latencies, 0.95),
        "throughput_fps": len(detector_inputs) * 1000.0 / mean_ms,
        "peak_allocated_memory_mib": peak_memory_mib,
    }


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)


def value(item):
    return "NA" if item is None else str(item)


def write_markdown(path, profile):
    procedure = profile["procedure"]
    lines = [
        "# V48 Efficiency Summary",
        "",
        f"Generated: {profile['generated_at']}",
        "",
        "## Procedure",
        "",
        "- Full FCOS detector inference was measured without dataloader or file-I/O time.",
        f"- Input: `{procedure['batch_size']}x5x{procedure['img_size']}x{procedure['img_size']}`, `{procedure['precision_mode']}`.",
        f"- Warm-up iterations: `{procedure['warmup_iterations']}`; measured iterations: `{procedure['measured_iterations']}`.",
        "- Each measured iteration is bracketed by CUDA synchronization when CUDA is used; latency is host wall time for the complete detector call.",
        "- Operator FLOPs are summed from `torch.profiler` events for one full-detector inference. Derived MACs equal FLOPs/2 and exclude operations with no profiler FLOP estimate.",
        "",
        "## Results",
        "",
        "| Model | Total params | Trainable params | Operator FLOPs | Derived MACs | Mean ms | Median ms | P95 ms | FPS | Peak allocated MiB | Checkpoint |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in profile["models"]:
        display_row = {
            **row,
            "memory": value(row["peak_allocated_memory_mib"]),
            "display_checkpoint": row["checkpoint"] or "random initialization",
        }
        lines.append(
            "| {model_type} | {total_params} | {trainable_params} | {operator_flops} | {derived_macs} | "
            "{mean_latency_ms:.4f} | {median_latency_ms:.4f} | {p95_latency_ms:.4f} | {throughput_fps:.4f} | {memory} | `{display_checkpoint}` |".format(**display_row)
        )
    lines.extend(["", "## Hardware", ""])
    lines.extend(f"- {key}: `{value}`" for key, value in profile["environment"].items())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", default="early,reliability")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--batch-size", default=1, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--warmup", default=10, type=int)
    parser.add_argument("--iterations", default=30, type=int)
    parser.add_argument("--score-threshold", default=0.50, type=float)
    parser.add_argument("--out-dir", default="runs/v48_complete_ablation")
    args = parser.parse_args()
    if args.batch_size <= 0 or args.img_size <= 0 or args.iterations <= 0 or args.warmup < 0:
        raise SystemExit("img-size, batch-size, and iterations must be positive; warmup must be non-negative")

    requested_device = torch.device(args.device)
    if requested_device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA profiling was requested but CUDA is unavailable")
    torch.manual_seed(48)
    if requested_device.type == "cuda":
        torch.cuda.manual_seed_all(48)

    model_types = [item.strip() for item in args.models.split(",") if item.strip()]
    allowed = {"early", "reliability", "ra_static_equal", "ra_stems_project"}
    unknown = set(model_types) - allowed
    if unknown:
        raise ValueError(f"unknown models: {sorted(unknown)}")
    input_tensor = torch.randn(args.batch_size, 5, args.img_size, args.img_size, device=requested_device)
    detector_inputs = [input_tensor[index] for index in range(args.batch_size)]
    rows = []
    for model_type in model_types:
        model, checkpoint, checkpoint_hash = load_model(
            model_type,
            args.img_size,
            args.score_threshold,
            requested_device,
        )
        total_params, trainable_params = count_params(model)
        flops = operator_flops(model, detector_inputs, requested_device)
        timing = latency_and_memory(model, detector_inputs, requested_device, args.warmup, args.iterations)
        row = {
            "model_type": model_type,
            "total_params": total_params,
            "trainable_params": trainable_params,
            "operator_flops": flops,
            "derived_macs": flops / 2.0,
            **timing,
            "checkpoint": str(checkpoint.relative_to(PROJECT_ROOT)) if checkpoint else "",
            "checkpoint_sha256": checkpoint_hash,
            "input_shape": f"{args.batch_size}x5x{args.img_size}x{args.img_size}",
            "precision_mode": "float32",
        }
        rows.append(row)
        print(json.dumps({key: row[key] for key in ("model_type", "operator_flops", "mean_latency_ms", "throughput_fps")}, indent=2))
        del model
        if requested_device.type == "cuda":
            torch.cuda.empty_cache()

    environment = {
        "platform": platform.platform(),
        "pytorch": torch.__version__,
        "cuda": str(torch.version.cuda),
        "device": str(requested_device),
        "gpu": torch.cuda.get_device_name(0) if requested_device.type == "cuda" else "CPU",
    }
    profile = {
        "status": "V48_EFFICIENCY_PROFILE_COMPLETE",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "procedure": {
            "batch_size": args.batch_size,
            "img_size": args.img_size,
            "precision_mode": "float32",
            "warmup_iterations": args.warmup,
            "measured_iterations": args.iterations,
            "synchronization": "before and after each measured full-detector inference when CUDA is used",
            "flop_convention": "sum of torch.profiler full-detector operator FLOPs; derived MACs=FLOPs/2",
            "dataloader_time_included": False,
        },
        "environment": environment,
        "models": rows,
    }
    out_dir = resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "efficiency_per_model.csv", rows)
    (out_dir / "efficiency_summary.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    write_markdown(out_dir / "efficiency_summary.md", profile)


if __name__ == "__main__":
    main()
