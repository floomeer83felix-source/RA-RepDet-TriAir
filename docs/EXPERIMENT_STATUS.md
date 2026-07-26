# Experiment Status

Updated: 2026-07-25

## Active task

`V71_MMUAV_EXISTING_DEVVAL_TRIAIR_ZERO_SHOT_EXTERNAL_DOMAIN_VALIDATION_AUTHORIZED`

## Route correction

The previously authorized provider-source, rights, and official-test acquisition task was superseded before execution at the user's direction. The project will now begin dataset validation immediately using the existing frozen MM-UAV devval split.

This change does not convert the existing data into an independent blind test. The result will be reported as an exposed external-domain zero-shot validation only.

## Frozen evaluation target

- dataset manifest: existing frozen MM-UAV devval manifest from V65-V67;
- row count: exactly `1,845`;
- model source: six frozen TriAir manuscript checkpoints;
- methods: matched Early Fusion and full reliability-aware RA-RepDet;
- seeds: `0`, `1`, and `2` for each method;
- input: deterministic parameter-free RGB/thermal/event-to-five-channel conversion;
- resolution: `640 x 640`;
- score threshold: `0.001`;
- NMS: `0.6`;
- maximum detections: `100`;
- metrics: AP@[0.50:0.95], AP50, AP75, AR@1, AR@10, AR@100.

## Execution boundary

V71 will:

- verify and strictly load all six frozen TriAir checkpoints;
- freeze and test the deterministic five-channel adapter;
- run one no-metric finite-output smoke pass;
- evaluate each checkpoint exactly once over all 1,845 rows;
- produce per-checkpoint metrics and seed-matched `RA-RepDet - Early Fusion` comparisons;
- report mean, sample standard deviation, minimum, and maximum across the three seeds;
- commit compact metrics, hashes, tests, and summaries only.

V71 will not:

- train or fine-tune on MM-UAV;
- use MM-UAV-trained V57/V63/V65-V67 checkpoints;
- adapt, calibrate, tune thresholds, select checkpoints, add seeds, or rerun based on results;
- describe the result as an independent blind external test;
- place raw data, annotations, full predictions, checkpoints, local paths, or heavy/private artifacts in Git.

## Prior audit context

V69 established that all `424` locally available provider-train sequences are linked to prior development, and V70 found no newly supplied official test package. Those findings remain true but no longer block this explicitly non-blind external-domain validation.

## Intended completion

`V71_MMUAV_EXISTING_DEVVAL_ZERO_SHOT_EXTERNAL_DOMAIN_VALIDATION_COMPLETE`

Completion requires six valid full-devval metric records, a matched three-seed comparison, passing focused tests, and an explicit claim boundary that the split was previously exposed.
