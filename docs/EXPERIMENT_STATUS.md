# Experiment Status

Generated: 2026-07-09

## Current Status

`V44_SIVP_SUBMISSION_PREFLIGHT_COMPLETE`

The V42 locked held-out guard evaluation has been integrated into the active SIVP manuscript, and a V44 submission preflight has been completed. The paper is no longer described as validation-only. The active claim is now: three-seed component-disjoint development-validation evidence plus a locked same-dataset TriAir held-out guard evaluation using fixed seed0/seed1/seed2 checkpoints.

No new training, hyperparameter tuning, checkpoint selection, split modification, robustness experiment, profiling run, external-data evaluation, or metric recomputation was performed during V44. The task performed manuscript-facing claim scan, template compile preflight, render verification, and status/handoff updates only.

## Evidence Inputs

- V42 commit: `187632960a4093778d83c3383e7f5540723a60e1`.
- V42 source lock: `runs/v42_locked_guard_heldout/heldout_guard_source_lock.md/json`.
- V42 summary: `runs/v42_locked_guard_heldout/heldout_guard_summary.md/json`.
- V42 claim boundary: `runs/v42_locked_guard_heldout/heldout_guard_claim_boundary.md`.
- V44 preflight report: `runs/v44_submission_preflight/V44_SUBMISSION_PREFLIGHT_REPORT.md`.
- Guard source manifest: `runs/component_disjoint_v40/guard.txt`.
- Guard rows: 837 images.
- Guard GT boxes: 1264.
- Guard normalized LF SHA256: `9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e`.
- Guard raw file SHA256 recorded by evaluator: `0cf3270c0a73d03caf8d698bb4e9ddb0adba46e688c52d8589f57ea12488881f`.
- Evaluator: `rarepdet/eval_map.py` SHA256 `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715`.
- Metrics helper: `rarepdet/metrics.py` SHA256 `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081`.

## Manuscript updates already integrated

- Updated `submission/sivp/tex/ra_repdet_sivp.tex` to include V42 held-out guard evidence in the Introduction, protocol, Results, Discussion, Limitations, and Conclusion.
- Updated `submission/sivp/tex/main.tex`, root `main.tex`, and `main_sivp_snjnl.tex` title/abstract/keywords to describe component-disjoint development-validation plus locked held-out guard evaluation.
- Created `submission/sivp/tables/Table_9_locked_heldout_guard.tex` as the active held-out guard result table.
- Updated `submission/sivp/tables/Table_1_dataset_and_clean_split.tex` to include held-out guard images and boxes.
- Updated `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex` to include fixed-checkpoint guard evaluation.
- Updated `submission/sivp/tex/related_work_literature_expansion.tex` to match the V43/V44 claim boundary and avoid overlong citation-key lines in template preflight.
- Updated `submission/sivp/review/REVIEWER_REPORT_PRE_SUBMISSION.md` to reflect the stronger V42 evidence state.

## V44 preflight results

- Claim scan: no active `validation-only` wording remains in the checked manuscript text.
- No positive claim of external generalization, statistical significance, optimal dropout, COCO AP50:95 performance, or real sensor-failure robustness was found.
- Remaining restricted terms occur as explicit cautionary/negative claim-boundary statements.
- Springer-style template compile: completed in the assistant sandbox using `sn-jnl.cls` and `sn-basic.bst` from the previously provided SIVP source package.
- BibTeX/cross-reference closure: completed in the sandbox using `/usr/bin/bibtex.original` because the sandbox `bibtex` symlink is broken.
- Output PDF: `RA_RepDet_SIVP_V44_submission_preflight_snjnl.pdf`.
- Page count: 10 pages.
- Render verification: 10 pages rendered; no obvious page-level clipping or broken pages observed.
- Minor residual layout warning: one overfull hbox of approximately 22.33 pt around a displayed equation/table-area line.

## Development-validation descriptive summary

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.011629 | 0.016501 | 3 |
| Recall | +0.024487 | 0.026581 | 3 |
| F1 | +0.018524 | 0.006208 | 3 |
| AP50 | +0.016064 | 0.005699 | 3 |
| AP75 | +0.064657 | 0.016415 | 3 |

## Held-out guard descriptive summary

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.003213 | 0.010920 | 3 |
| Recall | +0.010549 | 0.016220 | 3 |
| F1 | +0.006946 | 0.008943 | 3 |
| AP50 | +0.008562 | 0.006229 | 3 |
| AP75 | +0.002173 | 0.017305 | 3 |

## Current claim boundary

Allowed wording: component-disjoint development-validation evidence plus locked same-dataset held-out TriAir guard evaluation, using descriptive three-seed paired comparisons between matched early fusion and reliability-aware `p=0.15`.

Disallowed wording: external dataset generalization, independent public benchmark test, training-time model selection or tuning using guard results, statistical significance, optimal dropout, calibrated physical sensor reliability, real sensor-fault robustness, or COCO AP@[0.50:0.95].

## Remaining scientific limitations

- The held-out guard partition is within the TriAir project dataset, not an external dataset.
- The evidence is descriptive with three seed pairs only.
- The guard results must not be used for future model selection without rewriting the claim boundary.
- No causal ablation separates stems, dynamic gate, and modality dropout.
- No COCO mAP@[0.50:0.95] package is available.
- Dataset provider provenance remains only partially resolved by naming TriAir as public.
- Label-quality review remains incomplete.

## Remaining submission-packaging items

- Use the official Springer/SIVP template package in the final author environment.
- Confirm that `sn-jnl.cls`/`sn-basic.bst` are included or supplied according to the journal submission workflow.
- Optional replacement of simple text schematics with high-resolution vector artwork.
- Public release/archive DOI and release metadata if required by the submission workflow.
