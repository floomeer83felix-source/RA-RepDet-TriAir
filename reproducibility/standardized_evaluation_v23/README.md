# V23 standardized re-evaluation evidence

This directory contains lightweight provenance records and aggregate results for the standardized validation re-evaluation used by the manuscript refresh.

The evidence scope is:

- frozen validation split `block64_guard16_seed0`;
- detector-output threshold `0.001`;
- operating threshold `0.50` for precision, recall, and F1;
- NMS threshold `0.6`;
- at most `100` detections per image;
- eight full-input checkpoint evaluations and 42 missing-modality rows.

Raw data and checkpoints are not included. The guard partition is excluded from model selection and headline metrics. Missing-modality conditions are synthetic channel-removal evaluations.

See `docs/STANDARDIZED_EVALUATION_V23.md` for the human-readable protocol.
