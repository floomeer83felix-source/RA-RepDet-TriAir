# Literature Screening and Reference Expansion

## Purpose

This record documents the expanded reference base for Manuscript Draft A. The goal is to strengthen the paper's positioning without overstating relevance or treating citation count as evidence. Every added source is placed in a theme that corresponds to a concrete part of the manuscript: detector lineage, UAV/remote sensing, visible--thermal fusion, event vision, robustness, evaluation integrity, or efficient deployment.

## Quartile Rule

The catalogue contains **37 formal journal articles** and **17 top conference or workshop papers**. The journals were screened from venues commonly used for high-quality peer-reviewed research in computer vision, remote sensing, image processing, robotics, information fusion, and machine learning. A static `Q1` or `Q2` label is intentionally not written beside individual papers because JCR/SJR quartiles can change by year and subject category. Before submission, confirm the applicable category-year rule required by the institution or target journal.

## Formal Journal Articles (37)

### Detection, UAV, remote sensing, and multimodal theory

| key | venue | role in Draft A |
| --- | --- | --- |
| `Liu2020GenericOD` | International Journal of Computer Vision | generic detector taxonomy |
| `Zhao2019ODReview` | IEEE Transactions on Neural Networks and Learning Systems | deep object-detection review |
| `Zou2023OD20Years` | Proceedings of the IEEE | historical object-detection review |
| `Cheng2016RSODSurvey` | ISPRS Journal of Photogrammetry and Remote Sensing | optical remote-sensing detection |
| `Zhu2017DLRemoteSensing` | IEEE Geoscience and Remote Sensing Magazine | remote-sensing deep-learning context |
| `Ma2019DLRemoteSensing` | ISPRS Journal of Photogrammetry and Remote Sensing | remote-sensing meta-review |
| `Wu2022UAVSurvey` | IEEE Transactions on Geoscience and Remote Sensing | UAV detection and tracking survey |
| `Deng2018MultiscaleRSOD` | ISPRS Journal of Photogrammetry and Remote Sensing | multi-scale remote-sensing detection |
| `Baltrusaitis2019MMLSurvey` | IEEE Transactions on Pattern Analysis and Machine Intelligence | multimodal learning taxonomy |
| `Ramachandram2017DeepMultimodal` | IEEE Signal Processing Magazine | deep multimodal learning survey |
| `Minaee2022SegmentationSurvey` | IEEE Transactions on Pattern Analysis and Machine Intelligence | dense-vision survey context |
| `Voulodimos2018DLVision` | Computational Intelligence and Neuroscience | deep vision background |

### Visible--thermal fusion and event vision

| key | venue | role in Draft A |
| --- | --- | --- |
| `Gallego2022EventSurvey` | IEEE Transactions on Pattern Analysis and Machine Intelligence | event-vision survey |
| `Gehrig2021DSEC` | IEEE Robotics and Automation Letters | event-driving dataset context |
| `Zhu2018MVSEC` | IEEE Robotics and Automation Letters | event stereo/3D dataset context |
| `Mueggler2017EventDataset` | International Journal of Robotics Research | event dataset and simulator context |
| `Li2019DenseFuse` | IEEE Transactions on Image Processing | learned visible--infrared fusion |
| `Ma2019FusionGAN` | Information Fusion | adversarial visible--infrared fusion |
| `Zhang2020IFCNN` | Information Fusion | CNN image-fusion framework |
| `Li2021RFNNest` | Information Fusion | residual fusion architecture |
| `Xu2022U2Fusion` | IEEE Transactions on Pattern Analysis and Machine Intelligence | unsupervised fusion network |
| `Ma2019InfraredSurvey` | Information Fusion | infrared/visible fusion survey |
| `Li2013GuidedFiltering` | IEEE Transactions on Image Processing | classical image fusion baseline |

### Evaluation integrity, benchmarks, robustness, and efficiency

| key | venue | role in Draft A |
| --- | --- | --- |
| `Cawley2010JMLR` | Journal of Machine Learning Research | model-selection bias |
| `Kapoor2023Patterns` | Patterns | leakage and reproducibility |
| `Russakovsky2015ImageNet` | International Journal of Computer Vision | benchmark design context |
| `Everingham2010VOC` | International Journal of Computer Vision | detection benchmark context |
| `Geiger2013KITTI` | International Journal of Robotics Research | autonomous-driving benchmark context |
| `Srivastava2014Dropout` | Journal of Machine Learning Research | dropout regularization |
| `Krizhevsky2017CACM` | Communications of the ACM | CNN lineage |
| `Khan2020CNN` | Artificial Intelligence Review | CNN architecture survey |
| `Khan2022TransformersVision` | ACM Computing Surveys | vision-transformer survey |
| `Han2023VisionTransformer` | IEEE Transactions on Pattern Analysis and Machine Intelligence | vision-transformer survey |
| `Shorten2019Augmentation` | Journal of Big Data | augmentation survey |
| `Alzubaidi2021DLReview` | Journal of Big Data | deep-learning background |
| `Sze2017EfficientDNN` | Proceedings of the IEEE | efficient DNN implementation |
| `Cheng2018CompressionSurvey` | IEEE Signal Processing Magazine | model compression and acceleration |

## Top Conference / Workshop Papers (17)

| key | venue | role in Draft A |
| --- | --- | --- |
| `SSD2016` | ECCV | one-stage detection lineage |
| `YOLO2016` | CVPR | real-time detection lineage |
| `DeformableConv2017` | ICCV | spatially adaptive convolution |
| `DOTA2018` | CVPR | aerial-object detection dataset |
| `MobileNetV2_2018` | CVPR | mobile CNN design |
| `EfficientNet2019` | ICML | efficient scaling context |
| `MobileNetV3_2019` | ICCV | hardware-aware mobile CNN |
| `DETR2020` | ECCV | transformer detector lineage |
| `DeformableDETR2021` | ICLR | deformable transformer detector |
| `RepVGG2021` | CVPR | structural re-parameterization |
| `Swin2021` | ICCV | hierarchical vision transformers |
| `DINO2023` | ICLR | denoising DETR formulation |
| `RepViT2024CVPR` | CVPR | tested backbone lineage |
| `ViT2021` | ICLR | vision-transformer reference |
| `ATSS2020` | CVPR | adaptive assignment |
| `DroneVehicle2021ICCVW` | ICCV Workshops | drone RGB--infrared vehicle dataset |
| `LLVIP2021ICCVW` | ICCV Workshops | low-light visible--infrared dataset |

## Integration Status

- The four BibTeX packs are in `submission/sivp/tex/`.
- All three manuscript entry files now load the literature appendix and the four reference packs.
- `related_work_literature_expansion.tex` cites the added sources by theme; it does not alter any frozen experiment number, table, split, figure decision, or publication claim.
- The main manuscript body retains conservative validation-only wording.

## Required Final Check

Before a final submission build, the author team must:

1. check each selected journal against the required institutional JCR/SJR year and subject category;
2. remove peripheral citations that do not materially improve the target journal's narrative;
3. compile the Springer source with BibTeX or Biber according to the final template; and
4. verify that all entries resolve with no missing-key, duplicate-key, or malformed-author warnings.
