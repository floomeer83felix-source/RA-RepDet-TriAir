# Data and Split Boundary

The code expects five-channel `.npy` samples ordered as RGB, thermal, and event representation. Detection labels use class `0` in text files and are shifted to torchvision label `1`, with `0` reserved for background. Missing label files are treated as empty-target images.

The publication split is component-disjoint:

| Partition | Images | Manifest | SHA256 |
| --- | ---: | --- | --- |
| Train | 7,439 | [`splits/train.txt`](../splits/train.txt) | `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f` |
| Development-validation | 2,213 | [`splits/validation.txt`](../splits/validation.txt) | `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f` |

The development-validation partition participates in checkpoint retention. It is not an independent test set. A separate 837-image historical partition is not included in this public package.

Raw arrays, labels, archives, and transformed copies are excluded. Users must obtain TriAir through a provider-approved route. Dataset access, license, and redistribution rights are not granted by this code license.
