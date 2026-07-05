# V39 Audit-Scope Resolution

- Generated: 2026-07-05T16:02:26
- Git commit: `578be1dd5f5633c01c47ed3606e48a651f20bdc6`
- Status: `V39_ORIGINAL_COMPONENT_RULE_PASS_FILENAME_DIAGNOSTIC_PENDING`

## Decision

Audit A passes under the original exact/pHash/dHash candidate-component rule for the current V39 train/validation manifests.

Filename proximity remains an unresolved diagnostic risk: the 353 same-family nearest-ID candidates are not covered by the original perceptual candidate graph and require human review, or future claims must be narrowed to the fixed perceptual candidate rule.

Guard overlap disqualifies the guard partition from independent-test use, but does not by itself determine train/validation component integrity.

## Audit A: Original Candidate Rule

| Metric | Value |
| --- | ---: |
| exact decoded-RGB train/validation pairs | 0 |
| pHash <= 4 train/validation pairs | 0 |
| dHash <= 4 train/validation pairs | 0 |
| candidate-graph cross-split edges | 0 |
| candidate components in both train and validation | 0 |
| reviewed 41 components wholly assigned | 41 / 41 |

## Audit B: Filename-Proximity Diagnostic

| Metric | Value |
| --- | ---: |
| same-family nearest-ID candidates | 353 |
| covered by original perceptual graph | 0 |
| covered by reviewed 41 component | 0 |
| not covered by original graph | 353 |
| uncovered clusters | 70 |
| deterministic shortlist rows | 70 |

## Outputs

- Audit A outputs: `original_candidate_rule/`.
- Audit B outputs: `filename_proximity_diagnostic/`.
- No training, split change, manuscript edit, checkpoint change, raw-data change, or label change was performed.
