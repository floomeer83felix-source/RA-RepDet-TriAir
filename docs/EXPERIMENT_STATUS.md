# Experiment Status

Generated: 2026-07-04T09:36:38
Handoff source: `E:\RepViT-main\runs\handoff_latest.md`

## Current best model

- Best AP50: E2 Reliability + Dropout 0.15 (0.979990)
- Best AP75: E2 Reliability + Dropout 0.15 (0.950906)

## Latest completed experiments

| Experiment | Method | Precision | Recall | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0 | Early Fusion | 0.028842 | 0.996213 | 0.976620 | 0.928824 | 6074 | 209800 | 0.135346 |
| E1 | Reliability Fusion | 0.028866 | 0.997037 | 0.979317 | 0.947634 | 6074 | 209800 | 0.125795 |
| E2 | Reliability + Dropout 0.15 | 0.028837 | 0.996049 | 0.979990 | 0.950906 | 6074 | 209800 | 0.131865 |
| E3 | Reliability + Dropout 0.10 | 0.949248 | 0.945341 | 0.977738 | 0.945218 | 6074 | 6049 | 0.774961 |
| E4 | Reliability + Dropout 0.20 | 0.946437 | 0.951268 | 0.978692 | 0.948514 | 6074 | 6105 | 0.799311 |
| E5 | ACRF + Dropout 0.15 | 0.938290 | 0.953737 | 0.978066 | 0.946602 | 6074 | 6174 | 0.779350 |
| E6 | MSCD + Dropout 0.15 | 0.937297 | 0.949951 | 0.974990 | 0.945138 | 6074 | 6156 | 0.801200 |

### Best threshold by F1

| Method | Threshold | Precision | Recall | F1 | AP50 | AP75 | Predictions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.5 | 0.9291325957992624 | 0.9540665130062562 | 0.941434489480952 | 0.9766198396682739 | 0.9288238883018494 | 6237 |
| E1 Reliability Fusion | 0.5 | 0.9257206208425721 | 0.9622983207112282 | 0.9436551501453019 | 0.9793174862861633 | 0.9476337432861328 | 6314 |
| E2 Reliability + Dropout 0.15 | 0.5 | 0.9310565977232644 | 0.9560421468554494 | 0.943383965559256 | 0.9799898266792297 | 0.9509060382843018 | 6237 |

### Missing modality AP50

| Method | Full | w/o RGB | w/o Thermal | w/o Event | RGB only | Thermal only | Event only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.976620 | 0.739537 | 0.410636 | 0.974633 | 0.398050 | 0.700867 | 0.013115 |
| E1 Reliability Fusion | 0.979317 | 0.688697 | 0.370994 | 0.477850 | 0.477494 | 0.000240 | 0.004093 |
| E2 Reliability + Dropout 0.15 | 0.979990 | 0.948710 | 0.811566 | 0.978972 | 0.802234 | 0.863495 | 0.304352 |

### Missing modality AP75

| Method | Full | w/o RGB | w/o Thermal | w/o Event | RGB only | Thermal only | Event only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.928824 | 0.564886 | 0.333051 | 0.925954 | 0.312297 | 0.536687 | 0.001062 |
| E1 Reliability Fusion | 0.947634 | 0.600607 | 0.350580 | 0.345952 | 0.347069 | 0.000003 | 0.000245 |
| E2 Reliability + Dropout 0.15 | 0.950906 | 0.820473 | 0.552192 | 0.948703 | 0.542798 | 0.663646 | 0.171463 |

### Model profile

| Model | Params | Trainable Params | GFLOPs | FPS | Latency ms/img | CUDA Memory MB |
| --- | --- | --- | --- | --- | --- | --- |
| E0/Early Fusion | 6591609 | 6591609 | 105.207355 | 24.914556 | 40.137179 | 123.43 |
| E1/E2 Reliability Fusion | 6593293 | 6593293 | 105.981501 | 47.389574 | 21.101688 | 236.40 |

## Phase 2A outputs

### Paper main results at score threshold 0.50

