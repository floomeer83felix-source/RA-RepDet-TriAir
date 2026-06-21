#!/usr/bin/env python
"""Profile RarePDet model params, optional GFLOPs, FPS, latency, and memory."""

import argparse
import csv
from pathlib import Path
import sys
import time

import torch
from torch import nn


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.models.early_fusion_fcos import build_detector


class DetectorTensorWrapper(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):
        outputs = self.model([x[i] for i in range(x.shape[0])])
        if not outputs:
            return x.new_zeros(())
        scores = [output.get("scores", x.new_zeros((0,))).sum() for output in outputs]
        return torch.stack(scores).sum()


def resolve_out(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def count_params(model):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def try_thop(model, dummy):
    try:
        from thop import profile
    except Exception as exc:
        return None, f"thop unavailable: {exc}"

    try:
        wrapper = DetectorTensorWrapper(model).eval()
        macs, _ = profile(wrapper, inputs=(dummy,), verbose=False)
        return float(macs) * 2.0 / 1e9, "detector"
    except Exception as detector_exc:
        try:
            macs, _ = profile(model.backbone.eval(), inputs=(dummy,), verbose=False)
            return float(macs) * 2.0 / 1e9, f"backbone_fpn_only; detector profile failed: {detector_exc}"
        except Exception as backbone_exc:
            return None, f"thop failed: detector={detector_exc}; backbone={backbone_exc}"


def profile_fps(model, dummy, device, warmup, iters):
    model.eval()
    inputs = [dummy[i] for i in range(dummy.shape[0])]
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    with torch.no_grad():
        for _ in range(warmup):
            _ = model(inputs)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        start = time.perf_counter()
        for _ in range(iters):
            _ = model(inputs)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        elapsed = time.perf_counter() - start

    images = dummy.shape[0] * iters
    fps = images / max(elapsed, 1e-9)
    latency = elapsed * 1000.0 / max(images, 1)
    memory_mb = torch.cuda.max_memory_allocated(device) / (1024 ** 2) if device.type == "cuda" else 0.0
    return fps, latency, memory_mb


def write_results(out_dir, row):
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / "profile_results.txt"
    csv_path = out_dir / "profile_results.csv"
    with txt_path.open("w", encoding="utf-8") as f:
        for key, value in row.items():
            f.write(f"{key}: {value}\n")
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)
    return txt_path, csv_path


def main():
    parser = argparse.ArgumentParser(description="Profile RarePDet model complexity.")
    parser.add_argument("--model", default="early", choices=("early", "reliability"))
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=1, type=int)
    parser.add_argument("--warmup", default=50, type=int)
    parser.add_argument("--iters", default=200, type=int)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        device = torch.device("cpu")

    model = build_detector(model_type=args.model, img_size=args.img_size).to(device).eval()
    dummy = torch.randn(args.batch_size, 5, args.img_size, args.img_size, device=device)
    params, trainable = count_params(model)
    gflops, gflops_note = try_thop(model, dummy)
    fps, latency, memory_mb = profile_fps(model, dummy, device, args.warmup, args.iters)

    row = {
        "Model": args.model,
        "Img Size": args.img_size,
        "Batch Size": args.batch_size,
        "Params": params,
        "Trainable Params": trainable,
        "GFLOPs": "NA" if gflops is None else f"{gflops:.6f}",
        "GFLOPs Note": gflops_note,
        "FPS": f"{fps:.6f}",
        "Latency ms/img": f"{latency:.6f}",
        "CUDA max memory MB": f"{memory_mb:.2f}",
    }
    txt_path, csv_path = write_results(resolve_out(args.out), row)
    print(f"Saved: {txt_path}")
    print(f"Saved: {csv_path}")
    print(row)


if __name__ == "__main__":
    main()
