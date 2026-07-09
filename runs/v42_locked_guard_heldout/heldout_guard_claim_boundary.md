# V42 Held-out Guard Claim Boundary

## Allowed claims

- Locked held-out guard evaluation on `runs/component_disjoint_v40/guard.txt`.
- Three fixed seed pairs: matched early fusion vs reliability-aware p=0.15 for seed0, seed1, and seed2.
- Descriptive AP50/AP75/F1/precision/recall comparisons under the project-local evaluator and fixed operating threshold.
- The guard manifest was not used to train, tune, select checkpoints, sweep dropout, profile, or edit manuscript claims during this task.

## Required cautions

- This is a held-out TriAir guard partition from the same project dataset, not an external dataset.
- The result is descriptive with n=3 seed pairs; do not state statistical significance.
- Do not claim optimal dropout, calibrated physical sensor reliability, robustness to real sensor faults, or COCO AP@[0.50:0.95].
- Do not use the guard results for future model selection unless the guard is explicitly reclassified and the claim boundary is rewritten.

## Recommended wording

A locked held-out guard evaluation on the frozen V40 component-disjoint guard manifest showed descriptive mean AP50/AP75/F1 gains for reliability-aware p=0.15 over matched early fusion across three fixed seed pairs, with mixed per-seed F1 and AP75 deltas. These results remain within-dataset held-out evidence and should not be described as external generalization or statistical proof.
