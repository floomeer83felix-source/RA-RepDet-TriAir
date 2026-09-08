# Experiment Status

Updated: 2026-09-08

## Active task

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_AUTHORIZED`

## V86 completion

V86 completed at commit `d489b82ae0bd9fe650e012c157fb1eb0212a5495` with a deterministic three-seed RGB+thermal dynamic control under the same frozen TriAir component-disjoint development-validation protocol as the authoritative tri-modal dynamic-gating source.

Completion facts:

- RGB+thermal dynamic seeds `0/1/2`: complete;
- matched RGB+thermal+event dynamic seeds `0/1/2`: frozen from authoritative V84 source;
- common split SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`;
- deterministic result regeneration: verified;
- GPU released; stderr error: none;
- historical guard access: none;
- V86 outer-fold access: none;
- checkpoints/weights committed to Git: none.

### V86 three-seed summary

| Model | AP@[.50:.95] | AP50 | AP75 | AR100 |
| --- | ---: | ---: | ---: | ---: |
| RGB+thermal dynamic | `0.6912 +/- 0.0280` | `0.9461 +/- 0.0028` | `0.8409 +/- 0.0241` | `0.7673 +/- 0.0232` |
| RGB+thermal+event dynamic | `0.7251 +/- 0.0121` | `0.9475 +/- 0.0003` | `0.8742 +/- 0.0081` | `0.7917 +/- 0.0098` |

Paired tri-modal minus RGB+thermal:

- AP: `+0.033904545 +/- 0.040004676`, positive seeds `2/3`;
- AP50: `+0.001470700`, positive seeds `2/3`;
- AP75: `+0.033273038`, positive seeds `2/3`;
- AR100: `+0.024367934`, positive seeds `2/3`.

Seed-level AP differences are `-0.011024848`, `+0.065663667`, and `+0.047074816` for seeds 0, 1, and 2 respectively.

## Scientific conclusion

The V86 evidence supports a descriptive average contribution from the event stream under the frozen TriAir development-validation protocol. The mean gain is concentrated in COCO AP, AP75, and AR100, while AP50 is effectively unchanged. Because seed 0 does not improve and only `2/3` seeds are positive, V86 does not support uniform per-seed improvement, statistical significance, or universal event utility.

This result complements the authoritative V81 single-modality evidence:

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | `0.4473 +/- 0.0033` | `0.7674 +/- 0.0036` | `0.4428 +/- 0.0098` | `0.1650 +/- 0.0009` | `0.5225 +/- 0.0036` | `0.5897 +/- 0.0024` |
| Thermal-only | `0.5196 +/- 0.0196` | `0.8320 +/- 0.0154` | `0.5776 +/- 0.0244` | `0.2035 +/- 0.0081` | `0.5826 +/- 0.0148` | `0.6473 +/- 0.0132` |
| Event-only | `0.1949 +/- 0.0012` | `0.3657 +/- 0.0032` | `0.1943 +/- 0.0049` | `0.0751 +/- 0.0033` | `0.2694 +/- 0.0014` | `0.3558 +/- 0.0067` |

Together, V81 and V86 support the bounded interpretation that event is weak as a standalone detector but can provide complementary information when fused with RGB and thermal.

## Active V87 work

V87 must integrate the V81 and V86 evidence into the current manuscript with exact number traceability and conservative wording. No new experiment is authorized.

Required completion state:

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_COMPLETE`

Required completion commit:

`docs: integrate V81-V86 TriAir event contribution evidence into manuscript`