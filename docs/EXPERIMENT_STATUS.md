# Experiment Status

Updated: 2026-08-04

## Active status

`V81_CHECKPOINT_BACKED_SINGLE_MODALITY_EVIDENCE_SELECTED_AUTHORITATIVE`

## Author evidence-source decision

On 2026-08-04, after reviewing the latest pushed branch `research/ra-repdet-triair`, the author explicitly selected the fresh checkpoint-backed V81 retraining and standardized COCO evaluation as the authoritative single-modality evidence for all subsequent manuscript work.

The supplied V77/V80 tables remain archived for historical reconciliation only. They must not be used as the primary single-modality result, silently mixed with V81, or described as originating from the V81 checkpoints.

## Authoritative V81 single-modality results

All nine models completed the frozen 50-epoch protocol and all nine retained `best.pt` checkpoints completed one standardized COCO evaluation. Values below are mean ± sample standard deviation over seeds 0, 1, and 2.

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.4473 ± 0.0033 | 0.7674 ± 0.0036 | 0.4428 ± 0.0098 | 0.1650 ± 0.0009 | 0.5225 ± 0.0036 | 0.5897 ± 0.0024 |
| Thermal-only | 0.5196 ± 0.0196 | 0.8320 ± 0.0154 | 0.5776 ± 0.0244 | 0.2035 ± 0.0081 | 0.5826 ± 0.0148 | 0.6473 ± 0.0132 |
| Event-only | 0.1949 ± 0.0012 | 0.3657 ± 0.0032 | 0.1943 ± 0.0049 | 0.0751 ± 0.0033 | 0.2694 ± 0.0014 | 0.3558 ± 0.0067 |

## Evidence identity

- training completion: `9/9`, exactly 50 epochs each;
- standardized COCO evaluation: `9/9`;
- retained checkpoint epoch: recorded for `9/9`;
- checkpoint SHA256: recorded for `9/9`;
- validation split SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f` for `9/9`;
- guard access: none;
- tuning, seed replacement, selective rerun, or checkpoint substitution: none;
- compact evidence: `runs/v79_single_modality_evaluator_completion/` and `runs/v81_single_modality_retraining_reconciliation/`.

## Reconciliation boundary

V81 differs materially from the supplied V77/V80 table. This is not display rounding. The V81 checkpoints are fresh retraining outputs and are not recovered identities for the earlier supplied rows. The older rows remain available only to document the discrepancy and provenance history.

## Manuscript status

The repository root manuscript is still V78 until a clean new manuscript version is built. The next manuscript revision must use the authoritative V81 table above, explicitly describe it as a fresh checkpoint-backed replication, and remove the supplied V77/V80 single-modality table from primary claims. No value may be combined across the two evidence sets.

## Existing scientific boundaries

The component-disjoint development-validation, locked internal holdout, and supervised exposed-MM-UAV-devval boundaries remain unchanged. V81 is not an independent public test, does not establish statistical significance, and does not demonstrate physical sensor-failure robustness.
