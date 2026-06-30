# Reliability-Aware RepViT-FCOS for Tri-Modal UAV Vehicle Detection Under Leakage-Aware Evaluation

Front-matter note: this is a journal-neutral draft, not a submission-formatted manuscript. Alternative titles for later journal targeting are: "Leakage-Aware Tri-Modal UAV Vehicle Detection with Reliability-Gated RepViT-FCOS"; "Robust RGB-Thermal-Event Vehicle Detection for UAV Perception Using Modality Dropout"; and "A Reproducible RepViT-FCOS Baseline for TriAir Vehicle Detection with Missing-Modality Robustness".

## Abstract

Multi-sensor UAV perception can benefit from RGB, thermal, and event information, but evaluation is easily overstated when adjacent frames or duplicated visual content leak across splits. We present RA-RepDet, a lightweight RepViT-FCOS detector for TriAir vehicle detection that combines RGB, thermal, and event channels through reliability-aware fusion and modality-dropout training. The study is built around a leakage-aware blocked split with a guard band: 7439 training images, 2213 validation images, and 837 excluded guard images, with zero exact RGB train/validation matches and zero same-family guard violations after a duplicate audit of the former random split. In controlled two-seed experiments, the proposed R4 variant, reliability fusion with modality dropout p=0.20, achieved mean AP50=0.962495, AP75=0.891266, and F1=0.920861. It improved the matched tri-modal early-fusion RepViT-FCOS baseline in full-modality AP50 and provided the strongest robustness among evaluated reliability variants when one sensor stream was synthetically removed. The RGB-only YOLO11n comparison is reported as an external baseline, not an architecture-only ablation. The results support RA-RepDet as a practical and reproducible tri-modal UAV detection baseline, while the two-seed design, single dataset, synthetic missingness, and remaining thermal-drop vulnerability delimit the claims.

## Keywords

UAV vehicle detection; RGB-thermal-event fusion; RepViT; FCOS; missing-modality robustness; data leakage; blocked split.

## 1. Introduction

UAV vehicle detection increasingly needs to operate under changing illumination, target scale variation, and sensor uncertainty. RGB cameras provide detailed texture and color cues, thermal sensors can retain target contrast when visible light degrades, and event streams can encode sparse temporal changes with high dynamic range. A practical detector for this setting should be lightweight enough for deployment-oriented research, should use all available modalities without relying on one stream alone, and should be evaluated under a protocol that does not inflate performance through visual overlap between train and validation images.

This work studies tri-modal vehicle detection on TriAir using five-channel samples composed of RGB, thermal, and event channels. The detector uses a RepViT-M0.9 backbone [REF: RepViT2024], an FPN neck [REF: FPN2017], and an FCOS anchor-free detection head [REF: FCOS2019]. The baseline, R0, projects the five input channels to three channels and applies RepViT-FCOS. The proposed main variant, R4, uses modality-specific stems and a learned reliability estimator to fuse RGB, thermal, and event features before the RepViT backbone. During training, R4 uses modality dropout with p=0.20 to improve behavior when a sensor stream is removed at inference-like evaluation time.

The central methodological point is that the paper does not rely on the original random split. A Phase 3C audit found 153 exact RGB-content train/validation overlaps in the random split, corresponding to 0.072927 of validation images. We therefore use a frozen block64/guard16 split with 7439 training images, 2213 validation images, and 837 guard images. This split has zero exact RGB train/validation matches and zero same-family guard-band violations. This protocol is important because benchmark leakage and selection bias can make apparent gains less reliable [REF: Kapoor2023Leakage] [REF: Cawley2010Overfitting].

The contributions are conservative. First, we provide a reproducible RepViT-FCOS tri-modal UAV vehicle detection baseline on a leakage-aware clean split. Second, we show that reliability-aware fusion improves the matched tri-modal early-fusion baseline in controlled two-seed experiments. Third, we show that modality dropout improves robustness under synthetic single-modality removal, with p=0.20 selected as the main variant by controlled clean-split evidence. Fourth, we separate the matched tri-modal ablation from an RGB-only YOLO11n external baseline [REF: YOLO11Docs], avoiding the unsupported claim that the gap is due only to architecture.

