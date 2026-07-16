# Task Blocker

Status: `V57_PAIRED_FUSION_ABLATION_AUTHORIZED_NO_ACTIVE_PREFLIGHT_BLOCKER`

Generated: 2026-07-16

## Current state

V56 completed the three-seed alignment confirmation with AP50:95 direction positive for 3/3 seeds. The user has now authorized V57 to keep learned alignment enabled and compare fixed equal fusion against learned reliability-aware fusion under one frozen seed-0 paired protocol.

No active engineering blocker remains before V57 source-lock, V56-evidence, superset-initialization, and shared-order checks.

## Authorized boundary

V57 may:

- reproduce the frozen manifests, hashes, and committed V56 evidence;
- create a V57-only superset model with identical parameter names/shapes in both variants;
- zero-initialize the reliability scorer final layer for exact uniform starting weights;
- train `alignment_on_equal_superset` and `alignment_on_reliability_superset` for exactly 7,187 steps each;
- use one common initialization and one identical deterministic sample order;
- complete at most 14,374 optimizer steps total;
- evaluate each final checkpoint exactly once on all 1,845 devval rows;
- record detection metrics, signed fusion deltas, fusion-weight diagnostics, alignment diagnostics, timing, memory, and finite-value evidence;
- commit compact logs, metadata, hashes, tests, and summaries only.

V57 may not:

- disable alignment in either variant;
- change any paired factor beyond whether reliability weights are bypassed or used;
- initialize from trained V54-V56 checkpoints;
- optimize on devval;
- run extra seeds, extra primary runs, sweeps, tuning, early stopping, checkpoint selection, or more than 14,374 total steps;
- modify production TriAir defaults, historical evidence, V51 history, manuscript files, raw data, or annotations;
- publish or redistribute MM-UAV data, derivatives, predictions, or checkpoints.

## Fail-closed blockers

Stop with the matching V57 blocked state on:

1. manifest, V56 evidence, common initialization, parameter-shape, or shared-order mismatch;
2. alignment disabled or paired differences beyond fusion behavior;
3. equal weights not exactly uniform or reliability weights not initially uniform;
4. OOM or non-finite training, alignment, fusion, prediction, or evaluation values;
5. invalid fusion weights or normalization failure;
6. incomplete paired training, devval optimization leakage, evaluator mismatch, or step-limit violation;
7. protected-file or heavy-artifact Git violation.

Do not automatically change the frozen configuration after observing behavior.

## Next action

Execute V57 exactly as written in `docs/NEXT_TASK.md`. A completed pair must report `reliability - equal` metric deltas and fusion-weight behavior as single-seed preliminary internal evidence only. Multi-seed fusion confirmation requires a separate future authorization.
