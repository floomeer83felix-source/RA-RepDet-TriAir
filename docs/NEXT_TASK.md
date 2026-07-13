# Current Task

## Title

V51 recover VisDrone-SEEN external evidence with a pre-registered clean evaluation protocol.

## Goal

Continue using the audited local dataset at:

```text
D:\datasets\visdrone_seen
```

while repairing the V50 test-access-order violation without deleting, rewriting, or reinterpreting the quarantined V50 artifacts.

V51 must establish one of two scientifically valid routes:

1. **Preferred route — untouched external partition:** locate and source-lock a genuinely untouched VisDrone-family evaluation partition that was not used by V50 for training, development, zero-shot evaluation, threshold selection, or result inspection.
2. **Fallback route — pre-registered group-disjoint cross-validation:** if no untouched partition exists, explicitly abandon the blind-test claim and run a frozen group/sequence-disjoint cross-validation protocol on the audited RGB-only dataset.

V51 must not describe the existing V50 test results as independent, blind, official, or final evidence.

## Starting State

The following V50 facts are frozen:

- the local dataset is RGB-only;
- 8,629 JPEG images and paired labels were audited;
- the V50 split contained 6,471 train, 548 development-validation, and 1,610 test images;
- V50 zero-shot test outputs were generated before the three dataset-specific RGB checkpoints were frozen;
- those test outputs are quarantined as protocol-violation evidence;
- RGB seed0 was stopped during epoch 1 and seeds1/2 were not started;
- no V50 final performance claim is accepted.

Read and preserve:

```text
docs/TASK_BLOCKER.md
runs/v50_visdrone_seen/protocol_violation_evidence.md
runs/v50_visdrone_seen/protocol_violation_evidence.json
runs/v50_visdrone_seen/source_lock_v50.md
runs/v50_visdrone_seen/source_lock_v50.json
runs/v50_visdrone_seen/dataset_audit.md
runs/v50_visdrone_seen/dataset_audit.json
runs/v50_visdrone_seen/split_manifest.json
runs/v50_visdrone_seen/claim_boundary.md
```

All V50 files are immutable inputs. Do not delete or overwrite the prematurely generated test metrics.

## Required Start

Before V51 work:

1. switch to and fast-forward the active branch;
2. record the starting commit SHA;
3. verify all V50 source-lock hashes and protocol-violation evidence;
4. confirm no V50 training process remains alive;
5. create a new output directory:

```text
runs/v51_visdrone_recovery/
```

V51 is an evidence-generation task. Do not edit the SIVP manuscript until V51 is complete and separately reviewed.

## Stage 1: Recovery Audit

Create:

```text
runs/v51_visdrone_recovery/recovery_audit.md
runs/v51_visdrone_recovery/recovery_audit.json
```

The audit must determine:

- every locally available VisDrone/VisDrone-SEEN/seen/unseen/test-dev companion directory under `D:\datasets` that may contain images or annotations not present in the 8,629-image V50 inventory;
- exact image-content hashes for every candidate partition;
- annotation and split-file hashes;
- whether candidate images overlap any V50 train/devval/test image by exact content;
- whether candidate IDs, sequence prefixes, videos, scenes, or source folders overlap V50 development data;
- whether any prior V50 command, log, result file, or cache references the candidate partition;
- whether labels are locally available and compatible with the frozen vehicle mapping;
- whether the partition has defensible source/provider provenance;
- whether `seen`/`unseen` terminology can be established from local evidence rather than guessed.

The audit may inspect file names, metadata, hashes, annotations, dimensions, category definitions, and local README/license text. It must not run model inference on a candidate final partition.

## Stage 2: Route Decision Gate

Write:

```text
runs/v51_visdrone_recovery/route_decision.md
runs/v51_visdrone_recovery/route_decision.json
```

### Route A — Untouched external partition

Route A is allowed only if all of the following are true:

- the candidate partition contains no exact image overlap with any V50 partition;
- it was not used in any V50 model command, result artifact, threshold choice, or checkpoint decision;
- its sequence/scene relationship to V51 training and development data is documented and acceptably separated;
- labels and category semantics are established;
- the partition can be frozen before any model inference;
- provenance supports the exact wording used in reports.

If these conditions hold, create immutable manifests:

```text
runs/v51_visdrone_recovery/manifests/train.txt
runs/v51_visdrone_recovery/manifests/devval.txt
runs/v51_visdrone_recovery/manifests/final_test.txt
runs/v51_visdrone_recovery/split_manifest.json
```

The existing quarantined V50 test partition must not be relabelled as the V51 final test.

### Route B — Group-disjoint cross-validation

Use Route B when no genuinely untouched external partition is available.

Route B must:

- explicitly abandon any blind-test or independent-test claim;
- create deterministic sequence/group-disjoint folds using the strongest available sequence, video, scene, or filename-prefix grouping;
- prevent neighboring or related frames from crossing train and validation folds;
- freeze all folds before any V51 training result is inspected;
- report cross-validation results only, not a held-out test result.

Preferred design:

```text
3 group-disjoint folds x seeds 0,1,2
```

If computation permits, use five group-disjoint folds. Any reduced design must be justified before training in the source lock.

Required fold files:

```text
runs/v51_visdrone_recovery/folds/fold_0_train.txt
runs/v51_visdrone_recovery/folds/fold_0_val.txt
runs/v51_visdrone_recovery/folds/fold_1_train.txt
runs/v51_visdrone_recovery/folds/fold_1_val.txt
runs/v51_visdrone_recovery/folds/fold_2_train.txt
runs/v51_visdrone_recovery/folds/fold_2_val.txt
runs/v51_visdrone_recovery/fold_manifest.json
runs/v51_visdrone_recovery/fold_integrity.md
```

No fold may be changed after a metric is observed.

## Stage 3: V51 Source Lock

Before any V51 result-producing command, create:

```text
runs/v51_visdrone_recovery/source_lock_v51.md
runs/v51_visdrone_recovery/source_lock_v51.json
```

Record:

- starting commit SHA and branch;
- selected route and justification;
- all dataset roots used;
- image, annotation, mapping, manifest, and fold hashes;
- exact vehicle class mapping and ignored-region handling;
- Python, PyTorch, torchvision, CUDA, driver, GPU, and OS versions;
- all relevant loader, model, training, evaluator, COCO metric, and gate-script hashes;
- exact training length, image size, optimizer, learning rate, batch size, seeds, checkpoint-selection rule, thresholds, NMS, and max detections;
- all six frozen TriAir checkpoint paths and hashes if zero-shot stress evaluation is retained;
- explicit statement that V50 quarantined test metrics are not inputs to V51 selection or reporting;
- exact final-test or fold-access rules.

## Stage 4: Hard Test-Access Gate

Route A must implement a technical gate, not only a written promise.

Create a wrapper that refuses to open `final_test.txt`, final-test annotations, or final-test image paths unless all required release conditions are satisfied.

Required files:

```text
runs/v51_visdrone_recovery/test_access_lock.json
runs/v51_visdrone_recovery/test_access_release.json        # created only at final release
runs/v51_visdrone_recovery/test_access_log.jsonl
```

Initial state:

```json
{"locked": true}
```

The release file may be created only after automated verification that:

- RGB seeds 0, 1, and 2 completed from scratch;
- all three selected checkpoint hashes are frozen;
- evaluator, preprocessing, class mapping, thresholds, and COCO metric hashes are frozen;
- no pending training or tuning process remains;
- development-validation reports and claim boundary are complete;
- the release command and timestamp are recorded.

After release, run all final-test evaluations in one controlled final stage. No result-dependent rerun, threshold adjustment, architecture change, or checkpoint replacement is allowed.