## 2. Related Work

### 2.1 UAV Vehicle Detection

Vehicle detection from UAV imagery has been studied through benchmarks such as VisDrone and UAVDT, which emphasize small objects, dense scenes, viewpoint changes, and platform motion [REF: VisDrone2018] [REF: UAVDT2018]. These benchmarks helped clarify why conventional object detectors require careful multi-scale processing in aerial views. General object detection progress, including region-proposal detectors, dense one-stage detectors, and focal-loss formulations, provides the backbone of modern detection systems [REF: FasterRCNN2015] [REF: RetinaNet2017]. Our work follows this line but focuses on a tri-modal UAV setting, where the sensor representation and split integrity are as important as the detector family.

### 2.2 RGB-Thermal-Event / Multi-Sensor Detection

RGB-thermal perception has a long history in pedestrian and vehicle detection because visible and infrared cues respond differently to illumination and heat contrast. KAIST multispectral pedestrian detection, FLIR ADAS, LLVIP, and DroneVehicle are representative resources for visible-infrared learning [REF: KAIST2015] [REF: FLIRADAS] [REF: LLVIP2021] [REF: DroneVehicle2021]. Cross-modal supervision and modality hallucination further demonstrate that information from one sensor can regularize or substitute another during training [REF: CrossModalDistillation2016] [REF: ModalityHallucination2016]. Event-camera work complements this view by providing high-temporal-resolution sensing and robustness to high dynamic range scenes, as summarized in event-based vision surveys and driving datasets such as MVSEC, DSEC, and GEN1 [REF: Gallego2020EventSurvey] [REF: MVSEC2018] [REF: DSEC2021] [REF: Gen1Events]. RA-RepDet is positioned inside this multi-sensor detection space, but the contribution is a practical fusion baseline rather than a broad event-vision model.

### 2.3 Missing-Modality Robustness

Missing-modality learning addresses the case in which one or more input streams are unavailable, corrupted, or intentionally withheld. Modality dropout and hetero-modal learning are common strategies for reducing dependence on a single stream [REF: ModDrop2016] [REF: HeMIS2016]. In this study, synthetic missingness is implemented by zeroing a modality during evaluation. This is a controlled stress test rather than a complete model of real sensor failure. The reliability-weight audit is therefore interpreted as observed gating behavior under synthetic removal, not as causal evidence of physical modality importance.

## 3. Method

### 3.1 Overall Architecture

The detector receives a five-channel tensor containing RGB, thermal, and event inputs. All variants use RepViT-M0.9 features with four stages of channel sizes 48, 96, 192, and 384, followed by an FPN that maps each stage to 128 channels and an FCOS detection head. This structure preserves the lightweight mobile-convolutional design of RepViT while using a standard anchor-free detection formulation [REF: RepViT2024] [REF: FCOS2019] [REF: TorchvisionFCOS]. The task is single-class vehicle detection. TriAir label class 0 is converted to torchvision label 1 during training, while background remains label 0.

### 3.2 Early-Fusion Baseline

The matched tri-modal baseline, R0, uses a 1x1 input projection from five channels to three channels before the RepViT backbone. This design keeps the backbone interface compatible with ImageNet-style three-channel models while exposing all modalities to the detector. It is intentionally simple and serves as the primary architecture/fusion baseline. Because R0 and the reliability variants share the same detection head, FPN width, backbone family, training split, image size, and evaluation code, R0 versus R1/R2/R4 is the valid matched ablation for fusion design.

### 3.3 Reliability-Aware Tri-Modal Fusion

The reliability model separates the input into RGB, thermal, and event streams. RGB is processed by a Conv2d(3,16,3,padding=1)+BN+SiLU stem, thermal by a Conv2d(1,16,3,padding=1)+BN+SiLU stem, and event by the same one-channel stem. Global average pooled stem features are concatenated into a 48-dimensional vector and passed through a lightweight estimator, Linear(48,16)+SiLU+Linear(16,3), followed by softmax. The resulting alpha values weight the three 16-channel stem tensors, and the fused tensor is projected to three channels before RepViT. This adds only a small parameter increase relative to R0 while making the fusion operation input-adaptive.

