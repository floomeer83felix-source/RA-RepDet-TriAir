"""COCO-style metrics for the single-class TriAir detection task."""

from contextlib import redirect_stdout
import io

import numpy as np
import torch
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval


COCO_IOU_THRESHOLDS = tuple(round(0.50 + 0.05 * index, 2) for index in range(10))
COCO_RECALL_THRESHOLDS = tuple(round(0.01 * index, 2) for index in range(101))


def _mean_valid(values):
    values = np.asarray(values, dtype=np.float64)
    valid = values[values > -1]
    return float(valid.mean()) if valid.size else 0.0


def _xyxy_to_xywh(box):
    x1, y1, x2, y2 = (float(value) for value in box)
    return [x1, y1, max(x2 - x1, 0.0), max(y2 - y1, 0.0)]


def _build_coco_inputs(
    predictions,
    targets,
    *,
    foreground_label=1,
    score_thresh=0.0,
    max_detections=100,
):
    if len(predictions) != len(targets):
        raise ValueError("predictions and targets must contain the same number of images")
    if max_detections <= 0:
        raise ValueError("max_detections must be positive")

    images = []
    annotations = []
    detections = []
    annotation_id = 1

    for image_index, (prediction, target) in enumerate(zip(predictions, targets), start=1):
        images.append({"id": image_index})

        gt_boxes = target["boxes"].detach().to(torch.float32).cpu()
        gt_labels = target["labels"].detach().to(torch.int64).cpu()
        for box in gt_boxes[gt_labels == foreground_label]:
            bbox = _xyxy_to_xywh(box.tolist())
            if bbox[2] <= 0.0 or bbox[3] <= 0.0:
                continue
            annotations.append(
                {
                    "id": annotation_id,
                    "image_id": image_index,
                    "category_id": foreground_label,
                    "bbox": bbox,
                    "area": bbox[2] * bbox[3],
                    "iscrowd": 0,
                }
            )
            annotation_id += 1

        boxes = prediction["boxes"].detach().to(torch.float32).cpu()
        scores = prediction["scores"].detach().to(torch.float32).cpu()
        labels = prediction["labels"].detach().to(torch.int64).cpu()
        keep = torch.nonzero(
            (labels == foreground_label) & (scores >= float(score_thresh)),
            as_tuple=False,
        ).flatten()
        if keep.numel() > 0:
            order = torch.argsort(scores[keep], descending=True, stable=True)
            keep = keep[order[:max_detections]]
        for prediction_index in keep.tolist():
            bbox = _xyxy_to_xywh(boxes[prediction_index].tolist())
            if bbox[2] <= 0.0 or bbox[3] <= 0.0:
                continue
            detections.append(
                {
                    "image_id": image_index,
                    "category_id": foreground_label,
                    "bbox": bbox,
                    "score": float(scores[prediction_index]),
                }
            )

    dataset = {
        "info": {"description": "TriAir project-local COCO metric adapter"},
        "licenses": [],
        "images": images,
        "annotations": annotations,
        "categories": [{"id": foreground_label, "name": "vehicle"}],
    }
    return dataset, detections


def _empty_detection_api(dataset):
    detection_api = COCO()
    detection_api.dataset = {
        "info": dict(dataset.get("info", {})),
        "licenses": list(dataset.get("licenses", [])),
        "images": list(dataset["images"]),
        "annotations": [],
        "categories": list(dataset["categories"]),
    }
    detection_api.createIndex()
    return detection_api


def coco_detection_metrics(
    predictions,
    targets,
    *,
    foreground_label=1,
    score_thresh=0.0,
    max_detections=100,
    iou_thresholds=COCO_IOU_THRESHOLDS,
):
    """Compute COCO 101-point AP/AR for TriAir's single vehicle class.

    The detector output is capped per image before evaluation. The default
    threshold grid is IoU 0.50:0.05:0.95 and the recall grid is 0.00:0.01:1.00.
    AR is reported at maxDets 1, 10, and ``max_detections`` (100 in the frozen
    evaluation contract).
    """

    iou_thresholds = tuple(float(value) for value in iou_thresholds)
    if not iou_thresholds:
        raise ValueError("iou_thresholds must not be empty")

    dataset, detections = _build_coco_inputs(
        predictions,
        targets,
        foreground_label=foreground_label,
        score_thresh=score_thresh,
        max_detections=max_detections,
    )

    quiet = io.StringIO()
    with redirect_stdout(quiet):
        ground_truth_api = COCO()
        ground_truth_api.dataset = dataset
        ground_truth_api.createIndex()
        if detections:
            detection_api = ground_truth_api.loadRes(detections)
        else:
            detection_api = _empty_detection_api(dataset)

        evaluator = COCOeval(ground_truth_api, detection_api, iouType="bbox")
        evaluator.params.imgIds = [image["id"] for image in dataset["images"]]
        evaluator.params.catIds = [foreground_label]
        evaluator.params.iouThrs = np.asarray(iou_thresholds, dtype=np.float64)
        evaluator.params.recThrs = np.asarray(COCO_RECALL_THRESHOLDS, dtype=np.float64)
        evaluator.params.maxDets = [1, 10, int(max_detections)]
        evaluator.evaluate()
        evaluator.accumulate()

    precision = evaluator.eval["precision"][:, :, 0, 0, 2]
    ap_by_iou = {
        f"{threshold:.2f}": _mean_valid(precision[index])
        for index, threshold in enumerate(iou_thresholds)
    }
    ap_values = list(ap_by_iou.values())

    recall_tensor = evaluator.eval["recall"][:, 0, 0, :]
    ar_by_max_dets = {
        str(int(max_det)): _mean_valid(recall_tensor[:, index])
        for index, max_det in enumerate(evaluator.params.maxDets)
    }

    return {
        "ap50_95": float(np.mean(ap_values)),
        "ap50": ap_by_iou.get("0.50", 0.0),
        "ap75": ap_by_iou.get("0.75", 0.0),
        "ap_by_iou": ap_by_iou,
        "ar1": ar_by_max_dets.get("1", 0.0),
        "ar10": ar_by_max_dets.get("10", 0.0),
        "ar100": ar_by_max_dets.get(str(int(max_detections)), 0.0),
        "ar_by_max_dets": ar_by_max_dets,
        "images": len(dataset["images"]),
        "gt_boxes": len(dataset["annotations"]),
        "detections": len(detections),
        "iou_thresholds": list(iou_thresholds),
        "recall_thresholds": len(COCO_RECALL_THRESHOLDS),
        "max_detections": int(max_detections),
        "backend": "pycocotools.cocoeval.COCOeval",
    }
