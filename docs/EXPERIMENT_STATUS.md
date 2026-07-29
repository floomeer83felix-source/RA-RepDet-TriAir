# Experiment Status

Updated: 2026-07-29

## Active status

`V79_SINGLE_MODALITY_EVALUATOR_ONLY_CODE_READY_LOCAL_CHECKPOINT_EXECUTION_PENDING`

## Closed submission items

1. Competing interests: the authors declare no competing interests.
2. TriAir source: untagged provider `triair.zip`, Drive file ID `1w71v6n41yqjP7BCr9ni4JdcxMnQ2ocR0`, Last-Modified 2025-11-21.
3. Archive audit: 20,240 paths/sizes/CRC32 values compared; missing 0, extra 0, different 0.
4. Runtime representation: provider-supplied `(301,391,5)` `uint8` arrays; only HWC-to-CHW, normalization, YOLO-to-`xyxy`, and foreground remapping occur at runtime.
5. Split provenance: initial 8,391/2,098 seed-0 random split is project-generated and non-official; final results use component-disjoint manifests.
6. Count boundary: paper-reported 24,223 vehicles and current-archive 30,634 valid label lines remain distinct; the 6,411 difference is unresolved.
7. Redistribution: upstream MIT statement applies to code; no explicit dataset-archive license was located, so data are not redistributed.

## V79 evaluator-only completion

The evaluator contract now reports:

- COCO AP@[0.50:0.95];
- AP50 and AP75;
- AR1, AR10, and AR100;
- checkpoint SHA256;
- frozen validation-manifest SHA256.

A fail-closed nine-checkpoint queue was added at `rarepdet/tools/run_v79_single_modality_eval_only.py`. It verifies the dataset root, the component-disjoint validation manifest, and all nine retained `best.pt` files before running inference. It contains no training entrypoint and does not access the guard partition.

The current ChatGPT environment does not contain `D:\download\triair` or the nine retained checkpoints, so no new AP/AR value has been generated or inferred. Execute on the authorized local workspace:

```powershell
python rarepdet/tools/run_v79_single_modality_eval_only.py --data D:\download\triair --device cuda --resume
```

## Validation

- V79 Python syntax compile: `PASS`;
- V79 source-contract tests: `2 passed`;
- preflight missing-input behavior: `PASS`;
- new training: `none`;
- new checkpoint evaluation in this environment: `none`.

## Manuscript status

The V78 15-page manuscript remains authoritative until all nine standardized evaluator JSON files are complete and reconciled against the supplied V77 AP50/AP75 rows. Existing values must not be silently overwritten.

## Scientific boundary

The development-validation, locked internal holdout, and supervised exposed-MM-UAV-devval boundaries remain unchanged. The evaluator-only pass does not convert any internal result into independent public-test evidence.
