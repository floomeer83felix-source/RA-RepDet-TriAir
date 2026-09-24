"""Deterministic one-to-one vehicle detection matching for M3OT displays."""

from __future__ import annotations

import torch

from rarepdet.metrics import box_iou


def match_prediction(prediction: dict, target: dict, *, score_thr: float = 0.25,
                     iou_thr: float = 0.50) -> dict:
    gt = target["boxes"].detach().cpu()[target["labels"].detach().cpu() == 1]
    boxes = prediction["boxes"].detach().cpu()
    scores = prediction["scores"].detach().cpu()
    labels = prediction["labels"].detach().cpu()
    indices = torch.nonzero((labels == 1) & (scores >= score_thr), as_tuple=False).flatten()
    indices = indices[torch.argsort(scores[indices], descending=True, stable=True)]
    remaining = torch.ones(len(gt), dtype=torch.bool)
    matched, false_positives = [], []
    for index in indices.tolist():
        if not bool(remaining.any()):
            false_positives.append(index)
            continue
        ious = box_iou(boxes[index:index + 1], gt).flatten()
        ious[~remaining] = -1
        best_iou, best_gt = torch.max(ious, dim=0)
        if float(best_iou) >= iou_thr:
            best_gt = int(best_gt)
            remaining[best_gt] = False
            matched.append((index, best_gt))
        else:
            false_positives.append(index)
    false_negatives = torch.nonzero(remaining, as_tuple=False).flatten().tolist()
    return {"tp": len(matched), "fp": len(false_positives), "fn": len(false_negatives),
            "matches": matched, "fp_indices": false_positives, "fn_indices": false_negatives}
