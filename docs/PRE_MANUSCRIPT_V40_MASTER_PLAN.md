# Pre-Manuscript V40 Master Plan

## Purpose

This is the complete experimental and evidence-preparation plan to finish **before drafting a new manuscript**. It does not authorize article writing, manuscript edits, PDF generation, submission, or claims of independent testing.

This plan supersedes any earlier task note that conflicts with it. Older V38 and V39 results remain archival or exploratory evidence only. V40 v1 remains an archived split-integrity artifact and must not be used for model training because its validation-GT tie-break accounting is inconsistent.

The intended paper evidence is validation-only unless the separate independent-test branch is completed.

## Global rules

- Work on `research/ra-repdet-triair` only.
- Never use the guard partition for model selection, performance reporting, or test claims.
- Do not use DroneVehicle or any other external data in the V40 evidence pipeline.
- Do not change raw data, labels, model code, loaders, trainer core, evaluator core, or prior V38/V39 artifacts unless a later task explicitly authorizes a source-controlled correction.
- Do not use AP, F1, loss, predictions, confidence, checkpoints, or qualitative images to construct a split or choose training settings.
- Do not call any split `leakage-free`, any validation set `independent`, or filename IDs verified temporal metadata.
- Do not run `finish_task.ps1`.
- Do not stage, delete, or modify the two unrelated untracked DroneVehicle scripts.
- Every new report must record input paths, SHA-256 values, source commit, output commit, environment, script hashes, and PASS/FAIL/BLOCKED status.
- Checkpoints and raw data remain local; commit only lightweight configs, manifests, scripts, metrics, reports, and hashes.

## Status vocabulary

Use only these evidence descriptions:

- `human-adjudicated adjacent-or-near-identical component`
- `validation-only evidence`
- `expanded-adjacency component-disjoint split`
- `synthetic channel removal`

Do not use:

- leakage-free
- independent test
- held-out test
- verified temporal metadata
- sequence label
- real sensor-failure robustness

---

# Gate 0 — Correct and re-audit V40 split assignment

## Why this gate exists

V40 v1 separated all original and human-adjudicated graph components, but its assignment report has inconsistent validation-GT accounting. The corrected split must be built before any training.

## Required task

Execute:

```text
docs/V40_ASSIGNMENT_OBJECTIVE_CORRECTION_TASK.md
```

## Required outputs

Create a new immutable root:

```text
reproducibility/v40_expanded_adjacency_component_split_v2/
```

It must include source lock, extended graph, deterministic assignment, manifests, independent assignment-GT reconciliation, audit tables, status report, and rerun handoff.

## Pass criteria

- V40 universe is exactly the frozen V39 train-plus-validation universe: 9652 samples.
- Train and validation manifests have no overlap, no duplicates, and no missing samples.
- Original exact/pHash/dHash graph has zero train-validation edges and zero split components.
- Human-adjudicated adjacency graph has zero train-validation edges.
- Extended graph has zero train-validation edges and zero split components.
- Reported validation GT boxes equal an independent sum from final assignment rows.
- Reported validation-GT absolute difference equals the arithmetic absolute difference from frozen V39 validation GT boxes.
- The deterministic objective is replayable and uses, in order: validation-count difference, moved samples, validation-GT difference, and stable lexicographic component assignment.

## Gate status

Proceed only on:

```text
V40_V2_READY_FOR_FROZEN_RERUN
```

Any other status blocks all model runs.

---

# Gate 1 — Freeze the V40 v2 experiment contract

Before the first model run, create a single immutable experiment-contract report under:

```text
reproducibility/v40_experiment_contract_v1/
```

The contract must lock and hash:

- accepted V40 v2 train and validation manifests;
- dataset root and label-count method;
- model source commit and relevant file hashes;
- training command templates;
- 50 epochs, image size 640, batch size 4, learning rate 1e-4;
- optimizer, scheduler, augmentations, deterministic settings, and data-loader configuration;
- evaluator path/hash and standardized evaluation settings;
- class mapping and project-local AP definition;
- GPU/software environment;
- run seeds 0 and 2;
- output directory naming;
- selection rule;
- prohibited tuning actions.

Run a label-free configuration smoke test and a single short data-loader/model-forward smoke test. Do not train beyond the smoke-test allowance and do not record it as an experimental result.

The contract must state that no setting may be changed because of V40 validation performance.

---

# Gate 2 — Core V40 fusion comparison

Run every condition twice, with seeds 0 and 2, using the frozen V40 v2 contract.

## Required conditions

1. matched early fusion;
2. reliability-aware fusion with dropout `p=0.00`;
3. reliability-aware fusion with dropout `p=0.15`;
4. reliability-aware fusion with dropout `p=0.20`.

