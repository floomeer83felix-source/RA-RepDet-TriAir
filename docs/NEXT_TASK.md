# Current Task

## Authorization

The user authorizes **V61 MM-UAV early bbox-collapse prevention paired pilot** under the standing local/private-research-only rule.

V59 established that both V57 fusion checkpoints ended with all-degenerate bbox geometry. V60 then established that the V55 and V57 FCOS bbox heads were bit-identical at initialization and that usable V57 geometry existed initially, but the historical logs were too sparse to identify the first collapse step or a unique provenance mechanism. V61 therefore performs one bounded, densely instrumented corrective pilot before any full rerun.

V61 compares exactly two seed-0, alignment-on, equal-fusion V57-superset variants:

1. `v57_equal_control_instrumented`: exact historical V57 initialization and training behavior;
2. `v57_equal_bbox_bias_p001`: the same initial state, except the four-element final FCOS bbox-regression output bias is set once to exactly `+0.01` before training.

The single scientific intervention is the bbox-output bias initialization. V61 does not authorize a bias sweep, reliability-fusion training, activation or loss changes, full training, AP/AR evaluation, manuscript edits, public claims, redistribution, or external sharing.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization-base evidence commit: `8e3ac7151c9b70edd4631cfd6aabfdc359a1cc95`.

Read `AGENTS.md`, project/status/blocker/task/handoff files, all V52-V60 evidence, V55/V57 model builders and runners, V57 shared sample order, V60 initialization/geometry/gradient evidence, torchvision FCOS bbox-head/loss/decode code, and protected-file rules. Record the actual starting commit. Stop before CUDA work on unexpected repository changes or source-lock mismatch. V51 remains untouched.

## Frozen V60 Evidence

Reproduce without modifying historical evidence:

- V60 status: `V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_CAUSE_UNRESOLVED`;
- V55 and V57 seed-0 initialization SHA256: `91fec577380f895c932ffeb090bba7d376abc1ea1d97d568ae46901a7bbcb983` and `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- initial bbox-regression weights and biases were bit-identical;
- initial V55/V57 states produced `18,401 / 17,134` valid boxes on the frozen 32-row train subset, so collapse was absent at initialization;
- final V57 equal/reliability states produced `0 / 272,000` valid boxes on both frozen train and devval probes;
- final V57 bbox output-layer weight and bias gradients were zero on all four frozen probe rows;
- final V55 remained geometrically valid with nonzero bbox gradients;
- historical V57 equal/reliability bbox loss was exactly `1.0` on 4,726 / 4,725 target-bearing observations and never strictly between zero and one;
- V60 could not identify the exact first collapse step because historical bbox-output and bbox-parameter-gradient traces were absent.

V60 evidence is read-only. Do not relabel V57 as a successful fusion experiment or modify its historical metrics.

## Frozen Data, Initialization, and Order

Use exactly:

- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- train rows: 7,187;
- train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- RGB boxes as the sole detector targets;
- historical V57 shared sample order: `runs/v57_mmuav_paired_fusion_ablation/shared_sample_order.txt`;
- historical order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`;
- V57 common seed-0 superset initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- V60 frozen 32-row train audit subset SHA256: `d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`;
- V60 frozen four-row gradient subset SHA256: `bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`;
- V59 frozen 32-row devval subset SHA256: `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.

Train on exactly the first 500 entries of the frozen historical V57 order. Materialize and hash that 500-row prefix before model construction. Both variants must use the identical prefix exactly once and in the same order. Do not substitute, reshuffle, repeat, or extend rows after observing results.

Reconstruct the exact historical V57 common initialization before either run. Verify its serialized SHA256. Create one in-memory copy per variant. For the intervention copy, locate the actual final FCOS bbox-regression output bias from the source-locked model, verify it has exactly four finite elements, and set only those four values to `+0.01`. Record the parameter name, before/after values, delta, and intervention-state hash. Every other tensor must remain bit-identical to the control initial state.

Do not initialize from V55, V57 final, or any trained checkpoint.

## Frozen Architecture and Configuration

Use the isolated V57 equal-superset path:

```text
independent RGB/IR/event stems
-> learned IR/event feature alignment to RGB reference grid (enabled)
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
- FCOS historical loss and decode paths unchanged;
- AdamW, LR `1e-4`, weight decay `1e-4`;
- no scheduler, clipping, augmentation, workers, early stopping, checkpoint selection, or hyperparameter search;
- alignment always enabled;
- equal fusion always active and exactly uniform;
- reliability scorer dormant in both variants.

