# Task Blocker

Status: `V74_MANUSCRIPT_INTEGRATION_AUTHORIZED_WITH_V73_AGGREGATE_CORRECTION_LOCK`

Generated: 2026-07-29

## Current state

V73 completed its authorized training and evaluation protocol at commit `eafceccdedfc0bea93170a671906619b004412f4`. Its uploaded aggregate metric values and negative-transfer conclusion were incorrect and have been superseded by:

`runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/RESULT_CORRECTION.md`

There is no active training or runtime blocker. V74 may proceed as aggregate-only manuscript integration under the correction lock below.

## Corrected result boundary

| Training setting | AP | AP50 | AP75 | AR100 | Conclusion |
| --- | ---: | ---: | ---: | ---: | --- |
| Frozen TriAir, naive-grid zero-shot | 0.000 | 0.000 | 0.000 | 0.000 | Direct transfer failed |
| MM-UAV Scratch Equal | 0.220 ± 0.007 | 0.557 | 0.134 | 0.351 | Aligned supervised training recovered performance |
| TriAir Init Equal | 0.233 ± 0.006 | 0.580 | 0.151 | 0.374 | Source-domain pretraining was beneficial |
| TriAir Init Reliability | 0.250 ± 0.008 | 0.610 | 0.178 | 0.398 | Reliability-aware fusion improved performance further |

The combined conclusion is:

- naive-grid frozen zero-shot transfer failed;
- aligned MM-UAV supervision recovered useful performance;
- TriAir initialization improved the corrected aggregate result over scratch;
- reliability-aware fusion improved the corrected aggregate result further and achieved the best reported values.

## Invalidated evidence boundary

The pre-correction `per_run_metrics.csv`, `per_run_metrics.json`, `paired_transfer_comparison.csv`, and `paired_transfer_comparison.json` must not be used. Corrected seed-level records were not supplied.

V74 may not:

- include the invalidated nine-row per-seed table;
- report paired differences, seed-wise directions, minima, maxima, or ranges;
- reconstruct seed-level values from aggregate means and standard deviations;
- retain wording that scratch equal is best, TriAir initialization is negative transfer, or reliability fusion provides no gain.

## Active task

`V74_TRIAIR_MANUSCRIPT_MMUAV_CROSS_DATASET_TRANSFER_INTEGRATION_AUTHORIZED`

V74 is documentation and build work only. It must integrate the corrected aggregate table, update the scientific interpretation, perform traceability and claim audits, build the manuscript cleanly, and inspect rendered pages.

## Scientific boundary

The study remains supervised target-domain transfer. It may not be described as independent/blind external validation, official untouched-test performance, V73 zero-shot success, statistically significant external generalization, or generalization without MM-UAV labels.

## Fail-closed conditions

Finish with the matching blocked state only when:

1. the corrected aggregate numbers cannot be traced to the correction record;
2. any invalidated old value or conclusion remains in active manuscript sources;
3. the manuscript source or clean build procedure cannot be resolved;
4. prohibited external-validation wording remains;
5. new tables or text cannot be rendered legibly;
6. protected files drift outside the authorized scope;
7. private or heavy artifacts enter Git.

## Next action

Execute `docs/NEXT_TASK.md`. Integrate the corrected aggregate V72-V73 transfer study and push with:

`docs: integrate corrected V72-V73 MM-UAV cross-dataset transfer study`
