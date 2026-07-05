# Split Integrity Summary

Data root: `D:\download\triair`
Train split: `E:\RepViT-main\runs\component_disjoint_candidates\candidate_component_disjoint_v1_train.txt`
Val split: `E:\RepViT-main\runs\component_disjoint_candidates\candidate_component_disjoint_v1_val.txt`

## Final Status

**CAUTION: near-duplicate or adjacent-frame review required**

Exact byte duplicates and path overlap are separated from near-duplicate signature similarity. A compact RGB perceptual signature can flag candidates for review, but no distance threshold proves leakage by itself.

## Summary Metrics

| Metric | Value | Notes |
| --- | --- | --- |
| train_count | 7439 | Existing split file rows. |
| val_count | 2213 | Existing split file rows. |
| path_overlap_count | 0 | Identical resolved paths in both splits. |
| exact_sha256_duplicate_pairs | 0 | Exact .npy byte duplicates across train/val. |
| numeric_id_parseable | yes | Numeric id parsed from final number in filename stem. |
| val_with_train_id_within_1 | 0.481699 | Fraction of val ids with a train id within +/- this distance. |
| val_with_train_id_within_2 | 0.503841 | Fraction of val ids with a train id within +/- this distance. |
| val_with_train_id_within_5 | 0.545413 | Fraction of val ids with a train id within +/- this distance. |
| val_with_train_id_within_10 | 0.569815 | Fraction of val ids with a train id within +/- this distance. |
| signature_distance_min | 0.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p01 | 6.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p05 | 14.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p10 | 20.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p25 | 32.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p50 | 50.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p75 | 64.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p90 | 74.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p95 | 78.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p99 | 84.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_max | 92.000000 | Hamming distance, 256-bit RGB pooled signature. |
| fraction_signature_distance_<=0 | 0.000452 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=4 | 0.005423 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=8 | 0.016268 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=16 | 0.064618 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=32 | 0.256213 | Fraction of val samples at or below threshold. |
| final_status | CAUTION: near-duplicate or adjacent-frame review required | Automatic audit label required by Phase 3B. |

## Closest-Pair Review

- Exact byte duplicate pairs, if any: `runs/split_integrity_exact_duplicates.csv`.
- Nearest train partner for every validation sample: `runs/split_integrity_nearest_pairs.csv`.
- Top 50 closest cross-split pairs for manual review: `runs/split_integrity_manual_review.csv`.
- Local-only panels created: 0.

Human review of the closest pairs is required when the final status is `CAUTION: near-duplicate or adjacent-frame review required`.
