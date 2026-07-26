# Next Task Write Record

Written: 2026-07-25
Branch: `research/ra-repdet-triair`
V70 completion commit: `bd62068aa0f3ab046d8545c4eef69938b4e73c9b`
Superseded V71 authorization head: `9f650b80023beebeda241beb3904ed8f1f9cfd6d`
Canonical task file: `docs/NEXT_TASK.md`

## User-directed correction

The user directed the project to begin MM-UAV dataset validation immediately and not spend the active task on provider authority, official version, rights, or official-test acquisition.

The following task was superseded before execution:

`V71_MMUAV_PROVIDER_SOURCE_RIGHTS_AND_OFFICIAL_TEST_ACQUISITION_AUTHORIZED`

## Active task

`V71_MMUAV_EXISTING_DEVVAL_TRIAIR_ZERO_SHOT_EXTERNAL_DOMAIN_VALIDATION_AUTHORIZED`

Execute V71 exactly as specified in `docs/NEXT_TASK.md`:

1. lock the existing frozen 1,845-row MM-UAV devval manifest and unchanged evaluator;
2. locate, hash, and strictly load Early Fusion and RA-RepDet checkpoints for seeds 0, 1, and 2;
3. freeze a deterministic parameter-free RGB/thermal/event-to-five-channel adapter at `640 x 640`;
4. freeze the vehicle ontology, score threshold `0.001`, NMS `0.6`, and maximum `100` detections;
5. run a fixed no-metric finite-output smoke pass;
6. evaluate each checkpoint exactly once over all 1,845 rows;
7. report AP@[0.50:0.95], AP50, AP75, AR@1, AR@10, AR@100, prediction coverage, valid geometry, timing, and memory;
8. compute matched seed-wise RA-RepDet minus Early Fusion differences and descriptive three-seed summaries;
9. run focused tests and protected-file audits;
10. stop without result-driven tuning, checkpoint substitution, seed addition, variant addition, or rerun.

## Scientific label

The dataset and its sequences were previously exposed during V52-V70 development. Therefore the output must be labeled:

`zero-shot external-domain validation on the existing exposed MM-UAV devval split`

It must not be labeled:

- independent external validation;
- blind external test;
- official MM-UAV test performance.

This limitation does not block the authorized internal validation run.

## Completion boundary

Successful completion state:

`V71_MMUAV_EXISTING_DEVVAL_ZERO_SHOT_EXTERNAL_DOMAIN_VALIDATION_COMPLETE`

Required completion commit message:

`exp: run V71 MM-UAV existing-devval TriAir zero-shot external-domain validation`

Push to:

`research/ra-repdet-triair`
