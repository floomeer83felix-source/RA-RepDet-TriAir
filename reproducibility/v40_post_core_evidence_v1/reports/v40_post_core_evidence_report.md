# V40 Post-Core Evidence Report

- Status: `V40_POST_CORE_EVIDENCE_COMPLETE`
- Readiness: `PRE_MANUSCRIPT_VALIDATION_ONLY_READY`
- No new training, tuning, p=0.00/p=0.20 run, manuscript work, external data, guard evaluation, DroneVehicle work, or finish_task.ps1 occurred.

## Channel Removal Aggregate

| model_group | condition | metric | mean | delta_from_all_modal_mean |
| --- | --- | --- | --- | --- |
| matched_early | all_modal | precision | 0.9187693819194747 | 0.0 |
| matched_early | all_modal | recall | 0.8719959093233338 | 0.0 |
| matched_early | all_modal | f1 | 0.8944584358717531 | 0.0 |
| matched_early | all_modal | ap50 | 0.9408408999443054 | 0.0 |
| matched_early | all_modal | ap75 | 0.8207659125328064 | 0.0 |
| matched_early | rgb_removed | precision | 0.8201992199541255 | -0.09857016196534918 |
| matched_early | rgb_removed | recall | 0.6531447076870632 | -0.2188512016362706 |
| matched_early | rgb_removed | f1 | 0.7269142808945528 | -0.16754415497720032 |
| matched_early | rgb_removed | ap50 | 0.7378746867179871 | -0.20296621322631836 |
| matched_early | rgb_removed | ap75 | 0.5265026688575745 | -0.29426324367523193 |
| matched_early | thermal_removed | precision | 0.8225959044160284 | -0.09617347750344629 |
| matched_early | thermal_removed | recall | 0.30032384523606614 | -0.5716720640872677 |
| matched_early | thermal_removed | f1 | 0.4399902923605564 | -0.4544681435111967 |
| matched_early | thermal_removed | ap50 | 0.3648492246866226 | -0.5759916752576828 |
| matched_early | thermal_removed | ap75 | 0.26256974786520004 | -0.5581961646676064 |
| matched_early | event_removed | precision | 0.9000886764912421 | -0.018680705428232525 |
| matched_early | event_removed | recall | 0.8731038009204022 | 0.0011078915970683667 |
| matched_early | event_removed | f1 | 0.8862980533853604 | -0.008160382486392725 |
| matched_early | event_removed | ap50 | 0.9338785707950592 | -0.006962329149246216 |
| matched_early | event_removed | ap75 | 0.8020583689212799 | -0.01870754361152649 |
| reliability_p015 | all_modal | precision | 0.9273281114012184 | 0.0 |
| reliability_p015 | all_modal | recall | 0.8996931992500425 | 0.0 |
| reliability_p015 | all_modal | f1 | 0.9132822400096081 | 0.0 |
| reliability_p015 | all_modal | ap50 | 0.958569347858429 | 0.0 |
| reliability_p015 | all_modal | ap75 | 0.8759667277336121 | 0.0 |
| reliability_p015 | rgb_removed | precision | 0.8568867017190755 | -0.07044140968214285 |
| reliability_p015 | rgb_removed | recall | 0.8229077893301517 | -0.0767854099198908 |
| reliability_p015 | rgb_removed | f1 | 0.8394060693814127 | -0.0738761706281954 |
| reliability_p015 | rgb_removed | ap50 | 0.8984862864017487 | -0.0600830614566803 |
| reliability_p015 | rgb_removed | ap75 | 0.7051162719726562 | -0.1708504557609558 |
| reliability_p015 | thermal_removed | precision | 0.8320588113940757 | -0.09526930000714273 |
| reliability_p015 | thermal_removed | recall | 0.5884608829043805 | -0.31123231634566206 |
| reliability_p015 | thermal_removed | f1 | 0.6893521377211514 | -0.22393010228845667 |
| reliability_p015 | thermal_removed | ap50 | 0.7030294239521027 | -0.2555399239063263 |
| reliability_p015 | thermal_removed | ap75 | 0.3883095979690552 | -0.4876571297645569 |
| reliability_p015 | event_removed | precision | 0.930546441516446 | 0.0032183301152276522 |
| reliability_p015 | event_removed | recall | 0.8969660814726437 | -0.0027271177773988686 |
| reliability_p015 | event_removed | f1 | 0.9134402048100072 | 0.00015796480039909078 |
| reliability_p015 | event_removed | ap50 | 0.958166241645813 | -0.0004031062126159668 |
| reliability_p015 | event_removed | ap75 | 0.8600485026836395 | -0.015918225049972534 |

## Efficiency Summary

