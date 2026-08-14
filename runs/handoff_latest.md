# RA-RepDet-TriAir Handoff

Generated: 2026-08-14T16:28:54+08:00

## Current task

- Status: `V85_SUBMISSION_FIGURE_ASSETS_TRACKING_COMPLETE`.
- V85 generated, integrated, and Git-tracked a real checkpoint-backed qualitative figure.
- No training, threshold tuning, synthetic content, manual box editing, or locked-holdout access occurred.

## Frozen evidence

- Candidate table covers all 2,213 frozen development-validation samples.
- Selected samples: `frame_00846` (`v40c_00410`), `nframe_01125` (`v40c_02482`), `nframe_07517` (`v40c_04592`).
- Scenes use three distinct components and model-independent descriptor selection.
- Checkpoints are matched early seed 0 and dynamic gate/no-dropout seed 0, both SHA256-verified.
- One global display contract: score 0.25, NMS IoU 0.60, maximum 100 detections.

## Artifacts

- Summary: `runs/v85_real_qualitative_figure/V85_QUALITATIVE_FIGURE_SUMMARY.md`.
- Provenance: `runs/v85_real_qualitative_figure/provenance/qualitative_figure_provenance.md`.
- Manuscript: `submission/v85_real_qualitative_manuscript/main.tex`.
- Frozen figure PNG/PDF are Git-tracked under `submission/v85_real_qualitative_manuscript/figures/`.
- Source and submission-copy SHA256 values match exactly for both formats.
- Two-pass manuscript source validation passed with zero undefined references.

## Next action

- Author review of the frozen qualitative figure before final submission packaging.
