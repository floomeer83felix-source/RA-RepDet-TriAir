# Current Task

## Title

V41 interim development-validation consolidation and status cleanup.

## Goal

Consolidate the completed V40 seed0/seed2 evidence and the fresh V41 seed1 evidence into one auditable **three-seed interim development-validation package** without running any new training or evaluation.

This task exists because seed3/seed4 are not planned now. It must improve repository clarity, remove stale blocker confusion, and create a clean evidence handoff for manuscript-revision planning while preserving the validation-only claim boundary.

Do **not** run any GPU job. Do **not** train seed3/seed4. Do **not** evaluate guard/test data. Do **not** run p=0.20, p=0.00, ablations, modality baselines, COCO metrics, synthetic channel removal, degradation, efficiency profiling, gate analysis, or manuscript rewriting.

## Read First

1. `AGENTS.md`
2. `PROJECT_PROFILE.md`
3. `docs/PROJECT_CONTEXT.md`
4. `docs/EXPERIMENT_STATUS.md`
5. `runs/handoff_latest.md`
6. `docs/TASK_BLOCKER.md`
7. `docs/V40_PUBLICATION_SNAPSHOT.md`
8. `docs/REPRODUCIBILITY.md`
9. `runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json`
10. `runs/v41_q1_upgrade/seed1/seed1_per_run_summary.csv`
11. `runs/v41_q1_upgrade/seed1/seed1_pair_comparison.md`
12. `runs/v41_q1_upgrade/seed1/source_lock_seed1.md`

## Frozen Assets

- V40 evidence-package commit: `b37db7025413dd80016ac5d23f63e8e1737472e6`.
- V41 fresh seed1 completion commit: `5d839ae900849919189edff4bdd364f42c043b86`.
- Train manifest SHA256: `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f`.
- Development-validation manifest SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`.
- Standardized evaluation convention: detector threshold `0.001`, P/R/F1 threshold `0.50`, NMS `0.6`, max detections/image `100`, project-local AP50/AP75.
- Available seed pairs for this consolidation only:
  - seed0: V40 `matched_early_seed0` and `reliability_p015_seed0`.
  - seed1: fresh V41 `matched_early_seed1` and `reliability_p015_seed1`.
  - seed2: V40 `matched_early_seed2` and `reliability_p015_seed2`.

## Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `docs/V41_INTERIM_DEVVAL_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/v41_q1_upgrade/interim_devval/**`
- New V41-only reporting script under `rarepdet/tools/v41_interim_*`

## Forbidden Files To Modify

- Any existing V40/V39 result directory, manifest, report, source lock, checkpoint, or evidence package.
- Existing seed1 run directories and reports under `runs/v41_q1_upgrade/seed1/**` except reading them.
- `rarepdet/train_early_fusion.py`
- `rarepdet/eval_map.py`
- `rarepdet/metrics.py`
- `rarepdet/data.py`
- `datasets/triair_dataset.py`
- `rarepdet/models/**`
- Requirements, environment locks, default configs, manuscript source, tables, figures, release files, data, labels, checkpoints, raw images, `.npy` arrays, or prediction caches.
- Any guard/test partition file or output.

## Required Commands

### 1. Verify available evidence files

Create a V41-only reporting tool and run:

```powershell
python rarepdet/tools/v41_interim_devval_consolidate.py --repo . --v40-summary runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json --seed1-summary runs/v41_q1_upgrade/seed1/seed1_per_run_summary.csv --seed1-source-lock runs/v41_q1_upgrade/seed1/source_lock_seed1.json --out runs/v41_q1_upgrade/interim_devval
```

The tool must fail closed if any required input is missing or malformed. It must read only existing report files and lightweight source-lock metadata; it must not load checkpoints, raw data, predictions, or guard/test manifests.

### 2. Build a three-seed interim development-validation table

Create:

- `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.csv`
- `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.md`
- `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.json`

The table must contain seed0, seed1, and seed2 paired rows for:

- `matched_early`
- `reliability_p015`

For each seed/model row, report Precision, Recall, F1, AP50, AP75, checkpoint SHA256 if available, source file references, and whether the row came from V40 or V41-seed1 evidence.

Also report reliability-minus-early paired deltas for every seed and descriptive mean ± sample SD across the three seed-level deltas. Label all statistics exactly as:

`three-seed interim development-validation descriptive summary`

Do not use the terms final, significant, independent test, external generalization, or manuscript-final aggregate.

### 3. Clean stale blocker state

`docs/TASK_BLOCKER.md` currently may still describe the older V40 GPU-deferred task. Replace it with a short current-state note only if no active blocker exists:

- title: `# Task Blocker`
- status: `NO_ACTIVE_BLOCKER`
- explain that the old V40 GPU-deferred blocker is historical and seed1 fresh evidence is complete.
- do not delete historical evidence files.

If an actual blocker is found while consolidating, keep `docs/TASK_BLOCKER.md` as an active blocker and stop.

### 4. Update status and handoff

Update:

- `docs/V41_INTERIM_DEVVAL_STATUS.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`

These files must state:

- seed1 fresh paired evidence is complete;
- seed0/1/2 interim development-validation evidence is consolidated;
- no seed3/seed4 are planned in the current task;
- no guard/test evaluation was run;
- no new training or evaluation was run in this consolidation task;
- remaining scientific limitations remain: validation-only, three seeds only, no independent test, no causal ablations, no COCO metrics, unresolved provider provenance, and incomplete label-quality review.

## Required Outputs

- `rarepdet/tools/v41_interim_devval_consolidate.py`
- `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.csv`
- `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.md`
- `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.json`
- `runs/v41_q1_upgrade/interim_devval/interim_claim_boundary.md`
- `docs/V41_INTERIM_DEVVAL_STATUS.md`
- Updated `docs/TASK_BLOCKER.md`
- Updated `docs/EXPERIMENT_STATUS.md`
- Updated `runs/handoff_latest.md`
- Updated `runs/handoff_latest.json`

## Acceptance Criteria

- No training or evaluation command is executed.
- No checkpoint, raw data, prediction cache, image artifact, or guard/test file is read or committed.
- Seed0/1/2 values are copied only from existing V40 and V41 seed1 report artifacts.
- The consolidated summary includes all three paired seeds and all five metrics: Precision, Recall, F1, AP50, AP75.
- Delta calculations are reproducible from the CSV/JSON outputs.
- `docs/TASK_BLOCKER.md` no longer presents the old V40 GPU-deferred state as an active blocker unless a new real blocker is discovered.
- All wording remains development-validation-only and does not claim independent testing, final manuscript proof, statistical significance, or external generalization.

## Commit Message

`v41: consolidate three-seed interim development validation evidence`

## Completion / Blocker Rule

On completion, update `docs/EXPERIMENT_STATUS.md`, `runs/handoff_latest.md`, and `runs/handoff_latest.json`; commit and push.

If any required V40 or seed1 evidence file is missing, inconsistent, malformed, or ambiguous, write `docs/TASK_BLOCKER.md` with the exact file path, observed issue, command, timestamp, and minimal action needed. Commit and push the blocker state. Do not invent missing results or start any experiment.