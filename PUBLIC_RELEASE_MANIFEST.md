# Public Release Manifest

This branch was rebuilt as a minimal public experiment release. It intentionally excludes large or restricted artifacts.

Included categories:

- RA-RepDet source code under `rarepdet/`.
- TriAir dataset adapter under `datasets/`.
- Lightweight utility scripts under `tools/`.
- Clean split manifests and lightweight result summaries under `runs/`.
- Manuscript table/figure source CSV and Markdown files under `manuscript/`.
- Reproducibility/design notes under `docs/`.

Excluded categories:

- Raw `.npy` / `.npz` data.
- Checkpoints and weights: `.pt`, `.pth`, `.ckpt`.
- Prediction/visualization images: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tif`, `.tiff`, `.pdf`, `.eps`.
- Large logs, local caches, rendered panels, and local environment files.
- Upstream RepViT/SAM/segmentation/detection code that is not needed for the RA-RepDet experiments.
