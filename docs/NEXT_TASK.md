# Current Task

## Authorization

The user authorizes **V55 MM-UAV paired alignment ablation** under the standing local/private-research-only rule.

Run exactly two single-seed variants:

1. `alignment_off_equal`
2. `alignment_on_equal`

This task measures the preliminary contribution of learned feature alignment while holding all other factors fixed. Do not ask again whether the work is private. Do not treat one-seed results as statistically reliable or manuscript-ready.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization-base evidence commit: `0e1829094c683218b00e3350b08c51e79441dbfc`.

Read `AGENTS.md`, project/status/blocker/task/handoff files, all V52-V54 evidence, the MM-UAV dataset adapter, V53 alignment scaffold, V54 detector integration, and existing evaluator utilities. Record the actual starting commit. Stop before GPU work on unexpected changes or source-lock mismatch. V51 remains untouched.

## Frozen Data Contract

Use exactly:

- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- devval manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- train/devval/total: 7,187 / 1,845 / 9,032;
- train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- sequence overlap: 0;
- 106 IR-only rows excluded;
- 35,898 no-GT rows remain `UNLABELED` and excluded;
- RGB boxes are the only detector targets;
- IR boxes are metadata only; event has no detector target.

No pseudo labels, interpolation, box transfer, nearest-frame substitution, empty-target conversion, or devval optimization is allowed. Reproduce all counts and hashes before CUDA work.

## Frozen Architecture

Reuse the isolated V54 integration:

```text
independent RGB/IR/event stems
-> optional IR/event feature alignment to RGB reference grid
-> fixed equal fusion
-> 1x1 projection to 3 channels
-> existing RepViT-M0.9-FPN-FCOS
```

The only paired difference is `alignment_enabled`:

- off: `False`;
- on: `True`.

Both runs must have identical parameter shapes, detector, equal fusion, preprocessing, optimizer, training budget, evaluator, and sample order. No raw-channel concatenation and no RA/reliability fusion training.

Generate one common seed-0 initial state before either run. Load it into both variants. Record its SHA256 and verify all shared tensors are bit-identical at step 0. Do not use the V54 step-200 checkpoint as initialization. The alignment-on residual heads must start at exact identity.

## Frozen Training Protocol

Run order is fixed:

1. `alignment_off_equal`
2. `alignment_on_equal`

Common configuration:

- seed 0;
- input 320x320;
- batch size 1;
- FP32, AMP off;
- feature channels 32;
- FPN channels 128;
- no pretrained backbone;
- AdamW, LR `1e-4`, weight decay `1e-4`;
- no scheduler, clipping, augmentation, or hyperparameter search;
- train manifest only;
- one exact manifest pass per variant: 7,187 optimizer steps;
- total V55 ceiling: 14,374 optimizer steps.

Create one deterministic row order and reuse the identical order for both runs. Record the row list and SHA256 before training. Every train row must appear exactly once per variant. Do not change configuration or run order after observing results.

Save only final step-7,187 checkpoints unless crash recovery technically requires otherwise. Checkpoints remain local; commit metadata and hashes only. No intermediate checkpoint selection or early stopping.

## Frozen Evaluation

Evaluate each final checkpoint exactly once on all 1,845 frozen devval rows using identical settings and RGB-coordinate targets.

Record:

- AP50:95;
- AP50;
- AP75;
- AR100;
- image and target counts;
- inference timing;
- peak allocated/reserved memory;
- finite-output status.

Compute signed deltas as `alignment_on_equal - alignment_off_equal`. Devval results must not trigger reruns, tuning, extension, or checkpoint selection. The AP50:95 direction may be recorded as positive/zero/negative, always labeled single-seed preliminary evidence.

## Diagnostics and Stop Rules

For both runs log step, row ID, loss components, LR, global gradient norm, timings, memory, and finite flags. For alignment-on also log IR/event alignment gradient norms, theta deviation, determinants, and grid out-of-bounds fraction. Save summaries at steps 0, 1, 10, 50, 100, 200, 500, 1000, 2000, 4000, 6000, and 7187.

Fail closed on:

- source, initialization, or sample-order mismatch;
- OOM or non-finite loss/gradient/parameter/theta/grid/prediction/metric;
- target mismatch or devval optimization leakage;
- more than 7,187 steps in either run or 14,374 total;
- any paired configuration difference beyond alignment enabled;
- protected-file changes.

Do not automatically alter batch size, resolution, precision, LR, optimizer, width, modalities, augmentation, budget, or order. An incomplete pair is not an alignment comparison.

## Required Outputs

Create `runs/v55_mmuav_paired_alignment_ablation/` containing compact protocol/source-lock files, common-init metadata, shared sample order/hash, per-variant configs and training logs/summaries, alignment trace, frozen evaluation protocol, both metric files, paired comparison, checkpoint metadata, memory summary, tests, and final decision. Keep checkpoints, predictions, tensors, and media outside Git.

## Required Tests

Verify:

- exact counts/hashes and zero sequence overlap;
- same common initialization and bit-identical shared tensors;
- exact identity alignment initialization;
- identical sample order and one appearance per train row per variant;
- only `alignment_enabled` differs;
- 7,187-step per-run and 14,374-step total caps;
- no devval optimization;
- evaluation uses exactly 1,845 final-checkpoint-only rows;
- no raw concatenation or checkpoint selection path;
- heavy artifacts stay outside Git;
- production TriAir, V40-V54 evidence, V51 evidence, and manuscript files remain unchanged.

Run CPU/source-lock tests before CUDA and save full commands/output.

## Allowed Changes

- current task/status/blocker/handoff files;
- `runs/v55_mmuav_paired_alignment_ablation/**`;
- V55-only tools, wrappers, evaluator adapters, configs, and tests;
- minimal imports needed for isolated V55 code without changing defaults.

## Forbidden Changes

- raw data or annotations;
- historical V40-V54 evidence except current pointers;
- V51 history;
- production defaults or TriAir semantics;
- RA/reliability fusion training;
- extra seeds, extra primary runs, sweeps, early stopping, budget extension, or more than 14,374 optimizer steps;
- public derivatives, manuscript, or submission files.

## Completion State

Choose exactly one:

- `V55_PAIRED_SINGLE_SEED_COMPLETE_METRICS_RECORDED`
- `V55_BLOCKED_SOURCE_OR_INITIALIZATION_CONTRACT`
- `V55_BLOCKED_TRAINING_PAIR_INCOMPLETE`
- `V55_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V55_BLOCKED_EVALUATION_CONTRACT`
- `V55_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`

A successful result reports signed metric deltas but does not authorize multi-seed work or manuscript claims.

Update status, blocker, and handoff files, then run `rarepdet/tools/finish_task.ps1`.

## Commit Message

exp: run V55 MM-UAV paired alignment ablation

## Final Report Requirements

The final report must include commit SHAs, source hashes/counts, common-init and sample-order hashes, exact configs and step counts, checkpoint metadata, timing/memory/finite summaries, alignment diagnostics, both devval metric sets, signed deltas, test/protected-file results, the single-seed limitation, and the next authorization boundary.
