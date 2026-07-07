# V40 Validation-Only Manuscript Draft Task

## Entry condition

The V40 post-core package at commit `b37db7025413dd80016ac5d23f63e8e1737472e6` reports `PRE_MANUSCRIPT_VALIDATION_ONLY_READY`.

Draft a new manuscript from the V40-v2 evidence only. This task permits writing and controlled figure/table preparation. It does not permit new experiments, new training, split changes, tuning, external-data evaluation, guard evaluation, or use of V38/V39 metrics as manuscript results.

## Scope

The manuscript is validation-only. Use this title working version:

```text
Reliability-Aware RGB–Thermal–Event Fusion for Lightweight UAV Vehicle Detection with Expanded-Adjacency Component-Disjoint Validation
```

Use this central result framing:

```text
The pre-specified reliability-aware p=0.15 configuration is compared with matched early fusion on the V40-v2 expanded-adjacency component-disjoint validation partition.
```

Do not call p=0.15 V40-optimal. Do not call the data leakage-free. Do not call the validation partition independent, held-out test, external test, or test set.

## Evidence inputs

Read and cite internal artifact paths in a manuscript provenance note:

- V40-v2 split audit and manifests;
- compute-minimized contract amendment;
- four-run summary;
- channel-removal report;
- efficiency report;
- bootstrap report;
- qualitative packet;
- TriAir provenance ledger;
- pre-manuscript readiness report.

Use only these V40 two-run means in the main performance comparison:

```text
matched early: P 0.918769, R 0.871996, F1 0.894458, AP50 0.940841, AP75 0.820766
pre-specified reliability p=0.15: P 0.927328, R 0.899693, F1 0.913282, AP50 0.958569, AP75 0.875967
```

Use the bootstrap differences and percentile 95% CIs exactly as reported:

```text
AP50: +0.017728 [0.015256, 0.020348]
AP75: +0.055320 [0.048323, 0.062222]
F1: +0.018736 [0.014980, 0.022625]
```

State that bootstrap intervals are conditional on the two fixed checkpoints and are descriptive image-resampling uncertainty evidence, not model-selection tests.

## Required result interpretation

- The reliability system has higher two-run mean AP50, AP75, F1, precision, and recall than matched early fusion under the fixed V40-v2 validation protocol.
- The p=0.15 configuration was pre-specified from archived development evidence before V40 results; no V40 dropout sweep was performed.
- Synthetic channel removal is a deterministic zero-channel evaluation, not a physical sensor-fault experiment.
- In synthetic channel removal, report all-modal, RGB-removed, thermal-removed, and event-removed aggregates exactly; do not infer real deployment fault tolerance.
- Efficiency must state raw-forward and detector-inference boundaries separately. Reliability p=0.15 has modest additional parameters/compute/memory and must not be described as faster.
- The main paper comparison is system-level: reliability-aware architecture plus its locked p=0.15 modality-dropout training. Do not claim this comparison isolates the causal effect of gating alone.

## Mandatory limitations

Include an explicit limitations section covering:

1. validation-only evidence; no independent or external test;
2. expanded adjacency rule is based on exact/pHash/dHash candidates plus human-adjudicated adjacent-or-near-identical observations; it does not prove absence of every possible scene correlation;
3. filename numbers were not treated as verified temporal metadata;
4. p=0.15 was pre-specified; no V40 dropout optimization claim;
5. no trained single-modality baselines or static-global-weight control in the compute-minimized path;
6. synthetic channel removal is not measured physical sensor failure;
7. bootstrap is conditional on the two fixed checkpoints;
8. dataset public URL, license, version, redistribution terms, and temporal metadata remain unresolved unless authors verify them before submission.

## Tables and figures

Prepare only evidence-backed content:

- Table 1: V40-v2 split/audit protocol and scope.
- Table 2: two-run core comparison with mean, min-max range, and bootstrap difference CI.
- Table 3: synthetic channel-removal aggregates with deltas from all-modal mean.
- Table 4: efficiency with parameter count, GFLOPs, peak CUDA memory, raw-forward latency, and detector-inference latency; state boundaries in caption.
- Figure 1: method diagram derived from code, with no unsupported mechanism claims.
- Figure 2: deterministic qualitative packet only if the selected assets are accurately labelled as review examples and do not imply cherry-picking. Keep the selection rule in the caption or supplement.

Do not use old V38/V39 figures or tables. Do not use DroneVehicle results.

## Literature and data availability

Use verified scholarly references only. Do not invent citations, DOI, dataset source, license, URL, or availability statement.

Before final submission readiness, create an author-action note that requests confirmed data-provider facts for the data-availability statement. A draft may state that availability details are pending author verification; it must not claim public release without evidence.

## Source and output

Create a new manuscript root without overwriting archived V38/V39 sources:

```text
submission/sivp/v40_validation_only/
```

Use the existing Springer/SIVP source workflow already in the repository. Compile and inspect the PDF after each major revision. Keep manuscript source, BibTeX, figures, table generators, provenance note, and compilation log together.

## Prohibitions

- No new training, evaluation, profiling, bootstrap, channel-removal, split, or qualitative-selection experiment.
- No manuscript claim beyond validation-only scope.
- No guard performance.
- No use of external data or DroneVehicle.
- No modification of raw data, labels, model, loader, trainer, evaluator, V40 manifests, or archived V38/V39 evidence.
- Do not run `finish_task.ps1`.
- Do not touch unrelated DroneVehicle scripts.

## Completion status

Use one:

```text
V40_VALIDATION_ONLY_MANUSCRIPT_DRAFT_COMPLETE
V40_VALIDATION_ONLY_MANUSCRIPT_DRAFT_BLOCKED
```

The COMPLETE status means a technically compiled validation-only draft and evidence checklist exist. It is not a claim that the manuscript is ready for submission.

## Commit

Use:

```text
docs: add V40 validation-only manuscript draft
```
