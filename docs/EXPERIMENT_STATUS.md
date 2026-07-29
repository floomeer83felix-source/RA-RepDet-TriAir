# Experiment Status

Updated: 2026-07-29

## Active task

`V74_TRIAIR_MANUSCRIPT_MMUAV_CROSS_DATASET_TRANSFER_INTEGRATION_AUTHORIZED`

## V73 completion evidence

V73 completed at commit `eafceccdedfc0bea93170a671906619b004412f4` with:

`V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE`

All nine authorized supervised MM-UAV runs completed:

- methods: `scratch_equal`, `triair_init_equal`, `triair_init_reliability`;
- seeds: `0`, `1`, `2`;
- ten epochs and `71,870` optimizer steps per run;
- total optimizer steps: `646,830`;
- final-checkpoint-only devval evaluations: `9 / 9`;
- devval rows per evaluation: `1,845`;
- no early stopping, devval monitoring, tuning, checkpoint selection, or result-driven rerun;
- transfer-run destination parameter coverage: `0.9920156853111293`.

## Three-seed V73 results

| Method | AP@[.50:.95] mean ± sample std | AP50 | AP75 | AR100 |
| --- | ---: | ---: | ---: | ---: |
| `scratch_equal` | `0.2234327171146003 ± 0.007329674213261401` | `0.556931726947029` | `0.134019814828121` | `0.3512863268222963` |
| `triair_init_equal` | `0.2177868187542824 ± 0.0020161156114949915` | `0.5526032852323605` | `0.12540843897740625` | `0.34365570906781007` |
| `triair_init_reliability` | `0.21510604967221716 ± 0.009007102251984311` | `0.5451312175583816` | `0.1254178623160722` | `0.34215499444179764` |

Paired AP@[.50:.95] means:

- `triair_init_equal - scratch_equal`: `-0.00564589836031786`;
- `triair_init_reliability - scratch_equal`: `-0.008326667442383104`;
- `triair_init_reliability - triair_init_equal`: `-0.002680769082065243`.

## Combined V72-V73 conclusion

V72 remains the unadapted zero-shot stress-test baseline and produced effectively zero AP under naive unregistered five-channel concatenation.

V73 shows that MM-UAV supervision plus learned feature alignment recovered useful detection performance to approximately `0.22` mean AP. However, the from-scratch equal-fusion control achieved the highest three-seed mean. TriAir initialization did not provide an average AP benefit, and reliability-aware fusion did not improve the mean over matched equal fusion under this fixed protocol.

## Active V74 work

V74 will integrate V72 and V73 into the TriAir research manuscript as a cross-dataset transfer study. It will:

- add protocol, mean ± standard-deviation, per-seed, and paired-difference tables;
- explain zero-shot failure and supervised alignment-aware recovery;
- report the negative TriAir-initialization and reliability-fusion findings without overclaiming;
- preserve all existing TriAir in-domain evidence;
- perform arithmetic traceability, claim auditing, clean manuscript build, and rendered-page inspection;
- run no new experiment or tuning.

## Scientific boundary

The V73 output is:

`MM-UAV supervised cross-dataset transfer benchmark with learned feature alignment`

It is not zero-shot, independent/blind external validation, official untouched-test performance, or evidence of generalization without MM-UAV labels. Comparisons are descriptive and the devval split had prior engineering exposure.

## Intended completion

`V74_TRIAIR_MANUSCRIPT_MMUAV_TRANSFER_STUDY_INTEGRATED`

Required completion commit:

`docs: integrate V72-V73 MM-UAV cross-dataset transfer study`
