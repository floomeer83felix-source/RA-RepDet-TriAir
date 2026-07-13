"""Canonical COCO helpers for V50 converted annotations."""

from contextlib import redirect_stdout
import io
from pathlib import Path

import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval


def evaluate_detections(annotation_path, detections, max_detections=100):
    quiet = io.StringIO()
    with redirect_stdout(quiet):
        ground_truth = COCO(str(Path(annotation_path)))
        if detections:
            prediction_api = ground_truth.loadRes(detections)
        else:
            prediction_api = COCO()
            prediction_api.dataset = {
                "images": list(ground_truth.dataset["images"]),
                "annotations": [],
                "categories": list(ground_truth.dataset["categories"]),
            }
            prediction_api.createIndex()
        evaluator = COCOeval(ground_truth, prediction_api, "bbox")
        evaluator.params.imgIds = sorted(ground_truth.getImgIds())
        evaluator.params.catIds = [1]
        evaluator.params.maxDets = [1, 10, int(max_detections)]
        evaluator.evaluate()
        evaluator.accumulate()
        evaluator.summarize()

    stats = np.asarray(evaluator.stats, dtype=np.float64)
    positive_annotations = [
        item
        for item in ground_truth.dataset.get("annotations", [])
        if int(item.get("category_id", 0)) == 1
        and not int(item.get("iscrowd", 0))
        and not int(item.get("ignore", 0))
    ]
    ignored_annotations = [
        item
        for item in ground_truth.dataset.get("annotations", [])
        if int(item.get("iscrowd", 0)) or int(item.get("ignore", 0))
    ]
    return {
        "ap50_95": float(stats[0]),
        "ap50": float(stats[1]),
        "ap75": float(stats[2]),
        "ap_small": float(stats[3]),
        "ap_medium": float(stats[4]),
        "ap_large": float(stats[5]),
        "ar1": float(stats[6]),
        "ar10": float(stats[7]),
        "ar100": float(stats[8]),
        "ar_small": float(stats[9]),
        "ar_medium": float(stats[10]),
        "ar_large": float(stats[11]),
        "images": len(ground_truth.dataset.get("images", [])),
        "gt_boxes": len(positive_annotations),
        "ignored_regions": len(ignored_annotations),
        "detections": len(detections),
        "backend": "pycocotools.cocoeval.COCOeval",
        "summary_text": quiet.getvalue(),
    }


def outputs_to_detections(outputs, targets, score_threshold=0.001, max_detections=100):
    detections = []
    for output, target in zip(outputs, targets):
        image_id = int(target["image_id"].reshape(-1)[0].item())
        boxes = output["boxes"].detach().cpu()
        scores = output["scores"].detach().cpu()
        labels = output["labels"].detach().cpu()
        keep = (labels == 1) & (scores >= float(score_threshold))
        indices = keep.nonzero(as_tuple=False).flatten()
        if indices.numel():
            order = scores[indices].argsort(descending=True, stable=True)
            indices = indices[order[: int(max_detections)]]
        for index in indices.tolist():
            x1, y1, x2, y2 = [float(value) for value in boxes[index].tolist()]
            width = max(0.0, x2 - x1)
            height = max(0.0, y2 - y1)
            if width <= 0.0 or height <= 0.0:
                continue
            detections.append(
                {
                    "image_id": image_id,
                    "category_id": 1,
                    "bbox": [x1, y1, width, height],
                    "score": float(scores[index]),
                }
            )
    return detections

