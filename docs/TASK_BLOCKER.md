# Task Blocker

## Current Task

Execute `docs/NEXT_TASK.md` on branch `research/ra-repdet-triair`:

**V40 — Repair, Freeze, and Validate a Truly Component-Disjoint TriAir Split.**

The CPU-only deterministic split repair and strict audit have now passed. GPU training for R4 `p=0.20` seeds 0 and 2 is conditionally allowed by the audit gate, but it was not started in the current run because the user stated that the GPU already has another task running.

## Current V40 Status

| diagnostic | observed value |
| --- | ---: |
| status | AUDIT_PASSED_GPU_DEFERRED |
| complete inventory rows | 10489 |
| component count | 45 |
| largest component size | 4077 |
| train rows | 7439 |
| validation rows | 2213 |
| guard rows | 837 |
| deterministic rerun consistency | pass |
| final component-disjoint gate | PASS |
| train/validation path overlap | 0 |
| train/guard path overlap | 0 |
| validation/guard path overlap | 0 |
| train/validation exact RGB-content groups | 0 |
| train/guard exact RGB-content groups | 0 |
| validation/guard exact RGB-content groups | 0 |
| train/validation same-family distance-16 violation pairs | 0 |
| train/guard same-family distance-16 violation pairs | 0 |
| validation/guard same-family distance-16 violation pairs | 0 |
| component crossing count | 0 |

Evidence files:

- `runs/component_disjoint_v40/train.txt`
- `runs/component_disjoint_v40/val.txt`
- `runs/component_disjoint_v40/guard.txt`
- `runs/component_disjoint_v40/split_manifest.csv`
- `runs/component_disjoint_v40/split_manifest.json`
- `runs/v40_component_disjoint/split_audit.md`
- `runs/v40_component_disjoint/split_audit.csv`
- `runs/v40_component_disjoint/split_audit.json`
- `runs/phase_v40_component_disjoint_report.md`
- `runs/phase_v40_component_disjoint_report.json`

## Inherited V39 Failure

The V39 candidate component-disjoint split is not eligible for additional training. Its pre-run audit failed the explicit continuation gate.

| diagnostic | observed value |
| --- | ---: |
| train rows | 7439 |
| validation rows | 2213 |
| guard rows | 837 |
| train/validation path overlap | 0 |
| train/validation exact RGB-content groups | 0 |
| train/guard exact RGB-content groups | 4 |
| validation/guard exact RGB-content groups | 5 |
| same-family train/validation guard-band-16 violations | 353 |
| minimum same-family train/validation ID distance | 1 |
| V39 component-disjoint audit | FAIL |

The generic integrity audit also recorded a near-duplicate/adjacent-frame caution. No V39 R4 `p=0.20` training was started after the failure.

## V40 Continuation Gate

Before any GPU command, the replacement V40 split must prove all of the following:

1. every local sample is assigned once and only once to train, validation, or guard;
2. complete transitive components are assigned to only one partition;
3. pairwise train/validation/guard path overlaps are zero;
4. pairwise exact RGB-content overlap groups are zero;
5. pairwise same-family ID-distance-16 violations are zero;
6. repeated deterministic generation yields identical split SHA256 values; and
7. the audit has no unresolved error.

The current V40 audit passed all listed checks. The remaining work is deferred GPU execution, not an audit blocker.

## What Is Blocked

Until the deferred V40 GPU stage is explicitly resumed, do not:

- train R4 `p=0.20` on the failed V39 candidate split;
- start overlapping GPU jobs;
- run synthetic missingness, aggregate, or efficiency packaging before both V40 R4 seed runs and standardized evaluations complete;
- relabel V39 as clean, component-disjoint, or manuscript-grade evidence;
- replace the official R4 `block64_guard16_seed0` manuscript headline;
- edit manuscript sources, Tables 1--7, figures, submission metadata, author declarations, or release records;
- commit raw data, `.npy` samples, checkpoints, weights, prediction dumps, or visual artifacts.

## Required Follow-On Evidence

After V40, the research-evidence queue is V41 public-protocol baseline/cross-dataset feasibility, V42 realistic degradation stress tests, V43 three-seed uncertainty extension, V44 qualitative error taxonomy, and V45 evidence reconciliation. See `docs/SCI_EVIDENCE_STRENGTHENING_PLAN.md` and `docs/UPCOMING_TASKS.md`.

## Branch Discipline

All V40--V45 work must remain on `research/ra-repdet-triair` unless the user explicitly approves a different branch strategy. Use fast-forward pulls only; do not reset, force-push, or rewrite history.
