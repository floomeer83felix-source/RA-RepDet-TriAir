# Next Task Write Record

Written: 2026-09-08
Branch: `research/ra-repdet-triair`

## Completed prior task

V86 completion commit:

`d489b82ae0bd9fe650e012c157fb1eb0212a5495`

Commit message:

`results: add three-seed RGB-thermal dynamic control`

Verified V86 result:

`V86_MINIMAL_RGBT_DYNAMIC_DEVVAL_COMPLETE`

The branch head was exactly the V86 completion commit before this handoff was written.

## Frozen V86 evidence

Three-seed means +/- sample SD:

| Model | AP@[.50:.95] | AP50 | AP75 | AR100 |
| --- | ---: | ---: | ---: | ---: |
| RGB+thermal dynamic | `0.6912 +/- 0.0280` | `0.9461 +/- 0.0028` | `0.8409 +/- 0.0241` | `0.7673 +/- 0.0232` |
| RGB+thermal+event dynamic | `0.7251 +/- 0.0121` | `0.9475 +/- 0.0003` | `0.8742 +/- 0.0081` | `0.7917 +/- 0.0098` |

Paired tri-modal minus two-modal AP by seed:

- seed 0: `-0.011024848`;
- seed 1: `+0.065663667`;
- seed 2: `+0.047074816`;
- mean: `+0.033904545`;
- sample SD: `0.040004676`;
- positive seeds: `2/3`.

Paired mean deltas for other metrics:

- AP50: `+0.001470700`;
- AP75: `+0.033273038`;
- AR100: `+0.024367934`.

Authoritative V86 files:

- `reproducibility/v86_minimal_rgbt_dynamic_devval/results/V86_MINIMAL_RGBT_DYNAMIC_RESULT.md`;
- `reproducibility/v86_minimal_rgbt_dynamic_devval/results/rgbt_dynamic_per_seed.csv`;
- `reproducibility/v86_minimal_rgbt_dynamic_devval/results/paired_event_deltas.csv`.

## Active next task

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_AUTHORIZED`

Canonical task file:

`docs/NEXT_TASK.md`

V87 must integrate the authoritative V81 single-modality results together with V86 into the manuscript. The intended scientific message is bounded:

1. Thermal-only is the strongest single modality, RGB-only is second, and event-only is weakest under the V81 COCO protocol.
2. Event-only weakness does not imply zero complementary value in fusion.
3. Adding event to the matched RGB+thermal dynamic model increases three-seed mean AP by `+0.0339`, AP75 by `+0.0333`, and AR100 by `+0.0244`.
4. AP50 changes by only `+0.00147` on average.
5. Seed 0 does not improve in AP, AP75, or AR100; therefore only descriptive average improvement is supported.
6. No significance, universal event benefit, independent-test, calibrated-reliability, or physical sensor-health claim is authorized.

## Execution restriction

V87 is manuscript-only. No new training, inference, evaluator run, threshold tuning, seed addition, holdout access, V86 outer-fold access, or result-driven rerun is authorized.

## Required completion

Successful state:

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_COMPLETE`

Required completion commit:

`docs: integrate V81-V86 TriAir event contribution evidence into manuscript`

Push to `research/ra-repdet-triair`.