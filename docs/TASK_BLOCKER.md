# Task Blocker

Status: `NO_ACTIVE_SUBMISSION_BLOCKER_V83_OPTIONAL_HOLDOUT_REUSE_GATED`

Updated: 2026-08-08

## Current state

V82 is complete and submission-capable after final author metadata and live journal checks. The new V83 plan is optional evidence enrichment based on the authoritative V81 weights; it is not required to make the current manuscript scientifically complete.

## Authorized work

- verify the nine V81 weight identities against the archived manifest;
- run a label-free fixed-hardware efficiency benchmark;
- archive runtime environment, latency, memory, parameter-count, and available profiler outputs;
- update compact evidence documentation.

## Authorization-gated work

The 837-image locked internal holdout may be reused with the V81 weights only after a separate explicit author instruction. This planning update does not authorize that access.

If holdout reuse is later authorized:

- no checkpoint, threshold, epoch, or seed selection may use holdout results;
- all nine V81 checkpoints must be evaluated under one frozen contract;
- the holdout must remain described as internal to the same provider archive and previously used in V42, not as a pristine or independent external test.

## Prohibited

- retraining or fine-tuning;
- hyperparameter/threshold sweep;
- `last.pt` substitution;
- checkpoint or seed replacement;
- selective reruns driven by results;
- numerical mixing with historical V77/V80 supplied rows;
- statistical-significance, independent-test, or physical sensor-failure claims.

## Remaining mandatory submission closure

1. Final author, affiliation, corresponding-author, and ORCID metadata.
2. Live target-journal formatting and submission-portal verification.
