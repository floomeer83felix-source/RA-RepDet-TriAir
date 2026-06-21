# RA-RepDet-TriAir Handoff

Generated: 2026-06-21T13:05:48
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

## Model And Code Structure

- E0: 5-channel early fusion -> 1x1 Conv(5,3) -> RepViT-M0.9 -> FPN -> FCOS.
- E1: RGB/Thermal/Event reliability stems -> alpha fusion -> Conv(16,3) -> RepViT-M0.9 -> FPN -> FCOS.
- E2: E1 plus modality dropout 0.15 during training.
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

- Review Phase 2A paper-facing result package in runs/phase2a_report.md.
- Select qualitative cases from compare_E0_E1_E2 outputs.
- Run brightness/noise robustness tests if needed for the robustness section.
- Decide whether Phase 2B should add noise/weather proxies or qualitative failure-case mining.

## Recently Modified Files

- `M docs/EXPERIMENT_STATUS.md`
- ` M runs/handoff_latest.json`
- ` M runs/handoff_latest.md`
- ` M runs/phase2a_profile_e0/profile_raw_runs.csv`
- ` M runs/phase2a_profile_e0/profile_results.csv`
- ` M runs/phase2a_profile_e0/profile_results.txt`
- ` M runs/phase2a_profile_e2/profile_raw_runs.csv`
- ` M runs/phase2a_profile_e2/profile_results.csv`
- ` M runs/phase2a_profile_e2/profile_results.txt`
- ` M runs/phase2a_report.md`

## Next Recommended Tasks

- Publish this lightweight workspace without datasets, weights, npy files, or visual outputs.
- Add paper tables from profile, threshold sweep, missing-modality, and final eval summaries.
- Use E2 as the robustness-oriented best model and E1 as the best F1 threshold-sweep model.
