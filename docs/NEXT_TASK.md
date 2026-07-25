# Current Task

## Authorization

The user reported that V69 completed and was pushed. Under the standing automatic handoff workflow, the next task is authorized as:

`V70_MMUAV_UNTOUCHED_EXTERNAL_PARTITION_INTAKE_AND_BLIND_FREEZE_AUTHORIZED`

V69 completed at commit `dbf728207396df869dfe7165f432010d303174dc` with `V69_BLOCKED_NO_UNUSED_MMUAV_PARTITION`. The complete locally available provider-train inventory contains `897,578` synchronized triplets across `424` sequences, and every sequence is linked to V52-V67 development. Existing local MM-UAV material therefore cannot provide an independent external test set.

V70 is an external-input-gated CPU/metadata/documentation task. It may accept and audit only one of the following:

1. a provider-defined official MM-UAV test split that was absent from and unexposed during V52-V69; or
2. wholly new provider flights/sequences/components with provider metadata proving independence from all `424` development-linked sequences.

V70 performs no model training, fine-tuning, adaptation, calibration, checkpoint selection, threshold tuning, candidate prediction generation, AP/AR computation, or result-driven protocol modification.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Expected authorization base and V69 completion commit:

`dbf728207396df869dfe7165f432010d303174dc`

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, the current task/status/blocker files, V52-V69 evidence and handoffs, the V69 exposure-ledger outputs, the frozen TriAir manuscript protocol and checkpoint evidence, V68 rights records, evaluator code, and protected-file rules. Record the actual starting commit.

Stop before candidate media or label access on any repository drift, incomplete external source metadata, ambiguous split identity, overlap with V52-V69 exposure, or unauthorized acquisition route.

## External Input Gate

Do not begin candidate schema, checkpoint, adapter, or evaluator work until a new external package is supplied through an authorized route.

The package must include enough provider-issued metadata to establish:

- dataset or split name;
- provider or release authority;
- exact version or release identifier;
- official split designation, or new sequence/flight identifiers;
- acquisition/download source and date;
- archive or package SHA256 and byte count;
- modality inventory without opening media content;
- sequence/component identity metadata;
- canonical citation or provider documentation when available;
- license/access/research-use/reporting/redistribution terms when available.

Local possession, a code repository license, an arXiv license, or a manually renamed directory is not sufficient evidence of an official or independent test split.

If no new external package is supplied, finish with:

`V70_BLOCKED_EXTERNAL_TEST_MATERIAL_NOT_SUPPLIED`

## Independence Audit Before Media Access

Using only provider metadata, archive directory identities, filenames, opaque IDs, and cryptographic hashes:

1. compare all candidate split, flight, sequence, and component identifiers against the frozen V69 ledger;
2. prove that the candidate was absent from all V52-V69 inventories, manifests, development rows, diagnostics, visualizations, predictions, and metrics;
3. exclude any same-flight, same-sequence, adjacent, duplicate, near-duplicate, or provider-linked component associated with the existing `424` sequences;
4. verify that the candidate was not derived by randomly resplitting the currently available provider-train material;
5. record candidate sequence/component count and opaque identity hash without opening media or annotations;
6. preserve the full candidate manifest locally and outside Git.

If independence cannot be proved, finish with:

`V70_BLOCKED_EXTERNAL_PARTITION_OVERLAP_OR_PROVENANCE`

No candidate sample may be visualized, decoded, statistically summarized, or passed through a model before this gate passes.

## Blind Partition Freeze

After the metadata-only independence gate passes:

- create a local authoritative blind manifest using dataset-relative or opaque identifiers;
- record row count, sequence/component count, modality-presence schema, manifest SHA256, and source-package SHA256;
- hash all annotation files without parsing annotation contents;
- record a label-seal timestamp and hash ledger;
- prohibit class counts, box counts, object-size distributions, difficulty summaries, sample visualization, or any label-derived statistic;
- commit only compact hashes, counts, schemas, and audit conclusions;
- keep raw media, labels, the full manifest, provider correspondence, credentials, and local absolute paths outside Git.

The blind partition must remain sealed until a separately authorized one-time zero-shot evaluation task.

## Frozen TriAir Checkpoints

Only after the blind partition identity is frozen, locate and strictly verify the six authoritative TriAir manuscript checkpoints:

