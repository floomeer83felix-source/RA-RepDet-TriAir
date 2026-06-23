# RGB Cross-Split Duplicate Summary

Interpretation: **CONFIRMED RGB-CONTENT CROSS-SPLIT DUPLICATION**

This audit hashes only the first three RGB channels from each `.npy` sample. It does not claim full five-channel multimodal byte duplication.

## Metrics

| Metric | Value | Notes |
| --- | --- | --- |
| interpretation_label | CONFIRMED RGB-CONTENT CROSS-SPLIT DUPLICATION | Exact required Phase 3C label. |
| train_images | 8391 | Existing train split rows. |
| val_images | 2098 | Existing validation split rows. |
| exact_rgb_matched_val_images | 153 | Validation samples with at least one train sample sharing exact RGB content. |
| exact_rgb_matched_val_fraction | 0.072927 | Matched validation fraction. |
| exact_rgb_matched_train_images | 153 | Train samples with at least one validation sample sharing exact RGB content. |
| exact_rgb_matched_train_fraction | 0.018234 | Matched train fraction. |
| cross_split_rgb_groups | 153 | Distinct RGB-content hashes present in both splits. |
| group_total_size_min | 2 | Train+val samples per matched group. |
| group_total_size_p50 | 2 | Train+val samples per matched group. |
| group_total_size_max | 2 | Train+val samples per matched group. |
| group_val_size_p50 | 1 | Validation samples per matched group. |
| groups_identical_gt_box_counts | 123 | All records in the RGB group have one GT-box count. |
| groups_different_gt_box_counts | 30 | RGB group contains more than one GT-box count. |
| pair_id_distance_min | 1 | Representative exact RGB pairs, same filename family only. |
| pair_id_distance_p50 | 1 | Representative exact RGB pairs, same filename family only. |
| pair_id_distance_p90 | 1 | Representative exact RGB pairs, same filename family only. |
| train_gt_boxes | 24560 | Non-empty label rows in train split. |
| val_gt_boxes | 6074 | Non-empty label rows in validation split. |
| full_multimodal_byte_duplication_claim | not_claimed | This audit only hashes RGB channels; full 5-channel byte equality is not implied. |

## Representative Exact RGB Pairs

The CSV contains representative cross-split pairs from matched RGB-content groups, including direct RGB MAE and 256-bit signature distance checks.

