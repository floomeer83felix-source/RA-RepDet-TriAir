# Current Task

## Authorization

The user reported that V62 completed and was pushed. Under the standing automatic task-handoff workflow, the user authorizes **V63 MM-UAV paired bbox-activation rescue pilot** under the standing local/private-research-only rule.

V62 is frozen as `V62_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE`. Both the historical ReLU control and the exact `+0.01` four-element bbox-output-bias intervention first met strict early geometry-and-gradient collapse at step 20 and ended step 500 with zero valid boxes. V63 therefore tests one different, mechanistically targeted intervention: replace only the hard ReLU bbox-distance activation with a fixed parameter-free Softplus activation while preserving all parameters, initialization tensors, data, order, optimizer, losses, matching, decode semantics, alignment, and equal fusion.

V63 compares exactly two seed-0, alignment-on, equal-fusion V57-superset variants:

1. `v63_equal_relu_control`: exact historical V57 FCOS bbox-distance ReLU path;
2. `v63_equal_softplus_b1_t20`: the same model and state, except the actual FCOS bbox-distance activation is `torch.nn.functional.softplus(x, beta=1.0, threshold=20.0)` in both training and inference/decode paths.

The sole scientific intervention is the bbox-distance activation. V63 does not authorize a bias change or sweep, loss change, target/matching change, reliability-fusion training, full training, AP/AR evaluation, tuning, manuscript edits, public claims, redistribution, or external sharing.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization-base evidence commit: `286508ff34d4cd0ac494d803e5a146a686318f14`.

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, this task, all V52-V62 evidence and handoffs, V55/V57/V61/V62 model builders and runners, torchvision FCOS bbox-head/loss/decode code, and protected-file rules. Record the actual starting commit. Stop before CUDA work on unexpected repository changes or source-lock mismatch. V51 remains untouched.

## Frozen V62 Evidence

Reproduce without modifying historical evidence:

- V62 decision: `V62_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE`;
- V62 completion commit: `286508ff34d4cd0ac494d803e5a146a686318f14`;
- exact V57 common seed-0 initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- both V62 variants were `GEOMETRY_AND_GRADIENT_PRESERVED` at steps 0, 1, and 2;
- both first met strict `EARLY_BBOX_COLLAPSE` at step 20;
- both had `0 / 272,000` valid train boxes and `0 / 272,000` valid frozen-devval boxes at step 500;
- V62 control/intervention optimizer steps: `500 / 500`;
- V62 diagnostic backward calls: `96`;
- V62 verified recovery snapshots/recovery events: `24 / 0`;
- V62 control checkpoint SHA256: `644b26444f09707aa463658c2437585dc8664f237cd0dea006995312b77c097f`;
- V62 `+0.01` checkpoint SHA256: `8980901d2a4d8e137cb44d36f34139ef97ef4eba57b733f6e414448a41c100a4`.

V61 and V62 evidence are read-only. Do not resume, repair, pool, relabel, or initialize from their trained checkpoints.

## Frozen Data, Initialization, Order, and Subsets

Use exactly:

- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- devval manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- train/devval rows: `7,187 / 1,845`;
- train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- historical V57 sample order: `runs/v57_mmuav_paired_fusion_ablation/shared_sample_order.txt`;
- historical order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`;
- V57 common seed-0 initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- V60/V62 frozen 32-row train audit subset SHA256: `d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`;
- frozen four-row gradient subset SHA256: `bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`;
- frozen 32-row devval subset SHA256: `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`;
- RGB boxes as the sole detector targets.

Materialize and hash the first exactly 200 entries of the frozen historical V57 order before model construction. Both variants must use this identical prefix exactly once and in the same order. Do not reshuffle, repeat, substitute, or extend rows after observing results.

Reconstruct the exact historical V57 common initialization and reproduce its serialized SHA256 before either run. Create one independent in-memory copy per variant. At step 0, all parameter and buffer tensors must be bit-identical across variants. The historical bbox-output bias remains unchanged in both variants; the V62 `+0.01` intervention must not be reused.

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

- seed 0;
- input 320x320;
- batch size 1;
- FP32, AMP off;
- feature channels 32;
- FPN channels 128;
- RepViT-M0.9 without pretrained weights;
- historical FCOS target matching, losses, anchor generation, clipping, and decode paths unchanged;
- AdamW, LR `1e-4`, weight decay `1e-4`;
- no scheduler, clipping, augmentation, workers, early stopping, checkpoint selection, or hyperparameter search;
- alignment always enabled;
- equal fusion always active and exactly uniform;
- reliability scorer dormant and unchanged.

The only paired difference is the bbox-distance activation:

- control: the exact historical ReLU expression and source location;
- intervention: `softplus(beta=1.0, threshold=20.0)` at that same source location.

The Softplus intervention must be parameter-free and V63-specific. It may not change parameter names, shapes, state-dict keys, initialization, logits, matching, losses, anchors, scales, clipping, or evaluator behavior. At step 0, verify bit-identical pre-activation bbox logits, classification logits, centerness logits, fused features, and all state tensors. Only post-activation bbox distances may differ.

## CPU and Source-Lock Gates Before CUDA

Before any GPU work, tests must prove:

1. the historical control calls the exact source-locked ReLU bbox-distance path;
2. the intervention calls Softplus exactly once at the same semantic location for both training and inference;
3. Softplus parameters are exactly `beta=1.0`, `threshold=20.0`;
4. no bias, weight, loss, target, matcher, anchor, scale, decode, clipping, threshold, NMS, or evaluator field differs;
5. the two step-0 state dictionaries are bit-identical;
6. pre-activation bbox logits and non-bbox outputs are bit-identical on fixed CPU inputs;
7. the historical train-only optimization target guard remains unchanged;
8. the V62 split-agnostic trace target mover still accepts actual frozen devval row `devval:00005919` without box/label mutation;
9. atomic recovery snapshots round-trip model, optimizer, CPU/CUDA RNG, sample position, log ledger, and trace ledger;
10. production and historical protected-file fingerprints remain unchanged.

Fail closed before CUDA on any mismatch.

## Frozen Run Order and Budget

Run exactly:

1. `v63_equal_relu_control` — 200 optimizer steps;
2. `v63_equal_softplus_b1_t20` — 200 optimizer steps.

V63 optimizer-step ceiling: **400 total**, exactly 200 per variant. An incomplete pair is not valid evidence. Do not initialize from any trained V55-V62 checkpoint.

Immediately before every scheduled trace, atomically save and round-trip verify a local technical recovery snapshot containing model, optimizer, all RNG states, variant, next sample position, completed optimizer-step count, training-log state, and trace ledger. A technical restart is allowed only from an exact verified V63 snapshot and may not replay or skip optimizer steps. Recovery files remain local and outside Git.

## Dense Trace Contract

Trace at exactly:

```text
step 0, 1, 2, 3, 5, 10, 15, 20, 30, 50, 100, 150, 200
```

For every optimizer step, record:

- variant, step, row ID, and target-box count;
- classification, bbox-regression, centerness, and total losses;
- matched foreground-anchor count and valid target count;
- LR, global gradient norm, finite flags, elapsed time, and CUDA memory;
- final bbox-output weight and bias gradient norms before the step;
- bbox-output weight and bias values after the step;
- regression-tower and detector-head gradient norms.

At every trace step, run compact no-grad geometry instrumentation on the frozen 32-row train subset and record by FPN level and aggregate:

- bbox pre-activation count, min, max, mean, standard deviation, fixed quantiles, and negative/zero/positive fractions;
- post-activation distance count, min, max, mean, fixed quantiles, positive fraction, and all-zero-location fraction;
- local activation derivative summaries: ReLU indicator `x > 0` for control and `sigmoid(x)` for Softplus, including all-location and matched-anchor derivative min/mean/quantiles and exact-zero fraction;
- decoded width/height summaries before and after clipping;
- valid, degenerate, non-finite, clipped, and out-of-image box counts;
- bbox-output weight/bias norms, extrema, signs, and deltas from initialization;
- bbox loss, matched-anchor counts, and classification/centerness summaries sufficient to keep the diagnosis geometry-focused.

At each trace step, use a fresh ephemeral copy of the current in-memory state for exactly one no-step backward probe on each of the four frozen gradient rows. Maximum diagnostic backward calls: **104 total** (`13 traces x 4 rows x 2 variants`). Record component losses, matched anchors, pre/post-activation summaries, activation-derivative summaries at matched anchors, bbox-output weight/bias gradient norms, regression-tower gradients, and finite/nonzero gradient fractions. Discard every ephemeral state. Probe work may not mutate persistent parameters, buffers, optimizer, RNG/order ledger, or recovery state.

At step 200, additionally run no-grad geometry instrumentation on the frozen 32-row devval subset through the split-agnostic trace path. Do not run the full 1,845-row devval set and do not compute AP/AR.

## Pre-registered State Definitions

At a trace step, classify a variant as `EARLY_BBOX_COLLAPSE` only when both conditions hold simultaneously:

1. the frozen 32-row train subset has zero positive-area decoded boxes after clipping; and
2. the final bbox-output weight and bias gradient norms are exactly zero on all four frozen gradient-probe rows.

Classify a trace as `GEOMETRY_AND_GRADIENT_PRESERVED` only when:

1. the frozen 32-row train subset has at least one positive-area decoded box after clipping; and
2. at least one frozen gradient-probe row has a finite nonzero final bbox-output weight or bias gradient.

Otherwise classify it as `NEITHER_PREREGISTERED_STATE`.

Record the first trace satisfying each state. Do not select a favorable trace or invent a post-hoc threshold.

## Frozen Decision Logic

Choose exactly one scientific outcome:

- `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`: control reaches `EARLY_BBOX_COLLAPSE` at or before step 50; Softplus never reaches collapse and is `GEOMETRY_AND_GRADIENT_PRESERVED` at step 200;
- `V63_RELU_AND_SOFTPLUS_BOTH_COLLAPSE`: both variants reach `EARLY_BBOX_COLLAPSE` by step 200;
- `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_MIXED`: control collapses, but Softplus satisfies neither the rescue nor collapse definition at step 200;
- `V63_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS`: control never reaches strict collapse within the frozen budget;
- `V63_BLOCKED_SOURCE_INITIALIZATION_OR_ACTIVATION_CONTRACT`;
- `V63_BLOCKED_TRAINING_TRACE_OR_RECOVERY_INCOMPLETE`;
- `V63_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`;
- `V63_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`.

A Softplus rescue outcome supports the hard zero-derivative ReLU path as a necessary contributing mechanism under this V57 training path. It does not prove that ReLU is the sole cause, does not establish final localization quality or AP/AR, and does not authorize a full 7,187-step run. If both variants collapse, the result points away from a ReLU-only explanation and toward matching, loss, optimization, or upstream representation mechanisms, but does not itself identify one.

## Stop Rules

Fail closed on:

- V62 evidence, manifests, order, subsets, or initialization mismatch;
- any historical V40-V62 or V51 evidence mutation;
- any paired tensor, parameter, buffer, state-dict, bias, or weight difference at step 0;
- Softplus parameters or source location differing from the frozen contract;
- activation applied only in training or only in inference rather than both;
- any loss, matching, anchor, scale, clipping, decode, threshold, NMS, preprocessing, architecture, fusion, or evaluator difference;
- alignment disabled, equal weights non-uniform, or reliability scorer activated;
- incorrect run order, repeated/substituted rows, more than 200 optimizer steps per variant, or more than 400 total steps;
- more than 104 diagnostic backward calls or use of unregistered samples;
- invalid recovery snapshots, replayed/skipped optimizer steps, or diagnostic mutation of persistent state;
- OOM or non-finite loss, gradient, parameter, alignment, activation, geometry, or recovery value;
- full-devval evaluation, AP/AR, tuning, early stopping, checkpoint selection, extra variant/seed, rerun, or automatic budget extension;
- production, manuscript/submission, protected-file, or heavy-artifact Git violation.

Do not automatically change activation parameters, bias, LR, optimizer, precision, batch size, resolution, loss, run length, sample order, trace schedule, or recovery policy after observing results.

## Required Outputs

Create `runs/v63_mmuav_paired_bbox_activation_rescue/` containing compact files such as:

```text
protocol.json
protocol.md
source_lock_v63.json
v62_evidence_verification.json
initialization_verification.json
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

