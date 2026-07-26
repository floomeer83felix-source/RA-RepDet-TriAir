# Experiment Status

Updated: 2026-07-26

## Active task

`V73_MMUAV_TRIAIR_INITIALIZED_ALIGNMENT_AWARE_TRANSFER_BENCHMARK_AUTHORIZED`

## V72 completion evidence

V72 completed at commit `121d444e4885445e42f0755f7413c579e4ccf66e` with:

`V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE`

The six frozen TriAir checkpoints were evaluated exactly once on all `1,845` exposed MM-UAV devval rows under one naive unregistered five-channel adapter. All predictions and metric inputs were finite, but AP was effectively zero:

- Early Fusion mean AP@[.50:.95]: `9.48024496878457e-9`;
- RA-RepDet mean AP@[.50:.95]: `7.208000851646425e-7`;
- paired mean difference: `7.11319840195858e-7`.

V72 remains frozen as the unadapted zero-shot external-domain stress-test baseline. It is not an independent or physically registered external validation.

## Superseded task

The manuscript-only task:

`V73_TRIAIR_MANUSCRIPT_MMUAV_EXTERNAL_STRESS_TEST_INTEGRATION_AUTHORIZED`

was superseded before execution after the user authorized retraining to obtain a useful supervised target-domain transfer result.

## Active V73 benchmark

V73 will run a unified `640 x 640` learned-feature-alignment benchmark using the frozen MM-UAV train/devval manifests.

Exactly nine runs are authorized:

- `scratch_equal`, seeds `0`, `1`, `2`;
- `triair_init_equal`, seeds `0`, `1`, `2`;
- `triair_init_reliability`, seeds `0`, `1`, `2`.

The architecture uses independent RGB/IR/event stems, learned feature alignment, Softplus bbox-distance output, and either equal or reliability-aware fusion. No raw five-channel concatenation is used.

Each run uses:

- MM-UAV train rows: `7,187`;
- exactly `10` epochs;
- exactly `71,870` optimizer steps;
- batch size `1`;
- AdamW, initial LR `1e-4`, weight decay `1e-4`;
- `500`-step warmup and cosine decay to `1e-6`;
- AMP disabled;
- no augmentation, early stopping, devval monitoring, tuning, or checkpoint selection;
- final checkpoint evaluated exactly once on all `1,845` devval rows.

Total planned optimizer steps across nine runs: `646,830`.

## Transfer contract

For `triair_init_equal`, seed-matched frozen TriAir Early Fusion checkpoints initialize exact compatible shared backbone/FPN/FCOS tensors.

For `triair_init_reliability`, seed-matched frozen TriAir RA-RepDet `p=0.15` checkpoints initialize exact compatible shared tensors.

MM-UAV-specific modality stems, alignment modules, fusion projections, and unmatched parameters use the same frozen seed-specific initialization as the scratch control. All transferred and skipped tensors must be recorded exactly; tensor repair, averaging, reshaping, or seed substitution is forbidden.

## Required comparisons

For every seed and metric V73 will report:

1. `triair_init_equal - scratch_equal`;
2. `triair_init_reliability - triair_init_equal`;
3. `triair_init_reliability - scratch_equal`.

All nine run metrics, three-seed means, sample standard deviations, minima, maxima, ranges, transfer coverage, and reliability-weight diagnostics are required.

## Scientific boundary

The output is a:

`MM-UAV supervised cross-dataset transfer benchmark with learned feature alignment`

It is not zero-shot or independent external validation because MM-UAV train labels are used and the devval set was previously exposed during engineering. V65-V67 remain pilot evidence only and may not be numerically mixed with V73 because their protocol differs.

## Intended completion

`V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE`

Required completion commit:

`exp: run V73 MM-UAV TriAir-initialized alignment-aware transfer benchmark`
