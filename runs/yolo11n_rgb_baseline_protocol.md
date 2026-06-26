# YOLO11n RGB Baseline Protocol

Generated: 2026-06-26T23:45:32

## Environment

- Python: `3.9.21 (main, Dec 11 2024, 16:35:24) [MSC v.1929 64 bit (AMD64)]`
- Platform: `Windows-10-10.0.26200-SP0`
- Ultralytics: `8.3.28`
- PyTorch: `2.5.1`
- CUDA available: `true`
- CUDA version: `12.4`
- GPU: `NVIDIA GeForce RTX 3090`

## Official Checkpoint

- Requested model: `yolo11n.pt`
- Resolved checkpoint/source: `yolo11n.pt`
- No substitute detector is allowed for this baseline.

## Cache

- YAML: `E:\RepViT-main\runs\local_yolo11n_rgb_cache\triair_yolo11n_rgb.yaml`
- Train images exported: 7439
- Val images exported: 2213
- RGB-content train/val overlap after export: 0
- Guard samples are excluded from train and val exports.
- RGB source channels: `[0:3]` from TriAir `rgbte` arrays.
- Aspect ratio is preserved by writing each RGB frame at its native HxW size; YOLO letterboxes internally at `imgsz=640`.

## RGB Conversion Notes

- frame_00000.npy: source dtype=uint8, min=0.000000, max=255.000000; kept uint8 values
- frame_00001.npy: source dtype=uint8, min=0.000000, max=255.000000; kept uint8 values
- frame_00002.npy: source dtype=uint8, min=0.000000, max=255.000000; kept uint8 values
- frame_00003.npy: source dtype=uint8, min=0.000000, max=255.000000; kept uint8 values
- frame_00004.npy: source dtype=uint8, min=1.000000, max=255.000000; kept uint8 values
- frame_00192.npy: source dtype=uint8, min=0.000000, max=255.000000; kept uint8 values
- frame_00193.npy: source dtype=uint8, min=0.000000, max=255.000000; kept uint8 values
- frame_00194.npy: source dtype=uint8, min=2.000000, max=255.000000; kept uint8 values
- frame_00195.npy: source dtype=uint8, min=0.000000, max=255.000000; kept uint8 values
- frame_00196.npy: source dtype=uint8, min=0.000000, max=255.000000; kept uint8 values

## Exact Training Commands

```powershell
yolo detect train model=yolo11n.pt data=E:\RepViT-main\runs\local_yolo11n_rgb_cache\triair_yolo11n_rgb.yaml epochs=50 imgsz=640 seed=0 deterministic=True project=runs name=Y11n_rgb_seed0_block64g16_e50 exist_ok=False device=0
yolo detect train model=yolo11n.pt data=E:\RepViT-main\runs\local_yolo11n_rgb_cache\triair_yolo11n_rgb.yaml epochs=50 imgsz=640 seed=2 deterministic=True project=runs name=Y11n_rgb_seed2_block64g16_e50 exist_ok=False device=0
```
