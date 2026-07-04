# Manuscript Draft A Report

## Decision

**COMPLETE — evidence-locked SIVP first draft written for scientific and author review.**

This report does not claim formal submission readiness.

## Draft Scope

The following manuscript sources were revised directly from frozen repository evidence:

- `main.tex`
- `main_sivp_snjnl.tex`
- `submission/sivp/tex/main.tex`
- `submission/sivp/tex/ra_repdet_sivp.tex`

The draft now contains a complete English journal narrative covering the introduction, related work, method, data and leakage-aware protocol, experiments, discussion, limitations, and conclusion. The body retains all seven evidence-locked table inputs and all six final-artwork-pending figure placeholders.

## Front-Matter Outcome

- Title: `RA-RepDet: Reliability-Aware RGB--Thermal--Event Fusion for Lightweight UAV Vehicle Detection under Leakage-Aware Evaluation`.
- Abstract: revised to state the leakage-aware protocol, R4 design, headline validation values, synthetic missing-modality scope, external-baseline caveat, and key limitations.
- Keywords: revised for reliability-aware fusion, lightweight RepViT--FCOS detection, missing-modality robustness, and leakage-aware evaluation.
- Author, affiliation, email, funding, competing-interest, contribution, acknowledgment, and data-availability fields remain placeholders requiring author confirmation.

## Evidence Preserved

- Headline configuration: R4 Reliability p=0.20 on `block64_guard16_seed0`, controlled seeds 0 and 2.
- Headline values: AP50=0.962495; AP75=0.891266; F1@0.50=0.920861.
- Split: 7439 training images; 2213 validation images; 837 guard images; zero exact RGB train/validation matches; zero same-family guard-band violations.
- Historical random-split audit: 153 exact RGB-content matched validation samples; 0.072927 validation fraction; no full five-channel byte-duplication claim.
- R4 synthetic missing-modality AP50 means: w/o RGB=0.916051; w/o thermal=0.718277; w/o event=0.961577.
- R0 is retained as the matched tri-modal early-fusion baseline. YOLO11n remains an RGB-only external reference, not a matched architecture-only ablation.

## Editorial Boundaries Preserved

- No new experiments, inference, metrics, source CSVs, tables, figures, citations, references, data files, code, or model assets were changed.
- No author facts, declarations, data-governance facts, release/archive facts, environment facts, final figures, or panel selections were inferred or inserted.
- Missing-modality evaluation remains synthetic channel zeroing.
- Reliability-gate outputs remain descriptive observations rather than causal or calibrated sensor-reliability claims.
- The manuscript uses validation-only language and does not claim independent held-out evidence or statistical significance.

## Review Record

See `submission/sivp/review/MANUSCRIPT_DRAFT_A_EVIDENCE_CHECK.md` for the editorial evidence-consistency checklist.

## Remaining Work

Draft A is ready for scientific and author review. It is not ready for formal submission until the following are resolved:

1. author metadata and declarations;
2. TriAir citation/version/licence/access and redistribution facts;
3. release/archive decision and immutable record;
4. author-approved final Fig. 1--6 assets;
5. final environment record;
6. validation of all remaining external submission inputs;
7. strict preflight closure and Springer `sn-jnl` compile review.