- matched early fusion: seeds `0`, `1`, and `2`;
- full reliability-aware fusion with modality dropout `p=0.15`: seeds `0`, `1`, and `2`.

For each checkpoint record:

- method and seed;
- opaque local identifier;
- SHA256 and byte count;
- source commit and model class;
- state-dictionary key/tensor fingerprint;
- original TriAir checkpoint-selection rule and evidence reference;
- strict-load success in the unchanged manuscript architecture.

No MM-UAV-trained V57/V63/V65/V66/V67 checkpoint, learned alignment state, Softplus MM-UAV wrapper, optimizer state, checkpoint averaging, ensembling, repair, or replacement is permitted.

If any authoritative checkpoint cannot be located and strictly verified, finish with:

`V70_BLOCKED_TRIAIR_CHECKPOINT_OR_MODEL_CONTRACT`

## Parameter-Free MM-UAV-to-TriAir Adapter

Freeze a deterministic non-learned conversion into the exact five-channel representation expected by the TriAir manuscript models:

```text
RGB channels 0-2 + thermal channel 3 + event channel 4
```

The adapter may use only:

- the frozen TriAir preprocessing contract;
- provider documentation and metadata;
- already exposed V52-V69 MM-UAV development material for non-test micro-fixtures.

Freeze and hash:

- modality-to-channel mapping;
- bit depth, dtype conversion, clipping, scaling, and normalization;
- event representation semantics;
- spatial registration policy;
- deterministic resize/crop/pad/interpolation to `640 x 640`;
- box-coordinate transformation;
- corrupt/missing-modality stop policy;
- deterministic ordering and prohibition of randomness;
- implementation source hash and micro-fixture expected outputs.

Do not use learned feature alignment, domain adaptation, calibration, test-time fitting, candidate predictions, or candidate labels. If a defensible parameter-free conversion cannot be fixed, finish with:

`V70_BLOCKED_INPUT_REPRESENTATION_OR_LABEL_ONTOLOGY`

## Frozen Evaluator Contract

Before any candidate media schema pass, freeze:

- the six unchanged TriAir checkpoints and model classes;
- the `640 x 640` TriAir preprocessing contract;
- one shared vehicle-class ontology mapping;
- score threshold `0.001`;
- NMS threshold `0.6`;
- maximum `100` detections per image;
- canonical COCO-style AP@[0.50:0.95], AP50, AP75, AR@1, AR@10, and AR@100;
- exactly one final evaluation attempt per checkpoint in the later task;
- paired seed-wise Early Fusion versus RA-RepDet reporting;
- descriptive mean and sample standard deviation only;
- no test-time augmentation, calibration, adaptation, checkpoint selection, threshold selection, or dataset-specific normalization fitting.

Validate determinism only on synthetic fixtures or previously exposed MM-UAV development rows. Candidate predictions and metrics remain forbidden in V70.

## Candidate Schema Pass

Only after the partition, checkpoints, adapter, ontology, and evaluator are frozen may V70 perform a schema-only pass that verifies:

- files can be read;
- modalities required by the frozen adapter exist;
- tensor shapes and dtypes match the frozen contract;
- converted tensors are finite;
- annotation files remain sealed and unparsed.

Do not visualize media, run a model, generate predictions, inspect labels, or change the adapter because of candidate content. Any unexpected candidate schema must block with:

`V70_BLOCKED_CANDIDATE_SCHEMA_OR_LABEL_SEAL_CONTRACT`

## Rights and Reporting Boundary

Maintain two independent statuses:

- `internal_scientific_protocol_ready`;
- `manuscript_reporting_ready`.

V70 may become internally ready while manuscript reporting remains false. V68 remains blocked until provider authority, canonical citation, exact version, dataset license/access terms, research-use permission, aggregate-results reporting permission, and redistribution restrictions are verified.

No MM-UAV result, split description, metric, table, figure, or claim may enter the manuscript or be publicly shared solely because V70 succeeds.

## Required Outputs

Create `runs/v70_mmuav_external_partition_intake_and_blind_freeze/` containing compact files such as:

```text
protocol.md
external_package_metadata.json
external_package_hashes.json
provider_split_identity_audit.md
v69_exposure_ledger_verification.json
candidate_independence_audit.json
candidate_blind_manifest_metadata.json
candidate_manifest_sha256.txt
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
candidate_schema_audit.json
rights_and_reporting_boundary.md
protected_file_audit.json
test_commands.txt
test_output.txt
final_decision.json
handoff.md
```

