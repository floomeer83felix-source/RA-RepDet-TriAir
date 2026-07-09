# Pre-Submission Reviewer Report for SIVP

Generated: 2026-07-09

## Overall recommendation

**Major revision risk remains, but the manuscript is now substantially more defensible for formal submission.**

The manuscript now has a clearer signal/image/video processing story: a lightweight RGB--thermal--event fusion front end is compared with a matched early-fusion baseline under a component-disjoint development-validation protocol, and the fixed checkpoints are further checked on a locked same-dataset held-out guard partition. The paper is strongest when it presents the result as bounded, auditable within-dataset evidence rather than as external generalization or deployment-ready robustness.

## Summary of the manuscript

The paper proposes RA-RepDet, a lightweight RGB--thermal--event UAV vehicle detector built on RepViT-M0.9, FPN, and FCOS. The active comparison is reliability-aware fusion with modality dropout p=0.15 versus matched early fusion, evaluated over seed0/seed1/seed2 on a frozen V40 component-disjoint development-validation split and then on a locked 837-image held-out TriAir guard manifest. The manuscript reports descriptive positive mean deltas for F1, AP50, and AP75 on development-validation and smaller positive mean deltas on held-out guard, while explicitly stating that AP50/AP75 are project-local single-class metrics rather than COCO AP50:95.

## Strengths

1. **Clearer evidence boundary.** The manuscript no longer overclaims external-dataset generalization, physical sensor-failure robustness, statistical significance, or optimal dropout.
2. **Matched active comparison.** The main result compares reliability-aware fusion and early fusion under the same detector stack, evaluator, and seeds.
3. **Improved split-integrity discussion.** The component-disjoint development-validation and locked held-out guard protocol are presented as part of the contribution.
4. **Three paired seeds plus held-out guard.** The result is stronger than a validation-only report because the fixed checkpoints were checked once on a locked same-dataset guard manifest.
5. **Declarations and availability.** Author metadata, funding, competing interests, contributions, acknowledgments, data availability, and code availability are present.

## Major concerns

### 1. The held-out guard is same-dataset evidence, not external validation

The V42 held-out guard evaluation materially improves the manuscript, but the guard partition remains within TriAir. Reviewers may still ask for an external dataset or independent public benchmark. The manuscript should keep the current wording: held-out guard evidence, not external generalization.

**Action taken:** The abstract, introduction, results, discussion, limitations, and conclusion were updated to describe development-validation plus locked same-dataset held-out guard evidence.

### 2. Held-out gains are smaller and per-seed results are mixed

The guard evaluation shows smaller positive mean gains than development-validation. AP50 is positive across all three seed pairs, but F1 decreases for seed0 and AP75 decreases for seed2. This should be presented as a useful robustness check of the trend, not as a uniformly consistent improvement on every metric and seed.

**Action taken:** The held-out results section explicitly reports smaller mean gains and mixed per-seed F1/AP75 deltas.

### 3. Figures should remain conservative

Earlier manuscript versions contained explicit `Final artwork pending` placeholder figures. These were a desk-review risk. The current text schematics are acceptable for pre-submission review but could still be improved with final vector artwork.

**Action taken:** Explicit placeholder figures were replaced by simple in-manuscript schematic/table figures for architecture, split workflow, and paired deltas.

### 4. Auxiliary analyses should not distract from the active claim

External YOLO, synthetic missingness, gate weights, and qualitative materials are not currently the manuscript's strongest evidence. Presenting them as main results would invite reviewer criticism.

**Action taken:** These materials are described only as contextual or pending-review evidence. The active quantitative claim is the three-seed development-validation comparison plus the V42 held-out guard table.

### 5. Data-governance details remain incomplete

The manuscript names TriAir as a public dataset and avoids redistributing original files, which is acceptable as a concise availability statement. However, provider version, license, redistribution conditions, and synchronization details remain only partially resolved.

**Action taken:** The limitations section keeps these as future-work/submission-governance items rather than pretending they are fully solved.

## Minor concerns

1. The title is stronger and clearer, but it remains long. This is acceptable for SIVP if the journal template permits it.
2. AP50/AP75 should remain explicitly labelled project-local wherever possible.
3. If final figures are redrawn externally, ensure they do not imply causal gating or physical sensor robustness.
4. A full Springer `sn-jnl` build and BibTeX closure still need local toolchain verification.
5. The guard results must not be used for future model or threshold selection without redefining the claim boundary.

## Editorial decision if reviewed now

I would still expect a major-revision pathway rather than direct acceptance, mainly because there is no external dataset and no COCO AP@[0.50:0.95] package. However, after V42 the paper is no longer merely validation-only: it now contains a locked same-dataset held-out guard evaluation. For SIVP, this makes the manuscript substantially more defensible if the authors keep the claims bounded.

## Recommended next actions before formal submission

1. Compile with the real Springer/SIVP `sn-jnl` class and complete BibTeX/cross-reference closure.
2. Replace the simple text schematics with polished vector artwork if time permits.
3. Run one final active-claim scan for terms such as `external generalization`, `independent public benchmark`, `robustness`, `optimal`, and `statistical significance`.
4. Confirm whether the current GitHub repository will be public at submission time.
5. If possible, document TriAir provider/version/license details in a short provenance note, even if the manuscript only names the dataset.
