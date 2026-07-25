# Experiment Status

Updated: 2026-07-25

## Active task

`V70_BLOCKED_EXTERNAL_TEST_MATERIAL_NOT_SUPPLIED`

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

## V70 completion evidence

V70 completed as a fail-closed external-input audit with:

`V70_BLOCKED_EXTERNAL_TEST_MATERIAL_NOT_SUPPLIED`

The known MM-UAV provider root still contains only the previously audited `train` split. No provider-defined official test package, wholly new flight/sequence package, package hash, release identity, or provider metadata was supplied. The audit used directory identities only and did not open media or annotations.

- actual starting commit: `d851d4b2d855311a52578c6071df96ef07d1e253`;
- V69 evidence tree unchanged: `c799600b63fa7746cc4aea031904baa1ebd77971`;
- external packages accepted: `0`;
- candidate media opened: `false`;
- candidate labels parsed: `false`;
- predictions or metrics computed: `false`;
- CUDA or training used: `false`;
- V70 tests: `10 / 10` passed.

V70 stopped before independence, blind-manifest, label-seal, checkpoint, adapter, evaluator, and candidate-schema work because the required external package was absent.

## Authorized V70 input boundary

V70 may be resumed only after receiving:

1. a provider-defined official MM-UAV test split absent from V52-V69; or
2. wholly new provider flights/sequences/components with metadata proving independence from all `424` development-linked sequences.

After new material is supplied, a resumed V70 will:

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

## Intended completion after external input

A successful V70 outcome is:

`V70_MMUAV_BLIND_EXTERNAL_TEST_FROZEN_INTERNAL_ONLY`

Only that successful state may authorize a separate V71 one-time zero-shot external evaluation task.
