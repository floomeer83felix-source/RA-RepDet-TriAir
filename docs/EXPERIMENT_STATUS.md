# Experiment Status

## M3OT supervised six-seed experiment complete (2026-09-25)

All six matched RGB+thermal runs completed 50/50 epochs on official M3OT
train/val. Best checkpoints were selected by val AP50 and then re-evaluated
under the same deterministic CUDA settings; all four COCO metrics matched
the saved best-epoch metrics exactly. The final six-row CSV, sample-SD
summary, paired AP differences, fixed-threshold counts, and three preselected
qualitative scenes are under `runs/m3ot_supervised_rgbt_v1/results/` locally.
Lightweight result tables and the report are tracked in
`reproducibility/m3ot_supervised_rgbt_v1/results/`.

| Model | AP mean +/- sample SD | AP50 mean +/- sample SD | AP75 mean +/- sample SD | AR100 mean +/- sample SD |
| --- | ---: | ---: | ---: | ---: |
| Early RGB+thermal | 0.2095 +/- 0.0155 | 0.5028 +/- 0.0290 | 0.1239 +/- 0.0209 | 0.3482 +/- 0.0186 |
| Dynamic RGB+thermal | 0.2380 +/- 0.0156 | 0.5533 +/- 0.0128 | 0.1518 +/- 0.0231 | 0.3792 +/- 0.0142 |

Paired dynamic-minus-early AP is +0.041268, +0.020828, and +0.023166 for
seeds 0, 1, and 2; mean +0.028421 +/- 0.011187 sample SD. This is a
descriptive supervised train/val result, not a blind independent-test or
significance claim. At score >= 0.25, seed-0 dynamic routing has higher
recall but lower precision than seed-0 early fusion; per-seed TP/FP/FN/P/R
remain visible in the CSV. The M3OT public test split was not accessed.

## M3OT supervised checkpoint resume (2026-09-24 22:24 CST)

The first queue completed `early_seed0` (50/50 epochs; best epoch 40) and
`reliability_rgbt_seed0` through epoch 23. During dynamic epoch 24, the
Windows/PyTorch process exited with native code `-1073740791`; the remaining
four runs did not start. The epoch-23 `last.pt` loaded successfully and
contains model, optimizer, and RNG states matching the status/history files.
The unchanged six-run queue has now resumed from dynamic epoch 24, with
original crash logs preserved and new output in
`runs/m3ot_supervised_rgbt_v1/orchestrator.resume2.stdout.log`.
Final six-seed results remain pending. Do not interpret the partial seed-0
comparison as a final experimental conclusion.

## M3OT supervised run started (2026-09-24)

`M3OT_SUPERVISED_RGBT_SIX_SEED_RUNNING`: the read-only RGB/IR/GT audit and
eight-sample visual review passed. Official train has 8,630 usable RGB/IR
pairs and 111,678 vehicle boxes; val has 1,200 pairs and 13,781 boxes. One
official train RGB frame (`1-07/000451`) has no IR pair and is excluded.
RGB and IR are frame-paired but not perfectly pixel-aligned; GT remains in
RGB coordinates. There is no train/val frame overlap.

The matched 50-epoch queue started at 2026-09-24 09:48 CST with
`early_seed0`. The six runs are sequential and resumable. Run artifacts and
the orchestrator log stay local under `runs/m3ot_supervised_rgbt_v1/`.
Final AP, paired differences, counts, CSVs, and qualitative figures are
**pending**; no result or model superiority is claimed yet. The public M3OT
test split, TriAir archival guard, and frozen manuscript results were not
accessed or changed for this experiment.

## User-authorized M3OT experiment (2026-09-24)

`M3OT_SUPERVISED_RGBT_SIX_SEED_AUTHORIZED` is the active experiment. It
compares RGB+thermal early fusion with RGB+thermal dynamic routing on official
M3OT train/val, three matched seeds, from-scratch initialization, 50 epochs
per run, and one shared training/evaluation protocol. Pairing and qualitative
GT review are required before GPU training. V88 manuscript release audit is
deferred, not completed. The prior exploratory M3OT zero-shot and
inference-only scale-adapter results are not supervised baseline results and
must not be mixed with this experiment.

Updated: 2026-09-09

## Active status

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_COMPLETE`

V87 integrated the authoritative V81 single-modality evidence and V86 matched RGB+thermal versus RGB+thermal+event dynamic-gating comparison into the active manuscript. No new training, inference, evaluation, tuning, checkpoint selection, historical-holdout access, or V86 outer-fold access occurred.

## Integrated TriAir evidence

| System | AP@[.50:.95] | AP50 | AP75 | AR100 |
| --- | ---: | ---: | ---: | ---: |
| RGB-only | `0.4473 +/- 0.0033` | `0.7674 +/- 0.0036` | `0.4428 +/- 0.0098` | `0.5897 +/- 0.0024` |
| Thermal-only | `0.5196 +/- 0.0196` | `0.8320 +/- 0.0154` | `0.5776 +/- 0.0244` | `0.6473 +/- 0.0132` |
| Event-only | `0.1949 +/- 0.0012` | `0.3657 +/- 0.0032` | `0.1943 +/- 0.0049` | `0.3558 +/- 0.0067` |
| RGB+thermal dynamic | `0.6912 +/- 0.0280` | `0.9461 +/- 0.0028` | `0.8409 +/- 0.0241` | `0.7673 +/- 0.0232` |
| RGB+thermal+event dynamic | `0.7251 +/- 0.0121` | `0.9475 +/- 0.0003` | `0.8742 +/- 0.0081` | `0.7917 +/- 0.0098` |

Paired tri-modal minus RGB+thermal AP differences are `-0.0110`, `+0.0657`, and `+0.0471` for seeds 0, 1, and 2. Mean paired AP is `+0.0339 +/- 0.0400`, with positive gains in `2/3` seeds. AP50 is nearly unchanged; the descriptive gain is concentrated in AP75 and AR100.

## Scientific conclusion

Event-only is the weakest standalone TriAir detector, but the matched V86 comparison supports complementary event contribution on average when event is fused with RGB and thermal. The result is descriptive: it does not establish uniform per-seed improvement, statistical significance, universal event utility, or calibrated sensor-health estimation.

During V87 integration, an older manuscript section containing idealized V73 reference values was detected and corrected to the frozen actual V73 MM-UAV results:

- Scratch Equal AP: `0.2234 +/- 0.0073`;
- TriAir Init Equal AP: `0.2178 +/- 0.0020`;
- TriAir Init Reliability AP: `0.2151 +/- 0.0090`.

The MM-UAV conclusion is therefore restored to: supervised alignment recovers useful performance, while source initialization and reliability-aware fusion do not improve the three-seed mean under the frozen V73 schedule.

## Manuscript validation

- local integrated authoring PDF: 13 pages;
- two consecutive pdfLaTeX passes: PASS;
- undefined citations/references: 0;
- overfull boxes after table correction: 0;
- rendered-page audit: PASS;
- V85 qualitative figure asset: unchanged.

## Next task

`V88_MANUSCRIPT_RELEASE_CANDIDATE_CONSISTENCY_AUDIT_AUTHORIZED`

V88 is a final manuscript consistency and submission-readiness task only. No new experiment is authorized.
