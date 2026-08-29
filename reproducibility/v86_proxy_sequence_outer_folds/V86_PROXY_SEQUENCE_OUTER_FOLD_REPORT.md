# V86 Proxy-Sequence Outer-Fold Report

Status: **PASS**

The five manifests are held-out outer folds. For outer fold `k`, its training
complement is the union of the other four manifests.

## Frozen proxy-group rule

- Same-family consecutive numeric IDs with gap <= 16 are joined transitively.
- Exact decoded-RGB SHA256 identities are joined.
- Frozen human-adjudicated adjacent-or-near-identical edges are joined.
- pHash/dHash threshold matches remain candidates, not confirmed near-duplicate edges.
- No image pixels, annotations, predictions, checkpoints, or model metrics are used.

## Fold statistics

| Fold | Groups | Images | GT boxes | Zero-target | Boxes/image | Largest group | frame | nframe |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 4077 | 11157 | 738 | 2.736571 | 4077 | 4077 | 0 |
| 1 | 7 | 1603 | 7652 | 1 | 4.773550 | 1580 | 0 | 1603 |
| 2 | 13 | 1603 | 3409 | 0 | 2.126638 | 686 | 0 | 1603 |
| 3 | 13 | 1603 | 3258 | 0 | 2.032439 | 625 | 0 | 1603 |
| 4 | 11 | 1603 | 5158 | 0 | 3.217717 | 564 | 0 | 1603 |

## Pairwise isolation audit

| Fold A | Fold B | Shared images | Shared groups | Known near-duplicate edges | Known adjacency edges |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 0 | 0 | 0 | 0 |
| 0 | 2 | 0 | 0 | 0 | 0 |
| 0 | 3 | 0 | 0 | 0 | 0 |
| 0 | 4 | 0 | 0 | 0 | 0 |
| 1 | 2 | 0 | 0 | 0 | 0 |
| 1 | 3 | 0 | 0 | 0 | 0 |
| 1 | 4 | 0 | 0 | 0 | 0 |
| 2 | 3 | 0 | 0 | 0 | 0 |
| 2 | 4 | 0 | 0 | 0 | 0 |
| 3 | 4 | 0 | 0 | 0 | 0 |

## Global checks

- Images covered exactly once: 10,489
- GT boxes: 30,634
- Zero-target images: 739
- Proxy groups: 45
- Known exact-RGB near-duplicate edges: 473
- Known adjacency edges: 10721
- All 10 fold pairs pass all four zero-crossing requirements.

The filename numeric ID is used only as a proxy grouping key. It is not claimed
to be verified sequence, flight, timestamp, or acquisition-session metadata.
