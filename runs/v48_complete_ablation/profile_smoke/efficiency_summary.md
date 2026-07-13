# V48 Efficiency Summary

Generated: 2026-07-10T23:00:36+08:00

## Procedure

- Full FCOS detector inference was measured without dataloader or file-I/O time.
- Input: `1x5x64x64`, `float32`.
- Warm-up iterations: `0`; measured iterations: `1`.
- Each measured iteration is bracketed by CUDA synchronization when CUDA is used; latency is host wall time for the complete detector call.
- Operator FLOPs are summed from `torch.profiler` events for one full-detector inference. Derived MACs equal FLOPs/2 and exclude operations with no profiler FLOP estimate.

## Results

| Model | Total params | Trainable params | Operator FLOPs | Derived MACs | Mean ms | Median ms | P95 ms | FPS | Peak allocated MiB | Checkpoint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ra_static_equal | 6592458 | 6592458 | 1054337588 | 527168794.0 | 96.5674 | 96.5674 | 96.5674 | 10.3555 | NA | `random initialization` |

## Hardware

- platform: `Windows-10-10.0.26200-SP0`
- pytorch: `2.5.1`
- cuda: `12.4`
- device: `cpu`
- gpu: `CPU`
