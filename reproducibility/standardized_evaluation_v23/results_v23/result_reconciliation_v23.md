# V23 Result Reconciliation

All detector outputs were generated with a detector-output score threshold of 0.001. AP50 and AP75 were computed from this common candidate set. Precision, recall, and F1 were computed at an operating threshold of 0.50.

AP50/AP75 are project-local single-class metrics and are not COCO AP50:95.

## R4 Main Result

| Metric | V22 | V23 |
| --- | --- | --- |
| AP50 | 0.962495 | 0.9628656208515167 |
| AP75 | 0.891266 | 0.8917860090732574 |
| F1 | 0.920861 | 0.920861212399899 |

## Completeness

- Full-input runs completed: 8 / 8
- Missing-modality rows completed: 42 / 42 total rows (including supplementary single-modality rows)
- Manuscript missing-modality cells completed: 24 / 24

## Blockers

- Missing exact v22 manuscript source package: RA_RepDet_SIVP_v22_MethodsMetricsPolish_Source*


