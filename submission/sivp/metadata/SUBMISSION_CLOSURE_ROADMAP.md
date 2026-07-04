# Submission Closure Roadmap

This roadmap orders the remaining closure work without assigning dates or promising completion timing.

| step | closure action | required inputs | owner category | verification action | block-if-missing condition |
| --- | --- | --- | --- | --- | --- |
| 1 | Author responses and metadata confirmation | Completed response rows for authorship, affiliations, email, declarations, AI-use wording, and claim-scope decisions | authors | Update destination metadata and rerun strict preflight | Any response-only field remains blank for an item required by the final submission package |
| 2 | Figure decisions and final approved Fig. 1-6 assets | Completed figure decision CSV, Fig. 6 selection/composition decisions, approved final PDFs | authors/assets; assistant after approval | Verify final PDF paths and rerun strict preflight | Any Fig. 1-6 final PDF is absent or still pending review |
| 3 | Final release/data-governance decision | TriAir citation/version/licence/access terms; release URL or no-release policy; redistribution decision | authors; data owner; release owner | Update data availability, archive manifest, and release metadata | Dataset/provider terms, release policy, or redistribution rights are unconfirmed |
| 4 | Environment confirmation | Completed environment record with machine-specific hardware/software facts | authors; research owner | Update implementation/reproducibility metadata and record confirmation source | GPU/CPU/OS/Python/PyTorch/CUDA/cuDNN or confirmer/date fields are missing |
| 5 | Strict preflight | All ledger blockers closed and final figure assets present | assistant/local build owner | Run `python scripts/preflight_submission.py --root .` | Any strict preflight placeholder, metadata, claim, archive, or final asset check fails |
| 6 | Final Springer sn-jnl compile | Strict preflight PASS and local Springer dependencies available | assistant/local build owner | Compile final Springer `sn-jnl` package and retain build log | Strict preflight fails or compile dependencies are unavailable |
| 7 | Author visual review of tables/final figures | Final compiled PDF and final table/figure assets | authors | Record author visual approval or requested revisions | Any table layout, figure rendering, label, or caption issue remains unresolved |
| 8 | Final archive/release tag/immutable source record | Release tag, immutable commit/source identifier, archive date, licence, DOI if applicable | release owner | Freeze source record and update archive manifest | Release/archive facts are blank, mutable, or inconsistent with submitted source |
| 9 | Formal submission handoff | Final PDF, source package, metadata, declarations, data/release statements, and archive record | authors; submission owner | Produce final handoff checklist and submission package | Any required publisher field or source package artifact remains unconfirmed |
