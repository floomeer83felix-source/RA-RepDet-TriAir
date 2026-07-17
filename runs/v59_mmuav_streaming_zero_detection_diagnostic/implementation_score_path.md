# Installed FCOS Score Path

The source-locked torchvision 0.20.1 path computes `sqrt(sigmoid(class_logit) * sigmoid(centerness_logit))`, applies strict `score > 0.001`, then per-level top-k 1000, decode/clip, class-aware NMS 0.6, and global cap 100. The evaluator retains foreground label 1. No setting is changed by V59.
