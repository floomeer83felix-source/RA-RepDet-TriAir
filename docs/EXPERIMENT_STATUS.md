# Experiment Status

Updated: 2026-07-25

## Active task

`V69_MMUAV_ZERO_SHOT_EXTERNAL_VALIDATION_PROTOCOL_AND_BLIND_TEST_FREEZE_AUTHORIZED`

## Route correction

The prior `V69_TRIAIR_MANUSCRIPT_SUBMISSION_READINESS_AUTHORIZED` task was superseded before execution. The intended research objective is now explicit: evaluate frozen TriAir manuscript models on a genuinely unused MM-UAV partition without MM-UAV training, fine-tuning, adaptation, checkpoint selection, or threshold tuning.

V65-V67 remain valid internal MM-UAV development experiments, but their 7,187-row train and 1,845-row devval partitions cannot be relabeled as an independent external test set.

## Active V69 work

V69 is a CPU/documentation/preflight task that will:

- build a sample- and sequence-level exposure ledger for V52-V68;
- determine whether an untouched official split or unexposed sequence/component holdout exists;
- exclude all content-exposed, development-used, same-sequence, adjacent, duplicate, and near-duplicate items;
- locate and strictly verify the six frozen TriAir manuscript checkpoints;
- freeze a deterministic parameter-free MM-UAV-to-TriAir five-channel adapter at 640 x 640;
- freeze the unchanged TriAir inference and COCO-style evaluator contract;
- hash and seal candidate test labels without parsing them;
- produce no candidate predictions or metrics.

## Strict scientific boundary

The target is `TriAir-trained model -> MM-UAV zero-shot blind evaluation`. No MM-UAV-trained V57/V63/V65-V67 model, learned feature aligner, Softplus wrapper, calibration, pseudo-labeling, domain adaptation, or fine-tuning may be used.

If no untouched MM-UAV partition exists, V69 must stop with `V69_BLOCKED_NO_UNUSED_MMUAV_PARTITION`; it may not create an independent-test claim by renaming previously used data.

## Rights boundary

V68 remains frozen as `V68_BLOCKED_DATA_RIGHTS_OR_CITATION_INCOMPLETE`. Internal protocol preparation may continue under the standing private-research rule, but manuscript/public reporting remains forbidden until provider authority, citation, version, license, research-use, aggregate-reporting, and redistribution terms are verified.

## Intended completion

A successful V69 outcome is:

`V69_MMUAV_BLIND_EXTERNAL_TEST_FROZEN_INTERNAL_ONLY`

That outcome freezes the blind partition, six TriAir checkpoints, deterministic adapter, label seal, and evaluator. It does not compute AP/AR; a separate V70 task is required for the one-time zero-shot evaluation.
