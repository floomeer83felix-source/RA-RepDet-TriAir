# Task Blocker

Status: `V73_TRANSFER_BENCHMARK_AUTHORIZED_NO_ACTIVE_PREFLIGHT_BLOCKER`

Generated: 2026-07-26

## Current state

V72 completed successfully but produced effectively zero AP under naive unregistered five-channel zero-shot transfer. The user has authorized supervised retraining rather than immediate manuscript integration of that negative result.

The active task is:

`V73_MMUAV_TRIAIR_INITIALIZED_ALIGNMENT_AWARE_TRANSFER_BENCHMARK_AUTHORIZED`

There is no active data, checkpoint, adapter, or evaluator blocker before the ordered V73 source-lock and transfer-map checks. The frozen MM-UAV manifests, V53/V57-compatible learned alignment path, Softplus stability evidence, and all six source TriAir checkpoints already exist.

## Immediate execution path

V73 must:

1. lock the existing `7,187`-row train and `1,845`-row devval manifests;
2. reverify the six seed-matched TriAir source checkpoints;
3. freeze exact compatible tensor-transfer maps before training;
4. build one common alignment-aware MM-UAV architecture;
5. run `scratch_equal`, `triair_init_equal`, and `triair_init_reliability` for seeds `0`, `1`, and `2`;
6. train each run for exactly `10` epochs and `71,870` optimizer steps;
7. evaluate only the final checkpoint once on the full devval set;
8. compute the required paired transfer comparisons and three-seed summaries;
9. stop without result-driven tuning, extension, reruns, or variant additions.

## Frozen scientific controls

- same train/devval rows for all runs;
- same seed-specific epoch orders across all variants;
- same optimizer, scheduler, batch size, image size, and no-augmentation contract;
- same independent modality stems and learned feature alignment;
- same Softplus bbox activation;
- equal fusion for the scratch and equal-transfer controls;
- reliability fusion only for the reliability-transfer variant;
- no modality dropout or auxiliary fusion loss;
- no devval monitoring or checkpoint selection.

## Actual fail-closed conditions

Stop with the matching V73 blocked state only if:

1. a seed-matched TriAir checkpoint hash, model class, or source identity does not match frozen evidence;
2. an exact reproducible name-and-shape-compatible transfer map cannot be frozen;
3. the MM-UAV data manifests or evaluator differ from the frozen contract;
4. training or evaluation encounters unrecoverable OOM, corruption, non-finite state, or invalid geometry;
5. a final checkpoint cannot produce one complete metric record on all `1,845` rows;
6. optimizer, scheduler, RNG, or data-order recovery state cannot be restored exactly after interruption;
7. protected historical evidence drifts or raw/private/heavy artifacts enter Git.

Poor AP, inconsistent gains, or a negative seed result is not a blocker and must not trigger tuning, extra epochs, replacement checkpoints, or reruns.

## Claim boundary

The V73 output is supervised MM-UAV target-domain transfer. It may compare from-scratch training, TriAir initialization, and reliability-aware transfer under one matched protocol.

It may not be described as zero-shot, independent/blind external validation, or generalization without MM-UAV labels.

## Next action

Execute `docs/NEXT_TASK.md` immediately. Begin with source/data locks and the exact transfer-map audit, then launch the nine authorized runs in the specified order. Do not execute the superseded manuscript-only V73 integration task.
