# Current Task

## Title

V41 SIVP manuscript alignment with three-seed validation-only evidence.

## Goal

Revise the SIVP LaTeX manuscript so its active narrative uses the current V41 evidence state:

- matched early fusion vs reliability-aware fusion with modality dropout `p=0.15`;
- seed0, seed1, and seed2;
- frozen V40 component-disjoint development-validation split;
- three-seed interim development-validation descriptive summary;
- project-local AP50/AP75, not COCO AP50:95.

This is a manuscript-alignment task only. Do not run training or new evaluation. Do not create new metrics. Do not touch guard/test data. Do not make the manuscript claim independent testing, external generalization, statistical significance, final proof, optimal dropout, calibrated sensor reliability, or physical sensor-failure robustness.

## Read First

1. `AGENTS.md`
2. `PROJECT_PROFILE.md`
3. `docs/PROJECT_CONTEXT.md`
4. `docs/EXPERIMENT_STATUS.md`
5. `docs/V41_INTERIM_DEVVAL_STATUS.md`
6. `docs/TASK_BLOCKER.md`
7. `runs/handoff_latest.md`
8. `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.md`
9. `runs/v41_q1_upgrade/interim_devval/interim_claim_boundary.md`
10. `submission/sivp/review/V41_SIVP_CLAIM_LEDGER.md`
11. `submission/sivp/review/V41_SIVP_REPLACEMENT_TEXT.md`
12. `submission/sivp/review/V41_SIVP_MANUSCRIPT_ALIGNMENT_PLAN.md`
13. `submission/sivp/tables/Table_8_three_seed_interim_devval.tex`
14. `submission/sivp/tex/ra_repdet_sivp.tex`
15. `submission/sivp/tex/main.tex`

## Frozen Assets

- V41 interim dev-val package: `runs/v41_q1_upgrade/interim_devval/`.
- V41 fresh seed1 completion commit: `5d839ae900849919189edff4bdd364f42c043b86`.
- Latest assistant-prepared alignment package includes:
  - `submission/sivp/tables/Table_8_three_seed_interim_devval.tex`
  - `submission/sivp/review/V41_SIVP_CLAIM_LEDGER.md`
  - `submission/sivp/review/V41_SIVP_REPLACEMENT_TEXT.md`
  - `submission/sivp/review/V41_SIVP_MANUSCRIPT_ALIGNMENT_PLAN.md`
- Active quantitative values must come only from:
  - `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.csv`
  - `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.md`
  - `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.json`
- Claim boundary: validation-only; three seed pairs only; no independent test; no COCO AP50:95; no causal ablation; no final submission proof.

## Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `docs/V41_INTERIM_DEVVAL_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/v41_q1_upgrade/sivp_alignment/**`
- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/tex/main.tex` only if needed for table inclusion or compile wiring
- `submission/sivp/tables/Table_8_three_seed_interim_devval.tex`
- New review outputs under `submission/sivp/review/V41_*`

## Forbidden Files To Modify

- Any training, evaluation, metrics, data-loader, or model code outside a new review/reporting script if needed.
- Existing V40/V39 result directories, manifests, source locks, checkpoints, or evidence packages.
- Existing V41 seed1 evidence files under `runs/v41_q1_upgrade/seed1/**`.
- Raw data, labels, checkpoints, prediction caches, images, `.npy` arrays, or guard/test files.
- Figures or final artwork assets unless the user explicitly provides approved assets.
- Bibliography facts, author metadata, declarations, funding, conflicts, contributions, acknowledgments, data/code availability, repository archive DOI, or TriAir license/provider details unless author-confirmed.

## Required Commands

### 1. Inspect active manuscript claims

Run text checks before editing:

```powershell
python - <<'PY'
from pathlib import Path
p=Path('submission/sivp/tex/ra_repdet_sivp.tex')
text=p.read_text(encoding='utf-8')
for s in ['p=0.20','R4','block64','guard16','independent test','external generalization','statistical significance','optimal','physical sensor']:
    print(s, text.lower().count(s.lower()))
PY
```

Record the output in `runs/v41_q1_upgrade/sivp_alignment/pre_edit_claim_scan.txt`.

### 2. Apply V41 replacement text

Use `submission/sivp/review/V41_SIVP_REPLACEMENT_TEXT.md` and `submission/sivp/review/V41_SIVP_CLAIM_LEDGER.md` to revise `submission/sivp/tex/ra_repdet_sivp.tex`.

Minimum required manuscript changes:

1. Replace active R4 p=0.20 / seed0,2 / block64_guard16 headline with reliability-aware `p=0.15` seed0/1/2 V40 component-disjoint development-validation wording.
2. Replace or rewrite the contribution list so it matches V41 p=0.15 seed0/1/2 validation-only evidence.
3. Insert `submission/sivp/tables/Table_8_three_seed_interim_devval.tex` as the active main results table, or integrate the exact same values into the active main result table.
4. Rewrite Results so the active quantitative claim is the three-seed paired delta summary:
   - F1 mean paired delta `+0.018524`, sample SD `0.006208`;
   - AP50 mean paired delta `+0.016064`, sample SD `0.005699`;
   - AP75 mean paired delta `+0.064657`, sample SD `0.016415`.
5. Rewrite Discussion and Limitations to state validation-only, three seed pairs only, no independent test, no COCO AP50:95, no causal ablation, unresolved provenance, and incomplete label-quality review.
6. Remove R4 p=0.20 and block64_guard16 from the active headline narrative. They may remain only if clearly labeled historical/provenance and not used as the main result.

### 3. Run post-edit claim scan

Run the same scan and save it to:

```text
runs/v41_q1_upgrade/sivp_alignment/post_edit_claim_scan.txt
```

Explain any remaining high-risk terms in:

```text
runs/v41_q1_upgrade/sivp_alignment/post_edit_claim_scan_review.md
```

### 4. Run preflight/compile checks

At minimum:

```powershell
python scripts/preflight_submission.py --root . --allow-placeholders
```

If a local LaTeX environment is available, also compile the SIVP source and record the command and outcome. Save outputs under:

```text
runs/v41_q1_upgrade/sivp_alignment/
```

Do not treat missing final artwork, author metadata, or external data-governance facts as solved. Record them as residual submission blockers.

## Required Outputs

- Updated `submission/sivp/tex/ra_repdet_sivp.tex`.
- `runs/v41_q1_upgrade/sivp_alignment/pre_edit_claim_scan.txt`.
- `runs/v41_q1_upgrade/sivp_alignment/post_edit_claim_scan.txt`.
- `runs/v41_q1_upgrade/sivp_alignment/post_edit_claim_scan_review.md`.
- `runs/v41_q1_upgrade/sivp_alignment/preflight_allow_placeholders.txt`.
- Compile log if LaTeX is available, or `runs/v41_q1_upgrade/sivp_alignment/compile_not_run.md` if it is not available.
- Updated `docs/EXPERIMENT_STATUS.md`.
- Updated `runs/handoff_latest.md`.
- Updated `runs/handoff_latest.json`.
- Updated `docs/TASK_BLOCKER.md` only if a real blocker appears.

## Acceptance Criteria

- The manuscript active result is V41 reliability-aware `p=0.15` vs matched early fusion across seed0/1/2.
- The manuscript no longer presents R4 p=0.20 or block64_guard16 seed0/2 as the current headline result.
- The main table contains the three paired seeds and the descriptive mean ± sample SD paired deltas.
- All strong claims are restricted to validation-only wording.
- No new training or evaluation is run.
- No raw data, checkpoint, prediction cache, guard/test file, or new figure asset is touched.
- Preflight output is recorded.
- Residual blockers are explicitly listed rather than silently omitted.

## Commit Message

`submission: align SIVP draft with V41 validation-only evidence`

## Completion / Blocker Rule

On completion, update `docs/EXPERIMENT_STATUS.md`, `runs/handoff_latest.md`, and `runs/handoff_latest.json`; commit and push.

If the manuscript cannot be edited safely, LaTeX table inclusion breaks compilation, preflight cannot run, or active-claim ambiguity remains, write `docs/TASK_BLOCKER.md` with the exact file, command, observed issue, and minimal action needed. Commit and push the blocker state. Do not invent results or relax the claim boundary.