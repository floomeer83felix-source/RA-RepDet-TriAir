# V39 Audit B: Filename-Proximity Diagnostic

- Generated: 2026-07-05T16:02:26
- Rule: same-family nearest train numeric ID within <= 16 for each validation sample.
- This is a diagnostic proxy only; it is not treated as proof of capture order.
- Selection uses filename family and numeric ID distance only, not model output, labels, or visual appearance.

## Metrics

| Metric | Value |
| --- | ---: |
| filename_proximity_pair_count | 353 |
| covered_by_original_candidate_graph | 0 |
| covered_by_reviewed_41_component | 0 |
| not_covered_by_original_graph | 353 |
| uncovered_cluster_count | 70 |
| human_review_shortlist_count | 70 |

## Review Package

- Full pair table: `filename_proximity_pairs.csv`.
- Uncovered full review package: `uncovered_filename_proximity_pairs.csv`.
- Cluster table: `uncovered_filename_proximity_clusters.csv`.
- Deterministic representative shortlist: `human_review_shortlist.csv`.