The only permitted paired difference is the four-element bbox-output bias at initialization.

## Frozen Run Order and Budget

Run exactly:

1. `v57_equal_control_instrumented` — 500 optimizer steps;
2. `v57_equal_bbox_bias_p001` — 500 optimizer steps.

V61 optimizer-step ceiling: **1,000 total**, exactly 500 per variant. An incomplete pair is not valid evidence. No restart from a partially trained checkpoint is allowed unless a purely technical crash-recovery snapshot preserves the exact next row, optimizer state, RNG state, and trace ledger; any such recovery must be reported. Final step-500 checkpoints remain local and outside Git.

## Dense Instrumentation Contract

Trace the frozen checkpoints/states at:

```text
step 0, 1, 2, 5, 10, 20, 50, 100, 200, 300, 400, 500
```

For every optimizer step, record:

- row ID and target-box count;
- classification, bbox-regression, centerness, and total losses;
- LR, global gradient norm, finite flags, time, and CUDA memory;
- matched foreground-anchor count and valid target count;
- final bbox-output weight and bias gradient norms before the step;
- final bbox-output bias values after the step.

At every trace step, run compact instrumentation on the frozen 32-row train subset and record by FPN level and aggregate:

- bbox pre-ReLU count, min, max, mean, standard deviation, fixed quantiles, and negative/zero/positive fractions;
- post-ReLU positive-distance fraction and all-zero-location fraction;
- decoded width/height summaries before and after clipping;
- valid, degenerate, non-finite, clipped, and out-of-image box counts;
- bbox-output weight/bias norms, extrema, signs, and deltas from initial state;
- bbox loss and matched-anchor statistics;
- classification/centerness summaries only as needed to confirm the failure remains geometry-specific.

At each trace step, use a fresh ephemeral copy of the current in-memory state for one no-step backward probe on each of the exact four frozen gradient rows. This authorizes at most **96 diagnostic backward calls** total: 12 trace states x 4 rows x 2 variants. Record component losses, matched anchors, bbox pre/post-ReLU statistics, final bbox-output weight/bias gradient norms, and the fraction of finite nonzero bbox gradients. Discard each ephemeral probe state. Probe calls may not alter the training model, optimizer, RNG/order ledger, or persistent buffers.

At step 500, additionally run no-grad geometry instrumentation on the frozen 32-row V59 devval subset. Do not run the full 1,845-row devval set and do not compute AP/AR.

## Pre-registered Collapse and Preservation Definitions

At a trace step, classify a variant as in `EARLY_BBOX_COLLAPSE` only when both conditions hold simultaneously:

1. the frozen 32-row train subset has zero positive-area decoded boxes after clipping; and
2. the final bbox-output weight and bias gradient norms are exactly zero on all four frozen gradient-probe rows.

Classify a trace as `GEOMETRY_AND_GRADIENT_PRESERVED` only when:

1. the frozen 32-row train subset has at least one positive-area decoded box after clipping; and
2. at least one frozen gradient-probe row has a finite nonzero final bbox-output weight or bias gradient.

Record the first trace step meeting either state. Do not invent an intermediate success threshold or select a favorable trace after the run.

## Frozen Decision Logic

Choose exactly one scientific outcome:

- `V61_CONTROL_COLLAPSE_REPRODUCED_POSITIVE_BIAS_PREVENTS_THROUGH_STEP500`: control first reaches `EARLY_BBOX_COLLAPSE`, while the intervention never reaches it and is `GEOMETRY_AND_GRADIENT_PRESERVED` at step 500;
- `V61_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE`: both variants reach `EARLY_BBOX_COLLAPSE` by step 500;
- `V61_CONTROL_COLLAPSE_REPRODUCED_INTERVENTION_RESULT_MIXED`: control collapses, but the intervention satisfies neither the prevention nor collapse definition at step 500;
- `V61_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_500_STEPS`: control never reaches the strict collapse definition within the frozen budget;
- `V61_BLOCKED_SOURCE_INITIALIZATION_ORDER_OR_INTERVENTION_CONTRACT`;
- `V61_BLOCKED_TRAINING_OR_TRACE_INCOMPLETE`;
- `V61_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`;
- `V61_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`.

