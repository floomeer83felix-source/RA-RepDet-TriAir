# Next Task Write Record

Written: 2026-07-25
Branch: `research/ra-repdet-triair`
V69 completion commit: `dbf728207396df869dfe7165f432010d303174dc`
Canonical task file: `docs/NEXT_TASK.md`

## Completed prior task

`V69_BLOCKED_NO_UNUSED_MMUAV_PARTITION`

V69 completed the metadata-only exposure audit and established:

1. the local inventory contains `897,578` synchronized triplets across `424` provider-train sequences;
2. direct `DEVELOPMENT_USED`, `CONTENT_EXPOSED`, and `IDENTITY_ONLY` counts are `9,032`, `36,004`, and `852,542`;
3. every one of the `424` sequences is linked to V52-V67 development;
4. blind-eligible sequences and rows are both zero;
5. only the provider train split is locally present;
6. no candidate media or labels were opened;
7. no predictions or metrics were produced;
8. no CUDA, training, adaptation, tuning, or checkpoint selection occurred;
9. protected files remained unchanged;
10. V69 tests passed `9 / 9`.

Existing local MM-UAV data may not be randomly resplit, renamed, or reused as an independent external test set.

## Active next task

`V70_MMUAV_UNTOUCHED_EXTERNAL_PARTITION_INTAKE_AND_BLIND_FREEZE_AUTHORIZED`

Execute V70 exactly as specified in `docs/NEXT_TASK.md`:

1. accept only a provider-defined official MM-UAV test split absent from V52-V69, or wholly new provider sequences/components with metadata proving independence from all `424` old sequences;
2. stop with `V70_BLOCKED_EXTERNAL_TEST_MATERIAL_NOT_SUPPLIED` when no such package is supplied;
3. audit provider, split, version, archive hash, and sequence/component identities before opening media or labels;
4. prove zero prohibited overlap against the frozen V69 exposure ledger;
5. freeze a local blind manifest and commit only compact hashes/counts;
6. hash and seal annotations without parsing their contents;
7. verify the six frozen TriAir manuscript checkpoints for Early Fusion and RA-RepDet seeds 0, 1, and 2;
8. freeze a deterministic parameter-free RGB/thermal/event-to-five-channel adapter at `640 x 640`;
9. freeze vehicle ontology, score threshold `0.001`, NMS `0.6`, maximum `100` detections, and canonical COCO AP/AR evaluator semantics;
10. perform only a post-freeze schema pass;
11. do not run candidate inference, generate predictions, compute metrics, train, fine-tune, adapt, calibrate, or tune;
12. keep raw data, labels, full manifests, checkpoints, credentials, private correspondence, and heavy artifacts outside Git.

## Completion boundary

A successful V70 outcome is:

`V70_MMUAV_BLIND_EXTERNAL_TEST_FROZEN_INTERNAL_ONLY`

That state freezes the untouched external partition and complete zero-shot protocol but computes no metrics. Only after successful V70 completion may a separate V71 one-time zero-shot external evaluation be authorized.

V68 remains an independent manuscript/public-reporting blocker until provider-verifiable citation, version, license, research-use, aggregate-reporting, and redistribution documentation passes re-audit.
