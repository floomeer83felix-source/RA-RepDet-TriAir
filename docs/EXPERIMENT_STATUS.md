# Experiment Status

Updated: 2026-07-29

## Active status

`V74_TRIAIR_MANUSCRIPT_MMUAV_TRANSFER_STUDY_INTEGRATED`

## Corrected manuscript integration

The complete SIVP manuscript now integrates the authoritative corrected V72-V73 aggregate evidence:

| Training setting | AP | AP50 | AP75 | AR100 | Conclusion |
| --- | ---: | ---: | ---: | ---: | --- |
| Frozen TriAir, naive-grid zero-shot | 0.000 | 0.000 | 0.000 | 0.000 | Direct transfer failed |
| MM-UAV Scratch Equal | 0.220 ± 0.007 | 0.557 | 0.134 | 0.351 | Aligned supervised training recovered performance |
| TriAir Init Equal | 0.233 ± 0.006 | 0.580 | 0.151 | 0.374 | Source-domain pretraining was beneficial |
| TriAir Init Reliability | 0.250 ± 0.008 | 0.610 | 0.178 | 0.398 | Reliability-aware fusion improved performance further |

The old negative-transfer conclusion, invalidated nine-row per-seed table, paired differences, ranges, and seed-direction claims have been removed from all active manuscript source.

## Active manuscript source

- entrypoint: `main.tex`;
- SIVP wrapper: `main_sivp_snjnl.tex`;
- complete split source: `submission/v74_corrected_manuscript/main_part1.tex` through `main_part4.tex`;
- figure generator: `make_figures.py`;
- scientific and submission-readiness review: `ARTICLE_EVALUATION.md`.

## Validation

The uploaded complete source package was built with two pdfLaTeX passes after regenerating all figures:

- manuscript pages: `12`;
- fatal LaTeX errors: `0`;
- undefined citations: `0`;
- undefined references: `0`;
- overfull boxes: `0`;
- rendered-page audit: `PASS`;
- protected training files changed: `false`;
- new experiment, inference, or tuning: `none`.

Compact traceability and build evidence are stored under:

`runs/v74_triair_manuscript_mmuav_cross_dataset_transfer_integration/`

## Article evaluation

The manuscript evaluation recommends **major revision before submission** with an overall readiness score of `3.6 / 5`. The technical narrative is coherent and appropriately scoped, but submission closure still requires:

1. verified canonical TriAir and MM-UAV dataset citations;
2. author confirmation of the competing-interests declaration and final institutional metadata;
3. corrected V73 seed-level records if paired, seed-consistency, reproducibility, or statistical claims are desired.

## Scientific boundary

V73 remains an `MM-UAV supervised cross-dataset transfer benchmark with learned feature alignment`. It uses MM-UAV labels and an exposed devval split. It is not zero-shot success, independent/blind external validation, official untouched-test performance, statistically significant external generalization, or evidence of generalization without MM-UAV labels.

## Authorization boundary

V74 is complete. No new experiment, evaluation, rerun, tuning, seed reconstruction, or public submission is authorized by this completion record.