| Method | Threshold | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.50 | 0.929133 | 0.954067 | 0.941434 | 0.976620 | 0.928824 | 6074 | 6237 | 0.769583 |
| E1 Reliability Fusion | 0.50 | 0.925721 | 0.962298 | 0.943655 | 0.979317 | 0.947634 | 6074 | 6314 | 0.794935 |
| E2 Reliability + Dropout 0.15 | 0.50 | 0.931057 | 0.956042 | 0.943384 | 0.979990 | 0.950906 | 6074 | 6237 | 0.788404 |

### Phase 2A profile summary

| Model | Path | Batch Size | Img Size | Warmup | Iters | Repeats | Params | FPS mean | Latency ms/img mean | CUDA Memory MB mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | raw_forward | 1 | 640 | 100 | 300 | 3 | 6591609 | 111.427245 | 8.977959 | 115.153333 |
| early | detector_inference | 1 | 640 | 100 | 300 | 3 | 6591609 | 55.488686 | 18.030040 | 122.680000 |
| reliability | raw_forward | 1 | 640 | 100 | 300 | 3 | 6593293 | 117.451207 | 8.515909 | 228.006667 |
| reliability | detector_inference | 1 | 640 | 100 | 300 | 3 | 6593293 | 55.884826 | 17.895982 | 235.820000 |

### Phase 2A brightness-proxy outputs

- Rows: 9
- Groups: RGB mean-intensity terciles, not day/night labels.

### Phase 2A alpha outputs

- Rows: 8
- Modes: full, no_rgb, no_thermal, no_event for E1 and E2.


## Current active task

- Task file: `docs/NEXT_TASK.md`
- Current Task: Phase 7A - Final SIVP Asset Readiness and Author Metadata Intake
- Goal: Prepare final SIVP figure/table readiness, author metadata intake, and compile-blocker tracking without retraining models or changing experimental evidence.
- Status: pending

## Phase 2B ACRF outputs

- Report: `runs/acrf_evidence_report.md`
- Smoke test: `runs/acrf_smoke_test.md`
- Evidence rows: 3
- E5 missing-modality rows: 7
- E5 alpha-mode rows: 4

### ACRF evidence summary

| Method | Params | Full AP50 | Full AP75 | P@0.50 | R@0.50 | F1@0.50 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 Reliability Fusion | 6593293 | 0.979317 | 0.947634 | 0.925721 | 0.962298 | 0.943655 | 0.688697 | 0.370994 | 0.477850 | 0.512514 |
| E2 Reliability + Dropout 0.15 | 6593293 | 0.979990 | 0.950906 | 0.931057 | 0.956042 | 0.943384 | 0.948710 | 0.811566 | 0.978972 | 0.913083 |
| E5 ACRF + Dropout 0.15 | 6593341 | 0.978066 | 0.946602 | 0.938290 | 0.953737 | 0.945950 | 0.944019 | 0.846657 | 0.978531 | 0.923069 |

## Phase 2C MSCD outputs

- Report: `runs/mscd_evidence_report.md`
- Phase 2C report: `runs/phase2c_report.md`
- Smoke test: `runs/mscd_smoke_test.md`
- Evidence rows: 4
- E6 missing-modality rows: 7

### MSCD evidence summary

| Method | Extra inference params | Full AP50 | Full AP75 | P@0.50 | R@0.50 | F1@0.50 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 Reliability Fusion | 0 | 0.979317 | 0.947634 | 0.925721 | 0.962298 | 0.943655 | 0.688697 | 0.370994 | 0.477850 | 0.512514 |
| E2 Reliability + Dropout 0.15 | 0 | 0.979990 | 0.950906 | 0.931057 | 0.956042 | 0.943384 | 0.948710 | 0.811566 | 0.978972 | 0.913083 |
| E5 ACRF + Dropout 0.15 | 48 | 0.978066 | 0.946602 | 0.938290 | 0.953737 | 0.945950 | 0.944019 | 0.846657 | 0.978531 | 0.923069 |
| E6 MSCD + Dropout 0.15 | 0 | 0.974990 | 0.945138 | 0.937297 | 0.949951 | 0.943582 | 0.941817 | 0.757718 | 0.962810 | 0.887448 |

