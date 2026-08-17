#!/usr/bin/env python
"""Deterministic tiny-input smoke tests for the V46 COCO metric adapter."""

import math
from pathlib import Path
import sys

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.coco_metrics import coco_detection_metrics


def target(boxes):
    return {
        "boxes": torch.tensor(boxes, dtype=torch.float32).reshape(-1, 4),
        "labels": torch.ones(len(boxes), dtype=torch.int64),
        "image_id": torch.tensor([0], dtype=torch.int64),
    }


def prediction(boxes, scores):
    return {
        "boxes": torch.tensor(boxes, dtype=torch.float32).reshape(-1, 4),
        "scores": torch.tensor(scores, dtype=torch.float32),
        "labels": torch.ones(len(boxes), dtype=torch.int64),
    }


def assert_close(actual, expected, label):
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-9):
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def main():
    perfect = coco_detection_metrics(
        [prediction([[0, 0, 10, 10]], [0.9])],
        [target([[0, 0, 10, 10]])],
    )
    assert_close(perfect["ap50_95"], 1.0, "perfect AP50:95")
    assert_close(perfect["ap50"], 1.0, "perfect AP50")
    assert_close(perfect["ap75"], 1.0, "perfect AP75")

    false_positive_first = coco_detection_metrics(
        [prediction([[20, 20, 30, 30], [0, 0, 10, 10]], [0.9, 0.8])],
        [target([[0, 0, 10, 10]])],
    )
    assert_close(false_positive_first["ap50_95"], 0.5, "ranked false positive AP50:95")

    iou_point_eight = coco_detection_metrics(
        [prediction([[0, 0, 8, 10]], [0.9])],
        [target([[0, 0, 10, 10]])],
    )
    assert_close(iou_point_eight["ap50_95"], 0.7, "IoU threshold averaging")
    assert_close(iou_point_eight["ap_by_iou"]["0.80"], 1.0, "IoU 0.80 inclusion")
    assert_close(iou_point_eight["ap_by_iou"]["0.85"], 0.0, "IoU 0.85 exclusion")

    empty = coco_detection_metrics(
        [prediction([], [])],
        [target([[0, 0, 10, 10]])],
    )
    assert_close(empty["ap50_95"], 0.0, "empty detection AP50:95")

    print("PASS: COCO metric smoke tests")


if __name__ == "__main__":
    main()
