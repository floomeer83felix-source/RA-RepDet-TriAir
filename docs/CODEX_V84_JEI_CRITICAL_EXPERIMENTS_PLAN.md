# Codex Task Plan: V84 JEI Critical Experiment Closure

## Status

`V84_JEI_CRITICAL_EXPERIMENT_CLOSURE_PLANNED`

This plan responds to the remaining JEI reviewer-risk items after the V81/V83 evidence closure. The goal is to close the few experiments that materially affect the paper's scientific positioning, not to expand the experiment matrix indiscriminately.

The active manuscript remains the current authoritative manuscript until V84 evidence is complete and audited. Do **not** overwrite authoritative accuracy tables before the corresponding V84 phase passes its acceptance gate.

## Scientific re-positioning to preserve

The core method is:

> **RA-RepDet = sample-dependent / input-conditioned dynamic modality gating.**

Modality dropout is **not** the core method. Treat it as an optional robustness regularizer.

Current authoritative causal evidence already shows:

- matched early fusion AP: `0.6803 ± 0.0221`;
- dynamic gate without dropout AP: `0.7251 ± 0.0121`;
- dynamic gate + modality dropout AP: `0.7156 ± 0.0172`;
- fixed equal stems AP: `0.6631 ± 0.0068`;
- learned deterministic stems projection AP: `0.6848 ± 0.0095`;
- gate-no-dropout minus fixed equal stems: `+0.0621 ± 0.0188`;
- gate-no-dropout minus learned deterministic projection: `+0.0404 ± 0.0074`.

Therefore the manuscript must not present the p=0.15 dropout variant as the best nominal-accuracy model.

## Frozen evidence sources

Use only the existing authoritative sources for already-completed evidence:

- V81 single-modality checkpoints/results;
- V48 six-variant fusion ablation;
- V75 supervised MM-UAV transfer;
- V83 fixed-hardware checkpoint/efficiency evidence;
- V42 locked internal holdout only under the explicit holdout gate below.

Historical V77/V80 supplied rows remain reconciliation-only and must never return to primary claims.

---

# Priority 0 — Repository and checkpoint preflight

Before any new training or evaluation:

1. record current git commit and branch;
2. verify the exact component-disjoint train/validation manifests and their SHA256 identities;
3. inventory all existing V48 fusion checkpoints needed for the four-model matched analysis:
   - matched early / no dropout;
   - early + dropout;
   - dynamic gate / no dropout;
   - dynamic gate + dropout;
4. verify seed, epoch, model config, and checkpoint SHA256 where archived identities exist;
5. verify the V81 single-modality registry remains unchanged;
6. write the preflight to:

```text
runs/v84_jei_critical_closure/preflight/
```

Required files:

```text
repository_state.json
split_identity.json
checkpoint_inventory.json
preflight_summary.md
```

Fail closed on split mismatch or checkpoint identity mismatch. Do not silently substitute another checkpoint.

---

# Priority 1 — RGB + Thermal two-modality baseline, three seeds

## Why this is required

This is the highest-value new training task. Existing test-time event removal cannot answer whether the event modality contributes when the model is trained from the outset without the event channel.

## Required experiment

Train **RGB+Thermal only** under the same protocol as the authoritative fusion experiments:

- seeds: `0, 1, 2`;
- same component-disjoint train/validation manifests;
- same input size;
- same epoch budget and optimizer/schedule as the matched fusion protocol;
- same detector/backbone family;
- same checkpoint-retention rule;
- same standardized COCO evaluator;
- no threshold tuning;
- no seed replacement;
- no selective rerun;
- no checkpoint substitution.

Store under:

```text
runs/v84_jei_critical_closure/rgb_thermal_baseline/
```

Required metrics for every seed:

- AP@[.50:.95];
- AP50;
- AP75;
- AR1;
- AR10;
- AR100;
- retained epoch;
- checkpoint SHA256.

Required summary:

