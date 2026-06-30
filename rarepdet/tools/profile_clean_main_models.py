#!/usr/bin/env python
"""Unified current-code efficiency profile for clean-split R0 and R4 models."""

import argparse
import csv
from datetime import datetime
from pathlib import Path
import statistics
import sys
import time

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.models.early_fusion_fcos import build_detector


RUNS = [
    {
        "label": "R0 Early Fusion",
        "model": "early",
        "weights": "runs/R0_early_seed0_block64g16_e50/weights/best.pt",
        "compare_weights": None,
        "note": "seed0 checkpoint",
    },
    {
        "label": "R4 Reliability p=0.20",
        "model": "reliability",
        "weights": "runs/R4_reliability_p020_seed0_block64g16_e50/weights/best.pt",
        "compare_weights": "runs/R4_reliability_p020_seed2_block64g16_e50/weights/best.pt",
        "note": "seed0 checkpoint; dropout is training-only",
    },
]


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def pick_device(requested):
    device = torch.device(requested)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        return torch.device("cpu")
    return device


def count_params(model):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def load_model(run, img_size, score_thr, device):
    weights = resolve_path(run["weights"])
    if not weights.is_file():
        raise FileNotFoundError(f"Weights not found: {weights}")
    checkpoint = torch.load(weights, map_location=device)
    cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type=run["model"],
        model_name=cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=cfg.get("img_size", img_size),
        num_classes=cfg.get("num_classes", 2),
        fpn_out_channels=cfg.get("fpn_out_channels", 128),
        score_thresh=score_thr,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device).eval()
    return model


def param_count_from_checkpoint(run, img_size, score_thr, device):
    model = load_model(run, img_size, score_thr, device)
    params, trainable = count_params(model)
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return params, trainable


def measure(fn, images, device, warmup, iters):
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


def mean(values):
    return statistics.mean(values) if values else 0.0


def pstdev(values):
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def summarize(raw_rows):
    summary = []
    for label in sorted({row["Model"] for row in raw_rows}):
        for path_name in ("raw_forward", "detector_inference"):
            rows = [row for row in raw_rows if row["Model"] == label and row["Path"] == path_name]
            fps = [float(row["FPS"]) for row in rows]
            latency = [float(row["Latency ms/img"]) for row in rows]
            memory = [float(row["CUDA Memory MB"]) for row in rows]
            first = rows[0]
            summary.append(
                {
                    "Model": label,
                    "Path": path_name,
                    "Batch Size": first["Batch Size"],
                    "Img Size": first["Img Size"],
                    "Warmup": first["Warmup"],
                    "Iters": first["Iters"],
                    "Repeats": first["Repeats"],
                    "Params": first["Params"],
                    "Trainable Params": first["Trainable Params"],
                    "FPS mean": f"{mean(fps):.6f}",
                    "FPS std": f"{pstdev(fps):.6f}",
                    "Latency ms/img mean": f"{mean(latency):.6f}",
                    "Latency ms/img std": f"{pstdev(latency):.6f}",
                    "CUDA Memory MB mean": f"{mean(memory):.6f}",
                    "CUDA Memory MB std": f"{pstdev(memory):.6f}",
                    "Note": first["Note"],
                }
            )
    return summary


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def md_table(rows):
    headers = list(rows[0].keys()) if rows else []
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "NA")) for header in headers) + " |")
    return lines


def write_md(path, rows, device):
    lines = [
        "# Clean Main-Model Efficiency Profile",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Device: `{device}`",
        "",
        "Protocol: batch 1, input `5x640x640`, 100 warm-up iterations, 300 timed iterations, 3 repeats. Dataloader and file IO are excluded.",
        "",
        "R4 seed-0 and seed-2 checkpoints are checked for identical parameter counts; the seed-0 checkpoint is benchmarked because modality dropout is training-only.",
        "",
    ]
    lines.extend(md_table(rows))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Profile clean-split main models.")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=1, type=int)
    parser.add_argument("--warmup", default=100, type=int)
    parser.add_argument("--iters", default=300, type=int)
    parser.add_argument("--repeats", default=3, type=int)
    parser.add_argument("--score-thr", default=0.50, type=float)
    parser.add_argument("--out-dir", default="runs")
    args = parser.parse_args()

    device = pick_device(args.device)
    raw_rows = []
    for run in RUNS:
        model = load_model(run, args.img_size, args.score_thr, device)
        params, trainable = count_params(model)
        if run["compare_weights"]:
            compare_run = {**run, "weights": run["compare_weights"]}
            compare_params, compare_trainable = param_count_from_checkpoint(compare_run, args.img_size, args.score_thr, device)
            if (params, trainable) != (compare_params, compare_trainable):
                raise RuntimeError(
                    f"Parameter count mismatch for {run['label']}: "
                    f"seed0=({params},{trainable}) seed2=({compare_params},{compare_trainable})"
                )
        dummy = torch.randn(args.batch_size, 5, args.img_size, args.img_size, device=device)
        detector_inputs = [dummy[i] for i in range(dummy.shape[0])]
        for repeat in range(1, args.repeats + 1):
            raw_fps, raw_latency, raw_memory = measure(
                lambda: model.backbone(dummy),
                args.batch_size,
                device,
                args.warmup,
                args.iters,
            )
            det_fps, det_latency, det_memory = measure(
                lambda: model(detector_inputs),
                args.batch_size,
                device,
                args.warmup,
                args.iters,
            )
            print(f"{run['label']} repeat {repeat}/{args.repeats}: raw_fps={raw_fps:.3f}, det_fps={det_fps:.3f}")
            for path_name, fps, latency, memory in (
                ("raw_forward", raw_fps, raw_latency, raw_memory),
                ("detector_inference", det_fps, det_latency, det_memory),
            ):
                raw_rows.append(
                    {
                        "Model": run["label"],
                        "Path": path_name,
                        "Repeat": repeat,
                        "Batch Size": args.batch_size,
                        "Img Size": args.img_size,
                        "Warmup": args.warmup,
                        "Iters": args.iters,
                        "Repeats": args.repeats,
                        "Params": params,
                        "Trainable Params": trainable,
                        "FPS": f"{fps:.6f}",
                        "Latency ms/img": f"{latency:.6f}",
                        "CUDA Memory MB": f"{memory:.2f}",
                        "Note": run["note"],
                    }
                )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    summary_rows = summarize(raw_rows)
    out_dir = resolve_path(args.out_dir)
    write_csv(out_dir / "clean_efficiency_profile_raw_runs.csv", raw_rows)
    write_csv(out_dir / "clean_efficiency_profile.csv", summary_rows)
    write_md(out_dir / "clean_efficiency_profile.md", summary_rows, device)
    print(f"Saved: {out_dir / 'clean_efficiency_profile.csv'}")
    print(f"Saved: {out_dir / 'clean_efficiency_profile.md'}")


if __name__ == "__main__":
    main()
