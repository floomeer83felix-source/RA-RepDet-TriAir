# Task Blocker

Status: `V56_AUTHORIZED_NO_ACTIVE_PREFLIGHT_BLOCKER`

Generated: 2026-07-16

## Current state

V55 completed the exact frozen seed-0 paired comparison with positive on-minus-off deltas for AP50:95, AP50, AP75, and AR100. Source locks, common initialization, sample order, training, evaluation, heavy-artifact exclusion, tests, and protected-file checks passed.

The user has now authorized V56 to add exactly two paired seeds, 1 and 2, while preserving seed 0 as immutable historical evidence. No active engineering blocker remains before reproducing the frozen source and V55 evidence contracts.

## Authorized boundary

V56 may:

- reproduce frozen data counts/hashes and committed V55 seed-0 hashes/metrics;
- generate one seed-specific common initialization and sample order for each of seeds 1 and 2;
- train `alignment_off_equal` and `alignment_on_equal` once per new seed;
- complete exactly 7,187 optimizer steps per run, with a 28,748-step V56 ceiling;
- evaluate each of the four final checkpoints exactly once on all 1,845 devval rows;
- aggregate frozen seed 0 with seeds 1 and 2 using descriptive three-seed paired summaries;
- commit only compact source locks, hashes, logs, metrics, tests, metadata, and summaries.

V56 may not:

- retrain or reevaluate seed 0;
- alter paired settings beyond `alignment_enabled`;
- optimize on devval;
- use trained V54/V55 checkpoints as initialization;
- run seeds outside 1 and 2, extra runs, sweeps, tuning, early stopping, checkpoint selection, RA/reliability-fusion training, or more than 28,748 new optimizer steps;
- modify production TriAir defaults, V40-V55 historical evidence, V51 history, raw data, annotations, manuscript files, or public-release materials;
- publish or redistribute MM-UAV data, derivatives, predictions, or checkpoints.

## Fail-closed blockers

Stop with the matching V56 blocked state on:

1. source count/hash or committed V55 evidence mismatch;
2. seed-specific common-initialization or sample-order mismatch;
3. paired configuration asymmetry beyond alignment enabled;
4. OOM or non-finite training, alignment, prediction, or metric values;
5. incomplete paired training or evaluation;
6. devval optimization leakage, seed-0 execution, or step-limit violation;
7. protected-file changes or heavy artifacts entering Git.

Do not automatically change the frozen configuration after observing behavior.

## Next action

Execute V56 exactly as written in `docs/NEXT_TASK.md`. A completed task must report all three seeds and descriptive paired deltas without claiming statistical significance, manuscript readiness, or authorization for further experiments.