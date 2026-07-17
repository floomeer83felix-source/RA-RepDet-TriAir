# Current Task

## Authorization

The user authorizes **V60 MM-UAV V57 bbox-regression collapse provenance audit** under the standing local/private-research-only rule.

V59 directly established that both V57 fusion checkpoints produce finite, above-threshold foreground tensors but only degenerate decoded boxes, while the V55 alignment-on reference produces positive-area boxes through the same score, post-processing, and evaluator path. V60 must determine whether the V57 bbox collapse was already present at initialization, was induced during training, reflects a dead-ReLU gradient trap, or remains unresolved.

V60 is a diagnostic audit. It authorizes **zero optimizer steps** and no checkpoint repair. It does not authorize retraining, fine-tuning, parameter updates, threshold/NMS/evaluator changes, architecture changes, new seeds, metric replacement, manuscript edits, public claims, redistribution, or external sharing.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Treat the V59 completion commit at the current branch head as the prerequisite evidence base. Read `AGENTS.md`, project/status/blocker/task/handoff files, all V52-V59 evidence, V55/V57 model builders and runners, V55/V57 training logs and configs, torchvision FCOS regression-head/loss code, and protected-file rules. Record the actual starting commit. Stop on unexpected repository changes or source-lock mismatch. V51 remains untouched.

## Frozen V59 Evidence

Reproduce without modifying historical evidence:

- V59 status: `V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED`;
- direct mechanism: `V57_BBOX_REGRESSION_DEGENERATE_GEOMETRY`;
- V57 equal valid/degenerate decoded candidates: `0 / 5,534,979`;
- V57 reliability valid/degenerate decoded candidates: `0 / 5,535,000`;
- V55 reference valid/degenerate decoded candidates: `5,535,000 / 0`;
- V57 equal/reliability/V55 maximum-score medians: `0.34743 / 0.33545 / 0.35583`;
- every model retained all foreground candidates above the frozen `0.001` threshold before top-k;
- V57 bbox-regression biases were non-positive and feed torchvision's ReLU distance head; V55 final bbox-regression biases were positive;
- V59 optimizer/backward/training/gradient executions were `0 / 0 / 0 / 0`.

V59 evidence is read-only. V60 must not reinterpret zero-area boxes as valid detections or modify V57 metrics.

## Frozen Data, Initializations, and Checkpoints

Use exactly:

- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- devval manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- train/devval rows: `7,187 / 1,845`;
- train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- V55 common seed-0 initialization SHA256: `91fec577380f895c932ffeb090bba7d376abc1ea1d97d568ae46901a7bbcb983`;
- V57 common seed-0 superset initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- V55 final alignment-on checkpoint SHA256: `2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258`;
- V57 equal final checkpoint SHA256: `d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142`;
- V57 reliability final checkpoint SHA256: `b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df`.

All three final checkpoints are required locally and must be verified read-only. Reconstruct the V55 and V57 seed-0 initial states using the exact historical builders, construction order, seed handling, and configuration. Their serialized state hashes must reproduce exactly before model probes. If an exact historical initialization cannot be reconstructed, fail closed rather than substituting a new initialization.

## Frozen Sample Sets

Before reading model outputs, derive and hash:

1. a deterministic 32-row train audit subset using seed 60 and the frozen train manifest;
2. a deterministic 4-row gradient-probe subset equal to the first four ordered rows of that frozen 32-row subset;
3. reuse the V59 frozen 32-row devval subset, seed/count/SHA256 `58 / 32 / d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`, for final-checkpoint no-grad geometry comparison.

Do not change any subset after observing outputs. RGB boxes remain the sole detector targets.

## Audit Questions

V60 must determine, as far as direct evidence permits:

1. whether V55 and V57 detector/bbox-head initial states differ because model-construction order consumes RNG differently;
2. whether either reconstructed initial state already produces all-zero ReLU bbox distances or degenerate boxes;
3. whether V57 begins with usable positive bbox distances but collapses during the 7,187-step run;
4. whether historical V55/V57 logs show different bbox-loss trajectories, zero-loss plateaus, gradient behavior, or first-collapse timing;
5. whether a no-step loss/gradient probe confirms a dead-ReLU trap in V57 initial or final states;
6. whether the equal and reliability V57 variants share the same collapse mechanism;
7. whether another loss, target, parameter-loading, or construction-path difference explains the collapse;
8. whether provenance remains unresolved because historical evidence is insufficient.

