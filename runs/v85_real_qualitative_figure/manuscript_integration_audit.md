# V85 Manuscript Integration Audit

Status: `PASS`

- Evidence was frozen before manuscript integration.
- Candidate source: `submission/v85_real_qualitative_manuscript/main.tex`.
- Figure source: `runs/v85_real_qualitative_figure/figure/fig6_real_qualitative.pdf`.
- Git-tracked submission assets:
  `submission/v85_real_qualitative_manuscript/figures/fig6_real_qualitative.png`
  and `submission/v85_real_qualitative_manuscript/figures/fig6_real_qualitative.pdf`.
- PNG SHA256: `e498d4b47a8e199f9f47c8e5545c37a6f8a5d0c50e7c0dc305703f02b6155cdf`.
- PDF SHA256: `6d5ce6d2c6fcdfdb1587757024612c510f272cf7220f5ecf965f5e6a51e4035d`.
- Source and copied-asset SHA256 values match exactly for both formats; file
  lengths also match at 2,356,993 bytes (PNG) and 522,211 bytes (PDF).
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
- Asset tracking copied the frozen files byte-for-byte. It performed no
  retraining, sample selection, inference, image processing, manual editing, or
  locked historical-holdout access.
