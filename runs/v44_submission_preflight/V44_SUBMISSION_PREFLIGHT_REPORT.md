# V44 SIVP Submission Preflight Report

Generated: 2026-07-09

## Scope

Performed final manuscript-facing preflight after V43 integration of the V42 locked held-out guard evidence. No new training, tuning, checkpoint selection, split modification, external-data evaluation, robustness experiment, profiling run, or metric recomputation was performed.

## Source state checked

- Active branch: `research/ra-repdet-triair`.
- Evidence state: component-disjoint development-validation plus locked same-dataset TriAir held-out guard evaluation.
- Latest manuscript updates checked:
  - `submission/sivp/tex/main.tex`
  - `submission/sivp/tex/ra_repdet_sivp.tex`
  - `submission/sivp/tex/related_work_literature_expansion.tex`
  - `submission/sivp/tables/Table_1_dataset_and_clean_split.tex`
  - `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex`
  - `submission/sivp/tables/Table_8_three_seed_interim_devval.tex`
  - `submission/sivp/tables/Table_9_locked_heldout_guard.tex`

## Claim scan

Scan target terms:

- `validation-only`
- `independent test`
- `external generalization`
- `statistical significance`
- `optimal`
- `robustness`
- `COCO AP50:95`
- `sensor-failure`
- `external-dataset generalization`
- `independent public benchmark test`

Result:

- No active `validation-only` wording remains in the checked manuscript text.
- No positive claim of external generalization, statistical significance, optimal dropout, COCO AP50:95 performance, or real sensor-failure robustness was found.
- Remaining restricted terms occur as explicit cautionary/negative claim-boundary statements, e.g. avoiding external-dataset generalization, COCO AP50:95, and physical sensor-failure robustness.

## Springer/SIVP template compile

A local Springer-style compile was run in the assistant sandbox with:

- `sn-jnl.cls` and `sn-basic.bst` copied from the previously provided SIVP source package.
- `latexmk -pdf -interaction=nonstopmode -halt-on-error`.
- `/usr/bin/bibtex.original` was used because the sandbox `bibtex` symlink is broken.

Compile result:

- PDF generated successfully.
- Output PDF: `RA_RepDet_SIVP_V44_submission_preflight_snjnl.pdf`.
- Page count: 10 pages.
- BibTeX/cross-reference closure completed in the sandbox.
- Final log check: no unresolved references or undefined citations reported.
- One minor overfull hbox remained: approximately 22.33 pt around a displayed equation/table-area line. It did not cause page-level clipping in render review.

## Render verification

The generated PDF was rendered to PNG pages using the PDF skill render workflow.

- Rendered pages: 10.
- Contact-sheet review: no obvious page-level clipping or broken pages observed.
- Tables 8 and 9 rendered inside the page area in the preview.

## Remaining submission-packaging items

- Use the official Springer/SIVP template package in the final author environment.
- Confirm that `sn-jnl.cls`/`sn-basic.bst` are included or supplied according to the journal submission workflow.
- Optionally replace text schematics with higher-resolution vector artwork.
- Confirm public repository state and any release/DOI requirement.
- TriAir provider/version/license/synchronization details remain author-confirmation items beyond naming the public dataset.
- Label-quality review remains incomplete.

## Current allowed claim

Allowed wording: component-disjoint development-validation evidence plus locked same-dataset held-out TriAir guard evaluation, using descriptive three-seed paired comparisons between matched early fusion and reliability-aware `p=0.15`.

Disallowed wording: external dataset generalization, independent public benchmark test, training-time model selection or tuning using guard results, statistical significance, optimal dropout, calibrated physical sensor reliability, real sensor-fault robustness, or COCO AP@[0.50:0.95].
