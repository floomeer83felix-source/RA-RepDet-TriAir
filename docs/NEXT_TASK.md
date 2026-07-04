# Current Task

## Title
Phase 7B — Publication-State Reconciliation and Submission-Input Ledger

## Goal
Resolve the documentation inconsistency between the frozen blocked-split manuscript conclusion and legacy random-split summaries, then create one auditable ledger of author-provided and asset-provided requirements for strict SIVP preflight. This is a documentation and tooling task only; it must not retrain, re-evaluate, or change any scientific evidence.

## Read First
1. `AGENTS.md` if it exists.
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `runs/handoff_latest.md`
5. `runs/phase4b_report.md`
6. `runs/clean_block64g16_protocol.md`
7. `runs/phase7a_asset_readiness_report.md`
8. `docs/TASK_BLOCKER.md`
9. `AUTHOR_FINAL_INPUTS_REQUIRED_V18.md`
10. `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`
11. `submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md`
12. `scripts/preflight_submission.py`
13. `rarepdet/tools/generate_handoff.py`
14. `rarepdet/tools/update_project_status.py`

## Frozen Assets
- Remote branch: `research/ra-repdet-triair`.
- Manuscript protocol: `block64_guard16_seed0`.
- Frozen split cardinalities: train `7439`, validation `2213`, guard `837`.
- Official manuscript headline: **R4 Reliability p=0.20**, controlled seeds `0` and `2`, on the frozen blocked validation split.
- Phase 4B decision: `SELECT R4 AS CLEAN-SPLIT MAIN VARIANT`.
- Former E0–E6 random-split results are historical/exploratory diagnostics only and must never be labeled as the manuscript’s current best model.
- Strict V18 preflight remains blocked until authors supply factual metadata and final approved assets.

## Allowed Files To Modify
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7b_publication_state_reconciliation.md`
- `runs/phase7b_publication_state_reconciliation.json`
- `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
- `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Forbidden Files To Modify
- All training, model, dataset, loss, and primary AP-evaluation files.
- All split manifests, raw `.npy` data, weights, checkpoints, labels, images, rendered final figures, final PDFs, and prior experimental outputs.
- Do not modify reported numerical evidence or run any training, inference sweep, or metric-changing evaluation.

## Required Commands
Run only read-only inspection and documentation/tooling checks. Start with:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
```

If the fast-forward pull cannot run because of a genuine local/remote divergence, do not use `--allow-unrelated-histories`, force push, reset, or history rewriting. Record the blocker in `docs/TASK_BLOCKER.md`, commit only safe partial outputs, push only if it is fast-forward, and stop.

After reconciling the permitted tooling and documents, run:

```powershell
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

The strict preflight is expected to fail until real external inputs are supplied. Capture that failure accurately; do not weaken the strict validator merely to obtain a PASS.

## Required Outputs

### 1. Canonical publication-state wording
Make `docs/EXPERIMENT_STATUS.md` and `runs/handoff_latest.md` agree on all of the following:

- The official clean blocked-split manuscript headline is `R4 Reliability p=0.20`, with seeds `0, 2` and `block64_guard16_seed0`.
- The controlled-seed means are: F1@0.50 `0.920861`, AP50 `0.962495`, AP75 `0.891266`, w/o RGB AP50 `0.916051`, w/o Thermal AP50 `0.718277`, and w/o Event AP50 `0.961577`.
- Former E0–E6 results may be retained only in a clearly labeled **historical/exploratory random-split** section.
- Do not state or imply that legacy E2 is the current best model, headline model, or manuscript selection.
- If preserving legacy E2 rankings, label them explicitly as “legacy random-split historical” and never place them above the clean blocked-split publication snapshot.

Update `rarepdet/tools/generate_handoff.py` and/or `rarepdet/tools/update_project_status.py` only as needed to prevent this mismatch from reappearing after regeneration. Preserve all historical content that is factually valid and do not alter experiment numbers.

### 2. Final-submission input ledger
Create:

- `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
- `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`

Each row must contain these fields:

```text
item_id, category, exact_required_input, repository_destination, owner, source_or_evidence, current_state, strict_preflight_effect, action_to_close, notes
```

At minimum cover:

- author names, affiliations, ORCIDs, corresponding email;
- funding, acknowledgments, author contributions, competing interests;
- TriAir citation/data card, version/provider, licence, access terms, redistribution permission;
- public release URL, release tag, immutable commit, archive date, licence, Zenodo DOI if applicable;
- final Fig. 1–6 assets, explicitly distinguishing author/Visio-dependent Fig. 1–2 from data-derived Fig. 3–6;
- final publication tables;
- validation-only wording approval versus new independent held-out evidence;
- final hardware/software environment record;
- Springer `sn-jnl` local dependency and final compile readiness.

Use only verified facts from repository files. For any missing factual content, write `missing — author confirmation required`; do not invent names, citations, licence terms, DOIs, URLs, or approvals.

### 3. Reconciliation report
Create `runs/phase7b_publication_state_reconciliation.md` and matching JSON with:

- documents inspected and their commit/path provenance;
- every detected inconsistency and the corrective action;
- the canonical headline statement;
- strict and placeholder preflight outcomes;
- count of open ledger items by category;
- confirmation that no scientific metric, checkpoint, split, source data, or core model file changed;
- the exact next external inputs required from authors.

### 4. Blocker and handoff
Update `docs/TASK_BLOCKER.md` so it reflects the resolved documentation mismatch and preserves only genuine unresolved strict-preflight blockers. Do not remove the strict-preflight block unless every required field and final asset is actually present and verified.

Refresh `runs/handoff_latest.md` and `runs/handoff_latest.json`. Their top summary must show the clean blocked-split R4 headline first and must list Phase 7B completion plus the remaining author/asset blockers.

## Acceptance Criteria
- `docs/EXPERIMENT_STATUS.md`, `runs/handoff_latest.md`, and generated status output agree that R4 p=0.20 is the official clean blocked-split manuscript headline.
- No historical random-split row is called the current “best model” without a clear legacy label.
- The ledger covers every strict V18 blocker with owner, destination, status, and closure action.
- Placeholder-mode preflight is run and documented. Strict preflight remains FAIL unless all real inputs have been supplied; never fake a PASS.
- No training, GPU inference, experimental rerun, split mutation, source-data mutation, or core model/dataset/evaluation changes occur.
- All new/modified files are within the allowed list.
- `runs/handoff_latest.md` records the final commit SHA, changed files, command outcomes, and residual blockers.
- Commit all permitted outputs and push the branch.

## Commit Message
`docs: reconcile R4 publication status and submission ledger`

## Completion / Blocker Rule
Complete the documentation/tooling reconciliation, update the handoff, commit, and push. If author-provided facts or approved assets remain missing, keep strict preflight blocked, list them in the ledger and `docs/TASK_BLOCKER.md`, and stop. Do not create final submission PDFs or claim readiness for formal submission.