Keep the full manifest, raw media, labels, checkpoints, predictions, tensors, credentials, provider correspondence, and local paths outside Git.

## Required Tests

Prove before completion:

- V69 evidence and all historical hashes remain unchanged;
- the candidate external package is newly supplied and not a renamed local train split;
- candidate sequence/component identity has zero prohibited overlap with V52-V69;
- the blind manifest and label seal are deterministic and hashed;
- all six TriAir checkpoints strictly load and match frozen evidence;
- the adapter is parameter-free, deterministic, and identical across runs;
- no learned alignment, MM-UAV-trained checkpoint, Softplus MM-UAV wrapper, adaptation, or calibration is present;
- ontology, preprocessing, thresholds, NMS, detections, and evaluator are frozen before candidate schema access;
- candidate labels were not parsed;
- no candidate model inference, prediction, or metric computation occurred;
- no CUDA training, fine-tuning, tuning, checkpoint selection, seed addition, or variant addition occurred;
- protected manuscript, submission, production, TriAir, and V40-V69 files remain unchanged;
- no raw/private/heavy artifacts entered Git.

## Decision States

Choose exactly one:

- `V70_MMUAV_BLIND_EXTERNAL_TEST_FROZEN_INTERNAL_ONLY` — an eligible new external partition, six TriAir checkpoints, deterministic adapter, ontology, label seal, and evaluator contract are frozen; no inference or metrics were computed;
- `V70_BLOCKED_EXTERNAL_TEST_MATERIAL_NOT_SUPPLIED`;
- `V70_BLOCKED_EXTERNAL_PARTITION_OVERLAP_OR_PROVENANCE`;
- `V70_BLOCKED_TRIAIR_CHECKPOINT_OR_MODEL_CONTRACT`;
- `V70_BLOCKED_INPUT_REPRESENTATION_OR_LABEL_ONTOLOGY`;
- `V70_BLOCKED_CANDIDATE_SCHEMA_OR_LABEL_SEAL_CONTRACT`;
- `V70_BLOCKED_SOURCE_PROTECTED_OR_PRIVATE_ARTIFACT_VIOLATION`.

A successful V70 permits a separate V71 one-time zero-shot external evaluation task. No V70 outcome itself authorizes predictions, metrics, public reporting, or manuscript inclusion.

## Allowed Changes

- the four current task/status/blocker/write-record files;
- `runs/v70_mmuav_external_partition_intake_and_blind_freeze/**` compact audit outputs;
- V70-only metadata intake, exposure comparison, adapter, checkpoint-verification, label-seal, evaluator-freeze, and test utilities;
- minimal backward-compatible imports that do not change production or manuscript behavior.

## Forbidden Changes

- V40-V69 historical scientific evidence;
- active TriAir manuscript or submission claims;
- production model/training/evaluator behavior;
- reuse or random resplitting of the existing `424` provider-train sequences;
- MM-UAV training, fine-tuning, pseudo-labeling, learned alignment, domain adaptation, calibration, Softplus substitution, or checkpoint averaging;
- candidate-label inspection, visualization, prediction generation, or metric computation;
- threshold, preprocessing, ontology, checkpoint, seed, or variant selection using candidate information;
- raw media, labels, checkpoints, credentials, private correspondence, or heavy artifacts in Git;
- manuscript/public reporting before the separate V68 rights gate passes.

## Completion

Update the four task/status files, V70 final decision, and handoff. Commit with:

`docs: freeze V70 untouched MM-UAV external partition intake`

## Execution Result

Executed: 2026-07-25

Actual starting commit:

`d851d4b2d855311a52578c6071df96ef07d1e253`

Decision:

`V70_BLOCKED_EXTERNAL_TEST_MATERIAL_NOT_SUPPLIED`

The external-input gate found no newly supplied provider-defined official test split or wholly new independent provider flight/sequence package. The known MM-UAV root still contains only the previously audited provider `train` split at directory-identity level. V70 stopped before media or annotation access and before independence, blind-manifest, label-seal, checkpoint, adapter, evaluator, or schema work.

Commit message:

`docs: freeze V70 untouched MM-UAV external partition intake`
