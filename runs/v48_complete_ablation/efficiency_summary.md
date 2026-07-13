# V48 Efficiency Summary

Generated: 2026-07-13T14:43:19+08:00

## Procedure

- Full FCOS detector inference was measured without dataloader or file-I/O time.
- Input: `1x5x640x640`, `float32`.
- Warm-up iterations: `10`; measured iterations: `30`.
- Each measured iteration is bracketed by CUDA synchronization when CUDA is used; latency is host wall time for the complete detector call.
- Operator FLOPs are summed from `torch.profiler` events for one full-detector inference. Derived MACs equal FLOPs/2 and exclude operations with no profiler FLOP estimate.

## Results

| Model | Total params | Trainable params | Operator FLOPs | Derived MACs | Mean ms | Median ms | P95 ms | FPS | Peak allocated MiB | Checkpoint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| early | 6591609 | 6591609 | 104762427192 | 52381213596.0 | 40.4046 | 39.2998 | 46.0084 | 24.7497 | 122.49072265625 | `runs\v40_expanded_adjacency_v2_compute_minimized\matched_early_seed0\weights\best.pt` |
| reliability | 6593293 | 6593293 | 105392393627 | 52696196813.5 | 40.6794 | 39.0301 | 49.9728 | 24.5825 | 236.3974609375 | `runs\v40_expanded_adjacency_v2_compute_minimized\reliability_p015_seed0\weights\best.pt` |
| ra_static_equal | 6592458 | 6592458 | 105392391992 | 52696195996.0 | 39.6842 | 38.7484 | 48.2705 | 25.1990 | 229.626953125 | `random initialization` |
| ra_stems_project | 6593242 | 6593242 | 106008430392 | 53004215196.0 | 38.6505 | 37.7872 | 43.8376 | 25.8729 | 229.2392578125 | `random initialization` |

## Hardware

- platform: `Windows-10-10.0.26200-SP0`
- pytorch: `2.5.1`
- cuda: `12.4`
- device: `cuda`
- gpu: `NVIDIA GeForce RTX 3090`
