# RA-RepDet-TriAir Handoff

Generated: 2026-06-21T17:21:55+08:00
Workspace: `E:\RepViT-main`

## Current Blocker

Phase 2B ACRF from `docs/NEXT_TASK.md` is blocked because the required local workspace drive is not mounted in the current Windows session.

- `Get-PSDrive -PSProvider FileSystem` shows only `C:` and `D:`.
- `Test-Path 'E:\RepViT-main'` returns `False`.
- `gh --version` and `gh auth status` fail because `gh` is not on PATH.
- The blocker is documented in `docs/TASK_BLOCKER.md`.
- No E0/E1/E2 training results, weights, datasets, or core training files were modified during this blocked handoff update.

Smallest safe next action: restore access to `E:\RepViT-main`, then run `git -C E:\RepViT-main status -sb` and resume Phase 2B from `docs/NEXT_TASK.md` without deleting any local E5 artifacts.

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

## Phase 2B Status

- Active task: Availability-Conditioned Reliability Fusion (ACRF), defined in `docs/NEXT_TASK.md`.
- Status: blocked by missing local `E:` workspace and unavailable `gh` CLI.
- Required blocked files/artifacts: local ACRF source changes, any partial E5 checkpoints, and local `runs/E5_acrf_dropout015_repvit_fcos_e50` artifacts cannot currently be inspected.
- Blocker report: `docs/TASK_BLOCKER.md`.

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

- Restore access to `E:\RepViT-main`.
- Resume Phase 2B ACRF from `docs/NEXT_TASK.md` once the workspace is available.
- If the local E5 partial checkpoint exists, inspect and resume from `runs/E5_acrf_dropout015_repvit_fcos_e50/weights/last.pt`; do not delete or overwrite it.
- If the local workspace cannot be restored, re-clone the research branch on an available drive and rerun Phase 2B from scratch.

## Recently Modified Files

- `A docs/TASK_BLOCKER.md`
- `M runs/handoff_latest.md`

## Next Recommended Tasks

- Restore `E:` drive access and verify `E:\RepViT-main`.
- Resume or reconstruct the Phase 2B ACRF implementation.
- Run the required ACRF smoke test before any long training.
- Complete E5 training/evaluation only after the smoke test passes.
