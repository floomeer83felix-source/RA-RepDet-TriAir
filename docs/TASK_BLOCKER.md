# Task Blocker

Status: `V58_BLOCKED_INSTRUMENTATION_OR_INFERENCE_PATH`

Generated: 2026-07-17

## Exact failure

The V57-equal checkpoint completed one full 1,845-row read-only aggregate forward pass. During compact reduction of concatenated FPN-level score tensors, PyTorch raised:

```text
File "rarepdet/tools/run_v58_zero_detection_diagnostic.py", line 419, in diagnose_model
  "level": level, "classification_logit_quantiles": quantile_summary(cls),
File "rarepdet/tools/run_v58_zero_detection_diagnostic.py", line 217, in quantile_summary
  result = torch.quantile(values, q)
RuntimeError: quantile() input tensor is too large
```

The last error lines are preserved in `runs/v58_mmuav_zero_detection_diagnostic/blocker_error_tail.txt` and the complete wrapper output is in `runner_output.txt`.

## Attempted work

1. Verified the 1,845-row devval count/hash and froze its ordered row hash.
2. Froze a deterministic 32-row subset from seed 58 before reading outputs.
3. Verified exact SHA256, sizes, step metadata, state keys/shapes, and finite tensors for both required V57 checkpoints and the optional V55 reference.
4. Inspected and source-locked the actual torchvision FCOS score, threshold, top-k, decode, NMS, cap, and output path.
5. Ran 9/9 CPU/source-lock tests successfully.
6. Executed the first V57-equal read-only pass. Exact concatenation succeeded, but exact `torch.quantile` exceeded its supported input size.
7. Stopped immediately. No alternate quantile method, second pass, remaining checkpoint, threshold change, or AP/AR calculation was attempted.

## Related files

- `rarepdet/tools/run_v58_zero_detection_diagnostic.py`
- `tests/test_v58_zero_detection_diagnostic.py`
- `runs/v58_mmuav_zero_detection_diagnostic/protocol.json`
- `runs/v58_mmuav_zero_detection_diagnostic/checkpoint_verification.json`
- `runs/v58_mmuav_zero_detection_diagnostic/runner_output.txt`
- `runs/v58_mmuav_zero_detection_diagnostic/partial_pass_status.json`

## Pass state

- V57 equal: full forward completed; its single aggregate pass is consumed; compact summary unavailable.
- V57 reliability: not run.
- V55 reference: not run.
- Optimizer steps/backward/training-mode executions: 0 / 0 / 0.
- All three checkpoint hashes remained unchanged after failure.

## Proposed repair options

1. New task: pre-register deterministic streaming histograms or a fixed-size reservoir with explicit quantile approximation/error rules, then reset and run all three models once under the revised protocol.
2. New task: use a local non-Git NumPy memmap or chunked exact-selection implementation, delete temporary heavy data after compact aggregation, then reset and run all three models once.

Both options require explicit authorization because V58's equal pass has already been consumed. No repair or rerun is authorized now.
