# ACRF Smoke Test

| Status | Check |
| --- | --- |
| PASS | no_rgb alpha absent modality <= 1e-7 |
| PASS | no_rgb post-stem absent modality energy is zero |
| PASS | no_thermal alpha absent modality <= 1e-7 |
| PASS | no_thermal post-stem absent modality energy is zero |
| PASS | no_event alpha absent modality <= 1e-7 |
| PASS | no_event post-stem absent modality energy is zero |
| PASS | full alpha sums to 1 |
| PASS | FCOS training loss works |
| PASS | FCOS inference output works |
| INFO | rarepdet/train_early_fusion.py sha256=a03021b0788d08c9ba27fe2359aee3c49e87d51e0cc8fe86a7e3217bd39428b4 |
| INFO | rarepdet/models/early_fusion_fcos.py sha256=c2ad086c6dc0f0d1f390462184d496931d62ddf4c3e25c5816335f1b8c7db9f8 |
| INFO | rarepdet/models/reliability_fusion_fcos.py sha256=MISSING |
| INFO | datasets/triair_dataset.py sha256=f3592421394c465f469c45410e1981613223634e0dd3cfffded281777ddad705 |
