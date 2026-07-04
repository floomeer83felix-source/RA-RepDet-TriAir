# RA-RepDet-TriAir Handoff

Generated: 2026-07-04T15:08:26
Workspace: `E:\RepViT-main`

## Publication Headline

- Official clean blocked-split manuscript headline: R4 Reliability p=0.20 on `block64_guard16_seed0`, seeds 0, 2.
- Controlled-seed means: F1@0.50 0.920861, AP50 0.962495, AP75 0.891266, w/o RGB AP50 0.916051, w/o Thermal AP50 0.718277, w/o Event AP50 0.961577.
- Phase 4B decision: SELECT R4 AS CLEAN-SPLIT MAIN VARIANT.
- Scope note: Former E0-E6 random-split results are historical/exploratory diagnostics only.

## Current Active Task

- Task file: `docs/NEXT_TASK.md`
- Current Task: Phase 7F — Author Figure Review Intake and Fig. 6 Panel Inventory
- Goal: Prepare a clear author-review packet for the three local, non-final Fig. 3–5 candidates; make the Fig. 1–2 schematic decisions explicit; and perform a local-only inventory of real Fig. 6 validation panels referenced by the existing qualitative manifest. This task organizes review evidence and decisions. It must not approve assets on the authors’ behalf, generate final figures, insert figures into LaTeX, or change research evidence.
- Commit Message: `docs: add author figure review intake and panel inventory`

## Dataset

- Root: `D:\download\triair`
- Samples: 10489
- Images with label txt: 9751
- Images without label txt: 738
- Empty label txt files: 1
- Total valid boxes: 30634
- Val images / boxes: 2098 / 6074
- Note: Missing txt files are treated as empty-target images.

## Historical/Exploratory Random-Split Results

- Legacy E0-E6 rows below are retained for provenance only and are not the current manuscript headline.

| Method | Precision | Recall | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.028842 | 0.996213 | 0.976620 | 0.928824 | 6074 | 209800 | 0.135346 |
| E1 Reliability Fusion | 0.028866 | 0.997037 | 0.979317 | 0.947634 | 6074 | 209800 | 0.125795 |
| E2 Reliability + Dropout 0.15 | 0.028837 | 0.996049 | 0.979990 | 0.950906 | 6074 | 209800 | 0.131865 |
| E3 Reliability + Dropout 0.10 | 0.949248 | 0.945341 | 0.977738 | 0.945218 | 6074 | 6049 | 0.774961 |
| E4 Reliability + Dropout 0.20 | 0.946437 | 0.951268 | 0.978692 | 0.948514 | 6074 | 6105 | 0.799311 |
| E5 ACRF + Dropout 0.15 | 0.938290 | 0.953737 | 0.978066 | 0.946602 | 6074 | 6174 | 0.779350 |
| E6 MSCD + Dropout 0.15 | 0.937297 | 0.949951 | 0.974990 | 0.945138 | 6074 | 6156 | 0.801200 |

## Legacy Random-Split Historical Ranking

- Legacy random-split AP50 leader: E2 Reliability + Dropout 0.15 (0.979990)
- Legacy random-split AP75 leader: E2 Reliability + Dropout 0.15 (0.950906)
- These rankings must not be described as the current best or manuscript-selected model.

## Phase 2A Outputs

- Report: `runs/phase2a_report.md`
- Main table rows: 3
- E0 profile rows: 2
- E2 profile rows: 2
- Brightness-proxy rows: 9
- Alpha mode rows: 8

## Phase 2B ACRF Outputs

- Report: `runs/acrf_evidence_report.md`
- Smoke test: `runs/acrf_smoke_test.md`
- Evidence rows: 3
- E5 missing-modality rows: 7
- E5 alpha-mode rows: 4

## Phase 2C MSCD Outputs

- Report: `runs/mscd_evidence_report.md`
- Phase 2C report: `runs/phase2c_report.md`
- Smoke test: `runs/mscd_smoke_test.md`
- Evidence rows: 4
- E6 missing-modality rows: 7

## Phase 3A Outputs

- Dropout report: `runs/dropout_ablation_summary.md`
- Qualitative report: `runs/qualitative_cases_summary.md`
- Phase 3A report: `runs/phase3a_report.md`
- Dropout ablation rows: 4
- Qualitative manifest rows: 25

