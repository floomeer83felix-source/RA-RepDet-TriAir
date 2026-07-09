# V41 SIVP Claim Ledger

Generated: 2026-07-09

## Source of Truth

- Three-seed interim development-validation package: `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.md/json/csv`.
- V41 interim status: `docs/V41_INTERIM_DEVVAL_STATUS.md`.
- Fresh seed1 source lock: `runs/v41_q1_upgrade/seed1/source_lock_seed1.md/json`.
- V40 seed0/seed2 source: `runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json`.

## Allowed Core Claim

A reliability-aware RGB--thermal--event fusion front end with modality dropout p=0.15 showed positive descriptive paired deltas over a matched early-fusion baseline across seed0, seed1, and seed2 on the frozen V40 component-disjoint development-validation split.

Allowed quantitative wording:

- Precision mean paired delta: +0.011629, sample SD 0.016501, n=3 seed pairs.
- Recall mean paired delta: +0.024487, sample SD 0.026581, n=3 seed pairs.
- F1 mean paired delta: +0.018524, sample SD 0.006208, n=3 seed pairs.
- AP50 mean paired delta: +0.016064, sample SD 0.005699, n=3 seed pairs.
- AP75 mean paired delta: +0.064657, sample SD 0.016415, n=3 seed pairs.

Required qualifier: these are **three-seed interim development-validation descriptive** results.

## Disallowed or Unsafe Claims

Do not claim any of the following:

- independent test performance;
- external generalization;
- statistical significance;
- final manuscript aggregate;
- optimal dropout probability;
- physical sensor-failure robustness;
- calibrated sensor reliability;
- causal modality importance;
- COCO AP50:95 performance;
- public dataset redistribution rights or license compliance unless author-confirmed.

## Claims Requiring Replacement in the Current Draft

The current LaTeX draft still contains older R4 p=0.20 / block64_guard16 / seed0,2 language. For the SIVP validation-only revision, replace that narrative with V40/V41 p=0.15 seed0/1/2 wording.

High-risk older phrases to remove or rewrite:

- `R4 configuration uses dropout probability p=0.20`
- `block64/guard16 split`
- `R4 headline values are means across seeds 0 and 2`
- `R4 is therefore the selected main variant`
- `Controlled clean-split ablation`
- `R0, R1, R2, and R4 variants` as the headline result
- any claim that p=0.20 is the manuscript headline

Preferred replacement entities:

- `matched early fusion`
- `reliability-aware p=0.15`
- `frozen V40 component-disjoint development-validation split`
- `seed0/seed1/seed2 paired development-validation evidence`
- `project-local AP50/AP75, not COCO AP50:95`

## Required Limitations Paragraph Content

The revised manuscript must explicitly state:

1. all main evidence is validation-only;
2. seed count is three paired seeds, not a full stability analysis;
3. no independent held-out test or external dataset is included;
4. no COCO mAP@[.50:.95] package is included;
5. mechanism ablations separating separate stems, gate, and dropout are not complete;
6. synthetic channel removal is not physical sensor-failure robustness;
7. TriAir provider/version/license/redistribution/synchronization details remain author-confirmation items;
8. label-quality audit remains incomplete.

## Reviewer Risk Mapping

| Likely reviewer concern | Manuscript response |
| --- | --- |
| No independent test | Admit validation-only and avoid generalization claims. |
| Only three seeds | Present mean ± sample SD as descriptive, not significance. |
| No COCO AP50:95 | State project-local AP50/AP75 and list COCO package as future work. |
| Gate/dropout confounding | Call the method a combined front-end/training configuration; do not isolate causal mechanism. |
| Dataset provenance incomplete | Move provider/license/version facts to author-confirmation items and avoid redistribution claims. |
| Synthetic missingness not real faults | Label it as synthetic zero-channel stress only. |
