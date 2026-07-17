# Experiment Status

Updated: 2026-07-17

## Active task

`V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED`

## Outcome

V59 completed the authorized read-only rerun with bounded deterministic streaming histograms. The primary task classification is `EVALUATOR_OR_OUTPUT_SCHEMA_MISMATCH`; the directly observed mechanism is `V57_BBOX_REGRESSION_DEGENERATE_GEOMETRY`.

Both V57 checkpoints emit finite label-1 tensors with scores well above 0.001, but every decoded box is degenerate after clipping. The frozen COCO adapter excludes boxes whose width or height is not positive, explaining the historical zero detection count. V55 uses the same score, postprocess, tensor schema, and evaluator paths and produces positive-area boxes.

## Frozen contracts

- Starting commit: `02ccb571dc143afa32057624ec1b65c438546092`.
- Devval rows/hash: 1,845 / `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Ordered devval SHA256: `dd454cfbafa39f2556628ad45dc191b39b0c54bb926028447d5f57553456e867`.
- Detailed subset seed/count/SHA256: 58 / 32 / `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.
- V57 equal checkpoint: `d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142`, 791 tensors.
- V57 reliability checkpoint: `b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df`, 791 tensors.
- V55 reference checkpoint: `2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258`, 787 tensors.
- All checkpoint states were complete and finite, and hashes remained unchanged after inference.

## Histogram validation

- Logits: 16,384 linear bins over [-64, 64], width 0.0078125, exact underflow/overflow counts.
- Probabilities/scores: exact zero and positive-underflow counts plus 16,384 log bins over [1e-12, 1].
- Per model: 28 CPU int64 histograms and 3,673,600 retained histogram bytes.
- Synthetic zero, underflow, overflow, repeated-value, empty-level, chunking, and reverse-order tests passed.
- Every direct synthetic quantile fell inside its reported interval.
- No all-row tensor concatenation or exact all-value quantile was used during inference.

## Pass results

| Model | Passes | Rows | Seconds | Peak allocated | Valid boxes | Degenerate boxes | Final label-1 tensors |
|---|---:|---:|---:|---:|---:|---:|---:|
| V57 equal | 1 | 1,845 | 263.67 | 72,588,800 | 0 | 5,534,979 | 184,500 |
| V57 reliability | 1 | 1,845 | 233.09 | 73,145,856 | 0 | 5,535,000 | 184,500 |
| V55 reference | 1 | 1,845 | 228.37 | 73,140,224 | 5,535,000 | 0 | 184,500 |

Foreground maximum-score medians were 0.34743, 0.33545, and 0.35583 respectively. Per-level bounded median intervals are stored in the three streaming diagnostic JSON files. At threshold 0.001, every model retained all 15,682,500 foreground candidates before per-level top-k, so threshold selection did not cause the V57 zero metric.

## Direct mechanism

The installed torchvision FCOS regression head applies ReLU to predicted bbox distances. V57 equal/reliability bbox-regression bias means were approximately -2.70e-4 and -8.68e-4, with maximum bias 0 in both. V55's four bbox-regression biases were positive, minimum 0.00636. The full-row geometry traces confirm all V57 candidates were degenerate and all V55 candidates were valid.

This supports a checkpoint-level V57 bbox-regression collapse. It does not establish a source-code defect or authorize a repair.

## Safety and tests

- Optimizer steps/backward/training-mode/gradient executions: 0 / 0 / 0 / 0.
- Alternate-threshold AP/AR and threshold selection: not performed.
- Pre-CUDA and post-CUDA unit tests: 13/13 pass each.
- Post-CUDA consistency audit: pass for run order, one-pass budget, stage accounting, all histogram intervals, finite schemas, checkpoint immutability, and protected evidence fingerprint.
- Protected fingerprint: 791 files, SHA256 `8223ac9b7bba0ef2a817a8d9543c17ac8cf264f51ef3151a3d2d0701775e3416`, unchanged.
- V58, production TriAir, V40-V58 history, V51, manuscript, and submission files were unchanged.
- No checkpoints, predictions, images, feature maps, tensor dumps, or other heavy artifacts entered Git.

## Authorization boundary

Stop. V59 diagnoses the historical zero metric but does not authorize training, checkpoint repair, bbox-head changes, threshold/NMS changes, evaluator changes, extra inference, manuscript claims, release, redistribution, or external sharing. Any corrective experiment requires a new explicit task.
