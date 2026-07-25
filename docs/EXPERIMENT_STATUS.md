# Experiment Status

Updated: 2026-07-25

## Active task

`V70_MMUAV_UNTOUCHED_EXTERNAL_PARTITION_INTAKE_AND_BLIND_FREEZE_AUTHORIZED`

## V69 completion evidence

V69 completed at commit `dbf728207396df869dfe7165f432010d303174dc` with:

`V69_BLOCKED_NO_UNUSED_MMUAV_PARTITION`

The local MM-UAV inventory contains `897,578` synchronized provider-train triplets across `424` sequences. All `424` sequences are linked to V52-V67 development, leaving zero blind-eligible sequences and rows under the frozen same-sequence independence rule.

- direct `DEVELOPMENT_USED`: `9,032`;
- direct `CONTENT_EXPOSED`: `36,004`;
- direct `IDENTITY_ONLY` but sequence-ineligible: `852,542`;
- blind-eligible sequences/rows: `0 / 0`;
- candidate media opened: `false`;
- candidate labels parsed: `false`;
- predictions or metrics computed: `false`;
- V69 tests: `9 / 9` passed.

Only the provider train split is locally present. Existing 7,187/1,845 train/devval material and the remaining frames from those sequences cannot be renamed or resplit into an independent external test set.

## Active V70 work

V70 is an external-input-gated CPU/metadata task. It may accept only:

1. a provider-defined official MM-UAV test split absent from V52-V69; or
2. wholly new provider flights/sequences/components with metadata proving independence from all `424` development-linked sequences.

After new material is supplied, V70 will:

- verify provider/split/version/package identity and hashes before media access;
- prove zero prohibited overlap using the frozen V69 ledger;
- freeze a blind manifest and hash/seal labels without parsing them;
- verify the six frozen TriAir manuscript checkpoints;
- freeze a deterministic parameter-free five-channel adapter at `640 x 640`;
- freeze vehicle ontology, score threshold `0.001`, NMS `0.6`, maximum `100` detections, and COCO AP/AR evaluator semantics;
- perform only a post-freeze schema pass;
- generate no predictions and compute no metrics.

## Scientific boundary

The intended path remains:

`TriAir-trained frozen checkpoints -> untouched MM-UAV blind partition -> later one-time zero-shot evaluation`

No MM-UAV training, fine-tuning, learned alignment, domain adaptation, calibration, Softplus MM-UAV wrapper, checkpoint selection, threshold tuning, candidate-label inspection, inference, or metric computation is authorized in V70.

## Rights boundary

V68 remains separately blocked on provider authority, canonical citation, exact version, license/access terms, research-use permission, aggregate-results reporting permission, and redistribution terms. V70 success may establish internal scientific readiness only; it does not authorize manuscript inclusion or public reporting.

## Intended completion

A successful V70 outcome is:

`V70_MMUAV_BLIND_EXTERNAL_TEST_FROZEN_INTERNAL_ONLY`

Only that successful state may authorize a separate V71 one-time zero-shot external evaluation task.
