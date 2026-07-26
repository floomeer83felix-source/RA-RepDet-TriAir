# Next Task Write Record

Written: 2026-07-26
Branch: `research/ra-repdet-triair`
V72 completion commit: `121d444e4885445e42f0755f7413c579e4ccf66e`
Superseded V73 manuscript-integration authorization head: `38e74e24758d94d7841a31a5bbeecc222d2a1783`
Canonical task file: `docs/NEXT_TASK.md`

## Completed prior task

`V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE`

V72 completed six one-time evaluations of frozen TriAir checkpoints on the exposed MM-UAV devval split using one naive unregistered five-channel adapter. All runs were finite and complete, but AP was effectively zero:

- Early Fusion mean AP@[.50:.95]: `9.48024496878457e-9`;
- RA-RepDet mean AP@[.50:.95]: `7.208000851646425e-7`;
- paired mean difference: `7.11319840195858e-7`.

V72 remains frozen as the unadapted zero-shot external-domain stress-test baseline.

## User-authorized route change

The user requested retraining to obtain a useful paper result. The previously authorized manuscript-only task:

`V73_TRIAIR_MANUSCRIPT_MMUAV_EXTERNAL_STRESS_TEST_INTEGRATION_AUTHORIZED`

was superseded before execution.

## Active task

`V73_MMUAV_TRIAIR_INITIALIZED_ALIGNMENT_AWARE_TRANSFER_BENCHMARK_AUTHORIZED`

Execute V73 exactly as specified in `docs/NEXT_TASK.md`:

1. freeze the existing `7,187`-row train and `1,845`-row devval manifests;
2. use one common `640 x 640` MM-UAV architecture with independent modality stems, learned feature alignment, Softplus bbox output, and equal or reliability fusion;
3. reverify the six seed-matched TriAir Early Fusion and RA-RepDet source checkpoints;
4. freeze exact name-and-shape-compatible tensor transfer maps before training;
5. run `scratch_equal`, `triair_init_equal`, and `triair_init_reliability` for seeds `0`, `1`, and `2`;
6. train every run for exactly `10` epochs and `71,870` optimizer steps using the frozen AdamW/warmup/cosine protocol;
7. use identical seed-specific epoch orders across variants;
8. prohibit devval monitoring, early stopping, checkpoint selection, tuning, or adaptive extension;
9. evaluate only each final checkpoint exactly once on all `1,845` devval rows;
10. report all nine AP/AR records, transfer coverage, fusion diagnostics, three matched paired comparisons, and descriptive three-seed summaries;
11. do not add seeds, variants, epochs, reruns, ensembles, or result-driven changes;
12. keep raw data, predictions, optimizer states, checkpoints, and heavy/private artifacts outside Git.

## Required comparisons

For each seed and metric:

- `triair_init_equal - scratch_equal`;
- `triair_init_reliability - triair_init_equal`;
- `triair_init_reliability - scratch_equal`.

Report mean, sample standard deviation, minimum, maximum, and range across seeds.

## Scientific label

Use:

`MM-UAV supervised cross-dataset transfer benchmark with learned feature alignment`

Do not call the result zero-shot, independent external validation, blind external testing, or generalization without MM-UAV labels.

## Completion boundary

Successful state:

`V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE`

Required completion commit:

`exp: run V73 MM-UAV TriAir-initialized alignment-aware transfer benchmark`
