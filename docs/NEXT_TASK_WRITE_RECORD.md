# Next Task Write Record

Written: 2026-07-25
Branch: `research/ra-repdet-triair`
Authorization base: `0c5cafc695cbdb6d8b0e91c62eb18f84e14c0706`
V68 completion commit: `805342be2aba7bc57cb41704903ec9f47a8f1482`
Canonical task file: `docs/NEXT_TASK.md`

## Superseded task

`V69_TRIAIR_MANUSCRIPT_SUBMISSION_READINESS_AUTHORIZED`

This task was superseded before execution because the user clarified that the immediate objective is to build MM-UAV into a genuine zero-shot external validation dataset for the frozen TriAir models.

## Active next task

`V69_MMUAV_ZERO_SHOT_EXTERNAL_VALIDATION_PROTOCOL_AND_BLIND_TEST_FREEZE_AUTHORIZED`

Execute the corrected V69 preflight exactly as specified in `docs/NEXT_TASK.md`:

1. Build a complete V52-V68 sample- and sequence-level exposure ledger.
2. Distinguish identity-only inventory from content exposure and development use.
3. Exclude every used sample and linked same-sequence, adjacent, duplicate, or near-duplicate component.
4. Identify an unused official test split or a wholly unexposed sequence/component blind holdout without using labels, predictions, or metrics.
5. If no eligible partition exists, stop with `V69_BLOCKED_NO_UNUSED_MMUAV_PARTITION`; do not rename the historical train/devval split.
6. Locate, hash, and strictly load the six frozen TriAir manuscript checkpoints: early fusion and full reliability-aware fusion for seeds 0, 1, and 2.
7. Use no MM-UAV-trained checkpoint, learned feature aligner, Softplus MM-UAV wrapper, adaptation, calibration, or fine-tuning.
8. Freeze a deterministic parameter-free RGB/thermal/event-to-TriAir five-channel adapter at 640 x 640 using only the frozen TriAir contract and already exposed development material.
9. Freeze the vehicle ontology, score threshold 0.001, NMS 0.6, maximum 100 detections, and canonical COCO AP/AR evaluator before candidate schema validation.
10. Hash and seal candidate annotations without parsing them; produce no candidate inference, predictions, or metrics in V69.
11. Keep the full blind manifest, raw media, labels, checkpoints, local paths, and sensitive artifacts outside Git.
12. Preserve V40-V68 history, production behavior, and the active manuscript unchanged.

## Completion boundary

A successful outcome is:

`V69_MMUAV_BLIND_EXTERNAL_TEST_FROZEN_INTERNAL_ONLY`

This means the blind partition, six frozen TriAir checkpoints, deterministic adapter, ontology, label seal, and evaluator contract are ready. It does not authorize public reporting and does not compute AP/AR.

Only after successful V69 completion may the standing handoff workflow authorize a separate V70 one-time zero-shot external evaluation. If the partition is not genuinely untouched, the work must stop rather than manufacture an independence claim.
