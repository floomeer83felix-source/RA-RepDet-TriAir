#!/usr/bin/env python
"""Evaluate fixed RA-RepDet checkpoints on DroneVehicle single-modality streams.

The script only supports the locked RGB-only and thermal-only protocols prepared
by prepare_dronevehicle_modality_specific_eval.py. It does not tune thresholds,
NMS, input size, preprocessing, checkpoints, or model selection.
"""

import argparse
import csv
import gzip
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from PIL import Image
import torch
from torch.utils.data import DataLoader, Dataset


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.metrics import detection_metrics
from rarepdet.models.early_fusion_fcos import build_detector
from rarepdet.tools.eval_missing_modality import apply_missing_mode


SETTING_TO_GT = {
    "rgb_only": ("rgb", "rgb_native_hbb_annotations.jsonl", "DroneVehicle RGB", "thermal,event"),
    "thermal_only": ("thermal", "thermal_native_hbb_annotations.jsonl", "DroneVehicle thermal/IR", "rgb,event"),
}


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def sha256_file(path):
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
        "gpu": "NA",
    }
    if device.type == "cuda" and torch.cuda.is_available():
        env["gpu"] = torch.cuda.get_device_name(torch.cuda.current_device())
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


def add_f1(metrics):
    precision = metrics["precision"]
    recall = metrics["recall"]
    metrics["f1"] = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return metrics


class DroneVehicleModalityDataset(Dataset):
    def __init__(self, gt_jsonl, setting):
        if setting not in SETTING_TO_GT:
            raise ValueError(f"Unknown setting: {setting}")
        self.setting = setting
        self.records = []
        with Path(gt_jsonl).open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.records.append(json.loads(line))
        if not self.records:
            raise ValueError(f"No records found in {gt_jsonl}")

    def __len__(self):
        return len(self.records)

    def _load_rgb(self, image_path):
        with Image.open(image_path) as img:
            arr = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
        tensor = torch.from_numpy(arr).permute(2, 0, 1)
        image = torch.zeros((5, tensor.shape[1], tensor.shape[2]), dtype=torch.float32)
        image[0:3] = tensor
        return apply_missing_mode(image, "rgb_only")

    def _load_thermal(self, image_path):
        with Image.open(image_path) as img:
            arr = np.asarray(img.convert("L"), dtype=np.float32) / 255.0
        image = torch.zeros((5, arr.shape[0], arr.shape[1]), dtype=torch.float32)
        image[3] = torch.from_numpy(arr)
        return apply_missing_mode(image, "thermal_only")

    def __getitem__(self, index):
        record = self.records[index]
        if self.setting == "rgb_only":
            image = self._load_rgb(record["image_path"])
        else:
            image = self._load_thermal(record["image_path"])
        boxes = torch.tensor(record["boxes"], dtype=torch.float32)
        labels = torch.ones((boxes.shape[0],), dtype=torch.int64)
        target = {
            "boxes": boxes.reshape(-1, 4),
            "labels": labels,
            "image_id": torch.tensor([index], dtype=torch.int64),
        }
        return image, target


def load_model(args, device):
    weights = resolve_path(args.weights)
    if not weights.is_file():
        raise FileNotFoundError(f"Weights not found: {weights}")
    checkpoint = torch.load(weights, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type=args.model,
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=args.img_size,
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        score_thresh=args.detector_score_thr,
        nms_thresh=args.nms_thresh,
        detections_per_img=args.detections_per_img,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device)
    model.eval()
    return model, weights


def write_predictions(path, dataset, predictions):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for record, pred in zip(dataset.records, predictions):
            row = {
                "image_id": record["image_id"],
                "image_path": record["image_path"],
                "boxes": [[float(v) for v in box] for box in pred["boxes"].tolist()],
                "scores": [float(v) for v in pred["scores"].tolist()],
                "labels": [int(v) for v in pred["labels"].tolist()],
            }
            f.write(json.dumps(row, sort_keys=True) + "\n")


def result_fieldnames():
    return [
        "method_name",
        "checkpoint_label",
        "model_type",
        "external_setting",
        "real_input_modality",
        "unavailable_modalities",
        "native_gt_stream",
        "images",
        "gt_boxes",
        "raw_predictions",
        "precision",
        "recall",
        "f1",
        "ap50",
        "ap75",
        "predictions_at_metric_threshold",
        "mean_confidence",
        "aggregation_rule",
        "protocol_note",
        "weights",
        "checkpoint_sha256",
        "gt_jsonl",
        "gt_sha256",
        "data_manifest",
        "data_manifest_sha256",
        "git_commit",
        "detector_score_thr",
        "metric_score_thr",
        "nms_thresh",
        "detections_per_img",
        "img_size",
        "batch_size",
        "runtime_seconds",
        "fps",
        "start_time_utc",
        "end_time_utc",
        "env_python",
        "env_pytorch",
        "env_torchvision",
        "env_timm",
        "env_torch_cuda",
        "env_cuda_available",
        "env_gpu",
        "command",
        "predictions_file",
    ]


