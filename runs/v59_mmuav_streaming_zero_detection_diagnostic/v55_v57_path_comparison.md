# V55/V57 Read-Only Path Comparison

All models used the same manifest, modality preprocessing, detector transform, FCOS score equation, threshold, top-k, box decode/clip, NMS, final cap, tensor schema, and evaluator label contract. V57 replaces the V55 feature scaffold with its equal/reliability parameter superset.

V57 equal and reliability respectively decoded 5,534,979 and 5,535,000 finite candidates, but every box was degenerate after clipping. V55 decoded 5,535,000 candidates and every box had positive area. All models emitted 184,500 final finite label-1 tensors, so score thresholding, top-k, NMS, final cap, and label filtering did not cause the historical difference. The COCO adapter excluded the V57 zero-area boxes.

`post_inference_parameter_norms.json` records the complete classification, bbox-regression, centerness, and detector-image projection norms. The V57 bbox-regression biases are non-positive and feed a ReLU distance head; V55's four bbox-regression biases are positive. No code-path repair or replay was performed.
