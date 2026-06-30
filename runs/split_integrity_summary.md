# Split Integrity Summary

Data root: `D:\download\triair`
Train split: `D:\download\triair\splits\train.txt`
Val split: `D:\download\triair\splits\val.txt`

## Final Status

**CAUTION: near-duplicate or adjacent-frame review required**

Exact byte duplicates and path overlap are separated from near-duplicate signature similarity. A compact RGB perceptual signature can flag candidates for review, but no distance threshold proves leakage by itself.

## Summary Metrics

| Metric | Value | Notes |
| --- | --- | --- |
| train_count | 8391 | Existing split file rows. |
| val_count | 2098 | Existing split file rows. |
| path_overlap_count | 0 | Identical resolved paths in both splits. |
| exact_sha256_duplicate_pairs | 0 | Exact .npy byte duplicates across train/val. |
| numeric_id_parseable | yes | Numeric id parsed from final number in filename stem. |
| val_with_train_id_within_1 | 0.973308 | Fraction of val ids with a train id within +/- this distance. |
| val_with_train_id_within_2 | 0.994280 | Fraction of val ids with a train id within +/- this distance. |
| val_with_train_id_within_5 | 0.997617 | Fraction of val ids with a train id within +/- this distance. |
| val_with_train_id_within_10 | 0.999047 | Fraction of val ids with a train id within +/- this distance. |
| signature_distance_min | 0.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p01 | 0.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p05 | 0.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p10 | 0.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p25 | 4.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p50 | 8.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p75 | 14.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p90 | 22.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p95 | 30.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p99 | 74.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_max | 83.000000 | Hamming distance, 256-bit RGB pooled signature. |
| fraction_signature_distance_<=0 | 0.101049 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=4 | 0.322212 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=8 | 0.565300 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=16 | 0.823642 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=32 | 0.957579 | Fraction of val samples at or below threshold. |
| final_status | CAUTION: near-duplicate or adjacent-frame review required | Automatic audit label required by Phase 3B. |

## Closest-Pair Review

- Exact byte duplicate pairs, if any: `runs/split_integrity_exact_duplicates.csv`.
- Nearest train partner for every validation sample: `runs/split_integrity_nearest_pairs.csv`.
- Top 50 closest cross-split pairs for manual review: `runs/split_integrity_manual_review.csv`.
- Local-only panels created: 50.

Human review of the closest pairs is required when the final status is `CAUTION: near-duplicate or adjacent-frame review required`.
