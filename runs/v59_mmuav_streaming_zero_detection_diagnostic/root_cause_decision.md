# V59 Root Cause Decision

Primary classification: `EVALUATOR_OR_OUTPUT_SCHEMA_MISMATCH`. Direct mechanism: `V57_BBOX_REGRESSION_DEGENERATE_GEOMETRY`.

Both V57 checkpoints emit finite label-1 tensors with scores above 0.001, but every decoded box is degenerate after clipping. The frozen COCO adapter excludes zero-width or zero-height boxes, explaining the historical zero count. V55 uses the same score, postprocess, and evaluator paths and produces 5,535,000 valid decoded boxes. The torchvision regression head applies ReLU to bbox distances; both V57 bbox-regression bias vectors are non-positive, while all four V55 biases are positive.

This diagnosis does not authorize repair.