## Phase 3A outputs

- Dropout report: `runs/dropout_ablation_summary.md`
- Qualitative report: `runs/qualitative_cases_summary.md`
- Phase 3A report: `runs/phase3a_report.md`
- Dropout ablation rows: 4
- Qualitative manifest rows: 25

### Dropout-ratio ablation

| Method | Dropout Ratio | P@0.50 | R@0.50 | F1@0.50 | Full AP50 | Full AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 Reliability Fusion | 0.00 | 0.925721 | 0.962298 | 0.943655 | 0.979317 | 0.947634 | 0.688697 | 0.370994 | 0.477850 | 0.512514 |
| E3 Reliability + Dropout 0.10 | 0.10 | 0.949248 | 0.945341 | 0.947290 | 0.977738 | 0.945218 | 0.930783 | 0.723911 | 0.978295 | 0.877663 |
| E2 Reliability + Dropout 0.15 | 0.15 | 0.931057 | 0.956042 | 0.943384 | 0.979990 | 0.950906 | 0.948710 | 0.811566 | 0.978972 | 0.913083 |
| E4 Reliability + Dropout 0.20 | 0.20 | 0.946437 | 0.951268 | 0.948846 | 0.978692 | 0.948514 | 0.954897 | 0.872685 | 0.979640 | 0.935741 |

## Phase 3B outputs

- Split-integrity report: `runs/split_integrity_summary.md`
- Dropout selection note: `runs/dropout_ratio_selection_note.md`
- Phase 3B report: `runs/phase3b_report.md`
- Split summary rows: 26
- Manual-review rows: 50

### Split-integrity summary

| Metric | Value | Notes |
| --- | --- | --- |
| train_count | 8391 | Existing split file rows. |
| val_count | 2098 | Existing split file rows. |
| path_overlap_count | 0 | Identical resolved paths in both splits. |
| exact_sha256_duplicate_pairs | 0 | Exact .npy byte duplicates across train/val. |
| numeric_id_parseable | yes | Numeric id parsed from final number in filename stem. |
| val_with_train_id_within_1 | 0.973308 | Fraction of val ids with a train id within +/- this distance. |
| val_with_train_id_within_2 | 0.994280 | Fraction of val ids with a train id within +/- this distance. |
| val_with_train_id_within_5 | 0.997617 | Fraction of val ids with a train id within +/- this distance. |
| val_with_train_id_within_10 | 0.999047 | Fraction of val ids with a train id within +/- this distance. |
| signature_distance_min | 0.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p01 | 0.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p05 | 0.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p10 | 0.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p25 | 4.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p50 | 8.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p75 | 14.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p90 | 22.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p95 | 30.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_p99 | 74.000000 | Hamming distance, 256-bit RGB pooled signature. |
| signature_distance_max | 83.000000 | Hamming distance, 256-bit RGB pooled signature. |
| fraction_signature_distance_<=0 | 0.101049 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=4 | 0.322212 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=8 | 0.565300 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=16 | 0.823642 | Fraction of val samples at or below threshold. |
| fraction_signature_distance_<=32 | 0.957579 | Fraction of val samples at or below threshold. |
| final_status | CAUTION: near-duplicate or adjacent-frame review required | Automatic audit label required by Phase 3B. |

## Phase 3C outputs

- RGB duplicate report: `runs/rgb_cross_split_duplicate_summary.md`
- Blocked split report: `runs/blocked_split_proposal_summary.md`
- RGB strata report: `runs/rgb_separation_strata_summary.md`
- Phase 3C report: `runs/phase3c_report.md`
- RGB duplicate summary rows: 20
- Blocked split candidate rows: 3
- RGB separation strata rows: 6

### RGB duplicate summary

