# Current Task

## Active task

`V81_COMPLETE_EVIDENCE_SOURCE_DECISION_PENDING`

The user explicitly authorized regeneration of all nine missing single-modality checkpoints on 2026-07-30:

- RGB-only: seeds 0, 1, and 2;
- thermal-only: seeds 0, 1, and 2;
- event-only: seeds 0, 1, and 2.

These are new V81 retraining outputs. They must not be represented as the lost original checkpoints underlying the user-supplied V77 rows.

## Newly supplied standardized metric table

The user has now supplied nine rows of AP@[0.50:0.95], AP50, AP75, AR1, AR10, and AR100. They are recorded under:

```text
runs/v80_supplied_standardized_single_modality_metrics/
```

Independent arithmetic passed. Every AP50/AP75 value matches V77 exactly to three decimal places. The table does not include checkpoint SHA256, checkpoint epoch, split SHA256, runtime identity, or original evaluator JSON files, so the current V81 replication/provenance task remains active.

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

## Live execution

- started: `2026-07-30T08:04:13+08:00`;
- workspace: `E:\RepViT-v74-clean`;
- queue PID at launch: `57884`;
- active run at last confirmation: `rgb_seed0`;
- queue stdout: `runs/v76_triair_single_modality_ablation/execution_logs/v81_queue_stdout.log`;
- queue stderr: `runs/v76_triair_single_modality_ablation/execution_logs/v81_queue_stderr.log`;
- local launch record: `runs/v76_triair_single_modality_ablation/v81_queue_launch.json`;
- final state: training `9/9` complete, standardized COCO evaluation `9/9` complete;
- compact evidence: `runs/v79_single_modality_evaluator_completion/` and `runs/v81_single_modality_retraining_reconciliation/`.

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

## Completion and manuscript gate

After 9/9 training runs finish:

1. verify every run completed 50 epochs;
2. record best epoch and SHA256 for every new `best.pt`;
3. run the V79 standardized COCO evaluator on the nine new checkpoints;
4. compare the V81 standardized rows with both V77 and the newly supplied V80 table without claiming checkpoint identity;
5. explain every material difference as new-run versus supplied-record evidence;
6. archive compact evaluator JSON, checkpoint hashes, manifest hash, and runtime identity;
7. decide whether the supplied-table V80 draft can become authoritative or whether the V81 replication table must replace it transparently;
8. update handoff and push compact evidence only.

The V81 identity and reconciliation audit is complete. Material differences from the supplied V77/V80 rows prevent silent manuscript replacement. V78 remains authoritative until an explicit task selects either the checkpoint-backed V81 replication table or the supplied-table V80 evidence with its identity limitation.

## Estimated runtime

Historical RTX 3090 runs indicate approximately 5.7-7.0 hours per 50-epoch model. Nine serial runs are expected to require about 50-63 hours, plus final evaluation.

## Commit message

`results: archive V81 single-modality retraining evaluation`
