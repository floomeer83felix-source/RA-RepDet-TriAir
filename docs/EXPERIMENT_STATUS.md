# Experiment Status

Updated: 2026-07-22

## Active task

`V66_COMPLETE_NO_FURTHER_GPU_STAGE_AUTHORIZED`

## V66 result

V66 completed with the preregistered outcome:

`V66_SEED1_FULLTRAIN_COMPLETE_NONZERO_AP`

The exact frozen V64 seed-1 equal-fusion Softplus initialization completed all 7,187 optimizer steps and one final-checkpoint-only evaluation on all 1,845 devval rows.

Seed-1 metrics were AP@[0.50:0.95] `0.0030357792`, AP50 `0.0174066630`, AP75 `0.0003960396`, AR@1 `0.0109337780`, AR@10 `0.0180323964`, and AR@100 `0.0195569319`.

## Two-seed baseline

Across V65 seed-0 and V66 seed-1, AP@[0.50:0.95] mean/sample standard deviation/minimum/maximum/absolute difference were `0.0196700860 / 0.0235244622 / 0.0030357792 / 0.0363043928 / 0.0332686135`.

The large seed difference documents substantial initialization sensitivity under the frozen equal-fusion Softplus protocol. This descriptive result did not trigger selection, tuning, or a rerun.

## Geometry and safety

- All ten V66 audits were `GEOMETRY_AND_GRADIENT_PRESERVED`.
- Final compact train/devval geometry was `272,000 / 272,000` valid boxes on each subset.
- Optimizer steps/unique rows: `7,187 / 7,187`.
- Diagnostic backward calls: `40 / 40`.
- Verified recovery snapshots: `19 / 19`; recovery events: `0`.
- Full-devval evaluation attempts/rows: `1 / 1,845`.
- Post-run tests: `10 / 10` passed.
- No tuning, threshold selection, checkpoint selection, extra seed/variant, rerun, or extension occurred.

## Claim boundary

V65 and V66 establish only a two-seed equal-fusion Softplus baseline on frozen MM-UAV devval. They do not establish superiority, independent-test performance, or a reliability-fusion contribution. No further GPU experiment is currently authorized.
