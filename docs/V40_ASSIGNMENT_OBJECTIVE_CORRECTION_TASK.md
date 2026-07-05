# V40 assignment-objective correction task

## Status

Do not start `docs/V40_FROZEN_RERUN_TASK.md`. The V40 v1 integrity audit passed, but its assignment report has an arithmetic inconsistency in the third tie-break metric.

The report states frozen V39 validation GT boxes = 5931 and V40 validation GT boxes = 5842. Their absolute difference is 89, not 63. The builder computes correction GT as an addition even when a pure-validation component is moved to TRAIN.

V40 v1 is archived as a split-integrity artifact but is not eligible for training until this deterministic-assignment accounting issue is corrected and independently audited.

## Scope

Build a corrected V40 v2 split under:

```text
reproducibility/v40_expanded_adjacency_component_split_v2/
```

Do not overwrite or delete any v1 output. Do not train, evaluate, profile, edit the manuscript, touch V39 results, or touch the two unrelated DroneVehicle scripts. Do not run `finish_task.ps1`.

## Fixed inputs

Use the same completed author review, V39 train/validation universe, locked original candidate graph, and all 353 approved human-adjudicated adjacency edges used by V40 v1. Do not alter thresholds or add new adjacency rules.

## Required correction

When computing final validation GT boxes:

- add GT boxes for components moved TRAIN -> VALIDATION;
- subtract GT boxes for components moved VALIDATION -> TRAIN;
- add zero for no correction.

The deterministic objective remains:

1. minimize absolute validation-count difference from 2213;
2. then minimize moved samples relative to V39;
3. then minimize absolute validation-GT difference from the frozen V39 validation GT count;
4. then choose the lexicographically smallest stable component bitstring.

## Mandatory checks

For the selected assignment, calculate validation GT boxes independently from the final assignment CSV and require all of these equalities:

```text
reported_validation_gt_boxes == sum(final_validation_assignment_gt_boxes)
reported_validation_gt_abs_diff == abs(reported_validation_gt_boxes - frozen_v39_validation_gt_boxes)
```

Write both the optimization-internal values and independently recomputed values. Any mismatch is `V40_V2_ASSIGNMENT_ACCOUNTING_FAILED` and stops the task.

Rebuild all graph, manifest, assignment, and audit files in the v2 root. The v2 split is ready only if every original-graph, human-adjudicated-edge, and extended-component cross-partition audit count is zero, and the accounting checks pass.

Record `input_commit` separately from the final result commit. Do not label an input commit as the output commit.

## Final status

Use exactly one:

```text
V40_V2_READY_FOR_FROZEN_RERUN
V40_V2_ASSIGNMENT_ACCOUNTING_FAILED
V40_V2_SPLIT_AUDIT_FAILED
```

Do not start model runs in this task.

## Commit

Commit only scripts, manifests, source locks, CSV/JSON/Markdown reports, and audits.

Use:

```text
fix: correct V40 split assignment accounting
```
