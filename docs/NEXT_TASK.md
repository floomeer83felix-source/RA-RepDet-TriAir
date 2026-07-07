# Current Task

## Title

Fresh paired seed1 training and V40 development-validation evaluation.

## Goal

Run exactly two **fresh** seed1 trainings on the frozen V40 component-disjoint train/development-validation split:

1. matched early fusion with modality dropout `0.00`;
2. reliability-aware fusion with modality dropout `0.15`.

Do not search for, inspect, reuse, compare against, or aggregate any pre-existing seed1 artifact. Both seed1 checkpoints must be newly trained in this task.

## Read First

1. `AGENTS.md`
2. `PROJECT_PROFILE.md`
3. `docs/PROJECT_CONTEXT.md`
4. `docs/V40_PUBLICATION_SNAPSHOT.md`
5. `docs/REPRODUCIBILITY.md`
6. `reproducibility/v40_post_core_evidence_v1/source_lock/source_lock_manifest.md`
7. `runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json`
8. `runs/handoff_latest.md`

## Frozen Assets

- Dataset root: `D:\download\triair`.
- V40 evidence-package commit: `b37db7025413dd80016ac5d23f63e8e1737472e6`.
- Train manifest: `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt`.
  - Required SHA256: `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f`
- Development-validation manifest: `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt`.
  - Required SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`
- Guard is archival/non-test and is out of scope. Do not read, inspect, audit, evaluate, copy, or include guard samples.
- Frozen evaluator: `rarepdet/eval_map.py`.
  - Required SHA256: `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715`
- Frozen metrics: `rarepdet/metrics.py`.
  - Required SHA256: `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081`
- Fixed run settings: seed `1`; 50 epochs; image size 640; batch size 4; learning rate `1e-4`; workers 0; AdamW as implemented by the existing runner; one CUDA GPU only.
- Checkpoint rule: retain `best.pt` solely by highest V40 development-validation AP50.
- Standardized evaluation: candidate threshold `0.001`; P/R/F1 threshold `0.50`; NMS `0.6`; maximum detections/image `100`; project-local AP50/AP75 rather than COCO metrics.

## Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `docs/V41_*`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/v41_q1_upgrade/seed1/**`
- `reproducibility/v41_q1_upgrade/seed1/**`
- New verification/reporting scripts only under `rarepdet/tools/v41_seed1_*`

## Forbidden Files To Modify

- Any existing V40/V39 results, reports, manifests, source locks, logs, checkpoints, or evidence packages.
- `rarepdet/train_early_fusion.py`, `rarepdet/eval_map.py`, `rarepdet/metrics.py`, `rarepdet/data.py`, `datasets/triair_dataset.py`, `rarepdet/models/early_fusion_fcos.py`, or `rarepdet/models/repvit_fpn_backbone.py`.
- Requirements, environment locks, default configuration files, manuscript files, or release files.
- Raw data, labels, `.npy` arrays, checkpoints, prediction caches, large images, and every guard-partition path.

## Required Commands

### 1. Verify frozen assets before training

Create a V41-only verifier and run:

```powershell
python rarepdet/tools/v41_seed1_verify_contract.py --repo . --source-lock reproducibility/v40_post_core_evidence_v1/source_lock/source_lock_manifest.md --train-manifest reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-manifest reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --out runs/v41_q1_upgrade/seed1/contract
```

The verifier must record train/validation manifest hashes, hashes for frozen evaluator/metrics/data adapter/model builders/training runner, Python and package versions, GPU information, and pass/fail. It must fail closed. Any required mismatch blocks this task.

### 2. Train the fresh paired seed1 runs serially

Run exactly one GPU job at a time, in the following order:

```powershell
python rarepdet/train_early_fusion.py --model early --data D:\download\triair --train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.00 --seed 1 --out runs/v41_q1_upgrade/seed1/matched_early_seed1
```

```powershell
python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.15 --seed 1 --out runs/v41_q1_upgrade/seed1/reliability_p015_seed1
```

Do not change parameters after observing either run. Do not retry with altered settings. Do not run any other seed or model.

### 3. Frozen standardized evaluation on development validation only

1. Recover the exact V40 standardized evaluation command from V40 run metadata and save it verbatim to `runs/v41_q1_upgrade/seed1/frozen_evaluation_command.md`.
2. Verify it retains the frozen candidate threshold, P/R/F1 threshold, NMS, and maximum-detection convention.
3. Evaluate each fresh seed1 checkpoint once on the V40 development-validation manifest.
4. Do not evaluate guard samples, test candidates, or any other partition.
5. Do not run channel removal, COCO, degradation, efficiency, qualitative, gate, or aggregate analyses.

## Required Outputs

- `runs/v41_q1_upgrade/seed1/contract/contract_verification.md`
- `runs/v41_q1_upgrade/seed1/contract/contract_verification.json`
- `runs/v41_q1_upgrade/seed1/frozen_evaluation_command.md`
- `runs/v41_q1_upgrade/seed1/seed1_per_run_summary.csv`
- `runs/v41_q1_upgrade/seed1/seed1_per_run_summary.md`
- `runs/v41_q1_upgrade/seed1/seed1_pair_comparison.md`
- `runs/v41_q1_upgrade/seed1/source_lock_seed1.md`
- `runs/v41_q1_upgrade/seed1/source_lock_seed1.json`
- Updated `docs/EXPERIMENT_STATUS.md`
- Updated `runs/handoff_latest.md`
- Updated `runs/handoff_latest.json`

Reports must include both fresh seed1 rows, checkpoint SHA256 values, exact commands, manifest/source hashes, Precision, Recall, F1, AP50, AP75, and the paired reliability-minus-early differences.

A seed0/1/2 combined table is permitted only as `three-seed interim development-validation summary`. It must not be called a final stability, statistical-significance, independent-test, or manuscript-final result.

## Acceptance Criteria

- Contract verification passes before training.
- Exactly two fresh seed1 runs are completed: one early and one reliability p=0.15.
- Both use the frozen settings and execute serially.
- Both best checkpoints are selected only by V40 development-validation AP50.
- Both evaluations use only the frozen development-validation manifest and frozen standardized convention.
- No pre-existing seed1 artifact is reused.
- No guard access/evaluation or out-of-scope experiment occurs.
- Lightweight reports and hashes are committed; no raw data or checkpoints are committed.

## Commit Message

`v41: add fresh paired seed1 development validation evidence`

## Completion / Blocker Rule

On completion, update `docs/EXPERIMENT_STATUS.md`, `runs/handoff_latest.md`, and `runs/handoff_latest.json`; commit and push.

If verification fails, the environment cannot start fresh training, a required frozen asset is missing, or a protocol ambiguity occurs, write `docs/TASK_BLOCKER.md` with command, timestamp, paths, hashes, and the minimal action needed. Commit and push the blocker state. Do not start another seed or any later V41 stage.