# Task Blocker

Status: `V81_MANUSCRIPT_INTEGRATION_BLOCKED_MATERIAL_EVIDENCE_SOURCE_DIFFERENCE`

Updated: 2026-08-02

## Completed

- fresh V81 single-modality training: 9/9 runs, 50 epochs each;
- retained `best.pt`: 9/9, local only;
- standardized COCO evaluation: 9/9;
- checkpoint epoch and SHA256: 9/9;
- frozen validation split SHA256: consistent across 9/9;
- seed-matched reconciliation against supplied V77/V80 rows: complete;
- guard access, tuning, seed replacement, selective rerun, checkpoint substitution: none.

## Exact blocker

The V81 metrics differ materially from the supplied V77/V80 table. Examples at the three-seed mean level are:

- RGB AP@[.50:.95]: `0.4473` versus supplied `0.3073`;
- thermal AP75: `0.5776` versus supplied `0.6263`;
- event AP@[.50:.95]: `0.1949` versus supplied `0.1020`.

These are fresh retraining outputs and cannot establish the missing identity of the checkpoints behind the supplied table. The difference is not a rounding issue. No manuscript table was silently replaced.

## Resolution options

1. Use the checkpoint-backed V81 replication table as the reproducible single-modality evidence and transparently supersede the supplied V77/V80 rows.
2. Retain the supplied V80 table as author-provided evidence with explicit missing checkpoint/evaluator identity, and report V81 separately as a non-identical replication.

V78 remains the authoritative repository manuscript until an explicit evidence-source decision is made.