Route B does not use a test unlock. It must instead enforce immutable fold manifests and log every fold evaluation.

## Stage 5: Fresh Dataset-Specific RGB Baseline

Discard the interrupted V50 seed0 training as non-evidence. Do not resume its checkpoint.

Train a fresh pure-RGB RepViT-M0.9--FPN--FCOS baseline from scratch with seeds:

```text
0, 1, 2
```

Requirements:

- true three-channel RGB input;
- no pseudo thermal or event channels;
- input size 640;
- 50 epochs unless a pre-training source-lock amendment documents a resource constraint;
- checkpoint selection only by the frozen development-validation rule or the training fold's frozen validation partition;
- identical evaluator and canonical COCO convention across seeds/folds;
- exact commands, logs, runtimes, selected epochs, checkpoint hashes, and metrics.

Route A outputs:

```text
runs/v51_visdrone_recovery/rgb_train_commands.txt
runs/v51_visdrone_recovery/rgb_run_status.json
runs/v51_visdrone_recovery/rgb_devval_per_run.csv
runs/v51_visdrone_recovery/rgb_final_test_per_run.csv
runs/v51_visdrone_recovery/rgb_summary.md
runs/v51_visdrone_recovery/rgb_summary.json
```

Route B outputs:

```text
runs/v51_visdrone_recovery/cv_train_commands.txt
runs/v51_visdrone_recovery/cv_run_status.json
runs/v51_visdrone_recovery/cv_per_run.csv
runs/v51_visdrone_recovery/cv_fold_summary.csv
runs/v51_visdrone_recovery/cv_summary.md
runs/v51_visdrone_recovery/cv_summary.json
```

## Stage 6: Frozen TriAir-Checkpoint RGB-Only Stress Evaluation

The six frozen TriAir checkpoints may be retained as a separate zero-shot stress experiment:

- matched early fusion seeds 0/1/2;
- full reliability-aware `p=0.15` seeds 0/1/2.

Use the frozen adapter:

```text
input = [RGB, zero thermal channel, zero event channel]
```

This evaluates RGB-only domain shift and controlled missing modalities. It does not validate external RGB--thermal--event fusion, real sensor failure, calibrated reliability, or thermal/event transfer.

Route A ordering:

- verify adapter and annotation conversion on development-validation only;
- freeze all preprocessing and evaluator settings;
- do not evaluate the final test until the hard gate is released;
- evaluate all six checkpoints in the same final stage as the three RGB baselines.

Route B ordering:

- evaluate all six frozen checkpoints on every frozen validation fold;
- use identical fold membership and preprocessing for all checkpoints;
- report paired seed differences and fold-level heterogeneity.

Required outputs:

```text
runs/v51_visdrone_recovery/zero_shot_per_run.csv
runs/v51_visdrone_recovery/zero_shot_paired_deltas.csv
runs/v51_visdrone_recovery/zero_shot_summary.md
runs/v51_visdrone_recovery/zero_shot_summary.json
```

Negative, mixed, or near-zero results must be retained.

## Metrics

Report canonical `pycocotools` bbox metrics using the frozen convention:

- AP@[0.50:0.95];
- AP50;
- AP75;
- AR100;
- AP small/medium/large when area fields are valid;
- per-seed or per-fold values;
- descriptive mean and sample SD;
- paired matched-early versus full-RA deltas for the six frozen TriAir checkpoints.

Do not introduce significance claims unless separately authorized and statistically justified.

## Required Integrity Checks

Before training:

- verify zero exact image overlap across Route A train/devval/final-test partitions, or across Route B validation folds;
- verify group/sequence disjointness using available identifiers;
- verify class and ignored-region mapping;
- verify converted annotation geometry and image IDs;
- verify no final-test path can be opened while the gate is locked;
- verify V50 quarantined test outputs are excluded from all V51 summary builders.

Before final reporting:

- rerun all source-lock hashes;
- verify checkpoint hashes;
- verify every result row maps to a frozen manifest/fold and command;
- scan reports for prohibited claims;
- ensure no manuscript file changed;
- run repository preflight and `finish_task.ps1`.

## Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- new directory `runs/v51_visdrone_recovery/**`
- V51-specific dataset, split/fold, gate, training, evaluation, and reporting tools under `datasets/**` and `rarepdet/tools/**`
- pure-RGB model/training plumbing only where necessary
- tests under `tests/**`

## Forbidden Changes

- any raw file under `D:\datasets\visdrone_seen` or a candidate untouched partition;
- deletion, rewriting, or relabelling of V50 protocol-violation evidence;
- use of V50 quarantined test metrics for checkpoint, threshold, route, split, or narrative decisions;
- resuming the interrupted V50 RGB seed0 checkpoint;
- accessing a Route A final test before the hard gate release;
- random frame-level splitting when sequence/group information exists;
- pseudo thermal/event generation;
- TriAir holdout access;
- modification of V40--V50 frozen evidence packages;
- manuscript edits during V51;
- claims of official VisDrone benchmark status without provenance;
- claims of external tri-modal generalization, physical sensor-fault robustness, calibrated reliability, statistical significance, universal causality, or optimal dropout.

## Claim Boundary

Potentially allowed under Route A:

- external RGB-only aerial vehicle-detection evidence on a source-locked untouched partition;
- frozen-checkpoint RGB-only domain-shift and missing-modality stress results;
- three-seed dataset-specific RGB baseline results;
- exact statement of whether the partition is official, derived, seen, unseen, or locally constructed, based only on documented provenance.

Potentially allowed under Route B:

- pre-registered group-disjoint cross-validation evidence on the audited RGB-only dataset;
- fold- and seed-level descriptive results;
- frozen-checkpoint RGB-only stress comparisons across the same folds.

Always required:

- Route B is not an independent or blind test;
- RGB-only evidence does not validate thermal or event generalization;
- zero-filled channels are a controlled intervention, not a real sensor-failure simulation;
- V50 test metrics remain quarantined and are not final evidence;
- mixed and negative results are reported.

## Required Completion Outputs

- recovery audit and route decision;
- V51 source lock;
- immutable manifests or fold definitions;
- hard test-access gate and access log for Route A;
- fresh three-seed RGB baseline or precise resource blocker;
- six-checkpoint zero-shot stress evaluation under the selected route;
- canonical metric summaries;
- claim boundary and claim scan;
- preflight records;
- updated experiment status, blocker state, and handoff.

## Acceptance Criteria

- V50 protocol-violation evidence remains intact and quarantined;
- a route is selected before result-producing commands;
- Route A uses a genuinely untouched, non-overlapping final partition and enforces a technical access gate;
- Route B uses frozen group/sequence-disjoint folds and makes no blind-test claim;
- all RGB baselines start from scratch with seeds 0/1/2;
- no checkpoint, threshold, mapping, or split changes occur after protected evaluation begins;
- all numerical outputs are traceable to frozen commands, hashes, and manifests/folds;
- no TriAir holdout or manuscript file is accessed or modified;
- reports preserve the RGB-only and controlled-missing-modality interpretation boundary.

## Commit Message

```text
eval: recover V51 VisDrone evidence with a clean preregistered protocol
```

## Completion / Blocker Rule

On success, update `docs/EXPERIMENT_STATUS.md`, `runs/handoff_latest.md`, and `runs/handoff_latest.json`; clear `docs/TASK_BLOCKER.md` only if the selected V51 route is complete; run `rarepdet/tools/finish_task.ps1`; commit and push.

If no untouched partition and no defensible group/sequence split can be constructed, stop and write a blocker. Do not manufacture a blind test, do not reuse the quarantined V50 test as final evidence, and do not weaken the claim boundary.
