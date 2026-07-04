# Task Blocker

## Task

Execute `docs/NEXT_TASK.md` for Phase 7E: generate local-only, non-final candidate renders for Fig. 3, Fig. 4, and Fig. 5 from frozen validated CSV sources, keep the outputs ignored and untracked, refresh handoff/status, and push the documentation/code update.

## Blocking Condition

Phase 7E creates local author-review candidates only. It does not resolve final submission readiness.

Figure readiness detail:

- Fig. 1 `Fig1_overall_architecture.pdf`: current state remains `author-design required`; no Phase 7E render was created.
- Fig. 2 `Fig2_leakage_aware_protocol.pdf`: current state remains `author-design required`; no Phase 7E render was created.
- Fig. 3 `Fig3_controlled_ablation.pdf`: local non-final candidate exists at `runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf` for author review only; final artwork remains missing.
- Fig. 4 `Fig4_missing_modality_robustness.pdf`: local non-final candidate exists at `runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf` for author review only; final artwork remains missing.
- Fig. 5 `Fig5_reliability_weight_audit.pdf`: local non-final candidate exists at `runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf` for author review only; final artwork remains missing.
- Fig. 6 `Fig6_qualitative_results.pdf`: current state remains `local-panel inventory required`; no Phase 7E render was created.

The local candidates are ignored by Git and intentionally untracked. They are not publication assets, not author-approved, and are not inserted into `submission/sivp/tex/ra_repdet_sivp.tex`.

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

- Ran the required branch switch and fast-forward pull before Phase 7E edits.
- Ran `git status --short`; unrelated pre-existing untracked files were present before task edits and are not part of Phase 7E.
- Ran `python scripts/preflight_submission.py --root . --allow-placeholders`; result before Phase 7E edits: `PASS` with expected warnings.
- Ran `python submission/sivp/figures/figure_candidate_build.py --dry-run --root .`; result before rendering: `PASS`.
- Read the required Phase 7E context, SIVP source files, Phase 4B/7B/7C/7D reports, source CSVs, build specification, candidate check, preflight script, and handoff/status generators.
- Added an exact `.gitignore` rule for `runs/local_candidate_figures/`.
- Extended `submission/sivp/figures/figure_candidate_build.py` with mutually exclusive `--dry-run` and `--render-candidates --output-dir` modes.
- Validated the Fig. 3-5 source CSV headers, row counts, numerical-token counts, and Phase 7D SHA256 values before and after rendering.
- Rendered exactly three local non-final candidate PDFs plus `candidate_render_manifest.json` under `runs/local_candidate_figures/phase7e/`.
- Verified candidate PDF sizes: Fig. 3 = 27440 bytes, Fig. 4 = 26852 bytes, Fig. 5 = 25510 bytes.
- Verified `candidate_render_manifest.json` records top-level `final_asset_status: not_final` and every generated asset as `not_final`.
- Verified `git check-ignore -v` matches `.gitignore` for all three candidate PDFs.
- Verified `git status --short` does not list the local candidate directory.
- Verified no final `Fig1`-`Fig6` PDF exists under `figures/` or `submission/sivp/figures/`.
- Verified `submission/sivp/tex/ra_repdet_sivp.tex` still contains the six expected figure placeholders.
- Verified `pdftotext` finds candidate watermark text, source path, and SHA256 text in all three candidate PDFs.
- Created `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.md` and `.csv`.
- Created `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.md` and `.csv`.
- Created `runs/phase7e_candidate_render_report.md` and `.json`.
- No GPU training, GPU inference sweep, metric-changing evaluation, split mutation, source-data mutation, source CSV change, core model/dataset/evaluation change, final figure generation, LaTeX figure insertion, or final PDF compile was executed.

## Related Files

- `.gitignore`
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7e_candidate_render_report.md`
- `runs/phase7e_candidate_render_report.json`
- `submission/sivp/figures/figure_candidate_build.py`
- `submission/sivp/figures/FIGURE_BUILD_SPEC.md`
- `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.md`
- `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.csv`
- `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.md`
- `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.csv`
- `scripts/preflight_submission.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

Local-only untracked outputs:

- `runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf`
- `runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf`
- `runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf`
- `runs/local_candidate_figures/phase7e/candidate_render_manifest.json`

## Repair Option 1

Authors review the local Fig. 3-5 candidates, request any changes needed, then approve final figure assets only after Fig. 1-2 schematic assets and Fig. 6 qualitative panel assets are also ready. Then replace placeholders, rerun strict preflight, and compile the final Springer `sn-jnl` package.

## Repair Option 2

Keep the repository as a pre-submission readiness package with completed evidence-locked tables, locked figure sources, and local non-final Fig. 3-5 candidates. Use the placeholder-mode preflight PASS as a structural check, keep strict mode blocked, and do not label the package as formally submission-ready until every remaining blocker is closed.
