# Clean Block64G16 Protocol

Generated: 2026-06-23T10:57:04

## Candidate

- Candidate: `block64_guard16_seed0`
- Source: `runs/blocked_split_proposal_summary.csv`
- These files are used directly for Phase 4A clean-split training and validation.
- Guard samples are excluded from both training and validation inputs.

## Frozen List Files

| Split | Path | Count | SHA256 |
| --- | --- | --- | --- |
| train | `E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt` | 7439 | `c4d94e5b376e862c3875314d39d79149988c479f12e97a6fcbeea72d3dfa85e5` |
| validation | `E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt` | 2213 | `a48aff2ee29d041bd07b746947028191475a59f0df6b7b64d4882cd610746dc4` |
| guard | `E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_guard.txt` | 837 | `25a57cea733a218ce2bbd37b22acdf76722cdcc3856861020017340357b338a8` |

## Integrity Checks

| Check | Result |
| --- | --- |
| train count equals 7439 | pass |
| validation count equals 2213 | pass |
| guard count equals 837 | pass |
| train/validation/guard list overlap | none |
| exact RGB-content train/validation matches | 0 |
| exact RGB-content group count | 0 |
| same-family guard-band violations | 0 |

## Candidate Summary Row

| Metric | Value |
| --- | --- |
| train_images | 7439 |
| val_images | 2213 |
| guard_images | 837 |
| train_gt_boxes | 22443 |
| val_gt_boxes | 5904 |
| guard_gt_boxes | 2287 |
| val_share_all_images | 0.210983 |
| val_share_used_images | 0.229279 |
| nearest_signature_min | 2 |
| nearest_signature_p50 | 52 |
| nearest_signature_p90 | 74 |
| fraction_signature_le4 | 0.010845 |
| nearest_id_distance_min | 17 |
| nearest_id_distance_p50 | 38 |
