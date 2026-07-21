# Next Task Write Record

Written: 2026-07-21
Branch: `research/ra-repdet-triair`
V63 completion commit: `83bb9351a5d0a6115d81047482e23fef5eed26bb`
Canonical task file: `docs/NEXT_TASK.md`

## Active next task

`V64_MMUAV_SEED1_PAIRED_BBOX_ACTIVATION_CONFIRMATION_AUTHORIZED`

Execute the frozen V64 seed-1 paired bbox-activation confirmation exactly as specified in `docs/NEXT_TASK.md`:

1. Generate exactly one fresh seed-1 common initialization, serialize it locally, compute its SHA256, strictly reload it, and freeze it before CUDA.
2. Run `v64_seed1_equal_relu_control` for exactly 200 optimizer steps.
3. Run `v64_seed1_equal_softplus_b1_t20` for exactly 200 optimizer steps.
4. Use the identical V63 first-200 historical rows and order for both variants.
5. Preserve bit-identical paired step-0 parameters, buffers, pre-activation bbox logits, classification/centerness outputs, fused features, alignment outputs, historical bbox bias, losses, matching, decode, and equal-fusion behavior.
6. Permit only the bbox-distance activation difference: native historical ReLU versus exact `softplus(beta=1.0, threshold=20.0)` in the shared training/inference path.
7. Complete all source-lock, seed-1 freeze, paired-state, actual-devval-row, protected-file, and recovery-snapshot gates before CUDA.
8. Respect the 400 optimizer-step and 104 diagnostic-backward-call ceilings.
9. Do not run full devval, AP/AR, tuning, checkpoint selection, extra seeds/variants, reruns, or automatic extensions.
10. Keep initialization artifacts, checkpoints, optimizer states, recovery snapshots, tensors, predictions, and media local and outside Git.

## Handoff status

The V64 instruction is written and active. Begin with the pre-CUDA V63 evidence verification, torchvision source lock, and one-time seed-1 initialization freeze. Stop fail-closed on any contract mismatch.