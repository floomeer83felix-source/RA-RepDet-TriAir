# M3OT supervised RGB+thermal six-seed protocol

Authorized by the user on 2026-09-24. This is a **new supervised M3OT
train/val experiment**, not the previous frozen-TriAir zero-shot test or
inference-only scale adapter. It is not a blind test because val is used for
checkpoint selection every epoch. Do not use the M3OT public test split.

## Data gate

- Source root: `D:\download\M3OT (1)\M3OT`.
- Use official group 1 and group 2 `train` and `val` splits, actual local
  group/sequence/frame keys to pair RGB with IR. The known group-1 val IR
  COCO path typo must not drive pairing. Exclude the one train RGB frame
  without IR and inventory it; never synthesize its missing modality.
- Use only official RGB COCO `vehicle` boxes as detection GT in RGB pixel
  coordinates. No other classes or annotation rewrites.
- Audit counts, duplicate keys, image dimensions, channel content, finite and
  in-bounds boxes, and split overlap. Save deterministic RGB-with-GT/IR
  sample contact sheets and inspect them before GPU training.
- Expected from prior read-only audit: 8,630 train pairs / 111,678 GT boxes;
  1,200 val pairs / 13,781 GT boxes. Recheck rather than assume.

## Matched models and training

- Early fusion: `build_early_fusion_fcos(in_chans=4)` with RGB+IR input.
- Dynamic routing: `build_reliability_rgbt_fcos` with RGB+IR input and its
  unused fifth tensor slot fixed to zero; no event measurement.
- Both use their existing RepViT-M0.9/FPN/FCOS builders with
  `pretrained=False`. Do **not** load TriAir or M3OT checkpoints to initialize
  either model.
- Seeds: 0, 1, 2, with the same seeded shuffle stream and image order per
  corresponding seed. Train exactly 50 epochs, batch size 4, fixed 640x640
  detector input, AdamW, constant `lr=1e-4`, `weight_decay=1e-4`. No warm-up,
  scheduler, gradient accumulation, or architecture-specific tuning.
- Decode paired uint8 RGB/IR, concatenate RGB then IR, divide by 255;
  torchvision detector performs the same fixed 640x640 warp for both. No
  mosaic, mixup, random crop, flip, color jitter, or modality dropout.
- If batch 4 cannot run, **stop and document the blocker**. Do not silently
  lower it or otherwise break the matched protocol.
- Evaluate official val after every epoch with COCO AP@[.50:.95], AP50,
  AP75, AR100. Detector score floor 0.001, NMS IoU 0.60, max 100 detections
  per image. Save each run's best checkpoint on strictly higher val AP50;
  earliest epoch wins ties. Save last-epoch state for exact resume.

## Final outputs

- Six best-checkpoint rows with AP/AP50/AP75/AR100 and checkpoint SHA256;
  model-wise mean +/- **sample** standard deviation over seeds.
- Paired dynamic-minus-early AP differences for seeds 0/1/2 and their mean
  +/- sample standard deviation. Report unfavorable seeds without filtering.
- Best-checkpoint fixed operating point: score >= 0.25, one-to-one IoU >=
  0.50, TP/FP/FN and precision/recall, using the same rule for all runs.
- Three val scenes selected before inspecting predictions by deterministic,
  model-independent image/GT properties. Show RGB, IR, RGB-coordinate GT,
  early predictions, and dynamic predictions. The displayed pair is seed 0
  for both, threshold 0.25. Do not hand-pick successful scenes.
- Per-seed and summary CSV, pairing/visual audit, environment and protocol
  fingerprints, and a short honest experiment report under a new local output
  root `runs/m3ot_supervised_rgbt_v1/`.

The comparison establishes whether the matched supervised M3OT development
protocol reproduces a dynamic-routing gain; it does not by itself prove
independent blind test superiority, modality reliability calibration, or
general cross-dataset transfer. Do not change learning rate, epochs,
augmentation, threshold, checkpoint rule, or seeds based on which model leads.