| Metric | Value | Notes |
| --- | --- | --- |
| interpretation_label | CONFIRMED RGB-CONTENT CROSS-SPLIT DUPLICATION | Exact required Phase 3C label. |
| train_images | 8391 | Existing train split rows. |
| val_images | 2098 | Existing validation split rows. |
| exact_rgb_matched_val_images | 153 | Validation samples with at least one train sample sharing exact RGB content. |
| exact_rgb_matched_val_fraction | 0.072927 | Matched validation fraction. |
| exact_rgb_matched_train_images | 153 | Train samples with at least one validation sample sharing exact RGB content. |
| exact_rgb_matched_train_fraction | 0.018234 | Matched train fraction. |
| cross_split_rgb_groups | 153 | Distinct RGB-content hashes present in both splits. |
| group_total_size_min | 2 | Train+val samples per matched group. |
| group_total_size_p50 | 2 | Train+val samples per matched group. |
| group_total_size_max | 2 | Train+val samples per matched group. |
| group_val_size_p50 | 1 | Validation samples per matched group. |
| groups_identical_gt_box_counts | 123 | All records in the RGB group have one GT-box count. |
| groups_different_gt_box_counts | 30 | RGB group contains more than one GT-box count. |
| pair_id_distance_min | 1 | Representative exact RGB pairs, same filename family only. |
| pair_id_distance_p50 | 1 | Representative exact RGB pairs, same filename family only. |
| pair_id_distance_p90 | 1 | Representative exact RGB pairs, same filename family only. |
| train_gt_boxes | 24560 | Non-empty label rows in train split. |
| val_gt_boxes | 6074 | Non-empty label rows in validation split. |
| full_multimodal_byte_duplication_claim | not_claimed | This audit only hashes RGB channels; full 5-channel byte equality is not implied. |

### Blocked split candidates

| candidate | block_size | guard_band | train_images | val_images | guard_images | val_share_all_images | exact_rgb_matched_val_images | id_guard_violations | val_gt_boxes | recommended |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| block64_guard16_seed0 | 64 | 16 | 7439 | 2213 | 837 | 0.210983 | 0 | 0 | 5904 | yes |
| block128_guard32_seed0 | 128 | 32 | 7308 | 2231 | 950 | 0.212699 | 0 | 0 | 5040 | no |
| block256_guard64_seed0 | 256 | 64 | 6983 | 2384 | 1122 | 0.227286 | 0 | 0 | 6557 | no |

### RGB separation strata

| subset | model | image_count | gt_boxes | precision | recall | f1 | ap50 | ap75 | predictions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| near_rgb_match_or_near_neighbor | subset_only | 676 | 1923 | NA | NA | NA | NA | NA | NA |
| higher_rgb_separation | subset_only | 370 | 1071 | NA | NA | NA | NA | NA | NA |
| near_rgb_match_or_near_neighbor | E2 Reliability + Dropout 0.15 | 676 | 1923 | 0.942552 | 0.964119 | 0.953213 | 0.984299 | 0.957422 | 1967 |
| higher_rgb_separation | E2 Reliability + Dropout 0.15 | 370 | 1071 | 0.909589 | 0.929972 | 0.919668 | 0.961141 | 0.915696 | 1095 |
| near_rgb_match_or_near_neighbor | E4 Reliability + Dropout 0.20 | 676 | 1923 | 0.954476 | 0.970359 | 0.962352 | 0.985744 | 0.958865 | 1955 |
| higher_rgb_separation | E4 Reliability + Dropout 0.20 | 370 | 1071 | 0.924157 | 0.921569 | 0.922861 | 0.955066 | 0.917360 | 1068 |

## Phase 4A outputs

- Clean split protocol: `runs/clean_block64g16_protocol.md`
- Clean summary: `runs/clean_block64g16_summary.md`
- Phase 4A report: `runs/phase4a_report.md`
- Clean summary rows: 4

### Clean block64/guard16 summary

