# MSCD Smoke Test

| Status | Check |
| --- | --- |
| PASS | Parameter count of student equals E2 exactly |
| PASS | Hooks capture matching P3/P4/P5 shapes for teacher and student |
| PASS | Student parameters receive gradients from detector loss |
| PASS | Consistency loss is finite for one missing-modality synthetic batch |
| PASS | Teacher parameters receive no gradients |
| PASS | Student parameters receive gradients from consistency loss |
| PASS | Consistency loss is finite for full-modality synthetic batch |
| PASS | Inference output of the student is unchanged in structure relative to E2 |
| INFO | rarepdet/train_early_fusion.py sha256=a03021b0788d08c9ba27fe2359aee3c49e87d51e0cc8fe86a7e3217bd39428b4 |
| INFO | rarepdet/models/early_fusion_fcos.py sha256=c2ad086c6dc0f0d1f390462184d496931d62ddf4c3e25c5816335f1b8c7db9f8 |
| INFO | rarepdet/models/reliability_fusion_fcos.py sha256=MISSING |
| INFO | datasets/triair_dataset.py sha256=f3592421394c465f469c45410e1981613223634e0dd3cfffded281777ddad705 |
| INFO | rarepdet/train_availability_fusion.py sha256=32efee837ed91be3079a62a5535cecc71f231b38d1f43482761ca2008b8b5a2f |
| INFO | rarepdet/models/availability_reliability_fusion_fcos.py sha256=57480137c0891d2dd0851d40f80ceb0cc147274b4933a04ab08c12a814ce9c45 |
