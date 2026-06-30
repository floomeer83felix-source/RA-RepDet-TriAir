# Phase 3B Report

Phase 3B audited the existing random train/validation split for exact leakage, adjacent-frame risk, and near-duplicate visual similarity. It also corrects the Phase 3A dropout-ratio interpretation.

## Split Audit Outcome

Final automatic status: **CAUTION: near-duplicate or adjacent-frame review required**

Key findings:

- Train samples: 8391
- Validation samples: 2098
- Identical resolved paths across train/val: 0
- Exact cross-split SHA256 duplicate `.npy` pairs: 0
- Numeric ids were parseable from filenames.
- Fraction of validation ids with a train id within +/-1: 0.973308
- Fraction of validation ids with a train id within +/-2: 0.994280
- RGB signature nearest-neighbor median Hamming distance: 8.000000
- Fraction of validation samples with RGB signature distance <= 16: 0.823642

Interpretation:

- There is no automatic evidence of exact byte-level train/validation duplication.
- The split is still high-risk for adjacent-frame or near-duplicate leakage because most validation ids have neighboring train ids and the nearest RGB signatures are often very close.
- The RGB perceptual signature is a screening tool only; it does not prove leakage by itself.
- Human review is required for `runs/split_integrity_manual_review.csv` and the local-only panels in `runs/local_split_audit_panels/`.

## Corrected E2/E4 Positioning

The Phase 3A dropout-ratio ablation does not identify a universally dominant ratio.

- E2 (`p=0.15`) has the strongest full-modality AP50/AP75.
- E4 (`p=0.20`) has the strongest P@0.50/F1@0.50 and the strongest AP50 under `w/o RGB`, `w/o Thermal`, and `w/o Event`.
- For an accuracy-first main result, retain E2.
- For a robustness-first operating point, report E4 as a separate variant.
- Mean missing-modality AP50 is an arithmetic robustness summary, not a standard detection metric.

## Recommendation

Because the split audit status is **CAUTION**, do not begin manuscript drafting or final 100-epoch runs until the nearest-pair review is resolved.

Recommended next action:

1. Manually inspect the top 50 closest cross-split pairs in `runs/split_integrity_manual_review.csv`.
2. If adjacent-frame leakage is confirmed, create a grouped or sequence-aware split before final training.
3. If manual review clears the nearest pairs, document the review decision and then run a controlled seed-replication of E2 versus E4 before final model selection.

