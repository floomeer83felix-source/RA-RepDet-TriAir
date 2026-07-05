# V40 Split Audit Report

- Generated: 2026-07-05T23:12:04
- Git commit: `042a321ee416712b18c11b0bde3ea7425549c545`
- Status: `V40_EXPANDED_ADJACENCY_SPLIT_READY_FOR_FROZEN_RERUN`
- Required wording: human-adjudicated adjacent-or-near-identical component
- Environment: Python 3.12.7 on Windows-11-10.0.26200-SP0

## Split Counts

- Train samples: 7439
- Validation samples: 2213
- Validation GT boxes: 5842
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
