# V86 Minimal RGB+Thermal Dynamic Devval Protocol

Status: **FROZEN BEFORE TRAINING**

## Purpose

Train only the missing RGB+thermal two-way dynamic-gate control for seeds 0, 1,
and 2. This closes the event-marginal comparison against the existing V48
RGB+thermal+event dynamic-gate/no-dropout family without launching the full V86
outer-evaluation matrix.

This is component-disjoint development-validation evidence. It is not an
independent test, conventional outer cross-validation, or external validation.

## Data lock

- Train images: 7,439.
- Train manifest SHA256: `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f`.
- Development-validation images: 2,213.
- Validation manifest SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`.
- Historical 837-image partitions and V86 outer folds are not accessed.

## Model lock

- Model type: `reliability_rgbt`.
- Inputs used: RGB channels 0--2 and thermal channel 3.
- Event channel 4 is never read by the model.
- RGB and thermal stems: `Conv3x3 -> BN -> SiLU`, 16 channels each.
- Dynamic gate: pooled 32-vector, `Linear(32,16) -> SiLU -> Linear(16,2)`, softmax fusion.
- RepViT-M0.9 + FPN-128 + torchvision FCOS detector stack.
- Pretraining disabled.
- Parameters: 6,592,844; the existing three-way dynamic model has 6,593,293
  parameters, a disclosed difference of 449.
- Backbone source SHA256: `135ff9b5ee23c77a928fd39bd5f6776926797a547333225634431f7f8b21ef90`.
- Detector builder SHA256: `6907623fe7b33abc51e866ba6039d4a5f379ead678c952e89465d6702588cea7`.

## Training lock

- Seeds: 0, 1, 2; no replacement or selective rerun.
- Epochs: 50; batch size: 4; image size: 640; workers: 0.
- AdamW, learning rate `1e-4`, weight decay `1e-4`; no scheduler.
- Modality dropout: 0.
- Existing annotation clipping, target handling, and image normalization remain unchanged.
- Checkpoint retention: highest development-validation project-local AP50 across
  the 50 epochs, matching the V48 development-validation protocol.
- Training script SHA256: `4ad0c2038ed6e1f6fd4c47fdee559d4e83d50e3d78ec1c364ff45a5f911cf747`.
- `CUBLAS_WORKSPACE_CONFIG=:4096:8`, seeded Python/NumPy/PyTorch/DataLoader,
  cuDNN deterministic enabled, cuDNN benchmark disabled.

## Evaluation lock

- Standardized COCO evaluator after checkpoint retention.
- Detector score threshold: 0.001; metric operating threshold: 0.50.
- NMS IoU: 0.60; maximum detections: 100.
- Metrics: AP@[.50:.95], AP50, AP75, AR100, plus project operating metrics.
- Report all three seed rows, mean, sample SD, and same-seed differences against
  the existing V48 RGB+thermal+event dynamic-gate/no-dropout rows.
- No threshold, checkpoint, model, or claim may be changed after seeing results.

The result may support an event-marginal statement only within this frozen
development-validation protocol. It does not establish general event utility
outside TriAir or under an independent acquisition split.
