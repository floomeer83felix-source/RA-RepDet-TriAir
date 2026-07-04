# Upcoming Codex Task Queue

Generated: 2026-07-04
Branch: `research/ra-repdet-triair`

This file is a forward task queue. It is not the active execution entry point. Codex should execute only `docs/NEXT_TASK.md` unless the user explicitly asks to promote one queued task into `docs/NEXT_TASK.md`.

## Current Active Task

- `docs/NEXT_TASK.md`: Phase 7H - Author-Response Validation Gate and Application Readiness.

## Queue Discipline

- Keep exactly one current task in `docs/NEXT_TASK.md`.
- Promote the next queued task only after the current task is completed, handoff/status are refreshed, and the branch is pushed.
- Do not claim strict final-submission readiness until strict preflight passes without placeholders and all final assets/author facts are verified.
- Do not fabricate author metadata, data-governance facts, release URLs, DOIs, approvals, or figure decisions.
- Do not run training, GPU inference, metric recomputation, split mutation, source-data mutation, or LaTeX compilation unless a promoted task explicitly allows it.

---

## Phase 7I - Conditional Application of Confirmed Author Metadata and Declarations

### Trigger
Run only after `AUTHOR_RESPONSE_VALIDATION.md` shows the relevant author_metadata and declarations rows are structurally ready, author-confirmed, and have nonblank confirmation source metadata.

### Allowed Scope
Apply confirmed author names/order, affiliations, ORCIDs, corresponding email, funding, acknowledgments, contributions, competing interests, and AI-use disclosure to the explicit destination files listed in the readiness map.

### Cannot Run Until
The Phase 7H validation gate reports no missing response/confirmation fields for the rows being applied. Blank, partial, or unverified rows must remain untouched.

---

## Phase 7J - Conditional Application of Confirmed Data Governance and Release/Archive Facts

### Trigger
Run only after the data_governance and release_archive rows are structurally ready and externally verified by the data owner, provider terms, and release owner as applicable.

### Allowed Scope
Apply confirmed TriAir citation/version/licence/access/redistribution facts, release URL or no-release policy, release tag, immutable source identifier, archive date, release licence, and DOI state to the listed destination files.

### Cannot Run Until
Provider terms, release-owner confirmation, and all confirmation-source fields are available. A well-formed URL, DOI, licence, or citation string alone is not enough.

---

## Phase 7K - Conditional Final Figure Asset Workflow after author decisions

### Trigger
Run only after `AUTHOR_FIGURE_REVIEW_DECISIONS.csv` and the Fig. 6 panel review template contain author-approved decisions with confirmation metadata.

### Allowed Scope
Prepare or insert final Fig. 1-6 assets only from approved schematic sources, approved frozen-CSV candidate revisions, and approved real Fig. 6 panel selections/composition decisions.

### Cannot Run Until
Every affected figure has author approval, final asset authorization, confirmation date, approver identity, and source-of-confirmation. Local candidate PDFs and panel inventories are not final assets.

---

## Phase 7L - Environment Record and Reproducibility Metadata Closure

### Trigger
Run only after the environment row and environment record template are completed and confirmed by the responsible author or research owner.

### Allowed Scope
Apply confirmed hardware, OS, Python, PyTorch/Torchvision, CUDA/cuDNN, key package versions, and training/profiling protocol summary to reproducibility metadata.

### Cannot Run Until
Machine-specific facts and confirmer/date fields are present. Do not infer environment facts from the current machine unless explicitly confirmed.

---

## Phase 7M - Strict Preflight Closure Check

### Trigger
Run after author metadata, declarations, data governance, release/archive facts, figure assets, claim-scope decision, environment record, and compile-readiness inputs are all applied.

### Allowed Scope
Run strict preflight and document any remaining formal submission blockers without weakening validation.

### Cannot Run Until
All external confirmations and approved final assets are present. Placeholder-mode PASS remains a structural check only.

---

## Phase 7N - Springer `sn-jnl` Compile Dry Run

### Trigger
Run only after strict preflight passes and the local Springer LaTeX environment is available.

### Allowed Scope
Compile the approved SIVP source package, capture logs, and review references, figures, tables, captions, and layout.

### Cannot Run Until
Strict preflight passes. Do not label a PDF final unless the compile is clean and authors approve the compiled package.

---

## Phase 7O - Final Submission Bundle Assembly

### Trigger
Run only after strict preflight passes, compile review passes, release/archive records are frozen, and authors approve the final package.

### Allowed Scope
Assemble the final source package manifest, final PDF if approved, final figures/tables, metadata, declarations, and release/archive references.

### Cannot Run Until
Every publisher-required field and package artifact is confirmed. Do not include local-only candidates, raw data, checkpoints, or unapproved panels.

---

## Phase 8A - Optional post-submission research continuation

### Trigger
Run only after the SIVP submission package is finalized, or after the user explicitly pauses submission work and requests research continuation.

### Allowed Scope
Start a separate research-readiness task for the next paper direction, such as stress-suite robustness, asynchronous event-window tests, or reliability/registration-aware fusion.

### Cannot Run Until
Submission evidence and new research evidence are clearly separated. Submitted manuscript claims remain frozen unless authors explicitly approve a revision.
