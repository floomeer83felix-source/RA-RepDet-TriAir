# Phase 7C Table Insertion Report

Generated: 2026-07-04
Workspace: `E:\RepViT-main`
Baseline commit inspected: `48d67fd267c199364adff4c14a9ec9c8f842dcf5`

## Summary

- Table validation outcome: pass.
- Seven SIVP table fragments were generated exclusively from the existing `manuscript/tables/` CSV files.
- Source CSV values were not sorted, rounded, recomputed, filtered, averaged, or otherwise altered.
- Table placeholders were replaced with `\input{../tables/...}` references in `submission/sivp/tex/ra_repdet_sivp.tex`.

## Source To Fragment Mapping

| Table | Source CSV | Fragment | Source rows | Rendered rows | Numeric-token comparison | Row representation |
| --- | --- | --- | ---: | ---: | --- | --- |
| Table 1 | `manuscript/tables/Table_1_dataset_and_clean_split.csv` | `submission/sivp/tables/Table_1_dataset_and_clean_split.tex` | 12 | 12 | pass: source=20 rendered=20 | pass |
| Table 2 | `manuscript/tables/Table_2_implementation_and_reproducibility.csv` | `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex` | 12 | 12 | pass: source=25 rendered=25 | pass |
| Table 3 | `manuscript/tables/Table_3_controlled_ablation.csv` | `submission/sivp/tables/Table_3_controlled_ablation.tex` | 20 | 20 | pass: source=175 rendered=175 | pass |
| Table 4 | `manuscript/tables/Table_4_missing_modality_robustness.csv` | `submission/sivp/tables/Table_4_missing_modality_robustness.tex` | 27 | 27 | pass: source=136 rendered=136 | pass |
| Table 5 | `manuscript/tables/Table_5_rgb_only_external_baseline.csv` | `submission/sivp/tables/Table_5_rgb_only_external_baseline.tex` | 14 | 14 | pass: source=121 rendered=121 | pass |
| Table 6 | `manuscript/tables/Table_6_efficiency_and_convergence.csv` | `submission/sivp/tables/Table_6_efficiency_and_convergence.tex` | 12 | 12 | pass: source=57 rendered=57 | pass |
| Table 7 | `manuscript/tables/Table_7_reliability_weight_audit.csv` | `submission/sivp/tables/Table_7_reliability_weight_audit.tex` | 8 | 8 | pass: source=96 rendered=96 | pass |

## Verification Outcomes

| Check | Status | Notes |
| --- | --- | --- |
| all 7 input fragments exist | pass |  |
| body contains zero TABLE PLACEHOLDER strings | pass | count=0 |
| body contains 7 table fragment inputs | pass | count=7 |
| all 7 source CSVs are unchanged by this task | pass | no source CSV diff |
| Table 1 source rows represented exactly once | pass | source_rows=12; represented_once=12 |
| Table 2 source rows represented exactly once | pass | source_rows=12; represented_once=12 |
| Table 3 source rows represented exactly once | pass | source_rows=20; represented_once=20 |
| Table 4 source rows represented exactly once | pass | source_rows=27; represented_once=27 |
| Table 5 source rows represented exactly once | pass | source_rows=14; represented_once=14 |
| Table 6 source rows represented exactly once | pass | source_rows=12; represented_once=12 |
| Table 7 source rows represented exactly once | pass | source_rows=8; represented_once=8 |
| Table 3 and Table 4 use clean blocked-split R0/R1/R2/R4 evidence rather than legacy E0-E6 headline wording | pass | clean_names_ok=True; legacy_promoted=False |
| potential width/layout warnings | warning | Table 2: resizebox used for 4 columns or long text cells; Table 3: resizebox used for 10 columns or long text cells; Table 4: resizebox used for 10 columns or long text cells; Table 5: resizebox used for 13 columns or long text cells; Table 6: resizebox used for 12 columns or long text cells; Table 7: resizebox used for 14 columns or long text cells |
| expected strict-preflight result after table insertion | warning | strict preflight should still fail on author metadata, figure assets, release/data governance, environment and compile readiness, but not table placeholders |

## Command Outcomes

- git switch research/ra-repdet-triair: PASS
- git pull --ff-only research research/ra-repdet-triair: PASS
- git status --short: PASS; unrelated untracked files existed before Phase 7C edits
- python scripts/preflight_submission.py --root . --allow-placeholders: PASS with warnings before table insertion
- table fragment generation: PASS; 7 fragments created from unchanged source CSVs
- table rendering check: PASS; 12 pass and 2 warning checks
- python -m py_compile rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py: PASS
- python rarepdet/tools/generate_handoff.py: PASS
- python rarepdet/tools/update_project_status.py: PASS
- python scripts/preflight_submission.py --root . --allow-placeholders: PASS with warnings after table insertion; no TABLE PLACEHOLDER warning remains
- python scripts/preflight_submission.py --root .: FAIL as expected on author metadata, final artwork placeholders, release/data placeholders and missing Fig. 1-6 assets; no TABLE PLACEHOLDER failure remains

## Preflight Outcomes

- Placeholder mode: PASS with warnings; table placeholder warning removed
- Strict mode: FAIL as expected on non-table external inputs and missing final figure assets

## Remaining Strict-Preflight Blockers

- author-confirmed metadata and declarations are missing
- TriAir citation/version/licence/access/redistribution facts are missing
- public release/archive URL, tag, commit/archive hash, date, licence and DOI facts are missing
- final approved Fig. 1-6 assets are missing
- validation-only wording approval or independent held-out evidence decision is missing
- final hardware/software environment record is missing
- strict V18 preflight and final Springer sn-jnl compile remain blocked

## Non-Modification Confirmation

No metric, source evidence CSV, model, dataset, split, weight, checkpoint, figure asset, final PDF, training output, GPU inference output, or numerical evaluation output was changed. No training, GPU inference, metric-changing evaluation, split mutation, or source-data mutation was run.

## Compile Limitation

No final PDF compile was attempted; strict preflight remains blocked by external author/asset inputs and final figure assets.

Final commit SHA: pending until the completion commit is created.
