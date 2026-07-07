# V40 Component-Disjoint Validation Report

Status: **R4-completed**

## Split Audit

- Final gate: **PASS**
- Inventory rows: 10489; components: 45; largest component: 4077
- Split rows: train=7439, val=2213, guard=837
- Train/val distance-16 violation pairs: 0
- Train/guard distance-16 violation pairs: 0
- Val/guard distance-16 violation pairs: 0
- Component crossing count: 0
- Missing/unknown/duplicate assigned paths: 0 / 0 / 0

## Standardized Evaluation

| Seed | AP50 | AP75 | Precision | Recall | F1 | Eval FPS |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.905695 | 0.744196 | 0.872663 | 0.851392 | 0.861896 | 23.320844 |
| 2 | 0.904495 | 0.759297 | 0.889808 | 0.829218 | 0.858445 | 25.915243 |

Two-seed AP50 mean/stdev: 0.905095 / 0.000848.
Two-seed AP75 mean/stdev: 0.751747 / 0.010678.

## Missing-Modality Summary

| Mode | AP50 Mean | AP50 Stdev | Seed0 AP50 | Seed2 AP50 |
|---|---:|---:|---:|---:|
| event_only | 0.014163 | 0.007060 | 0.009171 | 0.019156 |
| full | 0.905095 | 0.000848 | 0.905695 | 0.904495 |
| no_event | 0.898558 | 0.002077 | 0.897090 | 0.900027 |
| no_rgb | 0.909699 | 0.000031 | 0.909721 | 0.909677 |
| no_thermal | 0.377464 | 0.015269 | 0.366667 | 0.388261 |
| rgb_only | 0.377355 | 0.010632 | 0.369837 | 0.384873 |
| thermal_only | 0.909995 | 0.000539 | 0.910376 | 0.909613 |

## Efficiency

- Params: 6593293
- GFLOPs: 105.981501 (detector)
- FPS: 51.074976
- Latency: 19.579060 ms/img
- CUDA max memory: 236.40 MB

## Notes

- The old V39 candidate was not overwritten or relabeled as passing.
- Training began only after the V40 split audit passed.
- GPU jobs were run sequentially: seed0 train/eval, seed2 train/eval, then missing-modality/profiling.
- Checkpoints and weights remain local and are excluded from commit scope.
- V40 results are validation-only and separate from manuscript headline claims.
- PyTorch emitted a CuBLAS deterministic warning during training because `CUBLAS_WORKSPACE_CONFIG` was not set before launch; this is recorded as a reproducibility caveat.
