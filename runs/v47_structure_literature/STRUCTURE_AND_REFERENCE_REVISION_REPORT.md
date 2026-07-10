# V47 Structure and Literature Revision Report

Generated: 2026-07-10

## Scope

Reorganized the SIVP manuscript and expanded the active cited literature to approximately 40 references. No training, evaluation, checkpoint selection, metric recomputation, split modification, or holdout access was performed.

## Structural changes

The active manuscript body is now organized as:

1. Introduction
2. Related Work
   - Lightweight UAV and small-object detection
   - Infrared--visible fusion and multispectral perception
   - Cross-modal registration, semantic perception, and reliability
   - Missing modalities and leakage-aware evaluation
3. Method
   - Problem setup and shared detector
   - Matched early fusion
   - Modality-specific softmax fusion
   - Modality dropout and mechanism scope
4. Dataset and Evaluation Protocol
   - TriAir representation and label handling
   - Leakage audit and component-disjoint partitioning
   - Development-validation and locked holdout
   - Training and evaluation conventions
5. Results
   - Three-seed development-validation results
   - Locked within-dataset holdout results
   - Interpretation and evidence boundary
6. Discussion
7. Limitations
8. Conclusion

The weak standalone literature appendix is no longer included by the active manuscript entry files. Its useful scope material was incorporated into the main Related Work, Discussion, and Limitations sections.

## Narrative corrections

- Replaced most manuscript-facing uses of `guard` with `locked within-dataset holdout`; repository artifact names remain unchanged.
- Shortened the title to focus on the method rather than embedding the complete evaluation protocol in the title.
- Reduced the contribution list from five mixed scientific/reporting items to three substantive contributions.
- Clarified that a locked holdout is methodologically more conservative but is not necessarily intrinsically more difficult than development-validation.
- Reframed the strongest held-out result around AP50; the manuscript now explicitly states that held-out F1/AP75 deltas are mixed and that high-IoU localization evidence is not consistent.
- Added explicit limitations concerning causal ablation, efficiency measurement, event-channel provenance, component-graph completeness, external evaluation, and standard COCO metrics.

## Reference expansion

Created:

- `submission/sivp/tex/references_recent_q12_2023_2025.bib`
- `submission/sivp/review/V47_RECENT_Q12_REFERENCE_LEDGER.md`

The revised body cites exactly 40 unique BibTeX keys:

- 28 newly added formal 2023--2024 journal articles selected from publicly verifiable Q1/Q2 journals;
- 3 recent formal journal references already present in the repository;
- 9 foundational original method/dataset references retained as explicitly documented provenance exceptions.

No `\nocite{*}` is used; only references cited in the manuscript are printed by BibTeX.

## Recent-journal selection boundary

`Q2 or above` is interpreted as public JCR/SJR Q1--Q2 journal status. The revision does not claim Chinese Academy of Sciences partitions. Journal quartiles can change by year and subject category, so final submission should use the institutionally accepted database edition.

## Files changed

- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/tex/main.tex`
- root `main.tex`
- root `main_sivp_snjnl.tex`
- `submission/sivp/tex/references_recent_q12_2023_2025.bib`
- `submission/sivp/review/V47_RECENT_Q12_REFERENCE_LEDGER.md`
- `runs/v47_structure_literature/STRUCTURE_AND_REFERENCE_REVISION_REPORT.md`
- `runs/v47_structure_literature/V47_COMPILE_AND_CITATION_CLOSURE.md`

## Evidence boundary preserved

The V41/V42 numerical evidence is unchanged. The manuscript continues to report:

- three-seed component-disjoint development-validation evidence;
- locked same-dataset holdout evaluation of six fixed checkpoints;
- project-local AP50/AP75 rather than COCO AP@[0.50:0.95];
- no external-generalization, statistical-significance, optimal-dropout, calibrated-sensor-reliability, or physical sensor-fault claim.

## Compile and citation closure

A fresh Springer-style V47 preflight build was completed using the `sn-jnl` class files from the previously supplied source package.

- cited keys found by static scan: 40;
- matching BibTeX entries: 40;
- missing citations: 0;
- undefined references after final pass: 0;
- PDF pages: 10;
- rendered pages inspected: 10;
- obvious page clipping or broken pages: none observed.

Output artifact: `RA_RepDet_SIVP_V47_structure_recent_literature_snjnl.pdf`.

The sandbox `bibtex` symlink was unavailable, so `/usr/bin/bibtex.original` was used. Full details are recorded in `runs/v47_structure_literature/V47_COMPILE_AND_CITATION_CLOSURE.md`.
