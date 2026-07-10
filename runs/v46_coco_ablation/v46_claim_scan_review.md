# V46 Claim Scan Review

Generated: 2026-07-10T22:28:49+08:00

Files scanned: 15

Phrase matches: 7

Unresolved affirmative matches: 0

| File | Line | Phrase | Classification | Context |
| --- | ---: | --- | --- | --- |
| `runs/v46_coco_ablation/ablation_claim_boundary.md` | 13 | statistical significance | guardrail_or_negation | - The new ablation contrasts have one seed and do not establish statistical significance. |
| `runs/v46_coco_ablation/ablation_claim_boundary.md` | 14 | external generalization | guardrail_or_negation | - The held-out guard is same-dataset evidence and is not an independent public benchmark or external generalization test. |
| `runs/v46_coco_ablation/ablation_claim_boundary.md` | 14 | independent public benchmark | guardrail_or_negation | - The held-out guard is same-dataset evidence and is not an independent public benchmark or external generalization test. |
| `runs/v46_coco_ablation/ablation_claim_boundary.md` | 15 | optimal dropout | guardrail_or_negation | - No result establishes optimal dropout, calibrated sensor reliability, or real sensor-fault robustness. |
| `runs/v46_coco_ablation/ablation_claim_boundary.md` | 15 | calibrated sensor reliability | guardrail_or_negation | - No result establishes optimal dropout, calibrated sensor reliability, or real sensor-fault robustness. |
| `runs/v46_coco_ablation/ablation_claim_boundary.md` | 15 | real sensor-fault robustness | guardrail_or_negation | - No result establishes optimal dropout, calibrated sensor reliability, or real sensor-fault robustness. |
| `runs/v46_coco_ablation/ablation_claim_boundary.md` | 16 | COCO proof | guardrail_or_negation | - COCO-style metric reporting is an evaluation convention, not COCO proof of generalization or robustness. |

Result: `PASS`. Every match is an explicit denial, caution, limitation, or claim-boundary guardrail; no affirmative prohibited claim was found.
