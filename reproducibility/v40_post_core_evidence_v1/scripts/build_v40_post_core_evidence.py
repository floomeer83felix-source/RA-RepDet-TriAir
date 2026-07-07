#!/usr/bin/env python
"""Build the V40 post-core non-training evidence package.

This script uses only the four fixed V40-v2 checkpoints produced by the
compute-minimized run. It does not train, tune, evaluate guard data, touch
DroneVehicle data, or edit manuscript files.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import random
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import median

import numpy as np
import torch
from torch.utils.data import DataLoader


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.triair_dataset import TriAirDataset, collate_fn, parse_yolo_label_file
from rarepdet.data import DetectionTriAirDataset
from rarepdet.metrics import box_iou, detection_metrics
from rarepdet.models.availability_reliability_fusion_fcos import build_availability_reliability_fcos
from rarepdet.models.early_fusion_fcos import build_detector


DATA_ROOT = Path("D:/download/triair")
POST_ROOT = ROOT / "reproducibility" / "v40_post_core_evidence_v1"
READINESS_ROOT = ROOT / "reproducibility" / "pre_manuscript_readiness_v1"
CORE_ROOT = ROOT / "runs" / "v40_expanded_adjacency_v2_compute_minimized"
SPLIT_ROOT = ROOT / "reproducibility" / "v40_expanded_adjacency_component_split_v2"
CONTRACT_ROOT = ROOT / "reproducibility" / "v40_experiment_contract_v1"
AMEND_ROOT = CONTRACT_ROOT / "amendments" / "compute_minimized_v1"
TRAIN_MANIFEST = SPLIT_ROOT / "manifests" / "v40_expanded_adjacency_component_disjoint_train.txt"
VAL_MANIFEST = SPLIT_ROOT / "manifests" / "v40_expanded_adjacency_component_disjoint_val.txt"
GUARD_MANIFEST = SPLIT_ROOT / "manifests" / "v40_guard_unchanged_archival.txt"
FROZEN_ENV = CONTRACT_ROOT / "contract" / "v40_environment.json"
LIMITATION = "These deterministic zero-channel evaluations do not emulate measured physical sensor faults or real cross-sensor deployment failures."

DETECTOR_SCORE_THR = 0.001
METRIC_SCORE_THR = 0.50
NMS_THRESH = 0.6
DETECTIONS_PER_IMG = 100
IMG_SIZE = 640
BATCH_SIZE = 4
NUM_WORKERS = 0
BOOTSTRAP_SEED = 20260707
BOOTSTRAP_RESAMPLES = 2000


RUNS = [
    {
        "run_id": "matched_early_seed0",
        "model_group": "matched_early",
        "model": "early",
        "seed": "0",
        "weights": CORE_ROOT / "matched_early_seed0" / "weights" / "best.pt",
    },
    {
        "run_id": "matched_early_seed2",
        "model_group": "matched_early",
        "model": "early",
        "seed": "2",
        "weights": CORE_ROOT / "matched_early_seed2" / "weights" / "best.pt",
    },
    {
        "run_id": "reliability_p015_seed0",
        "model_group": "reliability_p015",
        "model": "reliability",
        "seed": "0",
        "weights": CORE_ROOT / "reliability_p015_seed0" / "weights" / "best.pt",
    },
    {
        "run_id": "reliability_p015_seed2",
        "model_group": "reliability_p015",
        "model": "reliability",
        "seed": "2",
        "weights": CORE_ROOT / "reliability_p015_seed2" / "weights" / "best.pt",
    },
]

CONDITIONS = [
    ("all_modal", "all modalities available"),
    ("rgb_removed", "synthetic channel removal: channels 0:3 zeroed"),
    ("thermal_removed", "synthetic channel removal: channel 3 zeroed"),
    ("event_removed", "synthetic channel removal: channel 4 zeroed"),
]

METRICS = ["precision", "recall", "f1", "ap50", "ap75"]


@dataclass
class PredictionBundle:
    run: dict
    predictions: list[dict[str, torch.Tensor]]
    targets: list[dict[str, torch.Tensor]]
    sample_infos: list[dict]
    gt_counts: np.ndarray


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def md_table(rows: list[dict], fields: list[str] | None = None) -> list[str]:
    if not rows:
        return ["_No rows._"]
    fields = fields or list(rows[0].keys())
    lines = [
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join(["---"] * len(fields)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return lines


def git_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"NA ({type(exc).__name__}: {exc})"


def runtime_environment() -> dict:
    env = {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
    }
    try:
        import numpy
        import timm
        import torchvision

        env.update(
            {
                "numpy": numpy.__version__,
                "pytorch": torch.__version__,
                "torchvision": torchvision.__version__,
                "timm": getattr(timm, "__version__", "NA"),
                "torch_cuda": str(torch.version.cuda),
                "cuda_available": str(torch.cuda.is_available()),
                "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NA",
                "cudnn_version": str(torch.backends.cudnn.version()),
            }
        )
    except Exception as exc:
        env["torch_stack_probe_error"] = f"{type(exc).__name__}: {exc}"
    try:
        smi = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        env["nvidia_smi"] = smi
    except Exception as exc:
        env["nvidia_smi"] = f"NA ({type(exc).__name__}: {exc})"
    return env


def compare_environment(actual: dict, frozen: dict) -> dict:
    keys = ["python", "pytorch", "torchvision", "timm", "torch_cuda", "cuda_available", "gpu", "numpy", "nvidia_smi"]
    comparisons = {}
    for key in keys:
        comparisons[key] = {
            "actual": str(actual.get(key)),
            "frozen": str(frozen.get(key)),
            "match": str(actual.get(key)) == str(frozen.get(key)),
        }
    status = "PASS" if all(item["match"] for item in comparisons.values()) else "BLOCKED"
    return {"status": status, "comparisons": comparisons}


def ensure_dirs() -> None:
    for path in [
        "source_lock",
        "channel_removal",
        "efficiency",
        "bootstrap",
        "qualitative",
        "reproducibility",
        "provenance",
        "readiness",
        "scripts",
        "reports",
    ]:
        (POST_ROOT / path).mkdir(parents=True, exist_ok=True)
    READINESS_ROOT.mkdir(parents=True, exist_ok=True)


def pick_device() -> torch.device:
    requested = torch.device("cuda")
    if requested.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is required by the frozen V40 runtime but is not available.")
    return requested


def add_f1(metrics: dict) -> dict:
    precision = metrics["precision"]
    recall = metrics["recall"]
    metrics["f1"] = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return metrics


def apply_channel_condition(image: torch.Tensor, condition: str) -> torch.Tensor:
    image = image.clone()
    if condition == "all_modal":
        return image
    if condition == "rgb_removed":
        image[0:3] = 0
    elif condition == "thermal_removed":
        image[3:4] = 0
    elif condition == "event_removed":
        image[4:5] = 0
    else:
        raise ValueError(f"Unknown condition: {condition}")
    return image


def load_model(run: dict, device: torch.device):
    weights = run["weights"]
    if not weights.is_file():
        raise FileNotFoundError(f"Required checkpoint missing: {weights}")
    checkpoint = torch.load(weights, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model_type = run["model"]
    if model_type == "availability_reliability":
        model = build_availability_reliability_fcos(
            model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
            img_size=model_cfg.get("img_size", IMG_SIZE),
            num_classes=model_cfg.get("num_classes", 2),
            fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
            score_thresh=DETECTOR_SCORE_THR,
            nms_thresh=NMS_THRESH,
            detections_per_img=DETECTIONS_PER_IMG,
        )
    else:
        model = build_detector(
            model_type=model_type,
            model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
            img_size=model_cfg.get("img_size", IMG_SIZE),
            num_classes=model_cfg.get("num_classes", 2),
            fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
            score_thresh=DETECTOR_SCORE_THR,
            nms_thresh=NMS_THRESH,
            detections_per_img=DETECTIONS_PER_IMG,
        )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device)
    model.eval()
    return model, checkpoint


def make_loader() -> tuple[DetectionTriAirDataset, DataLoader]:
    dataset = DetectionTriAirDataset(
        DATA_ROOT,
        split_file=str(VAL_MANIFEST),
        mode="rgbte",
        train=False,
        modality_dropout=0.0,
    )
    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        collate_fn=collate_fn,
        pin_memory=True,
    )
    return dataset, loader


def evaluate_condition(
    model,
    loader: DataLoader,
    device: torch.device,
    condition: str,
    keep_predictions: bool = False,
):
    predictions = []
    targets_cpu = []
    start = time.perf_counter()
    with torch.inference_mode():
        for images, targets in loader:
            device_images = [apply_channel_condition(image, condition).to(device, non_blocking=True) for image in images]
            outputs = model(device_images)
            predictions.extend([{key: value.detach().cpu() for key, value in output.items()} for output in outputs])
            targets_cpu.extend([{key: value.detach().cpu() for key, value in target.items()} for target in targets])
    elapsed = max(time.perf_counter() - start, 1e-9)
    metrics = add_f1(detection_metrics(predictions, targets_cpu, score_thresh=METRIC_SCORE_THR))
    metrics["runtime_seconds"] = elapsed
    metrics["fps"] = len(targets_cpu) / elapsed
    if keep_predictions:
        return metrics, predictions, targets_cpu
    return metrics, None, None


def count_params(model) -> tuple[int, int]:
    params = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return params, trainable


def try_flops(model, dummy: torch.Tensor) -> dict:
    try:
        from thop import profile

        raw_macs, _ = profile(model.backbone.eval(), inputs=(dummy,), verbose=False)
        raw_gflops = float(raw_macs) * 2.0 / 1e9
    except Exception as exc:
        raw_gflops = "NA"
        raw_note = f"thop raw backbone profile failed: {type(exc).__name__}: {exc}"
    else:
        raw_note = "thop profile on model.backbone; reported as MACs*2/1e9."

    try:
        from thop import profile

        class DetectorWrapper(torch.nn.Module):
            def __init__(self, wrapped):
                super().__init__()
                self.wrapped = wrapped

            def forward(self, x):
                return self.wrapped([x[0]])

        det_macs, _ = profile(DetectorWrapper(model).eval(), inputs=(dummy,), verbose=False)
        det_gflops = float(det_macs) * 2.0 / 1e9
    except Exception as exc:
        det_gflops = "NA"
        det_note = f"thop detector profile failed: {type(exc).__name__}: {exc}"
    else:
        det_note = "thop profile on FCOS detector wrapper; reported as MACs*2/1e9."

    return {
        "raw_forward": {"gflops": raw_gflops, "note": raw_note},
        "detector_inference": {"gflops": det_gflops, "note": det_note},
    }


def measure_callable(fn, images: int, device: torch.device, warmup: int, iters: int) -> dict:
    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)
    with torch.inference_mode():
        for _ in range(warmup):
            _ = fn()
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        start = time.perf_counter()
        for _ in range(iters):
            _ = fn()
        if device.type == "cuda":
            torch.cuda.synchronize(device)
    elapsed = max(time.perf_counter() - start, 1e-9)
    latency = elapsed * 1000.0 / max(images * iters, 1)
    return {
        "runtime_seconds": elapsed,
        "fps": images * iters / elapsed,
        "latency_ms_per_img": latency,
        "cuda_peak_memory_mb": torch.cuda.max_memory_allocated(device) / (1024**2) if device.type == "cuda" else 0.0,
    }


def summarize_values(values: list[float]) -> dict:
    values = [float(v) for v in values]
    return {
        "median": median(values),
        "min": min(values),
        "max": max(values),
    }


def bootstrap_ap(sorted_image_ids: np.ndarray, sorted_tp: np.ndarray, sorted_fp: np.ndarray, counts: np.ndarray, total_gt: float) -> float:
    if total_gt <= 0:
        return 0.0
    weights = counts[sorted_image_ids].astype(np.float64)
    weighted_tp = sorted_tp * weights
    weighted_fp = sorted_fp * weights
    if weighted_tp.sum() + weighted_fp.sum() <= 0:
        return 0.0
    tp_cum = np.cumsum(weighted_tp)
    fp_cum = np.cumsum(weighted_fp)
    recalls = tp_cum / max(total_gt, 1e-12)
    precisions = tp_cum / np.maximum(tp_cum + fp_cum, 1e-12)
    mrec = np.concatenate(([0.0], recalls, [1.0]))
    mpre = np.concatenate(([0.0], precisions, [0.0]))
    for i in range(mpre.size - 1, 0, -1):
        if mpre[i - 1] < mpre[i]:
            mpre[i - 1] = mpre[i]
    changed = np.where(mrec[1:] != mrec[:-1])[0]
    return float(np.sum((mrec[changed + 1] - mrec[changed]) * mpre[changed + 1]))


def precompute_bootstrap_records(bundle: PredictionBundle, iou_thresh: float) -> dict:
    image_ids = []
    scores = []
    tps = []
    fps = []
    tp50_by_image = np.zeros(len(bundle.targets), dtype=np.float64)
    fp50_by_image = np.zeros(len(bundle.targets), dtype=np.float64)

    for image_index, (pred, target) in enumerate(zip(bundle.predictions, bundle.targets)):
        gt_boxes = target["boxes"].detach().cpu()
        gt_labels = target["labels"].detach().cpu()
        gt_boxes = gt_boxes[gt_labels == 1]

        boxes = pred["boxes"].detach().cpu()
        pred_scores = pred["scores"].detach().cpu()
        labels = pred["labels"].detach().cpu()
        keep = labels == 1
        boxes = boxes[keep]
        pred_scores = pred_scores[keep]
        if pred_scores.numel() == 0:
            continue
        order = torch.argsort(pred_scores, descending=True)
        boxes = boxes[order]
        pred_scores = pred_scores[order]
        matched = torch.zeros(len(gt_boxes), dtype=torch.bool)
        for box, score in zip(boxes, pred_scores):
            is_tp = 0.0
            is_fp = 1.0
            if gt_boxes.numel() > 0:
                ious = box_iou(box.view(1, 4), gt_boxes).view(-1)
                best_iou, best_index = torch.max(ious, dim=0)
                best_index = int(best_index)
                if float(best_iou) >= iou_thresh and not bool(matched[best_index]):
                    matched[best_index] = True
                    is_tp = 1.0
                    is_fp = 0.0
            image_ids.append(image_index)
            scores.append(float(score))
            tps.append(is_tp)
            fps.append(is_fp)
            if iou_thresh == 0.5 and float(score) >= METRIC_SCORE_THR:
                tp50_by_image[image_index] += is_tp
                fp50_by_image[image_index] += is_fp

    if scores:
        order = np.argsort(-np.asarray(scores, dtype=np.float64), kind="mergesort")
        sorted_image_ids = np.asarray(image_ids, dtype=np.int32)[order]
        sorted_tp = np.asarray(tps, dtype=np.float64)[order]
        sorted_fp = np.asarray(fps, dtype=np.float64)[order]
    else:
        sorted_image_ids = np.asarray([], dtype=np.int32)
        sorted_tp = np.asarray([], dtype=np.float64)
        sorted_fp = np.asarray([], dtype=np.float64)
    return {
        "image_ids": sorted_image_ids,
        "tp": sorted_tp,
        "fp": sorted_fp,
        "tp50_by_image": tp50_by_image,
        "fp50_by_image": fp50_by_image,
    }


def transient_prediction_cache(bundle: PredictionBundle, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{bundle.run['run_id']}_all_modal_prediction_cache.jsonl"
    h = hashlib.sha256()
    rows = 0
    with path.open("w", encoding="utf-8") as f:
        for image_index, (pred, target, info) in enumerate(zip(bundle.predictions, bundle.targets, bundle.sample_infos)):
            row = {
                "schema": "sample_id, image_index, gt_box_count, pred_boxes_xyxy, pred_scores, pred_labels; detector score threshold already applied",
                "sample_id": Path(info["image_path"]).stem,
                "image_index": image_index,
                "gt_box_count": int(target["boxes"].shape[0]),
                "pred_boxes_xyxy": [[round(float(x), 6) for x in box] for box in pred["boxes"].tolist()],
                "pred_scores": [round(float(x), 8) for x in pred["scores"].tolist()],
                "pred_labels": [int(x) for x in pred["labels"].tolist()],
            }
            line = json.dumps(row, sort_keys=True)
            f.write(line + "\n")
            h.update((line + "\n").encode("utf-8"))
            rows += 1
    size = path.stat().st_size
    digest = h.hexdigest()
    path.unlink()
    return {
        "run_id": bundle.run["run_id"],
        "schema": "JSONL rows with sample_id, image_index, gt_box_count, pred_boxes_xyxy, pred_scores, pred_labels.",
        "rows": rows,
        "sha256_before_deletion": digest,
        "bytes_before_deletion": size,
        "retained_in_git": False,
        "deletion_exclusion_policy": "Transient local prediction cache was hashed, consumed for bootstrap, and deleted before commit.",
        "path_deleted": rel(path),
    }


def split_counts(split_file: Path) -> dict:
    dataset = TriAirDataset(DATA_ROOT, mode="rgbte", split_file=split_file)
    return {
        "split_file": rel(split_file),
        "images": len(dataset),
        "images_with_label_txt": sum(1 for info in dataset.sample_infos if info["label_path"] is not None),
        "images_without_label_txt": sum(1 for info in dataset.sample_infos if info["label_path"] is None),
        "empty_label_txt_files": len(dataset.empty_label_txt_files),
        "gt_boxes": dataset.total_boxes,
    }


def source_lock(actual_env: dict, env_compare: dict) -> dict:
    rows = []

    def add(kind: str, path: Path, note: str) -> None:
        rows.append(
            {
                "kind": kind,
                "path": rel(path),
                "exists": path.is_file(),
                "sha256": sha256_file(path) if path.is_file() else "NA",
                "note": note,
            }
        )

    for path, note in [
        (TRAIN_MANIFEST, "V40-v2 train manifest"),
        (VAL_MANIFEST, "V40-v2 validation manifest used for all post-core evaluations"),
        (GUARD_MANIFEST, "V40 guard manifest recorded as archival/non-test; not evaluated"),
        (CORE_ROOT / "V40_FOUR_RUN_EXECUTION_STATUS.json", "Core four-run completion status"),
        (CORE_ROOT / "v40_four_run_summary.json", "Core four-run summary"),
        (SPLIT_ROOT / "audits" / "v40_split_audit_report.json", "V40-v2 split audit"),
        (SPLIT_ROOT / "reports" / "V40_V2_EXPANDED_ADJACENCY_SPLIT_STATUS.json", "V40-v2 split status"),
        (AMEND_ROOT / "contract" / "v40_compute_minimized_contract_amendment.json", "Compute-minimized amendment"),
        (AMEND_ROOT / "reports" / "V40_COMPUTE_MINIMIZED_CONTRACT_STATUS.json", "Compute-minimized status"),
        (FROZEN_ENV, "Frozen training environment"),
        (ROOT / "rarepdet" / "eval_map.py", "Frozen standardized evaluator"),
        (ROOT / "rarepdet" / "metrics.py", "Project-local metric implementation"),
        (ROOT / "rarepdet" / "data.py", "Detection dataset adapter"),
        (ROOT / "datasets" / "triair_dataset.py", "TriAir dataset loader"),
        (ROOT / "rarepdet" / "models" / "early_fusion_fcos.py", "Detector builders"),
        (ROOT / "rarepdet" / "models" / "repvit_fpn_backbone.py", "Backbone implementations"),
        (Path(__file__).resolve(), "V40 post-core evidence runner"),
    ]:
        add("source_or_manifest", path, note)

    for run in RUNS:
        add("checkpoint", run["weights"], f"Fixed checkpoint for {run['run_id']}")

    write_csv(POST_ROOT / "source_lock" / "source_lock_manifest.csv", rows)
    payload = {
        "generated_at": now(),
        "status": "PASS" if env_compare["status"] == "PASS" else "BLOCKED",
        "git_commit": git_output(["rev-parse", "HEAD"]),
        "runtime_environment": actual_env,
        "frozen_environment": read_json(FROZEN_ENV),
        "environment_comparison": env_compare,
        "source_lock_rows": rows,
    }
    write_json(POST_ROOT / "source_lock" / "source_lock_manifest.json", payload)
    lines = [
        "# V40 Post-Core Source Lock",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Status: `{payload['status']}`",
        f"- Git commit: `{payload['git_commit']}`",
        f"- Runtime environment comparison: `{env_compare['status']}`",
        "",
    ]
    lines.extend(md_table(rows, ["kind", "path", "exists", "sha256", "note"]))
    (POST_ROOT / "source_lock" / "source_lock_manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def run_channel_removal(device: torch.device, dataset: DetectionTriAirDataset, loader: DataLoader) -> tuple[list[dict], dict[str, PredictionBundle]]:
    rows = []
    bundles = {}
    val_hash = sha256_file(VAL_MANIFEST)
    evaluator_hash = sha256_file(ROOT / "rarepdet" / "eval_map.py")
    for run in RUNS:
        print(f"[channel] {run['run_id']}")
        model, checkpoint = load_model(run, device)
        checkpoint_hash = sha256_file(run["weights"])
        for condition, condition_description in CONDITIONS:
            keep = condition == "all_modal"
            metrics, predictions, targets = evaluate_condition(model, loader, device, condition, keep_predictions=keep)
            row = {
                "run_id": run["run_id"],
                "model_group": run["model_group"],
                "model": run["model"],
                "seed": run["seed"],
                "condition": condition,
                "condition_description": condition_description,
                "wording": "synthetic channel removal" if condition != "all_modal" else "all modalities available",
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "ap50": metrics["ap50"],
                "ap75": metrics["ap75"],
                "gt_boxes": metrics["gt_boxes"],
                "predictions": metrics["predictions"],
                "mean_confidence": metrics["mean_confidence"],
                "fps": metrics["fps"],
                "runtime_seconds": metrics["runtime_seconds"],
                "checkpoint_path": rel(run["weights"]),
                "checkpoint_sha256": checkpoint_hash,
                "evaluator_sha256": evaluator_hash,
                "manifest_sha256": val_hash,
                "detector_score_thr": DETECTOR_SCORE_THR,
                "metric_score_thr": METRIC_SCORE_THR,
                "nms_thresh": NMS_THRESH,
                "detections_per_img": DETECTIONS_PER_IMG,
                "limitation": LIMITATION,
            }
            rows.append(row)
            print(
                f"  {condition}: AP50={metrics['ap50']:.6f} AP75={metrics['ap75']:.6f} F1={metrics['f1']:.6f}"
            )
            if keep:
                gt_counts = np.asarray([int(t["boxes"].shape[0]) for t in targets], dtype=np.int32)
                bundles[run["run_id"]] = PredictionBundle(run, predictions, targets, list(dataset.dataset.sample_infos), gt_counts)
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    fields = [
        "run_id",
        "model_group",
        "model",
        "seed",
        "condition",
        "condition_description",
        "wording",
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
        "checkpoint_path",
        "checkpoint_sha256",
        "evaluator_sha256",
        "manifest_sha256",
        "detector_score_thr",
        "metric_score_thr",
        "nms_thresh",
        "detections_per_img",
        "limitation",
    ]
    write_csv(POST_ROOT / "channel_removal" / "channel_removal_per_checkpoint.csv", rows, fields)
    write_json(POST_ROOT / "channel_removal" / "channel_removal_per_checkpoint.json", {"generated_at": now(), "rows": rows})
    return rows, bundles


def aggregate_channel_removal(rows: list[dict]) -> list[dict]:
    agg = []
    for group in ["matched_early", "reliability_p015"]:
        all_mean = {}
        for metric in METRICS:
            values = [float(r[metric]) for r in rows if r["model_group"] == group and r["condition"] == "all_modal"]
            all_mean[metric] = sum(values) / len(values)
        for condition, _ in CONDITIONS:
            condition_rows = [r for r in rows if r["model_group"] == group and r["condition"] == condition]
            for metric in METRICS:
                values = [float(r[metric]) for r in condition_rows]
                mean = sum(values) / len(values)
                agg.append(
                    {
                        "model_group": group,
                        "condition": condition,
                        "metric": metric,
                        "mean": mean,
                        "min": min(values),
                        "max": max(values),
                        "range": max(values) - min(values),
                        "delta_from_all_modal_mean": mean - all_mean[metric],
                        "limitation": LIMITATION,
                    }
                )
    write_csv(POST_ROOT / "channel_removal" / "channel_removal_aggregate.csv", agg)
    write_json(POST_ROOT / "channel_removal" / "channel_removal_aggregate.json", {"generated_at": now(), "limitation": LIMITATION, "rows": agg})
    lines = [
        "# V40 Synthetic Channel Removal",
        "",
        "Required wording: synthetic channel removal.",
        "",
        LIMITATION,
        "",
        "## Aggregate",
        "",
    ]
    lines.extend(md_table(agg, ["model_group", "condition", "metric", "mean", "delta_from_all_modal_mean", "min", "max", "range"]))
    (POST_ROOT / "channel_removal" / "channel_removal_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return agg


def run_efficiency(device: torch.device) -> tuple[list[dict], list[dict]]:
    raw_rows = []
    summary_rows = []
    warmup = 200
    iters = 1000
    trials = 5
    for run in RUNS:
        print(f"[efficiency] {run['run_id']}")
        model, _ = load_model(run, device)
        params, trainable = count_params(model)
        dummy = torch.randn(1, 5, IMG_SIZE, IMG_SIZE, device=device)
        detector_inputs = [dummy[0]]
        flops = try_flops(model, dummy)
        for path_name, fn in [
            ("raw_forward", lambda: model.backbone(dummy)),
            ("detector_inference", lambda: model(detector_inputs)),
        ]:
            trial_rows = []
            for trial in range(1, trials + 1):
                result = measure_callable(fn, 1, device, warmup, iters)
                row = {
                    "run_id": run["run_id"],
                    "model_group": run["model_group"],
                    "model": run["model"],
                    "seed": run["seed"],
                    "checkpoint_sha256": sha256_file(run["weights"]),
                    "path": path_name,
                    "trial": trial,
                    "batch_size": 1,
                    "img_size": IMG_SIZE,
                    "warmup_iters": warmup,
                    "timed_iters": iters,
                    "params": params,
                    "trainable_params": trainable,
                    "fps": result["fps"],
                    "latency_ms_per_img": result["latency_ms_per_img"],
                    "cuda_peak_memory_mb": result["cuda_peak_memory_mb"],
                    "gflops": flops[path_name]["gflops"],
                    "flops_note": flops[path_name]["note"],
                    "boundary": (
                        "raw model forward: model.backbone(dummy_tensor); excludes FCOS head, transform, NMS, and dataloader"
                        if path_name == "raw_forward"
                        else "end-to-end detector inference: FCOS model([dummy_image]); includes transform, backbone, head, NMS/postprocess; excludes dataloader and file IO"
                    ),
                }
                raw_rows.append(row)
                trial_rows.append(row)
                print(f"  {path_name} trial {trial}: {result['latency_ms_per_img']:.3f} ms/img")
            summary_rows.append(
                {
                    "run_id": run["run_id"],
                    "model_group": run["model_group"],
                    "model": run["model"],
                    "seed": run["seed"],
                    "checkpoint_sha256": sha256_file(run["weights"]),
                    "path": path_name,
                    "trials": trials,
                    "warmup_iters": warmup,
                    "timed_iters": iters,
                    "params": params,
                    "trainable_params": trainable,
                    "latency_ms_median": summarize_values([r["latency_ms_per_img"] for r in trial_rows])["median"],
                    "latency_ms_min": summarize_values([r["latency_ms_per_img"] for r in trial_rows])["min"],
                    "latency_ms_max": summarize_values([r["latency_ms_per_img"] for r in trial_rows])["max"],
                    "fps_median": summarize_values([r["fps"] for r in trial_rows])["median"],
                    "fps_min": summarize_values([r["fps"] for r in trial_rows])["min"],
                    "fps_max": summarize_values([r["fps"] for r in trial_rows])["max"],
                    "cuda_peak_memory_mb_max": max(float(r["cuda_peak_memory_mb"]) for r in trial_rows),
                    "gflops": flops[path_name]["gflops"],
                    "flops_note": flops[path_name]["note"],
                    "boundary": trial_rows[0]["boundary"],
                }
            )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    write_csv(POST_ROOT / "efficiency" / "efficiency_raw_trials.csv", raw_rows)
    write_csv(POST_ROOT / "efficiency" / "efficiency_summary.csv", summary_rows)
    write_json(POST_ROOT / "efficiency" / "efficiency_summary.json", {"generated_at": now(), "rows": summary_rows})
    lines = [
        "# V40 Efficiency Measurement",
        "",
        "Protocol: GPU batch size 1, image size 640, torch.inference_mode(), model eval mode, CUDA synchronization, 200 warm-up iterations, five trials of 1000 timed iterations.",
        "",
        "Raw-forward boundary: `model.backbone(dummy_tensor)`; excludes FCOS head, transform, NMS, postprocessing, dataloader, and file IO.",
        "",
        "End-to-end detector boundary: `model([dummy_image])`; includes torchvision FCOS transform, backbone, head, NMS/postprocess; excludes dataloader and file IO.",
        "",
    ]
    lines.extend(md_table(summary_rows))
    (POST_ROOT / "efficiency" / "efficiency_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return raw_rows, summary_rows


def run_bootstrap(bundles: dict[str, PredictionBundle]) -> dict:
    print("[bootstrap] precomputing records")
    cache_manifest = []
    cache_dir = POST_ROOT / "bootstrap" / "_local_prediction_cache"
    for run_id in [r["run_id"] for r in RUNS]:
        cache_manifest.append(transient_prediction_cache(bundles[run_id], cache_dir))
    if cache_dir.exists():
        shutil.rmtree(cache_dir)

    precomputed = {}
    n_images = None
    for run_id, bundle in bundles.items():
        n_images = len(bundle.targets)
        rec50 = precompute_bootstrap_records(bundle, 0.5)
        rec75 = precompute_bootstrap_records(bundle, 0.75)
        precomputed[run_id] = {"ap50": rec50, "ap75": rec75, "gt_counts": bundle.gt_counts.astype(np.float64)}

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    counts_matrix = rng.multinomial(n_images, np.full(n_images, 1.0 / n_images), size=BOOTSTRAP_RESAMPLES)
    resample_rows = []
    for idx, counts in enumerate(counts_matrix, 1):
        per_run_metrics = {}
        for run in RUNS:
            run_id = run["run_id"]
            record = precomputed[run_id]
            total_gt = float(np.dot(record["gt_counts"], counts))
            ap50 = bootstrap_ap(record["ap50"]["image_ids"], record["ap50"]["tp"], record["ap50"]["fp"], counts, total_gt)
            ap75 = bootstrap_ap(record["ap75"]["image_ids"], record["ap75"]["tp"], record["ap75"]["fp"], counts, total_gt)
            tp = float(np.dot(record["ap50"]["tp50_by_image"], counts))
            fp = float(np.dot(record["ap50"]["fp50_by_image"], counts))
            precision = tp / max(tp + fp, 1e-12)
            recall = tp / max(total_gt, 1e-12)
            f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
            per_run_metrics[run_id] = {"ap50": ap50, "ap75": ap75, "f1": f1}
        early = {
            metric: (per_run_metrics["matched_early_seed0"][metric] + per_run_metrics["matched_early_seed2"][metric]) / 2.0
            for metric in ["ap50", "ap75", "f1"]
        }
        relp = {
            metric: (per_run_metrics["reliability_p015_seed0"][metric] + per_run_metrics["reliability_p015_seed2"][metric]) / 2.0
            for metric in ["ap50", "ap75", "f1"]
        }
        row = {"resample_index": idx}
        for metric in ["ap50", "ap75", "f1"]:
            row[f"matched_early_{metric}"] = early[metric]
            row[f"reliability_p015_{metric}"] = relp[metric]
            row[f"diff_reliability_minus_early_{metric}"] = relp[metric] - early[metric]
        resample_rows.append(row)
        if idx % 250 == 0:
            print(f"  bootstrap {idx}/{BOOTSTRAP_RESAMPLES}")

    summary_rows = []
    for metric in ["ap50", "ap75", "f1"]:
        diffs = np.asarray([row[f"diff_reliability_minus_early_{metric}"] for row in resample_rows], dtype=np.float64)
        summary_rows.append(
            {
                "comparison": "reliability_p015_minus_matched_early",
                "metric": metric,
                "resamples": BOOTSTRAP_RESAMPLES,
                "bootstrap_seed": BOOTSTRAP_SEED,
                "resampling_unit": "V40 validation image",
                "mean_difference": float(np.mean(diffs)),
                "median_difference": float(np.median(diffs)),
                "ci95_low_percentile": float(np.percentile(diffs, 2.5)),
                "ci95_high_percentile": float(np.percentile(diffs, 97.5)),
                "interpretation": "descriptive uncertainty evidence only; not used for model selection",
            }
        )

    write_csv(POST_ROOT / "bootstrap" / "bootstrap_resamples.csv", resample_rows)
    write_csv(POST_ROOT / "bootstrap" / "bootstrap_ci_summary.csv", summary_rows)
    write_csv(POST_ROOT / "bootstrap" / "prediction_cache_manifest.csv", cache_manifest)
    payload = {
        "generated_at": now(),
        "protocol": {
            "resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "resampling_unit": "V40 validation image",
            "groups": "each resample computes each fixed checkpoint metric, averages the two checkpoints within each model group, then differences reliability_p015 minus matched_early",
            "empty_gt_images": "retained in the resampling frame; they contribute false positives when predictions are present and zero GT to denominators",
            "metric_implementation": "project-local single-class AP/F1 logic consistent with rarepdet/metrics.py",
            "raw_prediction_cache": "transient local JSONL caches were hashed and deleted before commit",
        },
        "cache_manifest": cache_manifest,
        "ci_summary": summary_rows,
    }
    write_json(POST_ROOT / "bootstrap" / "bootstrap_protocol_and_summary.json", payload)
    lines = [
        "# V40 Bootstrap Inference",
        "",
        f"- Resamples: `{BOOTSTRAP_RESAMPLES}`",
        f"- Bootstrap seed: `{BOOTSTRAP_SEED}`",
        "- Resampling unit: V40 validation image.",
        "- Images with no GT boxes are retained; they contribute false positives when predictions are present and zero GT to denominators.",
        "- Use: descriptive uncertainty evidence only; not used to select or change a model.",
        "",
        "## 95% Percentile Confidence Intervals",
        "",
    ]
    lines.extend(md_table(summary_rows))
    (POST_ROOT / "bootstrap" / "bootstrap_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def render_qualitative(bundles: dict[str, PredictionBundle]) -> dict:
    print("[qualitative] rendering deterministic packet")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as exc:
        raise RuntimeError(f"Pillow is required for qualitative rendering: {exc}") from exc

    first_bundle = bundles["matched_early_seed0"]
    sample_rows = []
    for index, info in enumerate(first_bundle.sample_infos):
        sample_id = Path(info["image_path"]).stem
        key = sha256_text(sample_id)
        sample_rows.append(
            {
                "index": index,
                "sample_id": sample_id,
                "selection_sha256": key,
                "image_path": str(info["image_path"]),
                "label_state": info["label_state"],
                "gt_boxes": int(info["box_count"]),
            }
        )
    selected = sorted(sample_rows, key=lambda row: (row["selection_sha256"], row["sample_id"]))[:8]
    for rank, row in enumerate(selected, 1):
        row["selection_rank"] = rank
        row["selection_rule"] = "sort validation sample_id by SHA-256 and take first eight"

    assets_dir = POST_ROOT / "qualitative" / "review_assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    asset_rows = []
    panel_size = 640
    title_h = 30
    qualitative_dataset = DetectionTriAirDataset(
        DATA_ROOT,
        split_file=str(VAL_MANIFEST),
        mode="rgbte",
        train=False,
    )
    for row in selected:
        idx = int(row["index"])
        target = first_bundle.targets[idx]
        image_tensor, _ = qualitative_dataset[idx]
        rgb = (image_tensor[0:3].clamp(0, 1).permute(1, 2, 0).numpy() * 255.0).astype(np.uint8)
        base = Image.fromarray(rgb).resize((panel_size, panel_size))
        grid = Image.new("RGB", (panel_size * 2, (panel_size + title_h) * 2), "white")
        draw_grid = ImageDraw.Draw(grid)
        for p_i, run in enumerate(RUNS):
            pred = bundles[run["run_id"]].predictions[idx]
            panel = base.copy()
            draw = ImageDraw.Draw(panel)
            sx = panel_size / rgb.shape[1]
            sy = panel_size / rgb.shape[0]
            for box in target["boxes"].tolist():
                x1, y1, x2, y2 = [float(v) for v in box]
                draw.rectangle([x1 * sx, y1 * sy, x2 * sx, y2 * sy], outline=(0, 255, 0), width=2)
            boxes = pred["boxes"]
            scores = pred["scores"]
            labels = pred["labels"]
            keep = (labels == 1) & (scores >= METRIC_SCORE_THR)
            for box, score in zip(boxes[keep].tolist(), scores[keep].tolist()):
                x1, y1, x2, y2 = [float(v) for v in box]
                draw.rectangle([x1 * sx, y1 * sy, x2 * sx, y2 * sy], outline=(255, 220, 0), width=2)
                draw.text((x1 * sx, max(0, y1 * sy - 10)), f"{score:.2f}", fill=(255, 220, 0), font=font)
            xoff = (p_i % 2) * panel_size
            yoff = (p_i // 2) * (panel_size + title_h)
            draw_grid.text(
                (xoff + 4, yoff + 4),
                f"{row['sample_id']} | {run['run_id']} | GT green | pred>=0.50 yellow",
                fill=(0, 0, 0),
                font=font,
            )
            grid.paste(panel, (xoff, yoff + title_h))
        asset_path = assets_dir / f"v40_qualitative_{int(row['selection_rank']):02d}_{row['sample_id']}.png"
        grid.save(asset_path)
        asset_rows.append(
            {
                "selection_rank": row["selection_rank"],
                "sample_id": row["sample_id"],
                "asset_path": rel(asset_path),
                "asset_sha256": sha256_file(asset_path),
                "visual_convention": "RGB image; GT boxes green; predictions with score >= 0.50 yellow; all-modal only",
                "claims": "none; review packet only",
            }
        )

    write_csv(POST_ROOT / "qualitative" / "qualitative_selection_manifest.csv", selected)
    write_csv(POST_ROOT / "qualitative" / "qualitative_asset_manifest.csv", asset_rows)
    payload = {
        "generated_at": now(),
        "selection_rule": "sort stable validation sample IDs on SHA-256 and take the first eight",
        "not_selected_by": ["appearance", "score", "error", "confidence", "loss", "result_quality"],
        "display_threshold": METRIC_SCORE_THR,
        "assets": asset_rows,
    }
    write_json(POST_ROOT / "qualitative" / "qualitative_packet.json", payload)
    lines = [
        "# V40 Deterministic Qualitative Review Packet",
        "",
        "This packet is non-cherry-picked and is not a manuscript figure set.",
        "",
        "Selection: stable validation sample IDs sorted by SHA-256; first eight rows retained.",
        "",
        "Visual convention: RGB image, GT boxes in green, all-modal predictions with score >= 0.50 in yellow.",
        "",
        "No qualitative claims are made in this packet.",
        "",
        "## Selection",
        "",
    ]
    lines.extend(md_table(selected, ["selection_rank", "sample_id", "selection_sha256", "label_state", "gt_boxes", "selection_rule"]))
    lines.extend(["", "## Assets", ""])
    lines.extend(md_table(asset_rows))
    (POST_ROOT / "qualitative" / "qualitative_packet.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def build_provenance_and_index(stage_status: dict) -> tuple[list[dict], dict]:
    print("[provenance] building index and ledger")
    evidence_rows = []
    for path in sorted(list(POST_ROOT.rglob("*")) + list(READINESS_ROOT.rglob("*"))):
        if path.is_file():
            evidence_rows.append(
                {
                    "path": rel(path),
                    "sha256": sha256_file(path),
                    "bytes": path.stat().st_size,
                    "status": "created",
                }
            )
    for path in [
        SPLIT_ROOT / "audits" / "v40_split_audit_report.json",
        AMEND_ROOT / "contract" / "v40_compute_minimized_contract_amendment.json",
        CORE_ROOT / "v40_four_run_summary.json",
    ]:
        evidence_rows.append({"path": rel(path), "sha256": sha256_file(path), "bytes": path.stat().st_size, "status": "source"})
    write_csv(POST_ROOT / "reproducibility" / "v40_evidence_index.csv", evidence_rows)

    split_rows = []
    for name, path in [("train", TRAIN_MANIFEST), ("validation", VAL_MANIFEST), ("guard_archival_non_test", GUARD_MANIFEST)]:
        if path.is_file():
            counts = split_counts(path)
            counts["split"] = name
            split_rows.append(counts)
    write_csv(POST_ROOT / "provenance" / "triair_provenance_ledger.csv", split_rows)
    provenance = {
        "generated_at": now(),
        "dataset_formal_name": "TriAir",
        "local_alias": str(DATA_ROOT),
        "verified_from_local_files": split_rows,
        "author_held_provenance_evidence": "local dataset root and repository split manifests only",
        "verified_license_access_facts": "unverified in this task",
        "public_shareable_assets": "source code, split manifests, hashes, aggregate reports, rendered review packet; not raw data or weights",
        "unresolved_gaps": [
            "public URL not verified",
            "license not verified",
            "dataset version not verified",
            "redistribution terms not verified",
            "temporal metadata not independently verified",
        ],
        "guard_policy": "guard manifest is archival/non-test and was not evaluated",
    }
    write_json(POST_ROOT / "provenance" / "triair_provenance_ledger.json", provenance)
    lines = [
        "# TriAir Provenance and Availability Ledger",
        "",
        "- Dataset formal name: TriAir",
        f"- Local alias: `{DATA_ROOT}`",
        "- Verified license/access facts: unverified in this task.",
        "- Guard policy: guard is archival/non-test and was not evaluated.",
        "",
        "## Split Counts",
        "",
    ]
    lines.extend(md_table(split_rows, ["split", "images", "images_with_label_txt", "images_without_label_txt", "empty_label_txt_files", "gt_boxes", "split_file"]))
    lines.extend(["", "## Unresolved Gaps", ""])
    for item in provenance["unresolved_gaps"]:
        lines.append(f"- {item}")
    (POST_ROOT / "provenance" / "triair_provenance_ledger.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    index_payload = {
        "generated_at": now(),
        "stage_status": stage_status,
        "evidence_rows": evidence_rows,
        "guard_policy": "archival/non-test; no guard evaluation was run",
        "interpretation": "V40-v2 is a candidate validation-only evidence package.",
    }
    write_json(POST_ROOT / "reproducibility" / "v40_evidence_index.json", index_payload)
    lines = [
        "# V40 Evidence Index",
        "",
        "V40-v2 is recorded as a candidate validation-only evidence package. Guard remains archival/non-test.",
        "",
    ]
    lines.extend(md_table(evidence_rows, ["path", "sha256", "bytes", "status"]))
    (POST_ROOT / "reproducibility" / "v40_evidence_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return evidence_rows, provenance


def build_readiness(stage_status: dict) -> str:
    print("[readiness] building report")
    requirements = [
        ("V40-v2 split audit pass", stage_status.get("split_audit") == "PASS"),
        ("contract/amendment pass", stage_status.get("contract") == "PASS"),
        ("all four core runs completed", stage_status.get("core_runs") == "PASS"),
        ("source lock complete", stage_status.get("stage_a_source_lock") == "PASS"),
        ("channel removal complete", stage_status.get("stage_b_channel_removal") == "PASS"),
        ("efficiency complete", stage_status.get("stage_c_efficiency") == "PASS"),
        ("bootstrap complete", stage_status.get("stage_d_bootstrap") == "PASS"),
        ("deterministic qualitative packet complete", stage_status.get("stage_e_qualitative") == "PASS"),
        ("reproducibility/provenance complete", stage_status.get("stage_f_reproducibility_provenance") == "PASS"),
        ("limitations registered", True),
    ]
    ready = all(ok for _, ok in requirements)
    status = "PRE_MANUSCRIPT_VALIDATION_ONLY_READY" if ready else "PRE_MANUSCRIPT_NOT_READY"
    rows = [
        {
            "requirement": requirement,
            "status": "PASS" if ok else "FAIL",
            "notes": "validation-only manuscript scope" if ok else "required before readiness",
        }
        for requirement, ok in requirements
    ]
    write_csv(READINESS_ROOT / "readiness_matrix.csv", rows)
    limitation_lines = [
        "# Limitation Register",
        "",
        "- V40-v2 is validation-only evidence, not an independent test.",
        "- Guard data is archival/non-test and was not evaluated.",
        "- Reliability p=0.15 was pre-specified before V40 results; no V40 dropout sweep or V40-optimal dropout claim is supported.",
        "- Synthetic channel removal is deterministic zero-channel input and does not emulate measured physical sensor faults or real cross-sensor deployment failures.",
        "- Bootstrap intervals are descriptive uncertainty evidence only and are not model-selection tests.",
        "- Dataset public URL, license, version, redistribution terms, and temporal metadata remain unresolved unless separately verified.",
        "- No external-data generalization claim is supported.",
    ]
    (READINESS_ROOT / "limitation_register.md").write_text("\n".join(limitation_lines) + "\n", encoding="utf-8")
    evidence_index_path = POST_ROOT / "reproducibility" / "v40_evidence_index.csv"
    if evidence_index_path.is_file():
        shutil.copyfile(evidence_index_path, READINESS_ROOT / "evidence_index.csv")
    payload = {
        "generated_at": now(),
        "status": status,
        "stage_status": stage_status,
        "readiness_matrix": rows,
        "permitted_scope": "validation-only manuscript drafting",
        "not_permitted_claims": ["independent testing", "external generalization", "V40-optimal dropout", "physical sensor failure robustness"],
    }
    write_json(READINESS_ROOT / "readiness_report.json", payload)
    lines = [
        "# Pre-Manuscript Readiness Report",
        "",
        f"- Final status: `{status}`",
        "- Permitted scope: validation-only manuscript drafting.",
        "- Not permitted: independent-test, external-generalization, V40-optimal-dropout, or physical-sensor-failure claims.",
        "",
        "## Matrix",
        "",
    ]
    lines.extend(md_table(rows))
    (READINESS_ROOT / "readiness_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(POST_ROOT / "readiness" / "readiness_status.json", payload)
    return status


def build_reports(channel_agg: list[dict], efficiency_rows: list[dict], bootstrap_payload: dict, qualitative_payload: dict, final_status: str) -> None:
    summary = {
        "generated_at": now(),
        "status": "V40_POST_CORE_EVIDENCE_COMPLETE" if final_status == "PRE_MANUSCRIPT_VALIDATION_ONLY_READY" else "V40_POST_CORE_EVIDENCE_INCOMPLETE",
        "readiness_status": final_status,
        "channel_removal_aggregate": channel_agg,
        "efficiency_summary": efficiency_rows,
        "bootstrap_ci_summary": bootstrap_payload["ci_summary"],
        "qualitative_assets": qualitative_payload["assets"],
        "prohibited_work": {
            "training": False,
            "tuning": False,
            "p000_or_p020_run": False,
            "manuscript_work": False,
            "external_data": False,
            "guard_evaluation": False,
            "dronevehicle": False,
            "finish_task": False,
        },
    }
    write_json(POST_ROOT / "reports" / "v40_post_core_evidence_report.json", summary)
    lines = [
        "# V40 Post-Core Evidence Report",
        "",
        f"- Status: `{summary['status']}`",
        f"- Readiness: `{final_status}`",
        "- No new training, tuning, p=0.00/p=0.20 run, manuscript work, external data, guard evaluation, DroneVehicle work, or finish_task.ps1 occurred.",
        "",
        "## Channel Removal Aggregate",
        "",
    ]
    lines.extend(md_table(channel_agg, ["model_group", "condition", "metric", "mean", "delta_from_all_modal_mean"]))
    lines.extend(["", "## Efficiency Summary", ""])
    lines.extend(md_table(efficiency_rows, ["run_id", "model_group", "path", "latency_ms_median", "fps_median", "params", "cuda_peak_memory_mb_max", "gflops"]))
    lines.extend(["", "## Bootstrap CI Summary", ""])
    lines.extend(md_table(bootstrap_payload["ci_summary"]))
    lines.extend(["", "## Qualitative Assets", ""])
    lines.extend(md_table(qualitative_payload["assets"], ["selection_rank", "sample_id", "asset_path", "asset_sha256"]))
    (POST_ROOT / "reports" / "v40_post_core_evidence_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    start = time.perf_counter()
    random.seed(BOOTSTRAP_SEED)
    np.random.seed(BOOTSTRAP_SEED)
    torch.manual_seed(BOOTSTRAP_SEED)
    ensure_dirs()

    core_status = read_json(CORE_ROOT / "V40_FOUR_RUN_EXECUTION_STATUS.json")
    split_status = read_json(SPLIT_ROOT / "reports" / "V40_V2_EXPANDED_ADJACENCY_SPLIT_STATUS.json")
    amendment = read_json(AMEND_ROOT / "contract" / "v40_compute_minimized_contract_amendment.json")
    frozen_env = read_json(FROZEN_ENV)
    actual_env = runtime_environment()
    env_compare = compare_environment(actual_env, frozen_env)

    stage_status = {
        "split_audit": "PASS" if split_status.get("status") == "V40_V2_READY_FOR_FROZEN_RERUN" else "FAIL",
        "contract": "PASS" if amendment.get("status") == "V40_COMPUTE_MINIMIZED_CONTRACT_READY" else "FAIL",
        "core_runs": "PASS" if core_status.get("status") == "V40_FOUR_RUN_EXECUTION_COMPLETE" else "FAIL",
    }
    if env_compare["status"] != "PASS":
        write_json(POST_ROOT / "reports" / "V40_POST_CORE_EVIDENCE_INCOMPLETE.json", {"status": "V40_POST_CORE_EVIDENCE_INCOMPLETE", "reason": "runtime environment mismatch", "environment_comparison": env_compare})
        return 2
    for run in RUNS:
        if not run["weights"].is_file():
            write_json(POST_ROOT / "reports" / "V40_POST_CORE_EVIDENCE_INCOMPLETE.json", {"status": "V40_POST_CORE_EVIDENCE_INCOMPLETE", "reason": f"missing checkpoint {run['weights']}"})
            return 2

    source_lock(actual_env, env_compare)
    stage_status["stage_a_source_lock"] = "PASS"

    device = pick_device()
    dataset, loader = make_loader()
    channel_rows, bundles = run_channel_removal(device, dataset, loader)
    channel_agg = aggregate_channel_removal(channel_rows)
    stage_status["stage_b_channel_removal"] = "PASS" if len(channel_rows) == 16 else "FAIL"

    _, efficiency_summary = run_efficiency(device)
    stage_status["stage_c_efficiency"] = "PASS" if len(efficiency_summary) == 8 else "FAIL"

    bootstrap_payload = run_bootstrap(bundles)
    stage_status["stage_d_bootstrap"] = "PASS" if len(bootstrap_payload["ci_summary"]) == 3 else "FAIL"

    qualitative_payload = render_qualitative(bundles)
    stage_status["stage_e_qualitative"] = "PASS" if len(qualitative_payload["assets"]) == 8 else "FAIL"

    build_provenance_and_index(stage_status)
    stage_status["stage_f_reproducibility_provenance"] = "PASS"

    final_status = build_readiness(stage_status)
    stage_status["stage_g_readiness"] = "PASS" if final_status == "PRE_MANUSCRIPT_VALIDATION_ONLY_READY" else "FAIL"

    # Rebuild the evidence index after readiness files exist.
    build_provenance_and_index(stage_status)
    final_status = build_readiness(stage_status)
    build_reports(channel_agg, efficiency_summary, bootstrap_payload, qualitative_payload, final_status)

    status_payload = {
        "status": "V40_POST_CORE_EVIDENCE_COMPLETE" if final_status == "PRE_MANUSCRIPT_VALIDATION_ONLY_READY" else "V40_POST_CORE_EVIDENCE_INCOMPLETE",
        "readiness_status": final_status,
        "generated_at": now(),
        "runtime_seconds": time.perf_counter() - start,
        "stage_status": stage_status,
        "prohibited_work": {
            "training": False,
            "tuning": False,
            "p000_or_p020_run": False,
            "manuscript_work": False,
            "external_data": False,
            "guard_evaluation": False,
            "dronevehicle": False,
            "finish_task": False,
        },
    }
    write_json(POST_ROOT / "reports" / "V40_POST_CORE_EVIDENCE_STATUS.json", status_payload)
    print(json.dumps(status_payload, indent=2, sort_keys=True))
    return 0 if status_payload["status"] == "V40_POST_CORE_EVIDENCE_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
