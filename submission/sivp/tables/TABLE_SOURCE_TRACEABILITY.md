# Table Source Traceability

Generated: 2026-07-04

Every SIVP table fragment below was generated from exactly one frozen CSV source under `manuscript/tables/`. Source values were not sorted, rounded, recomputed, filtered, or reformatted beyond LaTeX escaping.

| Table | Fragment | Source CSV | Source rows | Rendered rows | Numeric-token comparison | Escaping | Status |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| Table 1 | `submission/sivp/tables/Table_1_dataset_and_clean_split.tex` | `manuscript/tables/Table_1_dataset_and_clean_split.csv` | 12 | 12 | pass: source=20 rendered=20 | escaped '_' | pass |
| Table 2 | `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex` | `manuscript/tables/Table_2_implementation_and_reproducibility.csv` | 12 | 12 | pass: source=25 rendered=25 | escaped '_' | pass |
| Table 3 | `submission/sivp/tables/Table_3_controlled_ablation.tex` | `manuscript/tables/Table_3_controlled_ablation.csv` | 20 | 20 | pass: source=175 rendered=175 | escaped '_' | pass |
| Table 4 | `submission/sivp/tables/Table_4_missing_modality_robustness.tex` | `manuscript/tables/Table_4_missing_modality_robustness.csv` | 27 | 27 | pass: source=136 rendered=136 | escaped '_' | pass |
| Table 5 | `submission/sivp/tables/Table_5_rgb_only_external_baseline.tex` | `manuscript/tables/Table_5_rgb_only_external_baseline.csv` | 14 | 14 | pass: source=121 rendered=121 | escaped '_' | pass |
| Table 6 | `submission/sivp/tables/Table_6_efficiency_and_convergence.tex` | `manuscript/tables/Table_6_efficiency_and_convergence.csv` | 12 | 12 | pass: source=57 rendered=57 | escaped '_' | pass |
| Table 7 | `submission/sivp/tables/Table_7_reliability_weight_audit.tex` | `manuscript/tables/Table_7_reliability_weight_audit.csv` | 8 | 8 | pass: source=96 rendered=96 | escaped '_' | pass |

## Headers

### Table 1
- Source header: `Item | Value | Source | Notes`
- Rendered header: `Item | Value | Source | Notes`
- Git commit: `48d67fd267c199364adff4c14a9ec9c8f842dcf5`
- Git blob: `9dca55aae20488d710292e41c0e625e06b7e9e99`

### Table 2
- Source header: `Item | Value | Source | Notes`
- Rendered header: `Item | Value | Source | Notes`
- Git commit: `48d67fd267c199364adff4c14a9ec9c8f842dcf5`
- Git blob: `c6e2179e760b1d3deefc2c2d3f631a9cfe421417`

### Table 3
- Source header: `Variant | Seed | Row Type | Dropout Ratio | P@0.50 | R@0.50 | F1@0.50 | AP50 | AP75 | Source`
- Rendered header: `Variant | Seed | Row Type | Dropout Ratio | P@0.50 | R@0.50 | F1@0.50 | AP50 | AP75 | Source`
- Git commit: `48d67fd267c199364adff4c14a9ec9c8f842dcf5`
- Git blob: `5d25c53ab689e90b78dcc074c236a303569ad902`

### Table 4
- Source header: `Variant | Seed | Condition | AP50 | Row Type | Mean | Min | Max | Range | Source`
- Rendered header: `Variant | Seed | Condition | AP50 | Row Type | Mean | Min | Max | Range | Source`
- Git commit: `48d67fd267c199364adff4c14a9ec9c8f842dcf5`
- Git blob: `12936204448153f6b45914f39f12a29907bd6bdd`

### Table 5
- Source header: `Method | Input | Seed | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Mean Confidence | Row Type | Source`
- Rendered header: `Method | Input | Seed | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Mean Confidence | Row Type | Source`
- Git commit: `48d67fd267c199364adff4c14a9ec9c8f842dcf5`
- Git blob: `4a48f24c0df1020658cc12464ee603be32b71120`

### Table 6
- Source header: `Group | Model | Path or Seed | Params | FPS mean | Latency ms/img mean | CUDA Memory MB mean | Best Epoch | Best AP50 | Status | Source | Notes`
- Rendered header: `Group | Model | Path or Seed | Params | FPS mean | Latency ms/img mean | CUDA Memory MB mean | Best Epoch | Best AP50 | Status | Source | Notes`
- Git commit: `48d67fd267c199364adff4c14a9ec9c8f842dcf5`
- Git blob: `c334614a94b95f86ed7532b9fcf089d7ce328336`

### Table 7
- Source header: `Variant | Seed | Mode | Samples | alpha_rgb_mean | alpha_rgb_std | alpha_thermal_mean | alpha_thermal_std | alpha_event_mean | alpha_event_std | dominant_rgb | dominant_thermal | dominant_event | Source`
- Rendered header: `Variant | Seed | Mode | Samples | alpha_rgb_mean | alpha_rgb_std | alpha_thermal_mean | alpha_thermal_std | alpha_event_mean | alpha_event_std | dominant_rgb | dominant_thermal | dominant_event | Source`
- Git commit: `48d67fd267c199364adff4c14a9ec9c8f842dcf5`
- Git blob: `79746c85b680aa95192eba52637e5138d356ac04`
