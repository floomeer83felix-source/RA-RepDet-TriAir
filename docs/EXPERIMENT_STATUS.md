# Experiment Status

Generated: 2026-07-09

## Current Status

`V45_STRICT_REVIEW_REVISION_COMPLETE`

A strict simulated SIVP reviewer pass has been completed after V44 preflight. The manuscript remains based on component-disjoint development-validation plus locked same-dataset TriAir held-out guard evaluation. The paper is not described as validation-only, and the strict reviewer pass further tightened the abstract to state that the held-out guard is same-dataset evidence, that the held-out gains are smaller than development-validation gains, and that per-seed held-out F1/AP75 deltas are mixed.

No new training, hyperparameter tuning, checkpoint selection, split modification, robustness experiment, profiling run, external-data evaluation, or metric recomputation was performed during V45. The task performed reviewer-style critique, manuscript wording revisions, template compile, render verification, and status/handoff updates only.

## Evidence Inputs

- V42 commit: `187632960a4093778d83c3383e7f5540723a60e1`.
- V42 source lock: `runs/v42_locked_guard_heldout/heldout_guard_source_lock.md/json`.
- V42 summary: `runs/v42_locked_guard_heldout/heldout_guard_summary.md/json`.
- V42 claim boundary: `runs/v42_locked_guard_heldout/heldout_guard_claim_boundary.md`.
- V44 preflight report: `runs/v44_submission_preflight/V44_SUBMISSION_PREFLIGHT_REPORT.md`.
- V45 strict review report: `submission/sivp/review/STRICT_REVIEWER_REPORT_V45.md`.
- V45 compile report: `runs/v45_strict_review/STRICT_REVIEW_AND_COMPILE_REPORT.md`.

## V45 manuscript updates

- Added `submission/sivp/review/STRICT_REVIEWER_REPORT_V45.md`.
- Tightened the abstract in `submission/sivp/tex/main.tex`, root `main.tex`, and root `main_sivp_snjnl.tex`.
- The abstract now explicitly states that the 837-image guard check is a same-dataset evaluation and that the held-out guard mean gains are smaller with mixed per-seed F1/AP75 deltas.
- The active claim boundary remains component-disjoint development-validation plus locked same-dataset held-out TriAir guard evaluation.

## V45 compile and render verification

- Output PDF: `RA_RepDet_SIVP_V45_strict_review_revised_snjnl.pdf`.
- Page count: 10 pages.
- Springer-style template compile completed in the assistant sandbox using `sn-jnl.cls` and `sn-basic.bst` from the previously provided SIVP source package.
- BibTeX/cross-reference closure completed using `/usr/bin/bibtex.original` because the sandbox `bibtex` symlink is broken.
- Render verification: 10 pages rendered with no obvious page-level clipping or broken pages observed.

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
