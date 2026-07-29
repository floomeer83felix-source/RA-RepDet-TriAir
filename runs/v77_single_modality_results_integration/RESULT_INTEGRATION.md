# V77 Single-Modality Result Integration

Status: `V77_SINGLE_MODALITY_RESULTS_INTEGRATED`

The user supplied nine completed rows for RGB-only, thermal-only, and event-only runs at seeds 0, 1, and 2.

## Recomputed three-seed summary

| Modality | Precision | Recall | F1 | AP50 | AP75 |
| --- | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.8183 ± 0.0065 | 0.5810 ± 0.0090 | 0.6790 ± 0.0080 | 0.6527 ± 0.0086 | 0.3807 ± 0.0085 |
| Thermal-only | 0.8563 ± 0.0055 | 0.7570 ± 0.0080 | 0.8040 ± 0.0070 | 0.8497 ± 0.0080 | 0.6263 ± 0.0111 |
| Event-only | 0.6910 ± 0.0095 | 0.2960 ± 0.0095 | 0.4143 ± 0.0110 | 0.3347 ± 0.0125 | 0.1260 ± 0.0080 |

The full reliability-aware V48 system exceeds thermal-only by `0.1037 ± 0.0094` AP50 and `0.2465 ± 0.0253` AP75 in seed-paired comparisons; all three seed differences are positive.

## Evidence boundary

The supplied rows do not include COCO AP@[0.50:0.95], AR1, AR10, AR100, checkpoint hashes, or evaluator output files. These values are not inferred. If retained checkpoints remain available, a standardized evaluator-only pass should add those fields without retraining.
