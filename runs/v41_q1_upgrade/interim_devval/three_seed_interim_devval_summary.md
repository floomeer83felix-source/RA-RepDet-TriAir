# Three-Seed Interim Development-Validation Summary

Generated: 2026-07-09

Status: `V41_INTERIM_DEVVAL_CONSOLIDATION_COMPLETE`

This is a **three-seed interim development-validation descriptive summary**. It is not an independent-test result, statistical-significance result, external-generalization result, or manuscript-final aggregate.

## Inputs

- V40 seed0/seed2 source: `runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json`
- V41 fresh seed1 source: `runs/v41_q1_upgrade/seed1/seed1_per_run_summary.csv`
- V41 fresh seed1 source lock: `runs/v41_q1_upgrade/seed1/source_lock_seed1.json`

## Per-run rows

| Seed | Model group | Run | Source | Precision | Recall | F1 | AP50 | AP75 | Checkpoint SHA256 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | matched_early | matched_early_seed0 | V40 | 0.909154 | 0.895517 | 0.902284 | 0.945549 | 0.841093 | `23331a6e668634f5f1ca1c7dfaddd23e9ee5445c0558e325621e8f454a0b1602` |
| 0 | reliability_p015 | reliability_p015_seed0 | V40 | 0.933333 | 0.897222 | 0.914921 | 0.958361 | 0.895214 | `4284aaa188cb7f065a01b6cf32b78265ab937da0de2d3423d4594d2102787436` |
| 1 | matched_early | matched_early_seed1 | V41_seed1 | 0.860109 | 0.910687 | 0.884676 | 0.942953 | 0.794412 | `60a338ed887c15d94d3f274df39684c1dc6de68f9f29ba13f9f9cb4d6fbcd804` |
| 1 | reliability_p015 | reliability_p015_seed1 | V41_seed1 | 0.877880 | 0.928754 | 0.902601 | 0.955687 | 0.877982 | `a59366dd0687754577d23d3e21358127199345d4ebf3a55a06472b933b57813d` |
| 2 | matched_early | matched_early_seed2 | V40 | 0.928385 | 0.848475 | 0.886633 | 0.936133 | 0.800439 | `b36b4965931da68b77a6be82e85e47b34f952445d64b941337f56a722f62737e` |
| 2 | reliability_p015 | reliability_p015_seed2 | V40 | 0.921323 | 0.902165 | 0.911643 | 0.958777 | 0.856719 | `27affa96df1b3baad3df6f0a591e0599c1f5c0f77f91fad9fdaa408e549f1415` |

## Paired deltas: reliability p=0.15 minus matched early

| Seed | Precision | Recall | F1 | AP50 | AP75 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | +0.024180 | +0.001704 | +0.012637 | +0.012812 | +0.054121 |
| 1 | +0.017770 | +0.018067 | +0.017925 | +0.012734 | +0.083570 |
| 2 | -0.007062 | +0.053690 | +0.025010 | +0.022645 | +0.056280 |

## Descriptive delta mean ± sample SD across three seed pairs

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| precision | +0.011629 | 0.016501 | 3 |
| recall | +0.024487 | 0.026581 | 3 |
| f1 | +0.018524 | 0.006208 | 3 |
| ap50 | +0.016064 | 0.005699 | 3 |
| ap75 | +0.064657 | 0.016415 | 3 |

## Boundary

No new training, evaluation, checkpoint loading, raw data access, prediction-cache access, guard/test access, or manuscript rewriting was performed by this consolidation task.

Remaining limitations: validation-only evidence, three seed pairs only, no independent test, no causal ablations, no COCO metrics, unresolved provider provenance, and incomplete label-quality review.
