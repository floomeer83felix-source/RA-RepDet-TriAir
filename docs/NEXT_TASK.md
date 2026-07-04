# Current Task

## Title
Manuscript Draft A — Evidence-Locked SIVP First Draft

## Goal
Write a coherent, full English first draft of the RA-RepDet SIVP manuscript from the already frozen repository evidence. Keep all author identity, affiliation, correspondence, declaration, data-governance, release/archive, environment, and final-asset fields explicitly blank or pending. This is a writing-and-consistency task only: no new experiment, metric recomputation, figure generation, data change, or claim-strengthening beyond the existing evidence.

## Read First
1. `AGENTS.md` if it exists.
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `runs/handoff_latest.md`
5. `runs/phase4b_report.md`
6. `runs/phase7b_publication_state_reconciliation.md`
7. `runs/phase7c_table_insertion_report.md`
8. `runs/phase7d_figure_source_lock_report.md`
9. `runs/phase7e_candidate_render_report.md`
10. `runs/phase7g_submission_intake_report.md`
11. `runs/phase7h_author_response_validation_report.md`
12. `runs/phase7i_update_planning_report.md`
13. `docs/TASK_BLOCKER.md`
14. `submission/sivp/tex/ra_repdet_sivp.tex`
15. `main.tex`
16. `main_sivp_snjnl.tex`
17. `submission/sivp/tex/main.tex`
18. `submission/sivp/tables/TABLE_SOURCE_TRACEABILITY.md`
19. `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md`
20. `submission/sivp/review/FIGURE_TABLE_CROSSWALK.md`
21. `submission/sivp/review/STATIC_SUBMISSION_SOURCE_AUDIT.md`
22. `submission/sivp/review/REPRODUCIBILITY_CLOSURE_AUDIT.md`
23. `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
24. `scripts/preflight_submission.py`
25. `submission/sivp/review/static_submission_audit.py`
26. `rarepdet/tools/generate_handoff.py`
27. `rarepdet/tools/update_project_status.py`

## Frozen Evidence and Non-Negotiable Wording
- The publication headline is **R4 Reliability p=0.20** on clean `block64_guard16_seed0`, with controlled seeds `0` and `2`.
- R4 headline means: F1@0.50 `0.920861`, AP50 `0.962495`, AP75 `0.891266`; synthetic no-RGB AP50 `0.916051`, no-thermal AP50 `0.718277`, no-event AP50 `0.961577`.
- Clean split: 7439 training images, 2213 validation images, 837 guard images; zero exact RGB train/validation matches and zero same-family guard-band violations.
- The retired random split had 153 exact RGB-content matched validation samples, or `0.072927` of validation images. Do not claim full five-channel byte duplication.
- R0 is the matched tri-modal early-fusion baseline. R1/R2/R4 are reliability-fusion variants. R2 uses p=0.15 and R4 uses p=0.20.
- R4 is supported as the main variant by controlled clean-split evidence. Two seeds are controlled replication only, not a statistical-significance test.
- The YOLO11n result is an RGB-only external baseline, not a matched architecture-only ablation.
- Missing-modality tests are synthetic modality removal, not a complete model of real sensor failures. Thermal removal remains the hardest condition.
- Fig. 1–2 require author-approved schematic assets; Fig. 3–5 are local, ignored, non-final candidates only; Fig. 6 requires author-approved real-panel selection and composition. The six figure placeholders must remain.
- Tables 1–7 are evidence-locked and already inserted. Do not alter table fragments or their source CSVs.
- The manuscript must use validation-only wording. Do not introduce test-set, benchmark-SOTA, statistical-significance, causal modality-importance, release, licence, DOI, or data-redistribution claims that are not already verified in repository evidence.

## Allowed Files To Modify
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/manuscript_draft_a_report.md`
- `runs/manuscript_draft_a_report.json`
- `main.tex`
- `main_sivp_snjnl.tex`
- `submission/sivp/tex/main.tex`
- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/review/MANUSCRIPT_DRAFT_A_EVIDENCE_CHECK.md`
- `submission/sivp/review/MANUSCRIPT_DRAFT_A_EVIDENCE_CHECK.csv`
- `submission/sivp/review/manuscript_draft_evidence_check.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Forbidden Files To Modify
- All author-information, declaration, data-governance, release/archive, environment, and figure-decision templates/CSVs.
- All BibTeX/reference files. Use only existing verified citation keys; do not add citations or bibliography entries.
- All table fragments, table CSVs, figure traceability records, figure files, candidate PDFs, local panels, final assets, raw data, labels, checkpoints, model/training/evaluation/data-loading/split code, and final PDFs.
- Do not change any numerical result, source value, split count, model definition, experimental protocol, or frozen evidence report.
- Do not fill author names, affiliations, ORCIDs, emails, funding, acknowledgments, contributions, competing interests, data availability, licence, citation, release, DOI, or environment facts.
- Do not run training, inference, evaluation, metric recomputation, data mutation, network access, figure generation, or LaTeX compilation.

