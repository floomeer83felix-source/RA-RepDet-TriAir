# V41 SIVP Manuscript Alignment Plan

Generated: 2026-07-09

## Objective

Align the SIVP manuscript with the current V41 evidence state before any formal submission package is assembled.

Current evidence state:

- Three-seed interim development-validation descriptive evidence is complete.
- Reliability-aware p=0.15 is the active comparison against matched early fusion.
- Main evidence is seed0/seed1/seed2 on the frozen V40 component-disjoint development-validation split.
- No independent test, external generalization, statistical significance, COCO AP50:95 package, or physical sensor-failure robustness claim is available.

## Files Prepared by Assistant

- `submission/sivp/tables/Table_8_three_seed_interim_devval.tex`
- `submission/sivp/review/V41_SIVP_CLAIM_LEDGER.md`
- `submission/sivp/review/V41_SIVP_REPLACEMENT_TEXT.md`
- `submission/sivp/review/V41_SIVP_MANUSCRIPT_ALIGNMENT_PLAN.md`

These files are safe manuscript-alignment inputs. They do not run experiments and do not modify raw evidence.

## Required Manuscript Source Changes

Target file:

- `submission/sivp/tex/ra_repdet_sivp.tex`

### 1. Replace active headline configuration

Replace active R4 p=0.20 / seed0,2 / block64_guard16 wording with:

- matched early fusion vs reliability-aware p=0.15;
- seed0, seed1, seed2;
- frozen V40 component-disjoint development-validation split;
- project-local AP50/AP75;
- descriptive mean ± sample SD, not significance.

R4 p=0.20 content may remain only as historical/provenance context if clearly labeled historical and not used as the manuscript headline.

### 2. Replace contribution list

Use the contribution list in `V41_SIVP_REPLACEMENT_TEXT.md`.

### 3. Replace primary results section

Use `Table_8_three_seed_interim_devval.tex` as the main results table. The old Table 3 controlled ablation may be removed, demoted to historical/provenance supplementary text, or left out of the active narrative.

### 4. Strengthen limitations

Ensure the Limitations section includes all items from `V41_SIVP_CLAIM_LEDGER.md`:

- validation-only;
- three seed pairs only;
- no independent held-out test;
- no external dataset;
- no COCO AP50:95;
- no causal mechanism ablation;
- synthetic channel removal is not physical sensor-failure robustness;
- TriAir provider/license/version/redistribution/synchronization facts remain unresolved;
- label-quality audit remains incomplete.

### 5. Update conclusion

Conclusion must not claim final proof, broad generalization, or robust deployment. It should say the method shows positive descriptive development-validation evidence and motivates future independent testing.

## Required Checks

After editing:

1. Run a grep/check for unsafe terms in active claims:
   - `independent test`
   - `external generalization`
   - `statistically significant`
   - `optimal dropout`
   - `sensor reliability`
   - `physical sensor failure`
   - `R4 p=0.20`
   - `block64_guard16`
2. These terms are allowed only in limitations, historical context, or disallowed-claim explanations.
3. Run LaTeX/preflight commands available in the repo, at minimum:
   - `python scripts/preflight_submission.py --root . --allow-placeholders`
4. If the environment supports it, compile the SIVP LaTeX source and record warnings/errors.

## What Assistant Could Not Safely Complete Here

- Directly rewrite the full LaTeX source, because the existing source is long, contains older table/figure structures, and should be compiled locally after edits.
- Compile the Springer/SIVP LaTeX package.
- Verify final artwork assets.
- Fill author declarations, conflict/funding/contribution statements, or final data/code availability details.
- Verify TriAir provider URL, version, license, redistribution rights, sensor synchronization, or official event representation.
- Perform new experiments, independent-test creation, COCO AP50:95 evaluation, causal ablations, or label-quality review.

## Codex Completion Definition

Codex should finish this task only when:

- `submission/sivp/tex/ra_repdet_sivp.tex` uses V41 p=0.15 seed0/1/2 development-validation evidence as the active results narrative;
- `Table_8_three_seed_interim_devval.tex` is inserted or the equivalent values are included in the active main table;
- all R4 p=0.20 / block64_guard16 claims are removed from the active headline narrative;
- validation-only limitations are explicit;
- preflight/compile results are recorded;
- status and handoff files are updated.
