# Experiment Status

Updated: 2026-07-15T08:41:00+08:00

## Active task

`V52_INTERVAL20_FROZEN_PILOT_BLOCKED`

## MM-UAV extracted subset

- Disk-full extraction produced 424 strictly complete source-train sequences and one incomplete sequence (`0512`).
- Sequence `0512` was moved without data loss to `D:\MM-UAV_incomplete_quarantine\train\0512` and excluded.
- Complete synchronized RGB/IR/event triplets: 897,578.
- User-authorized 1-based interval-20 rule: `1, 21, 41, ...`.
- Sequence-disjoint split: 339 train / 85 development-validation sequences.
- Frozen samples: 35,894 train + 9,142 development-validation = 45,036.

## Scientific blockers

- Only 9,138 sampled frames contain at least one source GT row; 35,898 have unresolved `UNLABELED_OR_EMPTY` status.
- GT cadence is predominantly `1, 101, 201, ...`; missing rows are not authorized as empty-target negatives.
- Native grids differ: RGB 640x360, IR 640x512, event 346x260.
- On 100 frames from 20 sequences, 215 same-track matches have mean IoU 0.00867 after dimension scaling; direct channel-aligned fusion is invalid.
- Provider/license, category semantics, and the final three GT fields remain unresolved.
- V51 remains incomplete with a stale `RUNNING` status and no active process.

## Verification

- V52 tests: 5/5 pass.
- Repository tests: 14/15 pass; the only failure is the pre-existing V51 assertion expecting `AWAITING_GPU_AUTHORIZATION` while its status records `RUNNING`.
- CPU loader benchmark: pass; GPU operations: 0.
- Pilot gate: locked.

## Decision

`NO_GO_DATA_OR_LICENSE_BLOCKER` for supervised interval-20 training. The file manifest is frozen and usable for CPU-side inspection, but not every row has a defensible target contract.
