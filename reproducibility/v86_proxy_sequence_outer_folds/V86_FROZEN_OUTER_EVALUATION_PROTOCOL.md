# V86 Frozen Outer Evaluation Protocol

Status: **FROZEN**

This protocol was frozen before any V86 outer-fold inference. The five parts are
an unequal proxy-sequence-grouped outer evaluation, not conventional balanced
five-fold cross-validation and not verified flight-independent test sets.

## Dataset and grouping lock

- Dataset: current local TriAir provider archive, 10,489 five-channel `uint8`
  arrays, 30,634 retained GT rows, and 739 zero-target images.
- Read-only provenance audit SHA256: `b0604f8ce50c78d0c6b2bad7cd7ac423279715f6fec9d8a253529bb64c2eda62`.
- Full file-inventory SHA256: `83c86c3f2eebd93cf085c53bdebddd9191111998de0827a60a1964a3a1719ad5`.
- Proxy-group builder SHA256: `fa56ec9ccc0ff618c9d4ddfe6d92f34efefd39458afee6d67fbc1ed9241d9eb0`.
- Proxy groups: 45 indivisible groups.
- Giant-group bridge audit: PASS. Candidate pHash/dHash edges are not used in
  grouping; filename adjacency alone retains the 4,077-image component.
- Giant-group audit script SHA256: `2456064a40c2387383d21d0d8a506e3a97ada5e9f1483c78c7fe8cb0d27a4bf3`.

Outer-fold manifest SHA256 values:

| Fold | Held-out manifest SHA256 | Training-complement SHA256 |
|---:|---|---|
| 0 | `2b03df3a645cf87f6cd684a2d56e96899e7a1d3c46aa935f504e0f051601619d` | `30a97801b9cbdcd1d8b1bbd7edf168bdc9352220e4196115b3484b867c77b4e7` |
| 1 | `363ba9835c5268e30af96288a79f93460a4bba0b21e8ccf38c97bc2f3fe01615` | `424299a25d366d6dc478b3edef877186ce78dbc79d0b9e154a499951e9e13374` |
| 2 | `afd294d76e0b1b4d5617ae8906ec88b8a6c81fdf7ed1eb4d7874f8c502e26e30` | `af38e0f1527421cccd8d53832da2de2e84abc6dd982957500637ddb3121c1510` |
| 3 | `7aa165194c7782f25d637b60eabfbd6805c7a83808a01842489fe3de5035deb9` | `11ca6ed76742e23187e90afc376da7cca9e0bf793bdf1fe229a783d76b04c127` |
| 4 | `c403b0e1bc443de34183e8fcf78bf7295e260f0351e128cec380d58b736db59d` | `eb6f49e66cd4a99dbd240e75929ca4790409fa036c401b78a48e351cd9db8711` |

## Architecture matrix

All detectors use RepViT-M0.9, four-level FPN with 128 output channels, and the
same torchvision FCOS head.

| ID | Frozen model | Implementation | Parameters |
|---|---|---|---:|
| A | Five-channel early fusion | `early` | 6,591,609 |
| B | Fixed-equal RGB/T/E stems | `ra_static_equal` | 6,592,458 |
| C | Learned static stem projection | `ra_stems_project` | 6,593,242 |
| D | RGB+thermal two-way dynamic gate | `reliability_rgbt` | 6,592,844 |
| E | RGB+thermal+event three-way dynamic gate | `reliability`, dropout 0 | 6,593,293 |
| F | Model E with modality-dropout training | `reliability`, dropout 0.15 | 6,593,293 |

Model D uses RGB and thermal stems, a `32 -> 16 -> 2` softmax gate, and never
reads event channel 4. Model E/F uses three stems and a `48 -> 16 -> 3` gate.
The D/E parameter difference is 449 and must be reported; D is not described as
exactly capacity-identical. No dummy stem is used in the primary matrix.

Architecture source locks:

- `rarepdet/models/repvit_fpn_backbone.py`: `135ff9b5ee23c77a928fd39bd5f6776926797a547333225634431f7f8b21ef90`.
- `rarepdet/models/early_fusion_fcos.py`: `6907623fe7b33abc51e866ba6039d4a5f379ead678c952e89465d6702588cea7`.
- `rarepdet/models/ablation_fusion_fcos.py`: `2cd96fbde6051ce01e99562e062fb0847fb5ba9dfae5611cdd2ae92aa00a7e77`.

## Training lock

- Seeds: `0, 1, 2, 3, 4`.
- Exactly 50 epochs; batch size 4; input size 640; workers 0.
- AdamW, learning rate `1e-4`, weight decay `1e-4`; no learning-rate scheduler.
- RepViT pretraining: disabled (`pretrained=False`).
- Existing image normalization and annotation clipping policy are unchanged.
- BN policy: BN statistics update in training mode on the four-fold training
  complement and are frozen by `model.eval()` during held-out inference.
- Modality dropout is applied only for F, to normalized input channels before
  modality stems. RGB, thermal, and event groups use independent Bernoulli
  probability 0.15; if all three are selected, one group is restored uniformly.
- Models A--E use modality dropout 0.
- Checkpoint selection: the final checkpoint after exactly epoch 50.
- Inner validation: none. No metric is used for checkpoint selection.
- Dedicated no-outer-access trainer SHA256:
  `8864aea60f88d148d7e342807572fdbbe69df0b4643cbb0aba77798da3c9baa0`.
- cuBLAS reproducibility gate: the trainer refuses to start unless
  `CUBLAS_WORKSPACE_CONFIG=:4096:8` was set before process launch.

Each fold model may read only its frozen four-fold training-complement manifest
during training. The held-out manifest is first opened after training has ended
and the epoch-50 checkpoint has been frozen.

## Evaluation lock

For every model and seed, each image receives exactly one held-out prediction
from the model whose outer fold contains that image. The five prediction sets are
pooled over all 10,489 unique image IDs and the complete COCO evaluator is run
once. Fold AP values are diagnostic only and must not be arithmetically averaged.

- Detector score threshold: 0.001.
- NMS IoU: 0.60.
- Maximum detections per image: 100.
- Primary metric: pooled out-of-fold COCO AP@[0.50:0.95].
- Secondary metrics: pooled AP50, AP75, and AR100; AP_S/AP_M only if the frozen
  evaluator supports the same area definitions without post-result changes.
- Main uncertainty: mean and sample SD across five seed-level pooled OOF values.
- Paired contrasts use same-seed pooled OOF differences. A descriptive 95% t
  interval uses 4 degrees of freedom; it is not presented as proof of significance.
- Secondary uncertainty: 5,000 proxy-group bootstrap replicates with fixed seed
  8604. Groups are sampled with replacement, replicated image IDs are made
  unique, and full COCO AP is recomputed for every replicate. Percentiles 2.5 and
  97.5 are reported as a 95% bootstrap interval.

Primary predeclared contrasts are E-A, E-B, E-C, E-D, and F-E. The E-D contrast
estimates the event-channel contribution within the dynamic-gate family while
retaining the disclosed 449-parameter capacity difference.

## Prohibited outer-fold uses

Outer-fold metrics, predictions, losses, or qualitative examples must not be used
for checkpoint selection, threshold tuning, hyperparameter tuning, architecture
modification, early stopping, seed continuation, sample selection, or changes to
paper claims. After any outer-fold result is viewed, model or protocol changes
require a new explicitly versioned experiment rather than silent V86 revision.

The historical 837-image partitions are not accessed or used by V86.
