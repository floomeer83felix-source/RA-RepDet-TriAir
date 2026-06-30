# Phase 3C Report

## 1. Exact RGB-Content Cross-Split Duplicates

- Interpretation label: **CONFIRMED RGB-CONTENT CROSS-SPLIT DUPLICATION**
- Matched validation samples: 153 (0.072927)
- Matched train samples: 153 (0.018234)
- Cross-split RGB-content groups: 153
- This is an RGB-channel content audit only; it is not a full multimodal byte-duplication claim.

## 2. Publication-Grade Benchmark Suitability

The current random split should not be treated as a publication-grade independent benchmark, because exact RGB-content train/validation overlap exists even though full five-channel byte duplicates were not claimed.

## 3. Blocked-Split Candidate Recommendation

Recommended candidate: `block64_guard16_seed0` with block size 64 and guard band 16. It has 0 exact RGB matched validation samples, 0 same-family guard violations, 2213 validation images, and 5904 validation GT boxes.

## 4. E2/E4 Ranking Across RGB-Separation Strata

The strata are diagnostics only. The higher-RGB-separation subset is not a clean independent test set.

- higher_rgb_separation: E2 Reliability + Dropout 0.15 leads AP50 by 0.006075 over E4 Reliability + Dropout 0.20.
- near_rgb_match_or_near_neighbor: E4 Reliability + Dropout 0.20 leads AP50 by 0.001445 over E2 Reliability + Dropout 0.15.

## 5. Next Safe Action

Do not begin manuscript drafting or final 100-epoch runs on the current random split. Use the blocked-split recommendation for the next retraining phase. Retrain only E2 (p=0.15) and E4 (p=0.20) on this candidate in the next phase.

Keep E2 as the accuracy-first variant and E4 as the robustness-first variant until a clean blocked-split comparison is available.

## Key Tables

### RGB Duplicate Summary

| Metric | Value | Notes |
| --- | --- | --- |
| interpretation_label | CONFIRMED RGB-CONTENT CROSS-SPLIT DUPLICATION | Exact required Phase 3C label. |
| train_images | 8391 | Existing train split rows. |
| val_images | 2098 | Existing validation split rows. |
| exact_rgb_matched_val_images | 153 | Validation samples with at least one train sample sharing exact RGB content. |
| exact_rgb_matched_val_fraction | 0.072927 | Matched validation fraction. |
| exact_rgb_matched_train_images | 153 | Train samples with at least one validation sample sharing exact RGB content. |
| exact_rgb_matched_train_fraction | 0.018234 | Matched train fraction. |
| cross_split_rgb_groups | 153 | Distinct RGB-content hashes present in both splits. |
| group_total_size_min | 2 | Train+val samples per matched group. |
| group_total_size_p50 | 2 | Train+val samples per matched group. |
| group_total_size_max | 2 | Train+val samples per matched group. |
| group_val_size_p50 | 1 | Validation samples per matched group. |
| groups_identical_gt_box_counts | 123 | All records in the RGB group have one GT-box count. |
| groups_different_gt_box_counts | 30 | RGB group contains more than one GT-box count. |
| pair_id_distance_min | 1 | Representative exact RGB pairs, same filename family only. |
| pair_id_distance_p50 | 1 | Representative exact RGB pairs, same filename family only. |
| pair_id_distance_p90 | 1 | Representative exact RGB pairs, same filename family only. |
| train_gt_boxes | 24560 | Non-empty label rows in train split. |
| val_gt_boxes | 6074 | Non-empty label rows in validation split. |
| full_multimodal_byte_duplication_claim | not_claimed | This audit only hashes RGB channels; full 5-channel byte equality is not implied. |

### Blocked Split Candidates

| candidate | block_size | guard_band | train_images | val_images | guard_images | val_share_all_images | exact_rgb_matched_val_images | id_guard_violations | val_gt_boxes | recommended |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| block64_guard16_seed0 | 64 | 16 | 7439 | 2213 | 837 | 0.210983 | 0 | 0 | 5904 | yes |
| block128_guard32_seed0 | 128 | 32 | 7308 | 2231 | 950 | 0.212699 | 0 | 0 | 5040 | no |
| block256_guard64_seed0 | 256 | 64 | 6983 | 2384 | 1122 | 0.227286 | 0 | 0 | 6557 | no |

### RGB Separation Strata Evaluation

| subset | model | image_count | gt_boxes | precision | recall | f1 | ap50 | ap75 | predictions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| near_rgb_match_or_near_neighbor | subset_only | 676 | 1923 | NA | NA | NA | NA | NA | NA |
| higher_rgb_separation | subset_only | 370 | 1071 | NA | NA | NA | NA | NA | NA |
| near_rgb_match_or_near_neighbor | E2 Reliability + Dropout 0.15 | 676 | 1923 | 0.942552 | 0.964119 | 0.953213 | 0.984299 | 0.957422 | 1967 |
| higher_rgb_separation | E2 Reliability + Dropout 0.15 | 370 | 1071 | 0.909589 | 0.929972 | 0.919668 | 0.961141 | 0.915696 | 1095 |
| near_rgb_match_or_near_neighbor | E4 Reliability + Dropout 0.20 | 676 | 1923 | 0.954476 | 0.970359 | 0.962352 | 0.985744 | 0.958865 | 1955 |
| higher_rgb_separation | E4 Reliability + Dropout 0.20 | 370 | 1071 | 0.924157 | 0.921569 | 0.922861 | 0.955066 | 0.917360 | 1068 |