## Required Commands
Start with source and static integrity checks:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
python submission/sivp/review/static_submission_audit.py --root . --output-prefix submission/sivp/review/static_submission_source_audit
```

If `git pull --ff-only` cannot proceed, do not reset, force-push, rewrite history, or merge unrelated histories. Record the blocker and stop.

After drafting and implementing the evidence check, run:

```powershell
python -m py_compile submission/sivp/review/manuscript_draft_evidence_check.py rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py
python submission/sivp/review/manuscript_draft_evidence_check.py --root . --body submission/sivp/tex/ra_repdet_sivp.tex --main-files main.tex main_sivp_snjnl.tex submission/sivp/tex/main.tex --output-prefix submission/sivp/review/manuscript_draft_a_evidence_check
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

Strict preflight is expected to remain FAIL because author, governance, release, final-figure, environment, and compile requirements are intentionally open. Do not compile LaTeX in this task.

## Required Writing Work

### A. Title, abstract, and front matter
Revise the title, abstract, and keyword line in all three mirrored main files so they are identical except for their existing input path. Preserve all author and declaration placeholders exactly as placeholders.

The revised abstract must be 180–250 words and include:

- motivation for robust lightweight RGB–thermal–event UAV vehicle detection;
- leakage-aware blocked validation protocol;
- R4 reliability-aware fusion plus p=0.20 modality dropout;
- exact R4 mean AP50/AP75/F1 values;
- careful scope of missing-modality and YOLO11n comparison;
- concise limitations: two controlled seeds, one dataset, synthetic missingness, thermal-removal weakness.

Do not call the draft final or submission-ready.

### B. Full manuscript body
Rewrite `submission/sivp/tex/ra_repdet_sivp.tex` into a cohesive first draft using the existing section structure where possible. Preserve all seven table inputs, all six figure placeholders, labels, and existing citation keys. Target 4,500–6,500 words in prose excluding table contents, captions, references, and placeholder box text.

The draft must contain these complete sections in a readable journal narrative:

1. **Introduction** — operational problem, tri-modal opportunity, leakage-aware rationale, bounded contributions.
2. **Related Work** — UAV vehicle detection, visible/thermal/event perception, missing-modality robustness, and the methodological importance of leakage-aware validation. Use only current citations.
3. **Method** — five-channel input, R0 matched early-fusion baseline, reliability estimator and softmax gating, modality-dropout training/inference distinction, precise architecture description only where repository evidence supports it.
4. **Dataset and Leakage-Aware Evaluation Protocol** — local TriAir representation, empty-label handling, duplicate audit, blocked split, guard band, headline evidence rule.
5. **Experiments** — reproducibility settings, controlled ablation, synthetic missing-modality robustness, external RGB-only baseline, efficiency/reliability-weight observations, qualitative-results scope.
6. **Discussion** — explain what the evidence supports and does not support. Include: R4’s AP50 improvement over R0, external-baseline comparison caveat, observed alpha behavior is not causal importance, no statistical significance claim, and why thermal removal is a limitation.
7. **Limitations** — retain/expand only supported limits: two seeds, one dataset, synthetic missingness, thermal removal, missing final panel/asset approval, and validation-only scope.
8. **Conclusion** — conservative summary of contribution and evidence.

