#!/usr/bin/env python
"""Evaluate one fixed RarePDet checkpoint with canonical COCO bbox AP."""

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

from datasets.triair_dataset import collate_fn
from rarepdet.coco_metrics import coco_detection_metrics
from rarepdet.data import DetectionTriAirDataset
from rarepdet.metrics import detection_metrics
from rarepdet.models.early_fusion_fcos import build_detector


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(*args):
    return subprocess.check_output(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


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
        "gpu": torch.cuda.get_device_name(torch.cuda.current_device())
        if device.type == "cuda"
        else "NA",
    }


def add_f1(metrics):
    precision = float(metrics["precision"])
    recall = float(metrics["recall"])
    metrics["f1"] = 0.0 if precision + recall == 0.0 else 2.0 * precision * recall / (precision + recall)
    return metrics


def evaluate(args):
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")

    weights = resolve_path(args.weights)
    split_file = resolve_path(args.split_file)
    if not weights.is_file():
        raise FileNotFoundError(f"checkpoint not found: {weights}")
    if not split_file.is_file():
        raise FileNotFoundError(f"split file not found: {split_file}")

    checkpoint = torch.load(weights, map_location=device, weights_only=False)
    model_cfg = checkpoint.get("model_cfg", {})
    train_args = checkpoint.get("train_args", {})
    model_type = args.model or model_cfg.get("model_type", "early")
    model = build_detector(
        model_type=model_type,
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", args.img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        score_thresh=args.detector_score_thr,
        nms_thresh=args.nms_thresh,
        detections_per_img=args.detections_per_img,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device)
    model.eval()

    dataset = DetectionTriAirDataset(
        args.data,
        split_file=str(split_file),
        mode="rgbte",
        train=False,
        modality_dropout=0.0,
    )
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=device.type == "cuda",
    )

    predictions = []
    targets_cpu = []
    inference_start = time.time()
    with torch.no_grad():
        for batch_index, (images, targets) in enumerate(loader, start=1):
            device_images = [image.to(device, non_blocking=True) for image in images]
            outputs = model(device_images)
            predictions.extend(
                [{key: value.detach().cpu() for key, value in output.items()} for output in outputs]
            )
            targets_cpu.extend(
                [{key: value.detach().cpu() for key, value in target.items()} for target in targets]
            )
            if batch_index == 1 or batch_index % 100 == 0 or batch_index == len(loader):
                print(f"inference batch {batch_index}/{len(loader)}")

    inference_seconds = max(time.time() - inference_start, 1e-9)
    metric_start = time.time()
    operating = add_f1(
        detection_metrics(predictions, targets_cpu, score_thresh=args.metric_score_thr)
    )
    coco = coco_detection_metrics(
        predictions,
        targets_cpu,
        score_thresh=0.0,
        max_detections=args.detections_per_img,
    )
    metric_seconds = time.time() - metric_start

    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "run_id": args.run_id,
        "protocol": args.protocol,
        "variant": args.variant,
        "model": model_type,
        "seed": int(train_args.get("seed", args.seed)) if str(train_args.get("seed", args.seed)).isdigit() else train_args.get("seed", args.seed),
        "modality_dropout": float(train_args.get("modality_dropout", args.modality_dropout)),
        "images": len(dataset),
        "precision": float(operating["precision"]),
        "recall": float(operating["recall"]),
        "f1": float(operating["f1"]),
        "project_ap50": float(operating["ap50"]),
        "project_ap75": float(operating["ap75"]),
        "ap50_95": float(coco["ap50_95"]),
        "ap50": float(coco["ap50"]),
        "ap75": float(coco["ap75"]),
        "ap_by_iou": coco["ap_by_iou"],
        "ar100": float(coco["ar100"]),
        "gt_boxes": int(coco["gt_boxes"]),
        "detections": int(coco["detections"]),
        "inference_seconds": inference_seconds,
        "metric_seconds": metric_seconds,
        "fps": len(dataset) / inference_seconds,
        "detector_score_thr": args.detector_score_thr,
        "metric_score_thr": args.metric_score_thr,
        "nms_thresh": args.nms_thresh,
        "detections_per_img": args.detections_per_img,
        "coco_recall_samples": coco["recall_thresholds"],
        "coco_backend": coco["backend"],
        "weights": str(weights),
        "checkpoint_sha256": file_sha256(weights),
        "split_file": str(split_file),
        "split_sha256": file_sha256(split_file),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_branch": git_value("branch", "--show-current"),
        "command": subprocess.list2cmdline([sys.executable, *sys.argv]),
        "environment": environment(device),
    }


def flattened(metrics):
    row = {key: value for key, value in metrics.items() if key not in {"ap_by_iou", "environment"}}
    for threshold, value in metrics["ap_by_iou"].items():
        row[f"ap_iou_{threshold.replace('.', '')}"] = value
    for key, value in metrics["environment"].items():
        row[f"env_{key}"] = value
    return row


def write_outputs(metrics, json_path):
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    row = flattened(metrics)
    csv_path = json_path.with_suffix(".csv")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)

    text_path = json_path.with_suffix(".txt")
    lines = [
        "V46 COCO-style checkpoint evaluation",
        "====================================",
        f"run_id: {metrics['run_id']}",
        f"protocol: {metrics['protocol']}",
        f"variant: {metrics['variant']}",
        f"checkpoint_sha256: {metrics['checkpoint_sha256']}",
        f"split_sha256: {metrics['split_sha256']}",
        f"images: {metrics['images']}",
        f"gt_boxes: {metrics['gt_boxes']}",
        f"detections: {metrics['detections']}",
        f"AP@[0.50:0.95]: {metrics['ap50_95']:.6f}",
        f"AP50: {metrics['ap50']:.6f}",
        f"AP75: {metrics['ap75']:.6f}",
        f"AR100: {metrics['ar100']:.6f}",
        f"precision@0.50: {metrics['precision']:.6f}",
        f"recall@0.50: {metrics['recall']:.6f}",
        f"F1@0.50: {metrics['f1']:.6f}",
        f"inference_seconds: {metrics['inference_seconds']:.3f}",
        f"metric_seconds: {metrics['metric_seconds']:.3f}",
        f"command: {metrics['command']}",
    ]
    for threshold, value in metrics["ap_by_iou"].items():
        lines.append(f"AP@{threshold}: {value:.6f}")
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path, text_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--protocol", required=True, choices=("devval", "guard", "ablation_devval"))
    parser.add_argument("--variant", required=True)
    parser.add_argument(
        "--model",
        choices=("early", "reliability", "reliability_rgbt", "ra_static_equal", "ra_stems_project"),
        default=None,
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--modality-dropout", type=float, default=0.0)
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--detector-score-thr", type=float, default=0.001)
    parser.add_argument("--metric-score-thr", type=float, default=0.50)
    parser.add_argument("--nms-thresh", type=float, default=0.6)
    parser.add_argument("--detections-per-img", type=int, default=100)
    parser.add_argument("--out-json", required=True)
    args = parser.parse_args()

    metrics = evaluate(args)
    json_path = resolve_path(args.out_json)
    csv_path, text_path = write_outputs(metrics, json_path)
    print(json.dumps({key: metrics[key] for key in ("run_id", "protocol", "ap50_95", "ap50", "ap75")}, indent=2))
    print(f"saved: {json_path}")
    print(f"saved: {csv_path}")
    print(f"saved: {text_path}")


if __name__ == "__main__":
    main()
