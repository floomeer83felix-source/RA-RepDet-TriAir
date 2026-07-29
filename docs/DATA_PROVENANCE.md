# Data Provenance

Updated: 2026-07-29

## Provider archive identity

The local experimental copy at `D:\download\triair` was compared against the current provider `triair.zip` entry by entry.

- provider archive status: untagged provider archive;
- Google Drive file ID: `1w71v6n41yqjP7BCr9ni4JdcxMnQ2ocR0`;
- provider Last-Modified marker: `2025-11-21`;
- archive size: `3,551,150,083` bytes;
- compared entries: `20,240`;
- comparison keys: relative path, uncompressed size, CRC32;
- missing entries: `0`;
- extra entries: `0`;
- different entries: `0`;
- semantic version or release tag: none provided.

The complete identity comparison is an author-performed local audit. The upstream repository independently identifies the same Drive file but does not publish semantic version metadata.

## Dataset paper and current archive counts

The canonical provider paper is:

Craig Iaboni and Pramod Abichandani, *Tri-Modal Fusion Transformers for UAV-based Object Detection*, CVPR 2026, pp. 4373-4382.

The paper reports `10,489` frames and `24,223` annotated vehicles. The current provider archive contains:

- `10,489` five-channel `.npy` arrays;
- `9,751` YOLO `.txt` files;
- `30,634` valid single-class label lines;
- arrays of shape `(301, 391, 5)` and type `uint8`;
- RGB channels `0-2`, thermal channel `3`, event channel `4`.

The `6,411` difference between the paper's `24,223` vehicles and the current archive's `30,634` valid label lines is unresolved. These values must remain separately labelled. `30,634` must not be described as the official vehicle count reported by the paper.

## Conversion provenance

No project-side offline conversion from raw RGB, thermal, and event recordings to the TriAir arrays was found. The provider archive already contains the five-channel arrays and YOLO labels.

The project performs only runtime operations:

1. HWC to CHW;
2. `uint8` to floating point and division by 255;
3. normalized YOLO coordinates to absolute `xyxy` boxes;
4. raw class `0` to torchvision foreground class `1`.

Missing or empty label files are retained as empty-target images.

## Initial local split provenance

- `train.txt`: 8,391 images; author-recorded SHA256 `9f264792...35daad6`;
- `val.txt`: 2,098 images; author-recorded SHA256 `2052677d...3995d2`;
- generator: `tools/create_triair_split.py`;
- seed: `0`;
- ratio: `80:20` random assignment;
- provider status: not an official provider split;
- manuscript status: not used for final reported results.

The final manuscript results use the frozen component-disjoint V40 manifests instead.

## Code provenance

The provider-code mirror was checked against upstream commit `8f4e31ed64f1f2fe019d4706670fc4560c0b2e23`; content matched apart from line-ending normalization. The upstream repository documents the same Drive file ID, five-channel order, and normalized YOLO label format.

## License and redistribution

The upstream repository states an MIT license for code. No explicit license for the dataset archive was located. The repository therefore does not redistribute TriAir raw data, label archives, `.npy` arrays, transformed copies, or downloaded dataset packages.

Trained checkpoints, rendered prediction panels, and large derived media also remain excluded. Frozen manifests and compact non-data audit artifacts may be included for reproducibility.
