#!/usr/bin/env python
"""Run the frozen V72 naive-grid MM-UAV external-domain stress test."""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import math
import statistics
import subprocess
import sys
import time
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import numpy as np
import torch
from pycocotools.cocoeval import COCOeval
from torch.utils.data import DataLoader


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import (  # noqa: E402
    MMUAVFeatureAlignmentDataset,
    collate_fn,
)
from rarepdet import coco_metrics  # noqa: E402
from rarepdet.models.early_fusion_fcos import build_detector  # noqa: E402
from rarepdet.tools import run_v71_mmuav_existing_devval_zero_shot as v71  # noqa: E402


RUN_DIR = ROOT / "runs/v72_mmuav_naive_grid_external_domain_stress_test"
STARTING_COMMIT = "9dcd0806032ec296703805121c38584d85ee6621"
SCIENTIFIC_LABEL = (
    "zero-shot external-domain stress test on the exposed MM-UAV devval split "
    "using a naive normalized-grid five-channel adapter"
)
METRICS = ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tensor_sha256(tensor: torch.Tensor) -> str:
    value = tensor.detach().cpu().contiguous()
    digest = hashlib.sha256()
    digest.update(f"{value.dtype}|{tuple(value.shape)}|".encode())
    digest.update(value.reshape(-1).view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def write_json(name: str, value: object) -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(name: str) -> object:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def naive_grid_adapter(sample: dict[str, object]) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    rgb = sample["rgb"]
    ir = sample["ir"]
    event = sample["event"]
    if not isinstance(rgb, torch.Tensor) or not isinstance(ir, torch.Tensor) or not isinstance(event, torch.Tensor):
        raise TypeError("Decoded modalities must be tensors")
    if tuple(rgb.shape) != (3, 640, 640) or tuple(ir.shape) != (1, 640, 640) or tuple(event.shape) != (1, 640, 640):
        raise ValueError(f"Unexpected modality shapes: {tuple(rgb.shape)}, {tuple(ir.shape)}, {tuple(event.shape)}")
    image = torch.cat((rgb, ir, event), dim=0)
    if image.dtype != torch.float32 or not torch.isfinite(image).all():
        raise ValueError("Adapter output must be finite float32")
    if image.min().item() < 0.0 or image.max().item() > 1.0:
        raise ValueError("Adapter output escaped frozen [0, 1] scaling")
    target = sample["target_rgb"]
    boxes = target["boxes"]
    labels = target["labels"]
    if not torch.isfinite(boxes).all() or (boxes[:, 2:] <= boxes[:, :2]).any():
        raise ValueError("RGB target contains non-finite or invalid boxes")
    return image, {"boxes": boxes, "labels": labels}


def build_model(model_type: str, checkpoint_path: Path, device: torch.device):
    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    model = build_detector(
        model_type,
        img_size=640,
        score_thresh=0.001,
        nms_thresh=0.6,
        detections_per_img=100,
    )
    incompatible = model.load_state_dict(payload["model_state"], strict=True)
    if incompatible.missing_keys or incompatible.unexpected_keys:
        raise RuntimeError(f"Strict load failed: {incompatible}")
    del payload
    model.eval()
    model.to(device)
    return model


def full_coco_metrics(predictions: list[dict[str, torch.Tensor]], targets: list[dict[str, torch.Tensor]]) -> dict[str, object]:
    dataset, detections = coco_metrics._build_coco_inputs(
        predictions,
        targets,
        foreground_label=1,
        score_thresh=0.0,
        max_detections=100,
    )
    quiet = StringIO()
    with redirect_stdout(quiet):
        ground_truth = coco_metrics.COCO()
        ground_truth.dataset = dataset
        ground_truth.createIndex()
        detection_api = ground_truth.loadRes(detections) if detections else coco_metrics._empty_detection_api(dataset)
        evaluator = COCOeval(ground_truth, detection_api, iouType="bbox")
        evaluator.params.imgIds = [image["id"] for image in dataset["images"]]
        evaluator.params.catIds = [1]
        evaluator.params.iouThrs = np.asarray(coco_metrics.COCO_IOU_THRESHOLDS, dtype=np.float64)
        evaluator.params.recThrs = np.asarray(coco_metrics.COCO_RECALL_THRESHOLDS, dtype=np.float64)
        evaluator.params.maxDets = [1, 10, 100]
        evaluator.evaluate()
        evaluator.accumulate()
    precision = evaluator.eval["precision"][:, :, 0, 0, 2]
    ap_by_iou = {
        f"{threshold:.2f}": coco_metrics._mean_valid(precision[index])
        for index, threshold in enumerate(coco_metrics.COCO_IOU_THRESHOLDS)
    }
    recall = evaluator.eval["recall"][:, 0, 0, :]
    result = {
        "ap50_95": float(np.mean(list(ap_by_iou.values()))),
        "ap50": ap_by_iou["0.50"],
        "ap75": ap_by_iou["0.75"],
        "ar1": coco_metrics._mean_valid(recall[:, 0]),
        "ar10": coco_metrics._mean_valid(recall[:, 1]),
        "ar100": coco_metrics._mean_valid(recall[:, 2]),
        "images": len(dataset["images"]),
        "gt_boxes": len(dataset["annotations"]),
        "detections": len(detections),
    }
    if not all(math.isfinite(float(result[key])) for key in METRICS):
        raise RuntimeError("COCO evaluator returned non-finite metrics")
    return result


def summarize(values: list[float]) -> dict[str, float]:
    if len(values) != 3:
        raise ValueError("V72 descriptive summaries require exactly three seeds")
    return {
        "mean": statistics.mean(values),
        "sample_std": statistics.stdev(values),
        "minimum": min(values),
        "maximum": max(values),
    }


def aggregate_records(records: list[dict[str, object]]) -> tuple[dict[str, object], list[dict[str, object]]]:
    by_key = {(record["method"], int(record["seed"])): record for record in records}
    if set(by_key) != {(method, seed) for method in ("matched_early", "reliability_p015") for seed in (0, 1, 2)}:
        raise ValueError("Expected one complete record for each of six method/seed pairs")
    methods = {}
    for method in ("matched_early", "reliability_p015"):
        methods[method] = {
            metric: summarize([float(by_key[(method, seed)][metric]) for seed in (0, 1, 2)])
            for metric in METRICS
        }
    paired = []
    for seed in (0, 1, 2):
        early = by_key[("matched_early", seed)]
        reliability = by_key[("reliability_p015", seed)]
        row = {"seed": seed}
        for metric in METRICS:
            row[metric] = float(reliability[metric]) - float(early[metric])
        paired.append(row)
    paired_summary = {
        metric: summarize([float(row[metric]) for row in paired])
        for metric in METRICS
    }
    return {"methods": methods, "paired_reliability_minus_early": paired_summary}, paired


def source_lock() -> dict[str, object]:
    paths = (
        "rarepdet/tools/run_v72_mmuav_naive_grid_stress_test.py",
        "tests/test_v72_mmuav_naive_grid_stress_test.py",
        "rarepdet/tools/run_v71_mmuav_existing_devval_zero_shot.py",
        "datasets/mmuav_feature_alignment_dataset.py",
        "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/repvit_fpn_backbone.py",
        "rarepdet/coco_metrics.py",
    )
    return {
        "starting_commit": STARTING_COMMIT,
        "v71_completion_is_ancestor": True,
        "clean_execution_worktree_at_start": True,
        "source_hashes": {path: sha256(ROOT / path) for path in paths},
    }


def prepare(checkpoint_repo: Path) -> None:
    if git("rev-parse", "HEAD") != STARTING_COMMIT:
        raise RuntimeError("Unexpected V72 starting commit")
    manifest_lock = v71.lock_manifest()
    checkpoint_manifest, checkpoint_verification = v71.verify_checkpoints(checkpoint_repo)
    dataset = MMUAVFeatureAlignmentDataset(v71.MANIFEST, 640, validate_paths=True)
    first = dataset[0]
    image_a, target_a = naive_grid_adapter(first)
    image_b, target_b = naive_grid_adapter(dataset[0])
    if not torch.equal(image_a, image_b) or not torch.equal(target_a["boxes"], target_b["boxes"]):
        raise RuntimeError("Real-row adapter fixture is not deterministic")
    synthetic = {
        "rgb": torch.arange(3 * 640 * 640, dtype=torch.float32).reshape(3, 640, 640) % 256 / 255,
        "ir": torch.full((1, 640, 640), 0.25),
        "event": torch.full((1, 640, 640), 0.75),
        "target_rgb": {"boxes": torch.tensor([[1.0, 2.0, 30.0, 40.0]]), "labels": torch.tensor([1])},
    }
    synthetic_image, synthetic_target = naive_grid_adapter(synthetic)
    adapter_tests = {
        "status": "PASS",
        "real_row_index": 0,
        "real_row_output_sha256": tensor_sha256(image_a),
        "real_row_box_sha256": tensor_sha256(target_a["boxes"]),
        "synthetic_output_sha256": tensor_sha256(synthetic_image),
        "synthetic_box_sha256": tensor_sha256(synthetic_target["boxes"]),
        "repeat_exact_equal": True,
        "output_shape": list(image_a.shape),
        "output_dtype": str(image_a.dtype),
        "output_finite": True,
        "physical_registration_asserted": False,
    }
    protocol = {
        "task": "V72_MMUAV_EXISTING_DEVVAL_TRIAIR_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST",
        "starting_commit": STARTING_COMMIT,
        "scientific_label": SCIENTIFIC_LABEL,
        "manifest_rows": 1845,
        "checkpoint_count": 6,
        "smoke_rows": 8,
        "adapter": "V53 independent letterbox to 640x640 then RGB+IR+event concatenation",
        "physical_registration_asserted": False,
        "score_threshold": 0.001,
        "nms_threshold": 0.6,
        "maximum_detections": 100,
        "evaluation_attempt_limit_per_checkpoint": 1,
        "training_adaptation_calibration_or_tuning": False,
    }
    write_json("protocol.json", protocol)
    (RUN_DIR / "protocol.md").write_text(
        "# V72 Naive-Grid External-Domain Stress Test\n\n"
        f"Scientific label: `{SCIENTIFIC_LABEL}`.\n\n"
        "RGB, IR, and event are decoded and independently letterboxed to 640 x 640 using the frozen "
        "V53 implementation, then concatenated as five channels. RGB annotation geometry is retained. "
        "This normalized-grid assumption does not establish physical cross-modal pixel registration.\n",
        encoding="utf-8",
    )
    write_json("source_lock.json", source_lock())
    write_json("devval_manifest_lock.json", manifest_lock)
    write_json("triair_checkpoint_manifest.json", {"count": 6, "entries": checkpoint_manifest})
    write_json("triair_checkpoint_verification.json", {
        "status": "PASS_6_OF_6_STRICT_CPU_LOAD",
        "entries": checkpoint_verification,
        "mmuav_trained_checkpoints_used": False,
        "softplus_wrapper_used": False,
    })
    write_json("adapter_contract.json", {
        "status": "FROZEN",
        "source_decoder_and_letterbox": "datasets/mmuav_feature_alignment_dataset.py",
        "branch_output_size": [640, 640],
        "channel_order": ["rgb_r", "rgb_g", "rgb_b", "ir_grayscale", "event_grayscale"],
        "dtype": "torch.float32",
        "range": [0.0, 1.0],
        "interpolation": "bilinear_align_corners_false",
        "padding": "zero_centered_letterbox",
        "box_geometry": "RGB letterbox transform only",
        "randomness": False,
        "learned_alignment": False,
        "physical_registration_asserted": False,
        "source_sha256": sha256(ROOT / "datasets/mmuav_feature_alignment_dataset.py"),
        "adapter_function_source_sha256": sha256(ROOT / "rarepdet/tools/run_v72_mmuav_naive_grid_stress_test.py"),
    })
    write_json("adapter_determinism_tests.json", adapter_tests)
    write_json("class_ontology_mapping.json", {
        "status": "FROZEN",
        "provider_rgb_category": "drone",
        "torchvision_foreground_label": 1,
        "background_label": 0,
        "single_vehicle_class_evaluation": True,
        "source": "V65-V67 frozen MM-UAV RGB target contract",
    })
    write_json("evaluator_contract.json", {
        "status": "FROZEN",
        "backend": "pycocotools.cocoeval.COCOeval",
        "score_threshold": 0.001,
        "nms_threshold": 0.6,
        "maximum_detections": [1, 10, 100],
        "iou_thresholds": list(coco_metrics.COCO_IOU_THRESHOLDS),
        "recall_threshold_count": len(coco_metrics.COCO_RECALL_THRESHOLDS),
        "metrics": list(METRICS),
        "source_sha256": sha256(ROOT / "rarepdet/coco_metrics.py"),
    })
    write_json("claim_boundary.json", {
        "scientific_label": SCIENTIFIC_LABEL,
        "previously_exposed_devval": True,
        "independent_or_blind_external_test": False,
        "official_test_performance": False,
        "physical_multimodal_registration": False,
        "public_or_manuscript_reporting_authorized": False,
    })
    write_json("attempt_ledger.json", {
        "status": "PREPARED",
        "smoke_attempts": 0,
        "checkpoint_attempts": {item["opaque_id"]: [] for item in v71.CHECKPOINTS},
    })
    write_json("smoke_test_summary.json", {"status": "PENDING", "rows": 8, "attempts": 0})
    write_json("per_checkpoint_metrics.json", {"status": "PENDING", "records": []})
    with (RUN_DIR / "per_checkpoint_metrics.csv").open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerow(
            ["method", "seed", *METRICS, "prediction_count", "images_with_predictions",
             "images_without_predictions", "finite_decoded_boxes", "valid_decoded_boxes",
             "wall_clock_seconds", "peak_gpu_memory_mib", "attempt_count"]
        )
    write_json("paired_seed_comparison.json", {"status": "PENDING", "records": []})
    with (RUN_DIR / "paired_seed_comparison.csv").open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerow(["seed", *METRICS])
    print(json.dumps({"status": "V72_PREPARED", "manifest_rows": len(dataset), "checkpoints": 6}, indent=2))


def validate_prediction(prediction: dict[str, torch.Tensor]) -> tuple[int, int]:
    boxes, scores, labels = prediction["boxes"], prediction["scores"], prediction["labels"]
    finite = (
        torch.isfinite(boxes).all(dim=1)
        & torch.isfinite(scores)
        & torch.isfinite(labels.float())
    )
    valid = finite & (boxes[:, 2] > boxes[:, 0]) & (boxes[:, 3] > boxes[:, 1])
    if not finite.all() or not valid.all():
        raise RuntimeError("Model returned non-finite or invalid decoded boxes")
    return int(finite.sum().item()), int(valid.sum().item())


def smoke(checkpoint_repo: Path, device: torch.device) -> None:
    ledger = read_json("attempt_ledger.json")
    if ledger["smoke_attempts"] != 0:
        raise RuntimeError("V72 smoke pass already attempted")
    ledger["smoke_attempts"] = 1
    ledger["status"] = "SMOKE_RUNNING"
    write_json("attempt_ledger.json", ledger)
    item = v71.CHECKPOINTS[0]
    dataset = MMUAVFeatureAlignmentDataset(v71.MANIFEST, 640, validate_paths=False)
    model = build_model(item["model_type"], checkpoint_repo / item["relative_path"], device)
    records = []
    try:
        torch.cuda.reset_peak_memory_stats(device)
        with torch.inference_mode():
            for index in range(8):
                image, target = naive_grid_adapter(dataset[index])
                output = model([image.to(device)])[0]
                finite, valid = validate_prediction(output)
                records.append({
                    "index": index,
                    "input_sha256": tensor_sha256(image),
                    "target_boxes": int(target["boxes"].shape[0]),
                    "predictions": int(output["boxes"].shape[0]),
                    "finite_decoded_boxes": finite,
                    "valid_decoded_boxes": valid,
                })
        summary = {
            "status": "PASS",
            "attempts": 1,
            "rows": 8,
            "checkpoint": item["opaque_id"],
            "metrics_computed": False,
            "records": records,
            "all_finite_and_valid": True,
            "peak_gpu_memory_mib": torch.cuda.max_memory_allocated(device) / (1024 ** 2),
        }
        write_json("smoke_test_summary.json", summary)
        ledger["status"] = "SMOKE_COMPLETE"
        write_json("attempt_ledger.json", ledger)
    except Exception as error:
        write_json("smoke_test_summary.json", {
            "status": "FAILED",
            "attempts": 1,
            "rows_completed": len(records),
            "error": f"{type(error).__name__}: {error}",
            "metrics_computed": False,
        })
        ledger["status"] = "SMOKE_FAILED"
        write_json("attempt_ledger.json", ledger)
        raise
    finally:
        del model
        torch.cuda.empty_cache()
        gc.collect()


def evaluate_one(
    item: dict[str, object],
    checkpoint_repo: Path,
    dataset: MMUAVFeatureAlignmentDataset,
    device: torch.device,
    batch_size: int,
) -> dict[str, object]:
    ledger = read_json("attempt_ledger.json")
    attempts = ledger["checkpoint_attempts"][item["opaque_id"]]
    if attempts:
        raise RuntimeError(f"Checkpoint already attempted: {item['opaque_id']}")
    attempt = {
        "attempt": 1,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "RUNNING",
        "completed_rows": 0,
        "failure_reason": None,
    }
    attempts.append(attempt)
    ledger["status"] = f"EVALUATING_{item['opaque_id']}"
    write_json("attempt_ledger.json", ledger)

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        collate_fn=collate_fn,
        pin_memory=True,
    )
    model = build_model(item["model_type"], checkpoint_repo / item["relative_path"], device)
    predictions: list[dict[str, torch.Tensor]] = []
    targets: list[dict[str, torch.Tensor]] = []
    prediction_count = 0
    images_with_predictions = 0
    finite_boxes = 0
    valid_boxes = 0
    started = time.perf_counter()
    torch.cuda.reset_peak_memory_stats(device)
    try:
        with torch.inference_mode():
            for batch in loader:
                adapted = [naive_grid_adapter(sample) for sample in batch]
                images = [image.to(device, non_blocking=True) for image, _ in adapted]
                outputs = model(images)
                for output, (_, target) in zip(outputs, adapted):
                    finite, valid = validate_prediction(output)
                    cpu_output = {key: value.detach().cpu() for key, value in output.items()}
                    predictions.append(cpu_output)
                    targets.append({key: value.detach().cpu() for key, value in target.items()})
                    count = int(cpu_output["boxes"].shape[0])
                    prediction_count += count
                    images_with_predictions += int(count > 0)
                    finite_boxes += finite
                    valid_boxes += valid
                attempt["completed_rows"] = len(predictions)
                if len(predictions) % 100 < len(batch):
                    write_json("attempt_ledger.json", ledger)
                    print(f"{item['opaque_id']}: {len(predictions)}/1845", flush=True)
        if len(predictions) != 1845:
            raise RuntimeError(f"Incomplete evaluation: {len(predictions)}/1845")
        torch.cuda.synchronize(device)
        elapsed = time.perf_counter() - started
        metrics = full_coco_metrics(predictions, targets)
        record = {
            "method": item["method"],
            "seed": item["seed"],
            "opaque_id": item["opaque_id"],
            **{key: metrics[key] for key in METRICS},
            "images": metrics["images"],
            "ground_truth_boxes": metrics["gt_boxes"],
            "prediction_count": prediction_count,
            "images_with_predictions": images_with_predictions,
            "images_without_predictions": 1845 - images_with_predictions,
            "finite_decoded_boxes": finite_boxes,
            "valid_decoded_boxes": valid_boxes,
            "wall_clock_seconds": elapsed,
            "peak_gpu_memory_mib": torch.cuda.max_memory_allocated(device) / (1024 ** 2),
            "attempt_count": 1,
            "failure_reason": None,
        }
        attempt["status"] = "COMPLETE"
        attempt["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        attempt["metric_record_complete"] = True
        ledger["status"] = f"COMPLETE_{item['opaque_id']}"
        write_json("attempt_ledger.json", ledger)
        return record
    except Exception as error:
        attempt["status"] = "FAILED"
        attempt["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        attempt["failure_reason"] = f"{type(error).__name__}: {error}"
        attempt["metric_record_complete"] = False
        ledger["status"] = f"FAILED_{item['opaque_id']}"
        write_json("attempt_ledger.json", ledger)
        raise
    finally:
        del model, predictions, targets
        torch.cuda.empty_cache()
        gc.collect()


def write_metrics(records: list[dict[str, object]]) -> None:
    write_json("per_checkpoint_metrics.json", {"status": "COMPLETE", "records": records})
    columns = [
        "method", "seed", *METRICS, "prediction_count", "images_with_predictions",
        "images_without_predictions", "finite_decoded_boxes", "valid_decoded_boxes",
        "wall_clock_seconds", "peak_gpu_memory_mib", "attempt_count",
    ]
    with (RUN_DIR / "per_checkpoint_metrics.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    aggregate, paired = aggregate_records(records)
    write_json("paired_seed_comparison.json", {
        "status": "COMPLETE",
        "records": paired,
        "descriptive_summary": aggregate,
        "significance_tests": False,
    })
    with (RUN_DIR / "paired_seed_comparison.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["seed", *METRICS])
        writer.writeheader()
        writer.writerows(paired)
    write_json("memory_timing_summary.json", {
        "per_checkpoint": [
            {
                "method": row["method"],
                "seed": row["seed"],
                "wall_clock_seconds": row["wall_clock_seconds"],
                "peak_gpu_memory_mib": row["peak_gpu_memory_mib"],
            }
            for row in records
        ],
        "total_wall_clock_seconds": sum(float(row["wall_clock_seconds"]) for row in records),
        "maximum_peak_gpu_memory_mib": max(float(row["peak_gpu_memory_mib"]) for row in records),
    })
    lines = [
        "# V72 Naive-Grid External-Domain Stress-Test Summary",
        "",
        f"Scientific label: `{SCIENTIFIC_LABEL}`.",
        "",
        "| Method | Seed | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in records:
        lines.append(
            f"| {row['method']} | {row['seed']} | {row['ap50_95']:.6f} | {row['ap50']:.6f} | "
            f"{row['ap75']:.6f} | {row['ar1']:.6f} | {row['ar10']:.6f} | {row['ar100']:.6f} |"
        )
    lines.extend([
        "",
        "The adapter independently letterboxes each modality and does not establish physical RGB/IR/event "
        "pixel registration. The split was previously exposed and is not an independent or blind test.",
    ])
    (RUN_DIR / "stress_test_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def execute(checkpoint_repo: Path, batch_size: int) -> None:
    if not (RUN_DIR / "source_lock.json").is_file():
        raise RuntimeError("Run prepare before execute")
    device = torch.device("cuda")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for V72 execution")
    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    smoke(checkpoint_repo, device)
    dataset = MMUAVFeatureAlignmentDataset(v71.MANIFEST, 640, validate_paths=False)
    records = []
    for item in v71.CHECKPOINTS:
        record = evaluate_one(item, checkpoint_repo, dataset, device, batch_size)
        records.append(record)
        write_json("per_checkpoint_metrics.json", {"status": "IN_PROGRESS", "records": records})
        print(
            f"COMPLETE {item['opaque_id']} AP={record['ap50_95']:.6f} "
            f"AP50={record['ap50']:.6f} seconds={record['wall_clock_seconds']:.1f}",
            flush=True,
        )
    write_metrics(records)
    ledger = read_json("attempt_ledger.json")
    ledger["status"] = "ALL_EVALUATIONS_COMPLETE"
    write_json("attempt_ledger.json", ledger)
    write_json("final_decision.json", {
        "decision": "V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE",
        "scientific_label": SCIENTIFIC_LABEL,
        "manifest_rows_per_checkpoint": 1845,
        "checkpoint_metric_records": 6,
        "smoke_attempts": 1,
        "evaluation_attempts_per_checkpoint": 1,
        "metrics_computed": True,
        "physical_registration_asserted": False,
        "training_adaptation_calibration_or_tuning": False,
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "execute"))
    parser.add_argument("--checkpoint-repo", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare(args.checkpoint_repo)
    else:
        execute(args.checkpoint_repo, args.batch_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
