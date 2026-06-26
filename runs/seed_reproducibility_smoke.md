# Seed Reproducibility Smoke Test

Overall: **pass**

## Checks

| Check | Result |
| --- | --- |
| same_seed_initial_state_identical | pass |
| different_seed_initial_state_differs | pass |
| same_seed_first_32_shuffle_identical | pass |
| different_seed_first_32_shuffle_differs | pass |
| config_and_log_record_seed | pass |
| early_param_count_unchanged | pass |
| reliability_param_count_unchanged | pass |
| legacy_unseeded_path_preserved | pass |
| train_count | pass |
| val_count | pass |
| guard_count | pass |
| exact_rgb_matched_val_images | pass |
| exact_rgb_matched_train_images | pass |
| exact_rgb_group_count | pass |
| id_guard_violations | pass |

## Initial Model SHA256

- seed 0 run A: `da255e0a1b35d59f68d83ad24c0895efeba1583fa1bc7c578b4de4164366c627`
- seed 0 run B: `da255e0a1b35d59f68d83ad24c0895efeba1583fa1bc7c578b4de4164366c627`
- seed 2: `f3237900ccc9e3347c7822be50ab89780f1db8f20c78171c20d36d0b29e2471b`

## First 32 Shuffled Training Indices

- seed 0 run A: `[7065, 5138, 3388, 2723, 4272, 434, 5115, 3214, 6552, 5042, 1505, 4165, 5564, 5628, 1617, 6375, 6001, 6725, 492, 252, 1267, 5238, 4074, 1429, 5058, 1478, 720, 2296, 1529, 5909, 3739, 2499]`
- seed 0 run B: `[7065, 5138, 3388, 2723, 4272, 434, 5115, 3214, 6552, 5042, 1505, 4165, 5564, 5628, 1617, 6375, 6001, 6725, 492, 252, 1267, 5238, 4074, 1429, 5058, 1478, 720, 2296, 1529, 5909, 3739, 2499]`
- seed 2: `[1573, 114, 5539, 5183, 6292, 152, 6061, 3338, 484, 3680, 1698, 3984, 3469, 3208, 2204, 2622, 7315, 6562, 4256, 5459, 3243, 1787, 5025, 4966, 2395, 7283, 3792, 1149, 1417, 2292, 4510, 3877]`

## Clean Split Integrity

- train list: `E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt`
- val list: `E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt`
- guard list: `E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_guard.txt`
- train/val/guard counts: 7439 / 2213 / 837
- exact RGB train/validation matches: 0
- same-family guard violations: 0