## Historical Source and Log Audit

Source-lock and compare:

- V55 and V57 model construction order and RNG seeding;
- the point at which stems, aligners, fusion scorer, detector projection, backbone/FPN, and FCOS heads are instantiated;
- parameter names/shapes and initialization routines for FCOS classification, centerness, and bbox-regression heads;
- the exact bbox distance activation and loss/decode path;
- optimizer parameter inclusion and weight-decay treatment;
- V55/V57 training-log schemas and all available per-step loss components, learning rates, finite flags, and gradient fields.

Record RNG-state hashes immediately before and after construction of the multimodal front end, reliability scorer, detector, and bbox-regression head for both reconstructed historical paths. Do not reorder construction to make hashes match.

Parse the complete committed V55 and V57 training logs. When bbox-specific losses or gradients are present, report exact first/last/min/max, selected frozen step summaries, zero/non-finite counts, and the earliest sustained collapse signal. When a requested field was not historically logged, record the absence explicitly and do not fabricate it.

## Initialization and Final-State Geometry Probe

For these five states:

1. reconstructed V55 seed-0 initialization;
2. reconstructed V57 seed-0 superset initialization in equal-bypass mode;
3. V55 final alignment-on checkpoint;
4. V57 final equal-superset checkpoint;
5. V57 final reliability-superset checkpoint;

run no-grad forward instrumentation on the frozen 32-row train subset and, for final states, also the frozen 32-row V59 devval subset.

Record by FPN level and aggregate:

- bbox-regression pre-ReLU logits: count, min, max, mean, standard deviation, and fixed quantiles on bounded compact summaries;
- fraction `<0`, `=0`, and `>0` before ReLU;
- post-ReLU distance positive fraction and all-zero-location fraction;
- decoded box width/height distributions before clipping and after clipping;
- valid, degenerate, non-finite, clipped, and out-of-image counts;
- bbox-head weight/bias norms, signs, extrema, and parameter deltas from exact initialization;
- classification and centerness score summaries sufficient to confirm the audit remains geometry-focused.

Do not compute AP/AR or alter score thresholds.

## Bounded No-Step Gradient Probe

V60 authorizes diagnostic backward computation but **no optimizer construction or optimizer step**.

Use fresh ephemeral model instances for the same five states and the fixed four-row gradient subset. For each state:

- load or reconstruct the state, snapshot parameter and buffer hashes, and clear gradients;
- use the historical training loss path with targets and the historical configuration;
- perform exactly one backward probe per row, for at most four backward calls per state and at most twenty backward calls total;
- record total and component losses, bbox-regression output positive fraction, bbox-head weight/bias gradient norms, detector-head gradient norms, and the fraction of bbox parameters receiving nonzero finite gradients;
- record whether zero ReLU outputs coincide with zero bbox gradients;
- discard the ephemeral instance after the probe.

No model state from a probe may be saved or reused. Checkpoint files must remain byte-identical. In-memory BatchNorm or other buffer changes inside an ephemeral probe instance are permitted only when required by the historical loss path; snapshot them, report them, discard the instance, and never persist them. Parameter values must remain unchanged before versus after backward.

## Root-Cause Refinement

Choose one primary classification:

- `V57_COLLAPSE_PRESENT_AT_INITIALIZATION`;
- `V57_TRAINING_INDUCED_DEAD_RELU_COLLAPSE`;
- `V57_CONSTRUCTION_ORDER_RNG_SHIFT_CONTRIBUTED`;
- `V57_LOSS_OR_GRADIENT_PATH_MISMATCH`;
- `V57_CHECKPOINT_OR_LOG_PROVENANCE_MISMATCH`;
- `V57_BBOX_COLLAPSE_PROVENANCE_UNRESOLVED`.

Supporting secondary factors may be recorded. A construction-order RNG difference alone is not causal unless the output/gradient probes link it to the bbox geometry. A dead-ReLU mechanism is confirmed only when non-positive pre-ReLU distances, zero post-ReLU distances, and absent bbox gradients are directly observed together.

## Stop Rules

