# V40 Compute-Minimized Contract Amendment

- Status: `V40_COMPUTE_MINIMIZED_CONTRACT_READY`
- Generated: `2026-07-06T09:23:13`
- Input commit: `d463914f5b7df77d9624f574e01c54f75b38b83d`
- Output commit: `PENDING_FINAL_COMMIT_RECORDED_IN_GIT_HISTORY_AND_FINAL_RESPONSE`
- Original contract: `reproducibility/v40_experiment_contract_v1/contract/v40_experiment_contract.json`
- Original contract disposition: `archival evidence`
- New output root: `runs/v40_expanded_adjacency_v2_compute_minimized`

## Launch Scope

This amendment supersedes the older eight-run dropout sweep only for launch scope.
The original contract remains archival evidence for recipe, source, manifest, and smoke-test locks.

| Run ID | Model | Seed | Dropout | Role |
| --- | --- | --- | --- | --- |
| `matched_early_seed0` | `early` | `0` | `0.00` | `comparator` |
| `matched_early_seed2` | `early` | `2` | `0.00` | `comparator` |
| `reliability_p015_seed0` | `reliability` | `0` | `0.15` | `primary` |
| `reliability_p015_seed2` | `reliability` | `2` | `0.15` | `primary` |

## Pre-Specification

Reliability-aware p=0.15 is pre-specified from archived development evidence before any V40 result is viewed. It is not selected or optimized on V40.

## Replaced Selection Rule

No V40 dropout selection is performed. The paper comparison is limited to matched early fusion versus the pre-specified reliability-aware p=0.15 configuration.

Do not run p=0.00 or p=0.20 for this V40 compute-minimized launch scope.

## No Work Started

- `training_started`: `False`
- `metric_evaluation_started`: `False`
- `result_recorded`: `False`
- `checkpoint_created`: `False`
- `loss_or_validation_iteration_run`: `False`
- `profiling_started`: `False`
- `robustness_started`: `False`
- `qualitative_started`: `False`
- `manuscript_changed`: `False`
- `external_data_used`: `False`
- `dronevehicle_changed`: `False`
