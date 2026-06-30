# Blocked Split Proposal Summary

These are diagnostic candidate lists only. They do not replace `D:\download\triair\splits\train.txt` or `val.txt`.

## Recommendation

Recommended candidate: **block64_guard16_seed0**.

It is selected because it has zero exact RGB-content train/val matches, zero same-family guard-band id violations, and the closest validation share among viable candidates.

## Candidate Metrics

| candidate | block_size | guard_band | train_images | val_images | guard_images | train_gt_boxes | val_gt_boxes | guard_gt_boxes | val_share_all_images | val_share_used_images | exact_rgb_matched_val_images | exact_rgb_matched_train_images | exact_rgb_group_count | id_guard_violations | nearest_signature_min | nearest_signature_p50 | nearest_signature_p90 | fraction_signature_le4 | nearest_id_distance_min | nearest_id_distance_p50 | recommended |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| block64_guard16_seed0 | 64 | 16 | 7439 | 2213 | 837 | 22443 | 5904 | 2287 | 0.210983 | 0.229279 | 0 | 0 | 0 | 0 | 2 | 52 | 74 | 0.010845 | 17 | 38 | yes |
| block128_guard32_seed0 | 128 | 32 | 7308 | 2231 | 950 | 23547 | 5040 | 2047 | 0.212699 | 0.233882 | 0 | 0 | 0 | 0 | 8 | 48 | 74 | 0.000000 | 33 | 72 | no |
| block256_guard64_seed0 | 256 | 64 | 6983 | 2384 | 1122 | 20876 | 6557 | 3201 | 0.227286 | 0.254511 | 0 | 0 | 0 | 0 | 1 | 52 | 74 | 0.009648 | 65 | 137 | no |

## Local Candidate Lists

- Directory: `E:\RepViT-main\runs\blocked_split_candidates`
- Each candidate writes train, val, and guard text files using dataset-relative image paths.
- Guard samples are excluded from training for that candidate.
