# Polished Preview Compile

Generated: 2026-07-09

## Scope

This note records the assistant-side polished manuscript preview generated after the SIVP text cleanup. No training, evaluation, checkpoint loading, raw data access, prediction-cache access, or guard/test access was performed.

## Manuscript polish performed

- Polished the active SIVP body text in `submission/sivp/tex/ra_repdet_sivp.tex`.
- Updated the title/abstract/keywords and declarations in:
  - `submission/sivp/tex/main.tex`
  - root `main.tex`
  - root `main_sivp_snjnl.tex`
- Aligned `Table_1_dataset_and_clean_split.tex` with V40 component-disjoint evidence.
- Aligned `Table_2_implementation_and_reproducibility.tex` with V41 seed0/seed1/seed2 p=0.15 active runs.
- Polished `related_work_literature_expansion.tex` to remove draft-screening and quartile-style language.
- Added a separate `Code Availability` declaration while keeping the public TriAir dataset statement concise.

## Local PDF preview

A local LaTeX preview PDF was generated in the assistant sandbox as:

`RA_RepDet_SIVP_V41_polished_compiled_preview.pdf`

Because the sandbox does not contain the Springer `sn-jnl` class or the full repository clone, the preview was compiled with a temporary fallback article-style class wrapper and a simplified references note. The preview is for reading/layout review, not a final Springer/SIVP submission build.

## Verification

- Local `pdflatex` completed successfully twice.
- Render verification completed for 7 pages using the PDF skill render workflow.
- No page-level clipping or obvious layout break was observed in the rendered contact-sheet review.

## Remaining submission blockers

- Replace Fig. 1--6 placeholders with final approved assets.
- Run the real Springer/SIVP `sn-jnl` class build in a local environment.
- Complete full BibTeX/cross-reference closure.
- Resolve public release/archive DOI if required by the target submission workflow.
- Confirm any TriAir provider/version/license/synchronization details needed beyond naming the public dataset.
- Complete label-quality review if required for a stronger submission package.
