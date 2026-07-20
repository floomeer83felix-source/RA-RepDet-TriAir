# Current Task

## Authorization

The user explicitly authorizes **V62 MM-UAV clean bbox-bias paired rerun** under the standing local/private-research-only rule and selects V61 blocker repair option 2.

V61 remains permanently closed as `V61_BLOCKED_TRAINING_OR_TRACE_INCOMPLETE`. Its 500-step control log is partial diagnostic-only evidence and must not be converted into a paired result, resumed, repaired in place, or combined with V62.

V62 is a newly numbered clean pilot. It must first correct and test the devval trace target-transfer path, then rerun the complete paired 500+500 protocol from the exact historical V57 seed-0 common initialization.

V62 compares exactly two alignment-on, equal-fusion V57-superset variants:

1. `v62_equal_control_instrumented`: exact historical V57 seed-0 common initialization and behavior;
2. `v62_equal_bbox_bias_p001`: the same initial state, except the four-element final FCOS bbox-regression output bias is set once to exactly `+0.01` before training.

The sole scientific intervention is the initial four-element bbox-output bias. V62 does not authorize a bias sweep, reliability-fusion training, activation or loss changes, full 7,187-step training, full-devval evaluation, AP/AR, tuning, manuscript edits, public claims, redistribution, or external sharing.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Treat the current branch head containing the V61 blocked report as the authorization evidence base. Record the actual starting commit before changes.

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, this task, all V52-V61 evidence and handoffs, the V55/V57/V61 builders and runners, the V57 shared sample order, torchvision FCOS regression/loss/decode code, and protected-file rules. V51 remains untouched.

## Frozen V61 Blocked Evidence

Reproduce without modifying historical evidence:

- V61 state: `V61_BLOCKED_TRAINING_OR_TRACE_INCOMPLETE`;
- failed variant/phase: `v57_equal_control_instrumented` / step-500 frozen devval geometry trace;
- failed row: `devval:00005919`;
- exception: `RuntimeError: Invalid optimization sample: devval:00005919`;
- control/intervention optimizer steps: `500 / 0`;
- diagnostic backward calls: `44`;
- control training-log rows: `500`;
- control training-log SHA256: `a96e0260079cbd05fd62fcc184a6908476490c42ecebe9b44373af4aebfd0965`;
- checkpoint or exact recovery snapshot: none;
- common V57 initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- protected fingerprint unchanged.

V61 partial observations may be cited only as blocked diagnostic context. They may not be pooled with V62, used for checkpoint initialization, used to skip the V62 control run, or reported as a prevention result.

## Required Trace-Path Correction

The V61 failure arose because inference-only geometry tracing reused the optimization-only `target_to_device()` helper, which requires `split == "train"`.

V62 must implement a V62-local or clearly trace-specific split-agnostic target tensor mover with these properties:

- accepts both frozen `train:` and `devval:` samples;
- moves only `target_rgb["boxes"]` and `target_rgb["labels"]` to the requested device;
- preserves shape, dtype, values, label semantics, and row identity;
- does not require a non-empty target for inference-only/no-grad geometry tracing;
- performs no augmentation, filtering, coordinate conversion, target rewriting, or optimization eligibility decision.

The historical optimization helper must remain train-only and must still reject devval rows when called by a training path. Do not weaken training-data safeguards globally.

Before CUDA training, add and pass CPU tests that:

1. use the actual frozen V61 failing row `devval:00005919`;
2. prove the trace-specific mover accepts it and preserves boxes/labels exactly;
3. prove the historical optimization helper still rejects the same devval row;
4. execute the complete V62 step-500-style no-grad geometry call chain on at least one actual frozen train row and the actual frozen devval row using a bounded CPU-compatible fixture or source-locked test double;
5. prove no optimizer construction, parameter mutation, threshold selection, AP/AR path, or split leakage is introduced.

Stop before CUDA if any correction or test contract fails.

## Frozen Data, Initialization, and Order

Use exactly:

- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- train rows: `7,187`;
- train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- RGB boxes as the sole detector targets;
- historical V57 shared sample order: `runs/v57_mmuav_paired_fusion_ablation/shared_sample_order.txt`;
- historical order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`;
- exact first 500 entries of that order, materialized and hashed before model construction;
- V57 common seed-0 superset initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- V60 frozen 32-row train audit subset SHA256: `d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`;
- V60 frozen four-row gradient subset SHA256: `bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`;
- V59 frozen 32-row devval subset SHA256: `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.

Both variants must use the identical 500-row prefix exactly once and in the same order. Do not substitute, reshuffle, repeat, truncate, or extend rows after observing results.