- mean ± sample SD;
- seed-paired delta vs matched early three-modality fusion when protocol-compatible;
- seed-paired delta vs dynamic gate no-dropout three-modality fusion when protocol-compatible.

## Conditional pairwise expansion

Do **not** automatically train RGB+Event and Thermal+Event before inspecting the RGB+Thermal result.

Proceed to the two additional pairwise baselines only if at least one of the following is true:

1. RGB+Thermal is close enough to three-modality performance that attribution of event contribution remains ambiguous;
2. event contribution appears concentrated in AP75 or another metric and pairwise decomposition is needed;
3. the manuscript's final claim still explicitly depends on three-way complementarity.

If triggered, run RGB+Event and Thermal+Event with the same three seeds and frozen protocol.

---

# Priority 2 — Fully matched 2×2 gate × modality-dropout channel-removal analysis

## No retraining unless a required checkpoint is missing

Use the existing four model families:

1. early / no dropout;
2. early / dropout;
3. gate / no dropout;
4. gate / dropout.

For seeds `0, 1, 2`, evaluate each model under exactly four inference conditions:

1. all modalities present;
2. RGB removed;
3. thermal removed;
4. event removed.

Use the same deterministic removal operator for every model and seed.

Required metrics:

- AP@[.50:.95];
- AP50;
- AP75;
- AR100.

Required outputs:

```text
runs/v84_jei_critical_closure/channel_removal_2x2/
  per_run.csv
  summary.csv
  paired_deltas.csv
  analysis.md
```

The analysis must separate:

- dynamic-gate main effect;
- modality-dropout main effect;
- gate × dropout interaction;
- modality-specific degradation patterns.

Do not attribute robustness to gating if the matched factorial analysis shows it is mainly explained by dropout.

---

# Priority 3 — Gate-weight and controlled-quality analysis

## Objective

Provide direct evidence that the learned weights respond systematically to input/modality quality. This supports the paper's `reliability-aware` interpretation while keeping the wording precise: the weights are learned task-driven modality weights, not calibrated physical sensor-health probabilities.

## Use gate-no-dropout as the primary analysis model

Use the dynamic-gate/no-dropout checkpoint family first so the analysis is not confounded by modality-dropout training.

## Clean-input analyses

For each validation sample, export:

- RGB gate weight;
- thermal gate weight;
- event gate weight;
- sample identifier/component identifier.

Compute simple, reproducible modality descriptors when directly supported by the stored arrays:

### RGB

- mean luminance/intensity;
- intensity standard deviation;
- entropy or another explicitly defined contrast proxy.

### Thermal

- mean intensity;
- intensity standard deviation;
- entropy/contrast proxy.

### Event

- nonzero fraction/activity ratio;
- mean magnitude/intensity;
- spatial entropy if well defined.

Report correlations and binned trends between these descriptors and gate weights.

Do not invent day/night labels. Only add day/night analysis if an authoritative label/metadata source already exists in the repository or dataset metadata.

## Controlled corruption analyses

Evaluate clean plus at least three severity levels for each modality separately.

Recommended operators:

- RGB: Gaussian blur and/or additive noise;
- thermal: blur and/or additive noise;
- event: sparsification/dropout or attenuation consistent with the event representation.

For each severity:

- corrupt only one modality;
- keep the other modalities unchanged;
- record gate weights;
- record detector AP/AP50/AP75 when evaluator labels are already authorized for the development-validation split.

Primary question:

> Does the weight assigned to a degraded modality decrease systematically as degradation increases, with compensating weight shifts toward the other modalities?

Required outputs:

```text
runs/v84_jei_critical_closure/gate_quality_analysis/
  clean_sample_weights.csv
  quality_descriptors.csv
  corruption_results.csv
  figures/
  analysis.md
```

Recommended manuscript figure:

- weight distribution by modality;
- descriptor-vs-weight trend;
- corruption severity vs corrupted-modality weight;
- corruption severity vs AP/AP75.

