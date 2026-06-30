# Data Provenance

This repository does not redistribute TriAir raw data, label archives, `.npy` arrays, or downloaded dataset packages. The local experimental copy was reported by the author as downloaded from the official website, but the official citation, access URL, license, and redistribution terms must be filled from the provider's current documentation before manuscript submission or public release notes cite them.

## Author-Filled Required Fields

- [Official TriAir citation]: TODO
- [Dataset version]: TODO
- [Provider/official access URL]: TODO
- [License/access terms]: TODO
- [Redistribution status]: TODO
- [Sensor synchronization and alignment statement]: TODO
- [Event representation statement]: TODO

## Repository Handling

- Raw data are not included in this repository.
- Trained checkpoints and exported weights are not included in this repository.
- Rendered prediction panels and qualitative image outputs are not included in this repository.
- Split manifests and lightweight derived CSV/MD/TXT summaries are included for reproducibility auditing.

## Local Data Assumptions Used by Code

The dataset adapter expects local TriAir samples as five-channel `.npy` arrays with RGB, thermal, and event channels in the project-specific order used by `datasets/triair_dataset.py`. YOLO-format label text files are read when available. Missing or empty label files are treated as empty-target images.

Before publication, replace every TODO field above with provider-verified text. Do not infer license terms or redistribution rights from local possession of the data.
