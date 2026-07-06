# V40 Label-Free Configuration Smoke

- Status: `PASS`
- This smoke reads manifests, hashes, source files, and command templates only.
- It does not read label txt files, image arrays, checkpoints, or predictions.

| Check | Observed | Expected | Status |
| --- | --- | --- | --- |
| gate0_status | `V40_V2_READY_FOR_FROZEN_RERUN` | `V40_V2_READY_FOR_FROZEN_RERUN` | `PASS` |
| gate0_training_started | `False` | `False` | `PASS` |
| gate0_evaluation_started | `False` | `False` | `PASS` |
| train_manifest_count | `7439` | `7439` | `PASS` |
| validation_manifest_count | `2213` | `2213` | `PASS` |
| manifest_overlap | `0` | `0` | `PASS` |
| run_matrix_count | `8` | `8` | `PASS` |
| dataset_root_recorded | `D:\download\triair` | `D:\download\triair` | `PASS` |
| python_for_future_commands_recorded | `C:\Users\xinnan\.conda\envs\pytorch\python.exe` | `existing path or <PYTORCH_PYTHON>` | `PASS` |
| command_excludes_v40_expanded_adjacency_component_split_v1 | `False` | `False` | `PASS` |
| command_excludes_v40_guard | `False` | `False` | `PASS` |
| command_excludes_finish_task.ps1 | `False` | `False` | `PASS` |
| command_excludes_eval_missing_modality | `False` | `False` | `PASS` |
| command_excludes_profile_ | `False` | `False` | `PASS` |
| command_excludes_DroneVehicle | `False` | `False` | `PASS` |
| source_lock_files_exist | `all_present` | `all_present` | `PASS` |
