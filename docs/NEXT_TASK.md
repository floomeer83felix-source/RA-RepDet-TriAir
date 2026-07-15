# Current Task

## User Authorization (2026-07-15)

The user authorized one final **CPU-only MM-UAV provider/alignment audit**.

The purpose is to determine whether the dataset provider supplies a scientifically defensible, reproducible cross-modal alignment/calibration method and an explicit sparse-GT contract. This authorization does **not** permit GPU work, model training, metric generation, learned alignment design, validation-GT fitting, or manuscript edits.

## Title

V52 final provider, sparse-GT, and cross-modal alignment audit.

## Goal

Resolve whether MM-UAV can be used in a future RA-RepDet tri-modal experiment without treating spatially misaligned RGB, IR, and event frames as channel-aligned inputs.

The task must answer four questions from provider-controlled evidence:

1. Does the provider define the meaning of frames with no GT row?
2. Does the provider define the target category and the final three MOT-like GT fields?
3. Does the provider provide a license or explicit research-use terms?
4. Does the provider provide a deterministic calibration, registration, warp, crop, coordinate transform, or official alignment implementation that can place RGB, IR, and event information in a defensible common detection coordinate system?

Stop after the audit and decision. Do not run the 200-step pilot.

## Required Start

Run:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Read:

- `AGENTS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `docs/NEXT_TASK.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/v52_mmuav_audit/dataset_audit.md`
- `runs/v52_mmuav_audit/annotation_audit.md`
- `runs/v52_mmuav_audit/synchronization_audit.md`
- `runs/v52_mmuav_audit/sampling_protocol.md`
- `runs/v52_mmuav_audit/sampled_manifest.json`
- `runs/v52_mmuav_audit/geometry_audit.csv`
- `runs/v52_mmuav_audit/feasibility_decision.md`
- `runs/v52_mmuav_audit/pilot_gate.json`
- `runs/v51_visdrone_recovery/cv_run_status.json`

Record the starting commit SHA.

## Frozen Facts

Preserve these facts unless a reproducible audit finds an arithmetic or parsing error:

- 424 complete source-train sequences are accepted as the local V52 subset; incomplete sequence `0512` remains quarantined.
- The frozen sequence split is 339 train and 85 development-validation sequences.
- The user-authorized sampling rule remains source indices `1, 21, 41, ...`.
- The interval-20 manifest contains 45,036 synchronized triplets.
- 9,138 sampled triplets contain at least one source GT row.
- 35,898 sampled triplets lack a verified supervised target contract and must not be treated as empty-target negatives.
- RGB, IR, and event native grids are 640x360, 640x512, and 346x260.
- Dimension-only scaling produced mean matched RGB/IR IoU about 0.00867 on the frozen geometry sample; direct channel-aligned fusion is invalid.
- Event frames have no separate detection boxes in the locally audited data.
- V51 is incomplete and must not be changed by this task.

## Scientific Boundary

Do not:

- interpret missing GT rows as empty scenes without an explicit provider statement;
- create interpolated, propagated, or pseudo labels;
- fit affine, homography, thin-plate-spline, optical-flow, or learned transforms using development-validation GT;
- claim synchronized filenames imply pixel alignment;
- copy RGB boxes into IR or event coordinates;
- call simple independent width/height scaling a valid registration;
- design or train a new alignment module;
- run CUDA forward/backward, the 200-step pilot, full training, inference, AP evaluation, or checkpoint comparison;
- modify V40--V51 evidence, protected training-core files, or manuscript files.

GPU optimizer steps must remain `0` and `pilot_gate.json` must remain locked.

## Stage 1 — Reproduce the Annotated-Only Contract

Audit the exact predicate that produced 9,138 included samples.

Create or update:

```text
runs/v52_mmuav_audit/annotated_only_protocol.md
runs/v52_mmuav_audit/annotated_only_protocol.json
runs/v52_mmuav_audit/annotated_only_status_counts.csv
runs/v52_mmuav_audit/annotated_only_integrity.md
```

Report exact counts for:

- RGB GT present;
- IR GT present;
- both RGB and IR GT present;
- RGB-only GT present;
- IR-only GT present;
- neither GT present;
- at least one valid source GT row;
- same-frame RGB/IR rows with at least one common track ID.

Also report train/devval sample counts and sequence counts for every status.

Requirements:

- reproduce exactly 9,138 included and 35,898 excluded rows;
- retain original interval-20 row IDs, source indices, sequence IDs, split membership, and paths;
- keep all no-GT rows as `UNLABELED`, never `EMPTY_TARGET`;
- fail closed and write `docs/TASK_BLOCKER.md` if the counts cannot be reproduced exactly.

Do not replace the frozen interval-20 manifest. Any annotated-only manifest is a filtered derivative with full traceability to the original row ID.

## Stage 2 — Exhaustive Local Provider-Evidence Search

Search all extracted MM-UAV files and locally available provider code/documentation for:

- `README`, license, citation, terms of use, dataset card, release notes, supplementary documentation;
- calibration matrices, intrinsic/extrinsic parameters, camera models, distortion coefficients;
- homography, affine, registration, rectification, warp, crop, resize, padding, ROI, coordinate-map, lookup-table, or correspondence files;
- timestamps, frame-rate files, synchronization tables, sensor offsets;
- official data loaders, conversion scripts, annotation parsers, visualizers, training/evaluation configs;
- GT cadence documentation and the meaning of absent frame rows;
- category names and all GT-column definitions;
- the official method's actual RGB/IR/event fusion path.

Search source file contents as well as filenames. Include common terms such as:

```text
align alignment registration calibration calibrate homography affine warp rectify rectification intrinsic extrinsic distortion transform coordinate crop resize pad roi timestamp sync gt annotation visibility occlusion truncation confidence class category license
```

Create:

```text
runs/v52_mmuav_audit/provider_contract_audit.md
runs/v52_mmuav_audit/provider_contract_audit.json
runs/v52_mmuav_audit/provider_evidence_inventory.csv
```

For every relevant artifact record:

- absolute or repository-relative path;
- SHA256;
- provider-controlled versus project-generated status;
- exact relevant line numbers, keys, or fields;
- the claim it supports;
- whether it is explicit evidence or only an inference.

Do not treat filenames, folder names, or comments from this project as provider contracts.

## Stage 3 — Official Repository and Publication Audit

When internet access is available, use only official or primary sources:

- the official MM-UAV repository;
- the official project page;
- the dataset paper and official supplementary material;
- files linked directly by those sources.

Do not rely on blogs, mirrors, reposted dataset descriptions, generated summaries, or third-party code as authoritative contracts.

Record stable source identifiers, retrieval timestamps, file hashes for downloaded text/code where practical, and precise sections or line ranges. Do not copy large media or archives into the repository.

If internet access is unavailable, state that clearly and complete the local audit without inventing results.

## Stage 4 — Distinguish Alignment Types

Create:

```text
runs/v52_mmuav_audit/alignment_source_audit.md
runs/v52_mmuav_audit/alignment_source_audit.json
runs/v52_mmuav_audit/alignment_candidate_inventory.csv
```

Classify every alignment-related finding as one of:

1. `PIXEL_SPACE_DETERMINISTIC_TRANSFORM`
2. `CALIBRATION_PARAMETERS_ONLY`
3. `FIXED_PREPROCESSING_WITHOUT_CALIBRATION`
4. `LEARNED_FEATURE_ALIGNMENT`
5. `TEMPORAL_SYNCHRONIZATION_ONLY`
6. `VISUALIZATION_ONLY`
7. `NO_ALIGNMENT_EVIDENCE`

For each candidate answer:

- which source and destination grids it maps;
- whether it applies to RGB-to-IR, RGB-to-event, IR-to-event, or all modalities;
- whether parameters are global, per sequence, or per frame;
- whether the provider supplies executable code and required inputs;
- whether it changes annotation coordinates;
- whether it was designed for detection or only tracking/feature fusion;
- whether it can be reproduced without fitting on V52 development-validation GT.

A learned feature-alignment block is not evidence that raw modalities can be directly channel-concatenated. A visualization resize is not calibration. Temporal synchronization is not spatial registration.

## Stage 5 — Optional CPU-Only Verification of an Official Deterministic Transform

Run this stage only when the provider supplies a deterministic transform or complete calibration recipe with all required parameters.

Implement a V52-only CPU verifier under `rarepdet/tools/` or `datasets/`. Do not modify the core model or trainer.

Verify on the already frozen geometry sample and report separately for train and development-validation:

- matched-track count;
- center displacement before and after transform;
- width/height ratio disagreement;
- IoU distribution before and after transform;
- invalid or out-of-bounds transformed boxes;
- sequence-level heterogeneity.

Do not fit or tune the transform on development-validation data. Do not select parameters based on the reported IoU.

Save:

```text
runs/v52_mmuav_audit/official_alignment_verification.md
runs/v52_mmuav_audit/official_alignment_verification.json
runs/v52_mmuav_audit/official_alignment_verification.csv
```

If no complete official deterministic transform exists, do not create a substitute. Record `NOT_RUN_NO_OFFICIAL_DETERMINISTIC_TRANSFORM`.

## Stage 6 — Sparse-GT, Category, and License Verdicts

Create:

```text
runs/v52_mmuav_audit/sparse_gt_contract.md
runs/v52_mmuav_audit/sparse_gt_contract.json
runs/v52_mmuav_audit/category_and_fields_contract.md
runs/v52_mmuav_audit/category_and_fields_contract.json
runs/v52_mmuav_audit/license_contract.md
runs/v52_mmuav_audit/license_contract.json
```

For each topic choose one status:

- `CONFIRMED_BY_PROVIDER`
- `PARTIALLY_CONFIRMED`
- `UNRESOLVED`
- `CONTRADICTORY_PROVIDER_EVIDENCE`

Sparse-GT evidence must explicitly answer whether a missing GT row means:

- unannotated frame;
- verified empty-target frame;
- interpolation expected;
- annotation only at a fixed cadence;
- another provider-defined rule.

Without explicit provider evidence, preserve the 35,898 rows as `UNLABELED`.

## Stage 7 — Final Decision

Update:

```text
runs/v52_mmuav_audit/feasibility_decision.md
runs/v52_mmuav_audit/feasibility_decision.json
runs/v52_mmuav_audit/claim_boundary.md
docs/EXPERIMENT_STATUS.md
docs/TASK_BLOCKER.md
runs/handoff_latest.md
runs/handoff_latest.json
runs/v52_mmuav_audit/pilot_gate.json
```

Choose exactly one audit outcome:

1. `OFFICIAL_REPRODUCIBLE_ALIGNMENT_FOUND_PILOT_STILL_LOCKED`
   - a complete provider-supplied transform/calibration is reproducible;
   - sparse-GT, category/field, and license contracts are reported separately;
   - a future task is still required before any GPU pilot.

2. `OFFICIAL_LEARNED_ALIGNMENT_ONLY_DIRECT_FUSION_NO_GO`
   - the provider relies on learned feature alignment but supplies no defensible raw-grid registration;
   - direct RA-RepDet channel concatenation remains invalid;
   - adding a learned alignment module would be a separate method-expansion task.

3. `NO_OFFICIAL_ALIGNMENT_DIRECT_FUSION_NO_GO`
   - no provider-supplied spatial alignment/calibration is found;
   - stop the MM-UAV training route for the current paper.

4. `BLOCKED_PROVIDER_EVIDENCE_INCOMPLETE`
   - the audit cannot access or interpret the required official evidence.

The pilot gate must remain:

```json
{
  "locked": true,
  "gpu_optimizer_steps": 0
}
```

Do not select `GO_TRI_MODAL_CONTROLLED_EXPERIMENT` in this task.

## Required Tests

Add or update V52-specific tests to verify:

- annotated-only counts reproduce 9,138 and 35,898 exactly;
- no unlabeled sample becomes an empty target;
- provider evidence records include path/source, hash, and evidence classification;
- alignment candidates cannot be promoted from visualization resize, temporal sync, or learned feature alignment to deterministic pixel registration;
- no development-validation GT fitting path exists;
- pilot gate remains locked;
- GPU optimizer steps remain zero;
- protected core and manuscript files are unchanged.

Save exact test commands and complete outputs. Do not change historical V51 evidence to satisfy a stale test assertion.

## Allowed Changes

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/v52_mmuav_audit/**`
- V52-only CPU audit/verifier tools under `rarepdet/tools/**`
- V52-only dataset audit helpers under `datasets/**`
- V52 tests under `tests/**`

## Forbidden Changes

- raw MM-UAV files and annotations;
- V40--V51 evidence;
- protected training-core files listed in `AGENTS.md`;
- model architecture, training runner, evaluator, thresholds, or checkpoints;
- manuscript files;
- any GPU operation or performance experiment;
- any transform learned or fitted from development-validation GT.

## Completion

Run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

Commit and push with:

```text
data: audit official MM-UAV alignment and provider contracts
```

The final report must state:

- starting and final commit SHA;
- exact annotated-only status counts;
- whether the 9,138/35,898 contract reproduced;
- official sparse-GT verdict;
- official category and GT-field verdict;
- official license verdict;
- every alignment candidate and its classification;
- whether a reproducible deterministic spatial transform exists;
- whether official code instead uses learned feature alignment;
- final audit outcome;
- pilot-gate state and GPU optimizer steps;
- tests and remaining blockers.
