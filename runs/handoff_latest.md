# RA-RepDet-TriAir Handoff

Generated: 2026-07-13T21:17:16+08:00

## Current task

- Task: V51 clean VisDrone evidence recovery.
- Status: `V51_RUNNING_FULL_ROUTE_B`.
- Starting commit: `520443266fb1a917e50acfbd09772b4d74f6bb00`.
- Selected route: Route B, pre-registered group-disjoint cross-validation.
- Route A rejected because all local source DET partitions overlap V50; remaining VisDrone-named data are derivatives/reference data.

## Frozen protocol

- Three folds over 8,629 images and 321 filename-sequence groups.
- Validation fold sizes: 2,868 / 2,952 / 2,809.
- Full design: 9 fresh RGB 50-epoch runs plus 18 frozen-checkpoint evaluations.
- The user authorized the full design and the queue started at `2026-07-13T21:17:16+08:00`.
- Current run: fold 0, seed 0; queue PID `45124`, launch training PID `19816`.
- Estimated full-design wall time: 65-75 hours on the local RTX 3090.

## Integrity

- V51 tests: 4/4 pass.
- Frozen hashes: 29/29 match.
- V50 protocol-violation evidence remains immutable and quarantined.
- No V50 process is alive; the source-locked V51 queue is active.

## Claim boundary

Route B is cross-validation only, not an independent/blind test. RGB-only and zero-channel evidence cannot validate external thermal/event fusion or physical sensor failure.
