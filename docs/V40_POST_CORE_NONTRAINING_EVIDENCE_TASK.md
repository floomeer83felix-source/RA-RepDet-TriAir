# V40 Post-Core Non-Training Evidence Task

## Authority and scope

This task starts only after `V40_FOUR_RUN_EXECUTION_COMPLETE` from commit `12a4b1c5a06cb0b862e8ef797a87ac5cfe557991`.

The four completed V40-v2 runs are the sole training evidence for the compute-minimized paper path:

```text
matched_early_seed0
matched_early_seed2
reliability_p015_seed0
reliability_p015_seed2
```

Reliability p=0.15 was pre-specified before V40 results. No V40 dropout sweep or V40 dropout selection was performed.

This is a non-training evidence task. Do not start any new model training, do not run p=0.00 or p=0.20, and do not change models, manifests, trainer, evaluator, raw data, labels, checkpoints, or manuscript files.

## Read first

1. `docs/V40_COMPUTE_MINIMIZED_EVIDENCE_PLAN.md`
2. `docs/V40_FOUR_RUN_EXECUTION_TASK.md`
3. `runs/v40_expanded_adjacency_v2_compute_minimized/V40_FOUR_RUN_EXECUTION_STATUS.json`
4. `runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json`
5. V40-v2 split audit and compute-minimized contract amendment.

## Inputs and checkpoint pairs

Use exactly these four fixed checkpoints:

```text
runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt
runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed2/weights/best.pt
runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt
runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed2/weights/best.pt
```

Use only the accepted V40-v2 validation manifest and the frozen standardized evaluator settings. Guard remains excluded.

## Global prohibitions

- No training, fine-tuning, threshold tuning, NMS tuning, calibration, checkpoint replacement, model selection, or seed selection.
- No p=0.00 or p=0.20 run.
- No DroneVehicle or external dataset.
- No guard-set evaluation or test claim.
- No manuscript source, PDF, figure, abstract, title, or submission update.
- No `finish_task.ps1`.
- Do not touch the two unrelated untracked DroneVehicle scripts.
- Do not call synthetic channel removal a physical sensor failure experiment.
- Do not claim leakage-free data, independent testing, verified temporal metadata, or V40-optimal dropout.

## Output root

Create:

```text
reproducibility/v40_post_core_evidence_v1/
  source_lock/
  channel_removal/
  efficiency/
  bootstrap/
  qualitative/
  reproducibility/
  provenance/
  readiness/
  scripts/
  reports/
```

Commit lightweight scripts, configs, aggregate CSV/JSON/Markdown reports, hashes, deterministic manifests, and rendered review assets only. Do not commit model weights, raw data, raw arrays, raw labels, or full per-image raw prediction dumps.

## Stage A — Source lock

Create a source-lock manifest with SHA-256 values for:

- V40-v2 train/validation manifests;
- V40 four-run summary and execution status;
- all four checkpoint hashes and paths;
- evaluator and metrics source files;
- model/data source files needed for inference;
- every new script;
- frozen environment record.

Record actual runtime environment before evaluation. Any mismatch from the frozen training environment must be reported. A meaningful mismatch blocks the affected result rather than being ignored.

## Stage B — Synthetic channel removal

For each of the four fixed checkpoints, run standardized V40 validation evaluation under these deterministic inputs:

1. all modalities available;
2. RGB removed: channels 0:3 zeroed;
3. thermal removed: channel 3 zeroed;
4. event removed: channel 4 zeroed.

Do not alter model weights, image size, threshold, NMS, evaluator, postprocessing, class mapping, or manifest. Use the same score and NMS settings as the core run.

For each checkpoint-condition record Precision, Recall, F1, AP50, AP75, GT boxes, predictions, checkpoint hash, evaluator hash, and manifest hash. Aggregate separately for matched early and pre-specified reliability p=0.15 over their two checkpoints. Report deltas from each model group's all-modal mean.

Required wording:

```text
synthetic channel removal
```

Required limitation:

```text
These deterministic zero-channel evaluations do not emulate measured physical sensor faults or real cross-sensor deployment failures.
```

## Stage C — Efficiency measurement

Measure only matched early and pre-specified reliability p=0.15 using the two fixed checkpoints per group.

