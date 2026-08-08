# Codex Task Plan: V83 Post-V81 Weight Evidence Enrichment

## Objective

Use the newly authoritative checkpoint-backed V81 single-modality weights to strengthen reproducibility and the lightweight-system evidence **without retraining, retuning, replacing checkpoints, or mixing the historical V77/V80 supplied rows back into the manuscript**.

The active manuscript remains V82. V81 is the only authoritative single-modality weight/result source.

## Authoritative weight registry

Use only the nine entries in:

```text
runs/v81_single_modality_retraining_reconciliation/checkpoint_manifest.json
```

The registry contains RGB-only, thermal-only, and event-only seeds 0/1/2, retained checkpoint epoch, local `best.pt` path, checkpoint SHA256, the common validation split SHA256, and the frozen selection rule.

Common development-validation split SHA256:

```text
722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f
```

Do not substitute `last.pt`, another epoch, another seed, or a retrained checkpoint.

## Priority 0 — Weight integrity preflight (required)

Before any benchmark or evaluation:

1. locate all nine V81 `best.pt` files in the authorized local workspace;
2. recompute SHA256 for every file;
3. compare against `checkpoint_manifest.json`;
4. verify each checkpoint `input_mode`, seed, selected epoch, and model configuration;
5. fail closed if any identity differs;
6. write compact evidence to:

```text
runs/v83_post_v81_weight_evidence/weight_preflight.json
```

A failed hash or metadata check stops every downstream task. Do not repair identity by selecting a different file.

## Priority 1 — Uniform efficiency benchmark (recommended next experiment)

This task does not reopen the locked holdout and does not require labels.

### Purpose

The manuscript describes RA-RepDet as lightweight. Use the new V81 weights to create an auditable, hardware-fixed efficiency baseline for each single-modality architecture and, only when exact checkpoint identities are available, the matched-early and reliability-aware multimodal architectures.

### Fixed benchmark contract

- device: authorized RTX 3090 CUDA workspace;
- input size: 640 x 640;
- batch size: 1;
- precision: FP32 for the primary table;
- AMP/TensorRT/compile: disabled for the primary table;
- CUDA synchronization before and after timed inference;
- warm-up: 50 iterations minimum;
- timed inference: 200 iterations minimum per checkpoint;
- no dataloader time inside model-latency timing;
- synthetic tensors are preferred so this task does not touch the validation or holdout labels;
- record PyTorch, torchvision, CUDA runtime, GPU model, driver if available, Python version, and git commit.

### Required outputs

For every benchmarked checkpoint/model record:

- parameter count;
- trainable parameter count;
- input channels;
- mean latency;
- median latency;
- p95 latency;
- FPS derived from synchronized batch-1 latency;
- peak CUDA allocated memory;
- peak CUDA reserved memory;
- model/checkpoint SHA256 when a checkpoint is used.

If a verified FLOP/MAC profiler is already available, record FLOPs/MACs under a clearly named profiler/backend. If the profiler is unavailable or incompatible, do not estimate or invent FLOPs.

Store results under:

```text
runs/v83_post_v81_weight_evidence/efficiency/
```

Suggested files:

```text
runtime_environment.json
per_run.csv
summary.json
summary.md
```

### Seed handling

The architecture is unchanged across seeds, but run all three V81 seeds when practical so runtime reporting is not tied to a single arbitrary checkpoint. Do not interpret runtime variation as statistical model-performance evidence.

## Priority 2 — Locked internal holdout evaluation (high value, authorization-gated)

**Do not run this phase merely because this task file exists.** It reuses the previously locked 837-image internal holdout and therefore requires a separate explicit author instruction authorizing holdout reuse with the V81 weights.

If and only if that authorization is provided:

1. identify the exact existing V42 locked-holdout manifest; do not create a new split;
2. evaluate all nine V81 checkpoints exactly once on that fixed holdout;
3. use one frozen standardized COCO evaluator contract for AP@[0.50:0.95], AP50, AP75, AR1, AR10, and AR100;
4. do not select checkpoints, thresholds, epochs, or seeds using holdout results;
5. record checkpoint SHA256 and holdout-manifest SHA256 in every JSON;
6. preserve the existing disclosure that this holdout comes from the same provider archive and is not an independent public test;
7. disclose that the holdout has already been used in prior V42 analysis and is therefore not pristine after this additional reuse.

Store any authorized outputs under:

```text
runs/v83_post_v81_weight_evidence/locked_holdout/
```

### Fusion-versus-single-modality holdout comparison gate

Do not compare V81 single-modality holdout values numerically against earlier V42 fusion numbers unless all of the following are verified:

- the same 837-image manifest;
- the same GT interpretation;
- compatible evaluator definitions;
- exact retained fusion checkpoint identities;
- no threshold or checkpoint reselection.

If these conditions are not met, report the V81 holdout results separately and do not compute fusion-minus-thermal deltas.

## Priority 3 — Manuscript integration gate

V82 remains authoritative during V83 execution.

### If only the efficiency benchmark is completed

Create a new manuscript revision only if the efficiency evidence materially improves the lightweight claim. Add one compact efficiency table and hardware/profiling protocol. Do not change accuracy values.

### If locked-holdout reuse is separately authorized and completed

Integrate only after all nine runs complete and the evaluator/manifest/checkpoint identity audit passes. Treat the result as repeated internal-holdout evidence, not an independent test.

## Priority 4 — Submission closure

Regardless of optional V83 experiments, complete before submission:

1. final author names and order;
2. affiliations;
3. corresponding-author email/details;
4. ORCID fields;
5. live target-journal template and submission-portal requirements;
6. final PDF/source-package check.

## Prohibited actions

- no retraining;
- no fine-tuning;
- no learning-rate or schedule change;
- no threshold sweep;
- no checkpoint reselection;
- no `last.pt` substitution;
- no seed replacement;
- no selective rerun based on results;
- no numerical mixing with historical V77/V80 supplied rows;
- no statistical-significance claim from three seeds;
- no claim that the 837-image holdout is an independent external test;
- no physical sensor-failure robustness claim;
- no guard/locked-holdout access without explicit authorization for Priority 2.

## Recommended execution order

1. V83 weight integrity preflight.
2. V83 fixed-hardware efficiency benchmark.
3. Update evidence summary and decide whether efficiency deserves manuscript integration.
4. Only after separate author authorization, optionally run the V81 locked-holdout evaluator-only phase.
5. Final submission metadata and live journal checks.

## Recommended commit message

```text
docs: replan post-V81 weight evidence tasks
```
