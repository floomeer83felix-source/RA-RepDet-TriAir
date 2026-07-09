# Experiment Status

Generated: 2026-07-09

## Current Status

`V41_SIVP_POLISHED_PREVIEW_READY`

The V41 three-seed interim development-validation evidence is consolidated, and the active SIVP LaTeX narrative has been aligned to the validation-only evidence state. The manuscript text has now been polished, declaration statements have been inserted, key tables have been aligned to the V40/V41 evidence state, and an assistant-side PDF preview has been compiled for reading/layout review.

No new training, evaluation, guard/test access, checkpoint loading, raw data access, or prediction-cache access was performed. Manuscript edits were limited to SIVP LaTeX metadata/declaration/narrative/table alignment and local PDF preview compilation.

## Evidence Inputs

- V40 seed0/seed2 source: `runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json`.
- V41 fresh seed1 source: `runs/v41_q1_upgrade/seed1/seed1_per_run_summary.csv`.
- V41 seed1 source lock: `runs/v41_q1_upgrade/seed1/source_lock_seed1.md/json`.
- V41 seed1 completion commit: `5d839ae900849919189edff4bdd364f42c043b86`.
- Three-seed package: `runs/v41_q1_upgrade/interim_devval/`.

## Author metadata inserted

- Authors: Nan Xin and Xueting Jin.
- Corresponding author: Nan Xin.
- Affiliation: Anhui Police College, Hefei, Anhui, China.
- Corresponding email: `floomeer83felix@gmail.com`.
- Updated entry files:
  - `submission/sivp/tex/main.tex`
  - root `main.tex`
  - root `main_sivp_snjnl.tex`

## Declarations inserted

- Funding: no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.
- Competing interests: the authors declare no competing interests.
- Author contributions: Nan Xin conceived/designed/implemented/evaluated/analyzed/drafted; Xueting Jin supervised, contributed to design/interpretation, and reviewed/revised; both authors read and approved the final manuscript.
- Acknowledgments: not applicable.
- Data availability: TriAir is named as the publicly available dataset; original files are not redistributed.
- Code availability: source code, split manifests, source-lock records, evaluation summaries, and manuscript evidence tables are available in the current project repository.

## Polished SIVP manuscript updates

- Polished `submission/sivp/tex/ra_repdet_sivp.tex` for journal-style wording, clearer claim boundaries, and updated limitations.
- Updated the title/abstract/keywords in `submission/sivp/tex/main.tex`, root `main.tex`, and root `main_sivp_snjnl.tex` to use component-disjoint validation wording.
- Updated `submission/sivp/tables/Table_1_dataset_and_clean_split.tex` to remove old block64/guard16 wording and align with V40 component-disjoint evidence.
- Updated `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex` to report seed0/seed1/seed2 and reliability-aware p=0.15 as the active setting.
- Polished `submission/sivp/tex/related_work_literature_expansion.tex` to remove draft-screening/quartile language and keep the appendix as technical context only.
- Recorded the assistant-side PDF preview compile in `runs/v41_q1_upgrade/sivp_alignment/polished_preview_compile.md`.

## Three-seed interim development-validation descriptive summary

Reliability p=0.15 minus matched early, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.011629 | 0.016501 | 3 |
| Recall | +0.024487 | 0.026581 | 3 |
| F1 | +0.018524 | 0.006208 | 3 |
| AP50 | +0.016064 | 0.005699 | 3 |
| AP75 | +0.064657 | 0.016415 | 3 |

Per-seed paired deltas:

| Seed | Precision | Recall | F1 | AP50 | AP75 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | +0.024180 | +0.001704 | +0.012637 | +0.012812 | +0.054121 |
| 1 | +0.017770 | +0.018067 | +0.017925 | +0.012734 | +0.083570 |
| 2 | -0.007062 | +0.053690 | +0.025010 | +0.022645 | +0.056280 |

## Claim boundary

Allowed wording: three-seed interim development-validation descriptive evidence on the frozen V40 component-disjoint development-validation split.

Disallowed wording: independent test, external generalization, statistical significance, manuscript-final aggregate, optimal dropout, calibrated sensor reliability, or physical sensor-fault robustness.

## PDF preview note

A compiled preview PDF was generated in the assistant sandbox using a temporary article-style wrapper because the hosted environment does not include the Springer `sn-jnl` class or a full repository clone. The preview is suitable for reading/layout review but is not a final Springer/SIVP submission build.

## Work intentionally left for final submission

- Final artwork for Fig. 1--6.
- Public release/archive DOI and release metadata.
- TriAir provider/license/version/redistribution/synchronization details beyond naming the public dataset.
- Full Springer `sn-jnl` class build and BibTeX/cross-reference closure after local toolchain repair.

## Remaining scientific limitations

- Validation-only evidence.
- Three seed pairs only; seed3/seed4 are not planned in the current line.
- No independent test.
- No causal ablations separating stems, dynamic gate, and dropout.
- No COCO mAP@[0.50:0.95] package.
- Dataset provider provenance remains only partially resolved by naming TriAir as public.
- Label-quality review remains incomplete.
