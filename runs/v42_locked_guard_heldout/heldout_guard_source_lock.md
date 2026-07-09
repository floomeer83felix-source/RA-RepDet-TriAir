# V42 Locked Held-out Guard Source Lock

Generated: 2026-07-09T15:05:41

## Scope

This record freezes the sources used for the V42 held-out guard evaluation. No training, checkpoint selection, hyperparameter tuning, split modification, robustness run, profiling run, manuscript edit, or external-data task was performed.

## Held-out guard source

- Source manifest: `runs\component_disjoint_v40\guard.txt`
- Rows: 837
- Raw file SHA256: `0cf3270c0a73d03caf8d698bb4e9ddb0adba46e688c52d8589f57ea12488881f`
- Normalized LF SHA256: `9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e`
- Split-manifest declared guard SHA256: `9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e`
- Components: 45
- Guard distance: 16
- Inventory count: 10489
- Deterministic rerun consistency: True

## Non-source archival guard note

- Not used: `reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_guard_unchanged_archival.txt`
- Rows: 837
- Raw file SHA256: `25a57cea733a218ce2bbd37b22acdf76722cdcc3856861020017340357b338a8`
- Normalized LF SHA256: `8a86d01cf27b60a3ec6d8f4cd153e88bc1bab1f5aff1059bbe3ea675300c50ae`
- Reason: this file has different content from the V42 source manifest; V42 uses the guard file matching `runs/component_disjoint_v40/split_manifest.json`.

## Evaluator

- Evaluator: `rarepdet/eval_map.py` `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715`
- Metrics: `rarepdet/metrics.py` `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081`
- Branch: `research/ra-repdet-triair`
- Commit at evaluation/reporting: `56a10e9a91f9b5e4e17358e1ea999de711013d44`

## Fixed checkpoints

| Run | Model | Seed | Checkpoint SHA256 | Source |
| --- | --- | ---: | --- | --- |
| matched_early_seed0 | early | 0 | `23331a6e668634f5f1ca1c7dfaddd23e9ee5445c0558e325621e8f454a0b1602` | V40 compute-minimized seed0/2 run set |
| matched_early_seed1 | early | 1 | `60a338ed887c15d94d3f274df39684c1dc6de68f9f29ba13f9f9cb4d6fbcd804` | V41 fresh paired seed1 run set |
| matched_early_seed2 | early | 2 | `b36b4965931da68b77a6be82e85e47b34f952445d64b941337f56a722f62737e` | V40 compute-minimized seed0/2 run set |
| reliability_p015_seed0 | reliability | 0 | `4284aaa188cb7f065a01b6cf32b78265ab937da0de2d3423d4594d2102787436` | V40 compute-minimized seed0/2 run set |
| reliability_p015_seed1 | reliability | 1 | `a59366dd0687754577d23d3e21358127199345d4ebf3a55a06472b933b57813d` | V41 fresh paired seed1 run set |
| reliability_p015_seed2 | reliability | 2 | `27affa96df1b3baad3df6f0a591e0599c1f5c0f77f91fad9fdaa408e549f1415` | V40 compute-minimized seed0/2 run set |

## Fixed evaluation settings

- `img_size=640`, `device=cuda`, `batch_size=4`, `num_workers=0`.
- `detector_score_thr=0.001`, `metric_score_thr=0.50`, `nms_thresh=0.6`, `detections_per_img=100`.
