# Task Blocker

## Current Task

Execute `docs/NEXT_TASK.md` on branch `research/ra-repdet-triair`:

**V40 — Repair, Freeze, and Validate a Truly Component-Disjoint TriAir Split.**

The immediate work is CPU-only deterministic split repair and strict auditing. GPU training for R4 `p=0.20` seeds 0 and 2 is conditionally allowed only after the new split passes every cross-partition component, exact-RGB, and same-family guard-band criterion.

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

A failed V40 audit is a valid blocked outcome. It must be committed with quantified diagnostics, refreshed handoff/status, and no GPU run.

## What Is Blocked

Until V40 passes, do not:

- train R4 `p=0.20` on the V39 candidate split;
- relabel V39 as clean, component-disjoint, or manuscript-grade evidence;
- replace the official R4 `block64_guard16_seed0` manuscript headline;
- edit manuscript sources, Tables 1--7, figures, submission metadata, author declarations, or release records;
- commit raw data, `.npy` samples, checkpoints, weights, prediction dumps, or visual artifacts.

## Required Follow-On Evidence

After V40, the research-evidence queue is V41 public-protocol baseline/cross-dataset feasibility, V42 realistic degradation stress tests, V43 three-seed uncertainty extension, V44 qualitative error taxonomy, and V45 evidence reconciliation. See `docs/SCI_EVIDENCE_STRENGTHENING_PLAN.md` and `docs/UPCOMING_TASKS.md`.

## Branch Discipline

All V40--V45 work must remain on `research/ra-repdet-triair` unless the user explicitly approves a different branch strategy. Use fast-forward pulls only; do not reset, force-push, or rewrite history.
