# Current Task

## Authorization

The user authorizes **V57 MM-UAV alignment-on equal-versus-reliability fusion paired ablation** under the standing local/private-research-only rule.

V56 established descriptive three-seed internal confirmation that learned feature alignment improves AP50:95 directionally. V57 now holds learned alignment enabled and tests whether learned reliability-aware fusion improves over fixed equal fusion.

This is a single-seed paired experiment. It does not authorize additional seeds, tuning, architecture search, manuscript edits, public claims, redistribution, or external sharing.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Record the actual starting commit. Read `AGENTS.md`, project/status/blocker/task/handoff files, all V52-V56 evidence, the MM-UAV adapter, feature aligner, V54 detector integration, V55/V56 runners and evaluator utilities, and protected-file rules. Stop before GPU work on unexpected changes or source-lock mismatch. V51 remains untouched.

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

## Frozen V56 Evidence

Do not rerun or reevaluate V55/V56 experiments. Reproduce committed evidence showing:

- three-seed AP50:95 off/on means: `0.0248520 / 0.0418382`;
- AP50:95 paired-delta mean: `+0.0169862`;
- AP50:95 positive direction: 3/3 seeds;
- AP50 and AR100 positive direction: 3/3 seeds;
- AP75 direction not consistent.

V57 concerns fusion only and must not reinterpret or alter V56 alignment evidence.

## Frozen Architecture

Use the isolated MM-UAV path:

```text
independent RGB/IR/event stems
-> learned IR/event feature alignment to RGB reference grid (always enabled)
-> paired fusion mode: fixed equal OR learned reliability-aware
-> 1x1 projection to 3 channels
-> existing RepViT-M0.9-FPN-FCOS
```

RGB remains the reference feature grid and detection coordinate system. Raw-channel concatenation is forbidden.

### Paired superset requirement

Create a V57-only fusion-superset wrapper so both variants instantiate identical parameter names and shapes, including the reliability scorer:

1. `alignment_on_equal_superset`: alignment enabled; reliability scorer instantiated but bypassed; fusion weights exactly `[1/3, 1/3, 1/3]`.
2. `alignment_on_reliability_superset`: alignment enabled; reliability scorer active; softmax weights learned from RGB/IR/event features.

Initialize the reliability scorer final layer to zeros so the reliability variant also begins with exact uniform weights. Do not modify V53-V56 historical implementation files unless a minimal backward-compatible import is required; prefer new V57-only modules.

Generate one common seed-0 superset initial state before either run. Load it into both variants, hash it, and verify all tensors are bit-identical at step 0. Alignment residual heads must start at exact identity/zero. Do not initialize from trained V54-V56 checkpoints.

The only scientific difference may be whether the reliability scorer output is bypassed or used. Record total parameter count, active-gradient parameter count, and the dormant scorer status in the equal variant.

## Frozen Configuration and Run Order

Run exactly:

1. seed 0 `alignment_on_equal_superset`;
2. seed 0 `alignment_on_reliability_superset`.

Common configuration:

- input 320x320;
- batch size 1;
- FP32, AMP off;
- feature channels 32;
- FPN channels 128;
- RepViT-M0.9 without pretrained weights;
- FCOS;
- AdamW, LR `1e-4`, weight decay `1e-4`;
- no scheduler, clipping, augmentation, workers, early stopping, checkpoint selection, or hyperparameter search;
- one exact 7,187-row train-manifest pass per variant;
- 7,187 optimizer steps per run;
- V57 total optimizer-step ceiling: **14,374**.

Create one deterministic seed-0 train permutation and reuse it exactly for both variants. Record the order and SHA256 before training. Every train row must appear exactly once in each run. Do not change configuration or order after observing results.

Save only final step-7,187 checkpoints unless crash recovery technically requires otherwise. Heavy checkpoints remain local; commit metadata and hashes only.

## Frozen Evaluation

Evaluate each final checkpoint exactly once on all 1,845 frozen devval rows with identical RGB-coordinate targets and evaluator settings.

Record:

- AP50:95;
- AP50;
- AP75;
- AR100;
- image and target counts;
- inference timing;
- peak allocated/reserved memory;
- finite-output status.

Compute signed deltas as `reliability - equal`. Devval outcomes must not trigger reruns, tuning, extensions, checkpoint selection, or additional seeds. Report the direction as single-seed preliminary fusion evidence only.

## Fusion and Alignment Diagnostics

For both runs log step, row ID, losses, LR, global gradient norm, timings, CUDA memory, finite flags, and IR/event alignment theta, determinant, and grid out-of-bounds diagnostics.

