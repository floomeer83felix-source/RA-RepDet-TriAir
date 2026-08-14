# Codex Task Plan: V85 Real Qualitative Detection Figure

## Status

`V85_REAL_QUALITATIVE_FIGURE_PLANNED`

This task adds one **genuine qualitative detection figure** to the JEI submission candidate. The figure must be generated only from real TriAir development-validation samples and real frozen checkpoint predictions. No synthetic, AI-generated, reconstructed, or manually invented sensor imagery, boxes, labels, confidence scores, or failure/success cases are permitted.

The current scientific positioning remains frozen from V84:

- `RA-RepDet` = sample-dependent / input-conditioned dynamic modality gating;
- gate/no-dropout is the primary nominal-input model;
- modality dropout is an optional robustness regularizer;
- routing weights are task-driven coefficients, not calibrated physical sensor-health probabilities;
- no SOTA claim, no independent-test claim, and no statistical-significance claim from three seeds alone.

---

# 1. Scope and hard constraints

## Allowed data

Use **only** the existing 2,213-image TriAir component-disjoint development-validation split already frozen for the paper.

## Forbidden data

The historical 837-image partition remains locked and must not be accessed, inspected, rendered, scored, or used for qualitative sample selection.

## Allowed checkpoints

Use the authoritative frozen checkpoints already used for V84/V85 evidence:

1. matched early fusion / no dropout;
2. dynamic gate / no dropout.

Use **seed 0** as the fixed qualitative checkpoint for both models unless the archived checkpoint registry proves seed 0 is unavailable. Do not choose the visually best seed or the best-performing seed after inspecting qualitative outputs.

If seed 0 cannot be used, stop and document the reason before substituting any other seed.

## No retraining

Do not retrain, fine-tune, alter thresholds based on qualitative appearance, replace checkpoints, or rerun training.

---

# 2. Scientific goal

Create a publication-quality qualitative figure that lets a reader inspect:

- the real RGB observation;
- the real thermal channel;
- the real stored event-representation channel;
- matched early-fusion detections;
- dynamic-gate detections;
- optionally ground-truth boxes if a separate clean display remains legible.

The figure is **illustrative evidence**, not a quantitative metric and not a replacement for Table 1.

The intended manuscript role is to complement the existing quantitative result that dynamic gate/no-dropout reaches `0.7251 ± 0.0121` AP and exceeds matched early fusion under the frozen development-validation protocol.

---

# 3. Deterministic sample-selection protocol

Do not manually browse the validation set and cherry-pick attractive examples.

Build a deterministic candidate table for all 2,213 validation samples using only predeclared, model-independent descriptors:

- sample ID / relative path;
- connected-component ID;
- number of ground-truth boxes;
- median/mean RGB luminance;
- RGB luminance standard deviation or contrast proxy;
- thermal mean and standard deviation;
- event-channel mean, standard deviation, and range;
- image dimensions.

Then select exactly **three primary scenes** with a deterministic rule:

### Scene A — bright / ordinary scene

- RGB mean luminance in the upper quartile;
- at least 2 ground-truth vehicles;
- choose the lexicographically smallest sample ID among candidates closest to the median GT-count within that bucket.

### Scene B — dark / low-visible-light scene

- RGB mean luminance in the lower quartile;
- at least 2 ground-truth vehicles;
- choose the lexicographically smallest sample ID among candidates closest to the median GT-count within that bucket.

### Scene C — crowded / small-target scene

- ground-truth count in the upper decile;
- choose the lexicographically smallest sample ID among candidates closest to the median RGB luminance of that bucket.

If these rules yield the same connected component for multiple scenes, keep Scene A and choose the next deterministic candidate for later scenes so that all three scenes come from different validation components.

Do **not** use model AP, per-image loss, detection success, or visual attractiveness to select Scenes A–C.

## Optional failure case

A fourth row may be created as a clearly labeled `Failure case` only if selected by a predeclared deterministic model-based rule applied **after** Scenes A–C are frozen:

- compute per-image matched prediction quality for both fixed checkpoints using a frozen IoU/assignment rule;
- define the failure score before inspecting images;
- select the lexicographically smallest sample among the worst 1% dynamic-gate samples by that score;
- report the selection rule in the provenance file.

If implementing a defensible per-image score would require ad-hoc choices, omit the failure row rather than improvise.

---

# 4. Real sensor visualization

For every selected sample, export the actual stored channels from the TriAir array used by the project.

## RGB

- channels 0–2;
- use the same channel interpretation already frozen in the project;
- no generative enhancement;
- no content-aware editing;
- only deterministic display scaling if required.

## Thermal

- channel 3;
- display with a fixed deterministic normalization shared across the selected figure rows where feasible;
- prefer grayscale unless the project already has an explicitly frozen thermal colormap;
- do not invent pseudo-temperature units.

## Event representation

- channel 4;
- this is the stored TriAir event representation, not raw asynchronous events;
- use a fixed scientifically faithful display transform;
- do not create red/blue positive/negative polarity visualization unless the stored channel semantics explicitly support it;
- document the exact transformation used.

