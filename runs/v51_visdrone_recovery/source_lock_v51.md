# V51 Source Lock

Generated: `2026-07-13T21:11:13+08:00`
Starting commit: `520443266fb1a917e50acfbd09772b4d74f6bb00`
Branch: `research/ra-repdet-triair`
Route: `B_GROUP_DISJOINT_CROSS_VALIDATION`.

## Frozen protocol

- Three group-disjoint folds; filename field 1 is the immutable group key.
- Seeds 0, 1, and 2 start from scratch for every fold.
- 50 epochs, RGB 640, batch 4, AdamW, learning rate 1e-4.
- Checkpoint selection uses only the paired frozen validation fold's canonical COCO AP50.
- Score threshold 0.001, NMS 0.6, max detections 100.
- V50 quarantined test metrics are not inputs and cannot become V51 evidence.
- Route B reports cross-validation only; it has no independent or blind test.

## Frozen artifacts

- `datasets/visdrone_seen_dataset.py`: `8a729f6de6b3dfb3cd9942cd9bb2d6d8977e5f74e714aa4dd67d2cce1ea02809`
- `rarepdet/models/rgb_fcos.py`: `c5d6bf2d261b4f0ab5e4ceb3360e7a5584f4d57067ad8a7d0cd32f30936eaade`
- `rarepdet/tools/build_v51_cv_reports.py`: `05d0e79fa63721fb4d9a54c7cbbf39d604556ecd8499b6dfd6ba0655467a58eb`
- `rarepdet/tools/eval_v50_visdrone_seen.py`: `071d5081978d6179fd02382dd1dd9183e8aca874712e6e4aa212a066d3a79072`
- `rarepdet/tools/eval_v51_visdrone_recovery.py`: `7d7d3ca3584c46788b21e1e3aad3dcdd5a4f75d7c23158ec2616ad2220919bc2`
- `rarepdet/tools/prepare_v51_visdrone_recovery.py`: `ed5e1a2283f3c589bff7b23c2607484f5ce0fd50d565936277c73fdbca2749fc`
- `rarepdet/tools/run_v51_cv_queue.py`: `074666b6b5330eaf857914599aee5d56e99fcb1e4679e53577e2ceb6fa10222b`
- `rarepdet/train_visdrone_rgb.py`: `5709027cb0d975e5cf420cc9a4bd0a2496ecbd429be3689b804f3eccf7c3ce14`
- `rarepdet/v50_coco.py`: `2e872da6cac347f199a9f70594fba56341c6c45e71c3d9bc19bd89cf77d7ddec`
- `runs/v50_visdrone_seen/class_mapping.json`: `9531834f4620ee14e2d9932f34a75695697c29929cb1fa0e666e7e7e2d16a053`
- `runs/v51_visdrone_recovery/candidate_annotation_hashes.json`: `7a52e5564061f05caaa8a323d824eb2e7c7cc43e34a7caf482066ee7cdcb3488`
- `runs/v51_visdrone_recovery/candidate_image_hashes.json`: `3e225d8aed4e5e6b16ec4fbdf6287eb71c0a14c4883e2363efe7158d20bd3336`
- `runs/v51_visdrone_recovery/converted_annotations/fold_0_train.json`: `33c687c674b0de6831d5432e72178b08a7086a3f1f639cce1d0e4eafe40bc46a`
- `runs/v51_visdrone_recovery/converted_annotations/fold_0_val.json`: `85d9be6763b70f1dc34f18fb997d832393e55cc99fe0e555e75b6358e07ef6bb`
- `runs/v51_visdrone_recovery/converted_annotations/fold_1_train.json`: `7e8f10c403f954614a1c6086ad179a686360f9aeb62f78dd02e3395799021c6e`
- `runs/v51_visdrone_recovery/converted_annotations/fold_1_val.json`: `6e51d6631a13b77d3cf174daa7ee6884f7cab8d830f379b6436dad7af1fc5f56`
- `runs/v51_visdrone_recovery/converted_annotations/fold_2_train.json`: `b1616c5d25e870b154df0202fd3c47623c0f23d44fb5ab6de7c7f5b668472648`
- `runs/v51_visdrone_recovery/converted_annotations/fold_2_val.json`: `a46977ff008d739c1375de1b6c585bfc18a7832c19fff46f28886d6d8a498118`
- `runs/v51_visdrone_recovery/cv_train_commands.txt`: `10f785a780b3cbe6711e6d51be6d9f81dd4623bd5c275dbc3a42ed8b962d3835`
- `runs/v51_visdrone_recovery/fold_integrity.md`: `336c4446d8eb7496f07b9cc0030a5cfd1cf9e5ade930424859a6f641fd4d588d`
- `runs/v51_visdrone_recovery/fold_manifest.json`: `288efd951c959c3b8ac9a4164de0e5b51fd22c73f9eae1ec6aa6d0c6189e75bc`
- `runs/v51_visdrone_recovery/folds/fold_0_train.txt`: `3340bd39061b5712bbaea195af48199d952674ed0b60fdaa3740729951d2baa7`
- `runs/v51_visdrone_recovery/folds/fold_0_val.txt`: `013f2e60c7b0f9f447a779f74b5c6f6da986aa03549ac71f01d3d5c6caa3d557`
- `runs/v51_visdrone_recovery/folds/fold_1_train.txt`: `6498ad58f57ad056fc6a84006bad426da816eccb2d12c48ed0d69f4c8a2708bb`
- `runs/v51_visdrone_recovery/folds/fold_1_val.txt`: `2ccf60b7f2e0729090af2f54b782e1763da94f4228464ccfd9c8b2eb6418fbd4`
- `runs/v51_visdrone_recovery/folds/fold_2_train.txt`: `91bccc7c1b12f1c6a3f011e3e0d28fc429d3f99c70f62ce00994cebeb3574259`
- `runs/v51_visdrone_recovery/folds/fold_2_val.txt`: `5c7f538eb57c4102e223f78c7badadb474878556e9630d09d20e638118dae2d0`
- `runs/v51_visdrone_recovery/recovery_audit.json`: `c28874592a057601587eec9a06969b83167ebf75513ea61c300e237a26b45425`
- `runs/v51_visdrone_recovery/route_decision.json`: `5885cb3f6701e10b8d831be822888467842ecd1ccc9d37154e752a1661376dbf`
