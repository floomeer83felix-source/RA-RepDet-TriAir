# V83 Post-V81 Efficiency Summary

Status: `V83_WEIGHT_PREFLIGHT_AND_EFFICIENCY_COMPLETE`

Synthetic label-free full-detector inference; RTX 3090; batch 1; 640x640; FP32; 50 warm-up and 200 measured iterations; CUDA synchronized around every timed inference.

| Group | N | Params | FLOPs | Mean ms (mean +/- SD) | Median ms | P95 ms | FPS | Peak allocated MiB | Peak reserved MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| event | 3 | 6591597 | 104752610753 | 22.1268 +/- 0.3090 | 21.9267 | 24.1507 | 45.1998 | 109.24 | 162.00 |
| matched_early | 3 | 6591609 | 104762430035 | 22.0800 +/- 0.3082 | 21.8179 | 24.0838 | 45.2957 | 122.49 | 176.00 |
| ra_full_p015 | 3 | 6593293 | 105392395691 | 22.2324 +/- 0.1879 | 22.1347 | 23.9717 | 44.9815 | 236.16 | 258.00 |
| rgb | 3 | 6591603 | 104757515549 | 22.0658 +/- 0.1616 | 21.9711 | 23.4099 | 45.3205 | 115.49 | 176.00 |
| thermal | 3 | 6591597 | 104752603681 | 22.1972 +/- 0.3814 | 21.9522 | 24.0521 | 45.0595 | 109.24 | 162.00 |

FLOPs are the sum reported by `torch.profiler` for one full detector call; derived MACs are FLOPs/2 and inherit profiler operator-coverage limitations.
Runtime variation across seeds is an execution repeat, not statistical accuracy evidence. No dataset, validation labels, or locked holdout were accessed.
