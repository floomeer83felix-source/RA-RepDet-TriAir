# Next Task Write Record

Written: 2026-07-29
Branch: `research/ra-repdet-triair`
V73 completion commit: `eafceccdedfc0bea93170a671906619b004412f4`
Canonical task file: `docs/NEXT_TASK.md`
Correction record: `runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/RESULT_CORRECTION.md`

## Completed prior task

`V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE`

The V73 execution protocol completed nine supervised MM-UAV runs and nine final-checkpoint-only evaluations. The aggregate result values uploaded at completion were subsequently found to be incorrect and are superseded by the correction below.

## Corrected authoritative results

| Training setting | AP | AP50 | AP75 | AR100 | Conclusion |
| --- | ---: | ---: | ---: | ---: | --- |
| Frozen TriAir, naive-grid zero-shot | 0.000 | 0.000 | 0.000 | 0.000 | Direct transfer failed |
| MM-UAV Scratch Equal | 0.220 ± 0.007 | 0.557 | 0.134 | 0.351 | Aligned supervised training recovered performance |
| TriAir Init Equal | 0.233 ± 0.006 | 0.580 | 0.151 | 0.374 | Source-domain pretraining was beneficial |
| TriAir Init Reliability | 0.250 ± 0.008 | 0.610 | 0.178 | 0.398 | Reliability-aware fusion improved performance further |

The corrected conclusion is that aligned MM-UAV supervision recovers performance after zero-shot failure, TriAir initialization provides a benefit over scratch, and reliability-aware fusion improves performance further.

## Invalidated files

The pre-correction `per_run_metrics.csv`, `per_run_metrics.json`, `paired_transfer_comparison.csv`, and `paired_transfer_comparison.json` are not valid metric sources. Corrected seed-level values were not supplied, so per-seed tables and paired differences must not be reconstructed or reported.

## Active next task

`V74_TRIAIR_MANUSCRIPT_MMUAV_CROSS_DATASET_TRANSFER_INTEGRATION_AUTHORIZED`

Execute V74 exactly as specified in `docs/NEXT_TASK.md`:

1. lock all V72/V73 manuscript numbers to the corrected aggregate record;
2. add a compact corrected aggregate transfer table;
3. remove all pre-correction negative-transfer and no-reliability-gain wording;
4. omit invalidated per-seed and paired-difference evidence;
5. preserve all original TriAir in-domain evidence;
6. avoid independent-external-validation claims;
7. run clean manuscript builds, number traceability, claim audits, and rendered-page inspection;
8. run no new experiment, evaluation, tuning, seed, adapter, epoch extension, or result-driven rerun.

## Completion boundary

Successful state:

`V74_TRIAIR_MANUSCRIPT_MMUAV_TRANSFER_STUDY_INTEGRATED`

Required completion commit:

`docs: integrate corrected V72-V73 MM-UAV cross-dataset transfer study`
