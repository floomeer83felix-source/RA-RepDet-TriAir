# Experiment Status

Updated: 2026-07-15

## Active task

`V53_CPU_PREFLIGHT_READY_FOR_SEPARATE_GPU_AUTHORIZATION`

## V53 result

The private MM-UAV CPU-only preflight is complete. It implements native RGB/IR/event loading, independent branch preprocessing and stems, RGB-coordinate detection supervision, and isolated STN-inspired residual affine feature alignment. No production TriAir builder or dataset behavior was changed.

## Frozen supervised contract

- Source root: `E:\MM-UAV_extracted\MMMUAV\train`.
- RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032.
- IR-only rows excluded: 106.
- No-GT rows retained as `UNLABELED` and excluded: 35,898.
- RGB boxes are the sole detector targets; IR boxes are metadata and event has no detector target.
- Train/devval sequences remain disjoint: 339 / 85.

## Experimental scaffold

- Three independent RGB, IR, and event stems.
- RGB is the reference feature grid.
- IR and event use separate STN-inspired residual affine feature aligners.
- Affine residual heads are zero initialized, yielding exact identity theta at initialization.
- `alignment_enabled=False` provides the no-alignment control.
- Equal and reliability-aware feature fusion interfaces are available.
- The scaffold is isolated under `rarepdet/experimental/` and is not wired into production builders.

## CPU preflight

- V53 tests: 9/9 pass.
- Equal-fusion scaffold: 52,220 parameters; estimated 342,835,584 MACs at branch input 320x320.
- Reliability-fusion scaffold: 53,309 parameters; estimated 342,838,752 MACs.
- Estimates cover only the scaffold, not a future detector/backbone integration.
- Protected core, V52 evidence, and manuscript changes: none.
- CUDA availability probe: not performed.
- GPU optimizer steps: 0.

## Gates

- Pilot gate remains locked with reason `V53_CPU_ONLY_PRE-REGISTRATION_AND_PREFLIGHT`.
- A 200-step GPU pilot requires separate explicit user authorization.
- RTX 3090 memory must be monitored when the scaffold is integrated with the future detector/backbones.
- The unresolved MM-UAV redistribution license remains a dissemination restriction.
- V51 remains separate and unchanged.
