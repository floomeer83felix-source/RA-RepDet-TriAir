# Task Blocker

## Task

Execute `docs/NEXT_TASK.md` for Phase 7G: reconcile the completed table ledger state, create a fillable author-submission intake package, run static source audits, document figure/table and reproducibility closure state, update handoff/status, and preserve all final-submission blockers that still require external confirmation.

## Blocking Condition

Phase 7G completed documentation and static validation only. `TAB_001` is now resolved because Phase 7C inserted evidence-locked Tables 1-7, and the static audit confirms zero `TABLE PLACEHOLDER` strings in the SIVP body. No open table_asset blocker remains.

Strict V18 final-submission preflight still fails because non-table external inputs and final figure assets remain unresolved:

- author_metadata: final author names, affiliations, ORCID decisions, and corresponding email.
- declarations: funding, acknowledgments, contributions, competing interests, and AI-use disclosure.
- data_governance: TriAir citation, version/provider, licence/access terms, and redistribution restrictions.
- release_archive: public URL or no-release policy, release tag, immutable source identifier, archive date, release licence, and DOI state.
- figure_asset: approved final Fig. 1-6 PDF assets are absent; Fig. 1-2 still require author-designed schematics; Fig. 3-5 candidates are non-final review inputs only; Fig. 6 still requires author panel selection, crop/redaction decisions, and final composition approval.
- claim_scope: authors must approve validation-only wording or provide new approved held-out evidence before any stronger claim.
- environment: final hardware/software record still needs author or research-owner confirmation.
- compile_readiness: final Springer `sn-jnl` compile must wait until strict preflight passes and final assets exist.

No author fact, approver identity, approval date, public release value, dataset licence/access statement, DOI, final figure asset, Fig. 6 panel selection, final figure insertion, manuscript claim change, or final PDF compile was produced in Phase 7G.

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

- Ran the required branch switch and fast-forward pull before Phase 7G edits.
- Ran `git status --short`; unrelated pre-existing untracked files were present before task edits and are not part of Phase 7G.
- Ran `python scripts/preflight_submission.py --root . --allow-placeholders`; result: `PASS` with expected warnings.
- Reconciled `TAB_001` in both canonical ledger formats to the completed Phase 7C table state.
- Created `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_PACKET.md`.
- Created `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv` with 29 unresolved rows, excluding resolved `TAB_001`, and leaving all response/confirmation fields blank.
- Created `submission/sivp/metadata/ENVIRONMENT_RECORD_TEMPLATE.md` with only repository-documented experimental settings prefilled.
- Created and ran `submission/sivp/review/static_submission_audit.py`; result: `PASS`.
- Created `submission/sivp/review/STATIC_SUBMISSION_SOURCE_AUDIT.md` and `.csv`.
- Created `submission/sivp/review/FIGURE_TABLE_CROSSWALK.md` and `.csv` with 13 assets.
- Created `submission/sivp/review/REPRODUCIBILITY_CLOSURE_AUDIT.md` and `.csv`.
- Created `submission/sivp/metadata/SUBMISSION_CLOSURE_ROADMAP.md`.
- Created `submission/sivp/review/SUBMISSION_INPUT_COMPLETENESS_CHECK.md` and `.csv`.
- Created `runs/phase7g_submission_intake_report.md` and `.json`.
- Updated handoff/status generators to report Phase 7G outputs and to avoid counting complete ledger rows as open blockers.
- No GPU training, GPU inference sweep, metric-changing evaluation, split mutation, source-data mutation, source CSV change, core model/dataset/evaluation change, final figure generation, candidate PDF generation, LaTeX figure insertion, strict-rule weakening, or final PDF compile was executed.

## Related Files

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7g_submission_intake_report.md`
- `runs/phase7g_submission_intake_report.json`
- `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
- `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`
- `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_PACKET.md`
- `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv`
- `submission/sivp/metadata/ENVIRONMENT_RECORD_TEMPLATE.md`
- `submission/sivp/metadata/SUBMISSION_CLOSURE_ROADMAP.md`
- `submission/sivp/review/STATIC_SUBMISSION_SOURCE_AUDIT.md`
- `submission/sivp/review/STATIC_SUBMISSION_SOURCE_AUDIT.csv`
- `submission/sivp/review/FIGURE_TABLE_CROSSWALK.md`
- `submission/sivp/review/FIGURE_TABLE_CROSSWALK.csv`
- `submission/sivp/review/REPRODUCIBILITY_CLOSURE_AUDIT.md`
- `submission/sivp/review/REPRODUCIBILITY_CLOSURE_AUDIT.csv`
- `submission/sivp/review/SUBMISSION_INPUT_COMPLETENESS_CHECK.md`
- `submission/sivp/review/SUBMISSION_INPUT_COMPLETENESS_CHECK.csv`
- `submission/sivp/review/static_submission_audit.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`
- `scripts/preflight_submission.py`

## Repair Option 1

Authors complete `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv`, the existing figure decision files, and the Fig. 6 review template. Then add only confirmed metadata, approved final Fig. 1-6 PDFs, approved data-governance/release/environment facts, rerun strict preflight, and compile the final Springer `sn-jnl` package.

## Repair Option 2

Keep the repository as a pre-submission readiness package with completed evidence-locked tables, source-locked figures, blank author intake fields, and static audit evidence. Continue using placeholder-mode preflight only as a structural check until every remaining author, asset, data-governance, release, claim-scope, environment, and compile-readiness item is closed.
