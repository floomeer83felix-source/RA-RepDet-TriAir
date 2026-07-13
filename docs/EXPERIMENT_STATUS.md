# Experiment Status

Updated: 2026-07-13T20:18:31+08:00

## Active task

`V50_BLOCKED_TEST_ACCESS_ORDER_VIOLATION`

V50 audits the local RGB-only VisDrone-SEEN derivative and separates frozen TriAir-checkpoint stress evaluation from a dataset-specific true-RGB baseline.

## Dataset gate

- 8,629 RGB JPEG images with paired YOLO labels; linked original eight-column annotations restore ignored regions.
- Local generator provenance validated with zero image and zero label mismatches.
- Exact cross-split duplicates: 0; candidate filename-prefix train/devval overlaps: 24.
- Four-wheel mapping: car, van, truck, and bus -> one vehicle class.

## Frozen checkpoint stress result

- Status: `BLOCKED_TEST_ACCESS_ORDER_VIOLATION`.
- Zero-shot devval outputs exist, but test outputs were generated before the three RGB checkpoints were frozen.
- Test metrics are quarantined and are not accepted V50 final evidence.
- RGB seed 0 was stopped during epoch 1; seeds 1 and 2 never started.

## RGB baseline

- Queue state: `BLOCKED_TEST_ACCESS_ORDER_VIOLATION`.
- seed 0: `STOPPED_UNAUTHORIZED_EXPLORATORY_CONTINUATION`.
- seed 1: `PENDING`.
- seed 2: `PENDING`.

## Claim boundary

No final V50 performance claim is accepted while the test-order violation remains unresolved.

Disallowed: tri-modal external generalization, physical sensor-fault robustness, calibrated reliability, sequence-disjoint independent testing, statistical significance, universal causality, or optimal dropout.

## Evidence paths

- `runs/v50_visdrone_seen/dataset_audit.md`
- `runs/v50_visdrone_seen/source_lock_v50.md`
- `runs/v50_visdrone_seen/zero_shot_summary.md`
- `runs/v50_visdrone_seen/rgb_summary.json`
- `runs/v50_visdrone_seen/protocol_violation_evidence.json`
- `runs/v50_visdrone_seen/claim_boundary.md`
