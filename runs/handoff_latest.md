# RA-RepDet-TriAir Handoff

Generated: 2026-07-17

## Current task

- V59 status: `V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED`.
- Starting commit: `02ccb571dc143afa32057624ec1b65c438546092`.
- Three frozen read-only passes completed in order: V57 equal, V57 reliability, V55 reference.
- Each checkpoint received exactly one V59 pass over all 1,845 devval rows.
- CPU streaming histogram validation and pre/post tests passed.

## Diagnosis

Primary classification: `EVALUATOR_OR_OUTPUT_SCHEMA_MISMATCH`.

Direct mechanism: `V57_BBOX_REGRESSION_DEGENERATE_GEOMETRY`.

Both V57 models produced 184,500 finite final label-1 tensors with scores above threshold, but every decoded candidate had zero width or height after clipping. The COCO adapter excludes these boxes. V55 produced 5,535,000 positive-area decoded candidates under the same score, postprocess, and evaluator paths.

| Model | Valid decoded | Degenerate decoded | Max-score median | Seconds |
|---|---:|---:|---:|---:|
| V57 equal | 0 | 5,534,979 | 0.34743 | 263.67 |
| V57 reliability | 0 | 5,535,000 | 0.33545 | 233.09 |
| V55 reference | 5,535,000 | 0 | 0.35583 | 228.37 |

The V57 bbox-regression biases were non-positive and feed torchvision's ReLU distance head; V55's four bbox-regression biases were positive. This is direct evidence of checkpoint-level bbox geometry collapse, not proof of a source-code defect.

## Frozen evidence

- Devval/order/subset hashes: `113c3047...a54` / `dd454cfb...e867` / `d622f671...1ee`.
- Checkpoint hashes: V57 equal `d298e6cf...e142`, V57 reliability `b1322ce4...e5df`, V55 `2b4bf19c...b258`.
- Histogram specification: 16,384 linear logit bins and 16,384 logarithmic probability/score bins.
- Full bounded intervals, ladder counts, stage counts, 32-row traces, norms, timing, and memory are under `runs/v59_mmuav_streaming_zero_detection_diagnostic/`.

## Safety

- Optimizer/backward/training/gradient executions: 0 / 0 / 0 / 0.
- Checkpoints and parameters unchanged.
- No alternate-threshold metrics or threshold selection.
- Protected 791-file fingerprint unchanged.
- No heavy artifacts committed.

## Required action

Stop. V59 does not authorize repair, retraining, threshold/evaluator changes, additional inference, or manuscript claims. A new explicit task must define any bbox-regression audit or corrective experiment.
