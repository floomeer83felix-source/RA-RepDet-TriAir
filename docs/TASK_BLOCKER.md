# Task Blocker

Status: `V51_AWAITING_GPU_AUTHORIZATION`

Generated: 2026-07-13T21:13:45+08:00

## Exact blocker

The non-GPU V51 recovery audit, Route-B decision, three immutable group-disjoint folds, evaluator, queue, reports, and source lock are complete. The next command starts a large GPU experiment, and the user requested an explicit decision before GPU work.

The source-locked full design requires:

- 9 fresh RGB trainings: 3 folds x seeds 0, 1, and 2;
- 50 epochs per run at RGB 640, batch 4;
- 18 frozen TriAir-checkpoint fold evaluations after baseline training;
- no resume from the interrupted V50 run.

## Time estimate

- V50 observed training throughput: 1,618 iterations in approximately 409 seconds (`0.253 s/iteration`).
- V51 fold training size: approximately 1,420-1,455 iterations per epoch.
- V50 frozen-checkpoint inference throughput: approximately 22 images/second.
- Expected full-design wall time on the RTX 3090: 65-75 hours, including per-epoch fold validation and final evaluations.

## Validation completed

- V50 immutable/source-lock checks: all match.
- V51 source-lock hashes: 29/29 match.
- V51 tests: 4/4 pass.
- Fold validation sizes: 2,868 / 2,952 / 2,809 images.
- No group leakage and no GPU process started.

## Decision options

1. Authorize the full frozen design: 9 training runs, estimated 65-75 hours. This preserves the current source lock and strongest Route-B evidence.
2. Authorize a reduced design: one seed per fold (seeds 0/1/2 assigned across the three folds), estimated 22-26 hours. This requires a pre-training source-lock amendment and yields weaker evidence without within-fold seed replication.

No training will start until one option is explicitly authorized.

## Related files

- `runs/v51_visdrone_recovery/recovery_audit.md`
- `runs/v51_visdrone_recovery/route_decision.md`
- `runs/v51_visdrone_recovery/fold_integrity.md`
- `runs/v51_visdrone_recovery/source_lock_v51.md`
- `runs/v51_visdrone_recovery/cv_run_status.json`
- `runs/v50_visdrone_seen/protocol_violation_evidence.json`
