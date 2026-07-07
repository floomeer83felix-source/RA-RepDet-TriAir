# V40 Component-Disjoint Split Audit

Final component-disjoint gate: **PASS**

Data root: `D:\download\triair`
Guard distance: `16`

## Summary Metrics

| metric | value | status | notes |
| --- | --- | --- | --- |
| complete_inventory_count | 10489 | info | All discovered local .npy image samples. |
| unique_inventory_paths | 10489 | pass | Unique relative paths in local inventory. |
| assigned_total_rows | 10489 | info | Rows across train, validation, and guard split files. |
| assigned_unique_paths | 10489 | info | Unique assigned relative paths. |
| missing_inventory_paths | 0 | pass | Local inventory paths absent from all split files. |
| unknown_assigned_paths | 0 | pass | Split rows not present in local inventory. |
| duplicate_assigned_paths | 0 | pass | Paths assigned more than once across all partitions. |
| component_count | 45 | info | Transitive component count in full inventory. |
| largest_component_size | 4077 | info | Largest connected component size. |
| train_sha256 | 5fc7b1b2cab42e1ab7411d13e3fcfd7e19d61eb009b1900701b023d74e8fb303 | info | SHA256 of split text entries. |
| val_sha256 | 2903f4747031386f4ee7f45a87a369e20f7cd11a8a9033f930971a5b6656788b | info | SHA256 of split text entries. |
| guard_sha256 | 9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e | info | SHA256 of split text entries. |
| deterministic_rerun_consistency | pass | pass | manifest hashes match actual split files and builder rerun consistency is true |
| train_rows | 7439 | info | Split rows. |
| train_gt_boxes | 23011 | info | Total label rows/boxes. |
| train_images_with_gt | 6701 | info | Images with at least one label row. |
| train_empty_target_images | 738 | info | Images with zero label rows, including missing label files. |
| val_rows | 2213 | info | Split rows. |
| val_gt_boxes | 6359 | info | Total label rows/boxes. |
| val_images_with_gt | 2212 | info | Images with at least one label row. |
| val_empty_target_images | 1 | info | Images with zero label rows, including missing label files. |
| guard_rows | 837 | info | Split rows. |
| guard_gt_boxes | 1264 | info | Total label rows/boxes. |
| guard_images_with_gt | 837 | info | Images with at least one label row. |
| guard_empty_target_images | 0 | info | Images with zero label rows, including missing label files. |
| train_val_path_overlap | 0 | pass | Identical relative paths across partitions. |
| train_val_exact_rgb_overlap_groups | 0 | pass | Unique exact RGB-content SHA256 groups shared across partitions. |
| train_val_same_family_distance_16_violation_pairs | 0 | pass | Cross-partition same-family ID pairs inside the guard distance. |
| train_val_same_family_distance_16_violating_records | 0 | pass | Records in the second partition with at least one nearby record in the first partition. |
| train_val_min_same_family_id_distance | 17 | pass | Minimum cross-partition same-family numeric ID distance. |
| train_guard_path_overlap | 0 | pass | Identical relative paths across partitions. |
| train_guard_exact_rgb_overlap_groups | 0 | pass | Unique exact RGB-content SHA256 groups shared across partitions. |
| train_guard_same_family_distance_16_violation_pairs | 0 | pass | Cross-partition same-family ID pairs inside the guard distance. |
| train_guard_same_family_distance_16_violating_records | 0 | pass | Records in the second partition with at least one nearby record in the first partition. |
| train_guard_min_same_family_id_distance | 17 | pass | Minimum cross-partition same-family numeric ID distance. |
| val_guard_path_overlap | 0 | pass | Identical relative paths across partitions. |
| val_guard_exact_rgb_overlap_groups | 0 | pass | Unique exact RGB-content SHA256 groups shared across partitions. |
| val_guard_same_family_distance_16_violation_pairs | 0 | pass | Cross-partition same-family ID pairs inside the guard distance. |
| val_guard_same_family_distance_16_violating_records | 0 | pass | Records in the second partition with at least one nearby record in the first partition. |
| val_guard_min_same_family_id_distance | 17 | pass | Minimum cross-partition same-family numeric ID distance. |
| assigned_paths_missing_component_id | 0 | pass | Assigned paths that could not be mapped to a rebuilt component. |
| component_crossing_count | 0 | pass | No connected component crosses partitions. |
| final_component_disjoint_gate | PASS | pass | Hard continuation gate for V40 GPU work. |

## Gate Interpretation

- PASS means all local samples are assigned exactly once, no path/exact-RGB/same-family guard-band leakage crosses partitions, components do not cross partitions, and deterministic builder hashes match the audited split files.
- FAIL means V40 must stop before GPU training and report this blocked state.
