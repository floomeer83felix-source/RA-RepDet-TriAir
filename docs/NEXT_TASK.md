# Current Task

## Authorization

The user authorizes **V56 MM-UAV three-seed paired alignment confirmation** under the standing local/private-research-only rule.

V55 seed 0 is frozen completed evidence and must not be rerun. V56 adds exactly two paired seeds:

1. seed 1: `alignment_off_equal`, then `alignment_on_equal`;
2. seed 2: `alignment_off_equal`, then `alignment_on_equal`.

The purpose is to determine whether the positive V55 alignment direction persists across three total seeds while holding all non-seed and non-alignment factors fixed. This remains internal research evidence; it does not authorize manuscript edits, public claims, redistribution, tuning, or RA/reliability-fusion training.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization-base evidence commit: `fe56b3e44b6bafbf1d6a77bf9b80637c01d55d3e`.

Read `AGENTS.md`, project/status/blocker/task/handoff files, all V52-V55 evidence, the MM-UAV adapter, alignment scaffold, V54 detector integration, V55 runner/evaluator, and protected-file rules. Record the actual starting commit. Stop before GPU work on unexpected changes or source-lock mismatch. V51 remains untouched.

## Frozen Data Contract

Use exactly:

- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- devval manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- train/devval/total: 7,187 / 1,845 / 9,032;
- train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- train/devval sequence overlap: 0;
- 106 IR-only rows excluded;
- 35,898 no-GT rows remain `UNLABELED` and excluded;
- RGB boxes are the sole detector targets;
- IR boxes are metadata only; event has no detector target.

No pseudo labels, interpolation, box transfer, nearest-frame substitution, empty-target conversion, or devval optimization is allowed. Reproduce counts and hashes before CUDA work.

## Frozen V55 Seed-0 Evidence

Do not retrain or reevaluate seed 0. Reproduce and ingest the committed V55 records:

- common initialization SHA256: `91fec577380f895c932ffeb090bba7d376abc1ea1d97d568ae46901a7bbcb983`;
- sample-order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`;
- off AP50:95 / AP50 / AP75 / AR100: `0.0132693 / 0.0644206 / 0.0015649 / 0.0501191`;
- on AP50:95 / AP50 / AP75 / AR100: `0.0482695 / 0.1927830 / 0.0071779 / 0.0989042`;
- signed seed-0 deltas: `+0.0350002 / +0.1283623 / +0.0056130 / +0.0487851`.

Fail closed if the committed V55 metrics or hashes do not reproduce exactly.

## Frozen Architecture and Configuration

Reuse the isolated V54/V55 path:

```text
independent RGB/IR/event stems
-> optional IR/event feature alignment to RGB reference grid
-> fixed equal fusion
-> 1x1 projection to 3 channels
-> existing RepViT-M0.9-FPN-FCOS
```

For every paired seed, the only scientific difference is `alignment_enabled=false/true`.

Common configuration:

- input 320x320;
- batch size 1;
- FP32, AMP off;
- feature channels 32;
- FPN channels 128;
- RepViT-M0.9 without pretrained weights;
- FCOS and fixed equal fusion;
- AdamW, LR `1e-4`, weight decay `1e-4`;
- no scheduler, clipping, augmentation, workers, early stopping, checkpoint selection, or hyperparameter search;
- one exact 7,187-row train-manifest pass per run.

For each seed, create one seed-specific common initial state before either variant. Load it into both variants, record its SHA256, verify all shared tensors are bit-identical, and verify the alignment-on residual heads start at exact identity/zero. Do not initialize from V54 or V55 trained checkpoints.

Generate one deterministic seed-specific train permutation and reuse it exactly for the off/on pair. Different seeds may have different orders; variants within a seed may not. Record every order and SHA256 before training.

## Frozen Run Order and Step Budget

Run exactly:

1. seed 1 `alignment_off_equal` — 7,187 steps;
2. seed 1 `alignment_on_equal` — 7,187 steps;
3. seed 2 `alignment_off_equal` — 7,187 steps;
4. seed 2 `alignment_on_equal` — 7,187 steps.

V56 new optimizer-step ceiling: **28,748**. The combined V55+V56 evidence will represent three paired seeds, but V55's 14,374 completed steps are historical and must not be repeated.

Save only final step-7,187 checkpoints unless crash recovery technically requires otherwise. Checkpoints remain local; commit metadata and hashes only. An incomplete seed pair is not valid paired evidence.

## Frozen Evaluation and Aggregation

Evaluate each of the four V56 final checkpoints exactly once on all 1,845 frozen devval rows using identical settings and RGB-coordinate targets.

Record per variant and seed:

- AP50:95;
- AP50;
- AP75;
- AR100;
- image/target counts;
- inference timing and peak allocated/reserved memory;
- finite-output status.

Compute signed deltas as `alignment_on_equal - alignment_off_equal` for seeds 1 and 2. Combine them with frozen V55 seed 0 and report, for each metric:

- all three per-seed off/on values and paired deltas;
- off and on mean and sample standard deviation;
- paired-delta mean, median, minimum, maximum, and positive-seed count;
- AP50:95 direction consistency across the three seeds.

Do not use a p-value or claim statistical significance from only three seeds. Devval outcomes must not trigger reruns, tuning, extra seeds, budget extension, or checkpoint selection.

## Diagnostics and Stop Rules

Log the same training, memory, gradient, timing, finite-value, theta, determinant, and grid-validity fields used by V55. Preserve trace summaries at the V55 trace steps.

Fail closed on:

- data, V55 evidence, initialization, or sample-order mismatch;
- OOM or non-finite loss/gradient/parameter/theta/grid/prediction/metric;
- target mismatch or devval optimization leakage;
- more than 7,187 steps in any run or 28,748 V56 steps total;
- any paired configuration difference beyond alignment enabled;
- seed-0 rerun or reevaluation;
- protected-file or heavy-artifact Git violation.

Do not automatically alter batch size, resolution, precision, LR, optimizer, width, modalities, augmentation, budget, seed set, or run order after observing results.

## Required Outputs

Create `runs/v56_mmuav_multiseed_alignment_confirmation/` containing compact protocol/source-lock files, imported V55 seed-0 evidence verification, per-seed common-init metadata, per-seed shared order/hashes, per-run configs/logs/summaries/alignment traces, final-checkpoint metadata, frozen evaluation records, three-seed aggregation, memory summary, tests, and final decision. Keep checkpoints, predictions, tensors, and media outside Git.

## Required Tests

Verify:

- exact data counts/hashes and zero sequence overlap;
- exact reproduction of committed V55 seed-0 evidence without executing seed 0;
- seed-specific common initialization and bit-identical shared tensors within each pair;
- exact identity alignment initialization;
- identical sample order within each seed pair and one appearance per train row per run;
- only `alignment_enabled` differs within each pair;
- exact four-run order and 28,748-step V56 cap;
- no devval optimization, rerun, early stopping, tuning, or checkpoint selection;
- evaluation uses exactly 1,845 rows once per final checkpoint;
- aggregation uses seeds 0, 1, and 2 exactly once;
- no raw concatenation and no RA/reliability-fusion training;
- heavy artifacts stay outside Git;
- production TriAir, V40-V55 evidence, V51 evidence, and manuscript files remain unchanged.

Run CPU/source-lock tests before CUDA and save full commands/output.

## Allowed Changes

- current task/status/blocker/handoff files;
- `runs/v56_mmuav_multiseed_alignment_confirmation/**`;
- V56-only tools, wrappers, configs, evaluator/aggregation adapters, and tests;
- minimal imports needed for isolated V56 code without changing defaults.

## Forbidden Changes

- raw data or annotations;
- historical V40-V55 evidence except current pointers;
- V51 history;
- production defaults or TriAir semantics;
- seed-0 retraining/reevaluation;
- RA/reliability-fusion training;
- seeds outside 1 and 2, extra runs, sweeps, early stopping, checkpoint selection, or more than 28,748 V56 optimizer steps;
- public derivatives, manuscript, submission, or public benchmark files.

## Completion State

Choose exactly one:

- `V56_THREE_SEED_PAIRED_ALIGNMENT_CONFIRMATION_COMPLETE`
- `V56_BLOCKED_SOURCE_OR_V55_EVIDENCE_CONTRACT`
- `V56_BLOCKED_INITIALIZATION_OR_ORDER_CONTRACT`
- `V56_BLOCKED_TRAINING_PAIR_INCOMPLETE`
- `V56_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V56_BLOCKED_EVALUATION_OR_AGGREGATION_CONTRACT`
- `V56_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`

A successful result provides three-seed internal confirmation evidence only. It does not authorize RA/reliability-fusion training, further seeds, tuning, manuscript changes, public claims, or redistribution.

Update status, blocker, and handoff files, then run `rarepdet/tools/finish_task.ps1`.

## Commit Message

exp: run V56 MM-UAV three-seed alignment confirmation

## Final Report Requirements

Report starting/final commit SHAs, source and V55 evidence hashes, seed-specific initialization and order hashes, exact configs and step counts, checkpoint metadata, timing/memory/finite summaries, alignment diagnostics, all seed-0/1/2 metrics and signed deltas, aggregate descriptive statistics and direction consistency, test/protected-file results, CUDA reproducibility limitations, and the next authorization boundary.