Fail closed on:

- V59 evidence, data, subset, initialization, checkpoint, or historical-log mismatch;
- inability to reconstruct exact committed initial states;
- checkpoint or source mutation;
- any optimizer construction or optimizer step;
- more than twenty backward probes or use of rows outside the frozen subsets;
- parameter changes during a no-step probe;
- non-finite values that prevent interpretation;
- AP/AR computation, threshold selection, retraining, repair, or architecture/evaluator modification;
- production, V40-V59 evidence, V51, manuscript, or heavy-artifact violation.

Do not automatically initialize a positive bbox bias, replace ReLU, add loss terms, resume V57, or start a corrected run. V60 diagnoses provenance only.

## Required Outputs

Create `runs/v60_mmuav_bbox_collapse_provenance_audit/` containing compact files such as:

```text
protocol.json
protocol.md
source_lock_v60.json
v59_evidence_verification.json
checkpoint_verification.json
initialization_reconstruction.json
rng_construction_trace.json
train_audit_subset.txt
train_audit_subset_sha256.txt
gradient_probe_subset.txt
gradient_probe_subset_sha256.txt
historical_log_schema.json
historical_loss_trajectory.json
parameter_init_final_diff.json
bbox_geometry_probe.json
no_step_gradient_probe.json
root_cause_refinement.json
root_cause_refinement.md
safety_audit.json
test_commands.txt
test_output.txt
final_decision.json
```

Commit only compact metadata, hashes, statistics, and summaries. Checkpoints, raw tensors, predictions, images, feature maps, serialized model states, and other heavy artifacts remain local and outside Git.

## Required Tests

Verify:

- exact V59 evidence, data, initialization, checkpoint, and historical-log source locks;
- deterministic train and gradient subsets;
- exact historical initialization reconstruction and state hashes;
- RNG tracing does not alter construction behavior;
- geometry instrumentation matches torchvision's actual bbox activation/decode path;
- five state probes use only frozen rows;
- optimizer construction/steps remain zero;
- backward calls do not exceed twenty and parameters remain unchanged;
- checkpoint hashes remain unchanged before/after;
- no AP/AR, threshold selection, retraining, or repair path exists;
- production TriAir, V40-V59 evidence, V51, manuscript, and submission files remain unchanged;
- heavy artifacts remain outside Git.

Run CPU/source-lock tests before any CUDA probe and save exact commands and outputs.

## Allowed Changes

- current task/status/blocker/handoff files;
- `runs/v60_mmuav_bbox_collapse_provenance_audit/**`;
- V60-only read-only audit, instrumentation, and tests;
- minimal backward-compatible imports needed for instrumentation without changing defaults.

## Forbidden Changes

- checkpoint modification or repaired checkpoints;
- optimizer construction/steps, training, fine-tuning, or resumed V57 runs;
- raw data or annotations;
- historical V40-V59 evidence except current pointers;
- V51 history;
- production defaults or TriAir semantics;
- bbox-bias initialization changes, ReLU replacement, new losses, threshold/NMS/evaluator changes;
- AP/AR recomputation or metric replacement;
- public derivatives, manuscript, submission, or public benchmark files.

## Completion State

Choose exactly one:

- `V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_MECHANISM_IDENTIFIED`;
- `V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_CAUSE_UNRESOLVED`;
- `V60_BLOCKED_SOURCE_INITIALIZATION_OR_CHECKPOINT_CONTRACT`;
- `V60_BLOCKED_AUDIT_OR_GRADIENT_INSTRUMENTATION`;
- `V60_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`.

A successful audit does not authorize checkpoint repair, retraining, positive-bias initialization, activation changes, extra evaluation, or manuscript claims. Any corrective experiment requires a separate task.

Update status, blocker, and handoff files, then run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Commit Message

`diag: audit V57 bbox-regression collapse provenance`

## Final Report Requirements

Report starting/final commit SHAs; all source, data, subset, initialization, checkpoint, and log hashes; exact reconstruction and RNG traces; historical loss-field availability and trajectories; initialization/final bbox parameter differences; all geometry and no-step gradient probes; optimizer/backward counts; checkpoint/parameter immutability; root-cause refinement with direct evidence; tests and protected-file results; unresolved limitations; and the next authorization boundary.