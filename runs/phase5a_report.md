# Phase 5A Report

Generated: 2026-06-27T01:37:03

## Clean-Split Main Results

The table below is copied from Phase 4B controlled-seed clean-split results. R4 is the selected main variant.

| Variant | Seed | Dropout Ratio | P@0.50 | R@0.50 | F1@0.50 | AP50 | AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R0 Early Fusion | 0 | NA | 0.890591 | 0.896172 | 0.893373 | 0.938560 | 0.827560 | NA | NA | NA |
| R0 Early Fusion | 2 | NA | 0.902247 | 0.891091 | 0.896634 | 0.937711 | 0.831114 | NA | NA | NA |
| R1 Reliability p=0.00 | 0 | 0.00 | 0.890553 | 0.916497 | 0.903339 | 0.952112 | 0.889847 | 0.673004 | 0.328742 | 0.425560 |
| R1 Reliability p=0.00 | 2 | 0.00 | 0.920263 | 0.899221 | 0.909620 | 0.954378 | 0.893068 | 0.752975 | 0.332811 | 0.711880 |
| R2 Reliability p=0.15 | 0 | 0.15 | 0.906797 | 0.912940 | 0.909858 | 0.961573 | 0.899166 | 0.911342 | 0.682321 | 0.961223 |
| R2 Reliability p=0.15 | 2 | 0.15 | 0.916368 | 0.909383 | 0.912862 | 0.957739 | 0.870351 | 0.904481 | 0.658199 | 0.955474 |
| R4 Reliability p=0.20 [MAIN] | 0 | 0.20 | 0.938850 | 0.920562 | 0.929616 | 0.965012 | 0.895019 | 0.923708 | 0.729869 | 0.963677 |
| R4 Reliability p=0.20 [MAIN] | 2 | 0.20 | 0.906763 | 0.917514 | 0.912107 | 0.959977 | 0.887513 | 0.908394 | 0.706685 | 0.959476 |

## YOLO11n RGB-Only External Baseline

| Method | Seed | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| YOLO11n RGB-only | 0 | 0.913918 | 0.793022 | 0.849188 | 0.886374 | 0.629228 | 5904 | 5123 | 0.808770 |
| YOLO11n RGB-only | 2 | 0.914027 | 0.786924 | 0.845727 | 0.885401 | 0.636794 | 5904 | 5083 | 0.782716 |

### YOLO11n Mean/Range

| Metric | Mean | Min | Max | Range |
| --- | --- | --- | --- | --- |
| Precision | 0.913973 | 0.913918 | 0.914027 | 0.000109 |
| Recall | 0.789973 | 0.786924 | 0.793022 | 0.006098 |
| F1 | 0.847457 | 0.845727 | 0.849188 | 0.003461 |
| AP50 | 0.885887 | 0.885401 | 0.886374 | 0.000973 |
| AP75 | 0.633011 | 0.629228 | 0.636794 | 0.007566 |
| Predictions | 5103.000000 | 5083.000000 | 5123.000000 | 40.000000 |
| Mean Confidence | 0.795743 | 0.782716 | 0.808770 | 0.026054 |

## Efficiency

| Model | Path | Params | FPS mean | Latency ms/img mean | CUDA Memory MB mean | Note |
| --- | --- | --- | --- | --- | --- | --- |
| R0 Early Fusion | raw_forward | 6591609 | 102.762853 | 9.747951 | 115.153333 | seed0 checkpoint |
| R0 Early Fusion | detector_inference | 6591609 | 48.065821 | 20.818388 | 122.680000 | seed0 checkpoint |
| R4 Reliability p=0.20 | raw_forward | 6593293 | 97.717654 | 10.238004 | 228.940000 | seed0 checkpoint; dropout is training-only |
| R4 Reliability p=0.20 | detector_inference | 6593293 | 50.436489 | 19.829330 | 236.756667 | seed0 checkpoint; dropout is training-only |

## Convergence Audit

| Variant | Seed | Best Epoch | Best AP50 | AP50 Epoch 40 | AP50 Epoch 45 | AP50 Epoch 50 | Delta AP50 40->50 | Best In Final Five | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R0 Early Fusion | 0 | 5 | 0.938600 | 0.914500 | 0.917300 | 0.891700 | -0.022800 | false | CLEARLY_PLATEAUED |
| R0 Early Fusion | 2 | 7 | 0.937700 | 0.875500 | 0.893100 | 0.857000 | -0.018500 | false | CLEARLY_PLATEAUED |
| R1 Reliability p=0.00 | 0 | 11 | 0.952100 | 0.907200 | 0.920800 | 0.919500 | 0.012300 | false | NEAR_PLATEAU |
| R1 Reliability p=0.00 | 2 | 6 | 0.954400 | 0.939900 | 0.910100 | 0.898700 | -0.041200 | false | CLEARLY_PLATEAUED |
| R2 Reliability p=0.15 | 0 | 7 | 0.961500 | 0.935100 | 0.936400 | 0.928000 | -0.007100 | false | CLEARLY_PLATEAUED |
| R2 Reliability p=0.15 | 2 | 6 | 0.957700 | 0.931400 | 0.933100 | 0.917000 | -0.014400 | false | CLEARLY_PLATEAUED |
| R4 Reliability p=0.20 | 0 | 10 | 0.965000 | 0.947900 | 0.942300 | 0.936000 | -0.011900 | false | CLEARLY_PLATEAUED |
| R4 Reliability p=0.20 | 2 | 7 | 0.960000 | 0.936000 | 0.934600 | 0.938900 | 0.002900 | false | CLEARLY_PLATEAUED |

