import torch


def box_iou(boxes1, boxes2):
    if boxes1.numel() == 0 or boxes2.numel() == 0:
        return torch.zeros((boxes1.shape[0], boxes2.shape[0]), dtype=torch.float32)

    boxes1 = boxes1.to(torch.float32).cpu()
    boxes2 = boxes2.to(torch.float32).cpu()

    lt = torch.maximum(boxes1[:, None, :2], boxes2[:, :2])
    rb = torch.minimum(boxes1[:, None, 2:], boxes2[:, 2:])
    wh = (rb - lt).clamp(min=0)
    inter = wh[:, :, 0] * wh[:, :, 1]

    area1 = ((boxes1[:, 2] - boxes1[:, 0]).clamp(min=0) * (boxes1[:, 3] - boxes1[:, 1]).clamp(min=0))
    area2 = ((boxes2[:, 2] - boxes2[:, 0]).clamp(min=0) * (boxes2[:, 3] - boxes2[:, 1]).clamp(min=0))
    union = area1[:, None] + area2 - inter
    return inter / union.clamp(min=1e-6)


def _prepare_records(predictions, targets, score_thresh=0.0):
    pred_records = []
    gt_by_image = {}
    total_gt = 0

    for image_index, target in enumerate(targets):
        gt_boxes = target["boxes"].detach().cpu()
        gt_labels = target["labels"].detach().cpu()
        keep_gt = gt_labels == 1
        gt_boxes = gt_boxes[keep_gt]
        gt_by_image[image_index] = gt_boxes
        total_gt += int(gt_boxes.shape[0])

        pred = predictions[image_index]
        boxes = pred["boxes"].detach().cpu()
        scores = pred["scores"].detach().cpu()
        labels = pred["labels"].detach().cpu()
        keep_pred = (labels == 1) & (scores >= score_thresh)
        for box, score in zip(boxes[keep_pred], scores[keep_pred]):
            pred_records.append(
                {
                    "image_index": image_index,
                    "score": float(score),
                    "box": box,
                }
            )

    pred_records.sort(key=lambda item: item["score"], reverse=True)
    return pred_records, gt_by_image, total_gt


def _match_predictions(pred_records, gt_by_image, iou_thresh):
    matched = {image_index: torch.zeros(len(boxes), dtype=torch.bool) for image_index, boxes in gt_by_image.items()}
    tp = []
    fp = []

    for pred in pred_records:
        image_index = pred["image_index"]
        gt_boxes = gt_by_image[image_index]
        if gt_boxes.numel() == 0:
            tp.append(0.0)
            fp.append(1.0)
            continue

        ious = box_iou(pred["box"].view(1, 4), gt_boxes).view(-1)
        best_iou, best_index = torch.max(ious, dim=0)
        best_index = int(best_index)
        if float(best_iou) >= iou_thresh and not bool(matched[image_index][best_index]):
            matched[image_index][best_index] = True
            tp.append(1.0)
            fp.append(0.0)
        else:
            tp.append(0.0)
            fp.append(1.0)

    return torch.tensor(tp, dtype=torch.float32), torch.tensor(fp, dtype=torch.float32)


def average_precision(predictions, targets, iou_thresh=0.5):
    pred_records, gt_by_image, total_gt = _prepare_records(predictions, targets, score_thresh=0.0)
    if total_gt == 0:
        return 0.0
    if not pred_records:
        return 0.0

    tp, fp = _match_predictions(pred_records, gt_by_image, iou_thresh)
    tp_cum = torch.cumsum(tp, dim=0)
    fp_cum = torch.cumsum(fp, dim=0)
    recalls = tp_cum / max(total_gt, 1)
    precisions = tp_cum / (tp_cum + fp_cum).clamp(min=1e-6)

    mrec = torch.cat([torch.tensor([0.0]), recalls, torch.tensor([1.0])])
    mpre = torch.cat([torch.tensor([0.0]), precisions, torch.tensor([0.0])])
    for i in range(mpre.numel() - 1, 0, -1):
        mpre[i - 1] = torch.maximum(mpre[i - 1], mpre[i])

    changed = torch.where(mrec[1:] != mrec[:-1])[0]
    ap = torch.sum((mrec[changed + 1] - mrec[changed]) * mpre[changed + 1])
    return float(ap)


def precision_recall(predictions, targets, iou_thresh=0.5, score_thresh=0.05):
    pred_records, gt_by_image, total_gt = _prepare_records(predictions, targets, score_thresh=score_thresh)
    if not pred_records:
        return 0.0, 0.0

    tp, fp = _match_predictions(pred_records, gt_by_image, iou_thresh)
    true_pos = float(tp.sum())
    false_pos = float(fp.sum())
    precision = true_pos / max(true_pos + false_pos, 1e-6)
    recall = true_pos / max(float(total_gt), 1e-6)
    return precision, recall


def detection_metrics(predictions, targets, score_thresh=0.05):
    precision, recall = precision_recall(predictions, targets, iou_thresh=0.5, score_thresh=score_thresh)
    pred_records, _, total_gt = _prepare_records(predictions, targets, score_thresh=score_thresh)
    if pred_records:
        mean_confidence = sum(record["score"] for record in pred_records) / len(pred_records)
    else:
        mean_confidence = 0.0
    return {
        "precision": precision,
        "recall": recall,
        "ap50": average_precision(predictions, targets, iou_thresh=0.5),
        "ap75": average_precision(predictions, targets, iou_thresh=0.75),
        "gt_boxes": total_gt,
        "predictions": len(pred_records),
        "mean_confidence": mean_confidence,
    }


def format_metrics(metrics):
    return (
        f"Precision={metrics['precision']:.4f} "
        f"Recall={metrics['recall']:.4f} "
        f"AP50={metrics['ap50']:.4f} "
        f"AP75={metrics['ap75']:.4f}"
    )
