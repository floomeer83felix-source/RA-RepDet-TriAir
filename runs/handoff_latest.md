# RA-RepDet-TriAir Handoff

Generated: 2026-06-22T07:48:04
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

## Model And Code Structure

- E0: 5-channel early fusion -> 1x1 Conv(5,3) -> RepViT-M0.9 -> FPN -> FCOS.
- E1: RGB/Thermal/Event reliability stems -> alpha fusion -> Conv(16,3) -> RepViT-M0.9 -> FPN -> FCOS.
- E2: E1 plus modality dropout 0.15 during training.
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

- Review Phase 2C MSCD evidence report in runs/mscd_evidence_report.md.
- Select qualitative cases from compare_E0_E1_E2 outputs.
- Keep E2 as the main paper model unless a later task defines a stronger controlled improvement.
- Run brightness/noise robustness tests if needed for the robustness section.

## Recently Modified Files

- `M docs/EXPERIMENT_STATUS.md`
- ` M rarepdet/tools/finish_task.ps1`
- ` M rarepdet/tools/generate_handoff.py`
- ` M rarepdet/tools/update_project_status.py`
- ` M runs/handoff_latest.json`
- ` M runs/handoff_latest.md`
- `?? docs/MSCD_DESIGN.md`
- `?? rarepdet/tools/build_mscd_report.py`
- `?? rarepdet/tools/test_mscd.py`
- `?? rarepdet/train_mscd.py`
- `?? runs/E6_mscd_dropout015_repvit_fcos_e50/`
- `?? runs/mscd_evidence_report.md`
- `?? runs/mscd_evidence_summary.csv`
- `?? runs/mscd_smoke_test.md`
- `?? runs/phase2c_report.md`

## Next Recommended Tasks

- Use E2 as the main robustness model unless the paper specifically needs the alpha-correctness ACRF ablation.
- Use E5 as an ablation showing exact zero absent-modality alpha with a small parameter increase.
- Use E6 as a training-strategy ablation because Phase 2C did not satisfy the E2 replacement rule.
- Add paper tables from Phase 2A, Phase 2B, and Phase 2C summaries.
