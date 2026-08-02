# V81 reconciliation protocol

- Training: nine fresh 50-epoch runs under frozen V40 component-disjoint train/devval manifests.
- Evaluation: one COCO pass per retained `best.pt`; IoU 0.50:0.05:0.95, 101 recall points, maxDets 1/10/100, score threshold 0.001, NMS 0.6.
- Comparison: seed-matched V81 minus supplied V80 across six AP/AR metrics.
- Boundary: development-validation only; no independent-test or significance claim.
