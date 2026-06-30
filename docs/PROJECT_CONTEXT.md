# Project Context

Repository: `floomeer83felix-source/RA-RepDet-TriAir`

Local workspace: `E:\RepViT-main`

Remote branch: `research/ra-repdet-triair`

Dataset root: `D:\download\triair`

This project studies RepViT-based multimodal UAV vehicle detection on TriAir. The current experimental line compares:

- E0: Early Fusion RepViT-FCOS.
- E1: Reliability Fusion RepViT-FCOS.
- E2: Reliability Fusion RepViT-FCOS with modality dropout 0.15.

TriAir uses 5-channel `.npy` samples in RGB, thermal, and event order. Missing label txt files are treated as empty-target images. The detection label class `0` is shifted to torchvision label `1`, with background remaining `0`.

Heavy artifacts must stay local: datasets, `.npy`, weights, checkpoints, prediction images, and large visualizations are not part of the GitHub handoff.
