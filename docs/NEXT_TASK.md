# Current Task

## Authorization

The user reported that V64 completed, was pushed, and the completion-state audit was executed. Under the standing automatic task-handoff workflow, the user authorizes **V65 MM-UAV seed-0 Softplus full-train and full-devval feasibility run** under the standing local/private-research-only rule.

V63 is frozen as `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`. V64 is frozen as `V64_SEED1_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS`. V64 therefore does not independently confirm a universal ReLU-collapse/Softplus-rescue contrast; instead it establishes initialization sensitivity in the bounded 200-step path. Both V63 and V64 nevertheless showed exact Softplus remained geometry-and-gradient preserved through step 200.

V65 is the first bounded transition from mechanism diagnostics to a paper-relevant performance signal. It runs one exact seed-0 equal-fusion Softplus model through the complete frozen 7,187-row training order and evaluates the final step-7,187 checkpoint exactly once on the full frozen 1,845-row devval manifest. V65 is a feasibility gate, not a final multi-seed method comparison.

No ReLU full run, reliability-fusion training, tuning, checkpoint selection, extra seed, rerun, manuscript claim, public release, redistribution, or external sharing is authorized.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization-base and V64 completion commit: `402eabb23896f7908b6a3eccd4d394d3ce41d487`.

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, this task, all V52-V64 evidence and handoffs, V57/V63/V64 model builders and runners, installed torchvision FCOS source, evaluator code, recovery utilities, and protected-file rules. Record the actual starting commit. Stop before CUDA on unexpected repository changes, evidence mismatch, source-lock mismatch, or evaluator-contract mismatch. V51 remains untouched.

## Frozen Prior Evidence

Reproduce without modifying historical evidence:

- V63 completion commit: `83bb9351a5d0a6115d81047482e23fef5eed26bb`;
- V63 outcome: `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`;
- V64 completion commit: `402eabb23896f7908b6a3eccd4d394d3ce41d487`;
- V64 outcome: `V64_SEED1_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS`;
- V57/V63 seed-0 common initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- V64 seed-1 common initialization SHA256: `50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476`;
- V63 Softplus preserved at every scheduled trace through step 200;
- V64 ReLU and Softplus both preserved at every scheduled trace through step 200;
- installed torchvision FCOS source SHA256 and exact activation location must match the V63/V64 source-lock records;
- exact Softplus intervention remains `torch.nn.functional.softplus(x, beta=1.0, threshold=20.0)` in the shared training/inference bbox-distance path.

V63, V64, and all earlier evidence are read-only. Do not resume, repair, pool, relabel, select, or initialize from any trained V55-V64 checkpoint.

## Frozen Data, Initialization, and Order

Use exactly:

- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- devval manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- train/devval rows: `7,187 / 1,845`;
- train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- historical V57 sample order: `runs/v57_mmuav_paired_fusion_ablation/shared_sample_order.txt`;
- historical order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`;
- exact V57/V63 seed-0 common initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- frozen 32-row train geometry subset SHA256: `d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`;
- frozen four-row gradient subset SHA256: `bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`;
- frozen 32-row devval geometry subset SHA256: `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`;
- RGB boxes as the sole detector targets.

Materialize and hash all exactly 7,187 entries of the frozen historical V57 order before model construction. Use each row exactly once, in order. Do not reshuffle, repeat, substitute, truncate, or extend rows.

Reconstruct the exact historical seed-0 common initialization and reproduce its serialized SHA256 before training. Strictly load it into one fresh V65 model. Do not initialize from the V63 step-200 Softplus checkpoint or any other trained checkpoint.

## Frozen Model and Training Configuration

Use exactly the isolated V57 equal-superset path:

```text
independent RGB/IR/event stems
-> learned IR/event feature alignment to the RGB reference grid (enabled)
-> V57 superset with reliability scorer instantiated but bypassed
-> exact equal weights [1/3, 1/3, 1/3]
-> 1x1 projection to 3 channels
-> RepViT-M0.9-FPN-FCOS
-> exact Softplus bbox-distance activation
```

Configuration:

- seed `0`;
- input `320x320`;
- batch size `1`;
- FP32, AMP off;
- feature channels `32`;
- FPN channels `128`;
- RepViT-M0.9 without pretrained weights;
- exact `softplus(beta=1.0, threshold=20.0)` in both training and inference/decode;
- historical FCOS losses, target matching, anchors, scales, clipping, decode, threshold, top-k, NMS, preprocessing, and evaluator semantics unchanged;
- AdamW, LR `1e-4`, weight decay `1e-4`;
- no scheduler, gradient clipping, augmentation, workers, early stopping, checkpoint selection, hyperparameter search, or adaptive extension;
- alignment enabled;
- equal fusion exactly uniform;
- reliability scorer dormant and unchanged.

The only correction relative to the historical V57 path is the already source-locked parameter-free Softplus bbox-distance activation. Do not modify production defaults; use a V65-specific wrapper or the tested V63 wrapper.

## CPU and Source-Lock Gates Before CUDA

Before GPU work, tests must prove:

1. V63/V64 evidence, manifests, full historical order, subsets, and protected fingerprints match exactly;
2. the installed torchvision FCOS source and activation location match the frozen V63/V64 records;
3. Softplus is applied exactly once per FPN feature at the shared training/inference semantic location;
4. Softplus parameters are exactly `beta=1.0`, `threshold=20.0`;
5. the exact seed-0 common initialization is reconstructed, serialized, hashed, strictly reloaded, and matches the frozen SHA256;
6. step-0 state dictionaries, pre-activation bbox logits, classification logits, centerness logits, fused features, and alignment outputs match the V63 seed-0 contract on fixed inputs;
7. no bias, weight, loss, target, matcher, anchor, scale, clipping, decode, threshold, top-k, NMS, preprocessing, evaluator, fusion, or scorer field differs;
8. the train-only optimization target guard remains unchanged;
9. the split-agnostic trace/evaluation target path accepts actual frozen devval row `devval:00005919` without boxes/labels mutation;
10. the full-devval evaluator produces deterministic schema-complete metrics on a fixed synthetic or frozen micro-fixture without selecting thresholds or checkpoints;
11. atomic recovery snapshots round-trip model, optimizer, CPU/CUDA RNG, next sample position, completed step count, training log, trace ledger, and source/config hashes;
12. production and historical V40-V64/V51/manuscript/submission fingerprints remain unchanged.

Fail closed before CUDA on any mismatch.

## Frozen Run Budget

Run exactly one variant:

`v65_seed0_equal_softplus_b1_t20_fulltrain`

Train for exactly **7,187 optimizer steps**, consuming the frozen historical order exactly once. The final scientific checkpoint is the state immediately after optimizer step 7,187. No intermediate checkpoint may be selected by loss, geometry, or devval performance.

Save and round-trip verify local recovery snapshots immediately before the scheduled audits and additionally every 500 completed optimizer steps. Recovery is allowed only from the latest exact verified V65 snapshot, with no replayed or skipped rows or optimizer steps. Recovery snapshots, optimizer states, and checkpoints remain local and outside Git.

## Frozen Audit Schedule

Run compact train-geometry and four-row no-step gradient audits at exactly:

```text
step 0, 15, 50, 200, 500, 1000, 2000, 4000, 6000, 7187
```

Maximum diagnostic backward calls: **40 total** (`10 audits x 4 frozen rows`). Every probe must use a fresh ephemeral copy and must not mutate persistent model, optimizer, RNG, sample-order, recovery, or log state.

At each audit record:

- bbox pre-activation and post-activation distributions by FPN level and aggregate;
- Softplus local derivative summaries for all locations and matched anchors;
- decoded width/height and valid, degenerate, clipped, out-of-image, and non-finite box counts on the frozen 32-row train subset;
- classification, bbox-regression, centerness, and total losses;
- matched foreground anchors and valid targets;
- bbox-output weight/bias values and gradient norms;
- regression-tower and detector-head gradient norms;
- finite-state, elapsed-time, and CUDA-memory summaries;
- exact state-isolation and recovery-ledger hashes.

At step 7,187, additionally run the frozen 32-row devval geometry audit, then evaluate the final checkpoint exactly once on all 1,845 frozen devval rows.

## Full-Devval Evaluation Contract

Compute and report the repository's frozen COCO-style detection metrics without threshold tuning or checkpoint selection, including at minimum:

- AP@[0.50:0.95];
- AP50;
- AP75;
- AR@1;
- AR@10;
- AR@100;
- evaluated image and ground-truth counts;
- prediction count, zero-prediction image count, and non-finite prediction count;
- fixed evaluator configuration and source hash;
- elapsed evaluation time and peak memory.

Use only the final step-7,187 checkpoint. Do not inspect full-devval metrics before training completes. Do not alter score thresholds, NMS, max detections, IoU settings, preprocessing, or checkpoint choice after observing results.

## Frozen Decision Logic

Choose exactly one outcome:

- `V65_FULLTRAIN_COMPLETE_NONZERO_AP`: all 7,187 steps and final full-devval evaluation complete, all required safety checks pass, and AP@[0.50:0.95] is finite and greater than zero;
- `V65_FULLTRAIN_COMPLETE_ZERO_AP`: all 7,187 steps and evaluation complete safely, but AP@[0.50:0.95] equals zero;
- `V65_FULLTRAIN_BBOX_COLLAPSE`: strict zero-valid-geometry and zero-bbox-output-gradient collapse is observed on two consecutive scheduled audits;
- `V65_BLOCKED_SOURCE_INITIALIZATION_OR_EVALUATOR_CONTRACT`;
- `V65_BLOCKED_TRAINING_TRACE_OR_RECOVERY_INCOMPLETE`;
- `V65_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`;
- `V65_BLOCKED_FULL_DEVVAL_EVALUATION`;
- `V65_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`.

A nonzero AP outcome establishes only that the frozen seed-0 equal-fusion Softplus path can complete one full training pass and produce a measurable full-devval result. It does not establish superiority over ReLU, reliability fusion, a static-fusion control, other seeds, an independent test set, or external datasets. It does not authorize a manuscript performance claim by itself.

## Stop Rules

Fail closed on:

- any V63/V64 evidence, data, order, subset, source, initialization, or protected-file mismatch;
- initialization from a trained checkpoint;
- any activation parameter or semantic-location mismatch;
- any loss, matcher, anchor, scale, clipping, decode, threshold, NMS, preprocessing, architecture, alignment, fusion, scorer, or evaluator change;
- any reshuffle, repeated/substituted row, replayed/skipped step, or step count above 7,187;
- more than 40 diagnostic backward calls or unregistered probe rows;
- invalid recovery round trip or diagnostic mutation of persistent state;
- OOM or non-finite loss, gradient, parameter, activation, alignment, geometry, prediction, metric, or recovery value;
- any full-devval evaluation before the final checkpoint;
- tuning, threshold selection, checkpoint selection, extra variant/seed, rerun, automatic extension, or reliability-fusion training;
- heavy artifacts entering Git.

If strict bbox collapse is observed at two consecutive scheduled audits, stop training and record `V65_FULLTRAIN_BBOX_COLLAPSE`; do not modify the activation, optimizer, LR, precision, batch size, resolution, loss, order, or audit schedule.

## Required Outputs

Create `runs/v65_mmuav_seed0_softplus_fulltrain_feasibility/` containing compact files such as:

```text
protocol.json
protocol.md
source_lock_v65.json
v63_v64_evidence_verification.json
initialization_verification.json
full_train_order_sha256.txt
audit_schedule.json
training_config.json
training_log.csv
geometry_audits.json
gradient_audits.json
activation_derivative_summary.json
recovery_ledger.json
final_checkpoint_metadata.json
full_devval_evaluator_contract.json
full_devval_metrics.json
prediction_safety_summary.json
memory_timing_summary.json
safety_audit.json
test_commands.txt
test_output.txt
final_decision.json
handoff.md
```

Keep checkpoints, optimizer states, recovery snapshots, initialization artifacts, raw predictions, tensors, images, feature maps, and other heavy artifacts local and outside Git.

## Required Tests

Verify:

- exact prior evidence and protected-file immutability;
- exact manifests, full historical order, subset hashes, and seed-0 initialization hash;
- exact source-locked Softplus activation and call count;
- unchanged model, loss, matching, decode, evaluator, alignment, equal-fusion, and dormant-scorer contracts;
- exact 7,187-row one-pass order and optimizer-step count;
- exact audit schedule and 40-call diagnostic ceiling;
- valid recovery round trips with no replay or skipped rows;
- diagnostic isolation from persistent state;
- finite losses, gradients, parameters, activations, geometry, predictions, metrics, and recovery metadata;
- final-checkpoint-only full-devval evaluation;
- zero tuning, threshold selection, checkpoint selection, extra variants/seeds, reruns, or automatic extensions;
- no heavy artifacts in Git.

Run all CPU/source-lock/evaluator-contract tests before CUDA and post-run tests afterward. Save exact commands and outputs.

## Allowed Changes

- current task/status/blocker/write-record and V65 handoff files;
- `runs/v65_mmuav_seed0_softplus_fulltrain_feasibility/**`;
- V65-only full-training runner, evaluator wrapper, audit instrumentation, recovery utilities, and tests;
- minimal backward-compatible imports that do not change production defaults.

## Forbidden Changes

- historical V40-V64 evidence or V51 history;
- production TriAir defaults or semantics;
- raw data or annotations;
- ReLU full training, reliability-fusion training, activation/bias/optimizer/loss sweeps;
- loss, target, matcher, anchor, scale, clipping, decode, threshold, NMS, preprocessing, detector, evaluator, alignment, fusion, or scorer changes;
- devval-based tuning, early stopping, checkpoint selection, additional seeds/variants, reruns, or automatic extension;
- public derivatives, manuscript, submission, or benchmark files.

## Completion State

Choose exactly one allowed V65 state, update `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, and the V65 handoff, then run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Commit Message

`exp: run V65 MM-UAV seed0 Softplus full-train devval feasibility`

## Final Report Requirements

Report starting/final commit SHAs; V63/V64 evidence verification; source/data/order/subset/initialization/evaluator hashes; exact model and activation contract; training and recovery counts; every scheduled audit classification; geometry and derivative evidence; final train/devval geometry; full-devval AP/AR and prediction-safety metrics; checkpoint hash and local-only location; timing/memory and finite-state results; test and protected-file status; reproducibility warnings; selected bounded V65 outcome; and the strict single-seed/equal-fusion/no-comparative-claim boundary.
