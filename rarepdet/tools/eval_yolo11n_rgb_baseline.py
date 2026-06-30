#!/usr/bin/env python
"""Evaluate YOLO11n RGB baseline with the project-local AP implementation."""

import argparse
import csv
from pathlib import Path
import sys
import time

import torch
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.metrics import detection_metrics


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def read_yaml_value(yaml_path, key):
    for line in Path(yaml_path).read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return None


def load_val_images(data_yaml):
    data_yaml = resolve_path(data_yaml)
    root = Path(read_yaml_value(data_yaml, "path"))
    if not root.is_absolute():
        root = data_yaml.parent / root
    val_rel = read_yaml_value(data_yaml, "val")
    image_dir = root / val_rel
    images = sorted(list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.jpeg")))
    if not images:
        raise FileNotFoundError(f"No validation images found in {image_dir}")
    label_dir = root / "labels" / "val"
    return images, label_dir


def target_from_label(image_path, label_dir):
    width, height = Image.open(image_path).size
    label_path = label_dir / f"{image_path.stem}.txt"
    boxes = []
    labels = []
    if label_path.exists():
        for raw in label_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 5:
                raise RuntimeError(f"Invalid YOLO label row in {label_path}: {line}")
            class_id = int(parts[0])
            if class_id != 0:
                raise RuntimeError(f"Unexpected YOLO class {class_id} in {label_path}; expected 0")
            cx, cy, bw, bh = [float(value) for value in parts[1:]]
            x1 = (cx - bw / 2.0) * width
            y1 = (cy - bh / 2.0) * height
            x2 = (cx + bw / 2.0) * width
            y2 = (cy + bh / 2.0) * height
            boxes.append((x1, y1, x2, y2))
            labels.append(1)
    return {
        "boxes": torch.tensor(boxes, dtype=torch.float32).reshape(-1, 4),
        "labels": torch.tensor(labels, dtype=torch.int64),
    }


def prediction_from_result(result):
    boxes_obj = result.boxes
    if boxes_obj is None or boxes_obj.xyxy is None or boxes_obj.xyxy.numel() == 0:
        return {
            "boxes": torch.zeros((0, 4), dtype=torch.float32),
            "scores": torch.zeros((0,), dtype=torch.float32),
            "labels": torch.zeros((0,), dtype=torch.int64),
        }
    boxes = boxes_obj.xyxy.detach().cpu().to(torch.float32)
    scores = boxes_obj.conf.detach().cpu().to(torch.float32)
    labels = boxes_obj.cls.detach().cpu().to(torch.int64) + 1
    return {"boxes": boxes, "scores": scores, "labels": labels}


def write_outputs(out_dir, row):
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / "eval_results.txt"
    csv_path = out_dir / "eval_results.csv"
    with txt_path.open("w", encoding="utf-8") as f:
        f.write("YOLO11n RGB baseline eval results\n")
        f.write("=================================\n")
        for key, value in row.items():
            f.write(f"{key}: {value}\n")
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)
    return txt_path, csv_path


def main():
    parser = argparse.ArgumentParser(description="Evaluate YOLO11n RGB baseline.")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--data-yaml", default=r"runs\local_yolo11n_rgb_cache\triair_yolo11n_rgb.yaml")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="0")
    parser.add_argument("--batch-size", default=16, type=int)
    parser.add_argument("--pred-conf", default=0.001, type=float)
    parser.add_argument("--score-thr", default=0.50, type=float)
    parser.add_argument("--iou", default=0.7, type=float)
    parser.add_argument("--method", default="YOLO11n RGB-only")
    parser.add_argument("--seed", default="NA")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    from ultralytics import YOLO

    weights = resolve_path(args.weights)
    if not weights.is_file():
        raise FileNotFoundError(f"Weights not found: {weights}")
    images, label_dir = load_val_images(args.data_yaml)
    targets = [target_from_label(path, label_dir) for path in images]

    model = YOLO(str(weights))
    predictions = []
    start = time.time()
    for start_idx in range(0, len(images), args.batch_size):
        batch = images[start_idx : start_idx + args.batch_size]
        results = model.predict(
            source=[str(path) for path in batch],
            imgsz=args.img_size,
            conf=args.pred_conf,
            iou=args.iou,
            device=args.device,
            verbose=False,
        )
        predictions.extend(prediction_from_result(result) for result in results)
        print(f"evaluated {min(start_idx + len(batch), len(images))}/{len(images)}")
    elapsed = max(time.time() - start, 1e-6)

    metrics = detection_metrics(predictions, targets, score_thresh=args.score_thr)
    precision = metrics["precision"]
    recall = metrics["recall"]
    f1 = 0.0 if precision + recall <= 0 else 2.0 * precision * recall / (precision + recall)
    row = {
        "Method": args.method,
        "Seed": args.seed,
        "Images": len(images),
        "Weights": str(weights),
        "Precision": f"{precision:.6f}",
        "Recall": f"{recall:.6f}",
        "F1": f"{f1:.6f}",
        "AP50": f"{metrics['ap50']:.6f}",
        "AP75": f"{metrics['ap75']:.6f}",
        "GT boxes": metrics["gt_boxes"],
        "Predictions": metrics["predictions"],
        "Mean Confidence": f"{metrics['mean_confidence']:.6f}",
        "FPS": f"{len(images) / elapsed:.6f}",
        "Score Threshold": args.score_thr,
        "Prediction Conf": args.pred_conf,
    }
    paths = write_outputs(resolve_path(args.out), row)
    for path in paths:
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()
