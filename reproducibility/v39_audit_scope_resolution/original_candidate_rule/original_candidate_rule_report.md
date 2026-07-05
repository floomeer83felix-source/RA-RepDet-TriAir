# V39 Audit A: Original Candidate-Component Rule

- Generated: 2026-07-05T16:02:26
- Git commit: `578be1dd5f5633c01c47ed3606e48a651f20bdc6`
- Rule: decoded RGB exact match, pHash Hamming <= 4, dHash Hamming <= 4, connected components over the locked candidate graph.
- Preprocessing source: channels 0:3 from TriAir `.npy`; decoded RGB array SHA-256; 64-bit pHash and dHash from the locked leakage-audit script.
- The filename-ID rule is not used in Audit A.

## Metrics

| Metric | Value |
| --- | ---: |
| exact_decoded_rgb_train_validation_pairs | 0 |
| phash_le4_train_validation_pairs | 0 |
| dhash_le4_train_validation_pairs | 0 |
| candidate_graph_cross_split_edges | 0 |
| secondary_review_component_cross_split_edges | 0 |
| candidate_components_represented_in_both_train_validation | 0 |
| reviewed_components_total | 41 |
| reviewed_components_wholly_assigned_to_one_side | 41 |
| reviewed_components_split_across_train_validation | 0 |
| train_guard_exact_rgb_groups | 4 |
| validation_guard_exact_rgb_groups | 5 |
| missing_required_original_inputs | 0 |

## Interpretation

- Audit A passes the original exact/pHash/dHash component rule for train/validation if all cross-split pair, edge, and component counts are zero and all 41 reviewed components are wholly assigned to one side.
- Guard overlap disqualifies the guard partition from independent-test use, but does not by itself determine train/validation component integrity.