## Phase 3B Outputs

- Split-integrity report: `runs/split_integrity_summary.md`
- Dropout selection note: `runs/dropout_ratio_selection_note.md`
- Phase 3B report: `runs/phase3b_report.md`
- Split summary rows: 26
- Nearest-pair rows: 2098
- Manual-review rows: 50
- Exact duplicate rows: 0

## Phase 3C Outputs

- RGB duplicate report: `runs/rgb_cross_split_duplicate_summary.md`
- Blocked split report: `runs/blocked_split_proposal_summary.md`
- RGB strata report: `runs/rgb_separation_strata_summary.md`
- Phase 3C report: `runs/phase3c_report.md`
- RGB duplicate summary rows: 20
- RGB exact pair rows: 153
- RGB group rows: 153
- Blocked split candidate rows: 3
- RGB strata rows: 6

## Phase 4A Outputs

- Clean split protocol: `runs/clean_block64g16_protocol.md`
- Clean summary: `runs/clean_block64g16_summary.md`
- Phase 4A report: `runs/phase4a_report.md`
- Clean summary rows: 4
- B1 missing-modality rows: 7
- B2 missing-modality rows: 7
- B4 missing-modality rows: 7

## Phase 4B Controlled-Seed Outputs

- Smoke test: `runs/seed_reproducibility_smoke.md`
- Seed replication report: `runs/clean_block64g16_seed_replication.md`
- Phase 4B report: `runs/phase4b_report.md`
- Seed replication rows: 8
- R1 missing-modality rows: 14
- R2 missing-modality rows: 14
- R4 missing-modality rows: 14
- Decision: SELECT R4 AS CLEAN-SPLIT MAIN VARIANT

## Phase 5A Paper-Readiness Outputs

- Phase 5A report: `runs/phase5a_report.md`
- YOLO11n protocol: `runs/yolo11n_rgb_baseline_protocol.md`
- Paper-readiness summary rows: 18
- Convergence rows: 8
- Efficiency rows: 4
- R4 reliability-weight rows: 8
- Qualitative manifest rows: 20
- YOLO11n eval rows: 2
- Decision: READY FOR MANUSCRIPT DRAFTING

## Phase 6A Manuscript Outputs

- Manuscript README: `manuscript/README.md`
- Draft manuscript: `manuscript/RA_RepDet_manuscript_v1.md`
- Phase 6A report: `runs/phase6a_manuscript_report.md`
- Table CSV files: 7
- Table Markdown files: 7
- Figure source CSV files: 3
- Figure manifest: `manuscript/figures/figure_manifest.md`
- Verified reference inventory rows: 31
- Claim ledger: `manuscript/submission_notes/claim_ledger.md`
- Self-audit: `manuscript/submission_notes/manuscript_self_audit.md`
- Decision: MANUSCRIPT DRAFT READY FOR JOURNAL TARGETING

## Phase 6B SIVP Submission-Source Outputs

- SIVP README: `submission/sivp/README.md`
- Main LaTeX source: `submission/sivp/tex/main.tex`
- Body LaTeX source: `submission/sivp/tex/ra_repdet_sivp.tex`
- BibTeX references: `submission/sivp/tex/references.bib`
- Phase 6B report: `runs/phase6b_sivp_preparation_report.md`
- Template/LaTeX source files: 16
- Metadata template files: 8
- Review/audit files: 18
- Figure insertion map: `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`
- Table insertion map: `submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md`
- Decision: READY FOR ASSISTANT FINAL FIGURES, TABLES, AND AUTHOR METADATA

## Phase 7B Publication-State Reconciliation

