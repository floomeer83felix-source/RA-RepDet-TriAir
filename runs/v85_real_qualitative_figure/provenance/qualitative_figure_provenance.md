# V85 Qualitative Figure Provenance

Generated: 2026-08-14T14:42:09+08:00

- Branch: `research/ra-repdet-triair`; generation commit: `36836ed23cee898698f2416d0f79d5e0c94f8a6f`.
- Validation manifest: `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt`; SHA256 `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`; 2,213 rows.
- Selection uses the frozen, model-independent protocol in `selection/selection_protocol.md`.
- Scene A: `frame_00846`, component `v40c_00410`, GT boxes 4, RGB mean 0.485813.
- Scene B: `nframe_01125`, component `v40c_02482`, GT boxes 3, RGB mean 0.022828.
- Scene C: `nframe_07517`, component `v40c_04592`, GT boxes 5, RGB mean 0.113348.

## Checkpoints

- matched_early: `E:\RepViT-main\runs\v40_expanded_adjacency_v2_compute_minimized\matched_early_seed0\weights\best.pt`, SHA256 `23331a6e668634f5f1ca1c7dfaddd23e9ee5445c0558e325621e8f454a0b1602`, seed `0`.
- dynamic_gate: `E:\RepViT-main\runs\v46_coco_ablation\local_training\ra_no_moddrop_seed0\weights\best.pt`, SHA256 `7c2817ff29414fcd91a9330c3f34b60dddfb505100f67810291f2e7ab09a1e5c`, seed `0`.

## Inference And Display

- Preprocessing: `DetectionTriAirDataset`, five stored channels divided by 255, torchvision fixed-size 640 x 640 transform.
- One global display threshold `0.25`, NMS IoU `0.6`, maximum `100` detections.
- Thermal transform: shared min-max scaling over the three selected stored channel-3 arrays, grayscale.
- Event transform: shared min-max scaling over the three selected stored channel-4 arrays, grayscale; this is the stored event representation, not raw events.
- Bounding boxes and scores are direct frozen-checkpoint outputs. They were not moved, resized, added, deleted, or relabeled manually.
- No AI-generated, synthetic, reconstructed, or invented sensor imagery, prediction, box, score, or annotation is used.
- The historical 837-image partition was not opened, rendered, scored, or used for selection.
- Generation command: `C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/tools/build_v85_real_qualitative_figure.py --data "D:\download\triair" --device cuda`.
