# RA-RepDet-TriAir Handoff

Generated: 2026-06-27T16:32:30
Workspace: `E:\RepViT-main`

## Dataset

- Root: `D:\download\triair`
- Samples: 10489
- Images with label txt: 9751
- Images without label txt: 738
- Empty label txt files: 1
- Total valid boxes: 30634
- Val images / boxes: 2098 / 6074
- Note: Missing txt files are treated as empty-target images.

## Core Results

| Method | Precision | Recall | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.028842 | 0.996213 | 0.976620 | 0.928824 | 6074 | 209800 | 0.135346 |
| E1 Reliability Fusion | 0.028866 | 0.997037 | 0.979317 | 0.947634 | 6074 | 209800 | 0.125795 |
| E2 Reliability + Dropout 0.15 | 0.028837 | 0.996049 | 0.979990 | 0.950906 | 6074 | 209800 | 0.131865 |
| E3 Reliability + Dropout 0.10 | 0.949248 | 0.945341 | 0.977738 | 0.945218 | 6074 | 6049 | 0.774961 |
| E4 Reliability + Dropout 0.20 | 0.946437 | 0.951268 | 0.978692 | 0.948514 | 6074 | 6105 | 0.799311 |
| E5 ACRF + Dropout 0.15 | 0.938290 | 0.953737 | 0.978066 | 0.946602 | 6074 | 6174 | 0.779350 |
| E6 MSCD + Dropout 0.15 | 0.937297 | 0.949951 | 0.974990 | 0.945138 | 6074 | 6156 | 0.801200 |

## Best Model

- Best AP50: E2 Reliability + Dropout 0.15 (0.979990)
- Best AP75: E2 Reliability + Dropout 0.15 (0.950906)

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

- Choose a target SCI/EI journal before final formatting.
- Finalize citation style and replace manuscript reference placeholders after journal selection.
- Prepare journal-specific figure dimensions from the commit-safe figure manifests and source CSV files.
- Keep random-split E-runs as historical diagnostics only.

## Recently Modified Files

- `M .gitignore`
- ` M docs/EXPERIMENT_STATUS.md`
- ` M rarepdet/tools/finish_task.ps1`
- ` M rarepdet/tools/generate_handoff.py`
- ` M rarepdet/tools/update_project_status.py`
- ` M runs/handoff_latest.json`
- ` M runs/handoff_latest.md`
- `?? manuscript/`
- `?? rarepdet/tools/build_phase6a_manuscript.py`
- `?? runs/phase6a_manuscript_report.md`

## Next Recommended Tasks

- Select the target journal and adapt manuscript formatting, citation style, and figure requirements.
- Review manuscript/RA_RepDet_manuscript_v1.md against the target journal scope and word limits.
- Render final Fig. 1 and Fig. 2 schematics only after target-journal figure specifications are known.
- Keep raw data, weights, rendered panels, and local qualitative assets out of Git.
