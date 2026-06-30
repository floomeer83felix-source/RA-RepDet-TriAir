# Implementation Details Evidence Template

This file records what is supported by current code/log evidence and what still requires author confirmation. Do not replace `AUTHOR_REQUIRED` fields without a real source.

| Field | Current value | Evidence source | Status |
| --- | --- | --- | --- |
| Input representation | RGB(3)+thermal(1)+event(1), five channels | `datasets/triair_dataset.py`; `rarepdet/data.py` | verified |
| Image tensor format | CxHxW float32, divided by 255.0 in detection adapter | `datasets/triair_dataset.py`; `rarepdet/data.py` | verified |
| Label handling | YOLO normalized boxes converted to absolute xyxy; class 0 shifted to label 1 | `datasets/triair_dataset.py`; `rarepdet/data.py` | verified |
| R0 early fusion | Conv2d(5,3,1) -> RepViT -> FPN -> FCOS | `rarepdet/models/repvit_fpn_backbone.py` | verified |
| R4 stems | RGB Conv2d(3,16,3,padding=1)+BN+SiLU; thermal/event Conv2d(1,16,3,padding=1)+BN+SiLU | `rarepdet/models/repvit_fpn_backbone.py` | verified |
| Reliability MLP | Linear(48,16)+SiLU+Linear(16,3)+softmax | `rarepdet/models/repvit_fpn_backbone.py` | verified |
| FPN channels | input [48, 96, 192, 384], output 128 | `rarepdet/models/repvit_fpn_backbone.py` | verified |
| FCOS classes | `num_classes=2` with background 0 and vehicle 1 | `rarepdet/models/early_fusion_fcos.py`; `rarepdet/train_early_fusion.py` | verified |
| Optimizer | AdamW | `rarepdet/train_early_fusion.py` | verified |
| Learning rate | 1e-4 in reported clean runs unless final config proves otherwise | `runs/*/config.txt`; `rarepdet/train_early_fusion.py` | verify per run |
| Weight decay | 1e-4 | `rarepdet/train_early_fusion.py` | verified |
| Scheduler | no explicit scheduler | `rarepdet/train_early_fusion.py` | verified |
| Complex augmentation | none; no mosaic/mixup | `rarepdet/data.py`; `rarepdet/train_early_fusion.py` | verified |
| Batch size | AUTHOR_REQUIRED_PER_FINAL_RUN | final run config/log | missing |
| Hardware | AUTHOR_REQUIRED | author/system record | missing |
| Software versions | AUTHOR_REQUIRED | `pip freeze`, environment file, or author record | missing |
| TriAir source/citation/licence | AUTHOR_REQUIRED | dataset documentation from author/provider | missing |
