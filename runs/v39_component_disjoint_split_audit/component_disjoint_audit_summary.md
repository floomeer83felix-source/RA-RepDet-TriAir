# V39 Component-Disjoint Split Audit

Data root: `D:\download\triair`

## Summary

| Metric | Value | Notes |
| --- | --- | --- |
| train_count | 7439 | train split row count |
| train_unique_paths | 7439 | train unique resolved relative paths |
| train_gt_boxes | 22416 | train total non-empty label rows |
| val_count | 2213 | val split row count |
| val_unique_paths | 2213 | val unique resolved relative paths |
| val_gt_boxes | 5931 | val total non-empty label rows |
| guard_count | 837 | guard split row count |
| guard_unique_paths | 837 | guard unique resolved relative paths |
| guard_gt_boxes | 2287 | guard total non-empty label rows |
| train_val_path_overlap | 0 | Identical relative paths across train and val |
| train_guard_path_overlap | 0 | Identical relative paths across train and guard |
| val_guard_path_overlap | 0 | Identical relative paths across val and guard |
| train-val_exact_rgb_group_count | 0 | Exact RGB-content hash groups present in both splits |
| train-guard_exact_rgb_group_count | 4 | Exact RGB-content hash groups present in both splits |
| val-guard_exact_rgb_group_count | 5 | Exact RGB-content hash groups present in both splits |
| same_family_train_val_guard_band_16_violations | 353 | Validation records with a same-family train ID within <=16 |
| same_family_train_val_nearest_id_min | 1 | Minimum same-family train/val ID distance |
| same_family_train_val_nearest_id_p50 | 32 | Median same-family train/val ID distance |
| component_disjoint_audit_status | FAIL | PASS requires counts, uniqueness, split disjointness, zero train-val exact RGB overlap, and zero same-family guard-band violations |

## Interpretation

- The generic split-integrity audit is retained in `split_integrity_summary.md`; its CAUTION status reflects near-signature similarity, not exact path or byte duplication.
- This component-disjoint audit is the gate used for V39 continuation: counts, uniqueness, split disjointness, exact RGB train/val overlap, and same-family guard-band violations.
