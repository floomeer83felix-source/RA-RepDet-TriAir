# Experiment Status

Updated: 2026-07-22

## Active task

`V66_MMUAV_SEED1_SOFTPLUS_FULLTRAIN_CONFIRMATION_AUTHORIZED`

## User authorization

The user reported that V65 completed and was pushed. Under the standing automatic task-handoff workflow, V66 is authorized as the next bounded stage: one seed-1 equal-fusion Softplus full-training confirmation using the exact V65 protocol.

## V65 prerequisite evidence

- Completion commit: `33609052b798a89fb8d3a1ab9351f8497e8f95d1`.
- Outcome: `V65_FULLTRAIN_COMPLETE_NONZERO_AP`.
- Full training: `7,187 / 7,187` optimizer steps and unique ordered rows.
- Full-devval evaluation: exactly one attempt on all `1,845` rows.
- AP@[0.50:0.95]: `0.0363043928`.
- AP50: `0.1493416683`.
- AP75: `0.0035733839`.
- AR@1 / AR@10 / AR@100: `0.0501429252 / 0.0753692234 / 0.0815388280`.
- All ten audits were `GEOMETRY_AND_GRADIENT_PRESERVED`.
- Diagnostic backward calls: `40 / 40`.
- Verified recovery snapshots: `19`; recovery events: `0`.
- Post-run tests: `10 / 10` passed.

## V66 authorized run

Run exactly one variant:

`v66_seed1_equal_softplus_b1_t20_fulltrain`

Use the exact frozen V64 seed-1 initialization SHA256 `50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476`, the same complete 7,187-row order, equal fusion, enabled alignment, dormant reliability scorer, exact Softplus activation, optimizer, audit schedule, recovery policy, and final-checkpoint-only evaluator used by V65.

Train exactly 7,187 steps and evaluate the final checkpoint exactly once on all 1,845 frozen devval rows. Produce the complete AP/AR metrics and a descriptive two-seed equal-fusion summary combining immutable V65 seed-0 results with V66 seed-1 results.

## Safety and claim boundary

- No initialization from a trained checkpoint.
- No ReLU full training or reliability-fusion training.
- No tuning, threshold selection, checkpoint selection, extra seed/variant, rerun, or automatic extension.
- No full-devval access before the final checkpoint.
- Production TriAir behavior, V40-V65 evidence, V51, manuscript, and submission files remain protected.
- Heavy artifacts remain local and outside Git.

A completed V66 run may establish a two-seed equal-fusion Softplus devval baseline. It does not establish superiority, an independent-test result, or a reliability-fusion contribution.
