# V39 Component-Disjoint Validation Blocker

The V39 continuation task was stopped at the required pre-run audit gate.

## Decision

`BLOCKED`: do not start the missing reliability `p=0.20` runs until the split issue is resolved or the research owner explicitly relaxes the gate.

## Evidence

- Generic split integrity audit: `runs/v39_component_disjoint_split_audit/split_integrity_summary.md`.
- Component-disjoint gate audit: `runs/v39_component_disjoint_split_audit/component_disjoint_audit_summary.md`.
- Guard-band violation sample: `runs/v39_component_disjoint_split_audit/component_disjoint_guard_band_violations_sample.csv`.

## Blocking Metrics

| Metric | Value |
| --- | ---: |
| train rows | 7439 |
| validation rows | 2213 |
| guard rows | 837 |
| train/validation path overlap | 0 |
| train/validation exact RGB groups | 0 |
| train/guard exact RGB groups | 4 |
| validation/guard exact RGB groups | 5 |
| same-family train/validation guard-band-16 violations | 353 |
| minimum same-family train/validation ID distance | 1 |
| component-disjoint audit status | FAIL |

## Actions Taken

- Ran required branch setup and fast-forward pull.
- Read the project instructions and V39 notes.
- Ran the generic split-integrity audit.
- Ran a V39-specific component-disjoint audit.
- Stopped before launching reliability `p=0.20` training.

No protected training core files, manuscript files, raw data, labels, or checkpoints were modified.