- Reconciliation report: `runs/phase7b_publication_state_reconciliation.md`
- Reconciliation JSON: `runs/phase7b_publication_state_reconciliation.json`
- Input ledger: `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
- Input ledger CSV: `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`
- Ledger rows: 30
- Open ledger items: 30
- Open categories: author_metadata=4, claim_scope=2, compile_readiness=1, data_governance=4, declarations=5, environment=1, figure_asset=6, release_archive=6, table_asset=1
- Command outcomes: git switch research/ra-repdet-triair: PASS; git pull --ff-only research research/ra-repdet-triair: PASS; git status --short: PASS; unrelated untracked files existed before Phase 7B edits; python scripts/preflight_submission.py --root . --allow-placeholders: PASS with warnings; python rarepdet/tools/generate_handoff.py: PASS; python rarepdet/tools/update_project_status.py: PASS; python scripts/preflight_submission.py --root . --allow-placeholders: PASS with warnings after reconciliation; python scripts/preflight_submission.py --root .: FAIL as expected on unresolved author metadata, placeholders, table placeholders and missing final Fig. 1-6 assets
- Phase 7B changed files: `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, `runs/handoff_latest.md`, `runs/handoff_latest.json`, `runs/phase7b_publication_state_reconciliation.md`, `runs/phase7b_publication_state_reconciliation.json`, `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`, `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`, `rarepdet/tools/generate_handoff.py`, `rarepdet/tools/update_project_status.py`
- Residual blockers: author-confirmed metadata and declarations are missing; TriAir citation/version/licence/access/redistribution facts are missing; public release/archive URL, tag, commit/archive hash, date, licence and DOI facts are missing; final approved Fig. 1-6 assets are missing; final publication Tables 1-7 remain pending; validation-only wording approval or independent held-out evidence decision is missing; final hardware/software environment record is missing; strict V18 preflight and final Springer sn-jnl compile remain blocked
- Final commit SHA: pending until the completion commit is created
- Phase 7B status: publication-state mismatch resolved; strict preflight remains blocked by author/asset inputs.

## Phase 7C Evidence-Locked Table Insertion

