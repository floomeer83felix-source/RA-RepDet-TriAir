# Experiment Status

Updated: 2026-07-30

## Active status

`V81_RETRAINING_AND_STANDARDIZED_EVALUATION_COMPLETE_MATERIAL_RECONCILIATION_DIFFERENCE`

## Closed submission items

1. Competing interests: the authors declare no competing interests.
2. TriAir source: untagged provider `triair.zip`, Drive file ID `1w71v6n41yqjP7BCr9ni4JdcxMnQ2ocR0`, Last-Modified 2025-11-21.
3. Archive audit: 20,240 paths/sizes/CRC32 values compared; missing 0, extra 0, different 0.
4. Runtime representation: provider-supplied `(301,391,5)` `uint8` arrays; only HWC-to-CHW, normalization, YOLO-to-`xyxy`, and foreground remapping occur at runtime.
5. Split provenance: initial 8,391/2,098 seed-0 random split is project-generated and non-official; final results use component-disjoint manifests.
6. Count boundary: paper-reported 24,223 vehicles and current-archive 30,634 valid label lines remain distinct; the 6,411 difference is unresolved.
7. Redistribution: upstream MIT statement applies to code; no explicit dataset-archive license was located, so data are not redistributed.

## Supplied standardized single-modality metrics

The user supplied nine standardized rows containing AP@[0.50:0.95], AP50, AP75, AR1, AR10, and AR100. Independent recomputation gives:

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.3073 ± 0.0065 | 0.6527 ± 0.0086 | 0.3807 ± 0.0085 | 0.2857 ± 0.0055 | 0.4550 ± 0.0070 | 0.4830 ± 0.0070 |
| Thermal-only | 0.4633 ± 0.0085 | 0.8497 ± 0.0080 | 0.6263 ± 0.0111 | 0.3877 ± 0.0065 | 0.5973 ± 0.0085 | 0.6320 ± 0.0090 |
| Event-only | 0.1020 ± 0.0060 | 0.3347 ± 0.0125 | 0.1260 ± 0.0080 | 0.1220 ± 0.0040 | 0.2437 ± 0.0075 | 0.2710 ± 0.0080 |

All nine AP50/AP75 pairs match the V77 supplied values exactly at three decimal places. The table does not contain checkpoint SHA256, checkpoint epoch, split SHA256, runtime identity, or original evaluator JSON records; these fields were not inferred. Compact evidence is stored under `runs/v80_supplied_standardized_single_modality_metrics/`.

## V80 evaluator-only execution

The evaluator contract reports:

- COCO AP@[0.50:0.95];
- AP50 and AP75;
- AR1, AR10, and AR100;
- checkpoint SHA256;
- frozen validation-manifest SHA256.

A fail-closed nine-checkpoint queue was added at `rarepdet/tools/run_v79_single_modality_eval_only.py`. It verifies the dataset root, the component-disjoint validation manifest, and all nine retained `best.pt` files before running inference. It contains no training entrypoint and does not access the guard partition.

The authorized local RTX 3090 environment was checked on 2026-07-30. The TriAir root and frozen V40 validation manifest are present, and the manifest SHA256 is `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`. CUDA, PyTorch, torchvision, and pycocotools are operational.

The original V76 checkpoint preflight found all nine required `weights/best.pt` files missing under both repository worktrees and stopped before inference as required.

## V81 retraining authorization

On 2026-07-30 the user explicitly authorized fresh training of RGB-only, thermal-only, and event-only models for seeds 0, 1, and 2. The fixed nine-run queue uses the V40 component-disjoint train/development-validation manifests, 50 epochs, batch size 4, 640-pixel inputs, AdamW at `1e-4`, no modality dropout, and CUDA on the RTX 3090.

The regenerated checkpoints are new V81 outputs. They are not assumed to be byte-identical to, or the original source of, the V77 supplied metrics. The supplied standardized table is recorded independently and does not convert new V81 checkpoints into recovered V77 identities.

The serial queue started at `2026-07-30T08:04:13+08:00` and completed on 2026-08-01. All nine runs reached 50 epochs and produced retained `best.pt` files. The V79 evaluator then completed 9/9 one-pass COCO evaluations. Every result records checkpoint epoch and SHA256, the common split SHA256 `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`, and inference runtime.

V81 three-seed means are RGB `0.4473` AP@[.50:.95], thermal `0.5196`, and event `0.1949`. Seed-matched comparison against the supplied V77/V80 rows found material differences, not display rounding. Fresh V81 checkpoints therefore remain a separate replication evidence set and are not treated as recovered V77/V80 identities.

## Validation

- supplied metric rows: `9/9`;
- independent mean/sample-SD arithmetic: `PASS`;
- AP50/AP75 reconciliation against V77: `PASS`, exact at three decimals;
- V80 draft PDF pages: `16`;
- two pdfLaTeX passes: `PASS`;
- undefined citations/references: `0`;
- overfull boxes: `0`;
- rendered-page audit: `PASS`;
- checkpoint/evaluator identity fields supplied with table: `no`;
- guard access: `none`.
- V81 training completion: `9/9` at 50 epochs;
- V81 standardized COCO evaluation: `9/9`;
- V81 checkpoint SHA256 records: `9/9`;
- V81 versus supplied-table reconciliation: `COMPLETE`, material differences present.

## Manuscript status

A 16-page V80 draft integrating the supplied standardized metric table has been built and visually audited outside the repository entrypoint. V81 identity evidence is now complete, but its metrics differ materially from the supplied table. The V78 root manuscript remains authoritative pending an explicit evidence-source decision. Existing V77/V80 values were not silently overwritten.

## Scientific boundary

The development-validation, locked internal holdout, and supervised exposed-MM-UAV-devval boundaries remain unchanged. Neither the supplied metric table nor the evaluator/retraining work converts any internal result into independent public-test evidence. No statistical-significance claim is made.
