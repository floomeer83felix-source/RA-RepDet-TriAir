# Experiment Status

Updated: 2026-07-15

## Active task

`V53_MMUAV_PRIVATE_FEATURE_ALIGNMENT_PREFLIGHT_AUTHORIZED`

## User decision

The user selected Plan A for MM-UAV: native RGB/IR/event inputs, independent modality branches, learned feature-level alignment, and RGB-coordinate detection supervision.

All MM-UAV work is local, private research only. Do not repeatedly ask the user to reconfirm this scope. Reconfirmation is required only before public redistribution, external sharing, commercial use, or a new manuscript/public benchmark claim.

## V52 final outcome retained

`OFFICIAL_LEARNED_ALIGNMENT_ONLY_DIRECT_FUSION_NO_GO`

Direct raw RGB/IR/event channel concatenation remains invalid. No complete provider-supplied deterministic raw-grid transform was found; official evidence supports learned RGB/IR feature alignment.

## Frozen MM-UAV subset

- Local root: `E:\MM-UAV_extracted\MMMUAV\train`.
- 424 complete source-train sequences; incomplete sequence `0512` remains quarantined.
- Sequence-disjoint split: 339 train / 85 development-validation sequences.
- Frozen interval-20 rule: source indices `1, 21, 41, ...`.
- Frozen rows: 45,036.
- RGB-supervised rows: 9,032 = 7,187 train + 1,845 development-validation.
- Both RGB and IR GT: 8,901.
- RGB-only: 131.
- IR-only: 106 and excluded from RGB supervision.
- No source GT: 35,898 and retained as `UNLABELED`.
- Event frames have no independent detection boxes.

## V53 scope

V53 is CPU-only pre-registration and preflight. It may:

- freeze RGB-supervised manifests;
- implement a V53-specific native-modality adapter;
- implement isolated experimental learned feature alignment;
- provide alignment-on and alignment-off interfaces;
- run CPU forward, shape, determinism, gradient, manifest, and protected-file tests;
- record source locks and compute estimates.

V53 may not run CUDA, the 200-step pilot, epoch training, checkpoint production, AP evaluation, manuscript edits, or public data/derivative release.

## License boundary

The MM-UAV dataset license remains unresolved for redistribution. This remains a dissemination restriction. The active task is local-only and must not publish or redistribute media, annotations, transformed copies, or derivative labels.

## Gates

- V51 remains incomplete and must not be modified.
- Pilot gate remains locked.
- GPU optimizer steps remain 0.
- A future GPU pilot requires a separate explicit authorization after V53 preflight passes.

## Target completion states

- `V53_CPU_PREFLIGHT_READY_FOR_SEPARATE_GPU_AUTHORIZATION`
- `V53_BLOCKED_RGB_SUPERVISED_MANIFEST_CONTRACT`
- `V53_BLOCKED_DATA_ADAPTER_OR_SYNCHRONIZATION`
- `V53_BLOCKED_FEATURE_ALIGNMENT_IMPLEMENTATION`
- `V53_BLOCKED_COMPUTE_OR_TEST_PREFLIGHT`
