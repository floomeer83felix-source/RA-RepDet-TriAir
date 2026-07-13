#!/usr/bin/env python
"""Evaluate a frozen fusion checkpoint or V50 RGB checkpoint."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.visdrone_seen_dataset import VisDroneSeenVehicleDataset, collate_fn
from rarepdet.models.early_fusion_fcos import build_detector
from rarepdet.models.rgb_fcos import build_rgb_fcos
from rarepdet.v50_coco import evaluate_detections, outputs_to_detections


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_version(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "NA"


def environment(device):
    return {
        "python": platform.python_version(),
        "pytorch": torch.__version__,
        "torchvision": package_version("torchvision"),
        "timm": package_version("timm"),
        "pycocotools": package_version("pycocotools"),
        "torch_cuda": str(torch.version.cuda),
        "cuda_available": torch.cuda.is_available(),
        "device": str(device),
        "gpu": torch.cuda.get_device_name(0) if device.type == "cuda" else "NA",
    }


def evaluate(args):
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")

    weights = resolve_path(args.weights)
    manifest = resolve_path(args.manifest)
    annotations = resolve_path(args.annotations)
    checkpoint = torch.load(weights, map_location="cpu", weights_only=False)
    model_cfg = checkpoint.get("model_cfg", {})
    train_args = checkpoint.get("train_args", {})

    if args.model == "rgb":
        model = build_rgb_fcos(
            model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
            img_size=model_cfg.get("img_size", args.img_size),
            num_classes=model_cfg.get("num_classes", 2),
            fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
            score_thresh=args.detector_score_thr,
            nms_thresh=args.nms_thresh,
            detections_per_img=args.detections_per_img,
        )
        five_channel = False
    else:
        model = build_detector(
            model_type=args.model,
            model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
            img_size=model_cfg.get("img_size", args.img_size),
            num_classes=model_cfg.get("num_classes", 2),
            fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
            score_thresh=args.detector_score_thr,
            nms_thresh=args.nms_thresh,
            detections_per_img=args.detections_per_img,
        )
        five_channel = True

    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device).eval()
    dataset = VisDroneSeenVehicleDataset(
        args.data, manifest, annotations, five_channel=five_channel
    )
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=device.type == "cuda",
    )

    detections = []
    start = time.time()
    with torch.no_grad():
        for batch_index, (images, targets) in enumerate(loader, 1):
            outputs = model([image.to(device, non_blocking=True) for image in images])
            detections.extend(
                outputs_to_detections(
                    outputs,
                    targets,
                    score_threshold=args.detector_score_thr,
                    max_detections=args.detections_per_img,
                )
            )
            if batch_index == 1 or batch_index % 100 == 0 or batch_index == len(loader):
                print(f"inference batch {batch_index}/{len(loader)}")
    inference_seconds = max(time.time() - start, 1e-9)
    metrics = evaluate_detections(
        annotations, detections, max_detections=args.detections_per_img
    )
    seed_value = train_args.get("seed", args.seed)
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "run_id": args.run_id,
        "protocol": args.protocol,
        "variant": args.variant,
        "model": args.model,
        "seed": int(seed_value) if str(seed_value).isdigit() else seed_value,
        **{key: value for key, value in metrics.items() if key != "summary_text"},
        "inference_seconds": inference_seconds,
        "fps": len(dataset) / inference_seconds,
        "detector_score_thr": args.detector_score_thr,
        "nms_thresh": args.nms_thresh,
        "detections_per_img": args.detections_per_img,
        "adapter": (
            "RGB float32/255 followed by appended thermal=0.0,event=0.0"
            if five_channel
            else "true three-channel RGB float32/255"
        ),
        "weights": str(weights),
        "checkpoint_sha256": file_sha256(weights),
        "manifest": str(manifest),
        "manifest_sha256": file_sha256(manifest),
        "annotations": str(annotations),
        "annotations_sha256": file_sha256(annotations),
        "git_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True
        ).strip(),
        "git_branch": subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=PROJECT_ROOT, text=True
        ).strip(),
        "command": subprocess.list2cmdline([sys.executable, *sys.argv]),
        "environment": environment(device),
        "coco_summary": metrics["summary_text"],
    }


def write_outputs(result, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    row = {
        key: value
        for key, value in result.items()
        if key not in {"environment", "coco_summary"}
    }
    for key, value in result["environment"].items():
        row[f"env_{key}"] = value
    with path.with_suffix(".csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    path.with_suffix(".txt").write_text(
        "V50 external RGB evaluation\n"
        "===========================\n"
        f"run_id: {result['run_id']}\n"
        f"protocol: {result['protocol']}\n"
        f"checkpoint_sha256: {result['checkpoint_sha256']}\n"
        f"AP@[0.50:0.95]: {result['ap50_95']:.6f}\n"
        f"AP50: {result['ap50']:.6f}\n"
        f"AP75: {result['ap75']:.6f}\n"
        f"AR100: {result['ar100']:.6f}\n"
        f"AP small/medium/large: {result['ap_small']:.6f} / {result['ap_medium']:.6f} / {result['ap_large']:.6f}\n"
        f"adapter: {result['adapter']}\n"
        f"command: {result['command']}\n\n"
        + result["coco_summary"],
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--protocol", required=True, choices=("devval", "test"))
    parser.add_argument("--variant", required=True)
    parser.add_argument("--model", required=True, choices=("early", "reliability", "rgb"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--data", default=r"D:\datasets\visdrone_seen")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--detector-score-thr", type=float, default=0.001)
    parser.add_argument("--nms-thresh", type=float, default=0.6)
    parser.add_argument("--detections-per-img", type=int, default=100)
    parser.add_argument("--out-json", required=True)
    args = parser.parse_args()
    result = evaluate(args)
    output = resolve_path(args.out_json)
    write_outputs(result, output)
    print(json.dumps({key: result[key] for key in ("run_id", "ap50_95", "ap50", "ap75")}, indent=2))


if __name__ == "__main__":
    main()

