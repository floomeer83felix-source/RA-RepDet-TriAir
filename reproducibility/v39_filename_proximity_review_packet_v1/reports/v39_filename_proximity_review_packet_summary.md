# V39 Filename-Proximity Review Packet Summary

- Generated: 2026-07-05T19:55:23
- Git commit: `8e4f314cacaee9427b69acc23af3c69ded51a1e6`
- Source-lock status: `PASS`
- Total clusters: 70
- Total filename-proximity pairs: 353
- Selected representative pairs in PDFs: 265
- Clusters marked high priority: 70

Filename numeric ID proximity is a diagnostic proxy only; it is not verified capture-session metadata and does not prove temporal leakage by itself.

## Preliminary Label Counts

| Label | Count |
| --- | ---: |
| exact_duplicate | 0 |
| adjacent_or_near_identical | 70 |
| same_scene_distinct_observation | 0 |
| false_candidate | 0 |
| uncertain | 0 |

## Review Paths

- Author review CSV: `reproducibility/v39_filename_proximity_review_packet_v1/reviewer_forms/filename_proximity_author_review.csv`
- HTML index: `reproducibility/v39_filename_proximity_review_packet_v1/html_index/index.html`
- Printable overview packet: `reproducibility/v39_filename_proximity_review_packet_v1/reports/v39_filename_proximity_human_review_packet.pdf`
- Per-cluster overview PNGs: `cluster_overviews/`.
- Per-cluster pair-review PDFs: `pair_reviews/`.

## Safeguards

- No p=0.20 training was started.
- No split, guard definition, model, evaluator, raw data, label, manuscript, existing V39 result, checkpoint, AP, loss, confidence, or prediction output was changed or used for prioritization.
- The author review form leaves `author_final_label`, `reviewed_by`, and `review_date` blank.
- Every Codex preliminary row has `preliminary_automated_triage_only=YES` and `requires_human_confirmation=YES`.
