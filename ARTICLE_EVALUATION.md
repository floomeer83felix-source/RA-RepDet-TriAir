# RA-RepDet manuscript evaluation - V78 provenance and declaration closure

## Overall recommendation

**Technically ready for final submission preparation, subject to journal-format and author-metadata checks.** V78 closes the two principal non-experimental blockers remaining after V77: the authors now declare no competing interests, and the exact local TriAir source is identified by a complete archive-entry audit rather than a generic provenance caveat.

The local study copy is recorded as the untagged provider `triair.zip`, Google Drive file ID `1w71v6n41yqjP7BCr9ni4JdcxMnQ2ocR0`, Last-Modified 2025-11-21, archive size 3,551,150,083 bytes. The author audit compared all 20,240 paths, sizes, and CRC32 values and found zero missing, extra, or different entries. The manuscript also distinguishes the paper-reported 24,223 vehicles from the current archive's 30,634 valid label lines; the unexplained difference of 6,411 is disclosed rather than reconciled by assumption.

## Scorecard

| Dimension | Score | Assessment |
| --- | ---: | --- |
| Novelty and relevance | 4.1 / 5 | Lightweight tri-modal dynamic fusion remains relevant. |
| Method clarity | 4.5 / 5 | Architecture, runtime data handling, controls, splits, and transfer boundaries are explicit. |
| Experimental rigor | 4.3 / 5 | Three-seed systems, six fusion controls, locked holdout, transfer study, and single-modality baselines are present. |
| Evidence traceability | 4.7 / 5 | Provider archive identity, local audit scope, split origin, and result sources are now directly recorded. |
| Statistical support | 3.9 / 5 | Three paired seeds remain descriptive rather than inferential. |
| Reproducibility | 4.6 / 5 | Frozen manifests, code paths, provider commit, archive identity, and runtime transformations are documented. |
| Writing and organization | 4.6 / 5 | Data provenance and count discrepancies are clearly separated from experimental claims. |
| Submission readiness | 4.4 / 5 | Competing interests and data provenance are closed; final author/institution fields and optional evaluator completion remain. |

**Overall: 4.5 / 5.** The manuscript is scientifically coherent and suitable for submission packaging. Remaining items are primarily administrative or optional evidence enrichment.

## Verified provenance interpretation

1. The provider paper reports 10,489 synchronized frames and 24,223 annotated vehicles.
2. The current untagged provider archive contains 10,489 five-channel arrays and 9,751 YOLO text files according to the complete local audit.
3. The current archive contains 30,634 valid single-class label lines. This number must not be described as the provider paper's official vehicle count.
4. No offline raw-to-TriAir conversion was found in this project. Runtime handling is limited to HWC-to-CHW, float conversion and normalization, normalized-YOLO-to-absolute-`xyxy`, and foreground label remapping.
5. The initial 8,391/2,098 local split is project-generated with seed 0 and an 80:20 ratio; it is not an official provider split and is superseded by the component-disjoint protocol for reported results.
6. The upstream repository identifies the same Google Drive file and documents the five-channel order and YOLO format. The provider-code mirror was checked against commit `8f4e31ed64f1f2fe019d4706670fc4560c0b2e23`, apart from line-ending normalization.

## Remaining reviewer concerns

1. The main development partition participates in checkpoint retention.
2. The locked holdout is internal to the same provider archive.
3. Three seeds support descriptive consistency but not strong statistical inference.
4. The V77 single-modality records still lack AP@[0.50:0.95], AR metrics, checkpoint hashes, and original evaluator files.
5. No explicit dataset-archive license was located, so non-redistribution must remain.

## Final closure checklist

1. Confirm final author names, affiliations, corresponding author, and ORCID fields.
2. Preserve the explicit 24,223-versus-30,634 distinction.
3. Preserve the statement that the original 8:2 split is project-generated, not official.
4. Optionally run evaluator-only passes on the nine retained single-modality checkpoints; do not retrain or tune.
5. Check the current target journal's live formatting and submission requirements immediately before upload.

## Acceptance outlook

The major scientific and provenance objections have been addressed. Reviewers may still request a truly independent sensor-compatible test set, more training seeds, or complete single-modality COCO/AR artifacts, but the paper no longer has an unresolved basic-control, competing-interest, or local-data-identity gap.
