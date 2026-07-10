# V47 Springer Compile and Citation Closure

Generated: 2026-07-10

## Scope

Compiled the V47 restructured SIVP manuscript after the recent-journal literature expansion. No model training, evaluation, checkpoint selection, metric recomputation, split modification, or holdout access was performed.

## Citation closure

A static scan of `submission/sivp/tex/ra_repdet_sivp.tex` found exactly 40 unique cited BibTeX keys.

Composition:

- 28 newly added formal 2023--2024 journal articles in `submission/sivp/tex/references_recent_q12_2023_2025.bib`;
- 3 recent formal journal references already present in the repository;
- 9 foundational primary-source exceptions retained for detector, backbone, benchmark, and missing-modality provenance.

Checks:

- cited keys: 40;
- available matching BibTeX entries: 40;
- missing cited keys: 0;
- unused entries in the compile-specific cited set: 0;
- `\nocite{*}`: not used.

## Compile procedure

The assistant sandbox did not have outbound Git access, so the active V47 manuscript files were reconstructed from the connected GitHub branch and compiled with the Springer class files from the previously supplied source package.

Commands:

```text
pdflatex -interaction=nonstopmode -halt-on-error main.tex
/usr/bin/bibtex.original main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The sandbox `bibtex` symlink was unavailable; `/usr/bin/bibtex.original` was used. The supplied `sn-basic.bst` was copied to the bibliography style name requested by the active `sn-jnl` class option for this preflight build.

## Result

- Output: `RA_RepDet_SIVP_V47_structure_recent_literature_snjnl.pdf`.
- Pages: 10.
- Undefined citations: 0.
- Undefined cross-references: 0.
- BibTeX completed successfully.
- All 40 cited works were printed in the reference list.

## Render verification

The final PDF was rendered at 180 dpi using the repository PDF workflow.

- rendered pages: 10;
- obvious page-level clipping: none observed;
- broken pages or missing tables: none observed;
- Tables 8 and 9 remained within the page area;
- reference list occupied pages 8--10 and rendered without visible truncation.

## Quartile boundary

`Q2 or above` is interpreted in the V47 ledger as publicly verifiable journal-level JCR/SJR Q1--Q2 status. This compile check does not convert that statement into a Chinese Academy of Sciences partition claim. The exact database edition and subject category required by the author's institution must still be confirmed before formal submission.
