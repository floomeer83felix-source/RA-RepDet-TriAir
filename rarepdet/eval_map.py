#!/usr/bin/env python
"""Evaluate RarePDet checkpoints without pycocotools."""

import argparse
import csv
import hashlib
import platform
from pathlib import Path
import sys
import subprocess
import time

import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.metrics import detection_metrics, format_metrics
from rarepdet.models.availability_reliability_fusion_fcos import build_availability_reliability_fcos
from rarepdet.models.early_fusion_fcos import build_detector


NMS_THRESH = 0.6
DETECTIONS_PER_IMG = 100


def resolve_path(path):
    path = Path(path)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def file_sha256(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "NA"


def runtime_environment(device):
    env = {
        "python": platform.python_version(),
        "pytorch": torch.__version__,
        "torch_cuda": str(torch.version.cuda),
        "cuda_available": str(torch.cuda.is_available()),
        "device": str(device),
    }
    if device.type == "cuda" and torch.cuda.is_available():
        env["gpu"] = torch.cuda.get_device_name(torch.cuda.current_device())
    else:
        env["gpu"] = "NA"
    try:
        import torchvision

        env["torchvision"] = torchvision.__version__
    except Exception:
        env["torchvision"] = "NA"
    try:
        import timm

        env["timm"] = getattr(timm, "__version__", "NA")
    except Exception:
        env["timm"] = "NA"
    return env


def resolve_thresholds(args):
    legacy_score = 0.05 if args.score_thresh is None else args.score_thresh
    if args.detector_score_thr is None:
        args.detector_score_thr = legacy_score
    if args.metric_score_thr is None:
        args.metric_score_thr = legacy_score
    return args


def add_f1(metrics):
    precision = metrics["precision"]
    recall = metrics["recall"]
    metrics["f1"] = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return metrics


def evaluate_checkpoint(args):
    requested_device = torch.device(args.device)
    if requested_device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but not available. Falling back to CPU.")
        requested_device = torch.device("cpu")
    device = requested_device
    print(f"Using device: {device}")

    weights = resolve_path(args.weights)
    if not weights.is_file():
        raise FileNotFoundError(f"Weights not found: {weights}")
    split_file = resolve_path(args.split_file)
    if not split_file.is_file():
        raise FileNotFoundError(f"Split file not found: {split_file}")

    checkpoint = torch.load(weights, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    train_args = checkpoint.get("train_args", {})
    model_type = args.model or model_cfg.get("model_type", "early")
    if model_type == "availability_reliability":
        model = build_availability_reliability_fcos(
            model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
            img_size=model_cfg.get("img_size", args.img_size),
            num_classes=model_cfg.get("num_classes", 2),
            fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
            score_thresh=args.detector_score_thr,
            nms_thresh=args.nms_thresh,
            detections_per_img=args.detections_per_img,
        )
    else:
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
        pin_memory=(device.type == "cuda"),
    )

    predictions = []
    targets_cpu = []
    start = time.time()
    with torch.no_grad():
        for images, targets in loader:
            device_images = [image.to(device, non_blocking=True) for image in images]
            outputs = model(device_images)
            predictions.extend([{key: value.detach().cpu() for key, value in output.items()} for output in outputs])
            targets_cpu.extend([{key: value.detach().cpu() for key, value in target.items()} for target in targets])

    metrics = add_f1(detection_metrics(predictions, targets_cpu, score_thresh=args.metric_score_thr))
    elapsed = max(time.time() - start, 1e-6)
    metrics["fps"] = len(dataset) / elapsed
    metrics["runtime_seconds"] = elapsed
    metrics["images"] = len(dataset)
    metrics["weights"] = str(weights)
    metrics["checkpoint_sha256"] = file_sha256(weights)
    metrics["split_file"] = str(split_file)
    metrics["split_sha256"] = file_sha256(split_file)
    metrics["model"] = model_type
    metrics["seed"] = train_args.get("seed", "NA")
    metrics["detector_score_thr"] = args.detector_score_thr
    metrics["metric_score_thr"] = args.metric_score_thr
    metrics["nms_thresh"] = args.nms_thresh
    metrics["detections_per_img"] = args.detections_per_img
    metrics["git_commit"] = git_commit()
    metrics.update({f"env_{key}": value for key, value in runtime_environment(device).items()})
    return metrics


def write_csv(metrics, out_path):
    csv_path = out_path.with_suffix(".csv")
    fieldnames = [
        "model",
        "seed",
        "images",
        "precision",
        "recall",
        "f1",
        "ap50",
        "ap75",
        "gt_boxes",
        "predictions",
        "mean_confidence",
        "fps",
        "runtime_seconds",
        "detector_score_thr",
        "metric_score_thr",
        "nms_thresh",
        "detections_per_img",
        "weights",
        "checkpoint_sha256",
        "split_file",
        "split_sha256",
        "git_commit",
        "env_python",
        "env_pytorch",
        "env_torchvision",
        "env_timm",
        "env_torch_cuda",
        "env_cuda_available",
        "env_gpu",
        "env_device",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({key: metrics.get(key, "NA") for key in fieldnames})
    return csv_path


def main():
    parser = argparse.ArgumentParser(description="Evaluate RarePDet AP without pycocotools.")
    parser.add_argument("--model", default=None, choices=("early", "reliability", "availability_reliability"), help="Override model type")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--weights", default="runs/rarepdet_early/best.pt")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=2, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--score-thresh", "--score-thr", dest="score_thresh", default=None, type=float)
    parser.add_argument("--detector-score-thr", default=None, type=float, help="Score threshold used inside FCOS output filtering.")
    parser.add_argument("--metric-score-thr", default=None, type=float, help="Operating threshold for precision/recall/F1.")
    parser.add_argument("--nms-thresh", default=NMS_THRESH, type=float)
    parser.add_argument("--detections-per-img", default=DETECTIONS_PER_IMG, type=int)
    parser.add_argument("--out", default="runs/rarepdet_early/eval_results.txt")
    args = resolve_thresholds(parser.parse_args())

    metrics = evaluate_checkpoint(args)
    result_text = (
        "RarePDet eval results\n"
        "====================\n"
        f"model: {metrics['model']}\n"
        f"weights: {metrics['weights']}\n"
        f"checkpoint_sha256: {metrics['checkpoint_sha256']}\n"
        f"split_file: {metrics['split_file']}\n"
        f"split_sha256: {metrics['split_sha256']}\n"
        f"git_commit: {metrics['git_commit']}\n"
        f"seed: {metrics['seed']}\n"
        f"detector_score_thr: {metrics['detector_score_thr']}\n"
        f"metric_score_thr: {metrics['metric_score_thr']}\n"
        f"nms_thresh: {metrics['nms_thresh']}\n"
        f"detections_per_img: {metrics['detections_per_img']}\n"
        f"images: {metrics['images']}\n"
        f"Precision: {metrics['precision']:.6f}\n"
        f"Recall: {metrics['recall']:.6f}\n"
        f"F1: {metrics['f1']:.6f}\n"
        f"AP50: {metrics['ap50']:.6f}\n"
        f"AP75: {metrics['ap75']:.6f}\n"
        f"GT boxes: {metrics['gt_boxes']}\n"
        f"Predictions: {metrics['predictions']}\n"
        f"Mean Confidence: {metrics['mean_confidence']:.6f}\n"
        f"FPS: {metrics['fps']:.2f}\n"
        f"runtime_seconds: {metrics['runtime_seconds']:.3f}\n"
        f"python: {metrics['env_python']}\n"
        f"pytorch: {metrics['env_pytorch']}\n"
        f"torchvision: {metrics['env_torchvision']}\n"
        f"timm: {metrics['env_timm']}\n"
        f"torch_cuda: {metrics['env_torch_cuda']}\n"
        f"cuda_available: {metrics['env_cuda_available']}\n"
        f"gpu: {metrics['env_gpu']}\n"
    )
    print(result_text)

    out_path = resolve_path(args.out)
    if out_path.suffix.lower() != ".txt":
        out_path = out_path / "eval_results.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result_text, encoding="utf-8")
    csv_path = write_csv(metrics, out_path)
    print(f"Saved eval results to: {out_path}")
    print(f"Saved eval CSV to: {csv_path}")


if __name__ == "__main__":
    main()