Reconstruct the exact common initialization before either run and verify its serialized SHA256. Create one independent in-memory copy per variant. For the intervention copy, locate the actual final FCOS bbox-regression output bias, verify that it contains exactly four finite elements, and set only those values to exact `+0.01`. Record the parameter name, original values, new values, delta, and intervention-state hash. Every other tensor must be bit-identical to the control initial state.

Do not initialize from V55, V57 final, V61 partial state, or any trained checkpoint.

## Frozen Architecture and Configuration

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

- seed `0`;
- input `320x320`;
- batch size `1`;
- FP32, AMP off;
- feature channels `32`;
- FPN channels `128`;
- RepViT-M0.9 without pretrained weights;
- historical FCOS loss and decode paths unchanged;
- AdamW, LR `1e-4`, weight decay `1e-4`;
- no scheduler, clipping, augmentation, workers, early stopping, checkpoint selection, or hyperparameter search;
- alignment enabled in both variants;
- equal fusion active and exactly uniform in both variants;
- reliability scorer dormant in both variants.

The only permitted paired scientific difference is the initial four-element bbox-output bias.

## Frozen Run Order and Budget

Run exactly, in order:

1. `v62_equal_control_instrumented` — exactly 500 optimizer steps;
2. `v62_equal_bbox_bias_p001` — exactly 500 optimizer steps.

V62 optimizer-step ceiling is **1,000 total**, exactly 500 per variant. Both variants are required for valid evidence. Control collapse does not permit early stopping or skipping the intervention.

This authorization explicitly permits repeating the 500 control steps consumed by blocked V61 because V62 is a new clean paired task. V61 artifacts remain immutable and are not reused.

## Technical Recovery Contract

To prevent a trace-only failure from consuming an unrecoverable trained state, immediately before every scheduled trace write an atomic local technical recovery snapshot containing:

- model state;
- optimizer state;
- completed optimizer-step count;
- next sample-order position;
- CPU, CUDA, NumPy, and Python RNG states;
- current training-log row count and SHA256;
- variant name, source commit, configuration hash, initialization hash, and trace step;
- trace-ledger completion state.

Write to a temporary path, fsync/close where supported, atomically rename, then reload and verify the snapshot before starting the trace. Recovery snapshots stay under a V62 local-only directory and outside Git.

A technical restart is allowed only from the latest byte-verified V62 snapshot after a purely technical crash. It must reproduce the exact step, order index, optimizer, RNG, log, and trace ledger without replaying or skipping optimizer steps. Report every recovery. No result-based rerun, checkpoint selection, or restart from V61 is allowed.

If no valid exact snapshot exists, fail closed.

## Dense Instrumentation Contract

Trace the frozen states at:

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
- valid, degenerate, non-finite, clipped, and out-of-image counts;
- bbox-output weight/bias norms, extrema, signs, and deltas from initialization;
- bbox loss and matched-anchor statistics;
- classification/centerness summaries only as needed to confirm geometry-specific behavior.

At each trace step, use a fresh ephemeral copy of the current state for one no-step backward probe on each of the exact four frozen gradient rows. This authorizes at most **96 diagnostic backward calls total**: 12 trace states x 4 rows x 2 variants. Record component losses, matched anchors, bbox pre/post-ReLU statistics, final bbox-output weight/bias gradient norms, and the fraction of finite nonzero bbox gradients. Discard the ephemeral state after each trace. Probe calls may not alter the persistent training model, optimizer, RNG/order ledger, or buffers.

At step 500, additionally run the corrected no-grad geometry path on the frozen 32-row devval subset. Do not run all 1,845 devval rows and do not compute AP/AR.

## Pre-registered State Definitions

At a trace step, classify a variant as `EARLY_BBOX_COLLAPSE` only when both hold simultaneously:

1. the frozen 32-row train subset has zero positive-area decoded boxes after clipping;
2. final bbox-output weight and bias gradient norms are exactly zero on all four frozen gradient-probe rows.

Classify a trace as `GEOMETRY_AND_GRADIENT_PRESERVED` only when both hold:

1. the frozen 32-row train subset has at least one positive-area decoded box after clipping;
2. at least one frozen gradient-probe row has a finite nonzero final bbox-output weight or bias gradient.

Record the first trace step meeting either state. Do not invent an intermediate threshold or select a favorable trace after execution.

## Frozen Decision Logic

Choose exactly one scientific outcome:

- `V62_CONTROL_COLLAPSE_REPRODUCED_POSITIVE_BIAS_PREVENTS_THROUGH_STEP500`;
- `V62_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE`;
- `V62_CONTROL_COLLAPSE_REPRODUCED_INTERVENTION_RESULT_MIXED`;
- `V62_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_500_STEPS`;
- `V62_BLOCKED_SOURCE_INITIALIZATION_ORDER_OR_TRACE_FIX_CONTRACT`;
- `V62_BLOCKED_TRAINING_TRACE_OR_RECOVERY_INCOMPLETE`;
- `V62_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`;
- `V62_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`.

