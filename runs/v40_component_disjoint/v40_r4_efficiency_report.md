# V40 R4 Efficiency Report

| Metric | Value |
|---|---:|
| Model | reliability |
| Image size | 640 |
| Batch size | 1 |
| Params | 6593293 |
| Trainable Params | 6593293 |
| GFLOPs | 105.981501 |
| GFLOPs Note | detector |
| FPS | 51.074976 |
| Latency ms/img | 19.579060 |
| CUDA max memory MB | 236.40 |

Measured with `rarepdet/tools/profile_model.py --model reliability --img-size 640 --device cuda --batch-size 1 --warmup 100 --iters 300`.
