# Experiment Status

Generated: 2026-06-21T17:21:55+08:00
Handoff source: `runs/handoff_latest.md`

## Current best model

- Best AP50: E2 Reliability + Dropout 0.15 (0.979990)
- Best AP75: E2 Reliability + Dropout 0.15 (0.950906)

## Current active task

- Task file: `docs/NEXT_TASK.md`
- Current Task: Phase 2B — Availability-Conditioned Reliability Fusion (ACRF)
- Status: blocked
- Blocker report: `docs/TASK_BLOCKER.md`
- Blocker summary: local workspace `E:\RepViT-main` is inaccessible because the `E:` drive is not mounted; `gh` is also unavailable on PATH, so the required local `finish_task.ps1` workflow cannot run.

## Latest completed experiments

| Experiment | Method | Precision | Recall | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0 | Early Fusion | 0.028842 | 0.996213 | 0.976620 | 0.928824 | 6074 | 209800 | 0.135346 |
| E1 | Reliability Fusion | 0.028866 | 0.997037 | 0.979317 | 0.947634 | 6074 | 209800 | 0.125795 |
| E2 | Reliability + Dropout 0.15 | 0.028837 | 0.996049 | 0.979990 | 0.950906 | 6074 | 209800 | 0.131865 |

### Best threshold by F1

| Method | Threshold | Precision | Recall | F1 | AP50 | AP75 | Predictions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.5 | 0.9291325957992624 | 0.9540665130062562 | 0.941434489480952 | 0.9766198396682739 | 0.9288238883018494 | 6237 |
| E1 Reliability Fusion | 0.5 | 0.9257206208425721 | 0.9622983207112282 | 0.9436551501453019 | 0.9793174862861633 | 0.9476337432861328 | 6314 |
| E2 Reliability + Dropout 0.15 | 0.5 | 0.9310565977232644 | 0.9560421468554494 | 0.943383965559256 | 0.9799898266792297 | 0.9509060382843018 | 6237 |

### Missing modality AP50

| Method | Full | w/o RGB | w/o Thermal | w/o Event | RGB only | Thermal only | Event only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.976620 | 0.739537 | 0.410636 | 0.974633 | 0.398050 | 0.700867 | 0.013115 |
| E1 Reliability Fusion | 0.979317 | 0.688697 | 0.370994 | 0.477850 | 0.477494 | 0.000240 | 0.004093 |
| E2 Reliability + Dropout 0.15 | 0.979990 | 0.948710 | 0.811566 | 0.978972 | 0.802234 | 0.863495 | 0.304352 |

### Missing modality AP75

| Method | Full | w/o RGB | w/o Thermal | w/o Event | RGB only | Thermal only | Event only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.928824 | 0.564886 | 0.333051 | 0.925954 | 0.312297 | 0.536687 | 0.001062 |
| E1 Reliability Fusion | 0.947634 | 0.600607 | 0.350580 | 0.345952 | 0.347069 | 0.000003 | 0.000245 |
| E2 Reliability + Dropout 0.15 | 0.950906 | 0.820473 | 0.552192 | 0.948703 | 0.542798 | 0.663646 | 0.171463 |

### Model profile

| Model | Params | Trainable Params | GFLOPs | FPS | Latency ms/img | CUDA Memory MB |
| --- | --- | --- | --- | --- | --- | --- |
| E0/Early Fusion | 6591609 | 6591609 | 105.207355 | 24.914556 | 40.137179 | 123.43 |
| E1/E2 Reliability Fusion | 6593293 | 6593293 | 105.981501 | 47.389574 | 21.101688 | 236.40 |

## Phase 2A outputs

- Report: `runs/phase2a_report.md`
- Paper main threshold: score threshold 0.50
- Brightness-proxy groups: RGB mean-intensity terciles, not day/night labels
- Alpha mode rows: full, no_rgb, no_thermal, no_event for E1 and E2

## Pending tasks

- Restore access to `E:\RepViT-main` and verify the local worktree.
- Resume Phase 2B ACRF implementation from `docs/NEXT_TASK.md`.
- If `runs/E5_acrf_dropout015_repvit_fcos_e50/weights/last.pt` exists locally, inspect and resume instead of deleting it.
- Run the required ACRF smoke test before any long training.
- Complete E5 evaluation and evidence report after training finishes.

## Known metric caveats

- Precision in the first-batch eval at score threshold 0.001 is artificially low because many low-confidence FCOS predictions are retained.
- AP50/AP75 are computed by score sorting and are not directly tied to the display threshold.
- Threshold sweep indicates 0.50 is the best F1 threshold for E0/E1/E2 in the current val split.
- Missing-modality tables use score threshold 0.05.
- Current AP implementation is project-local and does not depend on pycocotools.

## Important research decisions

- Missing txt labels are treated as empty-target images.
- TriAir class 0 is shifted to torchvision label 1; background remains label 0.
- E0/E1/E2 completed 50-epoch first-batch experiments and should not be retrained without explicit instruction.
- E2 is the strongest robustness-oriented model by missing-modality AP50/AP75.
- E1 has the highest F1 in the threshold sweep at threshold 0.50.
- Phase 2B should remain a targeted ACRF correction, not a generic attention or transformer expansion.

## Files or scripts currently under review

- `docs/NEXT_TASK.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `rarepdet/tools/finish_task.ps1`