Keep checkpoints, optimizer states, recovery snapshots, raw tensors, predictions, images, feature maps, and other heavy artifacts local and outside Git.

## Required Tests

Verify:

- exact V62 evidence, data, order, subset, and common-initialization hashes;
- exact first-200 order prefix and one use per row per variant;
- bit-identical paired step-0 states and pre-activation/non-bbox outputs;
- exact historical ReLU versus exact `softplus(beta=1.0, threshold=20.0)` as the only intervention;
- identical target matching, losses, anchors, scales, clipping, decode, threshold, NMS, and evaluator paths;
- dormant scorer, enabled alignment, and exact equal weights;
- actual `devval:00005919` trace-path preservation and unchanged train-only optimization guard;
- exact 200/200 run order and 400-step cap;
- exact trace schedule and at most 104 diagnostic backward calls;
- valid atomic recovery round trips and no replay/skipped steps;
- persistent training-state isolation from no-step probes;
- finite losses, gradients, activations, geometry, and recovery metadata;
- zero full-devval rows and no AP/AR, threshold selection, tuning, or checkpoint selection;
- unchanged V40-V62, V51, production, manuscript, and submission fingerprints;
- no heavy artifacts in Git.

Run CPU/source-lock tests before CUDA and post-run tests afterward. Save exact commands and outputs.

