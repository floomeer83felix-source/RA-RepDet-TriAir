# Phase 2A Report

Scope: post-processing only. E0/E1/E2 were not retrained, and detector/Dataset source files were not modified.

## Paper Main Results At Score Threshold 0.50

| Method | Threshold | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.50 | 0.929133 | 0.954067 | 0.941434 | 0.976620 | 0.928824 | 6074 | 6237 | 0.769583 |
| E1 Reliability Fusion | 0.50 | 0.925721 | 0.962298 | 0.943655 | 0.979317 | 0.947634 | 6074 | 6314 | 0.794935 |
| E2 Reliability + Dropout 0.15 | 0.50 | 0.931057 | 0.956042 | 0.943384 | 0.979990 | 0.950906 | 6074 | 6237 | 0.788404 |

## E0 Phase 2A Profile

| Model | Path | Batch Size | Img Size | Warmup | Iters | Repeats | Params | Trainable Params | FPS mean | FPS std | Latency ms/img mean | Latency ms/img std | CUDA Memory MB mean | CUDA Memory MB std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | raw_forward | 1 | 640 | 100 | 300 | 3 | 6591609 | 6591609 | 119.223563 | 2.346034 | 8.390822 | 0.163564 | 115.153333 | 0.400694 |
| early | detector_inference | 1 | 640 | 100 | 300 | 3 | 6591609 | 6591609 | 59.018778 | 0.009687 | 16.943760 | 0.002781 | 122.680000 | 0.000000 |

## E2 Phase 2A Profile

| Model | Path | Batch Size | Img Size | Warmup | Iters | Repeats | Params | Trainable Params | FPS mean | FPS std | Latency ms/img mean | Latency ms/img std | CUDA Memory MB mean | CUDA Memory MB std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reliability | raw_forward | 1 | 640 | 100 | 300 | 3 | 6593293 | 6593293 | 116.372946 | 1.680733 | 8.594858 | 0.124329 | 228.006667 | 0.004714 |
| reliability | detector_inference | 1 | 640 | 100 | 300 | 3 | 6593293 | 6593293 | 57.986395 | 0.291187 | 17.245861 | 0.086910 | 235.820000 | 0.000000 |

## Brightness-Proxy Grouped Evaluation

| Method | Group | Images | Brightness min | Brightness max | Brightness mean | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | brightness_low | 699 | 0.011780 | 0.082704 | 0.043748 | 0.942651 | 0.953998 | 0.948291 | 0.976407 | 0.911437 | 2326 | 2354 | 0.757747 |
| E0 Early Fusion | brightness_mid | 699 | 0.082919 | 0.442995 | 0.180875 | 0.908850 | 0.947514 | 0.927779 | 0.969213 | 0.924137 | 1810 | 1887 | 0.766367 |
| E0 Early Fusion | brightness_high | 700 | 0.442999 | 0.580126 | 0.497964 | 0.932365 | 0.960268 | 0.946111 | 0.984799 | 0.954131 | 1938 | 1996 | 0.786583 |
| E1 Reliability Fusion | brightness_low | 699 | 0.011780 | 0.082704 | 0.043748 | 0.920825 | 0.960017 | 0.940013 | 0.976550 | 0.924397 | 2326 | 2425 | 0.784853 |
| E1 Reliability Fusion | brightness_mid | 699 | 0.082919 | 0.442995 | 0.180875 | 0.910667 | 0.957459 | 0.933477 | 0.972411 | 0.951071 | 1810 | 1903 | 0.795425 |
| E1 Reliability Fusion | brightness_high | 700 | 0.442999 | 0.580126 | 0.497964 | 0.946123 | 0.969556 | 0.957696 | 0.989167 | 0.972201 | 1938 | 1986 | 0.806775 |
| E2 Reliability + Dropout 0.15 | brightness_low | 699 | 0.011780 | 0.082704 | 0.043748 | 0.938637 | 0.953568 | 0.946044 | 0.977633 | 0.933410 | 2326 | 2363 | 0.772085 |
| E2 Reliability + Dropout 0.15 | brightness_mid | 699 | 0.082919 | 0.442995 | 0.180875 | 0.917515 | 0.946409 | 0.931738 | 0.975794 | 0.953568 | 1810 | 1867 | 0.788439 |
| E2 Reliability + Dropout 0.15 | brightness_high | 700 | 0.442999 | 0.580126 | 0.497964 | 0.934728 | 0.968008 | 0.951077 | 0.987845 | 0.969801 | 1938 | 2007 | 0.807586 |

## Reliability Alpha Statistics

| Method | Mode | Samples | alpha_rgb_mean | alpha_rgb_std | alpha_thermal_mean | alpha_thermal_std | alpha_event_mean | alpha_event_std | dominant_rgb | dominant_thermal | dominant_event | dominant_rgb_ratio | dominant_thermal_ratio | dominant_event_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 Reliability Fusion | full | 2098 | 0.384446 | 0.318534 | 0.430405 | 0.307492 | 0.185149 | 0.019713 | 829 | 1269 | 0 | 0.395138 | 0.604862 | 0.000000 |
| E1 Reliability Fusion | no_rgb | 2098 | 0.264034 | 0.246390 | 0.530138 | 0.289724 | 0.205828 | 0.050843 | 731 | 1367 | 0 | 0.348427 | 0.651573 | 0.000000 |
| E1 Reliability Fusion | no_thermal | 2098 | 0.464783 | 0.322803 | 0.391140 | 0.297437 | 0.144078 | 0.029424 | 838 | 1260 | 0 | 0.399428 | 0.600572 | 0.000000 |
| E1 Reliability Fusion | no_event | 2098 | 0.932433 | 0.028578 | 0.000710 | 0.000490 | 0.066857 | 0.028095 | 2098 | 0 | 0 | 1.000000 | 0.000000 | 0.000000 |
| E2 Reliability + Dropout 0.15 | full | 2098 | 0.461698 | 0.314705 | 0.351996 | 0.209273 | 0.186307 | 0.106808 | 830 | 1268 | 0 | 0.395615 | 0.604385 | 0.000000 |
| E2 Reliability + Dropout 0.15 | no_rgb | 2098 | 0.236256 | 0.101906 | 0.433005 | 0.134575 | 0.330739 | 0.039443 | 295 | 1303 | 500 | 0.140610 | 0.621068 | 0.238322 |
| E2 Reliability + Dropout 0.15 | no_thermal | 2098 | 0.765732 | 0.141821 | 0.115696 | 0.063021 | 0.118572 | 0.079255 | 2098 | 0 | 0 | 1.000000 | 0.000000 | 0.000000 |
| E2 Reliability + Dropout 0.15 | no_event | 2098 | 0.527222 | 0.243574 | 0.356855 | 0.178735 | 0.115923 | 0.065657 | 884 | 1214 | 0 | 0.421354 | 0.578646 | 0.000000 |

## Notes

- Brightness-proxy groups are RGB mean-intensity terciles, not day/night labels.
- Precision, Recall, and F1 in the main table use score threshold 0.50.
- AP50/AP75 are score-ranked AP values from the same completed checkpoints.
- Raw forward profiling measures the model backbone/FPN path on a fixed random tensor.
- Detector inference profiling measures full torchvision FCOS inference on a fixed random tensor.
