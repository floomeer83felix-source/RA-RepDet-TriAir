# Upcoming Codex Task Queue

Generated: 2026-07-04
Branch: `research/ra-repdet-triair`

This file is a forward task queue. It is not the active execution entry point. Codex should execute only `docs/NEXT_TASK.md` unless the user explicitly asks to promote one queued task into `docs/NEXT_TASK.md`.

## Current Active Task

- `docs/NEXT_TASK.md`: Phase 7G — Submission Ledger Reconciliation and Author Intake Package.

## Queue Discipline

- Keep exactly one current task in `docs/NEXT_TASK.md`.
- Promote the next queued task only after the current task is completed, handoff/status are refreshed, and the branch is pushed.
- Do not claim strict final-submission readiness until strict preflight passes without placeholders and all final assets/author facts are verified.
- Do not fabricate author metadata, data-governance facts, release URLs, DOIs, approvals, or figure decisions.
- Do not run training, GPU inference, metric recomputation, split mutation, source-data mutation, or LaTeX compilation unless a promoted task explicitly allows it.

---

## Phase 7H — Apply Author Metadata and Declaration Responses

### Trigger
Run only after authors complete `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv` and the response source is committed or otherwise supplied explicitly.

### Goal
Validate author-provided metadata and declarations, then update only the relevant metadata placeholders and submission-support files.

### Scope
- Author names/order, affiliations, ORCIDs, corresponding email.
- Funding, acknowledgments, contributions, competing interests, AI-use disclosure.
- Do not alter scientific results or figures.

### Acceptance Criteria
- Every applied author fact has a source row and confirmation metadata.
- No blank response is treated as confirmed.
- Strict preflight may still fail on figures, data governance, release/archive, environment, or compile readiness.

---

## Phase 7I — Apply Data Governance and Release/Archive Responses

### Trigger
Run only after authors provide TriAir citation/version/licence/access/redistribution facts and release/archive decisions.

### Goal
Update data availability, references, release/archive manifests, and submission metadata using author-confirmed facts only.

### Scope
- TriAir citation and BibTeX if provided.
- Dataset provider/version/licence/access terms.
- Public release URL or explicit no-release/private policy.
- Release tag, immutable source identifier, archive date, release licence, DOI if applicable.

### Acceptance Criteria
- No DOI, URL, licence, citation, or access statement is invented.
- Ledger rows for data governance and release/archive are updated only when confirmed.
- Strict preflight may still fail on figures, author decisions, environment, or compile readiness.

---

## Phase 7J — Apply Author Figure Decisions and Prepare Final Figure Assets

### Trigger
Run only after authors complete `AUTHOR_FIGURE_REVIEW_DECISIONS.csv` and provide or approve final source material for Fig. 1–6.

### Goal
Convert approved figure decisions into final figure assets and update readiness checks.

### Scope
- Fig. 1–2: use author-approved schematic source or approved implementation checklist.
- Fig. 3–5: use approved candidate or apply requested revisions from frozen CSVs only.
- Fig. 6: use approved real local validation panels and approved crop/redaction/composition.

### Acceptance Criteria
- Final PDFs exist at the required final asset paths.
- Every final figure has author approval evidence.
- No candidate watermark remains in final approved assets.
- SIVP body figure placeholders are replaced only after final assets are verified.

---

## Phase 7K — Final Environment Record and Reproducibility Metadata

### Trigger
Run only after the environment record template is completed by the responsible author or research owner.

### Goal
Apply confirmed training/evaluation environment details to reproducibility metadata.

### Scope
- Hardware, OS, Python, PyTorch/Torchvision, CUDA/cuDNN, key package versions.
- Training and profiling protocol summary.
- Confirmation identity and date.

### Acceptance Criteria
- Environment details are not inferred from the current machine unless explicitly confirmed.
- Metadata is internally consistent with the manuscript and evidence tables.
- Strict preflight may still fail only on unresolved external inputs.

---

## Phase 7L — Strict Preflight Closure Check

### Trigger
Run after author metadata, declarations, data governance, release/archive, figures, claim-scope decision, and environment record are all applied.

### Goal
Run strict preflight and identify any remaining formal submission blockers without weakening validation.

### Scope
- `python scripts/preflight_submission.py --root .`
- Review placeholder patterns, missing final assets, metadata gaps, release/archive completeness, and compile prerequisites.

### Acceptance Criteria
- Strict preflight either passes or produces a precise blocker list.
- No final PDF is claimed ready unless strict preflight passes.
- Any failure is reflected in `docs/TASK_BLOCKER.md`, handoff, and status.

---

## Phase 7M — Springer sn-jnl Compile Dry Run

### Trigger
Run only after strict preflight passes and the local Springer LaTeX environment is available.

### Goal
Compile the SIVP manuscript package and capture build logs without altering scientific content.

### Scope
- Compile `main_sivp_snjnl.tex` or the repository-approved entry point.
- Capture warnings/errors.
- Check references, figures, tables, captions, and page layout.

### Acceptance Criteria
- PDF and log are generated locally and reviewed.
- Any layout or compile blocker is documented.
- Do not label the PDF as final unless the compile is clean and authors approve.

---

## Phase 7N — Final Submission Bundle Assembly

### Trigger
Run only after strict preflight passes, compile review passes, and authors approve the final package.

### Goal
Assemble a final, auditable SIVP submission bundle.

### Scope
- Source package manifest.
- Final figures and tables.
- Final PDF if approved.
- Metadata and declarations.
- Release/archive references.

### Acceptance Criteria
- All bundle components trace to confirmed sources.
- No local-only candidate, raw data, checkpoint, or unapproved panel is included.
- Handoff clearly states formal submission readiness only if every gate passes.

---

## Phase 8A — Optional Post-Submission Research Continuation

### Trigger
Run only after the SIVP package is finalized or the user explicitly pauses submission work.

### Goal
Return to research development for the next paper direction, such as R²-RepDet stress-suite robustness, asynchronous event-window tests, or reliability/registration-aware fusion.

### Scope
- Separate from the SIVP submission branch unless user requests otherwise.
- Start with a new task that audits current code/data readiness.
- Do not mix new experiments with the submitted manuscript evidence.

### Acceptance Criteria
- New research evidence is versioned separately.
- Submitted manuscript claims remain frozen unless authors explicitly approve a revision.
