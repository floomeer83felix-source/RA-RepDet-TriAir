# Experiment Status

Updated: 2026-07-15

## Active task

`V52_OFFICIAL_ALIGNMENT_PROVIDER_AUDIT_COMPLETE`

## Final outcome

`OFFICIAL_LEARNED_ALIGNMENT_ONLY_DIRECT_FUSION_NO_GO`

The final CPU-only audit found official learned RGB/IR feature alignment but no complete provider-supplied RGB/IR/event raw-grid registration. Direct channel-aligned fusion remains invalid. No GPU work, training, inference, learned alignment design, or manuscript change occurred.

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

## Provider-contract verdicts

- Annotated-only predicate reproduced exactly: 9,138 included / 35,898 `UNLABELED`.
- Sparse GT: `PARTIALLY_CONFIRMED`; the paper states train annotations every 100 frames and the official converter excludes unannotated frames, but absent rows are not defined as verified empty targets.
- Category and GT fields: `PARTIALLY_CONFIRMED`; official code confirms `drone` and operational use of the first six fields, but the final three fields are not completely defined.
- Dataset license: `UNRESOLVED`; Apache-2.0 applies to official code and the paper has a separate arXiv license, neither is an explicit dataset grant.
- Alignment: OGAA deformable convolution and STN are learned feature alignment. STN constants are incomplete calibration parameters/initialization, while temporal GMC, synchronization, resizing, and event crop expansion are not raw-grid registration.
- Official deterministic spatial transform: not found; verification status is `NOT_RUN_NO_OFFICIAL_DETERMINISTIC_TRANSFORM`.

## Gates

- V51 remains incomplete and must not be modified.
- Pilot gate remains locked.
- GPU optimizer steps remain 0.
- No 200-step pilot or full MM-UAV training is authorized.

## Current decision boundary

The MM-UAV route cannot use direct RGB/IR/event channel concatenation. Adding learned alignment would be a separately authorized method-expansion task. The pilot gate remains locked and GPU optimizer steps remain 0.
