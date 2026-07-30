# Experiment Status

Updated: 2026-07-30

## Active status

`V81_NINE_SINGLE_MODALITY_RETRAINING_AUTHORIZED_START_PENDING`

## Closed submission items

1. Competing interests: the authors declare no competing interests.
2. TriAir source: untagged provider `triair.zip`, Drive file ID `1w71v6n41yqjP7BCr9ni4JdcxMnQ2ocR0`, Last-Modified 2025-11-21.
3. Archive audit: 20,240 paths/sizes/CRC32 values compared; missing 0, extra 0, different 0.
4. Runtime representation: provider-supplied `(301,391,5)` `uint8` arrays; only HWC-to-CHW, normalization, YOLO-to-`xyxy`, and foreground remapping occur at runtime.
5. Split provenance: initial 8,391/2,098 seed-0 random split is project-generated and non-official; final results use component-disjoint manifests.
6. Count boundary: paper-reported 24,223 vehicles and current-archive 30,634 valid label lines remain distinct; the 6,411 difference is unresolved.
7. Redistribution: upstream MIT statement applies to code; no explicit dataset-archive license was located, so data are not redistributed.

## V80 evaluator-only execution

The evaluator contract now reports:

- COCO AP@[0.50:0.95];
- AP50 and AP75;
- AR1, AR10, and AR100;
- checkpoint SHA256;
- frozen validation-manifest SHA256.

A fail-closed nine-checkpoint queue was added at `rarepdet/tools/run_v79_single_modality_eval_only.py`. It verifies the dataset root, the component-disjoint validation manifest, and all nine retained `best.pt` files before running inference. It contains no training entrypoint and does not access the guard partition.

The authorized local RTX 3090 environment was checked on 2026-07-30. The TriAir root and frozen V40 validation manifest are present, and the manifest SHA256 is `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`. CUDA, PyTorch, torchvision, and pycocotools are operational.

The evaluator preflight found all nine required V76 `weights/best.pt` files missing under both repository worktrees. It stopped before inference as required. Exact paths are recorded in `runs/v79_single_modality_evaluator_completion/preflight.json` and `docs/TASK_BLOCKER.md`.

## V81 retraining authorization

On 2026-07-30 the user explicitly authorized fresh training of RGB-only, thermal-only, and event-only models for seeds 0, 1, and 2. The fixed nine-run queue uses the V40 component-disjoint train/development-validation manifests, 50 epochs, batch size 4, 640-pixel inputs, AdamW at `1e-4`, no modality dropout, and CUDA on the RTX 3090.

The regenerated checkpoints are new V81 outputs. They are not assumed to be byte-identical to, or the original source of, the V77 supplied metrics. V78 remains authoritative until 9/9 training, standardized evaluation, and transparent reconciliation complete.

## Validation

- V79 Python syntax compile: `PASS`;
- V79 source-contract tests: `3 passed`;
- preflight missing-input behavior: `PASS`;
- new training: `none`;
- new checkpoint inference: `none`;
- guard access: `none`.

## Manuscript status

The V78 15-page manuscript remains authoritative. No V80 manuscript was created because 0/9 standardized checkpoint evaluations completed. Existing values were not overwritten.

## Scientific boundary

The development-validation, locked internal holdout, and supervised exposed-MM-UAV-devval boundaries remain unchanged. The evaluator-only pass does not convert any internal result into independent public-test evidence.
