# Current Task

## Authorization

The user reported that V63 completed and was pushed. Under the standing automatic task-handoff workflow, the user authorizes **V64 MM-UAV seed-1 paired bbox-activation confirmation pilot** under the standing local/private-research-only rule.

V63 is frozen as `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`. On the exact historical seed-0 initialization, the native torchvision FCOS hard-ReLU bbox-distance path first met strict early geometry-and-gradient collapse at step 15, while exact parameter-free `softplus(beta=1.0, threshold=20.0)` remained `GEOMETRY_AND_GRADIENT_PRESERVED` at every scheduled trace through step 200.

V64 tests whether that mechanistic rescue transfers to a fresh independent initialization. It compares exactly two seed-1, alignment-on, equal-fusion V57-superset variants:

1. `v64_seed1_equal_relu_control`: native historical FCOS bbox-distance ReLU;
2. `v64_seed1_equal_softplus_b1_t20`: the same paired seed-1 state, replacing only the shared training/inference bbox-distance activation with `torch.nn.functional.softplus(x, beta=1.0, threshold=20.0)`.

The sole paired scientific difference is the bbox-distance activation. V64 does not authorize a bias or activation sweep, loss or matching changes, reliability-fusion training, full training, full-devval evaluation, AP/AR, tuning, manuscript edits, public claims, redistribution, or external sharing.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization-base and V63 completion commit: `83bb9351a5d0a6115d81047482e23fef5eed26bb`.

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, this task, all V52-V63 evidence and handoffs, the V57/V61/V62/V63 builders and runners, installed torchvision FCOS bbox-head/loss/decode source, and protected-file rules. Record the actual starting commit. Stop before CUDA on unexpected repository changes or source-lock mismatch. V51 remains untouched.

## Frozen V63 Evidence

Reproduce without modifying historical evidence:

- V63 decision: `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`;
- V63 completion commit: `83bb9351a5d0a6115d81047482e23fef5eed26bb`;
- V63 starting commit: `08783ed02856403d5cb0171f728f6244cef4bcd6`;
- V57 seed-0 common initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- first-200 prefix SHA256: `6345848e3287bea04f5c89927be7a714a6eed549a6b73d352779a6192b5c86ec`;
- ReLU first strict collapse: step `15`;
- Softplus preserved at every trace through step `200`;
- step-200 train and frozen-devval valid boxes, ReLU versus Softplus: `0 / 272,000` versus `272,000 / 272,000`;
- optimizer steps: `200 / 200`;
- diagnostic backward calls: `104`;
- verified recovery snapshots/recovery events: `26 / 0`;
- ReLU checkpoint SHA256: `ddd6b79e4695672c981f9083865f881c6b623ea818a3236e72acc691b148b2e6`;
- Softplus checkpoint SHA256: `6df9b915a2f520cbe1e51dc5ee962bd1e0b8fbb11465314377c9a3ba08a6269d`;
- post-run tests: `11 / 11` passed.

V63 and all earlier evidence are read-only. Do not resume, repair, pool, relabel, or initialize V64 from any trained V55-V63 checkpoint.

## Frozen Data, Order, and Subsets

Use exactly:

- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- devval manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- train/devval rows: `7,187 / 1,845`;
- train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- historical V57 sample order: `runs/v57_mmuav_paired_fusion_ablation/shared_sample_order.txt`;
- historical order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`;
- exact V63 first-200 prefix and SHA256 `6345848e3287bea04f5c89927be7a714a6eed549a6b73d352779a6192b5c86ec`;
- frozen 32-row train audit subset SHA256: `d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`;
- frozen four-row gradient subset SHA256: `bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`;
- frozen 32-row devval subset SHA256: `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`;
- RGB boxes as the sole detector targets.

Both variants must use the identical first-200 prefix exactly once and in the same order. Do not reshuffle, repeat, substitute, truncate, or extend rows after observing results.

## Fresh Seed-1 Common Initialization Contract

V64 must use a newly generated seed-1 common initialization, not the V57/V63 seed-0 state and not a trained checkpoint.

Before model construction:

1. set Python, NumPy, CPU Torch, and all CUDA RNG seeds to exact integer `1`;
2. apply the same deterministic/warn-only environment and constructor sequence used by V63;
3. construct one V57 equal-superset common model with the historical zero bbox-output bias and native state-dict contract;
4. serialize the complete CPU state dictionary to a local-only temporary artifact;
5. compute and record its SHA256, tensor count, parameter/buffer key lists, shapes, dtypes, and finite status;
6. reload it strictly into two independently constructed V64 models;
7. verify every step-0 parameter and buffer tensor is bit-identical across the pair.

The seed-1 initialization SHA256 is intentionally not preregistered because it has not yet been generated. It becomes frozen immediately after the pre-CUDA source-locked generation and round-trip verification. Once recorded, it may not be regenerated, selected among candidates, or changed after observing any training result.

At step 0, the two variants must have bit-identical state dictionaries, bbox pre-activation logits, classification logits, centerness logits, fused features, alignment outputs, and historical bbox-output weights/bias. Only post-activation bbox distances may differ.

## Frozen Architecture and Common Configuration

Use the isolated V57 equal-superset path:

```text
independent RGB/IR/event stems
-> learned IR/event feature alignment to the RGB reference grid (enabled)
-> V57 superset with reliability scorer instantiated but bypassed
-> exact equal weights [1/3, 1/3, 1/3]
-> 1x1 projection to 3 channels
-> RepViT-M0.9-FPN-FCOS
```

Common configuration:

- initialization seed `1`;
- input `320x320`;
- batch size `1`;
- FP32, AMP off;
- feature channels `32`;
- FPN channels `128`;
- RepViT-M0.9 without pretrained weights;
- historical FCOS target matching, losses, anchor generation, clipping, and decode paths unchanged;
- AdamW, LR `1e-4`, weight decay `1e-4`;
- no scheduler, clipping, augmentation, workers, early stopping, checkpoint selection, or hyperparameter search;
- alignment always enabled;
- equal fusion always active and exactly uniform;
- reliability scorer dormant and unchanged.

The only paired difference is:

- control: exact source-locked native ReLU bbox-distance activation;
- intervention: exact `softplus(beta=1.0, threshold=20.0)` at the same shared training/inference semantic location.

Use the V63-only activation wrapper or an equivalently source-locked V64 wrapper. Do not modify production defaults.

## CPU and Source-Lock Gates Before CUDA

Before any GPU work, tests must prove:

1. V63 evidence, manifests, historical order, first-200 prefix, subsets, and protected fingerprints match exactly;
2. the installed torchvision FCOS source hash and historical ReLU source location match V63;
3. Softplus is applied exactly once per FPN feature at the same shared training/inference semantic location;
4. Softplus parameters are exactly `beta=1.0`, `threshold=20.0`;
5. the seed-1 common initialization is generated once, saved locally, hashed, strictly reloaded, and then frozen;
6. both paired step-0 state dictionaries are bit-identical;
7. fixed-input pre-activation bbox logits, classification logits, centerness logits, fused features, and alignment outputs are bit-identical;
8. no bias, weight, loss, target, matcher, anchor, scale, decode, clipping, threshold, top-k, NMS, preprocessing, evaluator, fusion, or scorer field differs;
9. the historical train-only optimization target guard remains unchanged;
10. the split-agnostic trace target mover accepts actual frozen row `devval:00005919` without boxes/labels mutation;
11. atomic recovery snapshots round-trip model, optimizer, all RNG states, sample position, training log, and trace ledger;
12. production and historical V40-V63/V51/manuscript/submission fingerprints remain unchanged.

Fail closed before CUDA on any mismatch.

## Frozen Run Order and Budget

Run exactly, in order:

1. `v64_seed1_equal_relu_control` — exactly 200 optimizer steps;
2. `v64_seed1_equal_softplus_b1_t20` — exactly 200 optimizer steps.

V64 optimizer-step ceiling is **400 total**, exactly 200 per variant. Both variants are required. Do not stop after control collapse and do not initialize from any trained checkpoint.

Immediately before every scheduled trace, atomically save and round-trip verify a local technical recovery snapshot containing model, optimizer, all RNG states, variant, next sample position, completed optimizer-step count, source/config/initialization hashes, training-log state, and trace ledger. A technical restart is allowed only from an exact verified V64 snapshot and may not replay or skip optimizer steps. Recovery files remain local and outside Git.

## Dense Trace Contract

Trace exactly at:

```text
step 0, 1, 2, 3, 5, 10, 15, 20, 30, 50, 100, 150, 200
```

For every optimizer step, record:

- variant, step, row ID, target-box count, and matched foreground anchors;
- classification, bbox-regression, centerness, and total losses;
- LR, global gradient norm, finite flags, elapsed time, and CUDA memory;
- final bbox-output weight/bias gradients and values;
- regression-tower and detector-head gradient norms.

At every trace, run compact no-grad geometry instrumentation on the frozen 32-row train subset and record:

- bbox pre-activation distribution by FPN level and aggregate;
- post-activation distance distribution and all-zero-location fraction;
- local activation derivative summaries for all locations and matched anchors;
- decoded width/height before and after clipping;
- valid, degenerate, clipped, out-of-image, and non-finite box counts;
- bbox-output parameter statistics and deltas from initialization;
- bbox loss, matched-anchor, and minimal classification/centerness context.

At each trace, use a fresh ephemeral copy for exactly one no-step backward probe on each of the same four frozen gradient rows. Maximum diagnostic backward calls: **104 total** (`13 traces x 4 rows x 2 variants`). Record component losses, matched anchors, activation derivatives at matched anchors, bbox-output and regression-tower gradients, finite/nonzero fractions, and state-isolation hashes. Discard every ephemeral state.

At step 200, additionally trace only the frozen 32-row devval subset. Do not run all 1,845 devval rows and do not compute AP/AR.

## Pre-registered State Definitions

At a trace, classify a variant as `EARLY_BBOX_COLLAPSE` only when both hold:

1. zero positive-area decoded boxes on the frozen 32-row train subset after clipping;
2. exactly zero final bbox-output weight and bias gradient norms on all four frozen gradient rows.

Classify as `GEOMETRY_AND_GRADIENT_PRESERVED` only when both hold:

1. at least one positive-area decoded train box;
2. at least one frozen gradient row has a finite nonzero final bbox-output weight or bias gradient.

Otherwise classify as `NEITHER_PREREGISTERED_STATE`. Record the first trace satisfying each state without post-hoc thresholds.

## Frozen Decision Logic

Choose exactly one scientific outcome:

- `V64_SEED1_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`: ReLU reaches strict collapse at or before step 50; Softplus never reaches collapse and is preserved at step 200;
- `V64_SEED1_RELU_AND_SOFTPLUS_BOTH_COLLAPSE`: both variants reach strict collapse by step 200;
- `V64_SEED1_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_MIXED`: ReLU collapses, while Softplus is neither preserved nor collapsed at step 200;
- `V64_SEED1_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS`: the seed-1 ReLU control never reaches strict collapse;
- `V64_BLOCKED_SOURCE_INITIALIZATION_OR_ACTIVATION_CONTRACT`;
- `V64_BLOCKED_TRAINING_TRACE_OR_RECOVERY_INCOMPLETE`;
- `V64_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`;
- `V64_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`.

A seed-1 Softplus rescue would provide independent-initialization confirmation that hard-ReLU zero derivative is a reproducible necessary contributor under this bounded path. It would not prove sole causality, final localization quality, generalization, AP/AR, or authorize a full 7,187-step run. A failed seed-1 rescue must not trigger parameter tuning or a sweep.

## Stop Rules

Fail closed on:

- any V63 evidence, data, order, prefix, subset, or source mismatch;
- any historical V40-V63, V51, production, manuscript, or submission mutation;
- multiple seed-1 initialization candidates, regeneration after observation, or paired step-0 mismatch;
- wrong activation source location, parameters, call count, or train/inference asymmetry;
- any paired difference in parameters, buffers, bias, weight, loss, target, matching, anchors, scales, clipping, decode, threshold, NMS, preprocessing, architecture, alignment, fusion, scorer, or evaluator;
- incorrect run order, repeated/substituted rows, more than 200 steps per variant, or more than 400 total steps;
- more than 104 diagnostic backward calls or use of unregistered samples;
- invalid recovery state, replayed/skipped steps, or diagnostic mutation of persistent state;
- OOM or non-finite loss, gradient, parameter, activation, alignment, geometry, or recovery value;
- full devval, AP/AR, tuning, early stopping, checkpoint selection, extra seed/variant, rerun, or automatic extension;
- heavy artifacts entering Git.

Do not automatically change seed, activation parameters, bias, LR, optimizer, precision, batch size, resolution, loss, run length, order, trace schedule, or recovery policy after observing behavior.

## Required Outputs

Create `runs/v64_mmuav_seed1_bbox_activation_confirmation/` containing compact files such as:

```text
protocol.json
protocol.md
source_lock_v64.json
v63_evidence_verification.json
seed1_initialization_verification.json
activation_intervention.json
train_prefix_200.txt
train_prefix_200_sha256.txt
trace_schedule.json
per_variant_config.json
per_variant_training_log.csv
per_variant_trace_geometry.json
per_variant_trace_gradient.json
activation_derivative_summary.json
recovery_ledger.json
per_variant_checkpoint_metadata.json
paired_trace_comparison.json
final_decision.json
memory_timing_summary.json
safety_audit.json
test_commands.txt
test_output.txt
handoff.md
```

Keep initialization artifacts, checkpoints, optimizer states, recovery snapshots, raw tensors, predictions, images, feature maps, and other heavy artifacts local and outside Git.

## Required Tests

Verify:

- exact V63 evidence and protected-file immutability;
- exact manifests, order, first-200 prefix, and subset hashes;
- one-time seed-1 initialization generation, local serialization, SHA256, strict reload, and freeze;
- bit-identical paired step-0 state and pre-activation/non-bbox outputs;
- exact ReLU versus exact Softplus as the only intervention;
- identical losses, matching, anchors, scale, clipping, decode, threshold, NMS, evaluator, alignment, fusion, and scorer paths;
- unchanged train-only optimization guard and valid `devval:00005919` trace path;
- exact 200/200 order, 400-step ceiling, trace schedule, and 104-call ceiling;
- valid recovery round trips with no replay or skipped steps;
- persistent-state isolation from diagnostic probes;
- finite losses, gradients, activations, geometry, and recovery metadata;
- zero full-devval rows and no AP/AR, tuning, threshold selection, or checkpoint selection;
- no heavy artifacts in Git.

Run all CPU/source-lock tests before CUDA and post-run tests afterward. Save exact commands and outputs.

## Allowed Changes

- current task/status/blocker/write-record and V64 handoff files;
- `runs/v64_mmuav_seed1_bbox_activation_confirmation/**`;
- V64-only runner, seed-1 initialization freezer, activation wrapper/instrumentation, recovery utilities, and tests;
- minimal backward-compatible imports that do not change production defaults.

## Forbidden Changes

- historical V40-V63 evidence or V51 history;
- trained V55-V63 checkpoint modification, repair, resume, pooling, or initialization;
- production TriAir defaults or semantics;
- raw data or annotations;
- bias/weight changes, activation parameters other than exact Softplus, or any sweep;
- loss, target, matcher, anchor, scale, clipping, decode, threshold, NMS, preprocessing, detector, evaluator, alignment, fusion, or scorer changes;
- reliability-fusion training;
- full 7,187-step training, full devval, AP/AR, tuning, checkpoint selection, additional seeds/variants, reruns, or automatic extension;
- public derivatives, manuscript, submission, or benchmark files.

## Completion State

Choose exactly one allowed V64 state, update `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, and the V64 handoff, then run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Commit Message

`exp: run V64 seed1 paired bbox activation confirmation`

## Final Report Requirements

Report starting/final commit SHAs; V63 evidence verification; source/data/order/prefix/subset hashes; seed-1 generation procedure and frozen initialization SHA256; activation source location and exact parameters; proof of paired step-0 and pre-activation identity; optimizer/backward/recovery counts; every trace classification and first-collapse/preservation step; activation-derivative evidence; step-200 frozen train/devval geometry; checkpoint hashes and local-only locations; timing/memory and finite-state results; tests and protected-file status; reproducibility warnings; selected bounded V64 outcome; and the strict no-full-run/no-AP claim boundary.