# Current Task

## Title

V41 paired seed1 completion on the frozen V40 component-disjoint development-validation protocol.

## Goal

Run **only** the paired seed1 comparison under the frozen V40 protocol:

- `matched_early` with modality dropout `0.00`;
- `reliability_p015` with modality dropout `0.15`.

First check whether a complete, auditable local seed1 pair can be reused exactly. Reuse is allowed only when both seed1 models satisfy every provenance requirement below. Otherwise train exactly these two seed1 models, serially, then evaluate both only on the frozen V40 development-validation split.

Do not run any other seed, p value, ablation, modality baseline, guard/test audit, synthetic channel-removal experiment, COCO evaluator, degradation experiment, efficiency profile, gate analysis, manuscript update, or release task.

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

- Baseline evidence commit: `b37db7025413dd80016ac5d23f63e8e1737472e6`.
- Dataset root: `D:\download\triair`.
- Train manifest:
  `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt`
  - SHA256: `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f`
- Development-validation manifest:
  `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt`
  - SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`
- Guard is archival/non-test and is strictly out of scope. Do not read, inspect, audit, evaluate, copy, or include any guard sample in this task.
- Frozen evaluator: `rarepdet/eval_map.py`
  - SHA256: `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715`
- Frozen project-local metrics: `rarepdet/metrics.py`
  - SHA256: `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081`
- Frozen training setup:
  - seed: `1`
  - epochs: `50`
  - image size: `640`
  - batch size: `4`
  - learning rate: `1e-4`
  - workers: `0`
  - optimizer: AdamW as implemented by the existing frozen training runner
  - device: one CUDA GPU only
  - checkpoint rule: choose `best.pt` solely by highest V40 development-validation AP50
- Model settings:
  - early: `--model early --modality-dropout 0.00`
  - reliability: `--model reliability --modality-dropout 0.15`
- Standardized evaluation convention:
  - detector-output candidate threshold: `0.001`
  - P/R/F1 threshold: `0.50`
  - NMS threshold: `0.6`
  - maximum detections/image: `100`
  - AP50/AP75 are project-local single-class metrics, not COCO AP50:95

## Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `docs/V41_*`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/v41_q1_upgrade/seed1/**`
- `reproducibility/v41_q1_upgrade/seed1/**`
- New V41-only audit/reporting scripts under `rarepdet/tools/v41_seed1_*`

## Forbidden Files To Modify

- Any existing V40/V39 directories, manifests, reports, source locks, logs, checkpoints, or evidence packages.
- `rarepdet/train_early_fusion.py`
- `rarepdet/eval_map.py`
- `rarepdet/metrics.py`
- `rarepdet/data.py`
- `datasets/triair_dataset.py`
- `rarepdet/models/early_fusion_fcos.py`
- `rarepdet/models/repvit_fpn_backbone.py`
- `requirements.txt`, environment lock files, default configuration files, manuscript files, or release files.
- Raw data, labels, `.npy` arrays, checkpoints, prediction caches, or large images.
- Any path under or referring to the guard partition.

## Required Commands

### 1. Verify the frozen contract before reuse or training

Create a V41-only verifier and run:

```powershell
python rarepdet/tools/v41_seed1_verify_contract.py --repo . --source-lock reproducibility/v40_post_core_evidence_v1/source_lock/source_lock_manifest.md --train-manifest reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-manifest reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --out runs/v41_q1_upgrade/seed1/contract
```

The report must record manifest hashes, hashes of the frozen evaluator/metrics/data adapter/model builders/training runner, Python/package versions, GPU information, and pass/fail status. It must fail closed. Any mismatch blocks the task.

### 2. Audit whether an existing seed1 pair is reusable

Create a V41-only audit tool and run:

```powershell
python rarepdet/tools/v41_seed1_reuse_audit.py --repo . --workspace E:\RepViT-main --train-manifest reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-manifest reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --out runs/v41_q1_upgrade/seed1/reuse_audit
```

Search local workspace and preserved local handoff locations for both:

- a `matched_early` seed1 `best.pt`;
- a `reliability_p015` seed1 `best.pt`.

Set `reuse_verdict=ELIGIBLE_PAIRED_SEED1_REUSE` only if both candidates meet every condition:

1. Both checkpoint files exist and their SHA256 hashes are recorded.
2. Both have intact training logs and full configuration snapshots.
3. Both use the exact frozen train/validation manifest hashes.
4. Both match the required frozen source/evaluator hashes.
5. Both use seed1, 50 epochs, 640 input, batch size 4, LR `1e-4`, workers 0, and frozen optimizer behavior.
6. Early uses dropout `0.00`; reliability uses dropout `0.15`.
7. Both choose `best.pt` solely by V40 development-validation AP50.
8. Both can be re-evaluated with the frozen evaluator without checkpoint modification.
9. The pair was not selected post hoc because of performance.

If any condition is not fully verified, set `reuse_verdict=NOT_ELIGIBLE_FOR_REUSE`; do not use either candidate in results, and run both fresh seed1 trainings below. Never create a hybrid pair with one reused and one newly trained checkpoint.

### 3. Fresh training only when reuse is not eligible

Run serially, one GPU process at a time:

```powershell
python rarepdet/train_early_fusion.py --model early --data D:\download\triair --train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.00 --seed 1 --out runs/v41_q1_upgrade/seed1/matched_early_seed1
```

```powershell
python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.15 --seed 1 --out runs/v41_q1_upgrade/seed1/reliability_p015_seed1
```

Do not change any parameter after seeing the first run. Do not run retries with changed settings. Do not start seeds3/4.

### 4. Frozen standardized development-validation evaluation

For the verified reused pair or the fresh pair:

1. Recover the exact V40 standardized evaluation command from V40 run metadata and save it verbatim in `runs/v41_q1_upgrade/seed1/frozen_evaluation_command.md`.
2. Verify the command preserves the frozen candidate threshold, P/R/F1 threshold, NMS, and maximum-detection convention.
3. Evaluate each seed1 checkpoint once on the V40 development-validation manifest.
4. Do not evaluate guard samples or any candidate test split.
5. Do not run channel removal, COCO, degradation, efficiency, qualitative, or gate analyses.

## Required Outputs

- `runs/v41_q1_upgrade/seed1/contract/contract_verification.md`
- `runs/v41_q1_upgrade/seed1/contract/contract_verification.json`
- `runs/v41_q1_upgrade/seed1/reuse_audit/seed1_reuse_audit.md`
- `runs/v41_q1_upgrade/seed1/reuse_audit/seed1_reuse_audit.json`
- `runs/v41_q1_upgrade/seed1/frozen_evaluation_command.md`
- `runs/v41_q1_upgrade/seed1/seed1_per_run_summary.csv`
- `runs/v41_q1_upgrade/seed1/seed1_per_run_summary.md`
- `runs/v41_q1_upgrade/seed1/seed1_pair_comparison.md`
- `runs/v41_q1_upgrade/seed1/source_lock_seed1.md`
- `runs/v41_q1_upgrade/seed1/source_lock_seed1.json`
- Updated `docs/EXPERIMENT_STATUS.md`
- Updated `runs/handoff_latest.md`
- Updated `runs/handoff_latest.json`

Do not commit checkpoints. Reports must include both seed1 rows, checkpoint hashes, exact commands, manifest hashes, source hashes, Precision, Recall, F1, AP50, AP75, and paired reliability-minus-early differences.

A combined seed0/1/2 table is permitted only as `three-seed interim development-validation summary`. It must not be called a final stability result, statistical-significance result, independent-test result, or manuscript-final aggregate.

## Acceptance Criteria

- Contract verification passes before reuse or training.
- Exactly one complete paired seed1 result exists: both verified reuse or both fresh training.
- No hybrid reuse/fresh pair is used.
- Fresh training, if needed, uses only the frozen settings and runs serially.
- Both checkpoints are selected only by V40 development-validation AP50.
- Both evaluations use only the frozen development-validation manifest and standardized convention.
- No guard access/evaluation and no out-of-scope experiment occurs.
- All lightweight reports and hashes are committed; no raw data or checkpoint is committed.

## Commit Message

`v41: add paired seed1 development validation evidence`

## Completion / Blocker Rule

On completion, update `docs/EXPERIMENT_STATUS.md`, `runs/handoff_latest.md`, and `runs/handoff_latest.json`, commit, and push.

If contract verification fails, a candidate cannot be verified, fresh training cannot start, a required configuration/log/checkpoint is missing, or protocol ambiguity occurs, write `docs/TASK_BLOCKER.md` with the exact command, timestamp, paths, observed hashes, and minimal action needed. Commit and push the blocker state. Do not start any other seed or later V41 stage.