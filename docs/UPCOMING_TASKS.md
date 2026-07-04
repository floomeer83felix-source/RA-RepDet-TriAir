# Upcoming Codex Task Queue

Generated: 2026-07-04
Branch: `research/ra-repdet-triair`

This file is a forward task queue. It is not the active execution entry point. Codex should execute only `docs/NEXT_TASK.md` unless the user explicitly asks to promote one queued task into `docs/NEXT_TASK.md`.

## Current Active Task

- `docs/NEXT_TASK.md`: Manuscript Draft A — Evidence-Locked SIVP First Draft.
- Scope: write and evidence-audit the manuscript title, abstract, and body while retaining author/declaration placeholders, all frozen tables, six final-artwork-pending figure placeholders, and every external submission blocker.
- This editorial task is independent of the conditional author-input workflow. It does not authorize applying author metadata or declarations.

## Queue Discipline

- Keep exactly one current task in `docs/NEXT_TASK.md`.
- Promote the next queued task only after the current task is completed, handoff/status are refreshed, and the branch is pushed.
- Do not claim strict final-submission readiness until strict preflight passes without placeholders and all final assets/author facts are verified.
- Do not fabricate author metadata, data-governance facts, release URLs, DOIs, approvals, environment facts, or figure decisions.
- Do not run training, GPU inference, metric recomputation, split mutation, source-data mutation, network access, or LaTeX compilation unless a promoted task explicitly allows it.
- Treat `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.*` as a future-planning artifact only. It is not authorization to apply values.
- Treat Manuscript Draft A as a writing artifact, not a final or submission-ready package.

---

## Manuscript Draft A — Evidence-Locked SIVP First Draft

### Trigger
Run now. Frozen evidence, inserted tables, existing citation keys, and draft source files are already available.

### Allowed Scope
Revise the three mirrored main files and the SIVP body to form a coherent English first draft. Preserve author/declaration placeholders, all final-figure placeholders, frozen metrics, tables, labels, and existing citations.

### Cannot Run Until
No external confirmation is required to write a first draft. However, Draft A may not fill author information, declarations, data governance, release/archive metadata, environment facts, final figures, or claim-scope decisions.

---

## Phase 7J - Apply Confirmed Authorship and Declarations

### Trigger
Run only after the Phase 7H validator and Phase 7I planner identify eligible author_metadata and declarations rows with complete author responses, confirmer identity, confirmation date, and source-of-confirmation metadata.

### Allowed Scope
Apply only the eligible, author-confirmed authorship/declaration rows to their listed destination files. Keep all data-governance, release/archive, figure, environment, claim-scope, strict-preflight, compile, and bundle work out of scope.

### Cannot Run Until
Blank, partial, unverified, or externally gated rows must remain untouched. The Phase 7I plan must show the target rows as `eligible_for_future_guarded_application`.

---

## Phase 7K - Apply Confirmed Data Governance and Release Facts

### Trigger
Run only after data_governance and release_archive rows are author-confirmed and externally verified by the responsible data owner, provider terms, or release owner.

### Allowed Scope
Apply confirmed TriAir citation, version/provider, licence/access, redistribution facts, public URL or no-release policy, release tag, immutable source identifier, archive date, release licence, and DOI/no-DOI state to the listed destination files.

### Cannot Run Until
Provider terms, release-owner confirmation, and all confirmation-source fields are available. A well-formed URL, DOI, licence, or citation string alone is not enough.

---

## Phase 7L - Final Figure Workflow

### Trigger
Run only after author decisions and approved final Fig. 1-6 assets are available, including complete `AUTHOR_FIGURE_REVIEW_DECISIONS.csv` entries and Fig. 6 panel-selection/composition approval.

### Allowed Scope
Prepare or insert final Fig. 1-6 assets only from approved schematic sources, approved frozen-CSV candidate revisions, and approved real Fig. 6 panel selections/composition decisions.

### Cannot Run Until
Every affected figure has author approval, final asset authorization, confirmation date, approver identity, and source-of-confirmation. Local candidate PDFs and panel inventories are review inputs, not final assets.

---

## Phase 7M - Environment and Reproducibility Closure

### Trigger
Run only after a confirmed environment record is supplied by the responsible author or research owner.

### Allowed Scope
Apply confirmed hardware, OS, Python, PyTorch/Torchvision, CUDA/cuDNN, key package versions, and training/profiling protocol summary to reproducibility metadata.

### Cannot Run Until
Machine-specific facts and confirmer/date/source fields are present. Do not infer environment facts from the current machine unless explicitly confirmed.

---

## Phase 7N - Strict Preflight Closure Check

### Trigger
Run only after all external blockers are closed: author metadata, declarations, data governance, release/archive facts, final figure assets, claim scope, environment, and compile readiness.

### Allowed Scope
Run strict preflight and document any remaining formal submission blockers without weakening validation.

### Cannot Run Until
All external confirmations and approved final assets are present. Placeholder-mode PASS remains a structural check only.

---

## Phase 7O - Springer `sn-jnl` Compile Dry Run

### Trigger
Run only after strict preflight passes and the local Springer LaTeX environment is available.

### Allowed Scope
Compile the approved SIVP source package, capture logs, and review references, figures, tables, captions, and layout.

### Cannot Run Until
Strict preflight passes. Do not label a PDF final unless the compile is clean and authors approve the compiled package.

---

## Phase 7P - Final Submission Bundle Assembly

### Trigger
Run only after compile review and author final approval.

### Allowed Scope
Assemble the final source package manifest, final PDF if approved, final figures/tables, metadata, declarations, and release/archive references.

### Cannot Run Until
Every publisher-required field and package artifact is confirmed. Do not include local-only candidates, raw data, checkpoints, or unapproved panels.

---

## Phase 8A - Optional Post-Submission Research Continuation

### Trigger
Run only after the SIVP submission package is finalized, or after the user explicitly pauses submission work and requests research continuation.

### Allowed Scope
Start a separate research-readiness task for the next paper direction, such as stress-suite robustness, asynchronous event-window tests, or reliability/registration-aware fusion.

### Cannot Run Until
Submission evidence and new research evidence are clearly separated. Submitted manuscript claims remain frozen unless authors explicitly approve a revision.