A prevention outcome is an early-step, single-seed engineering result only. It does not establish final accuracy, reliability-fusion benefit, statistical confirmation, or authorization for a full 7,187-step run.

## Stop Rules

Fail closed on:

- V61 evidence, data, order, subset, or initialization mismatch;
- any modification of V61 blocked evidence;
- a trace mover that weakens the train-only optimization guard;
- inability to execute the actual frozen devval row through the corrected trace path before CUDA;
- any initial paired tensor difference beyond the exact four-element bias intervention;
- a bias value other than `+0.01`, a sweep, or post-start intervention change;
- alignment disabled, non-uniform equal fusion, or reliability scorer activation;
- incorrect run order, repeated/substituted rows, more than 500 steps per variant, or more than 1,000 total optimizer steps;
- more than 96 diagnostic backward calls or use of unregistered samples;
- trace/probe/recovery mutation of persistent training state or an unverified recovery snapshot;
- OOM or non-finite loss, gradient, parameter, alignment, geometry, or diagnostic value;
- full-devval evaluation, AP/AR, threshold selection, checkpoint selection, tuning, or automatic budget extension;
- protected-file changes or heavy artifacts entering Git.

Do not automatically change the bias, LR, optimizer, precision, batch size, resolution, activation, loss, run length, sample order, trace schedule, or recovery policy after observing behavior.

## Required Outputs

Create `runs/v62_mmuav_clean_bbox_bias_paired_rerun/` containing compact files such as:

```text
protocol.json
protocol.md
source_lock_v62.json
v61_blocked_evidence_verification.json
trace_target_transfer_fix.json
initialization_verification.json
intervention_delta.json
train_prefix_500.txt
train_prefix_500_sha256.txt
trace_schedule.json
per_variant_config.json
per_variant_training_log.csv
per_variant_trace_geometry.json
per_variant_trace_gradient.json
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

- exact V61 blocked evidence, data, historical order, subsets, and initialization hashes;
- V61 files and partial log remain byte-identical;
- actual `devval:00005919` passes the trace-specific target mover with exact target preservation;
- the historical optimization helper still rejects devval rows;
- the complete bounded train/devval geometry trace call chain passes before CUDA;
- exact first-500 order prefix and one use per row per variant;
- paired initial tensors differ only in the four-element bbox-output bias;
- intervention value is exact `+0.01`, with no sweep path;
- architecture/configuration identity and dormant scorer behavior;
- exact 500/500 run order and 1,000-step cap;
- atomic recovery snapshot round-trip and exact model/optimizer/RNG/order/log restoration;
- trace schedule, subset membership, and maximum 96 diagnostic backward calls;
- no persistent-state mutation by diagnostic probes;
- corrected step-500 frozen devval trace uses only 32 rows;
- no full-devval, AP/AR, threshold selection, tuning, or checkpoint selection path;
- checkpoint/recovery files remain local and outside Git;
- production TriAir, V40-V61 evidence, V51, manuscript, and submission files remain unchanged.

Run CPU/source-lock/trace-fix/recovery tests before CUDA and save exact commands and outputs.

## Allowed Changes

- current task/status/blocker and V62 handoff files;
- `runs/v62_mmuav_clean_bbox_bias_paired_rerun/**`;
- V62-only runner, trace-specific target transfer, atomic recovery utilities, and tests;
- minimal backward-compatible imports required for V62 instrumentation without changing defaults.

## Forbidden Changes

- modification or deletion of V61 blocked evidence;
- raw data or annotations;
- historical V40-V61 evidence except current pointers;
- V51 history;
- production defaults or TriAir semantics;
- global weakening of train-only target validation;
- bbox activation/loss changes, bias sweeps, threshold/NMS/evaluator changes;
- reliability-fusion training, extra variants/seeds, or full 7,187-step training;
- full-devval evaluation or AP/AR;
- public derivatives, manuscript, submission, or public benchmark files;
- checkpoints, optimizer states, recovery snapshots, predictions, tensors, or media in Git.

## Completion State

Choose exactly one state from the frozen V62 decision logic, update status, blocker, and handoff files, then run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Commit Message

`exp: run V62 clean bbox-bias paired rerun`

## Final Report Requirements

Report starting/final commit SHAs; V61 evidence and immutability hashes; trace-target correction and actual-devval-row tests; data/order/subset/initialization/intervention hashes; exact optimizer and backward counts; every trace state; first collapse/preservation state per variant; step-500 frozen train/devval geometry; recovery snapshot ledger and any recovery event; checkpoint metadata; timing/memory; numerical stability; tests; protected-file results; and the selected bounded V62 outcome with the no-AP/AR and no-full-training limitations.