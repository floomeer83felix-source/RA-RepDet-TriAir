# Phase 4B Report

Generated: 2026-06-26T21:07:57

## Protocol

- Frozen split: `runs/blocked_split_candidates/block64_guard16_seed0_train.txt` and `block64_guard16_seed0_val.txt`.
- Required split integrity: train=7439, validation=2213, guard=837, exact RGB train/validation matches=0, same-family guard violations=0.
- Guard samples are excluded from both training and validation.
- Former random-split E-runs are historical diagnostics only.
- Phase 4A B-runs are exploratory pilots only and are not pooled with controlled-seed R-runs.
- Two seeds are not sufficient for a statistical-significance claim.
- Missing-modality AP50 is interpreted per condition; arithmetic mean missing AP50 is not used as the sole selection criterion.

## Per-Run Table

| Variant | Seed | Dropout Ratio | P@0.50 | R@0.50 | F1@0.50 | AP50 | AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R0 Early Fusion | 0 | NA | 0.890591 | 0.896172 | 0.893373 | 0.938560 | 0.827560 | NA | NA | NA |
| R0 Early Fusion | 2 | NA | 0.902247 | 0.891091 | 0.896634 | 0.937711 | 0.831114 | NA | NA | NA |
| R1 Reliability p=0.00 | 0 | 0.00 | 0.890553 | 0.916497 | 0.903339 | 0.952112 | 0.889847 | 0.673004 | 0.328742 | 0.425560 |
| R1 Reliability p=0.00 | 2 | 0.00 | 0.920263 | 0.899221 | 0.909620 | 0.954378 | 0.893068 | 0.752975 | 0.332811 | 0.711880 |
| R2 Reliability p=0.15 | 0 | 0.15 | 0.906797 | 0.912940 | 0.909858 | 0.961573 | 0.899166 | 0.911342 | 0.682321 | 0.961223 |
| R2 Reliability p=0.15 | 2 | 0.15 | 0.916368 | 0.909383 | 0.912862 | 0.957739 | 0.870351 | 0.904481 | 0.658199 | 0.955474 |
| R4 Reliability p=0.20 | 0 | 0.20 | 0.938850 | 0.920562 | 0.929616 | 0.965012 | 0.895019 | 0.923708 | 0.729869 | 0.963677 |
| R4 Reliability p=0.20 | 2 | 0.20 | 0.906763 | 0.917514 | 0.912107 | 0.959977 | 0.887513 | 0.908394 | 0.706685 | 0.959476 |

## Aggregate Table

| Variant | Metric | Mean | Min | Max | Range |
| --- | --- | --- | --- | --- | --- |
| R0 Early Fusion | Full AP50 | 0.938136 | 0.937711 | 0.938560 | 0.000849 |
| R0 Early Fusion | Full AP75 | 0.829337 | 0.827560 | 0.831114 | 0.003554 |
| R0 Early Fusion | F1@0.50 | 0.895004 | 0.893373 | 0.896634 | 0.003261 |
| R0 Early Fusion | w/o RGB AP50 | NA | NA | NA | NA |
| R0 Early Fusion | w/o Thermal AP50 | NA | NA | NA | NA |
| R0 Early Fusion | w/o Event AP50 | NA | NA | NA | NA |
| R1 Reliability p=0.00 | Full AP50 | 0.953245 | 0.952112 | 0.954378 | 0.002266 |
| R1 Reliability p=0.00 | Full AP75 | 0.891458 | 0.889847 | 0.893068 | 0.003221 |
| R1 Reliability p=0.00 | F1@0.50 | 0.906479 | 0.903339 | 0.909620 | 0.006281 |
| R1 Reliability p=0.00 | w/o RGB AP50 | 0.712989 | 0.673004 | 0.752975 | 0.079971 |
| R1 Reliability p=0.00 | w/o Thermal AP50 | 0.330777 | 0.328742 | 0.332811 | 0.004069 |
| R1 Reliability p=0.00 | w/o Event AP50 | 0.568720 | 0.425560 | 0.711880 | 0.286320 |
| R2 Reliability p=0.15 | Full AP50 | 0.959656 | 0.957739 | 0.961573 | 0.003834 |
| R2 Reliability p=0.15 | Full AP75 | 0.884759 | 0.870351 | 0.899166 | 0.028815 |
| R2 Reliability p=0.15 | F1@0.50 | 0.911360 | 0.909858 | 0.912862 | 0.003004 |
| R2 Reliability p=0.15 | w/o RGB AP50 | 0.907911 | 0.904481 | 0.911342 | 0.006861 |
| R2 Reliability p=0.15 | w/o Thermal AP50 | 0.670260 | 0.658199 | 0.682321 | 0.024122 |
| R2 Reliability p=0.15 | w/o Event AP50 | 0.958349 | 0.955474 | 0.961223 | 0.005749 |
| R4 Reliability p=0.20 | Full AP50 | 0.962495 | 0.959977 | 0.965012 | 0.005035 |
| R4 Reliability p=0.20 | Full AP75 | 0.891266 | 0.887513 | 0.895019 | 0.007506 |
| R4 Reliability p=0.20 | F1@0.50 | 0.920861 | 0.912107 | 0.929616 | 0.017509 |
| R4 Reliability p=0.20 | w/o RGB AP50 | 0.916051 | 0.908394 | 0.923708 | 0.015314 |
| R4 Reliability p=0.20 | w/o Thermal AP50 | 0.718277 | 0.706685 | 0.729869 | 0.023184 |
| R4 Reliability p=0.20 | w/o Event AP50 | 0.961577 | 0.959476 | 0.963677 | 0.004201 |

## Interpretation

- Reliability fusion R1 improves early fusion R0 consistently at both seeds: yes.
  - AP50: R1 wins 2/2 seeds, R0 wins 0/2, ties 0.
  - AP75: R1 wins 2/2 seeds, R0 wins 0/2, ties 0.
  - F1@0.50: R1 wins 2/2 seeds, R0 wins 0/2, ties 0.
- R2 p=0.15 versus R4 p=0.20 leadership across seeds:
  - AP50: R2 wins 0/2 seeds, R4 wins 2/2, ties 0.
  - AP75: R2 wins 1/2 seeds, R4 wins 1/2, ties 0.
  - w/o RGB AP50: R2 wins 0/2 seeds, R4 wins 2/2, ties 0.
  - w/o Thermal AP50: R2 wins 0/2 seeds, R4 wins 2/2, ties 0.
  - w/o Event AP50: R2 wins 0/2 seeds, R4 wins 2/2, ties 0.
- R4 leads full-modality AP50 at both seeds and leads all three individual missing-modality AP50 conditions at both seeds; AP75 is split by seed.

## Decision

SELECT R4 AS CLEAN-SPLIT MAIN VARIANT