## Required run outputs

For each of the eight runs, record:

- frozen config;
- manifest SHA-256 values;
- source and evaluator hashes;
- environment;
- standardized evaluation JSON and CSV;
- Precision, Recall, F1, AP50, AP75, GT boxes, predictions, and checkpoint SHA-256;
- training completion status and failure logs if applicable.

Create a core summary with per-run results, two-run means, ranges, and standard deviations. Do not choose a model from a single run.

## Selection rule

Choose one reliability-dropout setting only after all six reliability runs complete:

1. highest two-run mean AP50;
2. then highest two-run mean F1;
3. then highest two-run mean AP75;
4. exact tie fallback: `p=0.00`, then `p=0.15`, then `p=0.20`.

Early fusion is a comparator and cannot win the reliability-dropout selection.

## Stop condition

If any run fails, uses a non-V40-v2 manifest, lacks standardized evaluation, or deviates from the frozen contract, report:

```text
V40_CORE_RERUN_INCOMPLETE
```

Do not selectively retry a weak-scoring run. Resolve a technical failure only by a documented full-contract rerun policy.

---

# Gate 3 — Fair modality and nonadaptive baselines

These baselines are required before manuscript drafting because the core matrix alone does not establish the contribution of tri-modal input or input-conditioned reliability weighting.

All baseline conditions use the same V40 v2 manifests, contract, training duration, evaluation settings, seeds 0 and 2, backbone family, feature stages, detector head, and class definition.

## Required single-modality baselines

1. RGB-only detector: RGB channels available; thermal and event channels deterministically zeroed.
2. Thermal-only detector: thermal channel available; RGB and event channels deterministically zeroed.
3. Event-only detector: event channel available; RGB and thermal channels deterministically zeroed.

These are trained detectors, not inference-only channel removals.

## Required nonadaptive fusion control

Implement one static-global-weight fusion control before training:

- same modality feature branches and detection head as reliability-aware fusion;
- three learned global fusion logits, shared by all samples, transformed by softmax;
- no input-conditioned reliability/gating computation;
- identical input/output interface and frozen V40 contract.

Report its exact parameter count and compute profile. Do not call it parameter-matched unless a source-level parameter audit proves equality without nonfunctional padding or architectural tricks.

## Baseline matrix

Run RGB-only, thermal-only, event-only, and static-global-weight fusion twice each with seeds 0 and 2.

Do not use these runs to replace or alter the already locked reliability-dropout selection rule. They support interpretation only.

---

# Gate 4 — Selected-setting robustness evaluation

After Gate 2 chooses the reliability setting, evaluate robustness without additional training or tuning.

## Required checkpoints

Use both final selected reliability checkpoints and both matched early-fusion checkpoints from Gate 2.

## Required synthetic channel-removal matrix

For each checkpoint, evaluate:

1. all modalities present;
2. RGB removed;
3. thermal removed;
4. event removed.

Use deterministic channel zeroing only. Do not alter model weights, threshold, NMS, or calibration. Aggregate across the two checkpoints per condition.

Report AP50, AP75, Precision, Recall, F1, GT boxes, prediction count, and deltas from all-modal input. Describe this strictly as synthetic channel removal, not physical sensor failure.

No condition may be selected because it performs well under removal.

---

# Gate 5 — Efficiency and resource measurement

Profile only the matched early-fusion baseline and the final selected reliability setting after Gate 2.

## Measurement protocol

- same GPU, driver, CUDA/PyTorch environment, precision mode, input size 640, batch size 1, and fixed tensor layout;
- disable training-time augmentation and dropout;
- use `torch.inference_mode()` and CUDA synchronization;
- 200 warm-up iterations;
- 1000 timed iterations per trial;
- five independent trials;
- report median and range across trials;
- measure raw model forward separately from end-to-end detector inference including preprocessing/postprocessing;
- report parameters, FLOPs or a documented FLOPs limitation, peak CUDA memory, raw forward latency, end-to-end latency, and throughput.

Do not infer a speed advantage from end-to-end runtime alone. If raw forward is slower, state that plainly.

---

# Gate 6 — Statistical and qualitative evidence pack

## Statistical analysis

For the final selected reliability setting versus matched early fusion on all-modal V40 validation:

- retain per-image predictions from the two fixed checkpoints;
- run a pre-specified image-level bootstrap with 2000 resamples;
- compute percentile 95% confidence intervals for AP50, AP75, and F1 differences;
- record the exact resampling unit, seed, implementation hash, and treatment of images with no GT boxes;
- do not use bootstrap results for configuration selection.

