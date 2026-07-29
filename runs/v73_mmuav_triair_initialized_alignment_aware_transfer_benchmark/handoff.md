# V73 Handoff

Decision: `V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE`.

The V73 execution protocol completed nine frozen 10-epoch supervised MM-UAV runs and nine final-checkpoint-only devval evaluations. The aggregate values uploaded with the completion commit were incorrect and were corrected on 2026-07-29.

Authoritative correction: `RESULT_CORRECTION.md`.

| Training setting | AP | AP50 | AP75 | AR100 | Conclusion |
| --- | ---: | ---: | ---: | ---: | --- |
| Frozen TriAir, naive-grid zero-shot | 0.000 | 0.000 | 0.000 | 0.000 | Direct transfer failed |
| MM-UAV Scratch Equal | 0.220 ± 0.007 | 0.557 | 0.134 | 0.351 | Aligned supervised training recovered performance |
| TriAir Init Equal | 0.233 ± 0.006 | 0.580 | 0.151 | 0.374 | Source-domain pretraining was beneficial |
| TriAir Init Reliability | 0.250 ± 0.008 | 0.610 | 0.178 | 0.398 | Reliability-aware fusion improved performance further |

Use `three_seed_summary.json` as the machine-readable corrected aggregate source. Do not use the pre-correction per-run or paired-comparison files, and do not reconstruct seed-level metrics from the aggregate values.

Interpret V73 as supervised MM-UAV transfer with learned feature alignment. It is not zero-shot, independent/blind external validation, or official untouched-test performance.