Convergence status summary: CLEARLY_PLATEAUED=7, NEAR_PLATEAU=1.

## Reliability-Weight Audit

| Seed | Mode | alpha_rgb_mean | alpha_thermal_mean | alpha_event_mean | alpha_sum_mean | finite_values |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | full | 0.430324 | 0.350048 | 0.219628 | 1.000000 | true |
| 0 | no_rgb | 0.235099 | 0.390569 | 0.374332 | 1.000000 | true |
| 0 | no_thermal | 0.708866 | 0.142052 | 0.149082 | 1.000000 | true |
| 0 | no_event | 0.443547 | 0.338973 | 0.217480 | 1.000000 | true |
| 2 | full | 0.459054 | 0.350642 | 0.190304 | 1.000000 | true |
| 2 | no_rgb | 0.240884 | 0.408295 | 0.350820 | 1.000000 | true |
| 2 | no_thermal | 0.761068 | 0.131866 | 0.107066 | 1.000000 | true |
| 2 | no_event | 0.465362 | 0.333710 | 0.200928 | 1.000000 | true |

Interpretation: these values describe implemented gating behavior under synthetic modality removal; they do not establish causal physical modality importance.

## Qualitative Manifest

- Rows: 20
- Category counts: R4 corrects R0 miss/localization failure: 5; R4 failure/hard case: 5; R4 missing-modality illustrative case: 5; Shared successful detection: 5
- Cases are illustrative only; local panels are not committed.

## Publication-Safe Interpretation

YOLO11n is reported strictly as a standard lightweight RGB-only external detector under the same clean split. It answers how the proposed full tri-modal system compares with a common RGB-only detector, but it does not isolate architecture-only benefit because the input modalities differ.
R0 versus R1/R4 remains the relevant architecture/fusion ablation within the same RepViT-FCOS detection family and tri-modal input setting.

## Output Checklist

| Section | Item | Status | Value | Notes |
| --- | --- | --- | --- | --- |
| Required Output | Phase 4B report | present | E:\RepViT-main\runs\phase4b_report.md |  |
| Required Output | Seed replication table | present | E:\RepViT-main\runs\clean_block64g16_seed_replication.csv |  |
| Required Output | Convergence audit | present | E:\RepViT-main\runs\clean_block64g16_convergence.csv |  |
| Required Output | Efficiency profile | present | E:\RepViT-main\runs\clean_efficiency_profile.csv |  |
| Required Output | R4 reliability audit | present | E:\RepViT-main\runs\r4_reliability_weight_audit.csv |  |
| Required Output | Qualitative manifest | present | E:\RepViT-main\runs\clean_qualitative_manifest.csv |  |
| Required Output | YOLO protocol | present | E:\RepViT-main\runs\yolo11n_rgb_baseline_protocol.md |  |
| Required Output | YOLO seed0 eval | present | E:\RepViT-main\runs\Y11n_rgb_seed0_block64g16_e50\eval_project\eval_results.csv |  |
| Required Output | YOLO seed2 eval | present | E:\RepViT-main\runs\Y11n_rgb_seed2_block64g16_e50\eval_project\eval_results.csv |  |
| Protocol | Current blocker | none | NA | Old resolved blocker files do not block Phase 5A. |
| Clean split main variant | R4 Full AP50 mean | complete | 0.962495 | R4 is marked as main variant by Phase 4B. |
| YOLO11n RGB-only | Seed 0 | complete | AP50=0.886374 AP75=0.629228 F1=0.849188 | External RGB-only baseline; not an architecture-only ablation. |
| YOLO11n RGB-only | Seed 2 | complete | AP50=0.885401 AP75=0.636794 F1=0.845727 | External RGB-only baseline; not an architecture-only ablation. |
| Convergence | R-run audit | complete | CLEARLY_PLATEAUED=7, NEAR_PLATEAU=1 | Descriptive only; no retraining triggered. |
| Efficiency | Clean profile rows | complete | 4 | Current-code profile, batch 1, 100 warmup, 300 iters, 3 repeats. |
| Reliability audit | R4 alpha rows | complete | 8 | Synthetic modality removal gating behavior only. |
| Qualitative | Manifest rows | complete | 20 | R4 corrects R0 miss/localization failure: 5; R4 failure/hard case: 5; R4 missing-modality illustrative case: 5; Shared successful detection: 5 |
| Decision | Phase 5A gate | READY FOR MANUSCRIPT DRAFTING | READY FOR MANUSCRIPT DRAFTING |  |

## Decision

READY FOR MANUSCRIPT DRAFTING