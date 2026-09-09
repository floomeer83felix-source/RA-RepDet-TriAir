# Experiment Status

Updated: 2026-09-09

## Active status

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_COMPLETE`

V87 integrated the authoritative V81 single-modality evidence and V86 matched RGB+thermal versus RGB+thermal+event dynamic-gating comparison into the active manuscript. No new training, inference, evaluation, tuning, checkpoint selection, historical-holdout access, or V86 outer-fold access occurred.

## Integrated TriAir evidence

| System | AP@[.50:.95] | AP50 | AP75 | AR100 |
| --- | ---: | ---: | ---: | ---: |
| RGB-only | `0.4473 +/- 0.0033` | `0.7674 +/- 0.0036` | `0.4428 +/- 0.0098` | `0.5897 +/- 0.0024` |
| Thermal-only | `0.5196 +/- 0.0196` | `0.8320 +/- 0.0154` | `0.5776 +/- 0.0244` | `0.6473 +/- 0.0132` |
| Event-only | `0.1949 +/- 0.0012` | `0.3657 +/- 0.0032` | `0.1943 +/- 0.0049` | `0.3558 +/- 0.0067` |
| RGB+thermal dynamic | `0.6912 +/- 0.0280` | `0.9461 +/- 0.0028` | `0.8409 +/- 0.0241` | `0.7673 +/- 0.0232` |
| RGB+thermal+event dynamic | `0.7251 +/- 0.0121` | `0.9475 +/- 0.0003` | `0.8742 +/- 0.0081` | `0.7917 +/- 0.0098` |

Paired tri-modal minus RGB+thermal AP differences are `-0.0110`, `+0.0657`, and `+0.0471` for seeds 0, 1, and 2. Mean paired AP is `+0.0339 +/- 0.0400`, with positive gains in `2/3` seeds. AP50 is nearly unchanged; the descriptive gain is concentrated in AP75 and AR100.

## Scientific conclusion

Event-only is the weakest standalone TriAir detector, but the matched V86 comparison supports complementary event contribution on average when event is fused with RGB and thermal. The result is descriptive: it does not establish uniform per-seed improvement, statistical significance, universal event utility, or calibrated sensor-health estimation.

During V87 integration, an older manuscript section containing idealized V73 reference values was detected and corrected to the frozen actual V73 MM-UAV results:

- Scratch Equal AP: `0.2234 +/- 0.0073`;
- TriAir Init Equal AP: `0.2178 +/- 0.0020`;
- TriAir Init Reliability AP: `0.2151 +/- 0.0090`.

The MM-UAV conclusion is therefore restored to: supervised alignment recovers useful performance, while source initialization and reliability-aware fusion do not improve the three-seed mean under the frozen V73 schedule.

## Manuscript validation

- local integrated authoring PDF: 13 pages;
- two consecutive pdfLaTeX passes: PASS;
- undefined citations/references: 0;
- overfull boxes after table correction: 0;
- rendered-page audit: PASS;
- V85 qualitative figure asset: unchanged.

## Next task

`V88_MANUSCRIPT_RELEASE_CANDIDATE_CONSISTENCY_AUDIT_AUTHORIZED`

V88 is a final manuscript consistency and submission-readiness task only. No new experiment is authorized.
