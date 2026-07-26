# Next Task Write Record

Written: 2026-07-26
Branch: `research/ra-repdet-triair`
V72 completion commit: `121d444e4885445e42f0755f7413c579e4ccf66e`
Canonical task file: `docs/NEXT_TASK.md`

## Completed prior task

`V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE`

V72 completed:

1. one fixed deterministic naive normalized-grid adapter;
2. one fixed 8-row no-metric smoke pass;
3. Early Fusion seeds `0`, `1`, and `2` over all `1,845` rows;
4. RA-RepDet `p=0.15` seeds `0`, `1`, and `2` over all `1,845` rows;
5. one complete evaluation attempt per checkpoint;
6. `184,500` finite valid predictions per checkpoint;
7. six complete AP/AR records;
8. `28 / 28` focused and alignment-regression tests;
9. no training, adaptation, calibration, tuning, substitution, or result-driven rerun.

Three-seed AP@[.50:.95] results:

- Early Fusion mean: `9.48024496878457e-9`;
- Early Fusion sample standard deviation: `8.69698401219258e-9`;
- RA-RepDet mean: `7.208000851646425e-7`;
- RA-RepDet sample standard deviation: `1.174160691123537e-6`;
- paired `RA-RepDet - Early Fusion` mean: `7.11319840195858e-7`;
- paired sample standard deviation: `1.172256488694345e-6`.

The near-zero outcome is a negative external-domain stress-test result under an independently normalized, physically unregistered five-channel adapter.

## Active next task

`V73_TRIAIR_MANUSCRIPT_MMUAV_EXTERNAL_STRESS_TEST_INTEGRATION_AUTHORIZED`

Execute V73 exactly as specified in `docs/NEXT_TASK.md`:

1. lock all manuscript numbers to the committed V72 JSON evidence;
2. add an appendix/supplement subsection for the exposed MM-UAV devval stress test;
3. add the exact six-checkpoint AP/AR table;
4. add method means, sample standard deviations, and paired mean difference;
5. document the frozen checkpoints, `1,845` rows, `640 x 640` naive adapter, threshold `0.001`, NMS `0.6`, and maximum `100` detections;
6. state that the modalities were not physically registered and the split was previously exposed;
7. interpret the near-zero result as failure of direct transfer under severe cross-sensor geometry/domain mismatch;
8. add one concise main discussion/limitations pointer to the appendix;
9. keep the result out of the abstract, headline contribution list, primary TriAir table, and positive conclusion claims;
10. build, inspect, trace every number, audit prohibited wording, and push.

## Required scientific label

Use exactly:

`zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`

Do not claim independent external validation, blind testing, official MM-UAV test performance, physical registration, robust cross-dataset generalization, or meaningful method superiority from the near-zero paired differences.

## Completion boundary

Successful state:

`V73_TRIAIR_MANUSCRIPT_MMUAV_STRESS_TEST_INTEGRATED`

Required commit message:

`docs: integrate V72 MM-UAV external-domain stress test into manuscript`

No new experiment, inference, training, adapter variant, threshold, seed, checkpoint, or dataset is authorized in V73.