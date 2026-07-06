# Upcoming Task Queue

Generated: 2026-07-06
Branch: `research/ra-repdet-triair`

This queue separates research-evidence strengthening from submission closure. Execute only `docs/NEXT_TASK.md` as the current task. Do not promote a later item until the current task has a report, refreshed handoff/status, and a pushed branch state.

## Current Active Task

- `docs/NEXT_TASK.md`: **V40 — Repair, Freeze, and Validate a Truly Component-Disjoint TriAir Split**.
- The V39 candidate split failed the continuation gate: it has 353 same-family train/validation guard-band-16 violations, minimum cross-partition distance 1, 4 train/guard exact-RGB groups, and 5 validation/guard exact-RGB groups.
- V40 is audit-gated. It may run GPU training only after a replacement split has zero component crossings, zero pairwise exact-RGB overlap, and zero pairwise distance-16 violations across train, validation, and guard.

## Research-Evidence Queue

### V40 — Repair and Freeze a Truly Component-Disjoint Split

**Trigger:** Run now.

**Purpose:** Replace the failed V39 candidate with a deterministic transitive component-disjoint split. If and only if it passes strict auditing, complete R4 `p=0.20` for seeds 0 and 2 with V39-compatible standardized evaluation, missing-modality checks, and efficiency reporting.

**Cannot proceed to GPU:** Until all split gates in `docs/NEXT_TASK.md` pass.

---

### V41 — Public-Protocol Baselines and Cross-Dataset Feasibility Matrix

**Trigger:** Only after V40 is reported, whether V40 ends as audit-blocked or audit-passed.

**Purpose:** Create a reproducible feasibility matrix for at least two published applicable baselines and at least one public compatible dataset/protocol. The task must distinguish: directly reproducible; reproducible after representation adaptation; incompatible because raw event, thermal calibration, labels, or licences are unavailable; and unavailable because of provider restrictions.

**Minimum experiment if feasible:** Run the selected R0/R4 configuration and at least two literature baselines under one frozen compatible public protocol. Preserve the local TriAir result as local validation evidence; do not combine datasets or claim cross-dataset generalization without actual evaluation.

**Cannot run:** Until dataset licence/access, representation mapping, class mapping, and baseline implementation provenance are recorded.

---

### V42 — Realistic Cross-Sensor Degradation Stress Suite

**Trigger:** After V40 audit outcome and baseline feasibility review.

**Purpose:** Extend synthetic channel zeroing with deterministic, documented degradations while keeping all existing clean results frozen.

**Required conditions:** RGB brightness/contrast reduction and blur; thermal contrast compression and noise; event sparsity/drop-rate or event-channel attenuation; at least one compound degradation. Use severity levels defined before model evaluation, retain clean and channel-zeroing results separately, and apply the same conditions to R0 and R4.

**Metrics:** AP50, AP75, F1@0.50, per-condition relative degradation from clean performance, and per-seed variability. Do not call a synthetic corruption a physical sensor failure.

---

### V43 — Three-Seed Uncertainty and Paired-Comparison Extension

**Trigger:** After V40 produces a passing split or after a documented decision keeps `block64_guard16_seed0` as the primary protocol.

**Purpose:** Add one predeclared additional seed to the matched R0 and R4 comparison, bringing the selected protocol to at least three seeds for both variants.

**Requirements:** Keep data, split, epochs, image size, batch size, learning rate, model implementation, and standard evaluation settings fixed. Report per-seed metrics, mean, standard deviation, and a transparent paired difference summary. Do not claim statistical significance unless the planned analysis and assumptions are explicitly satisfied.

---

### V44 — Qualitative Failure Taxonomy and Error Analysis

**Trigger:** After a selected split and selected final model are frozen.

**Purpose:** Turn the qualitative panel inventory into a structured scientific analysis before final figure approval.

**Required categories:** small/occluded vehicles, dense scenes, false positives, false negatives, low-visible-contrast cases, thermal-removal failures, and event-degraded cases where available. Use real validation examples only; retain paths privately when data redistribution is not authorized; do not add final manuscript figures without author approval.

---

### V45 — Evidence Review and Manuscript-Claim Decision

**Trigger:** After V40--V44 have either completed or been transparently blocked.

**Purpose:** Decide which evidence may enter the manuscript. Compare the frozen clean blocked split, V40 if valid, public-protocol outcomes if available, degradation suite, uncertainty summaries, and error analysis.

**Rule:** No result changes the R4 manuscript headline automatically. Any headline change requires an explicit evidence-reconciliation report and an author-approved manuscript revision task.

## Submission-Closure Queue

The tasks below remain independent of V40--V45. Research evidence does not close metadata, governance, release, figure, or compile blockers.

### Phase 7J — Apply Confirmed Authorship and Declarations
Run only after Phase 7H/7I identify `eligible_for_future_guarded_application` rows with complete author confirmation metadata.

### Phase 7K — Apply Confirmed Data Governance and Release Facts
Run only after provider terms and responsible-owner confirmation verify citation, licence/access, redistribution, release, archive, and DOI/no-DOI facts.

### Phase 7L — Final Figure Workflow
Run only after author-approved Fig. 1--6 assets and complete figure-decision metadata are available.

### Phase 7M — Environment and Reproducibility Closure
Run only after the responsible author confirms environment and profiling facts.

### Phase 7N — Strict Preflight Closure Check
Run only after all external author, governance, release, figure, claim-scope, environment, and compile blockers are closed.

### Phase 7O — Springer `sn-jnl` Compile Dry Run
Run only after strict preflight passes and the approved Springer environment is available.

### Phase 7P — Final Submission Bundle Assembly
Run only after compiled-package review and author final approval.

## Non-Negotiable Discipline

- Do not overwrite V39 candidate evidence or relabel it as passing.
- Do not commit raw data, `.npy` samples, weights, checkpoints, prediction dumps, figures, videos, or secrets.
- Do not change the official manuscript headline without an explicit evidence review.
- Do not fabricate metadata, data-governance facts, release facts, author information, approvals, environment facts, or figure decisions.
- Run no simultaneous GPU jobs.
- Keep all claims validation-only unless a separately frozen independent test or public protocol supports a stronger claim.
