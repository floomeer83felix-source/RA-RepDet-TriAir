# Experiment Status

Updated: 2026-07-29

## Active status

`V77_SINGLE_MODALITY_RESULTS_INTEGRATED_MANUSCRIPT_REBUILT`

## Completed single-modality evidence

The user supplied nine completed component-disjoint validation rows for RGB-only, thermal-only, and event-only runs at seeds 0, 1, and 2. Independent recomputation gives:

| Modality | Precision | Recall | F1 | AP50 | AP75 |
| --- | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.8183 ± 0.0065 | 0.5810 ± 0.0090 | 0.6790 ± 0.0080 | 0.6527 ± 0.0086 | 0.3807 ± 0.0085 |
| Thermal-only | 0.8563 ± 0.0055 | 0.7570 ± 0.0080 | 0.8040 ± 0.0070 | 0.8497 ± 0.0080 | 0.6263 ± 0.0111 |
| Event-only | 0.6910 ± 0.0095 | 0.2960 ± 0.0095 | 0.4143 ± 0.0110 | 0.3347 ± 0.0125 | 0.1260 ± 0.0080 |

Thermal-only is the strongest standalone stream. The full reliability-aware V48 system exceeds thermal-only by `0.1057 ± 0.0133` F1, `0.1037 ± 0.0094` AP50, and `0.2465 ± 0.0253` AP75 in seed-paired comparisons; every difference is positive.

## Manuscript integration

The active manuscript now includes:

- the nine per-seed single-modality rows;
- the independently recomputed summary table;
- paired comparisons against matched early and full reliability-aware fusion;
- revised abstract, contributions, discussion, conclusion, and article evaluation.

## Evidence boundary

The supplied rows do not include COCO AP@[0.50:0.95], AR1, AR10, AR100, checkpoint hashes, or original evaluator artifacts. These fields were not inferred. A standardized evaluator-only pass on retained checkpoints remains recommended; no retraining or tuning is authorized.

## Validation

- revised PDF pages: `15`;
- two pdfLaTeX passes: `PASS`;
- undefined citations/references: `0`;
- overfull boxes: `0`;
- rendered-page audit: `PASS`;
- new training performed by this integration task: `none`.

## Article evaluation

Updated readiness: `4.4 / 5`. The major experimental control gap is closed. Remaining submission closure is author metadata/declarations, exact local TriAir provenance, and optional completion of AP@[0.50:0.95]/AR plus checkpoint/evaluator identities.
