# Next Task Write Record

Written: 2026-07-20
Branch: `research/ra-repdet-triair`
Previous user-provided base: `286508ff34d4cd0ac494d803e5a146a686318f14`
Canonical task file: `docs/NEXT_TASK.md`

## Active next task

`V63_MMUAV_PAIRED_BBOX_ACTIVATION_RESCUE_PILOT_AUTHORIZED`

Execute the frozen V63 paired bbox-activation rescue pilot exactly as specified in `docs/NEXT_TASK.md`:

1. Run `v63_equal_relu_control` for exactly 200 optimizer steps.
2. Run `v63_equal_softplus_b1_t20` for exactly 200 optimizer steps.
3. Preserve identical seed-0 initialization, first-200 frozen sample order, parameters, buffers, losses, matching, decode, alignment, equal fusion, and dormant reliability scorer.
4. Permit only the bbox-distance activation difference: historical ReLU versus `softplus(beta=1.0, threshold=20.0)` in both training and inference paths.
5. Complete all CPU/source-lock, paired-state, activation-location, actual-devval-row, protected-file, and recovery-snapshot gates before CUDA.
6. Respect the 400 optimizer-step and 104 diagnostic-backward-call ceilings.
7. Do not run full devval, AP/AR, tuning, checkpoint selection, extra variants/seeds, reruns, or automatic extensions.
8. Keep checkpoints, optimizer states, recovery snapshots, tensors, predictions, and media local and outside Git.

## Handoff status

The next task instruction is present and active. Begin with the pre-CUDA source-lock and state-identity tests in `docs/NEXT_TASK.md`. Stop fail-closed on any contract mismatch.