def write_single_result(metrics, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "metrics.csv"
    txt_path = out_dir / "metrics.txt"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=result_fieldnames())
        writer.writeheader()
        writer.writerow({field: metrics.get(field, "NA") for field in result_fieldnames()})
    with txt_path.open("w", encoding="utf-8") as f:
        for field in result_fieldnames():
            f.write(f"{field}: {metrics.get(field, 'NA')}\n")


def update_per_checkpoint(prepared_root, metrics):
    out_path = prepared_root / "aggregate_results" / "external_modality_specific_per_checkpoint.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if out_path.exists():
        with out_path.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        rows = [
            row
            for row in rows
            if not (
                row["method_name"] == metrics["method_name"]
                and row["checkpoint_label"] == metrics["checkpoint_label"]
                and row["external_setting"] == metrics["external_setting"]
            )
        ]
    rows.append({field: metrics.get(field, "NA") for field in result_fieldnames()})
    rows.sort(key=lambda r: (r["method_name"], r["external_setting"], r["checkpoint_label"]))
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=result_fieldnames())
        writer.writeheader()
        writer.writerows(rows)
    return out_path


def summarize_aggregate(prepared_root):
    per_path = prepared_root / "aggregate_results" / "external_modality_specific_per_checkpoint.csv"
    if not per_path.exists():
        return
    with per_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    groups = {}
    for row in rows:
        groups.setdefault((row["method_name"], row["external_setting"]), []).append(row)
    agg_rows = []
    for (method, setting), group in sorted(groups.items()):
        def mean(field):
            vals = [float(r[field]) for r in group]
            return sum(vals) / len(vals)

        first = group[0]
        agg_rows.append(
            {
                "Model": method,
                "External setting": setting,
                "Real input modality": first["real_input_modality"],
                "Unavailable modalities": first["unavailable_modalities"],
                "Native GT stream": first["native_gt_stream"],
                "Number of images": first["images"],
                "Number of vehicle boxes": first["gt_boxes"],
                "AP50": f"{mean('ap50'):.6f}",
                "AP75": f"{mean('ap75'):.6f}",
                "Precision": f"{mean('precision'):.6f}",
                "Recall": f"{mean('recall'):.6f}",
                "F1": f"{mean('f1'):.6f}",
                "Aggregation rule": f"arithmetic mean across {len(group)} validation-selected checkpoint(s)",
                "Protocol note": "native single-modality GT stream; no fused RGB-thermal target",
            }
        )
    agg_path = prepared_root / "aggregate_results" / "external_modality_specific_results.csv"
    with agg_path.open("w", encoding="utf-8", newline="") as f:
        fields = list(agg_rows[0].keys()) if agg_rows else []
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(agg_rows)

    md_path = prepared_root / "aggregate_results" / "external_modality_specific_results.md"
    with md_path.open("w", encoding="utf-8") as f:
        if not agg_rows:
            f.write("# External Modality-Specific Results\n\nNo rows.\n")
        else:
            fields = list(agg_rows[0].keys())
            f.write("# External Modality-Specific Results\n\n")
            f.write("| " + " | ".join(fields) + " |\n")
            f.write("| " + " | ".join(["---"] * len(fields)) + " |\n")
            for row in agg_rows:
                f.write("| " + " | ".join(str(row[field]) for field in fields) + " |\n")

    manifest_path = prepared_root / "aggregate_results" / "reproducibility_manifest.yaml"
    with manifest_path.open("w", encoding="utf-8") as f:
        f.write(f"generated_at: \"{datetime.now(timezone.utc).isoformat()}\"\n")
        f.write(f"git_commit: \"{git_commit()}\"\n")
        f.write("fixed_parameters:\n")
        f.write("  detector_score_thr: 0.001\n")
        f.write("  metric_score_thr: 0.50\n")
        f.write("  nms_thresh: 0.60\n")
        f.write("  detections_per_img: 100\n")
        f.write("files:\n")
        for path in [per_path, agg_path, md_path]:
            f.write(f"  {path.name}: \"{path}\"\n")
            f.write(f"  {path.name}_sha256: \"{sha256_file(path)}\"\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--setting", choices=sorted(SETTING_TO_GT), required=True)
    parser.add_argument("--model", choices=("early", "reliability"), required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--checkpoint-label", required=True)
    parser.add_argument("--method-name", required=True)
    parser.add_argument("--prepared-root", default=str(PROJECT_ROOT / "reproducibility" / "external_dronevehicle_modality_specific"))
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--detector-score-thr", type=float, default=0.001)
    parser.add_argument("--metric-score-thr", type=float, default=0.50)
    parser.add_argument("--nms-thresh", type=float, default=0.60)
    parser.add_argument("--detections-per-img", type=int, default=100)
    args = parser.parse_args()

    prepared_root = resolve_path(args.prepared_root)
    _, gt_name, real_input, unavailable = SETTING_TO_GT[args.setting]
    gt_jsonl = prepared_root / "prepared_annotations" / gt_name
    data_manifest = prepared_root / "manifests" / "dataset_manifest.yaml"
    if not gt_jsonl.is_file():
        raise FileNotFoundError(f"Prepared GT not found: {gt_jsonl}")

    requested_device = torch.device(args.device)
    if requested_device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        requested_device = torch.device("cpu")
    device = requested_device
    start_utc = datetime.now(timezone.utc).isoformat()
    start = time.time()

    dataset = DroneVehicleModalityDataset(gt_jsonl, args.setting)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )
    model, weights = load_model(args, device)

    predictions = []
    targets_cpu = []
    with torch.no_grad():
        for batch_index, (images, targets) in enumerate(loader, start=1):
            if batch_index % 100 == 0:
                print(f"{args.setting} {args.checkpoint_label}: batch {batch_index}/{len(loader)}")
            images = [image.to(device, non_blocking=True) for image in images]
            outputs = model(images)
            predictions.extend([{k: v.detach().cpu() for k, v in output.items()} for output in outputs])
            targets_cpu.extend([{k: v.detach().cpu() for k, v in target.items()} for target in targets])

    metrics = add_f1(detection_metrics(predictions, targets_cpu, score_thresh=args.metric_score_thr))
    elapsed = max(time.time() - start, 1e-6)
    end_utc = datetime.now(timezone.utc).isoformat()
    raw_predictions = sum(int(pred["scores"].numel()) for pred in predictions)
    out_dir = prepared_root / "per_model_results" / args.setting / args.checkpoint_label
    pred_path = prepared_root / "inference_outputs" / args.setting / f"{args.checkpoint_label}_predictions.jsonl.gz"
    write_predictions(pred_path, dataset, predictions)

    env = runtime_environment(device)
    row = {
        "method_name": args.method_name,
        "checkpoint_label": args.checkpoint_label,
        "model_type": args.model,
        "external_setting": args.setting,
        "real_input_modality": real_input,
        "unavailable_modalities": unavailable,
        "native_gt_stream": "RGB XML" if args.setting == "rgb_only" else "thermal/IR XML",
        "images": len(dataset),
        "gt_boxes": metrics["gt_boxes"],
        "raw_predictions": raw_predictions,
        "precision": f"{metrics['precision']:.10f}",
        "recall": f"{metrics['recall']:.10f}",
        "f1": f"{metrics['f1']:.10f}",
        "ap50": f"{metrics['ap50']:.10f}",
        "ap75": f"{metrics['ap75']:.10f}",
        "predictions_at_metric_threshold": metrics["predictions"],
        "mean_confidence": f"{metrics['mean_confidence']:.10f}",
        "aggregation_rule": "fixed arithmetic mean across validation-selected checkpoints",
        "protocol_note": "native single-modality GT stream; no fused RGB-thermal target",
        "weights": str(weights),
        "checkpoint_sha256": sha256_file(weights),
        "gt_jsonl": str(gt_jsonl),
        "gt_sha256": sha256_file(gt_jsonl),
        "data_manifest": str(data_manifest),
        "data_manifest_sha256": sha256_file(data_manifest) if data_manifest.is_file() else "NA",
        "git_commit": git_commit(),
        "detector_score_thr": args.detector_score_thr,
        "metric_score_thr": args.metric_score_thr,
        "nms_thresh": args.nms_thresh,
        "detections_per_img": args.detections_per_img,
        "img_size": args.img_size,
        "batch_size": args.batch_size,
        "runtime_seconds": f"{elapsed:.6f}",
        "fps": f"{len(dataset) / elapsed:.6f}",
        "start_time_utc": start_utc,
        "end_time_utc": end_utc,
        "env_python": env["python"],
        "env_pytorch": env["pytorch"],
        "env_torchvision": env["torchvision"],
        "env_timm": env["timm"],
        "env_torch_cuda": env["torch_cuda"],
        "env_cuda_available": env["cuda_available"],
        "env_gpu": env["gpu"],
        "command": " ".join(sys.argv),
        "predictions_file": str(pred_path),
    }
    write_single_result(row, out_dir)
    update_per_checkpoint(prepared_root, row)
    summarize_aggregate(prepared_root)
    print(
        f"{args.setting} {args.checkpoint_label}: "
        f"AP50={row['ap50']} AP75={row['ap75']} "
        f"P={row['precision']} R={row['recall']} F1={row['f1']}"
    )


if __name__ == "__main__":
    main()
