# Current Task

## Active task

`V82_INTEGRATE_AUTHORITATIVE_V81_SINGLE_MODALITY_EVIDENCE`

## Author decision

On 2026-08-04 the author reviewed the latest pushed `research/ra-repdet-triair` branch and explicitly selected the checkpoint-backed V81 retraining/evaluation results as the authoritative single-modality evidence.

The supplied V77/V80 rows remain historical reconciliation records only. They must not appear as the primary single-modality table and must not be mixed numerically with V81.

## Authoritative V81 summary

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.4473 ± 0.0033 | 0.7674 ± 0.0036 | 0.4428 ± 0.0098 | 0.1650 ± 0.0009 | 0.5225 ± 0.0036 | 0.5897 ± 0.0024 |
| Thermal-only | 0.5196 ± 0.0196 | 0.8320 ± 0.0154 | 0.5776 ± 0.0244 | 0.2035 ± 0.0081 | 0.5826 ± 0.0148 | 0.6473 ± 0.0132 |
| Event-only | 0.1949 ± 0.0012 | 0.3657 ± 0.0032 | 0.1943 ± 0.0049 | 0.0751 ± 0.0033 | 0.2694 ± 0.0014 | 0.3558 ± 0.0067 |

## Required manuscript work

1. Copy the V78 provenance-closed manuscript into a new V82 manuscript directory; do not overwrite V78 or the supplied-table V80 draft.
2. Replace the primary single-modality evidence with the V81 per-seed and three-seed summary values from:
   - `runs/v79_single_modality_evaluator_completion/per_run.csv`;
   - `runs/v79_single_modality_evaluator_completion/summary.md`;
   - `runs/v81_single_modality_retraining_reconciliation/checkpoint_manifest.json`.
3. State that V81 is a fresh retraining replication under the frozen protocol, not a recovery of the unidentified V77/V80 checkpoints.
4. Remove supplied V77/V80 single-modality values from the abstract, headline results, main tables, discussion, conclusion, and acceptance assessment. They may be mentioned only in a compact provenance/reconciliation note if necessary.
5. Recompute every multimodal-versus-best-single-modality comparison using the authoritative V81 thermal-only values and compatible metrics only. Do not compare COCO AP@[.50:.95] to project-local AP or mix evaluator contracts.
6. Preserve all existing boundaries:
   - component-disjoint development-validation is not an independent test;
   - the 837-image holdout is internal;
   - MM-UAV is supervised target-domain adaptation on exposed devval;
   - three seeds support descriptive consistency, not statistical significance;
   - no physical sensor-failure robustness claim;
   - 24,223 paper-reported vehicles and 30,634 current-archive valid label lines remain separate;
   - no competing interests;
   - no dataset redistribution.
7. Update `ARTICLE_EVALUATION.md` using V81 as the evidence source.
8. Build the manuscript twice with pdfLaTeX, check citations/references/overfull boxes, render every page, and inspect all revised result tables.
9. Switch the root manuscript entrypoint only after the V82 build and audit pass.

## Evidence identity

- V81 training: `9/9`, 50 epochs each;
- V81 evaluation: `9/9`;
- checkpoint SHA256: `9/9`;
- common validation split SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`;
- guard access, tuning, seed replacement, selective rerun, checkpoint substitution: none.

## Completion state

The evidence-source decision is complete. Manuscript integration is the only active scientific-writing task. Until V82 passes build and rendered-page audit, the root V78 manuscript remains the repository entrypoint.

## Recommended commit message

`docs: integrate authoritative V81 single-modality evidence`