Use the frozen training environment, GPU, batch size 1, image size 640, `torch.inference_mode()`, model eval mode, CUDA synchronization, and no training-time dropout.

For each checkpoint and model group:

- 200 warm-up iterations;
- five trials of 1000 timed iterations;
- raw model forward latency measured separately from end-to-end detector inference;
- report median, minimum, maximum, and throughput;
- report parameter count, peak CUDA memory, and FLOPs if available;
- if FLOPs cannot be measured reliably, state the tool, error, and limitation instead of guessing.

End-to-end inference must include a documented preprocessing/postprocessing boundary. Do not infer a raw model speed advantage from end-to-end runtime alone.

## Stage D — Bootstrap inference

Compare matched early against pre-specified reliability p=0.15 under all-modal V40 validation only.

Use both fixed checkpoints per group. Generate only the minimum local per-image prediction representation needed to bootstrap; do not commit raw prediction dumps. Record their file hashes, schema, and deletion/exclusion policy.

Pre-specify and execute:

- 2000 image-level resamples;
- one fixed bootstrap seed;
- percentile 95% confidence intervals for differences in AP50, AP75, and F1;
- exact resampling unit;
- treatment of images with no GT boxes;
- implementation hash and evaluator consistency checks.

Bootstrap is descriptive uncertainty evidence only. Do not use it to select a model or change a training decision. Do not make inferential claims beyond the reported intervals.

## Stage E — Deterministic qualitative evidence packet

Create a non-cherry-picked package for review, not manuscript figures.

Select eight V40 validation sample IDs by sorting stable sample IDs on SHA-256 and taking the first eight. Commit the selection script and manifest. Do not select by appearance, score, error, confidence, loss, or result quality.

Render all-modal predictions from both model groups using the same frozen score/NMS settings. Use a fixed visual convention and include sample IDs, model label, checkpoint grouping, and no qualitative claims. Optionally include one predeclared synthetic channel-removal condition, clearly labeled as such.

## Stage F — Reproducibility and provenance

Create a V40 evidence index that links all V40-v2 split, contract, amendment, four-run, channel-removal, efficiency, bootstrap, and qualitative artifacts with hashes and status.

Create a factual TriAir provenance and availability ledger. Include only verified information: dataset formal name and local alias, V40 sample and annotation counts, author-held provenance evidence, verified license/access facts, public-shareable assets, and unresolved provenance/version/URL/license gaps. Do not invent a citation, URL, license, version, or public-data claim.

Update repository status documents only where needed to prevent V38/V39 from being presented as current manuscript evidence. State V40-v2 as the candidate validation-only evidence package and guard as archival/non-test.

## Stage G — Readiness report

Create:

```text
reproducibility/pre_manuscript_readiness_v1/
  readiness_matrix.csv
  readiness_report.md
  readiness_report.json
  evidence_index.csv
  limitation_register.md
```

For the compute-minimized path, use one exact final status:

```text
PRE_MANUSCRIPT_VALIDATION_ONLY_READY
PRE_MANUSCRIPT_NOT_READY
```

A READY status requires: V40-v2 split audit pass, contract/amendment pass, all four core runs completed, channel removal complete, efficiency complete, bootstrap complete, deterministic qualitative packet complete, reproducibility/provenance work complete, and all limitations registered.

The READY status permits drafting only a validation-only manuscript. It does not permit independent-test or external-generalization claims.

## Stop conditions

Write `V40_POST_CORE_EVIDENCE_INCOMPLETE` and stop before readiness if a required stage fails, a required checkpoint is missing, runtime/evaluator consistency is unverified, or prohibited work occurs.

## Commit

Use:

```text
results: add V40 post-core evidence package
```

## Final response

Return only:

1. Completion status for Stages A–G.
2. Channel-removal aggregate results by model group.
3. Efficiency measurements with raw-forward and end-to-end boundaries stated.
4. Bootstrap CIs and exact resampling protocol.
5. Qualitative selection manifest and provenance/readiness output paths.
6. Final readiness status and commit SHA.
7. Confirmation that no new training, tuning, manuscript work, external data, guard evaluation, or DroneVehicle work occurred.
