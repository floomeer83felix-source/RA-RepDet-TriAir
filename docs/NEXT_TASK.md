# Current Task

## Active task

`V81_RETRAIN_NINE_SINGLE_MODALITY_CHECKPOINTS`

The user explicitly authorized regeneration of all nine missing single-modality checkpoints on 2026-07-30:

- RGB-only: seeds 0, 1, and 2;
- thermal-only: seeds 0, 1, and 2;
- event-only: seeds 0, 1, and 2.

These are new V81 retraining outputs. They must not be represented as the lost original checkpoints underlying the user-supplied V77 rows.

## Frozen training contract

- dataset: `D:\download\triair`;
- train split: `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt`;
- development-validation split: `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt`;
- modes: exactly `rgb`, `thermal`, and `event`;
- seeds: exactly `0`, `1`, and `2`;
- epochs: exactly `50`;
- batch size: `4`;
- image size: `640`;
- optimizer: AdamW;
- learning rate: `1e-4`;
- weight decay: `1e-4`;
- modality dropout: `0.0`;
- workers: `0`;
- device: CUDA on the authorized RTX 3090;
- checkpoint rule: highest development-validation project-local AP50;
- authorized checkpoint names: each run's newly generated `weights/best.pt`;
- guard access: forbidden;
- tuning, early stopping, seed replacement, selective rerun, and checkpoint substitution: forbidden.

## Execution

Use the installed PyTorch environment:

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/tools/run_v76_single_modality_queue.py --data D:\download\triair --device cuda --resume
```

The queue must run serially in the fixed order:

1. `rgb_seed0`, `rgb_seed1`, `rgb_seed2`;
2. `thermal_seed0`, `thermal_seed1`, `thermal_seed2`;
3. `event_seed0`, `event_seed1`, `event_seed2`.

## Required outputs

For every run:

```text
runs/v76_triair_single_modality_ablation/training/<mode>_seed<seed>/
  run_status.json
  train_log.txt
  weights/best.pt
  weights/last.pt
```

The queue must also produce nine raw evaluation JSON files and the compact V76 summary. Large `.pt` files remain local and must not be committed.

## Completion and V80 gate

After 9/9 training runs finish:

1. verify every run completed 50 epochs;
2. record best epoch and SHA256 for every new `best.pt`;
3. run the V79 standardized COCO evaluator on the nine new checkpoints;
4. compare AP50/AP75 with V77 without claiming checkpoint identity;
5. explain material differences as new-run versus supplied-record differences;
6. create V80 manuscript evidence only if all evaluation and reconciliation gates pass;
7. update handoff and push compact evidence only.

V78 remains authoritative while training or evaluation is incomplete.

## Estimated runtime

Historical RTX 3090 runs indicate approximately 5.7-7.0 hours per 50-epoch model. Nine serial runs are expected to require about 50-63 hours, plus final evaluation.

## Commit Message

exp: authorize V81 nine-run single-modality retraining
