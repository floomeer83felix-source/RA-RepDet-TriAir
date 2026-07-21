# Task Blocker

Status: `V64_SEED1_PAIRED_BBOX_ACTIVATION_CONFIRMATION_AUTHORIZED_NO_ACTIVE_PREFLIGHT_BLOCKER`

Generated: 2026-07-21

## Current state

V63 completed successfully with
`V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`.

The seed-0 native ReLU control first met strict early geometry-and-gradient collapse at step 15 and ended step 200 with zero valid boxes on the frozen train and devval geometry subsets. Exact parameter-free `softplus(beta=1.0, threshold=20.0)` remained geometry-and-gradient preserved at every scheduled trace and ended with all 272,000 decoded boxes valid on both frozen subsets.

No active engineering blocker remains before V64 CPU source-lock, fresh seed-1 initialization freeze, paired-state identity, activation-location, actual-devval-row, recovery-snapshot, and bounded CUDA tests. CUDA work may begin only after every preflight gate in `docs/NEXT_TASK.md` passes.

## Authorized V64 boundary

V64 may:

- verify and preserve V63 and all earlier evidence byte-identically;
- generate exactly one fresh seed-1 common initialization, save it locally, hash and round-trip verify it, then freeze it;
- create two models whose step-0 parameters, buffers, pre-activation bbox logits, non-bbox outputs, fused features, and alignment outputs are bit-identical;
- retain native historical ReLU for the control;
- replace only the shared training/inference bbox-distance activation with exact `softplus(beta=1.0, threshold=20.0)` for the intervention;
- run control then Softplus for exactly 200 optimizer steps each on the identical frozen V63 first-200 prefix;
- keep alignment enabled, equal fusion exactly uniform, and the reliability scorer dormant;
- perform the thirteen frozen traces and at most 104 no-step diagnostic backward calls;
- save and round-trip verify local technical recovery state before every trace;
- run only the frozen 32-row devval geometry subset at step 200;
- commit compact source, tests, hashes, logs, statistics, and conclusions.

V64 may not:

- regenerate or select among seed-1 initializations after observing results;
- initialize from, resume, repair, modify, pool, or relabel any trained V55-V63 checkpoint;
- modify historical V40-V63 evidence or V51 history;
- change bbox weights or bias, run a sweep, or use Softplus parameters other than exact `beta=1.0`, `threshold=20.0`;
- change loss, targets, matching, anchors, scales, clipping, decode, threshold, NMS, preprocessing, detector, evaluator, alignment, fusion, or scorer behavior;
- exceed 200 optimizer steps per variant, 400 total steps, or 104 diagnostic backward calls;
- run full devval, AP/AR, tuning, early stopping, checkpoint selection, additional seeds/variants, reruns, or automatic extensions;
- modify production TriAir defaults, manuscript/submission files, raw data, or annotations;
- put initialization artifacts, checkpoints, optimizer states, recovery snapshots, tensors, predictions, images, feature maps, or other heavy artifacts in Git.

## Fail-closed blockers

Stop with the matching V64 blocked state on:

1. V63 evidence, manifest, order, first-200 prefix, subset, source, or protected-fingerprint mismatch;
2. multiple seed-1 candidates, seed-1 regeneration after result observation, invalid serialization/reload, or paired step-0 mismatch;
3. incorrect activation source location, parameters, call count, or training/inference asymmetry;
4. any paired difference beyond the exact activation;
5. failure of actual `devval:00005919` trace handling or weakening of the train-only optimization guard;
6. invalid recovery snapshots, replayed/skipped optimizer steps, incorrect run order, repeated/substituted rows, or budget violation;
7. more than 104 diagnostic backward calls, unregistered samples, or diagnostic persistent-state mutation;
8. OOM or non-finite loss, gradient, parameter, activation, alignment, geometry, or recovery value;
9. full-devval evaluation, AP/AR, tuning, checkpoint selection, protected-file mutation, or heavy-artifact Git violation.

Do not automatically change seed, activation parameters, bias, LR, optimizer, precision, batch size, resolution, loss, run length, sample order, trace schedule, or recovery policy after observing behavior.

## Next action

Execute V64 exactly as written in `docs/NEXT_TASK.md`. First generate and freeze one source-locked seed-1 common initialization and prove the two variants differ only in bbox-distance activation. Then run the bounded 200+200 pair. Even a positive independent-initialization confirmation does not authorize a full 7,187-step run or AP/AR evaluation.