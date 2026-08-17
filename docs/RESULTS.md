# Final Results

All accuracy values use the same frozen component-disjoint development-validation manifest and standardized COCO evaluator. Values are mean +/- sample standard deviation across seeds 0, 1, and 2.

## Core Comparison

| Variant | AP | AP50 | AP75 | AR100 |
| --- | ---: | ---: | ---: | ---: |
| Matched early fusion | 0.6803 +/- 0.0221 | 0.9372 +/- 0.0047 | 0.8090 +/- 0.0251 | 0.7578 +/- 0.0184 |
| Early fusion + dropout | 0.6840 +/- 0.0101 | 0.9437 +/- 0.0028 | 0.8211 +/- 0.0070 | 0.7607 +/- 0.0094 |
| Separate stems, fixed equal fusion | 0.6631 +/- 0.0068 | 0.9341 +/- 0.0078 | 0.8053 +/- 0.0095 | 0.7478 +/- 0.0085 |
| Separate stems, learned projection | 0.6848 +/- 0.0095 | 0.9405 +/- 0.0065 | 0.8341 +/- 0.0100 | 0.7643 +/- 0.0090 |
| **Dynamic gate, no dropout** | **0.7251 +/- 0.0121** | 0.9475 +/- 0.0003 | **0.8742 +/- 0.0081** | **0.7917 +/- 0.0098** |
| Dynamic gate + dropout p=0.15 | 0.7156 +/- 0.0172 | **0.9534 +/- 0.0017** | 0.8729 +/- 0.0192 | 0.7826 +/- 0.0161 |

The primary model is the no-dropout dynamic gate. Modality dropout is an optional robustness intervention rather than the source of the nominal-input gain.

## Single Modalities

| Input | AP | AP50 | AP75 |
| --- | ---: | ---: | ---: |
| RGB only | 0.4473 +/- 0.0033 | 0.7674 +/- 0.0036 | 0.4428 +/- 0.0098 |
| Thermal only | 0.5196 +/- 0.0196 | 0.8320 +/- 0.0154 | 0.5776 +/- 0.0244 |
| Event only | 0.1949 +/- 0.0012 | 0.3657 +/- 0.0032 | 0.1943 +/- 0.0049 |

Thermal is the strongest standalone stream. The primary RA-RepDet model exceeds thermal-only AP by `0.2055 +/- 0.0266`, positive for all three paired seeds. This does not isolate a positive event contribution: RGB + thermal early fusion reaches `0.6843 +/- 0.0312` AP, slightly above five-channel matched early fusion.

## Component Bootstrap

The descriptive bootstrap resamples 1,298 validation components, uses 5,000 replicates, and averages the component-macro metric across three seeds.

| Comparison | AP difference | 95% percentile interval |
| --- | ---: | ---: |
| Dynamic gate - matched early | +0.0420 | [0.0376, 0.0464] |
| Dynamic gate - fixed equal stems | +0.0496 | [0.0452, 0.0539] |
| Dynamic gate - learned projection | +0.0310 | [0.0269, 0.0351] |

These intervals describe component-aware uncertainty; no hypothesis test or statistical-significance claim is made.

## Efficiency

RTX 3090, batch size 1, 640 x 640, FP32. Detector inference includes torchvision transform, backbone, head, NMS, and postprocessing, excluding data loading and file I/O.

| Measurement | Matched early | Reliability-aware | Difference |
| --- | ---: | ---: | ---: |
| Parameters | 6,591,609 | 6,593,293 | +1,684 |
| Detector GFLOPs | 105.21 | 105.98 | +0.77 |
| Detector latency | 22.89 ms | 23.30 ms | +0.41 ms |

The gate has small parameter, compute, and latency overhead, but materially higher peak CUDA memory.

## Robustness Interpretation

Missing-event robustness is mainly associated with modality-dropout training and its interaction with gating. Controlled corruption did not produce monotonic down-weighting of the affected modality. Routing coefficients should therefore be interpreted as task-driven fusion weights, not calibrated physical reliability estimates.

Machine-readable summaries are available in [`results/`](../results/).
