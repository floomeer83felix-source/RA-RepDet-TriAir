# Current Task

## Authorization

The user explicitly directed the project to begin MM-UAV dataset validation immediately and to stop spending the active task on provider authority, official-version, rights, or official-test acquisition work.

The previously authorized `V71_MMUAV_PROVIDER_SOURCE_RIGHTS_AND_OFFICIAL_TEST_ACQUISITION_AUTHORIZED` task is superseded before execution.

The active task is:

`V71_MMUAV_EXISTING_DEVVAL_TRIAIR_ZERO_SHOT_EXTERNAL_DOMAIN_VALIDATION_AUTHORIZED`

V71 will evaluate the six frozen TriAir manuscript checkpoints directly on the existing frozen `1,845`-row MM-UAV devval manifest. No MM-UAV training, fine-tuning, adaptation, calibration, checkpoint selection, threshold tuning, or result-driven rerun is authorized.

This is an **external-domain zero-shot validation on a previously exposed development split**. It is not an independent blind external test and must never be described as one.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
git rev-parse HEAD
```

Require a clean worktree. Record the actual starting commit and verify that V70 completion commit `bd62068aa0f3ab046d8545c4eef69938b4e73c9b` is an ancestor of `HEAD`.

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, the current task/status/blocker files, frozen TriAir checkpoint evidence, the V52-V70 MM-UAV manifests and evaluator evidence, active model/dataset code, and protected-file rules.

## Frozen Evaluation Dataset

Use exactly the existing frozen MM-UAV devval manifest used by V65-V67:

- row count: exactly `1,845`;
- preserve exact row order, modality pairing, annotation mapping, and file identities;
- do not add, remove, replace, resample, or reorder rows;
- do not create a new split;
- do not use the 7,187-row MM-UAV training manifest for model updates or fitting.

Record the exact manifest path, row count, SHA256, modality-presence counts, annotation-file hashes, and overlap with prior V52-V70 work.

The overlap is expected and must be reported honestly. It is not a blocker for this task because V71 is explicitly an exposed external-domain validation, not a blind test.

## Frozen Models

Locate and strictly verify exactly six frozen TriAir manuscript checkpoints:

1. matched Early Fusion, seed `0`;
2. matched Early Fusion, seed `1`;
3. matched Early Fusion, seed `2`;
4. full reliability-aware RA-RepDet with modality dropout `p=0.15`, seed `0`;
5. full reliability-aware RA-RepDet with modality dropout `p=0.15`, seed `1`;
6. full reliability-aware RA-RepDet with modality dropout `p=0.15`, seed `2`.

For each checkpoint record:

- method and seed;
- local opaque identifier;
- filename, byte count, and SHA256;
- source commit and model class;
- state-dictionary key/tensor fingerprint;
- original checkpoint-selection rule and evidence reference;
- strict-load result in the unchanged TriAir architecture.

Do not use MM-UAV-trained V57/V63/V65/V66/V67 checkpoints, optimizer states, learned MM-UAV alignment, the MM-UAV Softplus wrapper, checkpoint averaging, ensembling, checkpoint repair, or replacement checkpoints.

If the six authoritative checkpoints cannot be located and strictly loaded, stop with `V71_BLOCKED_TRIAIR_CHECKPOINT_OR_MODEL_CONTRACT`.

## Deterministic MM-UAV-to-TriAir Adapter

Freeze a parameter-free deterministic conversion into the exact five-channel TriAir input:

```text
RGB channels 0-2 + thermal channel 3 + event channel 4
```

Freeze before metric computation:

- source modality mapping;
- bit depth, dtype conversion, clipping, scaling, and normalization;
- event representation semantics;
- spatial registration policy;
- deterministic resize/crop/pad/interpolation to `640 x 640`;
- box-coordinate transformation;
- missing/corrupt modality stop policy;
- deterministic ordering and prohibition of randomness;
- adapter source hash and micro-fixture expected outputs.

The adapter may use only the frozen TriAir preprocessing contract and already exposed MM-UAV development evidence. It may not learn parameters or be changed after observing V71 AP/AR.

If a defensible fixed conversion or vehicle ontology cannot be established, stop with `V71_BLOCKED_ADAPTER_OR_ONTOLOGY_CONTRACT`.

## Frozen Inference and Evaluator Contract

Use the unchanged TriAir inference contract:

- input size: `640 x 640`;
- score threshold: `0.001`;
- NMS threshold: `0.6`;
- maximum detections per image: `100`;
- shared vehicle-class mapping frozen before evaluation;
- no test-time augmentation;
- no per-dataset normalization fitting;
- no calibration, adaptation, threshold selection, or checkpoint selection.

Report for every checkpoint:

- COCO AP@[0.50:0.95];
- AP50;
- AP75;
- AR@1;
- AR@10;
- AR@100;
- prediction count;
- images with and without predictions;
- finite and valid decoded-box counts;
- wall-clock time and peak memory.

Report matched seed-wise `RA-RepDet - Early Fusion` differences for every metric, plus descriptive mean, sample standard deviation, minimum, and maximum across seeds. Do not run significance tests with only three seeds unless the repository already contains a frozen, pre-authorized analysis contract.

## Execution Order

1. verify source and protected-file fingerprints;
2. verify the exact 1,845-row devval manifest and evaluator contract;
3. strictly load and hash all six checkpoints;
4. freeze and test the deterministic five-channel adapter;
5. run a no-metric finite-output smoke pass on a fixed small prefix solely to catch runtime/schema failures;
6. run each checkpoint exactly once over all 1,845 rows;
7. compute the frozen AP/AR metrics;
8. create the matched three-seed comparison table;
9. repeat focused tests and protected-file audit;
10. stop without tuning or rerunning based on results.

The smoke pass may not compute AP/AR or change preprocessing, ontology, thresholds, checkpoints, seeds, or variants. Any smoke failure must be fixed only when it is an implementation error relative to the frozen contract; semantic ambiguity must block.

## Fail-Closed Conditions

Stop with the matching decision when:

- any frozen checkpoint or model contract cannot be verified;
- the 1,845-row manifest, row order, modality pairing, annotation mapping, or evaluator differs from the frozen evidence;
- the deterministic five-channel adapter or vehicle ontology cannot be fixed without learned or result-informed choices;
- any loss-free inference tensor, parameter, activation, decoded box, prediction, or metric input is non-finite;
- OOM, corrupted data, unreadable modality, coordinate mismatch, evaluator mismatch, or protected-file drift occurs;
- any training, fine-tuning, adaptation, calibration, tuning, checkpoint selection, seed addition, variant addition, or result-driven rerun is attempted;
- raw data, labels, checkpoints, predictions, local absolute paths, or heavy/private artifacts are added to Git.

Do not silently substitute data, checkpoints, preprocessing, class maps, thresholds, or evaluators.

## Decision States

Choose exactly one:

- `V71_MMUAV_EXISTING_DEVVAL_ZERO_SHOT_EXTERNAL_DOMAIN_VALIDATION_COMPLETE`;
- `V71_BLOCKED_TRIAIR_CHECKPOINT_OR_MODEL_CONTRACT`;
- `V71_BLOCKED_DATA_MANIFEST_OR_EVALUATOR_CONTRACT`;
- `V71_BLOCKED_ADAPTER_OR_ONTOLOGY_CONTRACT`;
- `V71_BLOCKED_RUNTIME_OR_FINITE_STATE`;
- `V71_BLOCKED_SOURCE_PROTECTED_OR_PRIVATE_ARTIFACT_VIOLATION`.

## Required Outputs

Create:

`runs/v71_mmuav_existing_devval_triair_zero_shot_external_domain_validation/`

Commit compact text/JSON/CSV evidence only, including:

- `protocol.md`
- `protocol.json`
- `source_lock.json`
- `devval_manifest_lock.json`
- `exposure_and_claim_boundary.json`
- `triair_checkpoint_manifest.json`
- `triair_checkpoint_verification.json`
- `triair_model_contract.json`
- `mmuav_to_triair_adapter_spec.md`
- `mmuav_to_triair_adapter_spec.json`
- `adapter_source_lock.json`
- `adapter_determinism_tests.json`
- `class_ontology_mapping.json`
- `zero_shot_evaluator_contract.json`
- `smoke_test_summary.json`
- `per_checkpoint_metrics.csv`
- `per_checkpoint_metrics.json`
- `paired_seed_comparison.csv`
- `paired_seed_comparison.json`
- `external_domain_validation_summary.md`
- `memory_timing_summary.json`
- `protected_file_audit.json`
- `test_commands.txt`
- `test_output.txt`
- `final_decision.json`
- `handoff.md`

Keep raw MM-UAV media, annotations, full predictions, tensors, checkpoints, local paths, and heavy artifacts outside Git.

## Tests

Add focused V71 tests covering at minimum:

- exact manifest row count/order/hash;
- six-checkpoint identity and strict loading;
- deterministic five-channel adapter output;
- frozen ontology, thresholds, NMS, maximum detections, and evaluator settings;
- no trainable or MM-UAV-trained adaptation path;
- one evaluation attempt per checkpoint;
- metric aggregation and paired-seed arithmetic;
- claim-boundary text stating exposed external-domain validation, not independent blind test;
- protected-file and private/heavy-artifact checks.

Run the V71 focused tests before inference and after completion, plus protected regression tests referenced by the latest TriAir manuscript handoff.

## Claim Boundary

V71 may establish only how the six frozen TriAir manuscript checkpoints perform zero-shot on the previously exposed MM-UAV devval domain under one frozen conversion and evaluator.

It may not establish:

- independent or blind external validation;
- performance on an official MM-UAV test set;
- absence of development-set influence;
- external generalization beyond this exposed MM-UAV devval split;
- permission for public redistribution or manuscript reporting.

Provider-source, official-version, and rights acquisition are not part of this active task. They must not delay the internal validation run.

## Completion

Update the four task/status/blocker/write-record files and the V71 run evidence. Commit the completed validation with exactly:

`exp: run V71 MM-UAV existing-devval TriAir zero-shot external-domain validation`

Push to:

`research/ra-repdet-triair`