The figure caption must call it `stored event representation` or equivalent rather than implying reconstruction of raw event streams.

---

# 5. Real detector predictions

Run label-preserving inference on the three frozen validation samples using:

- matched early / no dropout, seed 0;
- dynamic gate / no dropout, seed 0.

Use the same preprocessing and NMS implementation as the frozen evaluator.

For **display only**, a confidence threshold may be chosen in advance to avoid hundreds of very low-score COCO-evaluation candidates. Default display threshold:

```text
score >= 0.25
NMS IoU = 0.60
max detections = 100
```

Do not tune the display threshold per image or per model.

If `0.25` creates unusable clutter or hides essentially all detections, stop and document the issue before changing it. Any changed threshold must be one global value used for both models and all selected scenes.

Every rendered detection must come from an archived prediction produced by the actual checkpoint. Do not manually move, resize, add, delete, or relabel boxes.

Confidence text must use the real model score rounded consistently to two decimals if shown.

---

# 6. Figure layout

Preferred layout: **3 rows × 5 columns**.

Columns:

```text
(a) RGB
(b) Thermal
(c) Event representation
(d) Matched early fusion
(e) Dynamic gate
```

Rows:

```text
Scene A — bright / ordinary
Scene B — dark / low-visible-light
Scene C — crowded / small-target
```

Optional fourth row:

```text
Scene D — deterministic failure case
```

## Detection overlays

- use one consistent color for matched early predictions;
- use another consistent color for dynamic-gate predictions;
- use a third style for ground truth only if GT overlay is shown;
- line width and font scale must be readable at JEI manuscript width;
- do not use decorative effects or AI-generated backgrounds.

Do not encode qualitative superiority through thicker boxes, larger fonts, or more prominent colors for RA-RepDet. Both model columns must have equivalent visual treatment.

---

# 7. Required outputs

Write all artifacts under:

```text
runs/v85_real_qualitative_figure/
```

Required files:

```text
selection/
  validation_candidate_table.csv
  selected_samples.json
  selection_protocol.md

predictions/
  matched_early_seed0_predictions.json
  dynamic_gate_seed0_predictions.json
  checkpoint_identity.json

panels/
  scene_A_rgb.png
  scene_A_thermal.png
  scene_A_event.png
  scene_A_early.png
  scene_A_gate.png
  scene_B_...
  scene_C_...

figure/
  fig6_real_qualitative.png
  fig6_real_qualitative.pdf
  fig6_caption.txt

provenance/
  visualization_parameters.json
  qualitative_figure_provenance.md

V85_QUALITATIVE_FIGURE_SUMMARY.md
```

If a vector PDF is produced, raster sensor panels may remain embedded raster images while labels, borders, and panel headings should remain vector where practical.

---

# 8. Provenance requirements

`qualitative_figure_provenance.md` must state:

- branch and git commit;
- exact validation manifest identity / SHA256;
- selected sample IDs and connected-component IDs;
- selection descriptors and deterministic selection rule;
- exact checkpoint paths and SHA256 identities;
- exact model seed;
- preprocessing;
- display score threshold;
- NMS threshold;
- event visualization transform;
- thermal visualization transform;
- script/command used to generate the figure;
- explicit statement that no AI-generated or synthetic sensor imagery, predictions, boxes, scores, or annotations are used.

The summary must also state that the 837-image historical partition was not accessed.

---

# 9. Manuscript integration

Only after the figure and provenance pass review, integrate it into the current V85 JEI submission candidate.

Recommended placement:

- after the main nominal-fusion/channel-removal results, or immediately before `Discussion and Limitations` if layout is better.

Recommended caption draft:

> **Fig. 6.** Qualitative detections on deterministically selected TriAir component-disjoint development-validation samples. Columns show the RGB observation, thermal channel, stored event representation, matched early-fusion predictions, and dynamic-gate predictions from fixed seed-0 checkpoints. Samples are selected from predeclared image descriptors rather than model performance. Bounding boxes and confidence scores are direct checkpoint outputs under one fixed display threshold; no manual box editing is applied.

Adjust numbering automatically if the manuscript insertion point changes.

Add no language claiming that the qualitative examples establish generalization or sensor reliability.

---

# 10. Acceptance gate

Mark this task complete only when all of the following are true:

- all displayed sensor panels are traced to real TriAir validation arrays;
- all displayed prediction boxes/scores are traced to the two fixed real checkpoints;
- seed 0 is used for both models, or a documented stop occurs before substitution;
- sample selection follows the deterministic predeclared rule;
- scenes come from distinct validation components;
- no historical 837-image data are accessed;
- no synthetic or AI-generated image is used in the manuscript figure;
- prediction threshold is identical across models and scenes;
- `fig6_real_qualitative.png` and `.pdf` are generated;
- provenance files are complete;
- the manuscript is updated only after the evidence figure is frozen.

## Commit message

```text
figures: add real checkpoint-backed qualitative detections for JEI
```
