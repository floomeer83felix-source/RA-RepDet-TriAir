# Phase 7F Author Review Intake Report

Generated: 2026-07-04
Workspace: `E:\RepViT-main`
Baseline commit inspected: `7cdac6e`

## Summary

- Created an author-facing figure review packet for Fig. 1-6 without approving any figure asset.
- Created author decision templates for Fig. 1-6 and a safe Fig. 6 panel-review template.
- Ran a local-only Fig. 6 qualitative-panel inventory from `runs/clean_qualitative_manifest.csv`.
- Fig. 3-5 local candidates remain ignored, untracked, non-final review candidates.
- Fig. 1-2 remain author-design schematic dependencies, and Fig. 6 remains pending author panel selection and final composition approval.

## Fig. 3-5 Review Readiness

| Figure | Local candidate | Source CSV | SHA256 | State |
| --- | --- | --- | --- | --- |
| Fig. 3 | `runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf` | `manuscript/figures/fig3_controlled_ablation_source.csv` | `23e2984adac08ebd6584e1c8d56f82d3cdd0dfb9e5e32047d5064481076d21dc` | pending author review; not final |
| Fig. 4 | `runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf` | `manuscript/figures/fig4_missing_modality_source.csv` | `aea82341ac37547ece40428e56bd3d98fabf299304a4b24067a7705eaf642fde` | pending author review; not final |
| Fig. 5 | `runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf` | `manuscript/figures/fig5_reliability_weight_source.csv` | `ef93dca475e9a1fa704856952951fbe47ebb701c9e559ea60abf46d861a1239c` | pending author review; not final |

## Review Packet And Templates

- Author packet: `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`
- Author decision CSV: `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`
- Fig. 6 panel review template: `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md` and `.csv`
- Fig. 6 aggregate inventory check: `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md` and `.csv`

## Fig. 6 Local Inventory

| Metric | Value |
| --- | --- |
| manifest path | `runs/clean_qualitative_manifest.csv` |
| manifest SHA256 | `966a81923d5a91bd4d65578e7d607bc989769bad37489b90e56df76724989608` |
| manifest rows | 20 |
| rows with path metadata | 20 |
| locally existing panel files | 20 |
| missing or unverifiable | 0 |
| local JSON | `runs/local_candidate_figures/phase7f/fig6_panel_inventory.json` |
| image content opened | no |
| image or figure output written | no |
| committed local path or panel filename | no |
| status | ready for author selection |

## Author Decisions Required

- Fig. 1: provide an external schematic source, approve a future implementation from the checklist, revise the checklist, or defer.
- Fig. 2: provide an external schematic source, approve a future implementation from the checklist, revise the checklist, or defer.
- Fig. 3: approve the local non-final candidate or request revision.
- Fig. 4: approve the local non-final candidate or request revision.
- Fig. 5: approve the local non-final candidate or request revision.
- Fig. 6: choose real local validation panels, decide any crop/redaction needs, and approve final composition.

## Remaining Ledger Categories Outside Figures

| Category | Open items |
| --- | ---: |
| author_metadata | 4 |
| declarations | 5 |
| data_governance | 4 |
| release_archive | 6 |
| table_asset | 1 |
| claim_scope | 2 |
| environment | 1 |
| compile_readiness | 1 |

## Command Outcomes

- `git switch research/ra-repdet-triair`: PASS.
- `git pull --ff-only research research/ra-repdet-triair`: PASS.
- `git status --short`: PASS; unrelated pre-existing untracked files remained outside the task.
- `python scripts/preflight_submission.py --root . --allow-placeholders`: PASS with expected warnings before Phase 7F edits.
- `python submission/sivp/figures/figure_candidate_build.py --dry-run --root .`: PASS.
- `python submission/sivp/figures/qualitative_panel_inventory.py --dry-run --root . --output runs/local_candidate_figures/phase7f/fig6_panel_inventory.json`: PASS.
- `git check-ignore -v runs/local_candidate_figures/phase7f/fig6_panel_inventory.json`: PASS.
- `python -m py_compile submission/sivp/figures/qualitative_panel_inventory.py rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py`: PASS.
- `python rarepdet/tools/generate_handoff.py`: PASS.
- `python rarepdet/tools/update_project_status.py`: PASS.
- `python scripts/preflight_submission.py --root . --allow-placeholders`: PASS with expected warnings after Phase 7F.
- `python scripts/preflight_submission.py --root .`: FAIL as expected on unresolved author metadata, final artwork placeholders, release/data placeholders, and missing Fig. 1-6 assets.

## Changed Files Planned For Commit

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
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

Local-only uncommitted output:

- `runs/local_candidate_figures/phase7f/fig6_panel_inventory.json`

## Non-Modification Confirmation

No figure asset, candidate PDF, final PDF, source CSV, model, metric, dataset, split, panel image, raw data, checkpoint, SIVP LaTeX body, or final compiled PDF was changed. No training, GPU inference, metric recomputation, split mutation, source-data mutation, candidate/final figure generation, or LaTeX compilation was run.

## Remaining Blockers

- Author decisions for Fig. 1-6 are still missing.
- Final approved Fig. 1-6 assets are still missing.
- Fig. 1-2 still require author-approved schematic sources or checklist approval.
- Fig. 6 still requires author-approved panel selection, crop/redaction decisions, and final composition approval.
- Author-confirmed metadata and declarations are missing.
- TriAir citation, version, licence, access, and redistribution facts are missing.
- Public release/archive URL, tag, commit/archive hash, date, licence, and DOI facts are missing.
- Validation-only wording approval or independent held-out evidence decision is missing.
- Final hardware/software environment record is missing.
- Strict V18 preflight and final Springer `sn-jnl` compile remain blocked.

## Decision

AUTHOR FIGURE REVIEW INTAKE AND FIG. 6 LOCAL PANEL INVENTORY COMPLETED; FINAL FIGURE AND EXTERNAL AUTHOR/METADATA BLOCKERS REMAIN OPEN.

Final commit SHA: pending until completion commit is created.
