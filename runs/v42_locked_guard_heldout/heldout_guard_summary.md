# V42 Locked Held-out Guard Evaluation Summary

Generated: 2026-07-09T15:05:41

## Evaluation source

- Guard manifest: `runs\component_disjoint_v40\guard.txt`
- Guard rows: 837 images
- Guard GT boxes: 1264
- Normalized guard SHA256: `9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e`
- Raw file SHA256 recorded by evaluator: `0cf3270c0a73d03caf8d698bb4e9ddb0adba46e688c52d8589f57ea12488881f`

## Per-run results

| Run | Precision | Recall | F1 | AP50 | AP75 | Predictions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| matched_early_seed0 | 0.938534 | 0.942247 | 0.940387 | 0.965299 | 0.923818 | 1269 |
| matched_early_seed1 | 0.878990 | 0.936709 | 0.906932 | 0.954007 | 0.894974 | 1347 |
| matched_early_seed2 | 0.937147 | 0.920095 | 0.928543 | 0.957160 | 0.883246 | 1241 |
| reliability_p015_seed0 | 0.937451 | 0.936709 | 0.937080 | 0.966926 | 0.929140 | 1263 |
| reliability_p015_seed1 | 0.894619 | 0.946994 | 0.920061 | 0.964380 | 0.912660 | 1338 |
| reliability_p015_seed2 | 0.932243 | 0.946994 | 0.939560 | 0.970845 | 0.866755 | 1284 |

## Group descriptive aggregates

| Model group | Metric | Mean | Sample SD | Min | Max | n |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| matched_early | precision | 0.918224 | 0.033984 | 0.878990 | 0.938534 | 3 |
| matched_early | recall | 0.933017 | 0.011528 | 0.920095 | 0.942247 | 3 |
| matched_early | f1 | 0.925287 | 0.016963 | 0.906932 | 0.940387 | 3 |
| matched_early | ap50 | 0.958822 | 0.005826 | 0.954007 | 0.965299 | 3 |
| matched_early | ap75 | 0.900679 | 0.020879 | 0.883246 | 0.923818 | 3 |
| reliability_p015 | precision | 0.921437 | 0.023371 | 0.894619 | 0.937451 | 3 |
| reliability_p015 | recall | 0.943565 | 0.005938 | 0.936709 | 0.946994 | 3 |
| reliability_p015 | f1 | 0.932234 | 0.010614 | 0.920061 | 0.939560 | 3 |
| reliability_p015 | ap50 | 0.967383 | 0.003257 | 0.964380 | 0.970845 | 3 |
| reliability_p015 | ap75 | 0.902852 | 0.032328 | 0.866755 | 0.929140 | 3 |

## Paired deltas

Reliability-aware p=0.15 minus matched early fusion, paired by seed.

| Seed | Precision | Recall | F1 | AP50 | AP75 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | -0.001084 | -0.005538 | -0.003307 | 0.001628 | 0.005322 |
| 1 | 0.015628 | 0.010285 | 0.013129 | 0.010372 | 0.017686 |
| 2 | -0.004904 | 0.026899 | 0.011018 | 0.013685 | -0.016491 |

| Metric | Mean delta | Sample SD | Min | Max | n seed pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| precision | 0.003213 | 0.010920 | -0.004904 | 0.015628 | 3 |
| recall | 0.010549 | 0.016220 | -0.005538 | 0.026899 | 3 |
| f1 | 0.006946 | 0.008943 | -0.003307 | 0.013129 | 3 |
| ap50 | 0.008562 | 0.006229 | 0.001628 | 0.013685 | 3 |
| ap75 | 0.002173 | 0.017305 | -0.016491 | 0.017686 | 3 |

## Interpretation

On this locked held-out guard manifest, reliability-aware p=0.15 improves the three-seed mean recall, F1, AP50, and AP75 relative to matched early fusion. The per-seed deltas remain mixed for F1 and AP75, including a seed0 F1 decrease and a seed2 AP75 decrease, so the result should be treated as descriptive guard evidence only and was not used for training or tuning.