| Method | Dropout Ratio | Params | P@0.50 | R@0.50 | F1@0.50 | Full AP50 | Full AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0 Early Fusion | NA | 6591609 | 0.920573 | 0.881436 | 0.900580 | 0.941521 | 0.835843 | NA | NA | NA |
| B1 Reliability p=0.00 | 0.00 | 6593293 | 0.920237 | 0.894986 | 0.907436 | 0.949001 | 0.875731 | 0.675841 | 0.355645 | 0.428863 |
| B2 Reliability p=0.15 | 0.15 | 6593293 | 0.912933 | 0.914634 | 0.913783 | 0.956423 | 0.879736 | 0.906801 | 0.748108 | 0.957883 |
| B4 Reliability p=0.20 | 0.20 | 6593293 | 0.903604 | 0.925644 | 0.914491 | 0.960244 | 0.885327 | 0.907047 | 0.738021 | 0.961505 |

## Phase 4B outputs

- Seed reproducibility smoke: `runs/seed_reproducibility_smoke.md`
- Seed replication summary: `runs/clean_block64g16_seed_replication.md`
- Phase 4B report: `runs/phase4b_report.md`
- Seed replication rows: 8
- Decision: SELECT R4 AS CLEAN-SPLIT MAIN VARIANT

### Controlled-seed clean block64/guard16 summary

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

## Phase 5A outputs

- Phase 5A report: `runs/phase5a_report.md`
- Paper-readiness summary: `runs/paper_readiness_summary.csv`
- YOLO11n protocol: `runs/yolo11n_rgb_baseline_protocol.md`
- Convergence rows: 8
- Efficiency rows: 4
- R4 reliability-weight rows: 8
- Qualitative manifest rows: 20
- YOLO11n eval rows: 2
- Decision: READY FOR MANUSCRIPT DRAFTING

### YOLO11n RGB-only baseline

| Method | Seed | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| YOLO11n RGB-only | 0 | 0.913918 | 0.793022 | 0.849188 | 0.886374 | 0.629228 | 5904 | 5123 | 0.808770 |
| YOLO11n RGB-only | 2 | 0.914027 | 0.786924 | 0.845727 | 0.885401 | 0.636794 | 5904 | 5083 | 0.782716 |

### Clean efficiency profile

| Model | Path | Params | FPS mean | Latency ms/img mean | CUDA Memory MB mean | Note |
| --- | --- | --- | --- | --- | --- | --- |
| R0 Early Fusion | raw_forward | 6591609 | 102.762853 | 9.747951 | 115.153333 | seed0 checkpoint |
| R0 Early Fusion | detector_inference | 6591609 | 48.065821 | 20.818388 | 122.680000 | seed0 checkpoint |
| R4 Reliability p=0.20 | raw_forward | 6593293 | 97.717654 | 10.238004 | 228.940000 | seed0 checkpoint; dropout is training-only |
| R4 Reliability p=0.20 | detector_inference | 6593293 | 50.436489 | 19.829330 | 236.756667 | seed0 checkpoint; dropout is training-only |

## Phase 6A outputs

- Manuscript README: `manuscript/README.md`
- Draft manuscript: `manuscript/RA_RepDet_manuscript_v1.md`
- Phase 6A report: `runs/phase6a_manuscript_report.md`
- Figure manifest: `manuscript/figures/figure_manifest.md`
- Claim ledger: `manuscript/submission_notes/claim_ledger.md`
- Self-audit: `manuscript/submission_notes/manuscript_self_audit.md`
- Table CSV files: 7
- Table Markdown files: 7
- Figure source CSV files: 3
- Verified reference inventory rows: 31
- Decision: MANUSCRIPT DRAFT READY FOR JOURNAL TARGETING

## Phase 6B outputs

- SIVP README: `submission/sivp/README.md`
- Main LaTeX source: `submission/sivp/tex/main.tex`
- Body LaTeX source: `submission/sivp/tex/ra_repdet_sivp.tex`
- BibTeX references: `submission/sivp/tex/references.bib`
- Phase 6B report: `runs/phase6b_sivp_preparation_report.md`
- Figure insertion map: `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`
- Table insertion map: `submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md`
- Template/LaTeX source files: 16
- Metadata template files: 7
- Review/audit files: 5
- Decision: READY FOR ASSISTANT FINAL FIGURES, TABLES, AND AUTHOR METADATA


