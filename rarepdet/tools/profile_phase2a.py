#!/usr/bin/env python
"""Repeated Phase 2A profiling for raw backbone forward and detector inference."""

import argparse
import csv
from pathlib import Path
import statistics
import sys
import time

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.models.early_fusion_fcos import build_detector
from phase2a_common import pick_device, resolve_path


def count_params(model):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def load_model(args, device):
    checkpoint = torch.load(resolve_path(args.weights), map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type=args.model,
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", args.img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        score_thresh=args.score_thr,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device).eval()
    return model


def measure_callable(fn, images, device, warmup, iters):
    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)
    with torch.no_grad():
        for _ in range(warmup):
            _ = fn()
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        start = time.perf_counter()
        for _ in range(iters):
            _ = fn()
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        elapsed = time.perf_counter() - start
    fps = images * iters / max(elapsed, 1e-9)
    latency = elapsed * 1000.0 / max(images * iters, 1)
    memory = torch.cuda.max_memory_allocated(device) / (1024 ** 2) if device.type == "cuda" else 0.0
    return fps, latency, memory


def summarize(values):
    if not values:
        return "NA"
    if len(values) == 1:
        return f"{values[0]:.6f}"
    return f"{statistics.mean(values):.6f}"


def summarize_std(values):
    if not values:
        return "NA"
    if len(values) == 1:
        return "0.000000"
    return f"{statistics.pstdev(values):.6f}"


def write_outputs(rows, summary_rows, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "profile_raw_runs.csv"
    summary_path = out_dir / "profile_results.csv"
    txt_path = out_dir / "profile_results.txt"

    raw_fields = list(rows[0].keys()) if rows else []
    with raw_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=raw_fields)
        writer.writeheader()
        writer.writerows(rows)

    summary_fields = list(summary_rows[0].keys()) if summary_rows else []
    with summary_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary_rows)

    with txt_path.open("w", encoding="utf-8") as f:
        f.write("Phase 2A profile results\n")
        f.write("========================\n\n")
        for row in summary_rows:
            f.write(
                f"{row['Model']} {row['Path']}: FPS={row['FPS mean']} +/- {row['FPS std']}, "
                f"Latency={row['Latency ms/img mean']} ms, CUDA memory={row['CUDA Memory MB mean']} MB\n"
            )

    return raw_path, summary_path, txt_path


def main():
    parser = argparse.ArgumentParser(description="Repeated Phase 2A profiling.")
    parser.add_argument("--model", choices=("early", "reliability"), required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=1, type=int)
    parser.add_argument("--warmup", default=100, type=int)
    parser.add_argument("--iters", default=300, type=int)
    parser.add_argument("--repeats", default=3, type=int)
    parser.add_argument("--score-thr", default=0.50, type=float)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    device = pick_device(args.device)
    model = load_model(args, device)
    params, trainable = count_params(model)
    dummy = torch.randn(args.batch_size, 5, args.img_size, args.img_size, device=device)
    detector_inputs = [dummy[i] for i in range(dummy.shape[0])]

    rows = []
    for repeat in range(1, args.repeats + 1):
        raw_fps, raw_latency, raw_memory = measure_callable(
            lambda: model.backbone(dummy),
            args.batch_size,
            device,
            args.warmup,
            args.iters,
        )
        det_fps, det_latency, det_memory = measure_callable(
            lambda: model(detector_inputs),
            args.batch_size,
            device,
            args.warmup,
            args.iters,
        )
        rows.extend(
            [
                {
                    "Model": args.model,
                    "Path": "raw_forward",
                    "Repeat": repeat,
                    "Batch Size": args.batch_size,
                    "Img Size": args.img_size,
                    "Warmup": args.warmup,
                    "Iters": args.iters,
                    "Params": params,
                    "Trainable Params": trainable,
                    "FPS": f"{raw_fps:.6f}",
                    "Latency ms/img": f"{raw_latency:.6f}",
                    "CUDA Memory MB": f"{raw_memory:.2f}",
                },
                {
                    "Model": args.model,
                    "Path": "detector_inference",
                    "Repeat": repeat,
                    "Batch Size": args.batch_size,
                    "Img Size": args.img_size,
                    "Warmup": args.warmup,
                    "Iters": args.iters,
                    "Params": params,
                    "Trainable Params": trainable,
                    "FPS": f"{det_fps:.6f}",
                    "Latency ms/img": f"{det_latency:.6f}",
                    "CUDA Memory MB": f"{det_memory:.2f}",
                },
            ]
        )
        print(
            f"repeat {repeat}/{args.repeats}: raw_fps={raw_fps:.3f}, "
            f"detector_fps={det_fps:.3f}"
        )

    summary_rows = []
    for path_name in ("raw_forward", "detector_inference"):
        part = [row for row in rows if row["Path"] == path_name]
        fps_values = [float(row["FPS"]) for row in part]
        latency_values = [float(row["Latency ms/img"]) for row in part]
        memory_values = [float(row["CUDA Memory MB"]) for row in part]
        summary_rows.append(
            {
                "Model": args.model,
                "Path": path_name,
                "Batch Size": args.batch_size,
                "Img Size": args.img_size,
                "Warmup": args.warmup,
                "Iters": args.iters,
                "Repeats": args.repeats,
                "Params": params,
                "Trainable Params": trainable,
                "FPS mean": summarize(fps_values),
                "FPS std": summarize_std(fps_values),
                "Latency ms/img mean": summarize(latency_values),
                "Latency ms/img std": summarize_std(latency_values),
                "CUDA Memory MB mean": summarize(memory_values),
                "CUDA Memory MB std": summarize_std(memory_values),
            }
        )

    paths = write_outputs(rows, summary_rows, resolve_path(args.out))
    for path in paths:
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()

