# SIVP revision experiment and reproducibility plan

## Purpose

This document defines the experiments, reproducibility artifacts, and manuscript replacements required before submitting the RA-RepDet TriAir study to *Signal, Image and Video Processing* (SIVP). It is a specification for Codex and human review. It does **not** authorize inventing, backfilling, or overwriting results.

The current manuscript results are development-validation results on the frozen `block64_guard16_seed0` split. The existing 837-image guard partition must become the final held-out test set after the protocol below is locked. Do not inspect, tune on, or select a model by guard/test results.

## Non-negotiable safeguards

1. Preserve all existing experiment artifacts and current reported values under a dated `results/legacy_validation/` folder. Do not overwrite any legacy CSV, JSON, checkpoint, or figure.
2. Never use the guard partition for hyperparameter selection, threshold selection, checkpoint selection, early stopping, normalization fitting, or data-augmentation decisions.
3. Before the first guard evaluation, commit a protocol lock containing model definitions, seeds, input preprocessing, training schedules, checkpoint-selection rule, and metric scripts. Record the commit SHA in every result file.
4. Treat all former random-split results as **diagnostic leakage analysis only**, not headline performance.
5. Do not upload raw TriAir sensor data unless its provider licence explicitly permits public redistribution. Split manifests, hashes, code, configs, and derived metadata may be released only within the provider's terms.

## Required repository structure

Create these paths if they do not exist:

```text
configs/sivp_revision/
scripts/reproducibility/
scripts/experiments/
splits/block64_guard16_seed0/
results/sivp_revision_2026/
results/legacy_validation/
docs/reproducibility/
```

Every executable script must support `--help`, use explicit paths, and write a machine-readable JSON summary in addition to a human-readable Markdown report.

---

# Work package 0: public reproducibility release

## 0.1 Replace the inherited upstream README

The root `README.md` currently describes upstream RepViT/RepViT-SAM rather than this RA-RepDet project. Replace it with a project-specific README that includes:

- title and one-paragraph study description;
- TriAir input format: RGB (3) + thermal (1) + event (1), stored as a five-channel tensor;
- exact environment setup and pinned dependency versions;
- how to obtain data legally; do not claim public redistribution without proof of licence;
- how to generate the frozen split manifests;
- how to run train, validation, guard test, leakage audit, baselines, robustness tests, and efficiency measurements;
- a results-reproduction table linking each paper table/figure to one config and one output file;
- a licence for code and a statement of any third-party data restrictions;
- citation metadata and contact information.

## 0.2 Versioned release material

Prepare, but do not fabricate, the following files:

```text
requirements.lock.txt or environment.yml
CITATION.cff
LICENSE
DATASET_PROVENANCE.md
REPRODUCIBILITY.md
```

`DATASET_PROVENANCE.md` must state the TriAir source, version, provider, licence/terms, whether redistribution is allowed, input alignment assumptions, RGB/thermal/event preprocessing, class mapping, and treatment of missing or empty label files. Leave an explicit `UNKNOWN - DO NOT CLAIM PUBLIC RELEASE` marker for any field that cannot be verified from source documentation.

## 0.3 Manual release step

A repository administrator must make the code repository public (or use an anonymous review-access route when appropriate), create an immutable release tag, and archive that release with a persistent identifier such as a Zenodo DOI before submission. Codex should create a `docs/RELEASE_CHECKLIST.md` but must not assert that these actions have occurred until verified.

---

# Work package 1: reproducible leakage audit and frozen split

## 1.1 Exact RGB-content audit

Implement `scripts/reproducibility/audit_rgb_content.py`.

Requirements:

- Decode each RGB input deterministically to canonical RGB pixel bytes; do not hash filenames, paths, compressed file bytes, or metadata.
- Define and record the canonical conversion and hash algorithm in the report. Prefer SHA-256 of the decoded RGB array after a deterministic dtype/channel-order conversion.
- Report exact train-validation duplicates by hash, with source path/id, duplicate group id, partition, and count.
- Output:

```text
results/sivp_revision_2026/leakage_audit/exact_rgb_hashes.csv
results/sivp_revision_2026/leakage_audit/exact_rgb_matches.csv
results/sivp_revision_2026/leakage_audit/leakage_audit_summary.json
results/sivp_revision_2026/leakage_audit/leakage_audit_report.md
```

- Acceptance criterion for the frozen clean split: zero exact RGB train-validation matches.
- Retain the historical random-split count separately; do not rewrite or hide the 153-match finding.

## 1.2 Family/group construction

Implement `scripts/reproducibility/build_group_manifest.py`.

The script must determine how `block64_guard16_seed0` assigns samples to groups/families from the actual available metadata. Do not infer family membership from filenames alone unless filenames are the documented source of sequence/frame identity.

The manifest must include at least:

```text
sample_id
source_path
sequence_id or source_group
frame_index or ordering_key
block_id
family_id
dataset_partition
label_status
rgb_sha256
```

Document the exact logic for:

- how 64-frame blocks are constructed;
- how the 16-unit guard separation is applied;
- how group/family boundaries are defined;
- how seed 0 is used;
- how unlabelled and empty-label samples are handled.

Outputs:

```text
splits/block64_guard16_seed0/group_manifest.csv
splits/block64_guard16_seed0/split_spec.yaml
splits/block64_guard16_seed0/split_fingerprint.json
results/sivp_revision_2026/split_audit/same_family_violations.csv
results/sivp_revision_2026/split_audit/split_audit_report.md
```

Acceptance criteria:

- 7,439 train images, 2,213 validation images, 837 guard images;
- 0 exact RGB train-validation matches;
- 0 same-family guard violations;
- no guard sample appears in train or validation.

## 1.3 Frozen split artefacts

Export deterministic, sorted manifests:

```text
splits/block64_guard16_seed0/train.csv
splits/block64_guard16_seed0/val.csv
splits/block64_guard16_seed0/guard.csv
splits/block64_guard16_seed0/README.md
```

`split_fingerprint.json` must include SHA-256 hashes of each manifest and the code commit SHA that generated them.

---

# Work package 2: final held-out guard evaluation

## 2.1 Protocol lock

Before guard evaluation, create and commit:

```text
configs/sivp_revision/guard_test_protocol.yaml
results/sivp_revision_2026/PROTOCOL_LOCK.md
```

The protocol must freeze:

- input resolution;
- all preprocessing and normalization;
- training augmentations;
- optimizer, learning-rate schedule, batch size, weight decay, mixed-precision setting, gradient clipping, and scheduler;
- model variants and exact architectural definitions;
- random seeds;
- validation-only checkpoint-selection rule;
- metrics, IoU thresholds, confidence threshold for F1, and NMS settings;
- hardware/software environment;
- no-guard-access rule before evaluation;
- command lines used for each run.

## 2.2 Guard evaluation

Retrain all model variants after the protocol lock. Use training data for fitting and the validation partition only for the frozen checkpoint rule. Evaluate each selected checkpoint once on the guard partition.

Minimum required variants:

1. `R0_early_fusion_5to3`
2. `R0_rgb_only_matched` - same RepViT-FCOS detector family, RGB-only input, matched training pipeline
3. `equal_weight_tri_modal` - three modality stems and projection, fixed weights 1/3 each, no reliability estimator
4. `R1_reliability_p0`
5. `R2_reliability_p015`
6. `R4_reliability_p020`
7. `common_gate_baseline` - a documented standard gate/attention baseline with the same input stems and detector stack; choose one implementable baseline and describe its equations/configuration clearly
8. `YOLO11n_rgb_external` - retain only as an external system-level baseline, never as the sole main comparator

Use at least three seeds (`0, 1, 2`). Target five seeds (`0, 1, 2, 3, 4`) if compute permits. Do not add or remove seeds after observing guard outcomes.

Required per-run outputs:

```text
results/sivp_revision_2026/guard_test/<variant>/seed_<seed>/metrics.json
results/sivp_revision_2026/guard_test/<variant>/seed_<seed>/predictions.*
results/sivp_revision_2026/guard_test/<variant>/seed_<seed>/run_manifest.json
```

Required aggregate outputs:

```text
results/sivp_revision_2026/guard_test/guard_metrics_per_seed.csv
results/sivp_revision_2026/guard_test/guard_metrics_summary.csv
results/sivp_revision_2026/guard_test/guard_test_report.md
```

Report at least:

- AP50;
- AP75;
- AP50:95 / mAP@[0.50:0.95];
- precision;
- recall;
- F1 at a stated confidence threshold;
- parameter count;
- mean and sample standard deviation over seeds.

The manuscript headline table must use guard-test metrics after this work package completes. The existing validation table may remain in a supplement as model-development evidence.

---

# Work package 3: diagnostic leakage effect

Re-run the frozen, pre-registered R0 and R4 protocols on:

- the former random split (diagnostic only), and
- the clean blocked validation split.

Use the same seeds, preprocessing, training schedule, and metric script for both. Report exact duplicate counts beside each split.

Required outputs:

```text
results/sivp_revision_2026/leakage_effect/leakage_effect_per_seed.csv
results/sivp_revision_2026/leakage_effect/leakage_effect_summary.csv
results/sivp_revision_2026/leakage_effect/leakage_effect_report.md
```

Required manuscript table columns:

```text
Split | Exact train-validation matches | Model | AP50 mean +/- SD | AP75 mean +/- SD | F1 mean +/- SD
```

The random-split row must be explicitly labelled `diagnostic; not used for model selection or headline results`.

---

# Work package 4: model and preprocessing specification

