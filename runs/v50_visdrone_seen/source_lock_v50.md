# V50 Source Lock

- Starting commit: `0dafe892d9ea0559a47d8150d011e2eeb277a17b`
- Branch: `research/ra-repdet-triair`
- Dataset: `D:\datasets\visdrone_seen`
- Source mirror: `D:\datasets\visdrone`
- Generator SHA256: `a59532c1a6630821c7e40a3bd73b298e91e526daea9167e6b85bbc06de908bfb`
- Mapping SHA256: `9531834f4620ee14e2d9932f34a75695697c29929cb1fa0e666e7e7e2d16a053`
- Split-manifest SHA256: `54b0228a5657ef7e623e340c5d30ec405a6ecf8f339eaece1eafc3f275a740a2`
- Adapter: RGB scaled to `[0,1]`, then append thermal/event channels fixed at `0.0` for frozen-checkpoint stress evaluation.
- Frozen detector settings: score `0.001`, NMS `0.6`, max detections `100`.
- RGB selection: highest devval canonical COCO AP50; first epoch wins exact ties.
- Test rule: no test access before adapter, mapping, evaluator, thresholds, and all three RGB checkpoints are frozen.

## Frozen Checkpoints

- `matched_early_seed0`: `runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt` `23331a6e668634f5f1ca1c7dfaddd23e9ee5445c0558e325621e8f454a0b1602`
- `matched_early_seed1`: `runs/v41_q1_upgrade/seed1/matched_early_seed1/weights/best.pt` `60a338ed887c15d94d3f274df39684c1dc6de68f9f29ba13f9f9cb4d6fbcd804`
- `matched_early_seed2`: `runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed2/weights/best.pt` `b36b4965931da68b77a6be82e85e47b34f952445d64b941337f56a722f62737e`
- `reliability_p015_seed0`: `runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt` `4284aaa188cb7f065a01b6cf32b78265ab937da0de2d3423d4594d2102787436`
- `reliability_p015_seed1`: `runs/v41_q1_upgrade/seed1/reliability_p015_seed1/weights/best.pt` `a59366dd0687754577d23d3e21358127199345d4ebf3a55a06472b933b57813d`
- `reliability_p015_seed2`: `runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed2/weights/best.pt` `27affa96df1b3baad3df6f0a591e0599c1f5c0f77f91fad9fdaa408e549f1415`

## Boundary

The data are an audited local RGB-only VisDrone-SEEN derivative. Results can support only RGB-only domain-shift and zero-filled missing-modality stress claims. They cannot validate thermal/event generalization, calibrated reliability, a physical sensor fault, or a sequence-disjoint independent test.
