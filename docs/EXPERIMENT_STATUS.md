# Experiment Status

Updated: 2026-08-11

## Active status

`V84_JEI_CRITICAL_EVIDENCE_CLOSURE_COMPLETE`

V84 completed the required JEI evidence closure and integrated a new evidence-frozen manuscript source snapshot. All required computations completed or reached the preregistered transparent-stop condition. V84 did not access the locked 837-image internal holdout.

## V84 completion

- RGB+thermal baseline: seeds 0/1/2 complete, COCO AP `0.6843 +/- 0.0312`;
- matched gate-by-dropout channel-removal analysis: `48/48 COMPLETE`;
- gate-quality and controlled-corruption analysis: `30/30 COMPLETE`;
- component-cluster bootstrap: 12 checkpoints, 1,298 components, 5,000 replicates;
- published comparator: transparent stop because the pinned official implementation cannot satisfy the frozen split, evaluator, checkpoint-selection, and license contract without substantial adaptation;
- MM-UAV reproducibility: exact sequence, geometry, conversion, transfer, and evaluation details frozen;
- manuscript snapshot: `submission/v84_jei_evidence_manuscript/`, two-pass source-only pdfLaTeX compile successful;
- locked holdout access in V84: none.

The evidence narrows the reliability claim: dynamic gating improves nominal development-validation AP under component-aware uncertainty, but missing-event robustness is mainly attributable to modality-dropout training, and controlled corruption does not produce monotonic affected-modality down-weighting. Gate weights are task-driven fusion coefficients, not calibrated sensor-health probabilities. A positive isolated event contribution and same-protocol superiority over a published comparator are not established.

## V83 completion

- V81 weight identity: `9/9 PASS` for SHA256, epoch, input mode, seed, and model configuration;
- exact-identity fusion controls: `6/6 PASS` across matched early and reliability-aware seeds 0/1/2;
- efficiency benchmark: `15/15 COMPLETE` on RTX 3090, batch 1, 640x640, FP32, 50 warm-up and 200 synchronized measured iterations;
- dataset or label access: none;
- training or tuning: none;
- locked holdout access: none.

Reliability-aware fusion reports 6,593,293 parameters, 105.392 profiler GFLOPs, `22.2324 +/- 0.1879 ms` full-detector latency, and `44.9815 FPS`. Matched early fusion reports 6,591,609 parameters, 104.762 profiler GFLOPs, `22.0800 +/- 0.3082 ms`, and `45.2957 FPS`. The parameter, FLOP, and latency overhead is small, while peak CUDA memory is materially higher for reliability-aware fusion.

The V83 result corroborates but does not supersede the existing V82 efficiency table, whose timing protocol is stronger and whose raw-forward and detector-inference boundaries are separate. No V82 manuscript revision is created.

## Authoritative V81 single-modality results

Values are mean ± sample standard deviation over seeds 0, 1, and 2.

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.4473 ± 0.0033 | 0.7674 ± 0.0036 | 0.4428 ± 0.0098 | 0.1650 ± 0.0009 | 0.5225 ± 0.0036 | 0.5897 ± 0.0024 |
| Thermal-only | 0.5196 ± 0.0196 | 0.8320 ± 0.0154 | 0.5776 ± 0.0244 | 0.2035 ± 0.0081 | 0.5826 ± 0.0148 | 0.6473 ± 0.0132 |
| Event-only | 0.1949 ± 0.0012 | 0.3657 ± 0.0032 | 0.1943 ± 0.0049 | 0.0751 ± 0.0033 | 0.2694 ± 0.0014 | 0.3558 ± 0.0067 |

## Compatible multimodal-versus-thermal development-validation contrasts

| System | Metric | Mean delta | Sample SD | Positive seeds |
| --- | --- | ---: | ---: | ---: |
| Reliability-aware p=0.15 | AP | +0.1960 | 0.0329 | 3/3 |
| Reliability-aware p=0.15 | AP50 | +0.1215 | 0.0154 | 3/3 |
| Reliability-aware p=0.15 | AP75 | +0.2952 | 0.0349 | 3/3 |
| Matched early fusion | AP | +0.1606 | 0.0223 | 3/3 |
| Matched early fusion | AP50 | +0.1053 | 0.0199 | 3/3 |
| Matched early fusion | AP75 | +0.2314 | 0.0265 | 3/3 |

These remain descriptive component-disjoint development-validation comparisons under compatible standardized COCO definitions.

## Weight identity

- V81 training completion: `9/9`, exactly 50 epochs each;
- standardized COCO evaluation: `9/9`;
- checkpoint epoch and SHA256: `9/9`;
- checkpoint registry: `runs/v81_single_modality_retraining_reconciliation/checkpoint_manifest.json`;
- common development-validation split SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`;
- historical V77/V80 supplied rows: reconciliation-only, never primary evidence.

## V83 reordered work

1. **Weight integrity preflight:** verify all nine local V81 `best.pt` files against the archived hashes and metadata.
2. **Efficiency benchmark:** fixed RTX-3090, batch-1, 640x640, FP32 synchronized latency/memory/parameter benchmark without labeled-data access.
3. **Evidence review:** decide whether the efficiency result materially improves the lightweight claim before changing the manuscript.
4. **Locked holdout:** optional and separately authorization-gated. No holdout access is authorized by this planning update.
5. **Submission closure:** final author metadata and live journal/portal verification.

Detailed plan:

```text
docs/CODEX_V83_POST_V81_WEIGHT_TASK_PLAN.md
```

## V82 manuscript validation

- active root manuscript: V82;
- PDF pages: `16`;
- two pdfLaTeX passes: `PASS`;
- undefined citations/references: `0`;
- overfull boxes: `0`;
- PDF preflight: `PASS`;
- rendered-page audit: `16/16 PASS`.

## Scientific boundary

The component-disjoint validation partition participates in checkpoint retention, the 837-image holdout is internal and was already used in V42, and MM-UAV uses supervised target-domain labels on an exposed devval split. No significance, independent public-test, calibrated sensor-reliability, or physical sensor-failure claim is made.
