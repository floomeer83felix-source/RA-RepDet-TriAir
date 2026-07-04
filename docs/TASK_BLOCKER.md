# Task Blocker

## Task

Execute `docs/NEXT_TASK.md` for Phase 7D: lock the six SIVP figure sources, create a reproducible dry-run candidate-build specification for Fig. 3-5, record Fig. 1-2 and Fig. 6 author/input dependencies, refresh handoff/status, and push the documentation update.

## Blocking Condition

Phase 7D resolves figure source traceability and candidate-build specification only. It does not resolve final submission readiness.

Figure readiness detail:

- Fig. 1 `Fig1_overall_architecture.pdf`: source traceability documented from actual reliability builder/backbone code and manuscript method text; current state remains `author-design required`.
- Fig. 2 `Fig2_leakage_aware_protocol.pdf`: source traceability documented from Phase 3C duplicate-audit evidence and the clean block64/guard16 protocol; current state remains `author-design required`.
- Fig. 3 `Fig3_controlled_ablation.pdf`: frozen CSV source validated; current state is `candidate build spec ready`; final artwork is still pending author approval.
- Fig. 4 `Fig4_missing_modality_robustness.pdf`: frozen CSV source validated; current state is `candidate build spec ready`; final artwork is still pending author approval.
- Fig. 5 `Fig5_reliability_weight_audit.pdf`: frozen CSV source validated; current state is `candidate build spec ready`; final artwork is still pending author approval.
- Fig. 6 `Fig6_qualitative_results.pdf`: qualitative manifest identified with 20 local real validation panel rows; current state remains `local-panel inventory required`.

The table-placeholder blocker remains resolved from Phase 7C. The remaining blocker is strict V18 final-submission preflight. The repository still lacks author-confirmed metadata, TriAir citation/licence/access facts, release/archive metadata, final approved Fig. 1-6 assets, claim-scope approval, final environment details, and final compile readiness.

## Failed Command

```powershell
python scripts/preflight_submission.py --root .
```

## Last Error Lines

```text
RA-RepDet SIVP preflight
root: E:\RepViT-main
allow_placeholders: False
FAIL: Placeholder or unverified field remains in main.tex: /\[[A-Z0-9 _/-]*(AUTHOR|AFFILIATION|EMAIL|FUNDING|ACKNOWLEDG|COMPETING|CONTRIBUTION|DATA AVAILABILITY)[A-Z0-9 _/-]*\]/
FAIL: Placeholder or unverified field remains in archive_manifest.txt: /AUTHOR_(REQUIRED|CONFIRMATION_REQUIRED|CONFIRMATION REQUIRED)/
FAIL: Placeholder or unverified field remains in main.tex: /AUTHOR CONFIRMATION REQUIRED/
FAIL: Placeholder or unverified field remains in SUBMISSION_PRECHECK_V18.md: /NOT PROVIDED/
FAIL: Placeholder or unverified field remains in submission\sivp\tex\ra_repdet_sivp.tex: /Final artwork pending/
FAIL: Placeholder or unverified field remains in main.tex: /PLACEHOLDER/
FAIL: Missing final figure assets: figures/Fig1_overall_architecture.pdf, figures/Fig2_leakage_aware_protocol.pdf, figures/Fig3_controlled_ablation.pdf, figures/Fig4_missing_modality_robustness.pdf, figures/Fig5_reliability_weight_audit.pdf, figures/Fig6_qualitative_results.pdf
RESULT: FAIL
```

## Attempted Fixes

- Ran the required branch switch and fast-forward pull before Phase 7D edits.
- Ran `git status --short`; unrelated pre-existing untracked files were present before task edits and are not part of Phase 7D.
- Ran `python scripts/preflight_submission.py --root . --allow-placeholders`; result before Phase 7D edits: `PASS` with expected warnings.
- Read the required Phase 7D context, SIVP source files, Phase 4B/7B/7C reports, source CSVs, qualitative manifest, split/protocol evidence, preflight script, and handoff/status generators.
- Confirmed `rarepdet/models/reliability_fusion_fcos.py` is absent in this tree; traced Fig. 1 to the actual present files `rarepdet/models/early_fusion_fcos.py` and `rarepdet/models/repvit_fpn_backbone.py`.
- Created `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md` and `.csv` with six figure rows.
- Created `submission/sivp/figures/FIGURE_BUILD_SPEC.md`.
- Created `submission/sivp/figures/figure_candidate_build.py` with mandatory `--dry-run` and `--root` options.
- Created `submission/sivp/review/FIGURE_CANDIDATE_CHECK.md` and `.csv`.
- Created `runs/phase7d_figure_source_lock_report.md` and `.json`.
- Updated `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md` only with factual readiness states while retaining `final artwork pending` for every figure.
- Validated Fig. 3-5 source CSV headers, row counts, numerical-token counts, hashes, and future candidate target filenames.
- Confirmed no final `Fig1`-`Fig6` PDF assets exist or were added.
- Confirmed no image/PDF/SVG/JPG/PNG/EPS artifact was written by the dry-run workflow.
- Confirmed `submission/sivp/tex/ra_repdet_sivp.tex` still contains the expected figure placeholders.
- No GPU training, GPU inference sweep, metric-changing evaluation, split mutation, source-data mutation, core model/dataset/evaluation change, source CSV change, final figure generation, candidate artwork generation, LaTeX figure insertion, or final PDF compile was executed.

## Related Files

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7d_figure_source_lock_report.md`
- `runs/phase7d_figure_source_lock_report.json`
- `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`
- `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md`
- `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.csv`
- `submission/sivp/figures/FIGURE_BUILD_SPEC.md`
- `submission/sivp/figures/figure_candidate_build.py`
- `submission/sivp/review/FIGURE_CANDIDATE_CHECK.md`
- `submission/sivp/review/FIGURE_CANDIDATE_CHECK.csv`
- `scripts/preflight_submission.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Repair Option 1

Authors provide all remaining factual inputs and approved final Fig. 1-6 assets. Then replace placeholders, rerun strict preflight, and compile the final Springer `sn-jnl` package.

## Repair Option 2

Keep the repository as a pre-submission readiness package with completed evidence-locked tables and figure source locks. Use the placeholder-mode preflight PASS as a structural check, keep strict mode blocked, and do not label the package as formally submission-ready until every remaining blocker is closed.