### 3.4 Modality-Dropout Training

The R1 variant uses reliability fusion without modality dropout. R2 uses modality dropout p=0.15, and R4 uses p=0.20. Modality dropout is training-only: at training time, sensor streams can be zeroed to discourage brittle dependence on one stream; at standard full-modality inference, all streams are provided. Missing-modality evaluation uses synthetic removal of RGB, thermal, or event channels. This setup supports controlled robustness measurement, but it does not prove that the same behavior will transfer perfectly to all real sensor-failure mechanisms.

## 4. Dataset and Leakage-Aware Evaluation Protocol

### 4.1 TriAir Data Representation and Labels

TriAir is represented locally as 10489 `.npy` samples. Each sample is a five-channel RGB-thermal-event image, and labels are YOLO-format vehicle boxes. There are 9751 images with label text files, 738 images without label text files, and one empty label text file. Missing or empty label files are treated as empty-target images rather than discarded. Across the dataset, 30634 valid vehicle boxes are available. YOLO-normalized labels are converted to absolute xyxy boxes for torchvision detection training and evaluation.

### 4.2 RGB-Content Duplicate Audit

Before the clean protocol was adopted, the random split was audited for exact RGB-content overlap. The audit detected 153 validation samples with at least one training sample sharing exact RGB content, covering 0.072927 of validation images. This finding does not claim full five-channel byte duplication, but it is sufficient to make the random split unsuitable for publication-grade headline results. This decision follows the broader principle that leakage-aware evaluation is necessary when samples may be adjacent or visually repeated [REF: Kapoor2023Leakage] [REF: Recht2019ImageNet] [REF: Northcutt2021LabelErrors].

### 4.3 Blocked Split and Guard Band

The final evaluation uses the frozen `block64_guard16_seed0` split. It contains 7439 training images, 2213 validation images, and 837 guard images that are excluded from both training and validation. The validation set contains 5904 ground-truth boxes. Integrity checks report zero exact RGB train/validation matches and zero same-family guard violations. All main claims in this manuscript use this split only. The former E0-E6 random-split experiments are retained as historical diagnostics but are excluded from the abstract, main results tables, and conclusion.

## 5. Experiments

### 5.1 Experimental Settings and Reproducibility

The clean-split controlled comparison trains R0, R1, R2, and R4 for 50 epochs at seeds 0 and 2. The image size is 640, and the same local AP implementation is used for AP50 and AP75. The two seeds provide controlled replication and are not treated as a statistical-significance test. A seed reproducibility smoke test confirms that identical seeds reproduce initial state and early shuffling, while different seeds produce different initialization and shuffling. Efficiency profiling uses batch size 1, 640-pixel inputs, 100 warm-up iterations, 300 timed iterations, and three repeats, excluding dataloader and file I/O.

### 5.2 Controlled Clean-Split Ablation

The matched tri-modal ablation supports the selection of R4 as the main variant. R0 early fusion achieved AP50 values of 0.938560 and 0.937711 across seeds 0 and 2, with mean AP50=0.938136. R1 reliability fusion without dropout improved AP50 to 0.952112 and 0.954378, with mean AP50=0.953245. R2 with p=0.15 reached AP50=0.961573 and 0.957739, while R4 with p=0.20 reached AP50=0.965012 and 0.959977. R4 therefore had the highest mean AP50=0.962495. R4 also achieved mean AP75=0.891266 and mean F1=0.920861. AP75 leadership was split between R2 and R4 by seed, so the claim is not that R4 dominates every metric, but that it is the best overall clean-split main variant under the predefined selection logic.

### 5.3 Robustness to Synthetic Missing Modalities

