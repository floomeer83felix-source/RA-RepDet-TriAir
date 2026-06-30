#!/usr/bin/env python
"""Evaluate detector robustness under missing RGB/Thermal/Event modalities."""

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


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.metrics import detection_metrics
from rarepdet.models.availability_reliability_fusion_fcos import build_availability_reliability_fcos
from rarepdet.models.early_fusion_fcos import build_detector


MODES = ("full", "no_rgb", "no_thermal", "no_event", "rgb_only", "thermal_only", "event_only")
NMS_THRESH = 0.6
DETECTIONS_PER_IMG = 100


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def file_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
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
    legacy_score = 0.001 if args.score_thr is None else args.score_thr
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


def apply_missing_mode(image, mode):
    image = image.clone()
    if mode == "full":
        return image
    if mode == "no_rgb":
        image[0:3] = 0
    elif mode == "no_thermal":
        image[3:4] = 0
    elif mode == "no_event":
        image[4:5] = 0
    elif mode == "rgb_only":
        image[3:5] = 0
    elif mode == "thermal_only":
        image[0:3] = 0
        image[4:5] = 0
    elif mode == "event_only":
        image[0:4] = 0
    else:
        raise ValueError(f"Unknown missing-modality mode: {mode}")
    return image


def load_model(args, device):
    weights = resolve_path(args.weights)
    if not weights.is_file():
        raise FileNotFoundError(f"Weights not found: {weights}")
    checkpoint = torch.load(weights, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
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
    return model, model_type, checkpoint


def evaluate_mode(model, loader, device, mode, metric_score_thr):
    predictions = []
    targets_cpu = []
    start = time.time()
    with torch.no_grad():
        for images, targets in loader:
            images = [apply_missing_mode(image, mode).to(device, non_blocking=True) for image in images]
            outputs = model(images)
            predictions.extend([{k: v.detach().cpu() for k, v in output.items()} for output in outputs])
            targets_cpu.extend([{k: v.detach().cpu() for k, v in target.items()} for target in targets])
    metrics = add_f1(detection_metrics(predictions, targets_cpu, score_thresh=metric_score_thr))
    metrics["runtime_seconds"] = max(time.time() - start, 1e-6)
    metrics["fps"] = len(targets_cpu) / metrics["runtime_seconds"]
    return metrics


def write_outputs(rows, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / "missing_modality_results.txt"
    csv_path = out_dir / "missing_modality_results.csv"
    headers = [
        "Mode",
        "Precision",
        "Recall",
        "F1",
        "AP50",
        "AP75",
        "GT boxes",
        "Predictions",
        "Mean Confidence",
        "FPS",
        "Runtime Seconds",
        "Detector Score Thr",
        "Metric Score Thr",
        "NMS Thr",
        "Detections Per Img",
        "Model",
        "Seed",
        "Weights",
        "Checkpoint SHA256",
        "Split File",
        "Split SHA256",
        "Git Commit",
        "Python",
        "PyTorch",
        "Torchvision",
        "timm",
        "Torch CUDA",
        "CUDA Available",
        "GPU",
    ]

    with txt_path.open("w", encoding="utf-8") as f:
        f.write(" | ".join(headers) + "\n")
        f.write(" | ".join(["---"] * len(headers)) + "\n")
        for row in rows:
            f.write(
                f"{row['Mode']} | {row['Precision']:.6f} | {row['Recall']:.6f} | "
                f"{row['F1']:.6f} | {row['AP50']:.6f} | {row['AP75']:.6f} | "
                f"{row['GT boxes']} | {row['Predictions']} | {row['Mean Confidence']:.6f} | "
                f"{row['FPS']:.2f} | {row['Runtime Seconds']:.3f} | "
                f"{row['Detector Score Thr']} | {row['Metric Score Thr']} | "
                f"{row['NMS Thr']} | {row['Detections Per Img']} | {row['Model']} | "
                f"{row['Seed']} | {row['Weights']} | {row['Checkpoint SHA256']} | "
                f"{row['Split File']} | {row['Split SHA256']} | {row['Git Commit']} | "
                f"{row['Python']} | {row['PyTorch']} | {row['Torchvision']} | {row['timm']} | "
                f"{row['Torch CUDA']} | {row['CUDA Available']} | {row['GPU']}\n"
            )

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return txt_path, csv_path


def main():
    parser = argparse.ArgumentParser(description="Evaluate missing-modality robustness.")
    parser.add_argument("--model", choices=("early", "reliability", "availability_reliability"), default=None)
    parser.add_argument("--data", default="<LOCAL_DATASET_ROOT>")
    parser.add_argument("--split-file", default="runs/blocked_split_candidates/block64_guard16_seed0_val.txt")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--score-thr", "--score-thresh", dest="score_thr", default=None, type=float)
    parser.add_argument("--detector-score-thr", default=None, type=float, help="Score threshold used inside FCOS output filtering.")
    parser.add_argument("--metric-score-thr", default=None, type=float, help="Operating threshold for precision/recall/F1.")
    parser.add_argument("--nms-thresh", default=NMS_THRESH, type=float)
    parser.add_argument("--detections-per-img", default=DETECTIONS_PER_IMG, type=int)
    parser.add_argument("--out", required=True)
    args = resolve_thresholds(parser.parse_args())

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        device = torch.device("cpu")

    weights = resolve_path(args.weights)
    split_file = resolve_path(args.split_file)
    if not split_file.is_file():
        raise FileNotFoundError(f"Split file not found: {split_file}")
    model, model_type, checkpoint = load_model(args, device)
    train_args = checkpoint.get("train_args", {})
    env = runtime_environment(device)
    dataset = DetectionTriAirDataset(args.data, split_file=str(split_file), mode="rgbte", train=False)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )

    rows = []
    for mode in MODES:
        metrics = evaluate_mode(model, loader, device, mode, args.metric_score_thr)
        row = {
            "Mode": mode,
            "Precision": metrics["precision"],
            "Recall": metrics["recall"],
            "F1": metrics["f1"],
            "AP50": metrics["ap50"],
            "AP75": metrics["ap75"],
            "GT boxes": metrics["gt_boxes"],
            "Predictions": metrics["predictions"],
            "Mean Confidence": metrics["mean_confidence"],
            "FPS": metrics["fps"],
            "Runtime Seconds": metrics["runtime_seconds"],
            "Detector Score Thr": args.detector_score_thr,
            "Metric Score Thr": args.metric_score_thr,
            "NMS Thr": args.nms_thresh,
            "Detections Per Img": args.detections_per_img,
            "Model": model_type,
            "Seed": train_args.get("seed", "NA"),
            "Weights": str(weights),
            "Checkpoint SHA256": file_sha256(weights),
            "Split File": str(split_file),
            "Split SHA256": file_sha256(split_file),
            "Git Commit": git_commit(),
            "Python": env["python"],
            "PyTorch": env["pytorch"],
            "Torchvision": env["torchvision"],
            "timm": env["timm"],
            "Torch CUDA": env["torch_cuda"],
            "CUDA Available": env["cuda_available"],
            "GPU": env["gpu"],
        }
        rows.append(row)
        print(
            f"{model_type} {mode}: Precision={row['Precision']:.4f} Recall={row['Recall']:.4f} "
            f"F1={row['F1']:.4f} AP50={row['AP50']:.4f} AP75={row['AP75']:.4f}"
        )

    txt_path, csv_path = write_outputs(rows, resolve_path(args.out))
    print(f"Saved: {txt_path}")
    print(f"Saved: {csv_path}")


if __name__ == "__main__":
    main()
