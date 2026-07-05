# V40 Expanded-Adjacency Component-Disjoint Split Task

## Purpose

Build and audit a new V40 training/validation split that extends the original exact/pHash/dHash candidate graph with the filename-proximity clusters that were manually adjudicated as adjacent or near-identical observations.

This is a split-construction and audit task only. It is not a training, evaluation, profiling, manuscript, or submission task.

V39 remains frozen as exploratory validation-only evidence. Do not overwrite its manifests, reports, checkpoints, or existing results.

## Scientific scope

The original V39 train/validation manifests pass the locked exact decoded-RGB, pHash<=4, dHash<=4 candidate-component rule. However, the subsequent filename-proximity review package identified 70 cross-partition clusters for human adjudication. The research owner has reviewed those clusters and reports agreement with the preliminary triage.

Do not call filename numeric IDs timestamps, session labels, verified temporal metadata, or proof of leakage. In V40 they are used only after human adjudication as an operational source of adjacency edges.

Use the phrase:

```text
human-adjudicated adjacent-or-near-identical component
```

Do not use:

```text
leakage-free
independent test
held-out test
sequence label
verified temporal metadata
```

## Read first

1. `AGENTS.md`, if present.
2. `docs/V39_AUDIT_SCOPE_RESOLUTION_TASK.md`
3. `docs/V39_FILENAME_PROXIMITY_REVIEW_TASK.md`
4. `reproducibility/v39_audit_scope_resolution/V39_AUDIT_SCOPE_RESOLUTION.md`
5. `reproducibility/v39_audit_scope_resolution/original_candidate_rule/`
6. `reproducibility/v39_filename_proximity_review_packet_v1/`
7. `runs/component_disjoint_candidates/`
8. Existing V39 train and validation manifests.

## Hard constraints

- Work only on branch `research/ra-repdet-triair`.
- Do not modify raw data, labels, model code, data-loader code, training code, evaluator code, original V38/V39 manifests, guard definition, existing V39 run outputs, or manuscript files.
- Do not run p=0.20 training or any other training/evaluation/profiling.
- Do not use AP, F1, loss, predictions, confidence, checkpoints, qualitative results, or external data to construct or choose the split.
- Do not use the guard partition for model selection, performance reporting, or as an independent test set.
- Do not hand-move individual samples. All assignments must be generated from the extended graph by a deterministic algorithm.
- Do not run `finish_task.ps1`.
- Do not commit raw arrays, checkpoints, raw labels, or large copied source data.

## Required human-review gate

The V40 graph may use only clusters with an actual completed human-review record.

Read:

```text
reproducibility/v39_filename_proximity_review_packet_v1/reviewer_forms/filename_proximity_author_review.csv
```

Before constructing V40, verify:

- exactly 70 expected cluster IDs are present;
- every row has a non-empty `author_final_label`;
- every row has a non-empty `reviewed_by` and `review_date`;
- every final label is one of the allowed labels;
- the CSV is consistent with the source-lock and cluster manifest IDs.

Create a final human-review summary from the completed author values. Codex must never populate, change, infer, or backfill `author_final_label`, `reviewed_by`, or `review_date`.

If the human-review form is incomplete or inconsistent, write:

```text
V40_HUMAN_REVIEW_GATE_BLOCKED
```

with the missing or invalid rows, and stop before graph construction.

## V40 output root

Create all new outputs under:

```text
reproducibility/v40_expanded_adjacency_component_split_v1/
  source_lock/
  human_review_summary/
  extended_graph/
  split_build/
  manifests/
  audits/
  reports/
  scripts/
```

Every text report must record the current Git commit, input paths, SHA-256 values, environment, script SHA-256 values, and whether a stage passed, failed, or was blocked.

## Stage A — Source lock and human-review summary

Create:

```text
source_lock/input_lock_manifest.csv
source_lock/input_lock.md
human_review_summary/final_filename_proximity_human_review.csv
human_review_summary/final_filename_proximity_human_review_summary.md
human_review_summary/final_filename_proximity_human_review_summary.json
```

Lock at minimum:

- V39 train manifest;
- V39 validation manifest;
- V39 guard manifest for archival reference only;
- original exact/pHash/dHash graph nodes, edges, components, and reviewed-41 assignment table;
- filename-proximity cluster and pair manifests;
- completed author review CSV;
- V39 audit-scope resolution report;
- scripts used to construct and audit the V40 graph.

The human-review summary must report exact label counts and explicitly list the cluster IDs that will create V40 adjacency edges. A cluster creates V40 adjacency edges only when `author_final_label` is `exact_duplicate` or `adjacent_or_near_identical`.

Clusters labeled `same_scene_distinct_observation`, `false_candidate`, or `uncertain` must not be silently converted to adjacency edges. Record them separately.

## Stage B — Build the expanded adjacency graph

### B1. V40 graph universe

The graph universe is exactly the union of the frozen V39 train and validation manifests.

Expected universe size:

```text
7439 + 2213 = 9652 samples
```

The V39 guard manifest is excluded from the V40 performance universe. Keep it unchanged and report its known overlap limitations only as archival context.

### B2. Original graph edges

Include the locked original candidate graph edges generated by:

- decoded RGB exact match;
- pHash Hamming distance <= 4;
- dHash Hamming distance <= 4.

Do not recompute these rules with altered preprocessing or thresholds. Use the locked graph inputs where available and verify their hashes.

### B3. Human-adjudicated adjacency edges

For every filename-proximity cluster with a completed human final label of `exact_duplicate` or `adjacent_or_near_identical`:

- add the cluster's reviewed train/validation pair edges to the extended graph;
- union all endpoints connected by those edges;
- retain the source cluster ID and final human label on every added edge.

Do not add an edge merely because a sample ID is nearby. Only use the pair/cluster edges represented in the locked review packet and authorized by the completed author-review CSV.

### B4. Components

Construct connected components over the union of original graph edges and human-adjudicated adjacency edges.

Create:

```text
extended_graph/extended_nodes.csv
extended_graph/extended_edges.csv
extended_graph/extended_components.csv
extended_graph/component_membership.csv
extended_graph/component_provenance_summary.csv
extended_graph/extended_graph_build_report.md
extended_graph/extended_graph_build_report.json
```

For each edge, record at least:

- source type: `original_exact`, `original_phash`, `original_dhash`, or `human_adjudicated_filename_proximity`;
- source review/cluster ID when applicable;
- human final label when applicable;
- endpoint sample IDs;
- endpoint current V39 partition;
- whether it was cross-partition in V39.

For each component, record size, sample IDs, V39 partition composition, edge-source counts, and whether it contains any human-adjudicated adjacency edge.

## Stage C — Deterministic V40 split assignment

Construct a new train/validation assignment over the 9652-sample V40 universe. Each extended component is indivisible.

Target validation count:

```text
2213 samples
```

Do not use any metric, prediction, loss, or model result.

Use this deterministic lexicographic objective:

1. minimize `abs(new_validation_count - 2213)`;
2. among ties, minimize the number of samples whose partition differs from the frozen V39 train/validation assignment;
3. among ties, minimize `abs(new_validation_gt_box_count - frozen_V39_validation_gt_box_count)` using ground-truth box counts only;
4. among ties, select the lexicographically smallest component-assignment bitstring after components are sorted by stable component ID, where TRAIN=0 and VALIDATION=1.

If an exact optimizer is impractical, implement a deterministic algorithm and prove in the report that every tie-break is fixed, replayable, and independent of results. Do not introduce random seeds or manual overrides.

Non-component singleton samples may retain their V39 assignment unless changed by the deterministic optimization. No manual exceptions are allowed.

Create:

```text
split_build/v40_assignment.csv
split_build/v40_assignment_rationale.md
split_build/v40_assignment_rationale.json
split_build/v40_moved_samples.csv
split_build/v40_component_assignment.csv
```

## Stage D — V40 manifests and mandatory audits

Create manifests:

```text
manifests/v40_expanded_adjacency_component_disjoint_train.txt
manifests/v40_expanded_adjacency_component_disjoint_val.txt
manifests/v40_guard_unchanged_archival.txt
```

Then run a full audit using the locked original candidate graph and the new expanded graph.

Create:

```text
audits/v40_manifest_integrity.csv
audits/v40_original_candidate_rule_audit.csv
audits/v40_human_adjudicated_adjacency_audit.csv
audits/v40_extended_graph_integrity_audit.csv
audits/v40_exact_decoded_rgb_pairs.csv
audits/v40_phash_le4_pairs.csv
audits/v40_dhash_le4_pairs.csv
audits/v40_cross_partition_extended_edges.csv
audits/v40_cross_partition_extended_components.csv
audits/v40_split_audit_report.md
audits/v40_split_audit_report.json
```

The V40 split is a PASS only if all of the following are zero for train versus validation:

- sample-ID/path overlap;
- decoded RGB exact pairs;
- pHash<=4 pairs;
- dHash<=4 pairs;
- original candidate-graph cross-partition edges;
- original candidate components represented in both partitions;
- human-adjudicated adjacency cross-partition edges;
- extended-graph cross-partition edges;
- extended components represented in both partitions;
- manifest duplicates or missing-universe samples.

Also verify:

- train count plus validation count equals 9652;
- the V40 train/validation union exactly equals the frozen V39 train/validation universe;
- guard is unchanged and excluded from V40 performance claims;
- no new source data or labels were created or modified.

If any pass condition fails, state:

```text
V40_EXPANDED_ADJACENCY_SPLIT_BUILD_FAILED
```

and stop. Do not train.

If all pass conditions hold, state:

```text
V40_EXPANDED_ADJACENCY_SPLIT_READY_FOR_FROZEN_RERUN
```

This status means only that the split build and audit pass under the stated rule. It does not mean leakage-free or independently tested.

## Stage E — Final status and next-task handoff

Create:

```text
reports/V40_EXPANDED_ADJACENCY_SPLIT_STATUS.md
reports/V40_EXPANDED_ADJACENCY_SPLIT_STATUS.json
reports/V40_RERUN_HANDOFF.md
```

The handoff must state that no training has yet occurred and that the next task, if and only if V40 passes, is a frozen rerun of four variants on the V40 manifests:

1. matched early fusion;
2. reliability-aware fusion with p=0.00;
3. reliability-aware fusion with p=0.15;
4. reliability-aware fusion with p=0.20;

Each future variant requires two controlled independent runs under one locked training/evaluation protocol. The future final configuration must be selected only by two-run mean AP50, then F1, then AP75, with fixed fallback order p=0.00, p=0.15, p=0.20.

Do not create that rerun task or start any run in this task.

## Required checks

At minimum run and record:

```text
python -m py_compile <every new Python script>
python <split_builder_script> --help
python <split_audit_script> --help
```

Run the builder and audit on real locked inputs. Do not claim a pass from static code inspection.

## Git

Commit only lightweight scripts, manifests, CSV/JSON/Markdown reports, and source-lock records. Do not commit checkpoints, raw data, raw arrays, or model artifacts.

Use the commit message:

```text
docs: build V40 expanded adjacency split
```

## Final Codex response

Return only:

1. Human-review gate status and final label counts.
2. Number of original edges, human-adjudicated edges, and extended components.
3. V40 train/validation counts, validation GT boxes, and number of moved samples relative to V39.
4. Every V40 audit count required for PASS.
5. PASS or FAIL status.
6. Output paths and commit SHA.
7. A statement that no training, model, evaluator, manuscript, data, label, or V39 artifact was changed.