No claim of calibrated physical reliability is authorized.

---

# Priority 4 — Component-cluster bootstrap of primary paired comparisons

## Objective

Strengthen uncertainty reporting without pretending that image-level resampling is independent when the split construction is component based.

Use the component identity used by the leakage-aware split as the resampling unit.

Primary comparisons:

1. gate no-dropout vs matched early;
2. gate no-dropout vs fixed equal stems;
3. gate no-dropout vs learned deterministic projection.

Use a fixed, documented bootstrap seed and at least 2,000 component-cluster bootstrap replicates; 5,000 is preferred if inexpensive.

Report:

- observed delta;
- bootstrap mean delta;
- percentile 95% interval;
- fraction of bootstrap replicates with delta > 0.

Store:

```text
runs/v84_jei_critical_closure/component_cluster_bootstrap/
```

This is descriptive uncertainty evidence. Do not convert it into an unsupported broad significance claim.

---

# Priority 5 — One published multimodal comparator on the same split/evaluator

## Objective

Add one credible published comparator so the paper is not only an internal ablation study.

Preferred order:

1. an official TriAir representative method with code and weights/training recipe that can be reproduced lawfully;
2. otherwise one established public RGB-T/multimodal detector with a compatible implementation.

Do not compare the paper's COCO AP numerically against published TriAir numbers from a different split/evaluator.

## Required contract

For the selected comparator:

- same component-disjoint split;
- same 640×640 input where method permits;
- same three seeds if training from scratch/fine-tuning is required;
- same standardized COCO evaluator;
- record params and FLOPs/latency when practical;
- document any implementation deviation.

Required table columns:

- method;
- modalities;
- params;
- GFLOPs if measured with a verified profiler;
- AP;
- AP50;
- AP75;
- AR100.

Store under:

```text
runs/v84_jei_critical_closure/published_comparator/
```

If no published comparator can be reproduced without changing the evaluation contract or introducing unresolvable code/license problems, document the failure transparently and stop this phase rather than inventing a comparison.

---

# Priority 6 — Optional seed extension for the core comparison only

If GPU budget remains after Priorities 1–5, extend only the core nominal-accuracy comparison from three to five seeds:

- matched early: seeds `3, 4`;
- gate no-dropout: seeds `3, 4`.

Do not expand all six ablation variants to five seeds unless a later reviewer specifically requires it.

Use exactly the same frozen protocol as seeds 0–2.

Store under:

```text
runs/v84_jei_critical_closure/core_seed_extension/
```

---

# Priority 7 — MM-UAV reproducibility closure, no new training by default

The existing V75 supervised target-domain results remain authoritative. Do not rerun them merely to make a new version number.

Add a reproducibility package documenting:

- exact sequence IDs/manifests used for train and devval;
- tracking-to-detection annotation conversion;
- frame/subset extraction logic producing the reported sample counts;
- geometry/alignment preprocessing;
- alignment adapter architecture;
- parameter-transfer name/shape matching rule;
- exact interpretation of the reported `99.20%` compatible parameter match;
- which parameters were not transferred;
- seed configuration;
- checkpoint-selection/evaluation rule;
- explicit statement that this is supervised exposed devval, not blind zero-shot evaluation.

Store under:

```text
runs/v84_jei_critical_closure/mm_uav_reproducibility/
```

---

# Priority 8 — Manuscript integration after evidence freeze

Do not rewrite the manuscript piecemeal after each run. Integrate only after Priorities 1–5 have either passed or have a documented stop reason.

## Required manuscript positioning

1. `RA-RepDet` refers to the dynamic gate mechanism.
2. Gate/no-dropout is the primary nominal-accuracy model if it remains the best validated dynamic-gate variant.
3. Modality dropout is reported as an optional robustness regularizer with an accuracy/robustness tradeoff.
4. The RGB+Thermal baseline determines how strongly the paper may claim event contribution.
5. Reliability wording is supported by gate-quality/corruption evidence and remains explicitly task-driven rather than physically calibrated.
6. The published comparator is presented under the same split/evaluator only.
7. Cluster bootstrap is reported as component-aware uncertainty evidence.
8. MM-UAV remains supervised exposed-devval transfer evidence.

