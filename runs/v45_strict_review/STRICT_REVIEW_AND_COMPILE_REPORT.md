# V45 Strict Review and Compile Report

Generated: 2026-07-09

## Scope

Performed a strict simulated SIVP reviewer pass and manuscript-facing revision after V44 preflight. No new training, tuning, checkpoint selection, split modification, external-data evaluation, robustness experiment, profiling run, or metric recomputation was performed.

## Strict reviewer findings

Major concerns retained:

1. The held-out guard is same-dataset evidence, not external validation.
2. Held-out guard gains are smaller than development-validation gains.
3. Per-seed held-out F1 and AP75 deltas are mixed.
4. AP50/AP75 are project-local metrics, not COCO AP@[0.50:0.95].
5. The study still lacks causal ablations separating stems, softmax gating, and modality dropout.
6. The text schematics are acceptable for technical review but can be replaced with polished vector artwork.

## Manuscript changes made

- Added `submission/sivp/review/STRICT_REVIEWER_REPORT_V45.md`.
- Tightened the abstract in:
  - `submission/sivp/tex/main.tex`
  - root `main.tex`
  - root `main_sivp_snjnl.tex`
- The abstract now explicitly states:
  - the guard check is same-dataset;
  - held-out gains are smaller;
  - per-seed F1 and AP75 guard deltas are mixed;
  - the conclusion is bounded within-dataset evidence.
- The active claim boundary remains unchanged and conservative.

## Compile verification

A local Springer-style compile was run in the assistant sandbox with:

- `sn-jnl.cls` and `sn-basic.bst` copied from the previously provided SIVP source package.
- `latexmk -pdf -interaction=nonstopmode -halt-on-error`.
- `/usr/bin/bibtex.original` because the sandbox `bibtex` symlink is broken.

Compile result:

- Output PDF: `RA_RepDet_SIVP_V45_strict_review_revised_snjnl.pdf`.
- Page count: 10 pages.
- BibTeX/cross-reference closure completed.
- Render verification completed for 10 pages using the PDF skill render workflow.
- Contact-sheet review: no obvious page-level clipping or broken pages observed.

## Final reviewer stance after V45

The manuscript is now stricter and safer than the V44 version. It still has major-revision risk because there is no external dataset, no COCO AP@[0.50:0.95], no causal ablation package, and no real sensor-fault study. However, it is now honest and internally consistent for a SIVP-style engineering-validation submission based on component-disjoint development-validation plus locked same-dataset held-out guard evaluation.

## Current allowed claim

Allowed wording: component-disjoint development-validation evidence plus locked same-dataset held-out TriAir guard evaluation, using descriptive three-seed paired comparisons between matched early fusion and reliability-aware `p=0.15`.

Disallowed wording: external dataset generalization, independent public benchmark test, training-time model selection or tuning using guard results, statistical significance, optimal dropout, calibrated physical sensor reliability, real sensor-fault robustness, or COCO AP@[0.50:0.95].
