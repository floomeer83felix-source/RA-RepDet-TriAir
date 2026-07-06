# V40 Experiment Contract Validation

- Status: `PASS`
- Generated: `2026-07-06T09:07:45`
- Input commit: `e338ef259b8df123de8b1a9ed8f1f750000cdbfc`
- Output commit: `PENDING_FINAL_COMMIT_RECORDED_IN_GIT_HISTORY_AND_FINAL_RESPONSE`
- Checks failed: `0` / `33`

| Check | Observed | Expected | Status |
| --- | --- | --- | --- |
| contract_status | `V40_EXPERIMENT_CONTRACT_PASS` | `V40_EXPERIMENT_CONTRACT_PASS` | `PASS` |
| status_report_status | `V40_EXPERIMENT_CONTRACT_PASS` | `V40_EXPERIMENT_CONTRACT_PASS` | `PASS` |
| gate0_status | `V40_V2_READY_FOR_FROZEN_RERUN` | `V40_V2_READY_FOR_FROZEN_RERUN` | `PASS` |
| label_free_smoke | `PASS` | `PASS` | `PASS` |
| model_forward_smoke | `PASS` | `PASS` | `PASS` |
| train_manifest_line_count | `7439` | `7439` | `PASS` |
| validation_manifest_line_count | `2213` | `2213` | `PASS` |
| contract_train_manifest_sha | `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f` | `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f` | `PASS` |
| contract_validation_manifest_sha | `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f` | `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f` | `PASS` |
| validation_gt_boxes | `5867` | `5867` | `PASS` |
| run_matrix_count | `8` | `8` | `PASS` |
| command_template_count | `8` | `8` | `PASS` |
| run_seeds | `0,2` | `0,2` | `PASS` |
| model_dropout_pairs | `[('early', '0.00'), ('reliability', '0.00'), ('reliability', '0.15'), ('reliability', '0.20')]` | `[('early', '0.00'), ('reliability', '0.00'), ('reliability', '0.15'), ('reliability', '0.20')]` | `PASS` |
| command_contains_reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_train.txt | `True` | `True` | `PASS` |
| command_contains_reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_val.txt | `True` | `True` | `PASS` |
| command_contains_--epochs 50 | `True` | `True` | `PASS` |
| command_contains_--batch-size 4 | `True` | `True` | `PASS` |
| command_contains_--img-size 640 | `True` | `True` | `PASS` |
| command_contains_--lr 1e-4 | `True` | `True` | `PASS` |
| command_contains_--detector-score-thr 0.001 | `True` | `True` | `PASS` |
| command_contains_--metric-score-thr 0.50 | `True` | `True` | `PASS` |
| command_contains_--nms-thresh 0.6 | `True` | `True` | `PASS` |
| command_contains_--detections-per-img 100 | `True` | `True` | `PASS` |
| command_excludes_v40_expanded_adjacency_component_split_v1 | `False` | `False` | `PASS` |
| command_excludes_v40_guard | `False` | `False` | `PASS` |
| command_excludes_finish_task.ps1 | `False` | `False` | `PASS` |
| command_excludes_eval_missing_modality | `False` | `False` | `PASS` |
| command_excludes_profile_ | `False` | `False` | `PASS` |
| command_excludes_DroneVehicle | `False` | `False` | `PASS` |
| source_hashes_current | `all_match` | `all_match` | `PASS` |
| master_plan_disallowed_phrases_absent | `none` | `none` | `PASS` |
| no_forbidden_work_started_or_changed | `{"dronevehicle_changed": true, "labels_changed": true, "manuscript_changed": true, "metric_evaluation_started": true, "model_or_training_core_changed": true, "profiling_started": true, "raw_data_changed": true, "robustness_started": true, "training_started": true}` | `all_true` | `PASS` |
