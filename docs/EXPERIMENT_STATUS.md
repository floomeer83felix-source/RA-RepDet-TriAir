# Experiment Status

Generated: 2026-06-21T13:05:48
Handoff source: `E:\RepViT-main\runs\handoff_latest.md`

## Current best model

- Best AP50: E2 Reliability + Dropout 0.15 (0.979990)
- Best AP75: E2 Reliability + Dropout 0.15 (0.950906)

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

### Paper main results at score threshold 0.50

| Method | Threshold | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.50 | 0.929133 | 0.954067 | 0.941434 | 0.976620 | 0.928824 | 6074 | 6237 | 0.769583 |
| E1 Reliability Fusion | 0.50 | 0.925721 | 0.962298 | 0.943655 | 0.979317 | 0.947634 | 6074 | 6314 | 0.794935 |
| E2 Reliability + Dropout 0.15 | 0.50 | 0.931057 | 0.956042 | 0.943384 | 0.979990 | 0.950906 | 6074 | 6237 | 0.788404 |

### Phase 2A profile summary

| Model | Path | Batch Size | Img Size | Warmup | Iters | Repeats | Params | FPS mean | Latency ms/img mean | CUDA Memory MB mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | raw_forward | 1 | 640 | 100 | 300 | 3 | 6591609 | 111.427245 | 8.977959 | 115.153333 |
| early | detector_inference | 1 | 640 | 100 | 300 | 3 | 6591609 | 55.488686 | 18.030040 | 122.680000 |
| reliability | raw_forward | 1 | 640 | 100 | 300 | 3 | 6593293 | 117.451207 | 8.515909 | 228.006667 |
| reliability | detector_inference | 1 | 640 | 100 | 300 | 3 | 6593293 | 55.884826 | 17.895982 | 235.820000 |

### Phase 2A brightness-proxy outputs

- Rows: 9
- Groups: RGB mean-intensity terciles, not day/night labels.

### Phase 2A alpha outputs

- Rows: 8
- Modes: full, no_rgb, no_thermal, no_event for E1 and E2.


## Current active task

- Task file: `docs/NEXT_TASK.md`
- Current Task: Execute Phase 2A post-processing for paper-ready RA-RepDet TriAir results.
- Goal: Produce the Phase 2A paper-facing result package: threshold=0.50 main metrics, repeated E0/E2 profiling, brightness-proxy grouped evaluation, reliability alpha statistics, and a consolidated report.

## Pending tasks

- Review Phase 2A paper-facing result package in runs/phase2a_report.md.
- Select qualitative cases from compare_E0_E1_E2 outputs.
- Run brightness/noise robustness tests if needed for the robustness section.
- Decide whether Phase 2B should add noise/weather proxies or qualitative failure-case mining.

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

## Files or scripts currently under review

- `AGENTS.md`
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/PROJECT_CONTEXT.md`
- `rarepdet/tools/update_project_status.py`
- `rarepdet/tools/finish_task.ps1`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
