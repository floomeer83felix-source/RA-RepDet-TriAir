# Current Task

## Authorization

The user reported that V65 completed and was pushed. Under the standing automatic task-handoff workflow, the user authorizes **V66 MM-UAV seed-1 equal-fusion Softplus full-train and full-devval confirmation run** under the standing local/private-research-only rule.

V65 is frozen as `V65_FULLTRAIN_COMPLETE_NONZERO_AP`. The exact seed-0 equal-fusion Softplus model completed all 7,187 optimizer steps, remained geometry-and-gradient preserved at all ten audits, and produced final-checkpoint-only full-devval AP@[0.50:0.95] `0.0363043928`, AP50 `0.1493416683`, AP75 `0.0035733839`, AR@1 `0.0501429252`, AR@10 `0.0753692234`, and AR@100 `0.0815388280`.

V66 performs the same complete run with the single frozen seed-1 common initialization from V64. Its purpose is to convert the V65 single-seed feasibility signal into a two-seed equal-fusion Softplus baseline before any reliability-fusion method comparison.

V66 does not authorize reliability-fusion training, ReLU full training, tuning, checkpoint selection, threshold selection, extra seeds, reruns, manuscript edits, public claims, redistribution, or external sharing.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization-base and V65 completion commit: `33609052b798a89fb8d3a1ab9351f8497e8f95d1`.

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, this task, all V52-V65 evidence and handoffs, V57/V63/V64/V65 model builders and runners, the installed torchvision FCOS source, evaluator code, recovery utilities, and protected-file rules. Record the actual starting commit. Stop before CUDA on any unexpected repository change, evidence mismatch, source-lock mismatch, seed-1 initialization mismatch, or evaluator-contract mismatch. V51 remains untouched.

## Frozen V65 Evidence

Verify without modifying:

- V65 completion commit: `33609052b798a89fb8d3a1ab9351f8497e8f95d1`;
- V65 outcome: `V65_FULLTRAIN_COMPLETE_NONZERO_AP`;
- V65 optimizer steps and unique ordered rows: `7,187 / 7,187`;
- V65 diagnostic backward calls: `40 / 40`;
- V65 verified recovery snapshots/recovery events: `19 / 0`;
- V65 full-devval evaluation attempts and rows: `1 / 1,845`;
- V65 AP@[0.50:0.95]: `0.0363043928`;
- V65 AP50: `0.1493416683`;
- V65 AP75: `0.0035733839`;
- V65 AR@1: `0.0501429252`;
- V65 AR@10: `0.0753692234`;
- V65 AR@100: `0.0815388280`;
- all ten V65 audits were `GEOMETRY_AND_GRADIENT_PRESERVED`;
- final compact train/devval geometry was `272,000 / 272,000` valid boxes on each subset;
- V65 post-run tests: `10 / 10` passed;
- no tuning, threshold selection, checkpoint selection, rerun, or extra seed/variant occurred.

V65 and all earlier evidence are read-only. Do not resume, repair, pool, relabel, select, or initialize V66 from any trained V55-V65 checkpoint.

## Frozen Data, Initialization, and Order

Use exactly:

- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- devval manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- train/devval rows: `7,187 / 1,845`;
- train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- historical V57 sample order: `runs/v57_mmuav_paired_fusion_ablation/shared_sample_order.txt`;
- historical order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`;
- exact V64 frozen seed-1 common initialization SHA256: `50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476`;
- frozen 32-row train geometry subset SHA256: `d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`;
- frozen four-row gradient subset SHA256: `bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`;
- frozen 32-row devval geometry subset SHA256: `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`;
- RGB boxes as the sole detector targets.

Materialize and hash all exactly 7,187 entries of the frozen V57 order before model construction. Consume each row exactly once, in the same order used by V65. Do not reshuffle, repeat, substitute, truncate, or extend rows.

Reconstruct or strictly reload the exact frozen V64 seed-1 common initialization and reproduce SHA256 `50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476` before training. Generate no alternative initialization candidates. Do not initialize from the V64 or V65 trained checkpoints.

## Frozen Model and Training Configuration

Use exactly:

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

- seed `1`;
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

The only intentional difference from V65 is the frozen initialization seed/state. Source, model semantics, data, order, optimizer, evaluator, audit schedule, recovery policy, and Softplus activation must otherwise match V65 exactly.

## CPU and Source-Lock Gates Before CUDA

Before GPU work, prove:

1. V65 evidence and all protected fingerprints match exactly;
2. manifests, full order, subsets, and evaluator inputs match V65;
3. the installed torchvision FCOS source and activation location match V65;
4. Softplus is applied exactly once per FPN feature with `beta=1.0`, `threshold=20.0` in the shared training/inference path;
5. the exact V64 seed-1 initialization is reconstructed or strictly loaded and matches the frozen SHA256;
6. step-0 state dictionaries, pre-activation bbox logits, classification logits, centerness logits, fused features, and alignment outputs are deterministic for the frozen seed-1 state;
7. no bias, weight, loss, target, matcher, anchor, scale, clipping, decode, threshold, top-k, NMS, preprocessing, evaluator, fusion, or scorer field differs from V65;
8. the train-only optimization target guard remains unchanged;
9. the split-agnostic evaluation target path accepts actual row `devval:00005919` without boxes/labels mutation;
10. the full-devval evaluator reproduces the exact V65 schema and fixed configuration on a micro-fixture;
11. recovery snapshots round-trip model, optimizer, all RNG states, next row position, completed step count, logs, audit ledger, and hashes;
12. production and historical V40-V65/V51/manuscript/submission fingerprints remain unchanged.

Fail closed before CUDA on any mismatch.

## Frozen Run Budget

Run exactly one variant:

`v66_seed1_equal_softplus_b1_t20_fulltrain`

Train for exactly **7,187 optimizer steps**, consuming the complete frozen order exactly once. The final scientific checkpoint is the state immediately after step 7,187. No intermediate checkpoint may be selected by loss, geometry, or devval performance.

Save and round-trip verify local recovery snapshots immediately before each audit and additionally every 500 completed optimizer steps. Recovery is allowed only from the latest exact verified V66 snapshot, with no replayed or skipped row or optimizer step. Heavy recovery artifacts remain local and outside Git.

## Frozen Audit Schedule

Run compact train-geometry and four-row no-step gradient audits at exactly:

```text
step 0, 15, 50, 200, 500, 1000, 2000, 4000, 6000, 7187
```

Maximum diagnostic backward calls: **40 total**. Every probe must use a fresh ephemeral copy and must not mutate persistent model, optimizer, RNG, sample-order, recovery, or logging state.

Record the same geometry, activation-derivative, matched-anchor, component-loss, bbox-output gradient, regression-tower gradient, finite-state, timing, CUDA-memory, isolation, and recovery fields used by V65.

At step 7,187, additionally run the frozen 32-row devval geometry audit, then evaluate the final checkpoint exactly once on all 1,845 frozen devval rows.

## Full-Devval Evaluation Contract

Use the exact V65 evaluator configuration and source hash. Compute at minimum:

- AP@[0.50:0.95];
- AP50;
- AP75;
- AR@1;
- AR@10;
- AR@100;
- evaluated image and ground-truth counts;
- prediction count, zero-prediction image count, and non-finite prediction count;
- elapsed evaluation time and peak memory.

Use only the final step-7,187 checkpoint. Do not inspect full-devval metrics before training completes. Do not change score threshold, NMS, max detections, IoU settings, preprocessing, or checkpoint choice after observing results.

After evaluation, create a compact `two_seed_equal_fusion_summary.json` containing the immutable V65 seed-0 metrics, the V66 seed-1 metrics, arithmetic mean, sample standard deviation when defined, minimum, maximum, and absolute seed-to-seed difference for every AP/AR metric. This summary is descriptive only and may not be used to select or rerun a seed.

## Frozen Decision Logic

Choose exactly one outcome:

- `V66_SEED1_FULLTRAIN_COMPLETE_NONZERO_AP`;
- `V66_SEED1_FULLTRAIN_COMPLETE_ZERO_AP`;
- `V66_SEED1_FULLTRAIN_BBOX_COLLAPSE` if strict collapse is observed on two consecutive audits;
- `V66_BLOCKED_SOURCE_INITIALIZATION_OR_EVALUATOR_CONTRACT`;
- `V66_BLOCKED_TRAINING_TRACE_OR_RECOVERY_INCOMPLETE`;
- `V66_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`;
- `V66_BLOCKED_FULL_DEVVAL_EVALUATION`;
- `V66_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`.

A successful V66 run establishes a two-seed equal-fusion Softplus baseline on the frozen MM-UAV devval protocol. It does not establish superiority, an independent-test result, or a reliability-fusion contribution. No method claim is authorized until matched reliability-fusion runs are completed under the same seeds and protocol.

## Stop Rules

Fail closed on:

- any V65 evidence, data, order, subset, source, initialization, evaluator, or protected-file mismatch;
- any initialization candidate other than the exact frozen V64 seed-1 state;
- initialization from a trained checkpoint;
- any activation, model, loss, matcher, anchor, decode, threshold, preprocessing, alignment, equal-fusion, scorer, or evaluator difference from the frozen contract;
- reshuffled, repeated, substituted, replayed, or skipped rows or steps;
- more than 7,187 optimizer steps or more than 40 diagnostic backward calls;
- invalid recovery round trip or diagnostic mutation of persistent state;
- OOM or any non-finite training, geometry, prediction, metric, or recovery value;
- full-devval evaluation before the final checkpoint;
- tuning, threshold selection, checkpoint selection, extra variants/seeds, reruns, reliability-fusion training, or automatic extension;
- heavy artifacts entering Git.

If strict bbox collapse occurs at two consecutive audits, stop and record `V66_SEED1_FULLTRAIN_BBOX_COLLAPSE`; do not modify the activation, LR, optimizer, precision, resolution, loss, order, or audit schedule.

## Required Outputs

Create `runs/v66_mmuav_seed1_softplus_fulltrain_confirmation/` containing compact files such as:

```text
protocol.json
protocol.md
source_lock_v66.json
v65_evidence_verification.json
seed1_initialization_verification.json
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
two_seed_equal_fusion_summary.json
memory_timing_summary.json
safety_audit.json
test_commands.txt
test_output.txt
final_decision.json
handoff.md
```

Keep checkpoints, optimizer states, recovery snapshots, initialization artifacts, raw predictions, tensors, images, feature maps, and other heavy artifacts local and outside Git.

## Required Tests

Verify exact prior evidence and protected-file immutability; frozen data/order/subset hashes; exact seed-1 initialization hash; exact V65-equivalent source/model/evaluator contract; exact 7,187-row one-pass execution; audit schedule and 40-call ceiling; valid recovery round trips; diagnostic isolation; finite state; final-checkpoint-only full-devval evaluation; correct two-seed descriptive summary; zero tuning, selection, extra seeds/variants, reruns, or extensions; and no heavy artifacts in Git.

Run all CPU/source-lock/evaluator-contract tests before CUDA and post-run tests afterward. Save exact commands and outputs.

## Allowed Changes

- current task/status/blocker/write-record and V66 handoff files;
- `runs/v66_mmuav_seed1_softplus_fulltrain_confirmation/**`;
- V66-only runner, frozen seed-1 loader, evaluator wrapper, audit/recovery utilities, and tests;
- minimal backward-compatible imports that do not change production defaults.

## Forbidden Changes

- historical V40-V65 evidence or V51 history;
- production TriAir defaults or semantics;
- raw data or annotations;
- ReLU full training or reliability-fusion training;
- activation, bias, optimizer, LR, loss, target, matcher, anchor, decode, threshold, NMS, preprocessing, alignment, fusion, scorer, or evaluator sweeps/changes;
- independent-test claims, manuscript/submission changes, public derivatives, redistribution, or external sharing;
- additional seeds, variants, reruns, or automatic extension.

## Completion State

Choose exactly one allowed V66 state, update `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, and the V66 handoff, then run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Commit Message

`exp: run V66 MM-UAV seed1 Softplus full-train confirmation`

## Final Report Requirements

Report starting/final commit SHAs; V65 evidence verification; source/data/order/subset/evaluator hashes; exact seed-1 initialization proof; all training/audit/recovery counts; every audit classification; final train/devval compact geometry; final checkpoint hash and local-only location; complete seed-1 AP/AR; two-seed mean/std/min/max/difference summary; prediction safety; timing/memory; test and protected-file results; selected V66 outcome; and the strict no-superiority/no-independent-test claim boundary.