| run_id | model_group | path | latency_ms_median | fps_median | params | cuda_peak_memory_mb_max | gflops |
| --- | --- | --- | --- | --- | --- | --- | --- |
| matched_early_seed0 | matched_early | raw_forward | 10.45661629999995 | 95.63323079952782 | 6591609 | 199.71142578125 | 24.442939392 |
| matched_early_seed0 | matched_early | detector_inference | 22.8088679 | 43.84259685242862 | 6591609 | 207.52392578125 | 105.207355392 |
| matched_early_seed2 | matched_early | raw_forward | 10.400834600000053 | 96.14613042687891 | 6591609 | 222.42138671875 | 24.442939392 |
| matched_early_seed2 | matched_early | detector_inference | 22.972324800000024 | 43.53063996378803 | 6591609 | 229.64013671875 | 105.207355392 |
| reliability_p015_seed0 | reliability_p015 | raw_forward | 10.66540380000015 | 93.76110072831804 | 6593293 | 354.642578125 | 25.217085024 |
| reliability_p015_seed0 | reliability_p015 | detector_inference | 23.04108810000002 | 43.400728110579074 | 6593293 | 361.673828125 | 105.981501024 |
| reliability_p015_seed2 | reliability_p015 | raw_forward | 10.551875900000141 | 94.76987878524866 | 6593293 | 374.9306640625 | 25.217085024 |
| reliability_p015_seed2 | reliability_p015 | detector_inference | 23.55685339999991 | 42.45049128675241 | 6593293 | 382.7431640625 | 105.981501024 |

## Bootstrap CI Summary

| comparison | metric | resamples | bootstrap_seed | resampling_unit | mean_difference | median_difference | ci95_low_percentile | ci95_high_percentile | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reliability_p015_minus_matched_early | ap50 | 2000 | 20260707 | V40 validation image | 0.017728451787788167 | 0.017707346904498544 | 0.015256388005846302 | 0.020347639975607523 | descriptive uncertainty evidence only; not used for model selection |
| reliability_p015_minus_matched_early | ap75 | 2000 | 20260707 | V40 validation image | 0.05531997401242881 | 0.055327848153059744 | 0.048323405159029074 | 0.06222237985849988 | descriptive uncertainty evidence only; not used for model selection |
| reliability_p015_minus_matched_early | f1 | 2000 | 20260707 | V40 validation image | 0.018736217762584575 | 0.018710963262967506 | 0.014979827442707127 | 0.022624657627203396 | descriptive uncertainty evidence only; not used for model selection |

## Qualitative Assets

| selection_rank | sample_id | asset_path | asset_sha256 |
| --- | --- | --- | --- |
| 1 | nframe_07725 | reproducibility/v40_post_core_evidence_v1/qualitative/review_assets/v40_qualitative_01_nframe_07725.png | e1c889c05fdba509ef79beab00f705512f65ea85a3316e107db7f4ad6afa887b |
| 2 | nframe_07435 | reproducibility/v40_post_core_evidence_v1/qualitative/review_assets/v40_qualitative_02_nframe_07435.png | 9ade3ab3c54c142f416e0e527ecff964df55d4af7df3de5a2b8c39c29a6f619e |
| 3 | nframe_07948 | reproducibility/v40_post_core_evidence_v1/qualitative/review_assets/v40_qualitative_03_nframe_07948.png | 96bad7535a77524a7a595ebe86d6cac0a5537c926330c8bbb26f59daed67b841 |
| 4 | nframe_03921 | reproducibility/v40_post_core_evidence_v1/qualitative/review_assets/v40_qualitative_04_nframe_03921.png | 3c32fc9480470e293a89c29dcc069e90df9a53cc11574c0a91145972909d0469 |
| 5 | nframe_01208 | reproducibility/v40_post_core_evidence_v1/qualitative/review_assets/v40_qualitative_05_nframe_01208.png | 603e681ee66aa168fc668453aa59f5173bdfa6f79da59606a6f74909c78eb9ab |
| 6 | nframe_07440 | reproducibility/v40_post_core_evidence_v1/qualitative/review_assets/v40_qualitative_06_nframe_07440.png | 76e137231d28571105cde50752b8e8253fca7bd0313526526f2637be9e4a9d79 |
| 7 | frame_02259 | reproducibility/v40_post_core_evidence_v1/qualitative/review_assets/v40_qualitative_07_frame_02259.png | 2c4dd6a6732b26624e613938378b308a4a7938b6384fdfbaeea31d5cbe4092cf |
| 8 | frame_02296 | reproducibility/v40_post_core_evidence_v1/qualitative/review_assets/v40_qualitative_08_frame_02296.png | 6ffbb2f5636a8825023306545dc0b797f31dfac4570f0ea1f0d2bb5d96ff8b3f |
