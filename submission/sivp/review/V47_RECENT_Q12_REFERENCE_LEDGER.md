# V47 Recent Q1--Q2 Journal Reference Ledger

Generated: 2026-07-10

## Selection rule

The user requested approximately 40 references, emphasizing formally published work from the most recent three-year window and journals ranked in the second quartile or above.

For this revision:

- The recent window is interpreted as 2023--2025.
- `Q2 or above` is interpreted as publicly verifiable journal-level JCR/SJR Q1--Q2 status.
- This ledger does **not** claim Chinese Academy of Sciences journal partitions because those classifications require a separately specified edition and institutional rule.
- All entries newly added in `references_recent_q12_2023_2025.bib` are formal journal articles from 2023 or 2024.
- A small number of older original method/dataset publications remain cited in the manuscript because replacing primary provenance citations with newer surveys would be academically inappropriate. They are not counted as new recent-journal additions.

## Recent journal additions

| BibTeX key | Year | Journal | Topic | Public journal-quality basis |
| --- | ---: | --- | --- | --- |
| `ZhangDemiris2023DeepFusion` | 2023 | IEEE TPAMI | infrared--visible fusion survey/analysis | Q1 journal |
| `Li2023LRRNet` | 2023 | IEEE TPAMI | optimization-guided fusion | Q1 journal |
| `Yue2023DifFusion` | 2023 | IEEE TIP | diffusion-based fusion | Q1 journal |
| `Liu2024TIMFusion` | 2024 | IEEE TPAMI | task-guided architecture search | Q1 journal |
| `Rao2023ATGAN` | 2023 | Information Fusion | adversarial fusion | Q1 journal |
| `Wang2024FreqGAN` | 2024 | IEEE TCSVT | frequency-domain fusion | Q1/Q2 journal |
| `Tang2023TCCFusion` | 2023 | Pattern Recognition | transformer correlation fusion | Q1 journal |
| `Tang2023DATFuse` | 2023 | IEEE TCSVT | dual-attention fusion | Q1/Q2 journal |
| `Park2024CrossModalTransformers` | 2024 | IEEE TCSVT | cross-modal transformer fusion | Q1/Q2 journal |
| `Liu2023PromptFusion` | 2023 | IEEE/CAA Journal of Automatica Sinica | semantic-prompt fusion | Q1 journal |
| `Tang2023PSFusion` | 2023 | Information Fusion | task-oriented semantic fusion | Q1 journal |
| `Zhang2023CMX` | 2023 | IEEE TITS | RGB-X semantic fusion | Q1 journal |
| `Zhao2023ModalityDiscrepancies` | 2023 | IEEE TNNLS | RGB-T modality discrepancy | Q1 journal |
| `Tang2023RGBTTracking` | 2023 | Information Fusion | RGBT tracking fusion | Q1 journal |
| `Zhou2023MC3Net` | 2023 | IEEE TITS | RGB-T crowd counting | Q1 journal |
| `Yang2024CAGNet` | 2024 | Expert Systems with Applications | RGB-T adaptive fusion | Q1 journal |
| `Wang2023FusionSOD` | 2023 | Information Fusion | joint fusion and saliency | Q1 journal |
| `Xu2023MURF` | 2023 | IEEE TPAMI | registration and fusion | Q1 journal |
| `Zhang2023ConditionalGANFusion` | 2023 | IEEE TMM | transformer conditional GAN fusion | Q1 journal |
| `Rao2023TGFuse` | 2023 | IEEE TIP | transformer-GAN fusion | Q1 journal |
| `Luo2023UAVRegistration` | 2023 | Scientific Reports | visible--infrared UAV registration | Q1/Q2 journal depending category/year |
| `Xie2023SemanticsLeadAll` | 2023 | Information Fusion | semantic registration and fusion | Q1 journal |
| `Guo2023MultiSpectrumDepth` | 2023 | IEEE Transactions on Intelligent Vehicles | multispectral depth | Q1 journal |
| `Liu2023CoCoNet` | 2023 | International Journal of Computer Vision | contrastive multimodal fusion | Q1 journal |
| `Ektefaie2023MultimodalGraphs` | 2023 | Nature Machine Intelligence | multimodal representation learning | Q1 journal |
| `Gehrig2024LowLatencyEvent` | 2024 | Nature | event-camera perception | Q1 journal |
| `Kaufmann2023ChampionDrone` | 2023 | Nature | autonomous UAV perception/control | Q1 journal |
| `Song2023AutonomousRacing` | 2023 | Science Robotics | autonomous drone racing | Q1 journal |

## Existing recent journal references retained

The revised body also cites these recent formal journal articles that were already present in the repository bibliography:

| BibTeX key | Year | Journal | Purpose |
| --- | ---: | --- | --- |
| `Zou2023OD20Years` | 2023 | Proceedings of the IEEE | modern object-detection review |
| `Han2023VisionTransformer` | 2023 | IEEE TPAMI | vision-transformer review |
| `Kapoor2023Patterns` | 2023 | Patterns | leakage and reproducibility |

## Foundational primary-source exceptions

The following older or conference references remain because they are the original sources for the detector, backbone, split benchmarks, or missing-modality methods used in the paper:

- `RepViT2024`
- `FPN2017`
- `FCOS2019`
- `FasterRCNN2015`
- `RetinaNet2017`
- `VisDrone2018`
- `UAVDT2018`
- `ModDrop2016`
- `HeMIS2016`

These exceptions should not be represented as satisfying the recent-Q1/Q2-journal filter. They are retained solely for correct scholarly provenance.

## Manuscript citation target

The revised manuscript is designed to cite approximately 40 works in total:

- 28 newly added recent Q1/Q2 journal articles;
- 3 recent journal articles already in the repository;
- 9 foundational primary-source exceptions.

The bibliography database contains additional legacy entries, but BibTeX will print only cited items unless the manuscript later introduces `\\nocite{*}`. The revision does not use `\\nocite{*}`.

## Remaining verification caution

Journal quartiles can change by database edition and subject category. Before final submission, the author should export the institutionally accepted JCR/SJR evidence for the exact reporting year. If the institution specifically requires the Chinese Academy of Sciences partition, this ledger must be replaced by a CAS-edition-specific verification rather than relabelled without evidence.
