# V40 Compute-Minimized Contract Validation

- Status: `PASS`
- Amendment status: `V40_COMPUTE_MINIMIZED_CONTRACT_READY`
- Input commit: `d463914f5b7df77d9624f574e01c54f75b38b83d`
- Output commit: `PENDING_FINAL_COMMIT_RECORDED_IN_GIT_HISTORY_AND_FINAL_RESPONSE`
- Checks failed: `0` / `56`

| Check | Observed | Expected | Status |
| --- | --- | --- | --- |
| amendment_status | `V40_COMPUTE_MINIMIZED_CONTRACT_READY` | `V40_COMPUTE_MINIMIZED_CONTRACT_READY` | `PASS` |
| status_report_status | `V40_COMPUTE_MINIMIZED_CONTRACT_READY` | `V40_COMPUTE_MINIMIZED_CONTRACT_READY` | `PASS` |
| original_contract_preserved_as_archival | `archival evidence` | `archival evidence` | `PASS` |
| run_count | `4` | `4` | `PASS` |
| exact_run_ids | `matched_early_seed0,matched_early_seed2,reliability_p015_seed0,reliability_p015_seed2` | `matched_early_seed0,matched_early_seed2,reliability_p015_seed0,reliability_p015_seed2` | `PASS` |
| seeds | `0,2` | `0,2` | `PASS` |
| model_dropout_scope | `[('early', '0.00'), ('reliability', '0.15')]` | `[('early', '0.00'), ('reliability', '0.15')]` | `PASS` |
| command_template_count | `4` | `4` | `PASS` |
| train_manifest_hash_matches_original | `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f` | `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f` | `PASS` |
| validation_manifest_hash_matches_original | `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f` | `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f` | `PASS` |
| train_manifest_count | `7439` | `7439` | `PASS` |
| validation_manifest_count | `2213` | `2213` | `PASS` |
| evaluator_hash_matches_original | `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715` | `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715` | `PASS` |
| trainer_hash_matches_original | `d9cae1e22e41ad0c7cfab13bf83ac058b5335cd1fcc41e3da9b1f8c53d05167a` | `d9cae1e22e41ad0c7cfab13bf83ac058b5335cd1fcc41e3da9b1f8c53d05167a` | `PASS` |
| matched_early_seed0_epochs | `50` | `50` | `PASS` |
| matched_early_seed0_img_size | `640` | `640` | `PASS` |
| matched_early_seed0_batch_size | `4` | `4` | `PASS` |
| matched_early_seed0_train_manifest | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt` | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt` | `PASS` |
| matched_early_seed0_validation_manifest | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt` | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt` | `PASS` |
| matched_early_seed2_epochs | `50` | `50` | `PASS` |
| matched_early_seed2_img_size | `640` | `640` | `PASS` |
| matched_early_seed2_batch_size | `4` | `4` | `PASS` |
| matched_early_seed2_train_manifest | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt` | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt` | `PASS` |
| matched_early_seed2_validation_manifest | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt` | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt` | `PASS` |
| reliability_p015_seed0_epochs | `50` | `50` | `PASS` |
| reliability_p015_seed0_img_size | `640` | `640` | `PASS` |
| reliability_p015_seed0_batch_size | `4` | `4` | `PASS` |
| reliability_p015_seed0_train_manifest | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt` | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt` | `PASS` |
| reliability_p015_seed0_validation_manifest | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt` | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt` | `PASS` |
| reliability_p015_seed2_epochs | `50` | `50` | `PASS` |
| reliability_p015_seed2_img_size | `640` | `640` | `PASS` |
| reliability_p015_seed2_batch_size | `4` | `4` | `PASS` |
| reliability_p015_seed2_train_manifest | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt` | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt` | `PASS` |
| reliability_p015_seed2_validation_manifest | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt` | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt` | `PASS` |
| commands_contain_--epochs 50 | `True` | `True` | `PASS` |
| commands_contain_--batch-size 4 | `True` | `True` | `PASS` |
| commands_contain_--img-size 640 | `True` | `True` | `PASS` |
| commands_contain_--lr 1e-4 | `True` | `True` | `PASS` |
| commands_contain_--detector-score-thr 0.001 | `True` | `True` | `PASS` |
| commands_contain_--metric-score-thr 0.50 | `True` | `True` | `PASS` |
| commands_contain_--nms-thresh 0.6 | `True` | `True` | `PASS` |
| commands_contain_--detections-per-img 100 | `True` | `True` | `PASS` |
| commands_contain_runs/v40_expanded_adjacency_v2_compute_minimized | `True` | `True` | `PASS` |
| commands_exclude_reliability_p000 | `False` | `False` | `PASS` |
| commands_exclude_reliability_p020 | `False` | `False` | `PASS` |
| commands_exclude_p=0.00 | `False` | `False` | `PASS` |
| commands_exclude_p=0.20 | `False` | `False` | `PASS` |
| commands_exclude_runs/v40_expanded_adjacency/ | `False` | `False` | `PASS` |
| commands_exclude_eval_missing_modality | `False` | `False` | `PASS` |
| commands_exclude_profile_ | `False` | `False` | `PASS` |
| commands_exclude_DroneVehicle | `False` | `False` | `PASS` |
| commands_exclude_finish_task.ps1 | `False` | `False` | `PASS` |
| source_lock_hashes_current | `all_match` | `all_match` | `PASS` |
| no_forbidden_work_flags_false | `{"checkpoint_created": false, "dronevehicle_changed": false, "external_data_used": false, "loss_or_validation_iteration_run": false, "manuscript_changed": false, "metric_evaluation_started": false, "profiling_started": false, "qualitative_started": false, "result_recorded": false, "robustness_started": false, "training_started": false}` | `all_false` | `PASS` |
| planned_output_root_has_no_artifacts | `none` | `none` | `PASS` |
| master_plan_disallowed_phrases_absent | `none` | `none` | `PASS` |
