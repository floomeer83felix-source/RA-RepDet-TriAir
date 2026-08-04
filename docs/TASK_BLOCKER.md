# Task Blocker

Status: `NO_ACTIVE_EVIDENCE_SOURCE_BLOCKER_V82_MANUSCRIPT_INTEGRATION_PENDING`

Updated: 2026-08-04

## Resolved decision

The previous blocker was a material discrepancy between the supplied V77/V80 single-modality table and the fresh checkpoint-backed V81 replication. On 2026-08-04 the author explicitly selected V81 as the authoritative evidence source.

## Authoritative evidence

- fresh V81 training: `9/9`, exactly 50 epochs each;
- standardized COCO evaluation: `9/9`;
- checkpoint epoch and SHA256: `9/9`;
- frozen validation split SHA256: consistent across `9/9`;
- guard access, tuning, seed replacement, selective rerun, checkpoint substitution: none.

The authoritative three-seed AP@[.50:.95] means are:

- RGB-only: `0.4473 ± 0.0033`;
- thermal-only: `0.5196 ± 0.0196`;
- event-only: `0.1949 ± 0.0012`.

## Historical evidence boundary

The supplied V77/V80 values remain archived only as author-provided historical evidence without checkpoint identity. They must not be mixed with, silently substituted for, or attributed to V81.

## Remaining work

There is no active experimental blocker. The remaining task is to build and audit a new V82 manuscript that uses V81 as the primary single-modality evidence. The root V78 manuscript remains active until that manuscript integration passes compilation and rendered-page review.
