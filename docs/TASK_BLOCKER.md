# Task Blocker

Status: `V62_CLEAN_BBOX_BIAS_PAIRED_RERUN_AUTHORIZED_NO_ACTIVE_PREFLIGHT_BLOCKER`

Generated: 2026-07-20

## Current state

V61 remains closed as `V61_BLOCKED_TRAINING_OR_TRACE_INCOMPLETE`. Its exact failure was a trace-only implementation defect: the step-500 frozen devval geometry path reused the train-only optimization target mover and rejected `devval:00005919`. The control consumed 500 optimizer steps, the intervention consumed 0, and no exact recovery snapshot exists.

The user selected blocker repair option 2: preserve V61 as blocked diagnostic evidence and create a separately numbered clean V62 paired pilot with a corrected trace path and a newly frozen 500+500 budget.

No active engineering blocker remains before V62 CPU source-lock, trace-fix, actual-devval-row, recovery-snapshot, and paired-initialization tests. CUDA work may begin only after those tests pass.

## Authorized correction boundary

V62 may:

- verify and preserve all V61 blocked evidence byte-identically;
- implement a trace-specific split-agnostic mover for RGB boxes and labels;
- test that mover on the actual frozen failing row `devval:00005919`;
- retain the historical train-only optimization helper and prove that it still rejects devval rows;
- execute a bounded train/devval geometry call-chain test before CUDA;
- implement atomic local recovery snapshots that preserve model, optimizer, RNG, order, step, log, and trace-ledger state;
- reconstruct the exact historical V57 seed-0 common initialization;
- create a control and exact `+0.01` four-bias intervention pair;
- run the control and intervention in that order for exactly 500 optimizer steps each on the identical frozen 500-row prefix;
- perform the twelve frozen traces and at most 96 no-step diagnostic backward probes;
- run only the frozen 32-row devval geometry subset at step 500;
- commit compact source, tests, hashes, logs, statistics, and conclusions.

V62 may not:

- modify, resume, pool, repair, or initialize from the V61 partial run;
- weaken the global train-only optimization guard;
- alter any paired tensor beyond the four-element initial bbox-output bias;
- use a bias other than exact `+0.01`, run a sweep, or alter the intervention after start;
- activate reliability fusion, disable alignment, or change uniform equal fusion;
- replace ReLU, alter the loss, threshold, top-k, NMS, preprocessing, detector, architecture, or evaluator;
- exceed 500 steps per variant, 1,000 total optimizer steps, or 96 diagnostic backward calls;
- run full devval, AP/AR, tuning, checkpoint selection, extra variants/seeds, or automatic extensions;
- modify production TriAir defaults, V40-V61 evidence, V51, manuscript/submission files, raw data, or annotations;
- put checkpoints, optimizer states, recovery snapshots, predictions, tensors, images, feature maps, or other heavy artifacts in Git.

## Fail-closed blockers

Stop with the matching V62 blocked state on:

1. V61 evidence, data, historical order, subset, or initialization mismatch;
2. any V61 historical-file mutation;
3. failure of the actual `devval:00005919` trace-target or complete bounded geometry-call-chain tests;
4. any weakening of the optimization split guard;
5. any initial paired tensor difference beyond the exact four-element `+0.01` intervention;
6. invalid or non-round-trippable recovery state;
7. incorrect run order, repeated/substituted rows, replayed/skipped steps, or optimizer-budget violation;
8. more than 96 diagnostic backward calls, unregistered samples, or diagnostic mutation of persistent state;
9. alignment/fusion/scorer contract violation;
10. OOM or non-finite loss, gradient, parameter, alignment, geometry, or diagnostic value;
11. full-devval evaluation, AP/AR, tuning, checkpoint selection, protected-file change, or heavy-artifact Git violation.

Do not automatically change the bias, LR, optimizer, precision, batch size, resolution, activation, loss, run length, sample order, trace schedule, or recovery policy after observing behavior.

## Next action

Execute V62 exactly as written in `docs/NEXT_TASK.md`. First correct and test the trace-only target transfer and atomic recovery path. Then perform a clean 500+500 pair from the exact common initialization. Even a positive step-500 prevention result does not authorize a full 7,187-step corrected run.