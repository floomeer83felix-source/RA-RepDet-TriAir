# Experiment Status

Updated: 2026-07-15

## Active task

`V52_OFFICIAL_ALIGNMENT_PROVIDER_AUDIT_AUTHORIZED`

## User decision

The user authorized one final CPU-only audit of MM-UAV provider contracts and official cross-modal alignment evidence. No GPU work, training, inference, learned alignment design, or manuscript changes are authorized.

## Frozen MM-UAV subset

- 424 complete source-train sequences are accepted; incomplete sequence `0512` remains quarantined.
- Complete synchronized RGB/IR/event triplets: 897,578.
- Frozen interval-20 rule: source indices `1, 21, 41, ...`.
- Sequence-disjoint split: 339 train / 85 development-validation sequences.
- Frozen samples: 35,894 train + 9,142 development-validation = 45,036.
- 9,138 sampled triplets contain at least one source GT row.
- 35,898 sampled triplets remain `UNLABELED` and may not be treated as empty-target negatives.

## Alignment evidence already established

- Native grids differ: RGB 640x360, IR 640x512, event 346x260.
- Event frames have no separate source detection boxes in the locally audited subset.
- On the frozen geometry sample, dimension-only scaling produced mean matched RGB/IR IoU about 0.00867.
- Direct channel-aligned RGB/IR/event concatenation is scientifically invalid under the currently established evidence.

## Audit questions now authorized

The CPU-only audit must determine whether provider-controlled sources establish:

- the meaning of frames without GT rows;
- target category and final GT-column semantics;
- license or research-use terms;
- deterministic calibration, registration, warp, crop, coordinate transform, or official alignment implementation;
- whether the official method instead relies only on learned feature alignment.

## Gates

- V51 remains incomplete and must not be modified.
- Pilot gate remains locked.
- GPU optimizer steps remain 0.
- No 200-step pilot or full MM-UAV training is authorized.

## Current decision boundary

The task may end only as one of:

- `OFFICIAL_REPRODUCIBLE_ALIGNMENT_FOUND_PILOT_STILL_LOCKED`;
- `OFFICIAL_LEARNED_ALIGNMENT_ONLY_DIRECT_FUSION_NO_GO`;
- `NO_OFFICIAL_ALIGNMENT_DIRECT_FUSION_NO_GO`;
- `BLOCKED_PROVIDER_EVIDENCE_INCOMPLETE`.

A future GPU task requires separate user authorization even if a reproducible official alignment method is found.
