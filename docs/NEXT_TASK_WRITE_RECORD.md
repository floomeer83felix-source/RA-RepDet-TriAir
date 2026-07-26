# Next Task Write Record

Written: 2026-07-26
Branch: `research/ra-repdet-triair`
V71 completion commit: `bfca2e21ca7a46a5087b3addfcac7dab9d7e1618`
Canonical task file: `docs/NEXT_TASK.md`

## Completed prior task

`V71_BLOCKED_ADAPTER_OR_ONTOLOGY_CONTRACT`

V71 verified the exact `1,845`-row MM-UAV devval manifest and strictly loaded all six frozen TriAir manuscript checkpoints. No AP/AR was produced because V71 required defensible physical multimodal pixel registration.

## User-directed immediate experiment

The user directed the project to stop delaying the experiment for provider, version, rights, calibration, or other non-execution work.

The active task is:

`V72_MMUAV_EXISTING_DEVVAL_TRIAIR_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_AUTHORIZED`

Execute immediately:

1. freeze one adapter by reusing V53 independent modality decoding and letterbox;
2. independently map RGB, IR, and event to `640 x 640`;
3. concatenate RGB + IR grayscale + event grayscale into five channels;
4. use RGB annotation geometry and the frozen vehicle ontology;
5. preserve score threshold `0.001`, NMS `0.6`, maximum `100` detections, and COCO AP/AR;
6. run one fixed 8-row no-metric smoke pass;
7. immediately evaluate Early Fusion and RA-RepDet seeds `0`, `1`, and `2` over all `1,845` rows;
8. report per-checkpoint AP/AR, coverage, geometry, timing, memory, and matched seed differences;
9. do not train, adapt, calibrate, tune, add variants, or change the adapter after results;
10. commit compact evidence and push.

## Claim boundary

Use:

`zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`

Do not claim independent/blind validation or physical registration.

## Completion

Successful state:

`V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE`

Required commit message:

`exp: run V72 MM-UAV naive-grid external-domain stress test`