# V40 Data-Loader / Model-Forward Smoke

- Status: `PASS`
- Note: One validation-batch loader read plus eval-mode forward passes only; no loss, optimizer step, checkpoint, metric computation, or result recording.
- Device used: `cuda`
- This check performs one loader read and eval-mode forward passes only.
- It does not compute AP, F1, precision, recall, loss, runtime, or checkpoint output.

## Loader

- Split: `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt`
- Dataset length: `2213`
- Sample image shape: `[5, 301, 391]`
- Sample path: `D:\download\triair\data\images\frame_00192.npy`

## Models

| Model | Forward Completed | Output Keys | Experimental Result Recorded |
| --- | --- | --- | --- |
| early | `True` | `boxes,labels,scores` | `False` |
| reliability | `True` | `boxes,labels,scores` | `False` |
