# Current Task

## Authorization

The user clarified that the intended MM-UAV objective is **independent external validation of the frozen TriAir models**, not training a new detector on MM-UAV. The previously authorized `V69_TRIAIR_MANUSCRIPT_SUBMISSION_READINESS_AUTHORIZED` task is superseded before execution.

The active task is:

`V69_MMUAV_ZERO_SHOT_EXTERNAL_VALIDATION_PROTOCOL_AND_BLIND_TEST_FREEZE_AUTHORIZED`

V69 is a CPU/documentation/preflight task. It must establish whether a genuinely unused MM-UAV partition exists, freeze a parameter-free MM-UAV-to-TriAir input adapter, verify the frozen TriAir checkpoints and evaluator, and seal a blind external-test protocol. V69 performs **no model training, fine-tuning, checkpoint selection, threshold tuning, prediction generation, AP/AR computation, or test-label inspection**.

The standing local/private-research-only rule remains in force. The unresolved V68 data-rights and citation gate blocks manuscript/public reporting, but it does not block an internal protocol audit or blind evaluation preparation. No MM-UAV result may enter the manuscript until a provider-verifiable documentation re-audit passes.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization base: `0c5cafc695cbdb6d8b0e91c62eb18f84e14c0706`.

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, the current task/status/blocker files, all V40-V49 TriAir manuscript evidence, all V52-V68 MM-UAV manifests/evidence/handoffs, the active TriAir model and dataset code, the frozen evaluator, checkpoint metadata, and protected-file rules. Record the actual starting commit.

Stop on unexpected repository drift, missing historical evidence, unavailable frozen TriAir checkpoints, an unresolvable data-exposure ledger, an input-representation mismatch, or any attempt to reuse an exposed MM-UAV partition as an independent test set.

## Correct Scientific Objective

The required scientific path is:

```text
TriAir training and model selection only
-> freeze the six manuscript checkpoints
-> freeze a deterministic MM-UAV five-channel adapter
-> identify a never-used MM-UAV blind partition
-> seal labels and evaluator
-> run zero-shot inference in a later task
```

The following path is explicitly not the objective and must not be resumed:

```text
MM-UAV training -> MM-UAV devval evaluation
```

V65-V67 remain valid internal MM-UAV development evidence, but their 7,187-row train and 1,845-row devval partitions cannot be renamed or reused as an independent external test set.

## Independence and Exposure Contract

Build a complete sample-level and sequence/component-level exposure ledger for V52-V68. Classify every MM-UAV item into at least:

- `IDENTITY_ONLY`: path/name/hash/inventory metadata was recorded without viewing modality or label content;
- `CONTENT_EXPOSED`: any RGB, IR, event, annotation, visualization, decoded prediction, or per-sample statistic was inspected;
- `DEVELOPMENT_USED`: used for training, devval evaluation, geometry/gradient probes, adapter/model debugging, threshold/evaluator debugging, or result-driven decisions.

`IDENTITY_ONLY` inventory does not by itself disqualify a sample. `CONTENT_EXPOSED` and `DEVELOPMENT_USED` samples are ineligible for the blind test. Any same-flight, same-sequence, temporally adjacent, exact-content duplicate, or near-duplicate component linked to an ineligible sample is also ineligible unless provider metadata proves independence.

The preferred candidate is an official provider-defined test split never used by V52-V68. If no unused official split exists, a pre-registered blind external holdout may be formed only from wholly unexposed sequences/components using provider metadata and file identity, without label content, model predictions, or performance information. Do not randomly resplit the V52-V68 train/devval data.

If no eligible untouched partition remains, finish with `V69_BLOCKED_NO_UNUSED_MMUAV_PARTITION`. Do not compensate by adding seeds, retraining, or relabeling an old split.

## Blind-Test Data Freeze

For an eligible candidate partition:

1. create a local authoritative manifest using dataset-relative identifiers;
2. record its row count, sequence/component count, modality-presence schema, and SHA256;
3. keep the full manifest and any sensitive paths local and outside Git;
4. commit only compact hashes, counts, opaque identifiers when permitted, and audit conclusions;
5. hash candidate annotation files without parsing their contents;
6. do not compute class counts, box counts, size distributions, difficulty statistics, or any metric from candidate labels;
7. seal the labels until the later zero-shot evaluation task;
8. prove zero overlap with all `CONTENT_EXPOSED` and `DEVELOPMENT_USED` items at sample, sequence/component, exact-content, and available near-duplicate levels.

