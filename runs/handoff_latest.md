# RA-RepDet-TriAir Handoff

Generated: 2026-07-09

## Current Task State

- Task file: `docs/NEXT_TASK.md`
- Current task: V41 SIVP manuscript polish and PDF preview
- Status: `POLISHED_PREVIEW_READY`
- Active blocker: `NO_ACTIVE_BLOCKER`

## What Assistant/Codex Completed

Completed the SIVP manuscript alignment and polishing from existing V41 evidence only. No training, evaluation, guard/test access, checkpoint loading, raw data access, or prediction-cache access was performed.

Files updated or recorded:

- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/tex/main.tex`
- `main.tex`
- `main_sivp_snjnl.tex`
- `submission/sivp/tables/Table_1_dataset_and_clean_split.tex`
- `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex`
- `submission/sivp/tables/Table_8_three_seed_interim_devval.tex`
- `submission/sivp/tex/related_work_literature_expansion.tex`
- `submission/sivp/review/V41_SIVP_CLAIM_LEDGER.md`
- `submission/sivp/review/V41_SIVP_REPLACEMENT_TEXT.md`
- `submission/sivp/review/V41_SIVP_MANUSCRIPT_ALIGNMENT_PLAN.md`
- `runs/v41_q1_upgrade/sivp_alignment/pre_edit_claim_scan.txt`
- `runs/v41_q1_upgrade/sivp_alignment/post_edit_claim_scan.txt`
- `runs/v41_q1_upgrade/sivp_alignment/post_edit_claim_scan_review.md`
- `runs/v41_q1_upgrade/sivp_alignment/preflight_allow_placeholders.txt`
- `runs/v41_q1_upgrade/sivp_alignment/compile_summary.md`
- `runs/v41_q1_upgrade/sivp_alignment/pdflatex_compile.txt`
- `runs/v41_q1_upgrade/sivp_alignment/polished_preview_compile.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md/json`

## Author Metadata and Declarations

- Authors: Nan Xin and Xueting Jin.
- Corresponding author: Nan Xin.
- Affiliation: Anhui Police College, Hefei, Anhui, China.
- Corresponding email: `floomeer83felix@gmail.com`.
- Funding: no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.
- Competing interests: the authors declare no competing interests.
- Author contributions: Nan Xin conceived/designed/implemented/evaluated/analyzed/drafted; Xueting Jin supervised, contributed to design/interpretation, and reviewed/revised; both authors read and approved the final manuscript.
- Acknowledgments: not applicable.
- Data availability: the experimental dataset is the publicly available TriAir dataset; original files are not redistributed.
- Code availability: source code, split manifests, source-lock records, evaluation summaries, and manuscript evidence tables are available in the current project repository.

## Manuscript Polish Notes

- Active result remains reliability-aware `p=0.15` versus matched early fusion on seed0/seed1/seed2.
- Main evidence is explicitly three-seed interim development-validation descriptive evidence on the frozen V40 component-disjoint development-validation split.
- `Table_1_dataset_and_clean_split.tex` now uses V40 component-disjoint split wording and development-validation box count 5867.
- `Table_2_implementation_and_reproducibility.tex` now uses seed0/seed1/seed2 and p=0.15 active setting.
- `Table_8_three_seed_interim_devval.tex` remains the active main result table.
- R4 `p=0.20` and block64/guard16 are not active manuscript claims.
- The related-work appendix now avoids draft-screening, quartile, and internal-review language.

## PDF Preview

A compiled reading/layout preview was generated in the assistant sandbox as `RA_RepDet_SIVP_V41_polished_compiled_preview.pdf`.

Because the assistant sandbox does not contain the Springer `sn-jnl` class or full repository clone, the preview was compiled with a temporary article-style wrapper and a simplified references note. It is suitable for reading/layout review, not final Springer/SIVP submission.

## Residual Submission Blockers

- Final Fig. 1--6 assets are missing.
- Public release/archive DOI and release metadata remain unresolved.
- TriAir provider, version, license, redistribution, and synchronization facts remain author-confirmation items beyond naming the public dataset.
- Label-quality review remains incomplete.
- Full Springer `sn-jnl` class build and BibTeX/cross-reference closure require local toolchain repair.

## Three-Seed Interim Development-Validation Summary

Reliability p=0.15 minus matched early, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.011629 | 0.016501 | 3 |
| Recall | +0.024487 | 0.026581 | 3 |
| F1 | +0.018524 | 0.006208 | 3 |
| AP50 | +0.016064 | 0.005699 | 3 |
| AP75 | +0.064657 | 0.016415 | 3 |

## Claim Boundary

Allowed wording: three-seed interim development-validation descriptive evidence on the frozen V40 component-disjoint development-validation split.

Disallowed wording: independent test, external generalization, statistical significance, manuscript-final aggregate, optimal dropout, calibrated sensor reliability, or physical sensor-failure robustness.

## What Remains Out Of Scope

- Final figure/artwork verification.
- TriAir provider URL, version, license, redistribution rights, synchronization details, or official event representation verification.
- New experiments, independent test creation, COCO AP50:95, causal ablations, or label-quality review.
