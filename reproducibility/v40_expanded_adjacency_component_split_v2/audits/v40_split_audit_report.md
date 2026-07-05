# V40 Split Audit Report

- Generated: 2026-07-05T23:53:27
- Input commit: `a484a6165d2ce4078f7e68dbb79debcaba04ba81`
- Output commit: `PENDING_FINAL_COMMIT_RECORDED_IN_GIT_HISTORY_AND_FINAL_RESPONSE`
- Status: `V40_V2_READY_FOR_FROZEN_RERUN`
- Required wording: human-adjudicated adjacent-or-near-identical component
- Environment: Python 3.12.7 on Windows-11-10.0.26200-SP0

## Split Counts

- Train samples: 7439
- Validation samples: 2213
- Validation GT boxes: 5867
- Reported validation GT boxes: 5867
- Frozen V39 validation GT boxes: 5931
- Reported validation-GT absolute difference: 64
- Independent validation-GT absolute difference: 64
- Assignment accounting pass: True
- Moved samples relative to V39: 122

## Edge and Component Counts

- Original edges: 8574
- Human-adjudicated edges: 353
- Extended components: 5515

## PASS Counts

- `sample_id_path_overlap`: 0
- `decoded_rgb_exact_pairs`: 0
- `phash_le4_pairs`: 0
- `dhash_le4_pairs`: 0
- `original_candidate_graph_cross_partition_edges`: 0
- `original_candidate_components_represented_in_both_partitions`: 0
- `human_adjudicated_adjacency_cross_partition_edges`: 0
- `extended_graph_cross_partition_edges`: 0
- `extended_components_represented_in_both_partitions`: 0
- `manifest_duplicates_or_missing_universe_samples`: 0

## Scope Confirmation

No training, evaluation, profiling, manuscript update, model change, evaluator change, raw-data change, label change, or V39 split/result change was performed.