## Pending tasks

- Produce and author-approve final SIVP figures before replacing placeholder boxes.
- Prepare final publication tables from the existing manuscript/table CSV sources.
- Collect author metadata, declarations, funding, acknowledgments, and AI-use wording.
- Complete a final LaTeX compile after the local environment has required Springer dependencies.

## Known metric caveats

- Precision in the first-batch eval at score threshold 0.001 is artificially low because many low-confidence FCOS predictions are retained.
- AP50/AP75 are computed by score sorting and are not directly tied to the display threshold.
- Threshold sweep indicates 0.50 is the best F1 threshold for E0/E1/E2 in the current val split.
- Missing-modality tables use score threshold 0.05.
- Current AP implementation is project-local and does not depend on pycocotools.
- Phase 3C RGB-separation strata are diagnostics only and are not a clean independent test set.
- Phase 4A clean-split results use block64_guard16_seed0 only and should not be mixed with former random-split metrics.
- Phase 4B controlled-seed results use the same frozen block64_guard16_seed0 split with explicit seeds 0 and 2.
- Phase 4B still uses only two seeds; do not claim statistical significance.
- Phase 5A YOLO11n is an RGB-only external baseline and not an architecture-only ablation.
- Phase 6A manuscript is journal-neutral and citation style remains pending target journal selection.
- Phase 6B source package is pre-final and uses placeholders for final figures, tables, author details, and declarations.
- Phase 6B dry-run compilation was skipped if the local LaTeX environment lacks required Springer dependencies.
- Phase 7A is an asset-readiness and metadata-intake phase; it must not change clean-split metrics or retrain models.

## Important research decisions

- Missing txt labels are treated as empty-target images.
- TriAir class 0 is shifted to torchvision label 1; background remains label 0.
- E0/E1/E2 completed 50-epoch first-batch experiments and should not be retrained without explicit instruction.
- E2 is the strongest robustness-oriented model by missing-modality AP50/AP75.
- E1 has the highest F1 in the threshold sweep at threshold 0.50.
- E5 ACRF enforces exact zero alpha for synthetic absent modalities, but should remain an ablation unless the paper prioritizes alpha correctness over E2 full-modality AP.
- E6 MSCD keeps E2 inference architecture unchanged; use it as the main model only if the Phase 2C decision rule accepts it.
- Phase 3A should be used to justify the selected modality-dropout ratio without adding a new model family.
- Phase 3B corrects the ratio interpretation: E2 is accuracy-first, E4 is robustness-first; no ratio is universally dominant in the current single-seed ablation.
- If Phase 3C confirms exact RGB-content overlap, do not use the random split as a publication-grade independent benchmark.
- Phase 4A is the first clean blocked-split comparison and is single training-seed evidence only.
- Phase 4B decision gate: SELECT R4 AS CLEAN-SPLIT MAIN VARIANT.
- Phase 5A decision gate: READY FOR MANUSCRIPT DRAFTING.
- Phase 6A decision gate: MANUSCRIPT DRAFT READY FOR JOURNAL TARGETING.
- Phase 6B decision gate: READY FOR ASSISTANT FINAL FIGURES, TABLES, AND AUTHOR METADATA.
- Phase 7A starts from the completed Phase 6B SIVP source skeleton and should replace placeholders only after author approval.

## Files or scripts currently under review

- `AGENTS.md`
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/PROJECT_CONTEXT.md`
- `rarepdet/tools/update_project_status.py`
- `rarepdet/tools/finish_task.ps1`
- `rarepdet/tools/audit_rgb_cross_split_duplicates.py`
- `rarepdet/tools/propose_blocked_split.py`
- `rarepdet/tools/build_rgb_separation_subsets.py`
- `rarepdet/tools/validate_clean_block64_protocol.py`
- `rarepdet/tools/build_clean_block64_summary.py`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
