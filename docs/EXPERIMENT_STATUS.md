# Experiment Status

Updated: 2026-07-16

## Active task

`V56_MMUAV_THREE_SEED_ALIGNMENT_CONFIRMATION_AUTHORIZED`

## User authorization

The user authorized continuation from the completed V55 single-seed paired result to a frozen three-seed confirmation. V55 seed 0 remains historical evidence and must not be rerun or reevaluated. V56 may run exactly the alignment-off/alignment-on pairs for seeds 1 and 2 under `docs/NEXT_TASK.md`.

The standing local/private-research instruction remains frozen and must not be repeatedly reconfirmed.

## V55 prerequisite evidence

- V55 outcome: `V55_PAIRED_SINGLE_SEED_COMPLETE_METRICS_RECORDED`.
- Both seed-0 variants completed 7,187 steps and one 1,845-row devval evaluation.
- Seed-0 AP50:95 off/on/delta: `0.0132693 / 0.0482695 / +0.0350002`.
- Seed-0 AP50 off/on/delta: `0.0644206 / 0.1927830 / +0.1283623`.
- Seed-0 AP75 off/on/delta: `0.0015649 / 0.0071779 / +0.0056130`.
- Seed-0 AR100 off/on/delta: `0.0501191 / 0.0989042 / +0.0487851`.
- Seed-0 result is frozen single-seed preliminary evidence only.

## Frozen data contract

- RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032.
- Train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`.
- Devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Train/devval sequence overlap: 0.
- IR-only rows excluded: 106.
- No-GT rows remain `UNLABELED` and excluded: 35,898.
- RGB boxes remain the sole detector targets; IR boxes are metadata and event has no detector target.

## V56 paired protocol

Run exactly four new training/evaluation variants in this order:

1. seed 1 `alignment_off_equal`;
2. seed 1 `alignment_on_equal`;
3. seed 2 `alignment_off_equal`;
4. seed 2 `alignment_on_equal`.

Each run uses one exact 7,187-row train-manifest pass. V56's new optimizer-step ceiling is 28,748. Each final checkpoint is evaluated exactly once on all 1,845 devval rows.

Within each seed pair, all settings, shared initial tensors, sample order, detector, equal fusion, preprocessing, optimizer, budget, and evaluator must be identical; only `alignment_enabled` may differ. Seed-specific common initializations and sample orders must be frozen and hashed before training. Trained V54/V55 checkpoints may not initialize V56.

## Frozen configuration

- Input 320x320, batch size 1, FP32, AMP off.
- Feature channels 32 and FPN channels 128.
- RepViT-M0.9 without pretrained weights, FCOS, fixed equal fusion.
- AdamW, LR `1e-4`, weight decay `1e-4`.
- No scheduler, clipping, augmentation, workers, hyperparameter search, early stopping, checkpoint selection, or devval optimization.

## Aggregate evidence contract

Combine frozen seed 0 with new seeds 1 and 2. Report per-seed AP50:95, AP50, AP75, AR100 and signed on-minus-off deltas, plus descriptive mean/std and paired-delta summaries. Do not claim statistical significance from three seeds and do not use devval outcomes to trigger reruns, tuning, extra seeds, or extensions.

## Gates

- Only the exact V56 task in `docs/NEXT_TASK.md` is authorized.
- Seed 0 must not be rerun or reevaluated.
- V56 optimizer steps must not exceed 28,748.
- OOM, non-finite values, source/V55/init/order mismatch, devval optimization leakage, pair asymmetry, step-limit violation, protected-file changes, or heavy artifacts entering Git must fail closed.
- Production TriAir behavior, V40-V55 historical evidence, V51 evidence, and manuscript files remain protected.
- No RA/reliability-fusion training, further seeds, tuning, manuscript edits, public claims, release, redistribution, or external sharing is authorized.

## Allowed completion states

- `V56_THREE_SEED_PAIRED_ALIGNMENT_CONFIRMATION_COMPLETE`
- `V56_BLOCKED_SOURCE_OR_V55_EVIDENCE_CONTRACT`
- `V56_BLOCKED_INITIALIZATION_OR_ORDER_CONTRACT`
- `V56_BLOCKED_TRAINING_PAIR_INCOMPLETE`
- `V56_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V56_BLOCKED_EVALUATION_OR_AGGREGATION_CONTRACT`
- `V56_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`