- Table insertion report: `runs/phase7c_table_insertion_report.md`
- Table insertion JSON: `runs/phase7c_table_insertion_report.json`
- Source traceability: `submission/sivp/tables/TABLE_SOURCE_TRACEABILITY.md`
- Rendering check: `submission/sivp/review/TABLE_RENDERING_CHECK.md`
- Table fragments inserted: 7
- Table validation outcome: pass
- Command outcomes: git switch research/ra-repdet-triair: PASS; git pull --ff-only research research/ra-repdet-triair: PASS; git status --short: PASS; unrelated untracked files existed before Phase 7C edits; python scripts/preflight_submission.py --root . --allow-placeholders: PASS with warnings before table insertion; table fragment generation: PASS; 7 fragments created from unchanged source CSVs; table rendering check: PASS; 12 pass and 2 warning checks; python -m py_compile rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py: PASS; python rarepdet/tools/generate_handoff.py: PASS; python rarepdet/tools/update_project_status.py: PASS; python scripts/preflight_submission.py --root . --allow-placeholders: PASS with warnings after table insertion; no TABLE PLACEHOLDER warning remains; python scripts/preflight_submission.py --root .: FAIL as expected on author metadata, final artwork placeholders, release/data placeholders and missing Fig. 1-6 assets; no TABLE PLACEHOLDER failure remains
- Phase 7C changed files: `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, `runs/handoff_latest.md`, `runs/handoff_latest.json`, `runs/phase7c_table_insertion_report.md`, `runs/phase7c_table_insertion_report.json`, `submission/sivp/tex/ra_repdet_sivp.tex`, `submission/sivp/tables/Table_1_dataset_and_clean_split.tex`, `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex`, `submission/sivp/tables/Table_3_controlled_ablation.tex`, `submission/sivp/tables/Table_4_missing_modality_robustness.tex`, `submission/sivp/tables/Table_5_rgb_only_external_baseline.tex`, `submission/sivp/tables/Table_6_efficiency_and_convergence.tex`, `submission/sivp/tables/Table_7_reliability_weight_audit.tex`, `submission/sivp/tables/TABLE_SOURCE_TRACEABILITY.md`, `submission/sivp/tables/TABLE_SOURCE_TRACEABILITY.csv`, `submission/sivp/review/TABLE_RENDERING_CHECK.md`, `submission/sivp/review/TABLE_RENDERING_CHECK.csv`, `rarepdet/tools/generate_handoff.py`, `rarepdet/tools/update_project_status.py`
- Residual blockers: author-confirmed metadata and declarations are missing; TriAir citation/version/licence/access/redistribution facts are missing; public release/archive URL, tag, commit/archive hash, date, licence and DOI facts are missing; final approved Fig. 1-6 assets are missing; validation-only wording approval or independent held-out evidence decision is missing; final hardware/software environment record is missing; strict V18 preflight and final Springer sn-jnl compile remain blocked
- Final commit SHA: pending until the completion commit is created
- Phase 7C status: table placeholders removed; strict preflight remains blocked by non-table external inputs.

## Phase 7D Figure Source Lock

- Figure source-lock report: `runs/phase7d_figure_source_lock_report.md`
- Figure source-lock JSON: `runs/phase7d_figure_source_lock_report.json`
- Figure traceability: `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md` and `.csv`
- Figure build spec: `submission/sivp/figures/FIGURE_BUILD_SPEC.md`
- Figure candidate check: `submission/sivp/review/FIGURE_CANDIDATE_CHECK.md` and `.csv`
- Traceability rows: 6
- Review-check rows: 10
- Dry-run result: PASS
- Figure readiness states: Fig. 1=author-design required; Fig. 2=author-design required; Fig. 3=candidate build spec ready; Fig. 4=candidate build spec ready; Fig. 5=candidate build spec ready; Fig. 6=local-panel inventory required
- Command outcomes: git switch research/ra-repdet-triair: PASS; git pull --ff-only research research/ra-repdet-triair: PASS; git status --short: PASS; unrelated pre-existing untracked files remain outside this task; python scripts/preflight_submission.py --root . --allow-placeholders: PASS with expected warnings before Phase 7D edits; python -m py_compile submission/sivp/figures/figure_candidate_build.py rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py: PASS; python submission/sivp/figures/figure_candidate_build.py --dry-run --root .: PASS; wrote no artwork; final/candidate artifact check after dry run: PASS; no Fig1-Fig6 final PDF and no *_candidate image/PDF/SVG/JPG/EPS output found; python rarepdet/tools/generate_handoff.py: PASS; python rarepdet/tools/update_project_status.py: PASS; python scripts/preflight_submission.py --root . --allow-placeholders: PASS with expected warnings after Phase 7D; python scripts/preflight_submission.py --root .: FAIL as expected on unresolved author metadata, final artwork placeholders, release/data placeholders and missing Fig. 1-6 assets
- Phase 7D changed files: `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, `runs/handoff_latest.md`, `runs/handoff_latest.json`, `runs/phase7d_figure_source_lock_report.md`, `runs/phase7d_figure_source_lock_report.json`, `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`, `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md`, `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.csv`, `submission/sivp/figures/FIGURE_BUILD_SPEC.md`, `submission/sivp/figures/figure_candidate_build.py`, `submission/sivp/review/FIGURE_CANDIDATE_CHECK.md`, `submission/sivp/review/FIGURE_CANDIDATE_CHECK.csv`, `rarepdet/tools/generate_handoff.py`, `rarepdet/tools/update_project_status.py`
- Residual blockers: author-confirmed metadata and declarations are missing; TriAir citation, version, licence, access, and redistribution facts are missing; public release/archive URL, tag, commit/archive hash, date, licence, and DOI facts are missing; final approved Fig. 1-6 assets are missing; Fig. 1-2 require author-approved schematic/Visio-style design sources; Fig. 6 requires verified local real validation panel inventory and author-approved selection; validation-only wording approval or independent held-out evidence decision is missing; final hardware/software environment record is missing; strict V18 preflight and final Springer sn-jnl compile remain blocked
- Final commit SHA: pending until completion commit is created
- Phase 7D status: figure sources locked; candidate build spec ready for Fig. 3-5; strict preflight remains blocked by final figure and external author/metadata inputs.

## Phase 7E Local Candidate Renders

