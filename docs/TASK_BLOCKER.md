# Task Blocker

## Current M3OT experiment gate (2026-09-24)

No active failure is asserted. The M3OT RGB/IR/GT pairing and visual-review
gates passed on 2026-09-24, and the matched six-run training queue is now
running. The sole unpaired train RGB frame is excluded and documented in the
audit; imperfect RGB/IR pixel alignment is a disclosed limitation, not a
silent annotation correction. V88 remains deferred, and its frozen
scientific claims must not be silently revised. If M3OT training or final
verification fails, record the exact error here before proceeding.

Status: `V87_COMPLETE_NO_ACTIVE_EXPERIMENT_BLOCKER_V88_RELEASE_AUDIT_AUTHORIZED`

Updated: 2026-09-09

## Current state

V87 is complete. The V81 single-modality table, V86 matched event-contribution comparison, same-seed deltas, and bounded interpretation are integrated into the active manuscript. The V73 MM-UAV section has also been restored to the frozen actual metrics after removal of an older idealized reference table.

There is no active experimental blocker and no new experiment is authorized.

## Frozen claim boundary

The manuscript may state that:

- thermal-only is the strongest V81 standalone modality and event-only is the weakest;
- RGB+thermal+event dynamic improves mean AP over matched RGB+thermal dynamic by `+0.0339 +/- 0.0400`;
- the AP improvement is positive for `2/3` seeds and negative for seed 0;
- AP50 is nearly unchanged, while AP75 and AR100 show clearer descriptive mean gains;
- event provides complementary average value under the frozen TriAir development protocol;
- V73 supervised alignment restores MM-UAV performance, but TriAir initialization and reliability-aware fusion do not improve the three-seed mean.

The manuscript must not claim uniform event benefit, statistical significance, calibrated physical sensor health, independent blind external validation, universal cross-dataset superiority, or positive V73 transfer from the removed idealized reference values.

## V88 boundary

V88 may only perform final manuscript consistency, author-metadata, table/figure/reference, build, and release-candidate checks. It may not run training, inference, evaluation, threshold search, checkpoint replacement, or new dataset experiments.
