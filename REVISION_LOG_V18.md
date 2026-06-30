# Revision Log V18

## 2026-06-30

- Read `D:/download/CODEX_FINISH_V18_CN.md` and applied its evidence-first constraints.
- Ran the requested initial audit command before creating the script; it failed because `scripts/preflight_submission.py` did not yet exist.
- Added `scripts/preflight_submission.py` as an explicit final-submission gate.
- Created root `main.tex` and `main_sivp_snjnl.tex` from the existing Phase 6B Springer `sn-jnl` source and updated both files identically to input `submission/sivp/tex/ra_repdet_sivp.tex`.
- Created `metadata/submission_metadata.yaml`, `metadata/submission_metadata.tex`, `metadata/IMPLEMENTATION_DETAILS_TEMPLATE.md`, `AUTHOR_FINAL_INPUTS_REQUIRED_V18.md`, `SUBMISSION_PRECHECK_V18.md`, and `archive_manifest.txt`.
- Preserved all validation wording; no independent test or guard-test result was introduced.
- Did not invent TriAir citation, licence, access terms, public DOI, repository release URL, author information, or final figure assets.
- Strict final preflight remains blocked by author-supplied metadata and final assets that are not present in the repository.
