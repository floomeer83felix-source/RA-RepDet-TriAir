# Modality-Subset Consistency Distillation

Modality-Subset Consistency Distillation (MSCD) is a training-only extension for the existing Reliability Fusion RepViT-FCOS detector.

The goal is to improve robustness to synthetic missing modalities without changing the inference architecture, parameter count, or runtime of E2. The student remains the same reliability-fusion detector used by E2.

## Teacher And Student

- Teacher: frozen E2 reliability-fusion checkpoint, evaluated on the full 5-channel input.
- Student: the same reliability-fusion architecture as E2, trained with the existing modality-dropout convention.
- Inference: student only; no teacher, extra projection, attention block, decoder, or additional detector head is used.

## Feature Consistency

MSCD captures FPN feature maps from the teacher and student at the first three FPN levels, corresponding to P3, P4, and P5 in this project's four-level RepViT-FPN detector.

For each selected level:

1. Teacher receives the full RGB, thermal, and event input.
2. Student receives the modality-dropout input.
3. Both feature maps are L2-normalized along the channel dimension.
4. A smooth L1 feature consistency loss is computed and averaged over the selected levels.

The final training loss is:

`L = L_detector + lambda_cons * L_cons`

`lambda_cons` is zero during the warmup epochs, linearly ramps to `0.05`, and then remains fixed.

## Why This Is Training-Only

The consistency term uses the teacher only during training. The saved E6 checkpoint contains a standard reliability-fusion FCOS student. At inference time it has the same parameter count and computation path as E2.

## Selection Rule

E6 should replace E2 only if it keeps full-modality AP50 within 0.001 of E2 and improves mean missing-modality AP50, or if it improves full AP50/AP75 outright. Otherwise, E2 remains the paper main model and E6 is reported as a training-strategy ablation.