| rank | rgb_sha256 | val_path | train_path | val_family | train_family | val_id | train_id | id_distance | rgb_sha256_equal | signature_distance | direct_rgb_mae | val_gt_boxes | train_gt_boxes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 01269e0f77a6be3f63cd189ffbc93f3a6dd8efd3fa25095557be7d28d09dcafa | data/images/nframe_07236.npy | data/images/nframe_07235.npy | nframe | nframe | 7236 | 7235 | 1 | True | 0 | 0.000000 | 2 | 2 |
| 2 | 035a51ea352069b2b31c749453f84f0ec64b4b21a576bb28a126daea291b7e4e | data/images/nframe_09819.npy | data/images/nframe_09820.npy | nframe | nframe | 9819 | 9820 | 1 | True | 0 | 0.000000 | 2 | 2 |
| 3 | 04b1c7cfc92c7f17ccfab326505e955cd06ea94aa85b68d4b0c50aa66490c17b | data/images/nframe_02176.npy | data/images/nframe_02175.npy | nframe | nframe | 2176 | 2175 | 1 | True | 0 | 0.000000 | 5 | 5 |
| 4 | 0874d6acdf7cb96d539434b815422a079d928679e9db74a44d91229d9fc341fb | data/images/nframe_01439.npy | data/images/nframe_01438.npy | nframe | nframe | 1439 | 1438 | 1 | True | 0 | 0.000000 | 11 | 11 |
| 5 | 0dabe5217b6f50596eb01ae4c271a71cbe28367c39e68f8a213ed162f42dc031 | data/images/nframe_05529.npy | data/images/nframe_05530.npy | nframe | nframe | 5529 | 5530 | 1 | True | 0 | 0.000000 | 2 | 3 |
| 6 | 0dc9ad35920fbd0bdee9f9cf32bb44c8c4b93f1a9ad603055d7845af7d240c70 | data/images/nframe_07545.npy | data/images/nframe_07546.npy | nframe | nframe | 7545 | 7546 | 1 | True | 0 | 0.000000 | 2 | 2 |
| 7 | 109d65387c3e45695c4e64e5314f9396fadb072d88307f5a7b49e8bb2a789ec6 | data/images/nframe_01872.npy | data/images/nframe_01871.npy | nframe | nframe | 1872 | 1871 | 1 | True | 0 | 0.000000 | 4 | 3 |
| 8 | 11adfb41edc2e1bb92611895109c7f74334bf990be92ebfe9f5c0d7864304407 | data/images/nframe_07720.npy | data/images/nframe_07719.npy | nframe | nframe | 7720 | 7719 | 1 | True | 0 | 0.000000 | 3 | 3 |
| 9 | 14aaae4e46849d33cd5aa0358732f221ca6e97a210d0a247fc0b8c35f4a9027e | data/images/nframe_01730.npy | data/images/nframe_01729.npy | nframe | nframe | 1730 | 1729 | 1 | True | 0 | 0.000000 | 7 | 7 |
| 10 | 16386465564ae856a5d3fdf556fef609ae3641f64b88a1033ca8be7d604721d9 | data/images/nframe_07425.npy | data/images/nframe_07424.npy | nframe | nframe | 7425 | 7424 | 1 | True | 0 | 0.000000 | 4 | 4 |
| 11 | 17c3224eea202b979c88e0b67d81212e9c8bba44986697757e84bf16a6a94ba6 | data/images/nframe_07824.npy | data/images/nframe_07823.npy | nframe | nframe | 7824 | 7823 | 1 | True | 0 | 0.000000 | 2 | 2 |
| 12 | 1852dfda2e2051d4245ba354ef43fc2cc151d35702c4d5187d3919edeeb13912 | data/images/nframe_07448.npy | data/images/nframe_07447.npy | nframe | nframe | 7448 | 7447 | 1 | True | 0 | 0.000000 | 4 | 5 |
| 13 | 19f8756cf70ca367c24f3128f2259ebc1b400e8466284dda21ee2bc87524d725 | data/images/nframe_08675.npy | data/images/nframe_08674.npy | nframe | nframe | 8675 | 8674 | 1 | True | 0 | 0.000000 | 4 | 4 |
| 14 | 19f9a973f0ea7a841408b0d84eefe35187cb5d07fe069894784462ce7a2dbb63 | data/images/nframe_03317.npy | data/images/nframe_03318.npy | nframe | nframe | 3317 | 3318 | 1 | True | 0 | 0.000000 | 2 | 2 |
| 15 | 1a8de6f722b7932548d9adc83020807b4fb5f40f59000c3911e4c99a23f57c02 | data/images/nframe_03517.npy | data/images/nframe_03518.npy | nframe | nframe | 3517 | 3518 | 1 | True | 0 | 0.000000 | 1 | 1 |
| 16 | 1ac57c397d2ae04600fb2d07ed9f880975d44c08212ba669b9db1f954fdf8ba0 | data/images/nframe_05096.npy | data/images/nframe_05097.npy | nframe | nframe | 5096 | 5097 | 1 | True | 0 | 0.000000 | 1 | 1 |
| 17 | 1b0b109744a072a9fa7bc339fde127c6d9c4c187f130c2191685363c72c4cb4e | data/images/nframe_05337.npy | data/images/nframe_05338.npy | nframe | nframe | 5337 | 5338 | 1 | True | 0 | 0.000000 | 2 | 2 |
| 18 | 1c2a7c754dd1003c17dbcaa6dd01d8f093feaac388145c1786a6581be9aa382a | data/images/nframe_03372.npy | data/images/nframe_03373.npy | nframe | nframe | 3372 | 3373 | 1 | True | 0 | 0.000000 | 2 | 2 |
| 19 | 1eae6cdf205f03efb225f5bb9a585639a382d2a09fec5b0a03ddad32c17a0b37 | data/images/nframe_02851.npy | data/images/nframe_02850.npy | nframe | nframe | 2851 | 2850 | 1 | True | 0 | 0.000000 | 2 | 2 |
| 20 | 1fd7e3d4fae2f3804f715ede2dd4d9b5b92dcd8a6c465653cdf4fd98fdb25af8 | data/images/nframe_08691.npy | data/images/nframe_08690.npy | nframe | nframe | 8691 | 8690 | 1 | True | 0 | 0.000000 | 3 | 3 |
| 21 | 20424760c08a6a6782ea3b0674ab94a8b1eef87dea8aae9c6f885c90b1df93b8 | data/images/nframe_07756.npy | data/images/nframe_07755.npy | nframe | nframe | 7756 | 7755 | 1 | True | 0 | 0.000000 | 2 | 2 |
| 22 | 207225a57aff3bf907a8253b0493de9ff0fde8500af4d13ab8d54ef0342b41f0 | data/images/nframe_03918.npy | data/images/nframe_03917.npy | nframe | nframe | 3918 | 3917 | 1 | True | 0 | 0.000000 | 5 | 5 |
| 23 | 2084a5883cdcf300ca2199fff5742904bcd344aeec2c9d38d694a0bcb46c48f6 | data/images/nframe_01347.npy | data/images/nframe_01348.npy | nframe | nframe | 1347 | 1348 | 1 | True | 0 | 0.000000 | 7 | 7 |
| 24 | 22b9937c87015d8b95d4147e242534a823bf6fc647e1c4ddd037974d36b51290 | data/images/nframe_09054.npy | data/images/nframe_09053.npy | nframe | nframe | 9054 | 9053 | 1 | True | 0 | 0.000000 | 1 | 1 |
| 25 | 26d356754800c1d321dd7b32d37429d517b8c2782a1daf776fb56a3b68cdf346 | data/images/nframe_02548.npy | data/images/nframe_02549.npy | nframe | nframe | 2548 | 2549 | 1 | True | 0 | 0.000000 | 6 | 6 |
| 26 | 28552311b6218df4666afc77263997d9cb9f668ee03dd0f34e045a2186a2f13e | data/images/nframe_09255.npy | data/images/nframe_09254.npy | nframe | nframe | 9255 | 9254 | 1 | True | 0 | 0.000000 | 1 | 1 |
| 27 | 2b1ceba8812dd9243bb462363be82308b049cde917bca537e098bb367576488a | data/images/nframe_07410.npy | data/images/nframe_07409.npy | nframe | nframe | 7410 | 7409 | 1 | True | 0 | 0.000000 | 3 | 3 |
| 28 | 2c487ad642fba2dc9ba6438e7ecd68b94dbb0d72f9f439126674ecae58bdcc33 | data/images/nframe_00749.npy | data/images/nframe_00748.npy | nframe | nframe | 749 | 748 | 1 | True | 0 | 0.000000 | 1 | 1 |
| 29 | 31f224f5f49639f4251dc8210e0567ad897f63ff38bd66f501264302d5881cc0 | data/images/nframe_02022.npy | data/images/nframe_02023.npy | nframe | nframe | 2022 | 2023 | 1 | True | 0 | 0.000000 | 4 | 3 |
| 30 | 35b48f05e432a11b07e655bb16370ecafb216cc38c4538c6a5684f82bfaa8ca3 | data/images/nframe_04326.npy | data/images/nframe_04325.npy | nframe | nframe | 4326 | 4325 | 1 | True | 0 | 0.000000 | 1 | 1 |
