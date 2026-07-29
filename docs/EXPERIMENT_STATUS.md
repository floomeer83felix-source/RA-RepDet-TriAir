# Experiment Status

Updated: 2026-07-29

## Active task

`V74_TRIAIR_MANUSCRIPT_MMUAV_CROSS_DATASET_TRANSFER_INTEGRATION_AUTHORIZED`

## V73 result correction

The V73 aggregate values uploaded in completion commit `eafceccdedfc0bea93170a671906619b004412f4` were incorrect. The authoritative correction is:

`runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/RESULT_CORRECTION.md`

| Training setting | AP | AP50 | AP75 | AR100 | Conclusion |
| --- | ---: | ---: | ---: | ---: | --- |
| Frozen TriAir, naive-grid zero-shot | 0.000 | 0.000 | 0.000 | 0.000 | Direct transfer failed |
| MM-UAV Scratch Equal | 0.220 ± 0.007 | 0.557 | 0.134 | 0.351 | Aligned supervised training recovered performance |
| TriAir Init Equal | 0.233 ± 0.006 | 0.580 | 0.151 | 0.374 | Source-domain pretraining was beneficial |
| TriAir Init Reliability | 0.250 ± 0.008 | 0.610 | 0.178 | 0.398 | Reliability-aware fusion improved performance further |

## Corrected combined conclusion

V72 shows that frozen TriAir models fail under naive unregistered zero-shot transfer. V73 shows that aligned MM-UAV supervision restores useful performance. Under the corrected V73 aggregate results, TriAir initialization improves over matched scratch training, and reliability-aware fusion provides an additional gain over equal fusion.

## Invalidated metric sources

The pre-correction `per_run_metrics.csv`, `per_run_metrics.json`, `paired_transfer_comparison.csv`, and `paired_transfer_comparison.json` must not be used for manuscript numbers or conclusions. Corrected seed-level values were not supplied, so seed-wise tables and paired differences must not be reconstructed or reported.

`three_seed_summary.json` now contains the corrected aggregate values and explicitly records this invalidation.

## Active V74 boundary

V74 remains a documentation and manuscript-integration task. It must:

- use only the corrected aggregate table above for V73;
- present the zero-shot failure, supervised recovery, source-pretraining benefit, and reliability-fusion improvement accurately;
- omit the invalidated per-seed and paired-difference tables unless corrected seed-level records are later supplied;
- preserve all existing TriAir in-domain evidence;
- avoid claims of independent/blind external validation, official untouched-test performance, or generalization without MM-UAV labels;
- run no new training, evaluation, tuning, seed, checkpoint selection, or result-driven rerun.

## Scientific boundary

V73 is an `MM-UAV supervised cross-dataset transfer benchmark with learned feature alignment`. It is not zero-shot, independent/blind external validation, official untouched-test performance, or evidence of generalization without MM-UAV labels.

## Intended completion

`V74_TRIAIR_MANUSCRIPT_MMUAV_TRANSFER_STUDY_INTEGRATED`

Required completion commit:

`docs: integrate corrected V72-V73 MM-UAV cross-dataset transfer study`
