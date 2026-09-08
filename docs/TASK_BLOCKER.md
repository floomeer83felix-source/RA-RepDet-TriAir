# Task Blocker

Status: `V87_MANUSCRIPT_INTEGRATION_AUTHORIZED_NO_ACTIVE_EXPERIMENT_BLOCKER`

Updated: 2026-09-08

## Current state

V86 is complete at commit `d489b82ae0bd9fe650e012c157fb1eb0212a5495`. All three RGB+thermal dynamic seeds completed under the frozen TriAir component-disjoint development-validation split and were deterministically compared against the authoritative matched tri-modal dynamic-gating rows.

There is no active experimental blocker. The next task is manuscript integration only:

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_AUTHORIZED`

## Frozen evidence boundary

The manuscript may state that:

- RGB+thermal dynamic reaches AP `0.6912 +/- 0.0280`;
- RGB+thermal+event dynamic reaches AP `0.7251 +/- 0.0121`;
- the paired AP mean difference is `+0.0339 +/- 0.0400`;
- AP is positive for `2/3` seeds and negative for seed 0;
- AP50 is almost unchanged on average (`+0.00147`);
- AP75 (`+0.03327`) and AR100 (`+0.02437`) show the clearest descriptive mean gains;
- event-only remains the weakest V81 single-modality detector, so its value is complementary rather than dominant under this protocol.

## Claims that remain blocked

Do not state or imply:

- event improves every random seed;
- statistical significance;
- universal or dataset-independent event benefit;
- independent test-set validation;
- physical sensor-failure robustness;
- calibrated sensor-health probabilities;
- historical guard or V86 outer-fold confirmation;
- SOTA based on this comparison alone.

## Protected work boundary

V87 must not:

- run new training, inference, evaluation, threshold search, or hyperparameter tuning;
- access the historical 837-image partition;
- access V86 outer folds;
- rerun only unfavorable seeds;
- replace checkpoints or evaluator definitions;
- commit model weights, raw datasets, or private/heavy artifacts.

## Fail-closed conditions

Use a blocked V87 state only if one of the following occurs:

1. manuscript numbers cannot be traced exactly to the frozen V81/V86 evidence;
2. the manuscript still contains uniform-improvement, significance, independent-test, or calibrated-reliability overclaims;
3. the manuscript no longer compiles cleanly or the new tables/captions render incorrectly;
4. protected or heavy artifacts enter the Git diff.

Otherwise complete V87 with:

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_COMPLETE`.