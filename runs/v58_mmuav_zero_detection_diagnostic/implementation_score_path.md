# Actual FCOS Score Path

For every FPN level torchvision FCOS computes `sqrt(sigmoid(class_logit) * sigmoid(centerness_logit))`, flattens class/anchor candidates, applies the strict `score > score_thresh` filter, keeps at most `topk_candidates` per level, decodes and clips boxes, applies class-aware batched NMS, then keeps the first `detections_per_img` globally. V57 used score threshold 0.001, NMS 0.6, per-level top-k 1000, and final cap 100. The evaluator subsequently keeps foreground label 1 only and applies no second positive threshold.
