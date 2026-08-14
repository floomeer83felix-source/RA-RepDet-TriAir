# Current Task

## Active task

`V85_SUBMISSION_FIGURE_ASSETS_TRACKING_COMPLETE`

The frozen V85 real qualitative PNG/PDF have been copied byte-for-byte into the JEI manuscript submission assets directory and approved for Git tracking. No regeneration, inference, sample selection, or scientific-content change was performed.

Execute:

```text
docs/CODEX_V85_REAL_QUALITATIVE_FIGURE_PLAN.md
```

## Scientific purpose

Add a genuine qualitative figure using only:

- real TriAir component-disjoint development-validation samples;
- real stored RGB / thermal / event-representation channels;
- real matched-early/no-dropout checkpoint predictions;
- real dynamic-gate/no-dropout checkpoint predictions.

The figure must not contain synthetic, AI-generated, reconstructed, hand-edited, or invented sensor imagery, bounding boxes, labels, or confidence scores.

## Fixed qualitative checkpoints

Use **seed 0** for both:

1. matched early fusion / no dropout;
2. dynamic gate / no dropout.

Do not select the visually best seed or substitute another seed silently. If seed 0 cannot be verified, stop and document the reason.

## Deterministic sample selection

Select three scenes from the frozen 2,213-image development-validation split using the model-independent rule specified in the V85 plan:

- Scene A: bright / ordinary;
- Scene B: dark / low-visible-light;
- Scene C: crowded / small-target.

Scenes must come from distinct validation components. Do not manually browse and cherry-pick examples based on model success.

## Figure layout

Preferred layout:

```text
3 rows × 5 columns
(a) RGB
(b) Thermal
(c) Event representation
(d) Matched early fusion
(e) Dynamic gate
```

Use one global display threshold for both checkpoints and all scenes. Default: score `>= 0.25`, NMS IoU `0.60`, max detections `100`.

## Required output root

```text
runs/v85_real_qualitative_figure/
```

Required final artifacts include:

```text
figure/fig6_real_qualitative.png
figure/fig6_real_qualitative.pdf
figure/fig6_caption.txt
provenance/qualitative_figure_provenance.md
V85_QUALITATIVE_FIGURE_SUMMARY.md
```

The provenance must include sample IDs, component IDs, split identity, checkpoint SHA256 values, seed, preprocessing, visualization transforms, prediction threshold, and the generation command.

## Locked data protection

The historical 837-image partition remains **locked**.

Do not inspect, render, score, or use it for qualitative selection. This task is authorized only on the frozen 2,213-image development-validation split.

## Manuscript integration gate

Only after the real figure and provenance are frozen may Codex insert the figure into the current V85 JEI submission candidate. Do not replace quantitative results or change the V84 scientific positioning.

## Frozen scientific positioning

- `RA-RepDet` = sample-dependent / input-conditioned dynamic modality gating.
- Gate/no-dropout is the primary nominal-input model.
- Modality dropout is an optional robustness regularizer.
- Routing coefficients are task-driven and are not calibrated physical reliability estimates.
- No SOTA, independent-test, sensor-health, or three-seed significance claim.

## Commit message

submission: track frozen V85 real qualitative figure assets
