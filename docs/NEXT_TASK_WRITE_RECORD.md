# Next Task Write Record

Written: 2026-08-04
Branch: `research/ra-repdet-triair`

## Authoritative evidence-source decision

The author requested inspection of the latest pushed branch and explicitly directed that the latest checkpoint-backed experimental result be used as the source of truth.

The inspected branch HEAD before this decision record was:

```text
504182a4d63e5984cab2bfb942f3bf9469635611
```

Commit message:

```text
results: archive V81 single-modality retraining evaluation
```

## Selected evidence

`V81_CHECKPOINT_BACKED_SINGLE_MODALITY_EVIDENCE_SELECTED_AUTHORITATIVE`

V81 contains:

- nine fresh frozen-protocol single-modality training runs;
- nine retained `best.pt` checkpoints;
- nine standardized COCO evaluations;
- checkpoint epoch and SHA256 for every run;
- one consistent frozen validation-manifest SHA256;
- runtime and reconciliation records;
- no guard access, tuning, seed replacement, selective rerun, or checkpoint substitution.

Authoritative three-seed values:

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.4473 ± 0.0033 | 0.7674 ± 0.0036 | 0.4428 ± 0.0098 | 0.1650 ± 0.0009 | 0.5225 ± 0.0036 | 0.5897 ± 0.0024 |
| Thermal-only | 0.5196 ± 0.0196 | 0.8320 ± 0.0154 | 0.5776 ± 0.0244 | 0.2035 ± 0.0081 | 0.5826 ± 0.0148 | 0.6473 ± 0.0132 |
| Event-only | 0.1949 ± 0.0012 | 0.3657 ± 0.0032 | 0.1943 ± 0.0049 | 0.0751 ± 0.0033 | 0.2694 ± 0.0014 | 0.3558 ± 0.0067 |

## Superseded reporting source

The supplied V77/V80 single-modality table remains archived for provenance and reconciliation only. It lacks the complete checkpoint identity package and differs materially from V81. It is no longer authorized as the primary manuscript evidence and must not be numerically mixed with V81.

## Next task

Create and audit a new V82 manuscript using V81 as the primary single-modality evidence. V78 remains the root manuscript only until the V82 compilation and rendered-page audit pass.

## Decision commits

- `docs: select checkpoint-backed V81 evidence as authoritative`;
- `docs: set V82 authoritative V81 manuscript task`;
- `docs: resolve V81 evidence-source blocker`;
- `docs: record authoritative V81 evidence decision`.
