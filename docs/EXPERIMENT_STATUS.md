# Experiment Status

Generated: 2026-06-30

## Manuscript Publication Snapshot

- Manuscript protocol: `block64_guard16_seed0`
- Train / validation / guard: `7439 / 2213 / 837`
- Headline variant: `R4 Reliability p=0.20`
- Report scope: frozen validation partition only
- Clean protocol: `runs/clean_block64g16_protocol.md`
- Controlled-seed report: `runs/phase4b_report.md`
- Public snapshot evidence commit: `700e84556c31e044d100fa9a5f6243720f023d6f`

The only manuscript headline result is the clean blocked-split R4 result on the frozen validation partition. The earlier E0-E6 runs are retained below as historical/exploratory diagnostics and must not be reported as headline manuscript results.

## Headline Clean-Split Result

### Controlled-Seed R4 Summary

| Variant | Seeds | Dropout Ratio | Mean F1@0.50 | Mean AP50 | Mean AP75 | Mean w/o RGB AP50 | Mean w/o Thermal AP50 | Mean w/o Event AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R4 Reliability p=0.20 | 0, 2 | 0.20 | 0.920861 | 0.962495 | 0.891266 | 0.916051 | 0.718277 | 0.961577 |

### R4 Per-Seed Rows

| Variant | Seed | Precision | Recall | F1@0.50 | AP50 | AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R4 Reliability p=0.20 | 0 | 0.938850 | 0.920562 | 0.929616 | 0.965012 | 0.895019 | 0.923708 | 0.729869 | 0.963677 |
| R4 Reliability p=0.20 | 2 | 0.906763 | 0.917514 | 0.912107 | 0.959977 | 0.887513 | 0.908394 | 0.706685 | 0.959476 |

## Clean Split Protocol

| Split | Count | SHA256 |
| --- | --- | --- |
| train | 7439 | `c4d94e5b376e862c3875314d39d79149988c479f12e97a6fcbeea72d3dfa85e5` |
| validation | 2213 | `a48aff2ee29d041bd07b746947028191475a59f0df6b7b64d4882cd610746dc4` |
| guard | 837 | `25a57cea733a218ce2bbd37b22acdf76722cdcc3856861020017340357b338a8` |

Integrity checks reported zero exact RGB train/validation matches and zero same-family guard-band violations for `block64_guard16_seed0`. Guard samples are excluded from both training and validation.

## Matched Clean-Split Comparisons

The R0/R1/R2/R4 rows below are clean blocked-split controlled-seed evidence. R4 is the selected manuscript headline variant.

| Variant | Seed | Dropout Ratio | P@0.50 | R@0.50 | F1@0.50 | AP50 | AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R0 Early Fusion | 0 | NA | 0.890591 | 0.896172 | 0.893373 | 0.938560 | 0.827560 | NA | NA | NA |
| R0 Early Fusion | 2 | NA | 0.902247 | 0.891091 | 0.896634 | 0.937711 | 0.831114 | NA | NA | NA |
| R1 Reliability p=0.00 | 0 | 0.00 | 0.890553 | 0.916497 | 0.903339 | 0.952112 | 0.889847 | 0.673004 | 0.328742 | 0.425560 |
| R1 Reliability p=0.00 | 2 | 0.00 | 0.920263 | 0.899221 | 0.909620 | 0.954378 | 0.893068 | 0.752975 | 0.332811 | 0.711880 |
| R2 Reliability p=0.15 | 0 | 0.15 | 0.906797 | 0.912940 | 0.909858 | 0.961573 | 0.899166 | 0.911342 | 0.682321 | 0.961223 |
| R2 Reliability p=0.15 | 2 | 0.15 | 0.916368 | 0.909383 | 0.912862 | 0.957739 | 0.870351 | 0.904481 | 0.658199 | 0.955474 |
| R4 Reliability p=0.20 | 0 | 0.20 | 0.938850 | 0.920562 | 0.929616 | 0.965012 | 0.895019 | 0.923708 | 0.729869 | 0.963677 |
| R4 Reliability p=0.20 | 2 | 0.20 | 0.906763 | 0.917514 | 0.912107 | 0.959977 | 0.887513 | 0.908394 | 0.706685 | 0.959476 |

## Historical Experiments

These E0-E6 results are historical/exploratory. They were useful for development, threshold sweeps, and robustness probes, but they are not manuscript headline results because the later clean blocked split replaced the earlier random-split evidence.

### Historical E0-E6 Full-Modality Rows

