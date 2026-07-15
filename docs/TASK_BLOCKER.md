# Task Blocker

Status: `V52_OFFICIAL_LEARNED_ALIGNMENT_ONLY_DIRECT_FUSION_NO_GO`

Generated: 2026-07-15

## Exact blocker

The official MM-UAV paper and pinned baseline commit use learned RGB/IR feature alignment: deformable-convolution offsets or an STN with fixed affine initialization plus a learned delta. They do not provide a complete deterministic RGB/IR/event raw-grid calibration recipe, source pair/keypoints, coordinate conventions, annotation transform, or event calibration. Therefore direct channel-aligned RA-RepDet fusion remains scientifically invalid and the CPU transform verification was not run.

The paper confirms sparse training annotation every 100 frames, independent RGB/IR boxes, and no event boxes. The official converter intersects RGB/IR annotated frame IDs. Neither source defines every absent row as a true empty target, so 35,898 rows remain `UNLABELED`. The official code confirms category `drone`, but the final three MOT-like fields remain incompletely defined. No explicit dataset-file license or research-use grant was found.

## Last execution lines

```text
Annotated-only included / UNLABELED: 9138 / 35898
Common-track RGB/IR frames: 8883
Official deterministic transform: NOT FOUND
Official learned feature alignment: FOUND
V52 tests: 9/9 PASS
GPU optimizer steps: 0
Pilot gate: LOCKED
Outcome: OFFICIAL_LEARNED_ALIGNMENT_ONLY_DIRECT_FUSION_NO_GO
```

## Attempted checks

1. Reparsed all 45,036 frozen interval-20 manifest rows and source RGB/IR GT files.
2. Preserved original row IDs, indices, paths, split, and sequence membership in a 9,138-row derivative manifest.
3. Audited the official project, arXiv v3 paper, baseline commit `5051e4451a2b66dba9128fb0f766832152e7d120`, and evaluation commit `a468fb66db9e67c00357e1bd3f169745c389bab7`.
4. Classified learned feature alignment, incomplete calibration parameters, temporal GMC, synchronization, resizing, and event crop expansion separately.
5. Kept official alignment verification at `NOT_RUN_NO_OFFICIAL_DETERMINISTIC_TRANSFORM`; no development-validation GT fitting occurred.
6. Ran 9 V52 CPU tests; protected core and manuscript paths were unchanged.

## Related files

- `runs/v52_mmuav_audit/annotated_only_status_counts.csv`
- `runs/v52_mmuav_audit/provider_evidence_inventory.csv`
- `runs/v52_mmuav_audit/alignment_candidate_inventory.csv`
- `runs/v52_mmuav_audit/sparse_gt_contract.json`
- `runs/v52_mmuav_audit/category_and_fields_contract.json`
- `runs/v52_mmuav_audit/license_contract.json`
- `runs/v52_mmuav_audit/official_alignment_verification.json`
- `runs/v52_mmuav_audit/pilot_gate.json`

## Repair options

1. Obtain an explicit provider dataset license plus a complete raw-grid RGB/IR/event calibration package and coordinate-transform specification; then schedule a new CPU verification task before any pilot.
2. Explicitly authorize a method expansion using learned cross-modal feature alignment and an annotated-only supervised protocol. This would be a new experimental design and still requires a separate GPU decision.
