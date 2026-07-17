# Task Blocker

Status: `V59_STREAMING_DIAGNOSTIC_AUTHORIZED_NO_ACTIVE_PREFLIGHT_BLOCKER`

Generated: 2026-07-17

## Current state

V58 stopped correctly after exact `torch.quantile` failed on an oversized concatenated FPN tensor. The failure was in compact reduction, not checkpoint loading, inference numerics, CUDA execution, or protected-file compliance. No root-cause diagnosis was completed.

The user has continued the workflow, and V59 now authorizes a full read-only diagnostic reset using bounded deterministic streaming histograms and compact exact per-image summaries.

## Authorized repair boundary

V59 may:

- reproduce and preserve the committed V58 blocker evidence;
- reuse the exact frozen 1,845-row order and 32-row subset;
- verify the two V57 checkpoints and the available V55 reference with exact hashes;
- implement a V59-only streaming histogram reducer with frozen bins and declared quantile intervals;
- validate the reducer on manageable synthetic tensors before CUDA;
- rerun exactly one aggregate pass for V57 equal, V57 reliability, and V55 reference in the frozen order;
- record exact candidate-stage and threshold-ladder counts, compact detailed traces, path differences, timing, memory, and a root-cause decision;
- commit only compact metadata, histograms, counts, hashes, tests, and summaries.

V59 may not:

- modify V58 historical evidence or treat its failed partial pass as a usable aggregate;
- concatenate unbounded all-row score tensors or invoke all-value `torch.quantile`;
- construct or step an optimizer, run backward, enable training mode, or mutate parameters/checkpoints;
- change score threshold, top-k, NMS, preprocessing, model, scorer, detector, architecture, or evaluator;
- compute alternate-threshold AP/AR or select a threshold;
- perform training, fine-tuning, tuning, extra seeds, manuscript changes, public claims, redistribution, or external sharing;
- modify production TriAir defaults, V40-V58 evidence, V51 history, raw data, or annotations;
- place checkpoints, raw predictions, images, feature maps, or tensor dumps in Git.

## Fail-closed blockers

Stop with the matching V59 blocked state on:

1. V58 evidence, devval/order/subset, or checkpoint mismatch;
2. histogram validation failure or histogram specification drift;
3. unbounded score retention, oversized reduction, or instrumentation failure;
4. optimizer, backward, gradient, training-mode, parameter, or checkpoint mutation;
5. more than one V59 aggregate pass per checkpoint or incorrect run order;
6. non-finite values that prevent interpretation;
7. alternate-threshold AP/AR, threshold selection, protected-file change, or heavy-artifact Git violation.

Do not automatically switch to memmap, change binning, patch the detector, or retry a consumed pass after observing a failure. A new blocker must preserve the last error lines and two repair options.

## Next action

Execute V59 exactly as written in `docs/NEXT_TASK.md`. The task remains diagnostic only. A completed root-cause classification does not authorize the corrective experiment.
