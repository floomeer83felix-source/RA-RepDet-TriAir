# RA-RepDet manuscript evaluation - V77 single-modality integration

## Overall recommendation

**Major revision evidence package is complete at the supplied metric scope; pre-submission closure remains.** The trained RGB-only, thermal-only, and event-only controls close the largest basic experimental gap identified in V76. Thermal is the strongest standalone stream, but both multimodal systems exceed thermal-only on AP50 and AP75 in every paired seed. This supports a multimodal benefit rather than a result driven only by the strongest sensor.

The remaining technical reporting gap is narrower: the supplied single-modality table contains precision, recall, F1, AP50, and AP75, but not COCO AP@[0.50:0.95], AR1, AR10, AR100, checkpoint hashes, or evaluator artifacts. These values were not inferred. If the retained checkpoints are available, a standardized evaluation-only pass should add them without retraining.

## Scorecard

| Dimension | Score | Assessment |
| --- | ---: | --- |
| Novelty and relevance | 4.1 / 5 | Lightweight tri-modal dynamic fusion remains relevant. |
| Method clarity | 4.4 / 5 | Architecture, controls, splits, transfer protocol, and boundaries are clear. |
| Experimental rigor | 4.3 / 5 | Three-seed main systems, six fusion controls, locked holdout, transfer study, and trained single-modality baselines are now present. |
| Evidence traceability | 4.4 / 5 | Most evidence is source-locked; V77 values are traceable to the supplied nine-row table but lack checkpoint/evaluator identities. |
| Statistical support | 3.9 / 5 | Three paired seeds show consistent direction, but remain descriptive. |
| Reproducibility | 4.3 / 5 | Frozen protocols and scripts are strong; V77 checkpoint hashes and full evaluator records are still missing. |
| Writing and organization | 4.5 / 5 | The narrative now separates modality contribution, dynamic gating, dropout, holdout evidence, and supervised transfer. |
| Submission readiness | 4.0 / 5 | Experimental coverage is strong; declarations, exact data provenance, and optional full COCO/AR completion remain. |

**Overall: 4.4 / 5.** The manuscript is technically persuasive and suitable for final pre-submission editing after metadata/provenance closure.

## New evidence interpretation

| Modality | F1 | AP50 | AP75 |
| --- | ---: | ---: | ---: |
| RGB-only | 0.6790 ± 0.0080 | 0.6527 ± 0.0086 | 0.3807 ± 0.0085 |
| Thermal-only | 0.8040 ± 0.0070 | 0.8497 ± 0.0080 | 0.6263 ± 0.0111 |
| Event-only | 0.4143 ± 0.0110 | 0.3347 ± 0.0125 | 0.1260 ± 0.0080 |

Thermal-only is strongest across all supplied metrics. Relative to thermal-only, the full reliability-aware system gains `0.1057 ± 0.0133` F1, `0.1037 ± 0.0094` AP50, and `0.2465 ± 0.0253` AP75; every paired difference is positive. Matched early fusion also exceeds thermal-only by `0.0876 ± 0.0101` AP50 and `0.1827 ± 0.0352` AP75.

This closes the basic question of whether fusion merely reproduces the strongest modality. It does not establish calibrated reliability, causal physical-sensor importance, or universal superiority.

## Remaining reviewer concerns

1. The main TriAir development partition still participates in checkpoint retention.
2. The locked holdout is internal to the same local dataset inventory.
3. Three seeds support descriptive consistency but not strong statistical inference.
4. Exact local TriAir version/conversion provenance and final declarations require author confirmation.
5. The V77 single-modality records lack AP@[0.50:0.95], AR metrics, checkpoint hashes, and original evaluator files.

## Recommended final closure

1. Run the standardized evaluator once on the nine retained single-modality checkpoints to add AP@[0.50:0.95], AR1, AR10, and AR100; do not retrain or tune.
2. Record checkpoint SHA256 values and the frozen split/evaluator hashes.
3. Confirm competing interests and author/institution metadata.
4. Verify the exact local TriAir version and conversion mapping.
5. Preserve validation-only, internal-holdout, and supervised exposed-devval wording.

## Acceptance outlook

With metadata/provenance closure, the manuscript is a plausible journal submission. A reviewer may still request an independently acquired sensor-compatible test set or more seeds, but the absence of basic single-modality controls is no longer a defensible major objection.
