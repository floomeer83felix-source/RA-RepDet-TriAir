# V84 JEI Evidence-Frozen Manuscript

This source snapshot integrates V84 only after P1-P5 and P7 reached a complete
or documented-stop state. Concatenate or compile `main.tex`, which inputs the
five ordered source parts.

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

Rendered legacy figures are intentionally not regenerated in this source-only
snapshot. Any final submission render must rebuild figures against the V84
tables and claims before author review.
