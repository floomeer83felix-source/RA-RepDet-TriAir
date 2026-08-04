# RA-RepDet manuscript evaluation - V81 authoritative evidence decision

## Evidence-source decision

On 2026-08-04 the author reviewed the latest `research/ra-repdet-triair` branch and explicitly selected the fresh checkpoint-backed V81 retraining and standardized COCO evaluation as the authoritative single-modality evidence.

The supplied V77/V80 single-modality table remains archived only as historical author-provided evidence. It differs materially from V81 and lacks the complete checkpoint identity package; it must not be used in primary manuscript claims or numerically mixed with V81.

## Authoritative V81 single-modality evidence

All nine models completed the frozen 50-epoch protocol, and all nine retained checkpoints completed standardized COCO evaluation with checkpoint epoch, checkpoint SHA256, frozen split SHA256, and runtime identity recorded.

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.4473 ± 0.0033 | 0.7674 ± 0.0036 | 0.4428 ± 0.0098 | 0.1650 ± 0.0009 | 0.5225 ± 0.0036 | 0.5897 ± 0.0024 |
| Thermal-only | 0.5196 ± 0.0196 | 0.8320 ± 0.0154 | 0.5776 ± 0.0244 | 0.2035 ± 0.0081 | 0.5826 ± 0.0148 | 0.6473 ± 0.0132 |
| Event-only | 0.1949 ± 0.0012 | 0.3657 ± 0.0032 | 0.1943 ± 0.0049 | 0.0751 ± 0.0033 | 0.2694 ± 0.0014 | 0.3558 ± 0.0067 |

Thermal remains the strongest standalone modality on AP@[.50:.95], AP50, AP75, AR1, AR10, and AR100. The primary manuscript interpretation must be recomputed from these values rather than carried over from the supplied V77/V80 table.

## Evidence traceability

- training runs: `9/9`, exactly 50 epochs each;
- standardized evaluator runs: `9/9`;
- checkpoint hashes: `9/9`;
- common split SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`;
- guard access: none;
- tuning, seed replacement, selective rerun, checkpoint substitution: none;
- evidence directories: `runs/v79_single_modality_evaluator_completion/` and `runs/v81_single_modality_retraining_reconciliation/`.

## Overall recommendation

**Proceed with a new V82 manuscript integration.** The experimental evidence source is now resolved in favor of the reproducible checkpoint-backed V81 results. The root V78 manuscript should remain active only until the V82 rewrite, compilation, and rendered-page audit pass.

## Scorecard

| Dimension | Score | Assessment |
| --- | ---: | --- |
| Novelty and relevance | 4.1 / 5 | Lightweight tri-modal dynamic fusion remains relevant. |
| Method clarity | 4.5 / 5 | Architecture, runtime data handling, controls, splits, and transfer boundaries are explicit. |
| Experimental rigor | 4.5 / 5 | Three-seed systems, causal controls, locked holdout, transfer study, and checkpoint-backed single-modality replication are present. |
| Evidence traceability | 4.9 / 5 | V81 includes checkpoint epochs, SHA256 values, split identity, raw evaluator records, and reconciliation. |
| Statistical support | 3.9 / 5 | Three seeds support descriptive consistency, not strong inference. |
| Reproducibility | 4.8 / 5 | Frozen protocols, manifests, checkpoint identities, evaluator outputs, and environment records are archived. |
| Writing and organization | 4.4 / 5 | The current root manuscript still requires V81 integration and removal of supplied-table claims. |
| Submission readiness | 4.3 / 5 | Evidence is strong, but the manuscript must be rebuilt around the selected V81 source before submission. |

**Current overall assessment: 4.5 / 5.** The evidence package is stronger and more reproducible than before; the remaining task is manuscript consistency rather than additional experimentation.

## Required V82 corrections

1. Use V81 as the only primary single-modality table.
2. State that V81 is a fresh retraining replication and not a recovery of the unidentified V77/V80 checkpoints.
3. Recompute multimodal-versus-thermal comparisons only where evaluator definitions are compatible.
4. Do not retain supplied V77/V80 values in the abstract, main results, discussion, or conclusion.
5. Preserve development-validation, internal-holdout, and supervised exposed-MM-UAV-devval boundaries.
6. Preserve the no-competing-interests, data-provenance, 24,223-versus-30,634, and non-redistribution statements.
7. Make no statistical-significance, independent-test, or physical sensor-failure claim.

## Acceptance outlook

After a clean V82 integration, the paper remains a plausible SCI four-zone submission with a materially stronger reproducibility story. Reviewers may still question the internal validation structure, limited seed count, or absence of an independently acquired sensor-compatible test set, but the single-modality evidence itself is now checkpoint-backed and auditable.
