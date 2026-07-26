# Experiment Status

Updated: 2026-07-26

## Active task

`V73_TRIAIR_MANUSCRIPT_MMUAV_EXTERNAL_STRESS_TEST_INTEGRATION_AUTHORIZED`

## V72 completion evidence

V72 completed at commit `121d444e4885445e42f0755f7413c579e4ccf66e` with:

`V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE`

The completed experiment was:

`zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`

Execution facts:

- fixed smoke pass: `1 / 1` complete;
- full checkpoint evaluations: `6 / 6` complete;
- rows per checkpoint: `1,845`;
- sequences: `85`;
- ground-truth boxes: `4,198`;
- attempts per checkpoint: exactly `1`;
- predictions per checkpoint: `184,500`;
- finite/valid predictions: all;
- total checkpoint inference time: `349.60` seconds;
- maximum peak GPU memory: `818.44` MiB;
- focused and V52/V53 regression tests: `28 / 28` passed;
- training, adaptation, calibration, tuning, checkpoint substitution, and result-driven reruns: none.

| Method | Seed | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Early Fusion | 0 | `1.7089382511905107e-8` | `8.544691255952553e-8` | `0` | `0` | `0` | `4.764173415912339e-5` |
| Early Fusion | 1 | `1.1351352394448599e-8` | `1.1351352394448599e-7` | `0` | `0` | `0` | `2.3820867079561694e-5` |
| Early Fusion | 2 | `0` | `0` | `0` | `0` | `0` | `0` |
| RA-RepDet | 0 | `8.672098945411591e-8` | `5.150327766859084e-7` | `0` | `0` | `0` | `1.9056693663649358e-4` |
| RA-RepDet | 1 | `2.0756792660398117e-6` | `1.0378396330199058e-5` | `0` | `4.764173415912339e-5` | `4.764173415912339e-5` | `1.1910433539780849e-4` |
| RA-RepDet | 2 | `0` | `0` | `0` | `0` | `0` | `0` |

Three-seed AP@[.50:.95] summary:

- Early Fusion mean: `9.48024496878457e-9`;
- Early Fusion sample standard deviation: `8.69698401219258e-9`;
- RA-RepDet mean: `7.208000851646425e-7`;
- RA-RepDet sample standard deviation: `1.174160691123537e-6`;
- paired `RA-RepDet - Early Fusion` mean: `7.11319840195858e-7`;
- paired sample standard deviation: `1.172256488694345e-6`.

The values are near zero. They must not be presented as meaningful robustness, superiority, or successful external generalization.

## Active V73 work

V73 will immediately integrate the completed V72 experiment into the TriAir research manuscript as an appendix-level negative external-domain stress test.

Required changes:

- add the exact six-checkpoint AP/AR table;
- add protocol and aggregate-statistics text;
- state that the split was previously exposed and was not blind;
- state that the adapter independently normalized modality grids without physical registration;
- explain that direct cross-sensor transfer failed under this adapter;
- add one concise main discussion/limitations reference to the appendix;
- keep the result out of the abstract, headline contributions, primary TriAir table, and positive conclusion claims;
- trace every inserted number to committed V72 JSON;
- compile and inspect the manuscript.

No new experiment, inference, training, adapter search, threshold change, seed addition, or metric recomputation is authorized.

## Scientific boundary

Allowed conclusion:

> Frozen TriAir models did not transfer meaningfully to the exposed MM-UAV devval domain under the naive normalized-grid adapter, indicating that cross-sensor geometry and acquisition mismatch dominate direct channel-level transfer.

Forbidden conclusions include independent external validation, official MM-UAV test performance, physically registered validation, robust cross-dataset generalization, or meaningful RA-RepDet superiority from the tiny paired differences.

## Intended completion

`V73_TRIAIR_MANUSCRIPT_MMUAV_STRESS_TEST_INTEGRATED`

Required completion commit:

`docs: integrate V72 MM-UAV external-domain stress test into manuscript`