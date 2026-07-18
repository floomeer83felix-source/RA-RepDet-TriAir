# Task Blocker

Status: `V61_EARLY_BBOX_COLLAPSE_PREVENTION_AUTHORIZED_NO_ACTIVE_PREFLIGHT_BLOCKER`

Generated: 2026-07-18

## Current state

V60 completed successfully and excluded collapse at initialization and bbox-initialization changes caused by construction-order RNG consumption. It established that both final V57 variants have all-degenerate geometry and zero bbox output-layer gradients on the frozen probes, while the historical logs lack enough instrumentation to determine the exact first-collapse step.

No active engineering blocker remains before the V61 source-lock, paired-initialization, historical-order, dense-trace, and bounded 500-step CUDA pilot.

## Authorized pilot boundary

V61 may:

- reproduce the committed V60 evidence and all frozen data/order/subset/initialization hashes;
- reconstruct the exact V57 seed-0 common superset initial state;
- create two in-memory paired copies that differ only in the four-element final bbox-regression output bias;
- leave the control bias unchanged and set the intervention bias once to exact `+0.01`;
- train the control and intervention in that order for exactly 500 optimizer steps each on the identical first 500 historical V57 rows;
- keep alignment enabled, equal fusion uniform, and the reliability scorer dormant in both runs;
- perform dense trace instrumentation at the twelve pre-registered trace states;
- perform at most 96 no-step backward probes on fresh ephemeral copies using only the frozen four-row subset;
- run compact step-500 geometry probes on the frozen 32-row train and devval subsets;
- commit compact logs, hashes, statistics, tests, and conclusions only.

V61 may not:

- change any paired factor beyond the initial four-element bbox-output bias;
- use a bias value other than `+0.01`, run a sweep, or alter the intervention after training begins;
- activate reliability fusion, disable alignment, change equal weights, or initialize from trained checkpoints;
- replace ReLU, change loss, threshold, top-k, NMS, preprocessing, detector, architecture, or evaluator;
- exceed 500 steps per variant, 1,000 optimizer steps total, or 96 diagnostic backward calls;
- run full devval evaluation, AP/AR, tuning, extra variants/seeds, checkpoint selection, reruns, or automatic extensions;
- modify production TriAir defaults, V40-V60 evidence, V51 history, manuscript/submission files, raw data, or annotations;
- put checkpoints, optimizer states, predictions, images, feature maps, tensors, or other heavy artifacts in Git.

## Fail-closed blockers

Stop with the matching V61 blocked state on:

1. V60 evidence, manifest, historical order, subset, or initialization mismatch;
2. any initial paired tensor difference beyond the exact four-element bias intervention;
3. intervention-value drift, bias sweep, incorrect run order, repeated/substituted rows, or step-budget violation;
4. probe-state mutation, more than 96 diagnostic backward calls, or use of unregistered samples;
5. alignment/fusion/scorer contract violation;
6. OOM or non-finite loss, gradient, parameter, alignment, geometry, or diagnostic value;
7. AP/AR, full-devval evaluation, tuning, checkpoint selection, protected-file change, or heavy-artifact Git violation.

Do not automatically change the bias, LR, optimizer, precision, batch size, resolution, activation, loss, run length, sample order, or trace schedule after observing behavior.

## Next action

Execute V61 exactly as written in `docs/NEXT_TASK.md`. The task determines whether exact `+0.01` bbox-output bias initialization prevents the strict early geometry-and-gradient collapse through step 500. Even a positive result does not authorize a full corrected training run.