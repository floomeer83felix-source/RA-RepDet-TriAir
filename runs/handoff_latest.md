# RA-RepDet-TriAir Handoff

Generated: 2026-07-09

## Current Task State

- Task file: `docs/NEXT_TASK.md`
- User-explicit task: V42 locked held-out guard evaluation
- Status: `V42_LOCKED_HELDOUT_GUARD_EVALUATION_COMPLETE`
- Active blocker: `NO_ACTIVE_BLOCKER`

`docs/NEXT_TASK.md` still describes the prior V41 manuscript task. The latest user instruction explicitly changed the active scope to V42 guard evaluation, and this handoff records that executed scope.

## What Assistant/Codex Completed

Completed six fixed-checkpoint evaluations on the frozen V40 component-disjoint guard manifest:

- `matched_early_seed0`
- `matched_early_seed1`
- `matched_early_seed2`
- `reliability_p015_seed0`
- `reliability_p015_seed1`
- `reliability_p015_seed2`

No training, tuning, checkpoint selection, split modification, robustness, profiling, manuscript work, DroneVehicle work, or `finish_task.ps1` was performed.

## Outputs

- `runs/v42_locked_guard_heldout/heldout_guard_source_lock.md`
- `runs/v42_locked_guard_heldout/heldout_guard_source_lock.json`
- `runs/v42_locked_guard_heldout/heldout_guard_summary.md`
- `runs/v42_locked_guard_heldout/heldout_guard_summary.json`
- `runs/v42_locked_guard_heldout/heldout_guard_per_run_summary.csv`
- `runs/v42_locked_guard_heldout/heldout_guard_paired_deltas.csv`
- `runs/v42_locked_guard_heldout/heldout_guard_paired_delta_aggregates.csv`
- `runs/v42_locked_guard_heldout/heldout_guard_claim_boundary.md`
- Per-run standardized guard eval outputs under `runs/v42_locked_guard_heldout/<run>/standardized_guard_eval/`.
- Report generator: `rarepdet/tools/build_v42_guard_summary.py`.

## Guard Source Lock

- Source manifest: `runs/component_disjoint_v40/guard.txt`
- Rows: 837 images
- GT boxes: 1264
- Normalized LF SHA256: `9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e`
- Raw file SHA256: `0cf3270c0a73d03caf8d698bb4e9ddb0adba46e688c52d8589f57ea12488881f`
- Evaluator: `rarepdet/eval_map.py` SHA256 `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715`
- Metrics helper: `rarepdet/metrics.py` SHA256 `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081`

The archival guard at `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_guard_unchanged_archival.txt` has a different normalized hash and was not used.

## Held-out Guard Per-run Results

| Run | Precision | Recall | F1 | AP50 | AP75 |
| --- | ---: | ---: | ---: | ---: | ---: |
| matched_early_seed0 | 0.938534 | 0.942247 | 0.940387 | 0.965299 | 0.923818 |
| matched_early_seed1 | 0.878990 | 0.936709 | 0.906932 | 0.954007 | 0.894974 |
| matched_early_seed2 | 0.937147 | 0.920095 | 0.928543 | 0.957160 | 0.883246 |
| reliability_p015_seed0 | 0.937451 | 0.936709 | 0.937080 | 0.966926 | 0.929140 |
| reliability_p015_seed1 | 0.894619 | 0.946994 | 0.920061 | 0.964380 | 0.912660 |
| reliability_p015_seed2 | 0.932243 | 0.946994 | 0.939560 | 0.970845 | 0.866755 |

## Three-seed Held-out Guard Paired Deltas

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.003213 | 0.010920 | 3 |
| Recall | +0.010549 | 0.016220 | 3 |
| F1 | +0.006946 | 0.008943 | 3 |
| AP50 | +0.008562 | 0.006229 | 3 |
| AP75 | +0.002173 | 0.017305 | 3 |

## Claim Boundary

Allowed wording: locked held-out guard evaluation on the frozen V40 component-disjoint guard manifest, with descriptive three-seed paired comparisons between matched early fusion and reliability-aware `p=0.15`.

Disallowed wording: external dataset generalization, independent public benchmark test, training-time model selection or tuning using guard results, statistical significance, optimal dropout, calibrated physical sensor reliability, real sensor-fault robustness, or COCO AP@[0.50:0.95].

## What Remains Out Of Scope

- p=0.00 or p=0.20 runs.
- Any new training or checkpoint selection.
- Robustness, profiling, qualitative, bootstrap, or external-data work.
- SIVP manuscript update from the new guard evidence.
- DroneVehicle work.
