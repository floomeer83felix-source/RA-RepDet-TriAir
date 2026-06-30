# SIVP Pre-Final Source Package

Status: PRE-FINAL. This package cannot be submitted until final figures, final publication tables, author details, declarations, and a final checked PDF are approved by the authors.

Author placeholders appear in `submission/sivp/tex/main.tex`, `submission/sivp/tex/ra_repdet_sivp.tex`, and the files under `submission/sivp/metadata/`. They must be replaced with verified author names, affiliations, ORCIDs, correspondence information, funding information, acknowledgments, contribution statements, and competing-interest statements before submission.

Final artwork placeholders appear in `submission/sivp/tex/ra_repdet_sivp.tex`. The files listed in `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md` must later be replaced by assistant-produced and author-approved final scientific figures. No generated-art image may be used as scientific evidence.

Final table placeholders are listed in `submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md`. The numerical sources are the existing `manuscript/tables/` CSV files, but final publication table formatting is intentionally deferred.

Compilation dry run: compile `submission/sivp/tex/main.tex` using the official Springer Nature `sn-jnl` class and the `iicol` option. The current build is a placeholder-only dry run and must not be treated as a submission PDF.

Validation steps before final submission:

1. Replace all author and declaration placeholders.
2. Insert final PDF/EPS figures approved by the authors.
3. Format final tables to fit the 10-page two-column SIVP target.
4. Re-run citation validation and compile the complete LaTeX source.
5. Confirm that no datasets, weights, raw predictions, cache files, or local rendered draft panels are included.
