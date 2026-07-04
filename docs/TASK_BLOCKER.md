# Task Blocker

## Task

Execute `docs/NEXT_TASK.md` for Phase 7F: create an author figure review packet, decision templates, a safe Fig. 6 review template, and a local-only Fig. 6 panel inventory while preserving all figure placeholders and final-asset blockers.

## Blocking Condition

Phase 7F completes review intake, not final submission readiness. The review packet exists, the Fig. 6 local inventory found 20 locally existing panel files from 20 manifest rows, and the path-level JSON remains ignored and untracked at `runs/local_candidate_figures/phase7f/fig6_panel_inventory.json`.

Figure readiness detail:

- Fig. 1 `Fig1_overall_architecture.pdf`: author-design schematic decision still required.
- Fig. 2 `Fig2_leakage_aware_protocol.pdf`: author-design schematic decision still required.
- Fig. 3 `Fig3_controlled_ablation.pdf`: local non-final candidate remains available for author review only; final artwork is still missing.
- Fig. 4 `Fig4_missing_modality_robustness.pdf`: local non-final candidate remains available for author review only; final artwork is still missing.
- Fig. 5 `Fig5_reliability_weight_audit.pdf`: local non-final candidate remains available for author review only; final artwork is still missing.
- Fig. 6 `Fig6_qualitative_results.pdf`: local panel inventory is complete, but author panel selection, crop/redaction decisions, and final composition approval are still required.

No author approval, approver identity, approval date, final asset authorization, local panel selection, figure placeholder replacement, or final asset generation was performed. The remaining blocker is strict V18 final-submission preflight. The repository still lacks author-confirmed metadata, TriAir citation/licence/access facts, release/archive metadata, final approved Fig. 1-6 assets, claim-scope approval, final environment details, and final compile readiness.

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

- Ran the required branch switch and fast-forward pull before Phase 7F edits.
- Ran `git status --short`; unrelated pre-existing untracked files were present before task edits and are not part of Phase 7F.
- Ran `python scripts/preflight_submission.py --root . --allow-placeholders`; result before Phase 7F edits: `PASS` with expected warnings.
- Ran `python submission/sivp/figures/figure_candidate_build.py --dry-run --root .`; result: `PASS`.
- Read the required Phase 7F context files, SIVP source files, figure build specifications, review checks, manifest, preflight script, and handoff/status generators.
- Added `submission/sivp/figures/qualitative_panel_inventory.py` with local-only dry-run inventory behavior.
- Ran the Fig. 6 inventory command and wrote exactly one ignored local JSON file under `runs/local_candidate_figures/phase7f/`.
- Verified the local inventory JSON is ignored by Git with `git check-ignore -v`.
- Created `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`.
- Created `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv` with all approvals pending.
- Created `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md` and `.csv` using only safe manifest metadata.
- Created `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md` and `.csv` using aggregate non-sensitive results only.
- Created `runs/phase7f_author_review_intake_report.md` and `.json`.
- No GPU training, GPU inference sweep, metric-changing evaluation, split mutation, source-data mutation, source CSV change, core model/dataset/evaluation change, final figure generation, candidate PDF generation, LaTeX figure insertion, or final PDF compile was executed.

## Related Files

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7f_author_review_intake_report.md`
- `runs/phase7f_author_review_intake_report.json`
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`
- `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md`
- `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv`
- `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md`
- `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.csv`
- `submission/sivp/figures/qualitative_panel_inventory.py`
- `scripts/preflight_submission.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

Local-only untracked output:

- `runs/local_candidate_figures/phase7f/fig6_panel_inventory.json`

## Repair Option 1

Authors complete the Phase 7F decision templates: provide or approve Fig. 1-2 schematic sources, approve or request revisions to Fig. 3-5 candidates, select Fig. 6 panels, and approve any crop/redaction and final composition. Then generate only approved final assets, rerun strict preflight, and compile the final Springer `sn-jnl` package.

## Repair Option 2

Keep the repository as a pre-submission readiness package with completed evidence-locked tables, locked figure sources, local non-final Fig. 3-5 candidates, and a safe Fig. 6 panel inventory. Continue using placeholder-mode preflight as a structural check and keep strict mode blocked until every remaining author, asset, data-governance, release, environment, and compile-readiness item is closed.
