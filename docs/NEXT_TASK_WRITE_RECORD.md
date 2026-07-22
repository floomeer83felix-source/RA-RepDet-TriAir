# Next Task Write Record

Written: 2026-07-22
Branch: `research/ra-repdet-triair`
V64 completion commit: `402eabb23896f7908b6a3eccd4d394d3ce41d487`
Canonical task file: `docs/NEXT_TASK.md`

## Active next task

`V65_MMUAV_SEED0_SOFTPLUS_FULLTRAIN_DEVVAL_FEASIBILITY_AUTHORIZED`

Execute the frozen V65 full-training feasibility run exactly as specified in `docs/NEXT_TASK.md`:

1. Verify and preserve all V63/V64 and earlier evidence.
2. Reconstruct the exact historical seed-0 initialization with SHA256 `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`.
3. Build one alignment-on, exact equal-fusion, dormant-scorer model using exact `softplus(beta=1.0, threshold=20.0)` in the shared training/inference bbox-distance path.
4. Consume all 7,187 frozen historical training rows exactly once and run exactly 7,187 optimizer steps.
5. Run compact audits only at steps `0, 15, 50, 200, 500, 1000, 2000, 4000, 6000, 7187`, with at most 40 diagnostic backward calls.
6. Save and round-trip verify local recovery snapshots without replaying or skipping rows or steps.
7. Evaluate only the final step-7,187 checkpoint once on all 1,845 frozen devval rows.
8. Report fixed COCO-style AP/AR and prediction-safety metrics without tuning, threshold selection, or checkpoint selection.
9. Do not run a ReLU full control, reliability-fusion training, extra seed/variant, rerun, or automatic extension.
10. Keep checkpoints, optimizer states, recovery snapshots, raw predictions, tensors, images, and other heavy artifacts local and outside Git.

## Handoff status

The V65 instruction is written and active. Begin with the CPU source-lock, exact seed-0 initialization, complete-order, recovery, and evaluator-contract gates. Stop fail-closed on any contract mismatch.