| Experiment | Method | Precision | Recall | AP50 | AP75 | GT boxes | Predictions | Mean Confidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0 | Early Fusion | 0.028842 | 0.996213 | 0.976620 | 0.928824 | 6074 | 209800 | 0.135346 | historical/exploratory |
| E1 | Reliability Fusion | 0.028866 | 0.997037 | 0.979317 | 0.947634 | 6074 | 209800 | 0.125795 | historical/exploratory |
| E2 | Reliability + Dropout 0.15 | 0.028837 | 0.996049 | 0.979990 | 0.950906 | 6074 | 209800 | 0.131865 | historical/exploratory |
| E3 | Reliability + Dropout 0.10 | 0.949248 | 0.945341 | 0.977738 | 0.945218 | 6074 | 6049 | 0.774961 | historical/exploratory |
| E4 | Reliability + Dropout 0.20 | 0.946437 | 0.951268 | 0.978692 | 0.948514 | 6074 | 6105 | 0.799311 | historical/exploratory |
| E5 | ACRF + Dropout 0.15 | 0.938290 | 0.953737 | 0.978066 | 0.946602 | 6074 | 6174 | 0.779350 | historical/exploratory |
| E6 | MSCD + Dropout 0.15 | 0.937297 | 0.949951 | 0.974990 | 0.945138 | 6074 | 6156 | 0.801200 | historical/exploratory |

### Historical Missing-Modality AP50

| Method | Full | w/o RGB | w/o Thermal | w/o Event | RGB only | Thermal only | Event only | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.976620 | 0.739537 | 0.410636 | 0.974633 | 0.398050 | 0.700867 | 0.013115 | historical/exploratory |
| E1 Reliability Fusion | 0.979317 | 0.688697 | 0.370994 | 0.477850 | 0.477494 | 0.000240 | 0.004093 | historical/exploratory |
| E2 Reliability + Dropout 0.15 | 0.979990 | 0.948710 | 0.811566 | 0.978972 | 0.802234 | 0.863495 | 0.304352 | historical/exploratory |

## Efficiency Evidence

Clean-split profiling used batch size 1, 640-pixel inputs, 100 warm-up iterations, 300 timed iterations, and three repeats.

| Model | Path | Params | FPS mean | Latency ms/img mean | CUDA Memory MB mean | Note |
| --- | --- | --- | --- | --- | --- | --- |
| R0 Early Fusion | raw_forward | 6591609 | 102.762853 | 9.747951 | 115.153333 | seed0 checkpoint |
| R0 Early Fusion | detector_inference | 6591609 | 48.065821 | 20.818388 | 122.680000 | seed0 checkpoint |
| R4 Reliability p=0.20 | raw_forward | 6593293 | 97.717654 | 10.238004 | 228.940000 | seed0 checkpoint; dropout is training-only |
| R4 Reliability p=0.20 | detector_inference | 6593293 | 50.436489 | 19.829330 | 236.756667 | seed0 checkpoint; dropout is training-only |

## Known Metric Caveats

- The report scope is the frozen validation partition only; no independent hidden test set is claimed.
- The former E0-E6 rows are historical/exploratory and must not be used as manuscript headline results.
- The clean split uses `block64_guard16_seed0`; do not mix clean-split R-runs with former random-split E-runs.
- Controlled clean-split evidence uses two seeds, which is not a statistical-significance test.
- Missing-modality tests use synthetic channel removal and do not prove real sensor-failure deployment behavior.
- AP50/AP75 are computed with the project-local AP implementation and do not depend on pycocotools.
- Raw TriAir data are not redistributed in the public repository.

## Important Research Decisions

- Missing txt labels are treated as empty-target images.
- TriAir class 0 is shifted to torchvision label 1; background remains label 0.
- The former random split had RGB-content leakage risk and is superseded by `block64_guard16_seed0`.
- R4 Reliability p=0.20 is the manuscript headline variant because it leads clean-split AP50 at both seeds and has the strongest overall robustness profile among the controlled R variants.
- E0-E6 remain useful development history but are not the current publication baseline.

## Files Or Scripts Under Review

- `README.md`
- `docs/REPRODUCIBILITY.md`
- `docs/DATA_PROVENANCE.md`
- `runs/clean_block64g16_protocol.md`
- `runs/phase4b_report.md`
- `runs/clean_block64g16_seed_replication.csv`
- `rarepdet/train_early_fusion.py`
- `rarepdet/eval_map.py`
- `rarepdet/tools/eval_missing_modality.py`
- `rarepdet/tools/profile_model.py`
