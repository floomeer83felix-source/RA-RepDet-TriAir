# Current Task

## Authorization

V86 completed at commit `d489b82ae0bd9fe650e012c157fb1eb0212a5495` with the frozen result:

`V86_MINIMAL_RGBT_DYNAMIC_DEVVAL_COMPLETE`

The active next task is:

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_AUTHORIZED`

V87 is a manuscript-evidence integration task only. It must integrate the authoritative V81 single-modality evidence and the V86 matched RGB+thermal versus RGB+thermal+event dynamic-gating comparison into the current manuscript without new training, inference, tuning, checkpoint selection, or holdout access.

## Frozen evidence

### V81 single-modality three-seed results

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | `0.4473 +/- 0.0033` | `0.7674 +/- 0.0036` | `0.4428 +/- 0.0098` | `0.1650 +/- 0.0009` | `0.5225 +/- 0.0036` | `0.5897 +/- 0.0024` |
| Thermal-only | `0.5196 +/- 0.0196` | `0.8320 +/- 0.0154` | `0.5776 +/- 0.0244` | `0.2035 +/- 0.0081` | `0.5826 +/- 0.0148` | `0.6473 +/- 0.0132` |
| Event-only | `0.1949 +/- 0.0012` | `0.3657 +/- 0.0032` | `0.1943 +/- 0.0049` | `0.0751 +/- 0.0033` | `0.2694 +/- 0.0014` | `0.3558 +/- 0.0067` |

Common component-disjoint devval split SHA256:
`722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`.

### V86 matched event-contribution comparison

| Model | AP@[.50:.95] | AP50 | AP75 | AR100 |
| --- | ---: | ---: | ---: | ---: |
| RGB+thermal dynamic | `0.6912 +/- 0.0280` | `0.9461 +/- 0.0028` | `0.8409 +/- 0.0241` | `0.7673 +/- 0.0232` |
| RGB+thermal+event dynamic | `0.7251 +/- 0.0121` | `0.9475 +/- 0.0003` | `0.8742 +/- 0.0081` | `0.7917 +/- 0.0098` |

Same-seed tri-modal minus RGB+thermal AP:

- seed 0: `-0.011024848`;
- seed 1: `+0.065663667`;
- seed 2: `+0.047074816`;
- mean: `+0.033904545`;
- sample SD: `0.040004676`;
- positive seeds: `2/3`.

Other paired mean differences:

- AP50: `+0.001470700`, positive seeds `2/3`;
- AP75: `+0.033273038`, positive seeds `2/3`;
- AR100: `+0.024367934`, positive seeds `2/3`.

Authoritative sources:

- `reproducibility/v86_minimal_rgbt_dynamic_devval/results/V86_MINIMAL_RGBT_DYNAMIC_RESULT.md`;
- `reproducibility/v86_minimal_rgbt_dynamic_devval/results/rgbt_dynamic_per_seed.csv`;
- `reproducibility/v86_minimal_rgbt_dynamic_devval/results/paired_event_deltas.csv`;
- V86 completion commit `d489b82ae0bd9fe650e012c157fb1eb0212a5495`.

## Required manuscript changes

1. Add or update one compact single-modality table using the exact V81 COCO metrics.
2. Add one matched two-modal versus tri-modal dynamic-gating table using the exact V86 three-seed means and sample standard deviations.
3. Report the same-seed AP deltas and state explicitly that only `2/3` seeds improve.
4. State that AP50 is nearly unchanged, while the descriptive mean gain is concentrated in stricter localization and recall: AP75 and AR100.
5. Connect V81 and V86 without overclaiming: event-only is the weakest standalone modality, yet event information can still provide complementary value when fused with RGB and thermal.
6. Preserve the existing interpretation of dynamic gating as task-driven routing coefficients, not calibrated physical sensor-health estimates.
7. Keep all component-disjoint devval, holdout, MM-UAV, and external-generalization boundaries unchanged.
8. Rebuild the manuscript and inspect the updated tables, references, page layout, and captions.

## Required interpretation

Allowed wording should be equivalent to:

> On the frozen component-disjoint development-validation protocol, event-only detection is substantially weaker than RGB-only or thermal-only detection, but adding the event stream to the matched RGB+thermal dynamic-gating system yields a descriptive three-seed mean improvement in COCO AP (+0.0339), AP75 (+0.0333), and AR100 (+0.0244), while AP50 remains nearly unchanged. The AP improvement is positive for two of three seeds, so the evidence supports complementary event contribution on average but not uniform per-seed improvement or statistical significance.

## Prohibited claims

Do not claim:

- event improves every seed;
- statistically significant event benefit;
- universal event-sensor utility;
- independent test-set confirmation;
- calibrated sensor reliability or physical sensor-health estimation;
- SOTA solely from this comparison;
- access to or evidence from the historical guard or V86 outer folds.

## Forbidden work

- no new training, fine-tuning, inference, evaluation, seed, checkpoint, or threshold sweep;
- no result-driven reruns;
- no historical 837-image holdout access;
- no V86 outer-fold access;
- no metric recomputation from alternate evaluators;
- no selective omission of seed 0;
- no raw checkpoints or private/heavy artifacts committed to Git.

## Required outputs

Create a compact manuscript-integration record under:

`runs/v87_triair_event_contribution_manuscript_integration/`

Include at minimum:

- `evidence_lock.json`;
- `manuscript_change_map.json`;
- `number_traceability.json`;
- `claim_audit.json`;
- `build_output.txt`;
- `rendered_page_audit.md`;
- `final_decision.json`;
- `handoff.md`.

## Decision states

Choose exactly one:

- `V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_COMPLETE`;
- `V87_BLOCKED_EVIDENCE_OR_NUMBER_TRACEABILITY`;
- `V87_BLOCKED_CLAIM_OVERREACH`;
- `V87_BLOCKED_MANUSCRIPT_BUILD_OR_LAYOUT`;
- `V87_BLOCKED_PROTECTED_ARTIFACT_VIOLATION`.

## Completion commit

Commit with exactly:

`docs: integrate V81-V86 TriAir event contribution evidence into manuscript`

Push to `research/ra-repdet-triair`.