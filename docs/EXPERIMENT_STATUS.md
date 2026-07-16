# Experiment Status

Updated: 2026-07-16

## Active task

`V57_MMUAV_PAIRED_FUSION_ABLATION_AUTHORIZED`

## User authorization

The user authorized continuation from completed V56 alignment confirmation to one bounded, local/private, single-seed paired fusion experiment. V57 compares fixed equal fusion against learned reliability-aware fusion while keeping learned feature alignment enabled in both variants.

The standing private-research instruction remains frozen and must not be repeatedly reconfirmed.

## V56 prerequisite evidence

- V56 outcome: `V56_THREE_SEED_PAIRED_ALIGNMENT_CONFIRMATION_COMPLETE`.
- AP50:95 alignment-on minus alignment-off was positive for seeds 0, 1, and 2.
- Three-seed AP50:95 off/on means: `0.0248520 / 0.0418382`.
- Mean paired AP50:95 delta: `+0.0169862`.
- AP50 and AR100 directions were positive for 3/3 seeds; AP75 direction was not consistent.
- V55/V56 checkpoints and experiments must not be rerun or used as V57 initialization.

## Frozen data contract

- RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032.
- Train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`.
- Devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Train/devval sequence overlap: 0.
- IR-only rows excluded: 106.
- No-GT rows remain `UNLABELED` and excluded: 35,898.
- RGB boxes remain the sole detector targets; IR boxes are metadata and event has no detector target.

## V57 paired protocol

Run exactly two seed-0 variants in this order:

1. `alignment_on_equal_superset`;
2. `alignment_on_reliability_superset`.

Both variants must use an identical V57-only superset model with the same parameter names and shapes. Both keep IR/event learned feature alignment enabled. The reliability scorer exists in both variants; equal fusion bypasses it and remains exactly uniform, while reliability fusion uses it.

The reliability scorer final layer must be zero initialized so both variants begin with exact `[1/3, 1/3, 1/3]` fusion weights. One common initialization and one shared deterministic train order must be frozen and hashed before training.

## Frozen configuration

- Input 320x320, batch size 1, FP32, AMP off.
- Feature channels 32 and FPN channels 128.
- RepViT-M0.9 without pretrained weights, FCOS.
- AdamW, LR `1e-4`, weight decay `1e-4`.
- No scheduler, clipping, augmentation, workers, tuning, early stopping, checkpoint selection, or devval optimization.
- Exactly 7,187 optimizer steps per variant; V57 total ceiling 14,374.
- Each final checkpoint evaluated exactly once on all 1,845 devval rows.

## Evidence contract

Record AP50:95, AP50, AP75, AR100 and signed `reliability - equal` deltas. Also record reliability weights, modality statistics, entropy, dominance, normalization error, scorer gradients, alignment diagnostics, memory, timing, and finite-value status.

The result is single-seed preliminary internal fusion evidence only. Devval outcomes may not trigger reruns, tuning, extra seeds, or extensions.

## Gates

- Only the exact V57 protocol in `docs/NEXT_TASK.md` is authorized.
- Alignment must remain enabled in both variants.
- Paired differences beyond fusion behavior fail closed.
- V57 optimizer steps must not exceed 14,374.
- OOM, non-finite values, invalid fusion weights, source/V56/init/order mismatch, devval optimization leakage, incomplete pair, protected-file changes, or heavy artifacts entering Git must fail closed.
- Production TriAir behavior, V40-V56 evidence, V51 evidence, and manuscript files remain protected.
- No extra seeds, tuning, manuscript edits, public claims, release, redistribution, or external sharing is authorized.

## Allowed completion states

- `V57_PAIRED_SINGLE_SEED_FUSION_ABLATION_COMPLETE`
- `V57_BLOCKED_SOURCE_OR_V56_EVIDENCE_CONTRACT`
- `V57_BLOCKED_SUPERSET_INITIALIZATION_CONTRACT`
- `V57_BLOCKED_TRAINING_PAIR_INCOMPLETE`
- `V57_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V57_BLOCKED_EVALUATION_OR_FUSION_DIAGNOSTICS`
- `V57_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`
