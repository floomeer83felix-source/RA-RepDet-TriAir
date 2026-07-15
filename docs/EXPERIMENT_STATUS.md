# Experiment Status

Updated: 2026-07-15

## Active task

`V54_MMUAV_ALIGNMENT_GPU_PILOT_AUTHORIZED`

## User authorization

The user authorized one bounded local/private MM-UAV GPU verification pilot. V54 may perform CUDA integration smoke checks and one pre-registered primary run of at most 200 completed optimizer steps. It does not authorize epoch training, AP/AR evaluation, multi-seed experiments, hyperparameter search, manuscript edits, public release, redistribution, or external sharing.

The standing private-research instruction remains frozen and must not be repeatedly reconfirmed.

## V53 prerequisite status

- V53 CPU preflight outcome: `V53_CPU_PREFLIGHT_READY_FOR_SEPARATE_GPU_AUTHORIZATION`.
- V53 tests: 9/9 pass.
- Native RGB/IR/event loading and independent modality branches are implemented.
- RGB is the sole detection coordinate system.
- IR and event use separate STN-inspired residual affine feature aligners.
- Alignment initialization is exact identity.
- Alignment-off, equal-fusion, and reliability-aware fusion interfaces exist.
- Production TriAir builders and dataset semantics remain unchanged.

## Frozen supervised contract

- Source root: `E:\MM-UAV_extracted\MMMUAV\train`.
- RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032.
- IR-only rows excluded: 106.
- No-GT rows remain `UNLABELED` and excluded: 35,898.
- RGB boxes are the only detector targets.
- IR boxes are metadata only; event has no detector target.
- Train/devval sequences remain disjoint: 339 / 85.
- V53 manifest hashes and source lock must be reproduced before CUDA work.

## V54 primary pilot

- Maximum completed optimizer steps: 200.
- Seed: 0.
- Branch input size: 320x320.
- Batch size: 1.
- Optimization data: frozen train RGB-supervised manifest only.
- Primary variant: learned alignment enabled with fixed/equal fusion.
- Purpose: detector integration, memory, numerical stability, gradient flow, affine-grid stability, and logging verification.
- No AP/AR, model selection, accuracy claim, or manuscript conclusion is permitted.

Before the primary run, forward/backward smoke checks without optimizer steps must cover RGB-only, alignment-off equal fusion, alignment-on equal fusion, and alignment-on reliability-aware fusion.

## Gates

- GPU pilot gate is unlocked only for the exact bounded V54 protocol in `docs/NEXT_TASK.md`.
- Completed optimizer-step counter must never exceed 200.
- OOM, non-finite loss/gradient/theta/grid, target mismatch, manifest mismatch, devval optimization leakage, or protected-file modification must fail closed.
- Do not automatically change resolution, batch size, precision, model width, modalities, or optimizer settings after observing an OOM or instability.
- V51 remains separate and unchanged.
- The unresolved MM-UAV redistribution license remains a dissemination restriction.

## Allowed completion states

- `V54_GPU_PILOT_PASS_READY_FOR_PAIRED_ALIGNMENT_ABLATION`
- `V54_BLOCKED_DETECTOR_INTEGRATION`
- `V54_BLOCKED_DATA_OR_TARGET_CONTRACT`
- `V54_BLOCKED_OOM_OR_MEMORY`
- `V54_BLOCKED_NUMERICAL_INSTABILITY`
- `V54_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`
