# V85 JEI Real-Qualitative Manuscript

This source snapshot inherits the V84 evidence freeze and adds the V85 real,
checkpoint-backed qualitative figure only after deterministic selection,
seed-0 inference, provenance capture, and visual review completed. Concatenate
or compile `main.tex`, which inputs the five ordered source parts.

The V84 positioning is:

- RA-RepDet is the sample-dependent dynamic gate;
- gate/no-dropout is the primary nominal-accuracy variant;
- modality dropout is an optional channel-removal robustness regularizer;
- the RGB+thermal control does not establish a positive isolated event gain;
- gate weights are task-driven coefficients, not calibrated sensor-health probabilities;
- component bootstrap is a descriptive component-macro analysis;
- MM-UAV is supervised exposed-devval evidence;
- no same-protocol published comparator was obtained; and
- V84 did not access the locked 837-image internal holdout.

The V85 addition uses three real TriAir development-validation arrays from
distinct components and direct matched-early/dynamic-gate seed-0 predictions.
The fixed display contract is score 0.25, NMS IoU 0.60, and at most 100
detections. No synthetic imagery or manually edited prediction is used. Full
provenance is under `runs/v85_real_qualitative_figure/`.

The local V85 figure PDF is included for compilation but remains excluded from
Git by the repository's heavy-artifact policy. Rendered legacy figures are not
regenerated in this source snapshot. Final submission packaging must place all
reviewed figure PDFs in `figures/` before the author-approved render.
