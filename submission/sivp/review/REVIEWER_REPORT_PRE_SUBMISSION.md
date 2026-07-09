# Pre-Submission Reviewer Report for SIVP

Generated: 2026-07-09

## Overall recommendation

**Major revision before formal submission.**

The manuscript is now substantially more coherent than the earlier validation-only draft. The core story is appropriate for a signal/image/video processing venue: a lightweight RGB--thermal--event fusion front end is compared with a matched early-fusion baseline under a stricter component-disjoint development-validation protocol. The paper is strongest when it presents the result as bounded, auditable development-validation evidence rather than as deployment-ready robustness or broad generalization.

## Summary of the manuscript

The paper proposes RA-RepDet, a lightweight RGB--thermal--event UAV vehicle detector built on RepViT-M0.9, FPN, and FCOS. The active comparison is reliability-aware fusion with modality dropout p=0.15 versus matched early fusion, evaluated over seed0/seed1/seed2 on a frozen V40 component-disjoint development-validation split. The manuscript reports descriptive positive paired deltas for F1, AP50, and AP75 and explicitly states that AP50/AP75 are project-local single-class metrics rather than COCO AP50:95.

## Strengths

1. **Clearer evidence boundary.** The manuscript no longer overclaims independent-test generalization, physical sensor-failure robustness, statistical significance, or optimal dropout.
2. **Matched active comparison.** The main result compares reliability-aware fusion and early fusion under the same detector stack, split, evaluator, and seeds.
3. **Improved split-integrity discussion.** The component-disjoint validation protocol is presented as part of the contribution and not merely as a preprocessing detail.
4. **Three paired seeds.** The addition of seed1 makes the result more credible than a two-seed report, even though it remains descriptive.
5. **Declarations and availability.** Author metadata, funding, competing interests, contributions, acknowledgments, data availability, and code availability are now present.

## Major concerns

### 1. Validation-only evidence remains the central scientific limitation

The paper has no independent test set and no external dataset evaluation. This is now honestly stated, but reviewers may still judge the empirical evidence as insufficient for strong conclusions. The manuscript should keep the current restrained wording throughout.

**Action taken:** The abstract, introduction, results, discussion, limitations, and conclusion were kept within a validation-only claim boundary.

### 2. Figure placeholders were not acceptable for submission

Earlier manuscript versions contained explicit `Final artwork pending` placeholder figures. This would be a desk-review risk.

**Action taken:** The placeholders were replaced by simple in-manuscript schematic/table figures for architecture, split workflow, and paired deltas. Optional high-resolution artwork can still replace them later, but the manuscript no longer contains explicit placeholder figures.

### 3. Tables contained stale split and seed descriptions

Older table content still referred to block64/guard16 and seeds 0/2. That conflicted with the V41 p=0.15 seed0/1/2 narrative.

**Action taken:** Table 1 was aligned to V40 component-disjoint evidence and Table 2 was aligned to seed0/seed1/seed2 with reliability-aware p=0.15.

### 4. Auxiliary analyses risk distracting from the active claim

External YOLO, synthetic missingness, gate weights, and qualitative materials are not currently the manuscript's strongest evidence. Presenting them as main results would invite reviewer criticism.

**Action taken:** These materials are now described only as contextual or pending-review evidence, while the three-seed paired development-validation table remains the active quantitative claim.

### 5. Data-governance details remain incomplete

The manuscript names TriAir as a public dataset and avoids redistributing original files, which is acceptable as a concise availability statement. However, provider version, license, redistribution conditions, and synchronization details remain only partially resolved.

**Action taken:** The limitations section keeps these as future-work/submission-governance items rather than pretending they are fully solved.

## Minor concerns

1. The title is now stronger and clearer, but it remains long. This is acceptable for SIVP if the journal template permits it.
2. The abstract is careful but perhaps slightly defensive. This is preferable to overclaiming given the evidence state.
3. AP50/AP75 should remain explicitly labelled project-local wherever possible.
4. If final figures are redrawn externally, ensure they do not imply causal gating or physical sensor robustness.
5. A full Springer `sn-jnl` build and BibTeX closure still need local toolchain verification.

## Editorial decision if reviewed now

I would not recommend acceptance without revision, mainly because of the validation-only design and missing independent-test evidence. However, I would likely recommend **major revision rather than rejection** if the manuscript is submitted to a venue that accepts carefully scoped engineering validation studies. The current version is substantially safer for SIVP than the earlier draft because the claims, tables, and limitations are now internally consistent.

## Recommended next actions before formal submission

1. Compile with the real Springer/SIVP `sn-jnl` class and complete BibTeX/cross-reference closure.
2. Replace the simple text schematics with polished vector artwork if time permits.
3. Run one final active-claim scan for terms such as `independent test`, `external generalization`, `robustness`, `optimal`, and `statistical significance`.
4. Confirm whether the current GitHub repository will be public at submission time.
5. If possible, document TriAir provider/version/license details in a short provenance note, even if the manuscript only names the dataset.
