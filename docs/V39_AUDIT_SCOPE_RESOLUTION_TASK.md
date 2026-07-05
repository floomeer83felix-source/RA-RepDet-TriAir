# V39 Audit-Scope Resolution Task

## Objective

Resolve what the current V39 manifests do and do not establish before any further training, aggregation, missing-modality evaluation, profiling, or manuscript update.

The immediate question is not whether V39 scores are high. The immediate question is whether the V39 train/validation manifests satisfy the *original* candidate-component-disjoint rule, and whether filename-ID proximity reveals an additional unresolved sequence-correlation risk.

## Do not do

- Do not start the missing reliability `p=0.20` runs.
- Do not change a split, model, training setting, evaluator, raw data, labels, guard partition, manuscript, or existing V39 result.
- Do not use the guard partition as a test set.
- Do not treat filename proximity alone as verified temporal metadata.

## Required audit A: original candidate-component rule

Use the same locked inputs, thresholds, preprocessing, and graph definition used for the prior perceptual candidate review:

- exact decoded RGB match;
- pHash distance at most 4;
- dHash distance at most 4;
- connected components over the resulting candidate graph.

For the existing V39 manifests, report:

1. exact decoded-RGB train/validation pairs;
2. pHash-at-most-4 train/validation pairs;
3. dHash-at-most-4 train/validation pairs;
4. candidate-graph cross-split edges;
5. candidate components represented in both train and validation;
6. whether every one of the previously reviewed 41 components is wholly assigned to one side;
7. input paths, hashes, scripts, preprocessing, thresholds, and commit SHA.

Write outputs under:

```text
reproducibility/v39_audit_scope_resolution/original_candidate_rule/
```

If the original graph inputs or exact prior preprocessing cannot be recovered, report `ORIGINAL_COMPONENT_AUDIT_BLOCKED` and identify the missing evidence. Do not silently substitute the filename-ID rule or a different signature.

## Required audit B: filename-proximity diagnostic

Treat the same-family numeric-ID distance rule as a diagnostic proxy, not proof of capture order.

Using the existing V39 manifests, characterize the 353 guard-band candidates by:

- family (`frame`, `nframe`, or other);
- ID-distance distribution;
- relation to the original perceptual candidate graph and reviewed 41 components;
- number of pairs already covered by a reviewed component;
- number of pairs not covered by the original graph;
- deterministic shortlist for human review.

Create a review package for the uncovered filename-proximity candidates. Cluster related pairs first, then use a fixed ordering based on family, minimum ID distance, and lexical sample ID. Do not select pairs by model output, labels, or visual attractiveness.

Write outputs under:

```text
reproducibility/v39_audit_scope_resolution/filename_proximity_diagnostic/
```

## Required decision report

Create:

```text
reproducibility/v39_audit_scope_resolution/V39_AUDIT_SCOPE_RESOLUTION.md
reproducibility/v39_audit_scope_resolution/V39_AUDIT_SCOPE_RESOLUTION.json
```

The report must choose exactly one status:

- `V39_ORIGINAL_COMPONENT_RULE_PASS_FILENAME_DIAGNOSTIC_PENDING`
- `V39_ORIGINAL_COMPONENT_RULE_FAIL`
- `V39_ORIGINAL_COMPONENT_AUDIT_BLOCKED`

It must separately state that guard overlap disqualifies the guard partition from independent-test use but does not, by itself, determine train/validation component integrity.

## Completion rule

No new V39 training is allowed until audit A is complete. If audit A passes, filename-proximity review must be completed or the future manuscript claim must be explicitly narrowed to the fixed perceptual candidate rule. If audit A fails, preserve V39 as exploratory evidence and prepare a new split-design task rather than patching individual samples.

## Commit

Commit only audit scripts, manifests, review materials, and reports. Do not commit checkpoints or raw data.

Use:

```text
docs: resolve V39 audit scope
```
