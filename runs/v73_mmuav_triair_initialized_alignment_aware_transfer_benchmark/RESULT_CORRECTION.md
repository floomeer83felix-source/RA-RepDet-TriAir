# V73 Result Correction

Corrected: 2026-07-29

The V73 metrics uploaded in completion commit `eafceccdedfc0bea93170a671906619b004412f4` were incorrect. A first aggregate-only correction was subsequently superseded when the corrected nine-row seed-level table was supplied. The records below are authoritative for all subsequent documentation and manuscript work.

## Corrected three-seed summary

| Method | AP mean ± sample std | AP50 mean | AP75 mean | AR100 mean | Conclusion |
| --- | ---: | ---: | ---: | ---: | --- |
| Scratch Equal | 0.2210 ± 0.0030 | 0.5567 | 0.1347 | 0.3530 | Aligned supervised training recovered performance |
| TriAir Init Equal | 0.2340 ± 0.0020 | 0.5797 | 0.1510 | 0.3717 | Source-domain pretraining was beneficial |
| TriAir Init Reliability | 0.2503 ± 0.0025 | 0.6077 | 0.1750 | 0.3920 | Reliability-aware fusion improved performance further |

## Corrected per-seed metrics

| Seed | Method | AP | AP50 | AP75 | AR1 | AR10 | AR100 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | Scratch Equal | 0.218 | 0.552 | 0.131 | 0.171 | 0.332 | 0.349 |
| 0 | TriAir Init Equal | 0.232 | 0.575 | 0.148 | 0.179 | 0.349 | 0.368 |
| 0 | TriAir Init Reliability | 0.248 | 0.603 | 0.171 | 0.188 | 0.367 | 0.388 |
| 1 | Scratch Equal | 0.224 | 0.561 | 0.138 | 0.176 | 0.340 | 0.357 |
| 1 | TriAir Init Equal | 0.236 | 0.584 | 0.154 | 0.184 | 0.356 | 0.375 |
| 1 | TriAir Init Reliability | 0.253 | 0.612 | 0.179 | 0.193 | 0.375 | 0.396 |
| 2 | Scratch Equal | 0.221 | 0.557 | 0.135 | 0.174 | 0.336 | 0.353 |
| 2 | TriAir Init Equal | 0.234 | 0.580 | 0.151 | 0.181 | 0.353 | 0.372 |
| 2 | TriAir Init Reliability | 0.250 | 0.608 | 0.175 | 0.190 | 0.371 | 0.392 |

## Paired AP differences

- TriAir Init Equal minus Scratch Equal: `0.0130 ± 0.0010`; positive for all three seeds.
- TriAir Init Reliability minus TriAir Init Equal: `0.0163 ± 0.0006`; positive for all three seeds.
- TriAir Init Reliability minus Scratch Equal: `0.0293 ± 0.0006`; positive for all three seeds.

## Authority and scope

- `corrected_per_run_metrics.csv` and `.json` are the authoritative corrected seed-level metric sources.
- `three_seed_summary.json` and `corrected_paired_transfer_comparison.json` are independently recomputed from those nine rows.
- The old `per_run_metrics.*` and `paired_transfer_comparison.*` files remain invalidated historical uploads and must not be used.
- The comparisons are descriptive. Three seeds and an exposed devval split do not establish statistical significance, independent external validation, or official untouched-test performance.
