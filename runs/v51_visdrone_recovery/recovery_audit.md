# V51 Recovery Audit

Generated: `2026-07-13T21:10:42+08:00`
Starting commit: `520443266fb1a917e50acfbd09772b4d74f6bb00`

- All frozen V50 source-lock and protocol-evidence hashes match.
- No V50 queue or RGB training process is alive.
- Exact per-file hashes are stored in `candidate_image_hashes.json` and `candidate_annotation_hashes.json`.
- The local `seen` and `seen_strict` directories are copied/filtered derivatives of the same DET train/val/test-dev source used in V50.
- DAPA/object/reference directories are locally documented derivatives, not untouched evaluation partitions.
- The UAVDT directory is a separate dataset remapped to VisDrone class names, not a VisDrone-family partition.

| Candidate | Images | Exact V50 overlap | ID overlap | Route A |
|---|---:|---:|---:|---|
| visdrone_det_train | 6471 | 6471 | 6471 | no |
| visdrone_det_val | 548 | 548 | 548 | no |
| visdrone_det_test_dev | 1610 | 1610 | 1610 | no |
| visdrone_seen | 8629 | 8629 | 8629 | no |
| visdrone_seen_strict | 4072 | 4072 | 4072 | no |
| visdrone_object | 7019 | None | 7019 | no |
| visdrone_prompt_bank | 40 | None | 0 | no |
| visdrone_tvpa_refer_banks | 1275 | None | 1275 | no |
| uavdt_visdrone_mapping | 40423 | None | 0 | no |
| visdrone_dapa_st_dapa_only | 6471 | None | 6471 | no |
| visdrone_dapa_st_object_pg_hybrid | 6471 | None | 6471 | no |
| visdrone_dapa_st_pg_hybrid | 6471 | None | 6471 | no |
| visdrone_dapa_st_pg_loose | 6471 | None | 6471 | no |
| visdrone_dapa_st_pg_strict | 6471 | None | 6471 | no |
| visdrone_dapa_st_proposal_guided | 6471 | None | 6471 | no |
