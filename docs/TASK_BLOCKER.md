# Task Blocker

Status: `V63_PAIRED_BBOX_ACTIVATION_RESCUE_AUTHORIZED_NO_ACTIVE_PREFLIGHT_BLOCKER`

Generated: 2026-07-20

## Current state

V62 completed successfully with `V62_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE`. Both the historical ReLU control and the exact `+0.01` initial bbox-output-bias intervention first met strict early geometry-and-gradient collapse at step 20 and ended step 500 with zero valid train and frozen-devval boxes. This excludes the frozen `+0.01` bias intervention as an effective early rescue under the V57 path.

No active engineering blocker remains before V63 CPU source-lock, paired-state, activation-location, actual-devval-row, recovery-snapshot, and bounded CUDA tests. CUDA work may begin only after all preflight gates in `docs/NEXT_TASK.md` pass.

## Authorized V63 boundary

V63 may:

- verify and preserve V62 and all earlier evidence byte-identically;
- reconstruct the exact V57 seed-0 common initialization;
- create two step-0 models whose parameters, buffers, state-dict keys, pre-activation bbox logits, fused features, classification logits, and centerness logits are bit-identical;
- retain the historical ReLU bbox-distance activation for the control;
- replace only that activation with exact `softplus(beta=1.0, threshold=20.0)` for the intervention in both training and inference paths;
- retain historical bbox-output weights and bias in both variants;
- run control then Softplus for exactly 200 optimizer steps each on the identical first 200 historical V57 rows;
- keep alignment enabled, equal fusion exactly uniform, and the reliability scorer dormant;
- perform the thirteen frozen traces and at most 104 no-step diagnostic backward probes;
- record pre/post-activation geometry, activation derivatives, losses, matching, and output/regression gradients;
- atomically save and round-trip verify local technical recovery state before every trace;
- run only the frozen 32-row devval geometry subset at step 200;
- commit compact source, tests, hashes, logs, statistics, and conclusions.

V63 may not:

- modify, repair, resume, pool, or initialize from any trained V55-V62 checkpoint;
- modify historical V40-V62 evidence or V51 history;
- change bbox bias or weights, run an activation/bias sweep, or use Softplus parameters other than exact `beta=1.0`, `threshold=20.0`;
- apply the activation in only training or only inference;
- change loss, targets, matching, anchors, scales, decode, clipping, threshold, top-k, NMS, preprocessing, detector, evaluator, alignment, fusion weights, or scorer behavior;
- exceed 200 steps per variant, 400 optimizer steps total, or 104 diagnostic backward calls;
- run full devval, AP/AR, tuning, early stopping, checkpoint selection, extra variants/seeds, reruns, or automatic extensions;
- modify production TriAir defaults, manuscript/submission files, raw data, or annotations;
- put checkpoints, optimizer states, recovery snapshots, predictions, tensors, images, feature maps, or other heavy artifacts in Git.

## Fail-closed blockers

Stop with the matching V63 blocked state on:

1. V62 evidence, manifest, historical order, subset, or initialization mismatch;
2. any historical or protected-file mutation;
3. any step-0 paired state or pre-activation/non-bbox output mismatch;
4. incorrect activation source location, parameters, call count, or train/inference asymmetry;
5. any bias, weight, loss, matcher, anchor, scale, decode, clipping, threshold, NMS, preprocessing, detector, evaluator, alignment, fusion, or scorer difference;
6. failure of the actual `devval:00005919` trace-target path or weakening of the train-only optimization guard;
7. invalid recovery snapshots, replayed/skipped optimizer steps, incorrect run order, repeated/substituted rows, or budget violation;
8. more than 104 diagnostic backward calls, unregistered samples, or diagnostic mutation of persistent state;
9. OOM or non-finite loss, gradient, parameter, activation, alignment, geometry, or recovery value;
10. full-devval evaluation, AP/AR, tuning, checkpoint selection, protected-file change, or heavy-artifact Git violation.

Do not automatically change activation parameters, bias, LR, optimizer, precision, batch size, resolution, loss, run length, sample order, trace schedule, or recovery policy after observing behavior.

## Next action

Execute V63 exactly as written in `docs/NEXT_TASK.md`. First prove that exact historical ReLU versus exact parameter-free Softplus is the only paired difference. Then run the bounded 200+200 pilot. Even a positive Softplus rescue does not authorize a full 7,187-step corrected run or AP/AR evaluation.