- Candidate render report: `runs/phase7e_candidate_render_report.md`
- Candidate render JSON: `runs/phase7e_candidate_render_report.json`
- Candidate render manifest: `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.md` and `.csv`
- Candidate render check: `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.md` and `.csv`
- Manifest rows: 6
- Render-check rows: 13
- Local candidates: Fig. 3=runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf (27440 bytes, not_final); Fig. 4=runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf (26852 bytes, not_final); Fig. 5=runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf (25510 bytes, not_final)
- Local uncommitted outputs: `runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf`, `runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf`, `runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf`, `runs/local_candidate_figures/phase7e/candidate_render_manifest.json`
- Command outcomes: git switch research/ra-repdet-triair: PASS; git pull --ff-only research research/ra-repdet-triair: PASS; git status --short: PASS; unrelated pre-existing untracked files remain outside this task; python scripts/preflight_submission.py --root . --allow-placeholders: PASS with expected warnings before Phase 7E edits; python submission/sivp/figures/figure_candidate_build.py --dry-run --root .: PASS before rendering; python -m py_compile submission/sivp/figures/figure_candidate_build.py: PASS; git check-ignore -v candidate paths: PASS after adding .gitignore rule; python submission/sivp/figures/figure_candidate_build.py --render-candidates --root . --output-dir runs/local_candidate_figures/phase7e: PASS; python submission/sivp/figures/figure_candidate_build.py --dry-run --root .: PASS after rendering; pdftotext provenance check: PASS for all three candidate PDFs; python -m py_compile submission/sivp/figures/figure_candidate_build.py rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py: PASS; python rarepdet/tools/generate_handoff.py: PASS; python rarepdet/tools/update_project_status.py: PASS; python scripts/preflight_submission.py --root . --allow-placeholders: PASS with expected warnings after Phase 7E; python scripts/preflight_submission.py --root .: FAIL as expected on unresolved author metadata, final artwork placeholders, release/data placeholders, and missing Fig. 1-6 assets
- Phase 7E changed files: `.gitignore`, `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, `runs/handoff_latest.md`, `runs/handoff_latest.json`, `runs/phase7e_candidate_render_report.md`, `runs/phase7e_candidate_render_report.json`, `submission/sivp/figures/figure_candidate_build.py`, `submission/sivp/figures/FIGURE_BUILD_SPEC.md`, `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.md`, `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.csv`, `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.md`, `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.csv`, `rarepdet/tools/generate_handoff.py`, `rarepdet/tools/update_project_status.py`
- Residual blockers: candidate Fig. 3-5 PDFs await author review and are not publication assets; final approved Fig. 1-6 assets are still missing; Fig. 1-2 require author-approved schematic/Visio-style design sources; Fig. 6 requires verified local real validation panel inventory and author-approved selection; author-confirmed metadata and declarations are missing; TriAir citation, version, licence, access, and redistribution facts are missing; public release/archive URL, tag, commit/archive hash, date, licence, and DOI facts are missing; validation-only wording approval or independent held-out evidence decision is missing; final hardware/software environment record is missing; strict V18 preflight and final Springer sn-jnl compile remain blocked
- Final commit SHA: pending until completion commit is created
- Phase 7E status: local non-final Fig. 3-5 candidates generated for author review; strict preflight remains blocked by final figure and external author/metadata inputs.

## Phase 7F Author Figure Review Intake

- Author review report: `runs/phase7f_author_review_intake_report.md`
- Author review JSON: `runs/phase7f_author_review_intake_report.json`
- Author review packet: `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`
- Author decision CSV: `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`
- Fig. 6 panel review template: `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md` and `.csv`
- Fig. 6 inventory check: `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md` and `.csv`
- Author decision rows: 6
- Fig. 6 review-template rows: 20
- Fig. 6 local inventory: manifest rows=20; rows with path metadata=20; existing local panels=20; missing/unverifiable=0; status=ready for author selection
- Local uncommitted outputs: `runs/local_candidate_figures/phase7f/fig6_panel_inventory.json`
- Command outcomes: git switch research/ra-repdet-triair: PASS; git pull --ff-only research research/ra-repdet-triair: PASS; git status --short: PASS; unrelated pre-existing untracked files remained outside the task; python scripts/preflight_submission.py --root . --allow-placeholders: PASS with expected warnings before Phase 7F edits; python submission/sivp/figures/figure_candidate_build.py --dry-run --root .: PASS; python submission/sivp/figures/qualitative_panel_inventory.py --dry-run --root . --output runs/local_candidate_figures/phase7f/fig6_panel_inventory.json: PASS; git check-ignore -v runs/local_candidate_figures/phase7f/fig6_panel_inventory.json: PASS; python -m py_compile submission/sivp/figures/qualitative_panel_inventory.py rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py: PASS; python rarepdet/tools/generate_handoff.py: PASS; python rarepdet/tools/update_project_status.py: PASS; python scripts/preflight_submission.py --root . --allow-placeholders: PASS with expected warnings after Phase 7F; python scripts/preflight_submission.py --root .: FAIL as expected on unresolved author metadata, final artwork placeholders, release/data placeholders, and missing Fig. 1-6 assets
- Phase 7F changed files: `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, `runs/handoff_latest.md`, `runs/handoff_latest.json`, `runs/phase7f_author_review_intake_report.md`, `runs/phase7f_author_review_intake_report.json`, `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`, `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`, `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md`, `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv`, `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md`, `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.csv`, `submission/sivp/figures/qualitative_panel_inventory.py`, `rarepdet/tools/generate_handoff.py`, `rarepdet/tools/update_project_status.py`
- Residual blockers: author decisions for Fig. 1-6 are still missing; final approved Fig. 1-6 assets are still missing; Fig. 1-2 still require author-approved schematic sources or checklist approval; Fig. 6 still requires author-approved panel selection, crop/redaction decisions, and final composition approval; author-confirmed metadata and declarations are missing; TriAir citation, version, licence, access, and redistribution facts are missing; public release/archive URL, tag, commit/archive hash, date, licence, and DOI facts are missing; validation-only wording approval or independent held-out evidence decision is missing; final hardware/software environment record is missing; strict V18 preflight and final Springer sn-jnl compile remain blocked
- Final commit SHA: pending until completion commit is created
- Phase 7F status: author review intake and Fig. 6 local panel inventory completed; strict preflight remains blocked by author decisions, final figure assets, and external metadata inputs.

