# Experiment Status

Updated: 2026-08-04

## Active status

`V82_AUTHORITATIVE_V81_MANUSCRIPT_BUILT_AND_ACTIVATED`

## Authoritative evidence decision

The author selected the fresh checkpoint-backed V81 retraining and standardized COCO evaluation as the authoritative single-modality evidence. The earlier V77/V80 author-supplied table remains archived for historical reconciliation only and is not used in V82 primary claims.

## Authoritative V81 single-modality results

Values are mean ± sample standard deviation over seeds 0, 1, and 2.

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.4473 ± 0.0033 | 0.7674 ± 0.0036 | 0.4428 ± 0.0098 | 0.1650 ± 0.0009 | 0.5225 ± 0.0036 | 0.5897 ± 0.0024 |
| Thermal-only | 0.5196 ± 0.0196 | 0.8320 ± 0.0154 | 0.5776 ± 0.0244 | 0.2035 ± 0.0081 | 0.5826 ± 0.0148 | 0.6473 ± 0.0132 |
| Event-only | 0.1949 ± 0.0012 | 0.3657 ± 0.0032 | 0.1943 ± 0.0049 | 0.0751 ± 0.0033 | 0.2694 ± 0.0014 | 0.3558 ± 0.0067 |

## Compatible multimodal-versus-thermal contrasts

| System | Metric | Mean delta | Sample SD | Positive seeds |
| --- | --- | ---: | ---: | ---: |
| Reliability-aware p=0.15 | AP | +0.1960 | 0.0329 | 3/3 |
| Reliability-aware p=0.15 | AP50 | +0.1215 | 0.0154 | 3/3 |
| Reliability-aware p=0.15 | AP75 | +0.2952 | 0.0349 | 3/3 |
| Matched early fusion | AP | +0.1606 | 0.0223 | 3/3 |
| Matched early fusion | AP50 | +0.1053 | 0.0199 | 3/3 |
| Matched early fusion | AP75 | +0.2314 | 0.0265 | 3/3 |

These are descriptive component-disjoint development-validation comparisons under compatible standardized COCO definitions. No significance test is claimed.

## Evidence identity

- V81 training completion: `9/9`, exactly 50 epochs each;
- standardized COCO evaluation: `9/9`;
- retained checkpoint epoch and SHA256: `9/9`;
- common validation split SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`;
- guard access, tuning, seed replacement, selective rerun, checkpoint substitution: none;
- source artifacts: `runs/v79_single_modality_evaluator_completion/` and `runs/v81_single_modality_retraining_reconciliation/`.

## V82 manuscript validation

- active root manuscript: V82;
- PDF pages: `16`;
- two pdfLaTeX passes: `PASS`;
- undefined citations/references: `0`;
- overfull boxes: `0`;
- PDF preflight: `PASS`;
- rendered-page audit: `16/16 PASS`;
- new training or evaluation performed by integration task: `none`.

## Scientific boundary

The component-disjoint validation partition participates in checkpoint retention, the 837-image holdout is internal, and MM-UAV uses supervised target-domain labels on an exposed devval split. V82 does not claim statistical significance, independent public-test performance, calibrated sensor reliability, or physical sensor-failure robustness.