## Abstract requirement

Keep the JEI abstract within the live journal word limit verified immediately before submission. Prefer approximately 185–195 words to leave safety margin.

---

# Priority 9 — Locked 837-image internal holdout: STOP GATE

**Do not access, evaluate, inspect labels, or regenerate metrics on the locked 837-image holdout as part of automatic V84 execution.**

The holdout is internal to the same provider archive and has already been used in prior analysis. Reuse requires a separate explicit author instruction specifically authorizing `837-image locked holdout reuse` after the final V84 model/comparator/evaluator choices are frozen.

If such authorization is later received, create a separate one-shot protocol before touching the holdout. It should include:

- exact existing holdout manifest and SHA256;
- frozen model/checkpoint list;
- frozen COCO evaluator;
- early, gate-no-dropout, and gate+dropout only unless otherwise predeclared;
- AP/AP50/AP75/AR100;
- no threshold tuning;
- no checkpoint selection;
- no selective reruns;
- explicit disclosure that this is repeated internal-holdout evidence, not an independent external test.

Until then, this phase is prohibited.

---

# Global prohibited actions

- do not use V77/V80 historical supplied values as primary evidence;
- do not replace missing checkpoints with convenient alternatives;
- do not replace seeds after seeing outcomes;
- do not selectively rerun failed/weak seeds unless there is a documented technical failure independent of metric value;
- do not tune confidence/NMS thresholds on validation to improve reported AP;
- do not claim SOTA;
- do not claim independent external generalization from MM-UAV or the internal holdout;
- do not call learned weights calibrated sensor reliability probabilities;
- do not claim statistical significance solely from three training seeds;
- do not access the locked 837-image holdout without the separate explicit authorization described above.

---

# Recommended execution order

```text
P0 preflight
→ P1 RGB+Thermal 3-seed baseline
→ P2 matched 2×2 channel-removal evaluation
→ P3 gate-quality / controlled-corruption analysis
→ P4 component-cluster bootstrap
→ P5 one published comparator
→ P6 optional core seed extension if compute remains
→ P7 MM-UAV reproducibility package
→ P8 manuscript integration
STOP before P9 locked holdout unless separately authorized
```

Parallelization is allowed only when it cannot alter a frozen protocol. For example, P2/P3/P4 can run in parallel after P0 if they use existing verified checkpoints; P1 training may also proceed concurrently if compute permits.

---

# Completion criteria

V84 may be marked complete only when:

1. RGB+Thermal seeds 0/1/2 are complete and checkpoint identities archived;
2. the four-model × four-condition × three-seed channel-removal matrix is complete or a missing-checkpoint limitation is documented;
3. gate-weight quality/corruption analysis is complete with reproducible data and figures;
4. component-cluster bootstrap outputs are archived;
5. one published comparator is completed under the same split/evaluator, or a documented reproducibility/license stop reason is committed;
6. MM-UAV reproducibility documentation is complete;
7. no locked-holdout access occurred;
8. a concise evidence summary states exactly which claims are strengthened, weakened, or unchanged;
9. manuscript integration is performed only after the evidence freeze.

## Recommended evidence summary

```text
runs/v84_jei_critical_closure/V84_EVIDENCE_SUMMARY.md
```

## Recommended commit messages

During execution, use scoped commits such as:

```text
experiments: add V84 RGB-thermal baseline
analysis: add V84 matched channel-removal matrix
analysis: add V84 gate quality response evidence
analysis: add component-cluster bootstrap
experiments: add same-protocol published comparator
docs: close MM-UAV reproducibility details
paper: integrate V84 JEI evidence
```
