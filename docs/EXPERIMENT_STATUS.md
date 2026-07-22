# Experiment Status

Updated: 2026-07-22

## Active task

`V67_MMUAV_TWO_SEED_RELIABILITY_SOFTPLUS_BENCHMARK_AUTHORIZED`

## V66 completion evidence

V66 completed with `V66_SEED1_FULLTRAIN_COMPLETE_NONZERO_AP` at commit `70a54d92b8deb8cb9a0f748230731cddad641d9f`.

Seed-1 equal-fusion Softplus metrics were AP@[0.50:0.95] `0.0030357792`, AP50 `0.0174066630`, AP75 `0.0003960396`, AR@1 `0.0109337780`, AR@10 `0.0180323964`, and AR@100 `0.0195569319`.

Across V65 seed 0 and V66 seed 1, equal-fusion AP mean/sample standard deviation were `0.0196700860 / 0.0235244622`; the absolute seed difference was `0.0332686135`. This substantial initialization sensitivity requires any reliability-fusion comparison to use both matched seeds.

Both baseline runs completed all 7,187 ordered steps, remained `GEOMETRY_AND_GRADIENT_PRESERVED` at every audit, evaluated only their final checkpoints once on all 1,845 devval rows, and passed all frozen safety tests without tuning or selection.

## V67 authorized benchmark

Run exactly, in order:

1. `v67_seed0_reliability_softplus_b1_t20_fulltrain` — 7,187 steps and one final full-devval evaluation;
2. `v67_seed1_reliability_softplus_b1_t20_fulltrain` — 7,187 steps and one final full-devval evaluation.

Use the exact V65/V66 seed-specific initialization states, data, order, alignment, detector, Softplus activation, optimizer, audits, recovery policy, and evaluator. The sole method difference is activation of the existing V57 shared image-conditioned reliability scorer. No modality dropout or auxiliary fusion change is authorized.

V67 ceiling: **14,374 optimizer steps**, **80 diagnostic backward calls**, **38 expected verified recovery snapshots**, and **two final-checkpoint-only 1,845-row devval evaluations**.

## Intended evidence

V67 will produce a matched two-seed devval comparison of equal fusion versus reliability fusion, including per-seed AP/AR deltas and fusion-weight diagnostics. Results remain descriptive: n=2, no independent test set, no threshold/checkpoint selection, no tuning, and no automatic manuscript claim.