Do not report inferential claims beyond what the bootstrap supports.

## Qualitative protocol

Create a deterministic, non-cherry-picked qualitative package after all core and robustness results are frozen:

- choose eight V40 validation sample IDs by ascending SHA-256 of stable sample ID, with the selection script committed;
- render all-modal predictions for early fusion and selected reliability using the same score/NMS settings;
- optionally render the selected reliability model under one fixed synthetic channel-removal condition, but label it clearly;
- do not select images by apparent success, failure, confidence, loss, or visual attractiveness;
- preserve raw selected IDs, prediction files, and rendering script hashes.

This package is preparation evidence only; do not create manuscript figures yet.

---

# Gate 7 — Reproducibility, provenance, and repository truthfulness

Complete these before manuscript drafting.

## Reproducibility bundle

Create a source-controlled evidence bundle containing:

- V40 v2 manifests and hashes;
- V40 split and adjacency audit reports;
- frozen experiment contract;
- all core and baseline configs and summaries;
- selected-setting robustness and efficiency reports;
- statistical/qualitative scripts and manifests;
- environment lock or explicit dependency list;
- a clean reproduction entry point that performs configuration validation and smoke checks without requiring raw data or weights to be committed.

## Data provenance and availability ledger

Create a factual ledger for the Tri-modal UAV Detection Dataset / TriAir containing only verified information:

- dataset name and local alias;
- sample and annotation counts used in V40;
- source/provenance evidence available to the authors;
- license or access status, if verified;
- what can be shared publicly and what cannot;
- exact missing information, if provenance, URL, version, or license cannot be verified.

Do not invent a dataset citation, public URL, version, license, or availability claim. A lack of verified provenance must be preserved as a limitation and resolved with the data provider where possible.

## Documentation cleanup

Update stale public/repository status documents so they do not present V38 or V39 as current manuscript evidence. At minimum, make clear that:

- V38 is archival because confirmed adjacent observations crossed its train-validation boundary;
- V39 is exploratory because the stronger human-adjudicated adjacency rule was not yet used;
- V40 v2 is the only candidate evidence package for the new manuscript once all later gates pass;
- guard is archival only and is not an independent test set.

Do not edit a manuscript in this phase.

---

# Gate 8 — Independent tri-modal test branch

This branch is strongly recommended before a new submission and is mandatory for any claim of independent or cross-site generalization. It is separate from V40 validation-only evidence.

## Before collection or labeling

Create and lock an independent-test protocol that specifies:

- acquisition sites, sessions/dates, sensors, synchronization, calibration, coordinate system, and class definition;
- exclusion from all existing TriAir/V40 train, validation, guard, and review data;
- capture and annotation workflow;
- label lock and access control;
- a no-tuning rule after test data are available;
- pre-specified evaluator, metrics, bootstrap plan, and one-time final evaluation;
- evidence required to show it is a genuinely new tri-modal collection.

## Test execution

After the final V40 configuration and final checkpoints are frozen:

- run label-free pipeline smoke checks only;
- evaluate once on the locked independent test set;
- compute the same metrics and 2000-resample image-level confidence intervals;
- do not retrain, threshold-tune, or choose a new checkpoint from test results.

If this branch is not completed, the eventual manuscript must remain validation-only and cannot claim independent testing or external generalization.

---

# Final pre-manuscript readiness gate

Create:

```text
reproducibility/pre_manuscript_readiness_v1/
  readiness_matrix.csv
  readiness_report.md
  readiness_report.json
  evidence_index.csv
  limitation_register.md
```

The final report must state one of the following:

```text
PRE_MANUSCRIPT_VALIDATION_ONLY_READY
PRE_MANUSCRIPT_INDEPENDENT_TEST_READY
PRE_MANUSCRIPT_NOT_READY
```

`PRE_MANUSCRIPT_VALIDATION_ONLY_READY` requires Gates 0 through 7 to pass.

`PRE_MANUSCRIPT_INDEPENDENT_TEST_READY` requires Gates 0 through 8 to pass.

`PRE_MANUSCRIPT_NOT_READY` is required when any mandatory gate is missing, inconsistent, incomplete, or unverified.

No manuscript source, PDF, title selection, abstract, tables, figures, or submission package may be started until this readiness report exists and is not `PRE_MANUSCRIPT_NOT_READY`.

## Final completion response

For each completed gate, report only:

1. PASS/FAIL/BLOCKED status.
2. Input commit and output commit.
3. Output paths and SHA-256 manifests.
4. Core counts and metrics where applicable.
5. Whether training, evaluation, profiling, data, labels, code, or manuscript files changed.
6. Remaining gates and the next allowed action.