A positive-bias prevention outcome is an early-step, single-seed engineering result only. It does not establish final accuracy, fusion benefit, statistical confirmation, or authorization for a full 7,187-step run.

## Stop Rules

Fail closed on:

- V60 evidence, data, order, subset, or initialization mismatch;
- any initial paired tensor difference beyond the four-element bbox-output bias;
- bias value other than exact `+0.01`, a bias sweep, or post-start intervention change;
- alignment disabled, non-uniform equal fusion, or reliability scorer activation;
- incorrect run order, repeated/substituted rows, more than 500 steps per variant, or more than 1,000 total optimizer steps;
- more than 96 diagnostic backward calls or use of samples outside the frozen subsets;
- probe mutation of training parameters, buffers, optimizer, RNG state, or checkpoints;
- OOM or non-finite loss, gradient, parameter, alignment, bbox geometry, or diagnostic value;
- full-devval evaluation, AP/AR computation, threshold selection, checkpoint selection, tuning, or automatic budget extension;
- protected-file changes or heavy artifacts entering Git.

Do not automatically change LR, optimizer, precision, batch size, resolution, bias value, activation, loss, training length, sample order, or trace schedule after observing results.

## Required Outputs

Create `runs/v61_mmuav_early_bbox_collapse_prevention/` containing compact files such as:

```text
protocol.json
protocol.md
source_lock_v61.json
v60_evidence_verification.json
initialization_verification.json
intervention_delta.json
train_prefix_500.txt
train_prefix_500_sha256.txt
trace_schedule.json
per_variant_config.json
per_variant_training_log.csv
per_variant_trace_geometry.json
per_variant_trace_gradient.json
per_variant_checkpoint_metadata.json
paired_trace_comparison.json
final_decision.json
memory_timing_summary.json
safety_audit.json
test_commands.txt
test_output.txt
```

Keep checkpoints, optimizer states, raw tensors, predictions, images, feature maps, and other heavy artifacts local and outside Git.

## Required Tests

Verify:

- exact V60 evidence, data, historical order, subsets, and initialization hashes;
- exact first-500 order prefix and one use per row per variant;
- paired initial tensors differ only in the four-element bbox-output bias;
- intervention value is exactly `+0.01` with no sweep path;
- architecture/configuration identity and dormant scorer behavior;
- exact 500/500 run order and 1,000-step cap;
- trace schedule completeness and at most 96 no-step probe backward calls;
- probe-state isolation and no persistent mutation;
- collapse/preservation classification follows the pre-registered definitions;
- no full-devval AP/AR, threshold selection, tuning, checkpoint selection, or automatic extension;
- production TriAir, V40-V60 evidence, V51 evidence, manuscript, and submission files remain unchanged;
- heavy artifacts stay outside Git.

Run CPU/source-lock tests before CUDA and save exact commands and outputs.

## Allowed Changes

- current task/status/blocker/handoff files;
- `runs/v61_mmuav_early_bbox_collapse_prevention/**`;
- V61-only paired runner, instrumentation, configuration, and tests;
- a V61-only backward-compatible wrapper needed to set and verify the experimental initial bias without changing historical or production defaults.

## Forbidden Changes

- modification of historical V40-V60 evidence;
- V51 history;
- production defaults or TriAir semantics;
- modification or repair of V57 checkpoints;
- reliability-fusion training;
- bias values other than `+0.01`, bias sweeps, activation replacement, new loss terms, threshold/NMS/evaluator changes;
- more than 1,000 optimizer steps, extra variants, seeds, reruns, tuning, full-devval evaluation, AP/AR, or checkpoint selection;
- raw data, annotations, checkpoints, predictions, serialized states, images, tensors, or feature maps in Git;
- public derivatives, manuscript, submission, or public benchmark files.

## Completion and Handoff

Update status, blocker, and handoff files, then run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Commit Message

`exp: run V61 early bbox-collapse prevention pilot`

## Final Report Requirements

Report starting/final commit SHAs; all evidence/data/order/subset/initialization hashes; the exact intervention tensor and delta; paired configuration identity; exact step, row, and backward-probe counts; dense bbox loss, matched-anchor, geometry, gradient, and bias trajectories; first collapse/preservation traces; checkpoint metadata; timing/memory/finite results; tests and protected-file results; CUDA reproducibility limitations; the selected frozen outcome; and the next authorization boundary.