Use precise cross-references to Tables 1–7 and Fig. 1–6. For Figs. 1–6 retain the existing final-artwork-pending language. Do not pretend a local candidate or panel inventory is a final figure.

### C. Required numeric integrity
All manuscript numeric tokens that state headline evidence must exactly match the frozen facts above. Preserve all already inserted Table 1–7 values and do not copy unverified values into narrative text.

At minimum, the prose must include and correctly contextualize:

- R4: AP50 `0.962495`, AP75 `0.891266`, F1 `0.920861`;
- split sizes `7439`, `2213`, `837`;
- duplicate-audit values `153` and `0.072927`;
- controlled seeds `0` and `2`;
- modality-dropout p `0.20`;
- no-RGB, no-thermal, and no-event R4 AP50 means `0.916051`, `0.718277`, `0.961577`.

### D. Manuscript Draft A evidence check
Create `submission/sivp/review/manuscript_draft_evidence_check.py` and matching Markdown/CSV reports.

The script must be CPU-only and read-only with respect to manuscript sources. It must:

- accept `--root`, `--body`, `--main-files`, and `--output-prefix`;
- verify the three mirrored main files have identical title, abstract, keywords, author-placeholder lines, declaration-placeholder blocks, and title/abstract do not contain author-confirmed or final-submission claims;
- verify the body retains six figure placeholders, seven table inputs, all existing body labels, and no `TABLE PLACEHOLDER`;
- verify required frozen numeric tokens and wording guards: `validation`, `two seeds` or equivalent, no explicit `test set` claim, no `statistically significant`, no `state-of-the-art`, no unverified `DOI`, and no author name replacement;
- compare frozen Table 1–7 source/fragment file hashes or unchanged Git content where feasible without modifying them;
- report prose word count, section headings, required keywords, warning-only placeholder state, and any integrity error;
- exit nonzero for source mismatch, missing required token, body placeholder/table regression, author placeholder changes, forbidden claim wording, or inconsistent mirrored main files;
- write only its requested reports.

### E. Report, handoff, and blocker status
Create `runs/manuscript_draft_a_report.md` and matching JSON documenting:

- starting source state;
- prose word count and section inventory;
- title/abstract change summary;
- frozen-evidence audit outcome;
- confirmation that Tables 1–7, six figure placeholders, author/declaration fields, and all external blockers were preserved;
- strict-preflight expected outcome;
- remaining work after Draft A: author inputs, final figures, governance/release facts, environment record, strict preflight, and compile review.

Update `docs/TASK_BLOCKER.md` and status/handoff to state that a complete evidence-locked manuscript **first draft** exists, but is not final/submission-ready and still carries all external blockers. Keep the R4 clean blocked-split headline first; E0–E6 remain historical/exploratory only.

## Acceptance Criteria
- The three main files contain identical revised title, abstract, keywords, author placeholders, and declaration placeholders.
- `ra_repdet_sivp.tex` is a coherent 4,500–6,500 word English manuscript first draft with all required sections.
- All seven existing table inputs and six figure placeholders/labels remain intact.
- No tables, figures, source CSVs, references, model/training/data/evaluation files, author templates, or final assets change.
- The evidence check passes with zero integrity errors; intentional author and final-figure placeholders are warnings, not silently removed.
- Placeholder-mode preflight is documented. Strict preflight remains truthfully FAIL.
- No training, inference, metric computation, network access, image generation, or LaTeX compilation occurs.
- Commit only allowed writing/review/status files and push.

## Commit Message
`docs: draft evidence-locked SIVP manuscript`

## Completion / Blocker Rule
Write the complete first draft from frozen evidence and preserve all intentionally pending fields. If a requested claim lacks repository support, omit it or state it as a limitation; do not guess. Stop after Draft A and do not claim final or submission-ready status.