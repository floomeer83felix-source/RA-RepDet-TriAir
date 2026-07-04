# Figure Candidate Check

Phase 7D review confirms that figure sources and candidate-build rules are locked without creating final artwork.

| Check | Scope | Status | Evidence |
| --- | --- | --- | --- |
| One traceability row per figure | Fig. 1-6 | pass | `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.csv` contains 6 rows. |
| Fig. 3 CSV verified | Fig. 3 | pass | `Variant, Seed, F1, AP50, AP75`; 8 rows; 40 numerical tokens; sha256 `23e2984adac08ebd6584e1c8d56f82d3cdd0dfb9e5e32047d5064481076d21dc`. |
| Fig. 4 CSV verified | Fig. 4 | pass | `Variant, Seed, Condition, AP50`; 18 rows; 55 numerical tokens; sha256 `aea82341ac37547ece40428e56bd3d98fabf299304a4b24067a7705eaf642fde`. |
| Fig. 5 CSV verified | Fig. 5 | pass | `Seed, Mode, alpha_rgb_mean, alpha_thermal_mean, alpha_event_mean, alpha_rgb_std, alpha_thermal_std, alpha_event_std`; 8 rows; 56 numerical tokens; sha256 `ef93dca475e9a1fa704856952951fbe47ebb701c9e559ea60abf46d861a1239c`. |
| Fig. 1-2 not final | Fig. 1-2 | pass | Both remain `author-design required` with author approval required. |
| Fig. 6 not fabricated | Fig. 6 | pass | It remains `local-panel inventory required`; manifest has 20 rows and local real panel dependencies. |
| No final figure PDFs added | Fig. 1-6 | pass | No `Fig1`-`Fig6` final PDF exists under `figures/` or `submission/sivp/figures/`. |
| Dry run writes no artwork | Fig. 3-5 | pass | `figure_candidate_build.py --dry-run --root .` validates only source CSVs and does not render or write PDF/PNG/SVG/JPG/EPS output. |
| Figure placeholders retained | SIVP body | pass | `submission/sivp/tex/ra_repdet_sivp.tex` still contains the six `Final artwork pending` figure placeholders, as required. |
| Strict preflight remains blocked | Preflight | pass | Strict mode is expected to fail on unresolved author metadata, release/data facts, final figure assets, environment details, and compile readiness. |

Conclusion: Phase 7D creates a candidate source/build specification only. No final figure, candidate artwork, image, PDF, source evidence, model, split, metric, or LaTeX body placeholder is modified.
