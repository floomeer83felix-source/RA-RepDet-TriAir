# V81 single-modality retraining reconciliation

Status: `V81_RETRAINING_AND_STANDARDIZED_EVALUATION_COMPLETE_MATERIAL_RECONCILIATION_DIFFERENCE`.

Nine fresh V81 runs and nine standardized COCO evaluations completed. 
All records use split SHA256 `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`.

## Mean comparison

| Modality | Metric | V81 | Supplied V80 | Delta |
| --- | --- | ---: | ---: | ---: |
| RGB-only | ap50_95 | 0.4473 | 0.3073 | +0.1399 |
| RGB-only | ap50 | 0.7674 | 0.6527 | +0.1148 |
| RGB-only | ap75 | 0.4428 | 0.3807 | +0.0621 |
| RGB-only | ar1 | 0.1650 | 0.2857 | -0.1206 |
| RGB-only | ar10 | 0.5225 | 0.4550 | +0.0675 |
| RGB-only | ar100 | 0.5897 | 0.4830 | +0.1067 |
| Thermal-only | ap50_95 | 0.5196 | 0.4633 | +0.0563 |
| Thermal-only | ap50 | 0.8320 | 0.8497 | -0.0177 |
| Thermal-only | ap75 | 0.5776 | 0.6263 | -0.0487 |
| Thermal-only | ar1 | 0.2035 | 0.3877 | -0.1841 |
| Thermal-only | ar10 | 0.5826 | 0.5973 | -0.0148 |
| Thermal-only | ar100 | 0.6473 | 0.6320 | +0.0153 |
| Event-only | ap50_95 | 0.1949 | 0.1020 | +0.0929 |
| Event-only | ap50 | 0.3657 | 0.3347 | +0.0310 |
| Event-only | ap75 | 0.1943 | 0.1260 | +0.0683 |
| Event-only | ar1 | 0.0751 | 0.1220 | -0.0469 |
| Event-only | ar10 | 0.2694 | 0.2437 | +0.0258 |
| Event-only | ar100 | 0.3558 | 0.2710 | +0.0848 |

## Decision

The differences are material and cannot be treated as display rounding. The V81 checkpoints are fresh retraining outputs, while the supplied V77/V80 rows have no checkpoint identity package. Both evidence sets are retained and neither is silently overwritten. V78 remains authoritative pending an explicit evidence-source decision.

No guard access, tuning, seed replacement, selective rerun, or checkpoint substitution occurred. Large checkpoint files remain local.
