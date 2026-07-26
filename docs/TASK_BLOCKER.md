# Task Blocker

Status: `V71_ZERO_SHOT_EXTERNAL_DOMAIN_VALIDATION_AUTHORIZED`

Generated: 2026-07-25

## Current state

There is no provider-source or official-test acquisition gate for the active task. V71 may begin immediately with local checkpoint, adapter, manifest, and evaluator preflight, followed by the authorized six-checkpoint evaluation.

The existing MM-UAV devval split is previously exposed and therefore is not an independent blind test. This is a required reporting limitation, not a blocker for the authorized external-domain validation.

## Required start conditions

Before model inference, verify:

1. the worktree is clean and the current task commit is present;
2. the exact frozen 1,845-row MM-UAV devval manifest, row order, modality pairing, annotations, and evaluator are available;
3. the six authoritative frozen TriAir checkpoints can be located, hashed, and strictly loaded;
4. a deterministic parameter-free five-channel adapter can be frozen at `640 x 640`;
5. vehicle ontology, score threshold `0.001`, NMS `0.6`, maximum `100` detections, and COCO AP/AR semantics are fixed;
6. protected files and historical evidence match their frozen fingerprints.

## Authorized work

V71 may:

- use the existing frozen 1,845-row MM-UAV devval manifest;
- parse its annotations for the final frozen metric computation;
- run a fixed no-metric smoke pass;
- run each of six frozen TriAir checkpoints exactly once on the full devval set;
- compute AP, AP50, AP75, AR@1, AR@10, and AR@100;
- compute matched seed-wise RA-RepDet minus Early Fusion differences and descriptive three-seed summaries;
- commit compact hashes, contracts, metrics, tests, and conclusions.

V71 may not:

- call the dataset an independent or blind external test;
- train, fine-tune, adapt, calibrate, pseudo-label, or optimize on MM-UAV;
- use MM-UAV-trained V57/V63/V65-V67 weights, learned MM-UAV alignment, or the MM-UAV Softplus wrapper;
- tune preprocessing, ontology, thresholds, NMS, checkpoints, seeds, or variants using V71 results;
- rerun a checkpoint because its metric is poor;
- place raw media, labels, full predictions, tensors, checkpoints, local paths, or heavy/private artifacts in Git.

## Fail-closed conditions

Stop with the matching V71 blocked state if:

- any frozen TriAir checkpoint or model contract cannot be verified;
- the 1,845-row manifest or evaluator differs from frozen evidence;
- the five-channel adapter or ontology requires learned or result-informed choices;
- inference, decoded boxes, predictions, or metric inputs become non-finite;
- OOM, unreadable modalities, coordinate mismatch, evaluator mismatch, protected-file drift, or private/heavy Git artifacts occur;
- any unauthorized tuning, checkpoint substitution, seed addition, variant addition, or result-driven rerun is attempted.

## Next action

Execute `docs/NEXT_TASK.md` immediately. Complete CPU/source-lock and checkpoint/adapter/evaluator preflight, then run the six full 1,845-row evaluations under the frozen protocol.