A schema-only candidate pass is permitted only after the adapter, model contract, and evaluator are frozen. It may verify readable files, tensor shapes, finite values, and modality presence, but may not visualize samples, generate model predictions, inspect labels, or trigger a protocol change. Any unexpected candidate schema must block the task rather than cause test-informed adapter modification.

## Frozen TriAir Checkpoints

Identify and verify the exact six frozen manuscript checkpoints:

- matched early fusion, seeds 0, 1, and 2;
- full reliability-aware configuration with modality dropout `p=0.15`, seeds 0, 1, and 2.

For each checkpoint record locally and in compact Git metadata where allowed:

- method and seed;
- local checkpoint filename or opaque identifier;
- SHA256 and byte count;
- source commit and model class;
- state-dictionary key fingerprint;
- frozen TriAir checkpoint-selection rule and original evidence reference;
- successful strict load into the unchanged manuscript architecture.

No MM-UAV-trained V57/V63/V65/V66/V67 checkpoint, feature aligner, Softplus detector wrapper, reliability scorer state, or optimizer state may be used. No checkpoint may be selected, rejected, repaired, averaged, ensembled, or recalibrated using MM-UAV data.

If the six authoritative TriAir checkpoints cannot be located and strictly verified, finish with `V69_BLOCKED_TRIAIR_CHECKPOINT_OR_MODEL_CONTRACT`.

## Parameter-Free MM-UAV-to-TriAir Adapter

Freeze a deterministic, non-learned conversion to the exact five-channel input expected by the TriAir manuscript models:

```text
RGB channels 0-2 + thermal channel 3 + event channel 4
```

The adapter must be derived only from the frozen TriAir preprocessing contract, provider metadata, and already exposed MM-UAV development material. It must not learn parameters or use candidate-test labels, predictions, or metrics.

Freeze and hash at minimum:

- modality-to-channel mapping and class/label ontology mapping;
- source bit depth, value range, dtype conversion, clipping, and normalization;
- event representation semantics;
- spatial registration source and policy;
- resize/crop/pad/interpolation policy to the TriAir `640 x 640` input;
- box-coordinate transformation rules;
- missing/corrupt modality policy;
- deterministic ordering and random-state prohibition;
- code/source hashes and micro-fixture expected outputs.

Do not use the V53-V67 learned IR/event feature alignment path. If MM-UAV cannot be converted to a semantically defensible TriAir five-channel representation without learned adaptation or test-informed choices, finish with `V69_BLOCKED_INPUT_REPRESENTATION_OR_LABEL_ONTOLOGY`.

## Frozen Zero-Shot Evaluator Contract

Freeze the exact inference and evaluation semantics before labels are unsealed:

- the unchanged TriAir model architectures and checkpoints;
- input size and preprocessing from the TriAir manuscript protocol;
- score threshold `0.001`;
- NMS threshold `0.6`;
- maximum 100 detections per image;
- canonical COCO-style AP@[0.50:0.95], AP50, AP75, AR@1, AR@10, and AR@100;
- one shared vehicle-class ontology mapping fixed without candidate-label inspection;
- no test-time augmentation, calibration, adaptation, checkpoint selection, threshold selection, or per-dataset normalization fitting;
- one final evaluation attempt per checkpoint in the later task;
- paired seed-wise comparison of early fusion and reliability-aware fusion, with descriptive mean and sample standard deviation only.

Validate evaluator determinism and schema using synthetic fixtures or already exposed MM-UAV development rows only. Do not run any frozen TriAir checkpoint on the candidate blind partition in V69.

## Rights and Reporting Boundary

Record two independent statuses:

1. `internal_scientific_protocol_ready`: whether a strict blind zero-shot protocol is scientifically ready;
2. `manuscript_reporting_ready`: remains false until provider authority, canonical citation, exact version, dataset license/access terms, research-use permission, aggregate-results reporting permission, and redistribution restrictions are verified.

The rights blocker must not be used to justify training on MM-UAV or abandoning the zero-shot protocol. Conversely, scientific protocol readiness does not authorize publication.

## Required Outputs

Create `runs/v69_mmuav_zero_shot_external_validation_preflight/` containing compact files such as:

```text
protocol.md
protocol.json
historical_exposure_ledger_summary.json
historical_exposure_ledger_schema.md
full_inventory_metadata.json
candidate_partition_discovery.json
candidate_blind_manifest_metadata.json
candidate_manifest_sha256.txt
sequence_component_independence_audit.json
exact_and_near_duplicate_audit.json
label_seal_record.json
triair_checkpoint_manifest.json
triair_checkpoint_verification.json
triair_model_contract.json
mmuav_to_triair_adapter_spec.md
mmuav_to_triair_adapter_spec.json
adapter_source_lock.json
adapter_determinism_tests.json
class_ontology_mapping.json
zero_shot_evaluator_contract.json
rights_and_reporting_boundary.md
protected_file_audit.json
test_commands.txt
test_output.txt
final_decision.json
handoff.md
```

Keep the full blind manifest, raw media, annotations, candidate-label statistics, checkpoints, predictions, tensors, local absolute paths, provider correspondence, and other sensitive/heavy artifacts local and outside Git.

## Required Tests

Before completion, prove:

- all V52-V68 exposed samples and linked sequences/components are represented in the ledger;
- candidate-test membership was chosen without labels, predictions, or metrics;
- candidate test has zero prohibited sample/sequence/component overlap;
- adapter output is deterministic and matches the frozen five-channel TriAir contract;
- no learned alignment, Softplus MM-UAV wrapper, MM-UAV-trained weight, or trainable adaptation is present;
- all six TriAir checkpoints strictly load and match frozen manuscript evidence;
- model, preprocessing, threshold, NMS, max-detection, class mapping, and evaluator settings are frozen before candidate schema validation;
- candidate labels were hashed but not parsed;
- no inference or metric computation occurred on the candidate partition;
- no CUDA training, fine-tuning, rerun, seed addition, variant addition, tuning, checkpoint selection, or threshold selection occurred;
- protected TriAir evidence, V52-V68 history, manuscript, and production files remain unchanged;
- no heavy/private MM-UAV artifacts enter Git.

## Decision States

Choose exactly one:

- `V69_MMUAV_BLIND_EXTERNAL_TEST_FROZEN_INTERNAL_ONLY` — an eligible untouched partition, six frozen TriAir checkpoints, deterministic adapter, sealed labels, and evaluator contract are all verified; publication rights remain unresolved;
- `V69_BLOCKED_NO_UNUSED_MMUAV_PARTITION` — no untouched official split or defensible unexposed sequence/component holdout exists;
- `V69_BLOCKED_EXPOSURE_OR_SPLIT_INDEPENDENCE` — exposure or sequence/content overlap cannot be resolved;
- `V69_BLOCKED_TRIAIR_CHECKPOINT_OR_MODEL_CONTRACT` — one or more authoritative TriAir checkpoints or model contracts cannot be verified;
- `V69_BLOCKED_INPUT_REPRESENTATION_OR_LABEL_ONTOLOGY` — a defensible parameter-free five-channel conversion or class mapping cannot be frozen;
- `V69_BLOCKED_EVALUATOR_OR_LABEL_SEAL_CONTRACT` — evaluator determinism or blind-label sealing cannot be established;
- `V69_BLOCKED_SOURCE_PROTECTED_OR_PRIVATE_ARTIFACT_VIOLATION`.

No V69 outcome may itself compute external-test metrics. A successful V69 completion permits the standing handoff workflow to authorize a separate V70 zero-shot evaluation task.

## Allowed Changes

- the four current task/status/blocker/write-record files;
- `runs/v69_mmuav_zero_shot_external_validation_preflight/**` compact audit outputs;
- V69-only inventory, exposure-ledger, adapter, checkpoint-verification, evaluator-freeze, and test utilities;
- minimal backward-compatible imports that do not change production or manuscript model behavior.

## Forbidden Changes

- V40-V68 historical scientific evidence;
- active TriAir manuscript or submission claims;
- raw MM-UAV data or annotations;
- production model/training/evaluator behavior;
- MM-UAV training, fine-tuning, learned alignment, Softplus-head substitution, domain adaptation, calibration, pseudo-labeling, or checkpoint averaging;
- candidate-label inspection or candidate prediction/metric generation;
- threshold, NMS, preprocessing, class-map, checkpoint, seed, or variant selection using MM-UAV candidate-test results;
- publication or external-sharing claims before the V68 rights gate is repaired.

## Completion

Update the four task/status files, final decision, and handoff. Commit the completed preflight with:

`docs: freeze V69 MM-UAV zero-shot external validation protocol`
