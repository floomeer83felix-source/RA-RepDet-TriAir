# Experiment Status

Updated: 2026-07-29

## Active status

`V78_SUBMISSION_PROVENANCE_AND_DECLARATIONS_CLOSED`

## Closed submission items

1. Competing interests: the authors declare no competing interests.
2. TriAir source: untagged provider `triair.zip`, Drive file ID `1w71v6n41yqjP7BCr9ni4JdcxMnQ2ocR0`, Last-Modified 2025-11-21.
3. Archive audit: 20,240 paths/sizes/CRC32 values compared; missing 0, extra 0, different 0.
4. Runtime representation: provider-supplied `(301,391,5)` `uint8` arrays; only HWC-to-CHW, normalization, YOLO-to-`xyxy`, and foreground remapping occur at runtime.
5. Split provenance: initial 8,391/2,098 seed-0 random split is project-generated and non-official; final results use component-disjoint manifests.
6. Count boundary: paper-reported 24,223 vehicles and current-archive 30,634 valid label lines remain distinct; the 6,411 difference is unresolved.
7. Redistribution: upstream MIT statement applies to code; no explicit dataset-archive license was located, so data are not redistributed.

## Manuscript validation

- PDF pages: `15`;
- two pdfLaTeX passes: `PASS`;
- undefined citations/references: `0`;
- overfull boxes: `0`;
- rendered-page audit: `PASS`;
- PDF preflight: `PASS`;
- new training or evaluation: `none`.

## Article evaluation

Updated readiness: `4.5 / 5`. Major scientific, competing-interest, and local-data-identity blockers are closed. Remaining work is final author/institution metadata, current journal-format checks, and optional evaluator-only completion of missing single-modality COCO AP/AR and checkpoint identities.

## Scientific boundary

The development-validation, locked internal holdout, and supervised exposed-MM-UAV-devval boundaries remain unchanged. The provenance audit does not convert any internal result into independent public-test evidence.
