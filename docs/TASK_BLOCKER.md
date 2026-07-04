# Task Blocker

## Task

Execute `docs/NEXT_TASK.md` for Phase 7B: reconcile the official R4 clean blocked-split publication state, create the final-submission input ledger, refresh handoff/status, and push the documentation/tooling update.

## Blocking Condition

The publication-state documentation mismatch has been resolved: `R4 Reliability p=0.20` on `block64_guard16_seed0`, controlled seeds `0` and `2`, is now the official manuscript headline in the generated status and handoff. Legacy E0-E6 random-split results are retained only as historical/exploratory diagnostics.

The remaining blocker is strict V18 final-submission preflight. The repository still lacks author-confirmed metadata, TriAir citation/licence/access facts, release/archive metadata, final approved Fig. 1-6 assets, final publication tables, claim-scope approval, final environment details, and final compile readiness. The new ledger at `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md` and `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv` is the closure checklist.

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
FAIL: Placeholder or unverified field remains in submission\sivp\tex\ra_repdet_sivp.tex: /TABLE PLACEHOLDER/
FAIL: Placeholder or unverified field remains in main.tex: /PLACEHOLDER/
FAIL: Missing final figure assets: figures/Fig1_overall_architecture.pdf, figures/Fig2_leakage_aware_protocol.pdf, figures/Fig3_controlled_ablation.pdf, figures/Fig4_missing_modality_robustness.pdf, figures/Fig5_reliability_weight_audit.pdf, figures/Fig6_qualitative_results.pdf
RESULT: FAIL
```

## Attempted Fixes

- Ran the required branch switch and fast-forward pull before Phase 7B edits.
- Read the required context, Phase 4B decision, clean-split protocol, Phase 7A readiness report, preflight script, figure/table insertion maps, and handoff/status generators.
- Updated `rarepdet/tools/generate_handoff.py` so regenerated handoff puts the clean blocked-split R4 publication headline first and labels E0-E6 as legacy random-split historical diagnostics.
- Updated `rarepdet/tools/update_project_status.py` so regenerated experiment status puts the clean blocked-split R4 publication headline first and labels E0-E6 as historical/exploratory random-split results.
- Created the final-submission input ledger in Markdown and CSV with 30 open items across author metadata, declarations, data governance, release/archive, figures, tables, claim scope, environment, and compile readiness.
- Created `runs/phase7b_publication_state_reconciliation.md` and `.json`.
- Ran `python rarepdet/tools/generate_handoff.py`; result: `PASS`.
- Ran `python rarepdet/tools/update_project_status.py`; result: `PASS`.
- Ran `python scripts/preflight_submission.py --root . --allow-placeholders`; result: `PASS` with expected warnings.
- Ran strict `python scripts/preflight_submission.py --root .`; result: `FAIL` as expected on unresolved external inputs.
- No GPU training, GPU inference sweep, metric-changing evaluation, split mutation, source-data mutation, or core model/dataset/evaluation change was executed.

## Related Files

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7b_publication_state_reconciliation.md`
- `runs/phase7b_publication_state_reconciliation.json`
- `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
- `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`
- `AUTHOR_FINAL_INPUTS_REQUIRED_V18.md`
- `scripts/preflight_submission.py`
- `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`
- `submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md`
- `submission/sivp/tex/ra_repdet_sivp.tex`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Repair Option 1

Authors provide all missing factual inputs and approved assets listed in the Phase 7B ledger. Then replace placeholders, insert final figures/tables, rerun strict preflight, and compile the final Springer `sn-jnl` package.

## Repair Option 2

Keep the repository as a pre-submission readiness package. Use the placeholder-mode preflight PASS as a structural check, keep strict mode blocked, and do not label the package as formally submission-ready until every ledger item is closed.