## Model And Code Structure

- E0: 5-channel early fusion -> 1x1 Conv(5,3) -> RepViT-M0.9 -> FPN -> FCOS.
- E1: RGB/Thermal/Event reliability stems -> alpha fusion -> Conv(16,3) -> RepViT-M0.9 -> FPN -> FCOS.
- E2: E1 plus modality dropout 0.15 during training.
- E3: E1 plus modality dropout 0.10 during training.
- E4: E1 plus modality dropout 0.20 during training.
- E5: Availability-conditioned reliability fusion with post-stem masking, masked softmax, and modality dropout 0.15.
- E6: E2 inference architecture trained with modality-subset consistency distillation from frozen E2 full-input teacher.
- labels: TriAir class 0 is shifted to torchvision detection label 1; background remains 0.

- dataset: `datasets/triair_dataset.py`
- split_tool: `tools/create_triair_split.py`
- training: `rarepdet/train_early_fusion.py`
- evaluation: `rarepdet/eval_map.py`
- visualization: `rarepdet/val_early_fusion.py`
- backbones: `rarepdet/models/repvit_fpn_backbone.py`
- detector_builder: `rarepdet/models/early_fusion_fcos.py`
- postprocessing_tools: `rarepdet/tools/`

## Current Pending Experiments

- Strict V18 preflight remains blocked until author-confirmed metadata, TriAir governance facts, release metadata, final approved Fig. 1-6 assets, final environment record, and final compile readiness are supplied.
- Author review packet and decision templates now exist, but every Fig. 1-6 author decision remains pending.
- Fig. 6 local panel inventory found 20 locally existing manifest panels, but no panel selection, crop/redaction, or final composition is approved.
- Local Fig. 3-5 candidate PDFs and the Fig. 6 path-level inventory JSON remain ignored/untracked review inputs, not publication assets.

## Recently Modified Files

- `M docs/EXPERIMENT_STATUS.md`
- ` M docs/TASK_BLOCKER.md`
- ` M rarepdet/tools/generate_handoff.py`
- ` M rarepdet/tools/update_project_status.py`
- ` M runs/handoff_latest.json`
- ` M runs/handoff_latest.md`
- `A  runs/phase7f_author_review_intake_report.json`
- `?? runs/component_disjoint_candidates/`
- `?? runs/phase7f_author_review_intake_report.md`
- `?? runs/v39_component_disjoint/`
- `?? submission/sivp/figures/qualitative_panel_inventory.py`
- `?? submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`
- `?? submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`
- `?? submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.csv`
- `?? submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md`
- `?? submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv`
- `?? submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md`

## Next Recommended Tasks

- Collect written author decisions in submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv.
- Collect Fig. 6 panel selections and crop/redaction decisions in submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv.
- Collect author-confirmed metadata, TriAir governance facts, release/archive metadata, final environment details, and approved final Fig. 1-6 assets.
- Rerun strict V18 preflight and compile the final Springer sn-jnl PDF only after every remaining blocker is closed.
