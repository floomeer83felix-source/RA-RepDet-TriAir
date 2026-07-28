# Experiment Status

Updated: 2026-07-29

## Active status

`V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE`

V73 completed all nine authorized `640 x 640` supervised MM-UAV runs: three methods, seeds 0/1/2,
ten epochs and 71,870 optimizer steps per run. Total completed optimizer steps: `646,830`.
Each final checkpoint was evaluated exactly once on all 1,845 exposed devval rows.

## Three-seed descriptive results

- `scratch_equal`: AP 0.223433 +/- 0.007330; AP50 0.556932; AR100 0.351286.
- `triair_init_equal`: AP 0.217787 +/- 0.002016; AP50 0.552603; AR100 0.343656.
- `triair_init_reliability`: AP 0.215106 +/- 0.009007; AP50 0.545131; AR100 0.342155.

See `runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/three_seed_summary.json`
for all AP/AR statistics and paired differences.

## Scientific boundary

This is `MM-UAV supervised cross-dataset transfer benchmark with learned feature alignment`. It is not zero-shot, independent/blind
external validation, official untouched-test performance, or evidence of generalization without
MM-UAV labels. The three-seed comparisons are descriptive.
