# Experiment Status

Updated: 2026-07-29

## Active status

`V75_V73_CORRECTED_SEED_LEVEL_EVIDENCE_INTEGRATED`

## Corrected V73 seed-level evidence

The nine corrected V73 seed-level rows are now authoritative. Independently recomputed three-seed results are:

| Method | AP mean ± sample std | AP50 mean | AP75 mean | AR100 mean |
| --- | ---: | ---: | ---: | ---: |
| Scratch Equal | 0.2210 ± 0.0030 | 0.5567 | 0.1347 | 0.3530 |
| TriAir Init Equal | 0.2340 ± 0.0020 | 0.5797 | 0.1510 | 0.3717 |
| TriAir Init Reliability | 0.2503 ± 0.0025 | 0.6077 | 0.1750 | 0.3920 |

Paired AP differences are `0.0130 ± 0.0010`, `0.0163 ± 0.0006`, and `0.0293 ± 0.0006`; all are positive for seeds 0, 1, and 2.

## Manuscript integration

The active manuscript now contains the corrected summary, all nine seed-level rows, a paired AP table, updated Figure 5, revised discussion and conclusion, and an updated article evaluation. The earlier aggregate-only limitation has been removed.

## Validation

- local PDF pages: `13`;
- two pdfLaTeX passes: `PASS`;
- undefined citations/references: `0`;
- overfull boxes: `0`;
- rendered-page audit: `PASS`;
- new experiment, inference, or tuning: `none`;
- protected training files changed: `false`.

## Article evaluation

Updated readiness: `3.9 / 5`, with major revision still recommended before submission because canonical dataset citations, declarations, validation-only TriAir evidence, and limited replication remain unresolved.

## Scientific boundary

The MM-UAV result is supervised transfer on an exposed devval split. It is not independent/blind external validation, official untouched-test performance, statistical-significance evidence, or generalization without MM-UAV labels.