## Allowed Changes

- current task/status/blocker/handoff files;
- `runs/v63_mmuav_paired_bbox_activation_rescue/**`;
- V63-only experimental activation wrapper, runner, instrumentation, recovery utilities, and tests;
- minimal backward-compatible imports that do not change production defaults.

## Forbidden Changes

- modification of historical V40-V62 evidence or V51 history;
- modification, repair, resume, or initialization from trained V55-V62 checkpoints;
- production TriAir defaults or semantics;
- raw data or annotations;
- bbox bias/weight initialization changes or sweeps;
- loss, target, matcher, anchor, scale, clipping, decode, threshold, NMS, preprocessing, detector, evaluator, or fusion changes;
- reliability-fusion training;
- full 7,187-step training, full devval, AP/AR, tuning, checkpoint selection, extra seeds/variants, or automatic extension;
- public derivatives, manuscript, submission, or public benchmark files.

## Completion State

Choose exactly one allowed V63 state, update `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, and the V63 handoff, then run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Commit Message

`exp: run V63 MM-UAV paired bbox activation rescue pilot`

## Final Report Requirements

Report starting/final commit SHAs; all source/data/order/subset/initialization hashes; exact activation source location and parameters; proof of step-0 state and pre-activation identity; per-variant optimizer/backward/recovery counts; all trace classifications and first-collapse/preservation steps; activation-derivative evidence; train and frozen-devval geometry at step 200; checkpoint hashes and local-only locations; finite/safety results; tests; protected-file status; reproducibility warnings; selected scientific outcome; and the strict no-full-run/no-AP claim boundary.
