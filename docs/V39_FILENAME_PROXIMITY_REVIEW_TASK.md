# V39 Filename-Proximity Review Task

## Goal

Create a visual, human-reviewable package for all 70 filename-proximity clusters identified by the V39 audit-scope resolution. This task resolves whether the filename-proximity diagnostic reveals confirmed adjacent or near-identical cross-partition observations beyond the original exact/pHash/dHash candidate graph.

The task is review preparation and preliminary triage only. It is not a split-rebuild, training, evaluation, or manuscript task.

## Read first

1. `docs/V39_AUDIT_SCOPE_RESOLUTION_TASK.md`
2. `reproducibility/v39_audit_scope_resolution/V39_AUDIT_SCOPE_RESOLUTION.md`
3. `reproducibility/v39_audit_scope_resolution/original_candidate_rule/`
4. `reproducibility/v39_audit_scope_resolution/filename_proximity_diagnostic/`
5. `reproducibility/leakage_audit_v2/review_packet_v1/`, if present locally.

## Confirmed scope

- Audit A passed the original exact decoded-RGB / pHash<=4 / dHash<=4 candidate-component rule for V39 train/validation.
- Audit B found 353 same-family nearest-ID pairs within the <=16 diagnostic window, grouped into 70 uncovered clusters.
- Filename numeric ID is a diagnostic proximity proxy only. It is not verified capture-session metadata and must not be called a timestamp, sequence label, or leakage proof.
- The guard partition remains ineligible for independent-test use. It is outside this review task.

## Do not do

- Do not start p=0.20 training.
- Do not alter any split, model, training setting, evaluator, raw data, labels, manuscript, existing V39 result, or guard definition.
- Do not use prediction outputs, AP, loss, confidence, annotation counts, or visual quality to prioritize review.
- Do not rewrite the original candidate graph or claim that filename proximity is a replacement for it.
- Do not run `finish_task.ps1`.
- Do not commit raw arrays, checkpoints, or source data.

## Output root

Create:

```text
reproducibility/v39_filename_proximity_review_packet_v1/
  input_snapshot/
  manifests/
  cluster_overviews/
  pair_reviews/
  reviewer_forms/
  codex_preliminary_review/
  html_index/
  reports/
  scripts/
```

## Inputs and provenance

Freeze and record the following in `input_snapshot/input_lock_manifest.csv` and `input_snapshot/input_lock.md`:

- V39 train and validation manifests;
- `filename_proximity_pairs.csv`;
- `uncovered_filename_proximity_pairs.csv`;
- `uncovered_filename_proximity_clusters.csv`;
- `human_review_shortlist.csv` from the audit-scope resolution;
- original candidate-graph outputs;
- reviewed-41 component assignment table;
- current Git commit;
- SHA-256, byte size, original path, and snapshot path for each input.

## Cluster review package

Generate review material for every one of the 70 clusters.

For each cluster, create:

1. A cluster overview PNG containing representative train and validation observations.
2. A pair-review PDF with the selected representative pairs.
3. A machine-readable cluster manifest CSV or JSON.
4. One row in `reviewer_forms/filename_proximity_author_review.csv`.

Each visual page must visibly show only:

- partition: TRAIN or VALIDATION;
- sample ID;
- relative file path;
- filename family;
- numeric ID;
- ID distance;
- cluster ID.

Do not show model prediction, confidence, AP, loss, training setting, ground-truth count, annotation box, or any experimental result.

## Deterministic pair selection

For each cluster:

- include the minimum-ID-distance pair;
- include all pairs when the cluster contains 10 or fewer pairs;
- otherwise include the minimum-ID-distance pair and additional representative pairs chosen only by ascending ID distance and lexical pair ID;
- record the deterministic selection rule and the selected pair IDs in the cluster manifest.

Do not use model behavior, labels, annotations, or visual attractiveness in pair selection.

## Pair-relation semantics

Every pair and cluster output must keep these separate fields:

- `pair_is_original_candidate_graph_edge`
- `endpoints_in_same_reviewed_component`
- `one_or_more_endpoint_in_reviewed_component`
- `neither_endpoint_in_reviewed_component`

Do not describe a filename-proximity pair as covered by the old perceptual audit merely because one endpoint appears in one of the earlier reviewed components.

## Human-review form

Create `reviewer_forms/filename_proximity_author_review.csv` with at least:

- cluster_id
- preliminary_label
- author_final_label
- author_notes
- reviewed_by
- review_date
- requires_human_confirmation
- representative_pair_ids
- minimum_id_distance
- pair_count

Allowed final labels:

- `exact_duplicate`
- `adjacent_or_near_identical`
- `same_scene_distinct_observation`
- `false_candidate`
- `uncertain`

Use this fixed cluster-level precedence rule when summarizing completed author labels:

```text
exact_duplicate
> adjacent_or_near_identical
> uncertain
> same_scene_distinct_observation
> false_candidate
```

## Codex preliminary triage

Codex must inspect every cluster and write:

- `codex_preliminary_review/codex_preliminary_labels.csv`
- `codex_preliminary_review/codex_preliminary_review.md`
- `codex_preliminary_review/human_review_shortlist.csv`
- `codex_preliminary_review/codex_review_dashboard.html`

Every Codex-preliminary row must include:

```text
preliminary_automated_triage_only=YES
requires_human_confirmation=YES
```

Codex may rank clusters for review, but it must not fill `author_final_label`, `reviewed_by`, or `review_date` in the author form.

## Index and printable packet

Create:

- `html_index/index.html`
- `reports/v39_filename_proximity_human_review_packet.pdf`
- `reports/v39_filename_proximity_review_packet_summary.md`
- `reports/v39_filename_proximity_review_packet_summary.json`

The PDF and HTML index must provide a simple path to inspect each cluster without changing source data.

## Completion report

Report:

- total cluster count;
- total pair count;
- preliminary label counts;
- clusters marked high priority;
- source-lock status;
- paths to the author review CSV, HTML index, and print packet;
- current Git commit;
- confirmation that no training, split, manuscript, model, evaluator, or data change occurred.

Do not claim that filename proximity proves temporal leakage. The package only supports human adjudication.

## Commit

Commit only scripts, source-lock manifests, review forms, lightweight overview images, pair-review PDFs, HTML index, and reports.

Use:

```text
docs: add V39 filename proximity review packet
```
