# V80 supplied standardized single-modality metrics

## Received evidence

The user supplied nine rows covering RGB-only, thermal-only, and event-only at seeds 0, 1, and 2. Each row reports COCO AP@[0.50:0.95], AP50, AP75, AR1, AR10, and AR100.

Independent recomputation uses the sample standard deviation (`n-1`).

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.3073 ± 0.0065 | 0.6527 ± 0.0086 | 0.3807 ± 0.0085 | 0.2857 ± 0.0055 | 0.4550 ± 0.0070 | 0.4830 ± 0.0070 |
| Thermal-only | 0.4633 ± 0.0085 | 0.8497 ± 0.0080 | 0.6263 ± 0.0111 | 0.3877 ± 0.0065 | 0.5973 ± 0.0085 | 0.6320 ± 0.0090 |
| Event-only | 0.1020 ± 0.0060 | 0.3347 ± 0.0125 | 0.1260 ± 0.0080 | 0.1220 ± 0.0040 | 0.2437 ± 0.0075 | 0.2710 ± 0.0080 |

## Reconciliation

All nine AP50 and AP75 pairs match the V77 supplied values exactly at three decimal places. No earlier value is replaced by a numerically different result.

## Identity boundary

The table does not include checkpoint SHA256, checkpoint epoch, split SHA256, runtime environment, or the original evaluator JSON files. These fields are not inferred. The ongoing V81 retraining task remains a separate replication/provenance activity and must not be represented as recovery of the lost V77 checkpoints.

## Manuscript boundary

A 16-page V80 draft was built and visually audited from the supplied metric table, but the repository's authoritative manuscript should remain V78 while V81 is running and until checkpoint/evaluator identity evidence is archived or the authors explicitly accept the supplied-table-only provenance level.