For fusion, record at steps 0, 1, 10, 50, 100, 200, 500, 1000, 2000, 4000, 6000, and 7187:

- RGB/IR/event weights per sample;
- mean, standard deviation, minimum, and maximum weight per modality;
- weight-sum error from 1;
- fusion entropy;
- maximum-weight modality and dominance fraction;
- reliability-scorer gradient norm;
- whether the reliability weights departed from exact uniform initialization.

The equal variant must remain exactly uniform throughout. Low entropy or modality dominance is a reportable result, not automatically a failure, unless weights become non-finite, leave `[0,1]`, or fail to sum to 1 within numerical tolerance.

## Stop Rules

Fail closed on:

- data, V56 evidence, common initialization, parameter-shape, or sample-order mismatch;
- alignment not enabled in either variant;
- equal fusion not exactly uniform;
- reliability fusion not starting exactly uniform;
- any paired difference beyond fusion behavior;
- OOM or non-finite loss, gradient, parameter, theta, grid, prediction, metric, or fusion weight;
- fusion weights outside `[0,1]` or invalid weight sums;
- target mismatch or devval optimization leakage;
- more than 7,187 steps in either run or 14,374 total;
- protected-file changes or heavy artifacts entering Git.

Do not automatically alter batch size, resolution, precision, LR, optimizer, widths, modalities, augmentation, budget, run order, or scorer design after observing results. An incomplete pair is not valid fusion evidence.

## Required Outputs

Create `runs/v57_mmuav_paired_fusion_ablation/` containing compact protocol/source-lock files, V56 evidence verification, common-init metadata and hash, shared sample order and hash, per-variant configs/logs/summaries, alignment traces, fusion-weight traces, final-checkpoint metadata, frozen evaluation records, paired comparison, memory summary, tests, and final decision. Keep checkpoints, predictions, tensors, and media outside Git.

## Required Tests

Verify:

- exact data counts/hashes and zero sequence overlap;
- exact reproduction of committed V56 evidence without rerunning it;
- identical superset parameter names/shapes and bit-identical common initialization;
- exact identity alignment initialization and alignment enabled in both variants;
- exact uniform scorer initialization and equal-fusion outputs;
- identical sample order and one appearance per train row per variant;
- only fusion behavior differs;
- exact two-run order and 14,374-step cap;
- no devval optimization, tuning, early stopping, or checkpoint selection;
- evaluation uses exactly 1,845 rows once per final checkpoint;
- valid normalized reliability weights and required fusion diagnostics;
- no raw concatenation;
- heavy artifacts stay outside Git;
- production TriAir, V40-V56 evidence, V51 evidence, and manuscript files remain unchanged.

Run CPU/source-lock tests before CUDA and save full commands/output.

## Allowed Changes

- current task/status/blocker/handoff files;
- `runs/v57_mmuav_paired_fusion_ablation/**`;
- V57-only superset fusion modules, runner, evaluator adapters, configs, and tests;
- minimal imports needed for isolated V57 code without changing defaults.

## Forbidden Changes

- raw data or annotations;
- historical V40-V56 evidence except current pointers;
- V51 history;
- production defaults or TriAir semantics;
- alignment-off training;
- extra seeds, runs, sweeps, early stopping, checkpoint selection, or more than 14,374 optimizer steps;
- public derivatives, manuscript, submission, or public benchmark files.

## Completion State

Choose exactly one:

- `V57_PAIRED_SINGLE_SEED_FUSION_ABLATION_COMPLETE`
- `V57_BLOCKED_SOURCE_OR_V56_EVIDENCE_CONTRACT`
- `V57_BLOCKED_SUPERSET_INITIALIZATION_CONTRACT`
- `V57_BLOCKED_TRAINING_PAIR_INCOMPLETE`
- `V57_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V57_BLOCKED_EVALUATION_OR_FUSION_DIAGNOSTICS`
- `V57_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`

A successful result reports signed fusion metric deltas and weight diagnostics as single-seed preliminary internal evidence only. It does not authorize multi-seed fusion confirmation, tuning, manuscript changes, public claims, or redistribution.

Update status, blocker, and handoff files, then run `rarepdet/tools/finish_task.ps1`.

## Commit Message

`exp: run V57 MM-UAV paired fusion ablation`

## Final Report Requirements

Report starting/final commit SHAs, source and V56 evidence hashes, common-init and sample-order hashes, superset parameter verification, exact configs and step counts, checkpoint metadata, timing/memory/finite summaries, alignment diagnostics, fusion-weight/entropy/dominance diagnostics, both devval metric sets, signed deltas, test/protected-file results, CUDA reproducibility limitations, the single-seed limitation, and the next authorization boundary.
