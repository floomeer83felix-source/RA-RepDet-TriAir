# SCI Evidence-Strengthening Plan for RA-RepDet

## Purpose

This plan translates the manuscript publishability assessment into a sequenced experimental package. It is designed to improve the evidence for an applied SCI submission without changing the current paper's frozen headline by implication. Each phase has an explicit gate so that an invalid split, incompatible baseline, or unavailable public dataset becomes a documented result rather than an undocumented workaround.

## Current Scientific Position

The strongest current evidence is the matched R0/R1/R2/R4 ablation on the clean `block64_guard16_seed0` validation protocol. R4 `p=0.20` is the manuscript headline with two controlled seeds. This is adequate for a serious applied manuscript draft, but it is not enough to substantiate broad generalization, real sensor-failure robustness, or high-novelty claims.

The attempted V39 candidate component-disjoint split is not eligible for training continuation. Its audit found 353 same-family train/validation distance-16 violations, four train/guard exact RGB-content groups, five validation/guard exact RGB-content groups, and a minimum cross-partition same-family distance of one.

## Ordered Research Package

| phase | experiment | primary question | hard gate | manuscript role if successful |
| --- | --- | --- | --- | --- |
| V40 | Component-disjoint split repair and R4 completion | Does R4 retain evidence under a truly component-disjoint split? | no GPU work until all strict split checks pass | stronger validation protocol, separate until evidence review |
| V41 | Public-protocol baselines and cross-dataset feasibility | Does the method transfer or compare fairly under public data/protocols? | licence, class mapping, representation mapping, and baseline provenance | external validation / literature comparison |
| V42 | Realistic degradation stress suite | Does R4 remain more stable under controlled sensor-like degradations? | severity schedule fixed before evaluation; R0 and R4 both run | robustness section |
| V43 | Three-seed uncertainty extension | Is the R0--R4 result stable beyond two seeds? | fixed protocol and predeclared seed | uncertainty reporting |
| V44 | Qualitative error taxonomy | Where does the detector fail and why? | real validation panels; author approval required for final figures | qualitative/error analysis |
| V45 | Evidence reconciliation | Which new evidence can change paper wording or headline? | all reports reviewed; no automatic headline replacement | revision decision only |

## V40 Requirements

The split must be built on connected components created by the transitive closure of: exact RGB-content identity and same-family ID distance less than or equal to 16. Train, validation, and guard must each receive whole components. The audit must demonstrate:

- every local sample occurs once and only once;
- zero pairwise path overlap;
- zero pairwise exact RGB-content overlap;
- zero pairwise same-family distance-16 violation;
- zero cross-partition component;
- deterministic regeneration of the same split hashes.

Only then may R4 `p=0.20`, seeds 0 and 2, run for 50 epochs with the existing V39 hyperparameters. The output remains validation-only and separate from the current manuscript headline until V45.

## V41 Requirements

V41 must not invent comparability. For every candidate public dataset and baseline, record the source, licence/access status, modality availability, label classes, spatial/temporal alignment assumptions, preprocessing differences, and reason for inclusion or exclusion. A failed feasibility assessment is an acceptable documented result; silently adapting data or mixing incomparable metrics is not.

## V42 Degradation Matrix

| modality | controlled degradation | minimum severities |
| --- | --- | --- |
| RGB | brightness/contrast loss and blur | mild, medium, severe |
| thermal | contrast compression and additive noise | mild, medium, severe |
| event | sparsity/drop-rate or amplitude attenuation | mild, medium, severe |
| multimodal | one predeclared compound condition | at least one medium compound case |

For each condition report AP50, AP75, F1@0.50, change from clean performance, and per-seed summary. Synthetic degradation must never be called actual sensor failure.

## V43 Uncertainty Plan

Use one additional predeclared seed for R0 and R4 on the selected validated protocol. Hold architecture, data, split, epochs, image size, batch size, learning rate, and evaluator fixed. Report all seeds, mean, standard deviation, paired metric differences, and limitations. Do not advertise statistical significance unless an analysis plan and its assumptions are explicitly satisfied.

## V44 Error Analysis Plan

Annotate at least the following real validation case types: small or occluded vehicles, dense vehicles, false positives, false negatives, low-visible-contrast scenes, thermal-removal failures, and event-degraded cases where available. Report counts and representative examples. Do not insert source image paths, raw panels, or final figures into public materials without data-owner and author approval.

## Decision Rules

1. A failed audit or infeasible public baseline is a reportable blocker, not a reason to weaken a gate.
2. New evidence cannot overwrite the existing clean-split manuscript headline automatically.
3. The headline can change only after V45 documents a direct comparison, provenance, scope, and author-approved revision decision.
4. All experiments must remain on `research/ra-repdet-triair` until an explicit branch strategy says otherwise.
5. No raw data, checkpoints, weights, or large prediction artifacts are committed to Git.
