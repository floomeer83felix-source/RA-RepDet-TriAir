# Phase 7B Publication-State Reconciliation

Generated: 2026-07-04
Workspace: `E:\RepViT-main`
Remote branch: `research/ra-repdet-triair`
Provenance baseline commit inspected before Phase 7B edits: `d6b42ac8334cd86ad7d0bc072dcb1fa95ab866db`

## Documents Inspected

| Path | Provenance |
| --- | --- |
| `AGENTS.md` | required task rules inspected at baseline commit |
| `docs/PROJECT_CONTEXT.md` | project context inspected at baseline commit |
| `docs/EXPERIMENT_STATUS.md` | source of stale E2 current-best wording inspected at baseline commit |
| `docs/NEXT_TASK.md` | Phase 7B task definition inspected after fast-forward pull |
| `runs/handoff_latest.md` | source of stale E2 best-model handoff wording inspected at baseline commit |
| `runs/phase4b_report.md` | canonical clean blocked-split R4 decision source |
| `runs/clean_block64g16_protocol.md` | frozen split cardinality and integrity source |
| `runs/phase7a_asset_readiness_report.md` | strict V18 blocker and preflight history source |
| `docs/TASK_BLOCKER.md` | stale branch-divergence blocker and strict-preflight blocker source |
| `AUTHOR_FINAL_INPUTS_REQUIRED_V18.md` | author/external input requirement source |
| `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md` | final Fig. 1-6 asset requirement source |
| `submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md` | final table requirement source |
| `scripts/preflight_submission.py` | strict and placeholder preflight rule source |
| `rarepdet/tools/generate_handoff.py` | handoff regeneration source updated in Phase 7B |
| `rarepdet/tools/update_project_status.py` | experiment-status regeneration source updated in Phase 7B |

## Detected Inconsistencies And Actions

| Inconsistency | Corrective action |
| --- | --- |
| `docs/EXPERIMENT_STATUS.md` placed legacy random-split E2 under `Current best model`. | Updated the status generator so the top section is the clean blocked-split R4 publication headline, and legacy E0-E6 rows appear only under historical/exploratory random-split wording. |
| `runs/handoff_latest.md` placed legacy random-split E2 under `Best Model` before the clean split decision. | Updated the handoff generator so R4 appears first as the official publication headline and E0-E6 rankings are explicitly legacy random-split historical rankings. |
| The handoff still described Phase 7A as the active task after `docs/NEXT_TASK.md` moved to Phase 7B. | Updated task parsing and Phase 7B summary hooks so regeneration recognizes the current Phase 7B task and ledger/report outputs. |
| `docs/TASK_BLOCKER.md` still mixed a resolved branch-divergence history with the actual strict V18 blockers. | Rewritten blocker scope is limited to unresolved strict-preflight blockers from missing author metadata, release/data governance facts, final assets, final tables, claim approval, environment details, and compile readiness. |
| Strict V18 blockers were spread across multiple files rather than one auditable closure list. | Created `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md` and `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`. |

## Canonical Headline Statement

The official clean blocked-split manuscript headline is `R4 Reliability p=0.20` on `block64_guard16_seed0`, controlled seeds `0` and `2`.

Controlled-seed means: F1@0.50 `0.920861`, AP50 `0.962495`, AP75 `0.891266`, w/o RGB AP50 `0.916051`, w/o Thermal AP50 `0.718277`, and w/o Event AP50 `0.961577`.

Phase 4B decision: `SELECT R4 AS CLEAN-SPLIT MAIN VARIANT`.

Former E0-E6 random-split results are historical/exploratory diagnostics only and must not be labeled as the manuscript headline, current best model, or publication-grade independent benchmark.

## Preflight Outcomes

| Command | Outcome | Notes |
| --- | --- | --- |
| `git switch research/ra-repdet-triair` | PASS | branch already selected during Phase 7B start |
| `git pull --ff-only research research/ra-repdet-triair` | PASS | fast-forwarded to Phase 7B task definition before edits |
| `git status --short` | PASS | showed unrelated untracked files only before Phase 7B edits |
| `python scripts/preflight_submission.py --root . --allow-placeholders` | PASS with warnings | placeholder mode passed while warning about author placeholders and missing final figures |
| `python rarepdet/tools/generate_handoff.py` | PASS | refreshed `runs/handoff_latest.md` and `runs/handoff_latest.json` |
| `python rarepdet/tools/update_project_status.py` | PASS | refreshed `docs/EXPERIMENT_STATUS.md` |
| `python scripts/preflight_submission.py --root . --allow-placeholders` | PASS with warnings | final placeholder-mode run still warns about author placeholders, table placeholders, and missing final figures |
| `python scripts/preflight_submission.py --root .` | FAIL as expected | strict mode fails on unresolved author metadata, placeholders, table placeholders, and missing final Fig. 1-6 assets |

## Open Ledger Counts

| Category | Open items |
| --- | ---: |
| author_metadata | 4 |
| declarations | 5 |
| data_governance | 4 |
| release_archive | 6 |
| figure_asset | 6 |
| table_asset | 1 |
| claim_scope | 2 |
| environment | 1 |
| compile_readiness | 1 |
| **Total** | **30** |

## Non-Modification Confirmation

No scientific metric, checkpoint, split manifest, raw source data, label file, image asset, rendered final figure, final PDF, training script, model implementation, dataset loader, loss logic, or primary AP-evaluation file was changed in Phase 7B. No GPU training, GPU inference sweep, metric-changing evaluation, split mutation, or source-data mutation was run.

## Next External Inputs Required

1. Final author names, affiliations, ORCIDs, corresponding email, funding, acknowledgments, contributions, competing interests, and AI-use disclosure approval.
2. TriAir citation/data card, dataset version/provider, licence, access terms, and redistribution permission.
3. Public release URL, release tag, immutable commit/archive hash, archive date, release licence, and Zenodo DOI if applicable.
4. Final author-approved Fig. 1-2 Visio-dependent assets and final author-approved Fig. 3-6 publication assets.
5. Final publication Tables 1-7 inserted from existing evidence without changing values.
6. Author approval of validation-only wording, or separately produced independent held-out test evidence under a locked protocol.
7. Final hardware/software environment record.
8. Final strict preflight PASS and Springer `sn-jnl` compile after all ledger items are closed.

## Changed Files Planned For Commit

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

Final commit SHA: pending until the completion commit is created.
