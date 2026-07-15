# RA-RepDet-TriAir Handoff

Generated: 2026-07-15

## Current task

- V54 decision: `V54_GPU_PILOT_PASS_READY_FOR_PAIRED_ALIGNMENT_ABLATION`.
- Starting commit: `e00f4f829445216fd778f0dc842623793a93b93f`.
- Frozen RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032; hashes reproduced exactly.
- Integration: aligned/equal-fused features -> 1x1 3-channel projection -> existing RepViT-M0.9-FPN-FCOS.
- Four CUDA smoke interfaces passed finite forward/backward with zero optimizer steps.
- Primary `alignment_on_equal` pilot completed exactly 200/200 steps; all loss, gradient, parameter, theta, and grid checks were finite.
- Peak allocated/reserved memory: 354,884,608 / 394,264,576 bytes; mean step time 0.7190 seconds.
- Step-200 IR/Event theta deviations: 0.01609 / 0.04019; determinants: 1.00614 / 0.98230; grid OOB: 1.6875% / 1.5469%.
- Local checkpoint: `D:\MM-UAV_v54_local\alignment_on_equal_step200.pt`, 27,104,577 bytes, SHA256 `9853c9ffd66e83e7e0c46a953c9cb4cb67681ee6126706f4031b9a9b0854fcce`; not committed.
- Postrun inference-path smoke passed on four devval samples; no AP/AR was computed.
- CPU tests: 8/8 pass before and after GPU. Protected production/history/manuscript files unchanged.
- Reproducibility limitation: CUDA grid-sample backward and some CuBLAS operations emitted warn-only non-determinism notices.

## Required action

Do not run further GPU experiments without a new task. The next possible step is a separately authorized paired alignment-off/on ablation. V54 provides engineering stability evidence only, not an accuracy or manuscript claim. V51 and the private-use/license boundary remain unchanged.
