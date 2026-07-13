# Experiment Status

Updated: 2026-07-13T21:17:16+08:00

## Active task

`V51_RUNNING_FULL_ROUTE_B`

V51 preserves the quarantined V50 evidence and uses a pre-registered Route-B group-disjoint cross-validation recovery protocol.

## Recovery audit

- Starting commit: `520443266fb1a917e50acfbd09772b4d74f6bb00`.
- All 29 V51 frozen artifact hashes and all V50 immutable evidence checks match.
- No V50 queue or RGB training process remains alive.
- Route A rejected: the local DET train/val/test-dev images all occur in V50; `seen_strict` is a subset, and the other VisDrone-named directories are derivatives/reference data.
- Selected route: `B_GROUP_DISJOINT_CROSS_VALIDATION`; no blind or independent-test claim is allowed.

## Frozen folds

- Fold 0: 5,761 train / 2,868 validation images; 212 / 109 groups.
- Fold 1: 5,677 train / 2,952 validation images; 215 / 106 groups.
- Fold 2: 5,820 train / 2,809 validation images; 215 / 106 groups.
- The 321 filename-sequence groups are disjoint within every fold and each image appears in validation exactly once.

## GPU execution

- Queue state: `RUNNING`; full design explicitly authorized by the user.
- Full frozen design: 3 folds x seeds 0/1/2 = 9 from-scratch 50-epoch runs, followed by 18 frozen-checkpoint fold evaluations.
- Estimated wall time on the local RTX 3090: 65-75 hours.
- Current run: fold 0, seed 0, from scratch.
- Queue PID: `45124`; active training PID at launch: `19816`.
- Started: `2026-07-13T21:17:16+08:00`.

## Claim boundary

V51 Route B is RGB-only cross-validation evidence, not an independent test or tri-modal external validation. V50 test metrics remain quarantined and are excluded from V51 selection and reporting.
