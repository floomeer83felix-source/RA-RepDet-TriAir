# Experiment Status

Updated: 2026-07-15

## Active task

`V55_MMUAV_PAIRED_ALIGNMENT_ABLATION_AUTHORIZED`

## User authorization

The user authorized one bounded local/private paired experiment comparing `alignment_off_equal` against `alignment_on_equal` under one frozen single-seed protocol. The standing rule remains: once the user accepts a proposed next stage, write the task into Git immediately without waiting for another reminder.

## V54 prerequisite

- V54 outcome: `V54_GPU_PILOT_PASS_READY_FOR_PAIRED_ALIGNMENT_ABLATION`.
- Primary V54 pilot completed 200/200 optimizer steps with finite losses, gradients, theta, and grids.
- No OOM, devval optimization leakage, or protected-file violation occurred.
- V54 was engineering/numerical evidence only; AP/AR were not computed.

## Frozen data contract

- RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032.
- Train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`.
- Devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Train/devval sequence overlap: 0.
- IR-only excluded: 106.
- `UNLABELED` excluded: 35,898.
- RGB boxes are the sole detector targets; IR is metadata and event has no detector target.

## V55 paired protocol

- Variants: `alignment_off_equal` then `alignment_on_equal`.
- One common seed-0 initialization, shared parameter tensors bit-identical at step 0.
- Same deterministic sample order for both runs.
- Input 320x320, batch 1, FP32, AdamW, LR `1e-4`, weight decay `1e-4`.
- No scheduler, clipping, augmentation, pretrained backbone, sweep, early stopping, or checkpoint selection.
- Exactly one train-manifest pass per variant: 7,187 optimizer steps.
- Total V55 ceiling: 14,374 optimizer steps.
- Final checkpoints evaluated exactly once on all 1,845 frozen devval rows.
- Metrics: AP50:95, AP50, AP75, and AR100.
- Signed comparison: `alignment_on_equal - alignment_off_equal`.

## Claim boundary

V55 is single-seed preliminary accuracy evidence only. It does not authorize a multi-seed study, RA/reliability-fusion training, manuscript edits, public claims, or redistribution.

## Gates

- Configuration differences beyond `alignment_enabled` fail closed.
- OOM, non-finite values, source/init/order mismatch, devval optimization leakage, step-limit violation, or protected-file changes fail closed.
- Heavy checkpoints and predictions remain local and outside Git.
- V51 remains separate and unchanged.
- The unresolved MM-UAV redistribution license remains a dissemination restriction.

## Allowed completion states

- `V55_PAIRED_SINGLE_SEED_COMPLETE_METRICS_RECORDED`
- `V55_BLOCKED_SOURCE_OR_INITIALIZATION_CONTRACT`
- `V55_BLOCKED_TRAINING_PAIR_INCOMPLETE`
- `V55_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V55_BLOCKED_EVALUATION_CONTRACT`
- `V55_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`
