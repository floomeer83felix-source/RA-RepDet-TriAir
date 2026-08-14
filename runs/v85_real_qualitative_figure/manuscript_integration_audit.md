# V85 Manuscript Integration Audit

Status: `PASS`

- Evidence was frozen before manuscript integration.
- Candidate source: `submission/v85_real_qualitative_manuscript/main.tex`.
- Figure source: `runs/v85_real_qualitative_figure/figure/fig6_real_qualitative.pdf`.
- Placement: immediately before `Discussion and Limitations`.
- Caption states deterministic descriptor-based selection, fixed seed-0
  checkpoints, one display threshold, direct outputs, and no manual box edits.
- Accompanying text identifies the figure as illustrative and disallows external
  generalization, calibrated-reliability, or physical sensor-failure inference.
- Quantitative V84 results and scientific positioning were not changed.
- Two consecutive pdfLaTeX passes completed with zero undefined references,
  LaTeX errors, fatal errors, or overfull boxes.
- The compiled source-validation PDF uses the existing global demo mode because
  legacy Fig. 1-5 assets are absent from this source snapshot. The standalone
  V85 PNG/PDF was separately rendered and visually inspected at full resolution.
