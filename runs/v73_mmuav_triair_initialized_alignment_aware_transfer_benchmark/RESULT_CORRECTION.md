# V73 Result Correction

Corrected: 2026-07-29

The V73 result values previously uploaded in commit `eafceccdedfc0bea93170a671906619b004412f4` were incorrect. The table below is the authoritative aggregate result set for all subsequent documentation and manuscript work.

| Training setting | AP | AP50 | AP75 | AR100 | Conclusion |
| --- | ---: | ---: | ---: | ---: | --- |
| Frozen TriAir, naive-grid zero-shot | 0.000 | 0.000 | 0.000 | 0.000 | Direct transfer failed |
| MM-UAV Scratch Equal | 0.220 ± 0.007 | 0.557 | 0.134 | 0.351 | Aligned supervised training recovered performance |
| TriAir Init Equal | 0.233 ± 0.006 | 0.580 | 0.151 | 0.374 | Source-domain pretraining was beneficial |
| TriAir Init Reliability | 0.250 ± 0.008 | 0.610 | 0.178 | 0.398 | Reliability-aware fusion improved performance further |

## Authority and scope

- These aggregate values supersede the pre-correction V73 aggregate values and conclusions.
- `three_seed_summary.json` is updated to carry the corrected aggregate values.
- The previously uploaded `per_run_metrics.csv`, `per_run_metrics.json`, `paired_transfer_comparison.csv`, and `paired_transfer_comparison.json` are invalidated as metric sources because corrected seed-level values were not supplied with this correction.
- Do not reconstruct or invent seed-level metrics or paired differences from the aggregate table.
- Until corrected seed-level records are supplied, V74 may report only the aggregate table above and must not include the invalidated per-seed or paired-difference tables.
- The scientific boundary remains unchanged: V73 uses MM-UAV supervision and is not zero-shot, independent/blind external validation, or official untouched-test performance.