Create `docs/reproducibility/MODEL_AND_TRAINING_SPEC.md` and machine-readable config files that state the implementation exactly.

## Required details

### Data preprocessing

- original RGB, thermal, and event dimensions;
- geometric alignment/registration source and any transforms;
- RGB scaling and normalization;
- thermal conversion/scaling/normalization;
- event-channel construction from raw events or source arrays;
- resize/letterbox behaviour and label transformation;
- augmentation sequence and probabilities;
- handling of missing label files and the one empty label file;
- class mapping from source labels to detector labels.

### Architecture

- exact stem layer order, kernel size, stride, channels, activation, normalization, and initialization;
- reliability MLP input construction, hidden width, activation, output dimension, softmax dimension;
- projection layer details;
- backbone/checkpoint version, FPN, FCOS configuration, loss weights, anchors or anchor-free assignment settings;
- exact definition of R0, R1, R2, R4, equal-weight fusion, matched RGB-only, and common gate baseline;
- explanation: `R4` is a retained historical experiment identifier; `R3` was exploratory and is not part of the predefined controlled comparison. Do not renumber old outputs.

### Training and selection

- optimizer, learning-rate schedule, batch size, epochs, weight decay, warm-up, gradient clipping, AMP, worker count, deterministic flags;
- seed settings for Python, NumPy, PyTorch CPU/CUDA, and data-loader workers;
- validation checkpoint-selection rule;
- no-guard-access policy.

---

# Work package 5: robustness and efficiency

## 5.1 Missing-modality protocol

Keep the three synthetic zeroing conditions, but label them explicitly as controlled zero-input tests rather than real sensor-failure tests. Re-run the same conditions on the guard set for all applicable variants.

Report AP50, AP75, AP50:95, precision, recall, and F1 where supported. Include a short limitation statement that zeroing does not model all physical sensor failures.

## 5.2 Efficiency protocol

Implement `scripts/experiments/benchmark_efficiency.py` with:

- batch size 1;
- 100 warm-up iterations;
- 300 timed iterations per repeat;
- three repeats minimum;
- CUDA synchronization around timing;
- raw-forward and end-to-end detector profiles;
- data loading and file I/O excluded;
- peak allocated CUDA memory reported as the maximum across repeats.

Report latency and FPS as mean +/- sample SD; report peak memory as max over repeats. Use unambiguous table headings:

```text
R0 raw forward
R4 raw forward
R0 end-to-end detector
R4 end-to-end detector
```

Outputs:

```text
results/sivp_revision_2026/efficiency/efficiency_per_repeat.csv
results/sivp_revision_2026/efficiency/efficiency_summary.csv
results/sivp_revision_2026/efficiency/efficiency_report.md
```

---

# Work package 6: figures, tables, and manuscript integration

Do not replace empirical figures with synthetic imagery. Keep qualitative panels traceable to source image IDs and predictions.

## Required manuscript updates after results exist

1. Change every headline performance statement from `validation` to `held-out guard test` only after work package 2 succeeds.
2. Add a reproducible split-construction subsection that cites `split_spec.yaml`, manifests, and audit outputs.
3. Add an implementation-details table or compact subsection with the verified information from work package 4.
4. Replace the current external-only baseline emphasis with the matched baseline suite from work package 2.
5. Add the leakage-effect diagnostic table from work package 3.
6. Add AP50:95, precision, recall, and seed mean +/- SD in main or supplementary tables.
7. Replace the YOLO11 footnote with a proper numbered online reference including access date.
8. Update Data Availability with a real public repository URL, immutable release tag, persistent identifier/DOI, dataset citation, and licence statement. Do not claim a public release before it is actually public.
9. Ensure all figures are cited in order, captions have no terminal punctuation, and minimum lettering is 8-12 pt at final size.
10. Keep a separate `MANUSCRIPT_CHANGELOG_SIVP.md` mapping each manuscript change to an evidence file in `results/sivp_revision_2026/`.

---

# Completion gate

Codex must not mark the project submission-ready until all of the following are true:

- [ ] Split manifests reproduce 7,439 / 2,213 / 837 and pass both zero-violation checks.
- [ ] Guard-test protocol lock exists before guard metrics are produced.
- [ ] Guard results exist for all required matched baselines and seeds.
- [ ] Random-split leakage effect is reported only as a diagnostic.
- [ ] Model, preprocessing, and training details are fully documented.
- [ ] Code, configs, split manifests, audit scripts, and result logs have a versioned public release or a confirmed pre-submission public-release plan.
- [ ] The manuscript is regenerated from the official `sn-jnl` template, within the 10-page two-column limit.

## Expected human review points

- Verify TriAir provider, dataset licence, and redistribution permission before public data release.
- Approve the standard gate/attention baseline before compute begins.
- Confirm the final set of seeds before the guard protocol is locked.
- Review all changed author, data-availability, and contribution statements before submission.
