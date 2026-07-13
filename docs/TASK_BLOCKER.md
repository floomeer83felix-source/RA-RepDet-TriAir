# Task Blocker

Status: `V49_COMPILE_AND_RENDER_PENDING`

Generated: 2026-07-13

The former V46 GPU-time and architecture-scope blockers are resolved by the completed V48 package. All required seed1/2 replications, static controls, and efficiency measurements are present.

## Completed before the current blocker

- V46 canonical COCO-style evaluation is complete for the six fixed matched-early and full-RA checkpoints on development-validation and the locked same-dataset holdout.
- V48 completed all 10 fresh runs and all required three-seed causal contrasts.
- V49 integrated the V46/V48 evidence into the V47 manuscript structure.
- Tables 10--12 were added.
- Abstract, contributions, Method, evaluation protocol, Results, Discussion, Limitations, and Conclusion were revised.
- No new holdout access occurred in V48 or V49.

## Current blocker

A fresh Springer `sn-jnl` compile, BibTeX pass, and rendered-page inspection have not yet been completed for the V49 manuscript state.

The connected GitHub editing interface does not mount the updated repository tree as a local TeX workspace. Therefore the current writing changes can be committed and reviewed as source, but the final PDF cannot be honestly declared closed until the updated files are compiled together with the Springer class/style files and all bibliography databases.

## Required compile procedure

From a local checkout of `research/ra-repdet-triair` at or after the V49 integration commit, run:

```powershell
cd submission/sivp/tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

If the local `bibtex` command is broken, use the known working executable path for the environment, as in the V47 compile closure.

Then render every PDF page and verify:

- no undefined citations;
- no undefined cross-references;
- Tables 10--12 fit within the page area;
- no clipped abstract or bibliography;
- no table overlap or broken page;
- the reference list still prints the intended 40 cited works.

## Related files

- `submission/sivp/tex/main.tex`
- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/tables/Table_10_coco_fixed_checkpoint_summary.tex`
- `submission/sivp/tables/Table_11_three_seed_causal_ablation.tex`
- `submission/sivp/tables/Table_12_efficiency_profile.tex`
- `runs/v49_manuscript_integration/V49_MANUSCRIPT_INTEGRATION_REPORT.md`

## Repair options

1. Compile in the established local author environment using the official Springer package and commit the PDF/compile report.
2. Provide a mounted repository source package to the assistant environment, then run the same compile and render-verification workflow there.