Missing-modality evaluation shows the main benefit of modality dropout. R1 without dropout has weak missing-modality AP50, especially under thermal removal. R2 improves all three synthetic removal cases, and R4 improves the R2 results in both seeds for no-RGB, no-thermal, and no-event AP50. R4 mean AP50 values are 0.916051 without RGB, 0.718277 without thermal, and 0.961577 without event. Thermal removal remains the hardest condition, and this vulnerability is a limitation rather than a solved problem.

### 5.4 RGB-Only External Baseline

YOLO11n is included as an RGB-only external detector under the same clean split [REF: YOLO11Docs]. It is not a matched architecture-only ablation because it uses RGB input only, whereas R4 uses RGB, thermal, and event streams. Across seeds 0 and 2, YOLO11n RGB-only achieved AP50 values of 0.886374 and 0.885401, AP75 values of 0.629228 and 0.636794, and F1 values of 0.849188 and 0.845727. These values show the practical gap between the proposed tri-modal detector and a standard lightweight RGB-only external baseline, but they do not isolate whether the gap comes from architecture, modality availability, or both.

### 5.5 Efficiency and Convergence

R0 has 6591609 parameters, while R4 has 6593293 parameters. In raw-forward profiling, R0 measured 102.762853 FPS and 9.747951 ms per image, while R4 measured 97.717654 FPS and 10.238004 ms per image. In complete detector inference, R0 measured 48.065821 FPS and 20.818388 ms per image, while R4 measured 50.436489 FPS and 19.829330 ms per image. The detector-inference difference should be interpreted cautiously because it is small and measured on one hardware/software setting. Peak allocated CUDA memory was higher for R4, 236.756667 MB for complete detector inference compared with 122.680000 MB for R0. The convergence audit found seven runs clearly plateaued and one near plateau under the fixed 50-epoch schedule.

### 5.6 Reliability-Weight Analysis

The R4 reliability audit reports mean alpha values under full input and three synthetic missing-modality conditions. For seed 0 under full input, the means were alpha_rgb=0.430324, alpha_thermal=0.350048, and alpha_event=0.219628. For seed 2, the corresponding values were 0.459054, 0.350642, and 0.190304. When thermal was removed, the mean RGB alpha increased to 0.708866 for seed 0 and 0.761068 for seed 2, while the thermal alpha decreased but did not become zero. This is observed gating behavior under zeroed inputs. It should not be interpreted as a physically causal importance estimate or as exact absent-modality suppression.

### 5.7 Qualitative Results and Limitations

The qualitative manifest contains 20 illustrative cases: five where R4 corrects an R0 miss or localization failure, five shared successful detections, five R4 hard cases, and five missing-modality illustrative cases. These examples are intended to support visual inspection, not to prove universal superiority. The main limitations are fourfold. First, the controlled replication uses two seeds, so the evidence is not a statistical-significance analysis. Second, missingness is synthetic and does not cover all real sensor degradations. Third, the experiments use one dataset. Fourth, thermal removal remains the most difficult synthetic sensor-loss case even for R4.

## 6. Conclusion

This manuscript draft presents RA-RepDet, a reliability-aware RepViT-FCOS detector for RGB-thermal-event UAV vehicle detection. Under a leakage-aware blocked split with a guard band, R4 reliability fusion with modality dropout p=0.20 achieved mean AP50=0.962495, AP75=0.891266, and F1=0.920861 across two controlled seeds. The study supports reliability-aware fusion and modality-dropout training as practical tools for robust tri-modal detection, while carefully separating matched fusion ablations from an RGB-only YOLO11n external baseline. The next step is not more claim expansion, but target-journal selection, citation-style finalization, and figure-format preparation using the commit-safe tables and manifests created in this package.

## Data and Code Availability Statement

The source code, reproducible table files, figure manifests, and lightweight experiment summaries are intended to be versioned in the project repository. Raw TriAir arrays, local dataset files, trained weights, rendered qualitative panels, and large prediction outputs are not committed. The clean split file hashes and local evidence reports are recorded in `runs/clean_block64g16_protocol.md`, `runs/phase4b_report.md`, and `runs/phase5a_report.md`. Access to the original dataset should follow the dataset owner's distribution terms, and any final submission should replace this draft statement with a target-journal-compliant data and code availability statement.
