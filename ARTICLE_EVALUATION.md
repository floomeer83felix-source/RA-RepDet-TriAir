# RA-RepDet manuscript evaluation - V76 major revision

## Overall recommendation

**Major revision package completed; targeted single-modality experiments remain pending execution.** The manuscript is materially stronger than V75 because it now uses the already-completed three-seed COCO evaluation, six-variant causal fusion ablation, and locked internal holdout instead of relying on a two-run system comparison. The central mechanism claim is now better isolated: dynamic gating outperforms fixed equal stem fusion and deterministic learned stem projection, while modality dropout has mixed average effect.

The remaining experimental gap is narrow and explicit: trained RGB-only, thermal-only, and event-only baselines. A frozen nine-run execution package (three modalities by three seeds) is included, but no unexecuted result is inserted into the paper.

## Scorecard

| Dimension | Score | Assessment |
| --- | ---: | --- |
| Novelty and relevance | 4.1 / 5 | Lightweight tri-modal dynamic fusion remains timely and relevant. |
| Method clarity | 4.4 / 5 | Gate, stems, dropout, detector interface, split construction, and transfer boundaries are clear. |
| Experimental rigor | 4.1 / 5 | Three-seed full comparison, six causal variants, and a locked holdout substantially improve rigor. |
| Evidence traceability | 4.5 / 5 | V42, V48, V73, and V75 evidence is directly linked to compact source records. |
| Statistical support | 3.8 / 5 | Three paired seeds support descriptive consistency, but not strong inference. |
| Reproducibility | 4.5 / 5 | Frozen manifests, checkpoint hashes, evaluation contracts, and the new single-modality queue are explicit. |
| Writing and organization | 4.4 / 5 | The revised narrative separates development validation, locked holdout, and supervised transfer. |
| Submission readiness | 3.8 / 5 | Single-modality results, declarations, and exact TriAir provenance still require closure. |

**Overall: 4.2 / 5.** The paper is technically credible and much closer to submission, but the fixed single-modality experiment should be completed before making a comprehensive modality-contribution claim.

## Major revisions completed

1. Replaced the two-run headline with three-seed standardized COCO results.
2. Added six-variant causal ablation:
   - matched early fusion;
   - early fusion plus modality dropout;
   - separate stems with fixed equal fusion;
   - separate stems with learned deterministic projection;
   - dynamic gate without dropout;
   - dynamic gate with dropout.
3. Added seed-paired causal contrasts.
4. Added the 837-image locked internal holdout evaluated after checkpoint lock.
5. Corrected the discussion: static controls do exist and support a gate-specific descriptive conclusion.
6. Added canonical TriAir-related and MM-UAV dataset-paper citations, while retaining an explicit local-version provenance caveat.
7. Preserved the MM-UAV boundary: supervised target-domain adaptation on an exposed devval split, not independent external testing.

## Evidence interpretation

On component-disjoint development-validation, matched early fusion reaches `0.6803 +/- 0.0221` COCO AP and the full reliability-aware system reaches `0.7156 +/- 0.0172`, with paired gain `0.0354 +/- 0.0206`. The no-dropout dynamic gate reaches the highest mean AP (`0.7251 +/- 0.0121`) and exceeds fixed equal stem fusion by `0.0621 +/- 0.0188` and deterministic learned projection by `0.0404 +/- 0.0074`.

The modality-dropout increment is mixed: `-0.0095 +/- 0.0258` inside the gated architecture and `+0.0038 +/- 0.0322` inside early fusion. This prevents over-attributing the gain to dropout.

On the locked internal holdout, AP50 improves by `0.0086 +/- 0.0062` and is positive in all three seed pairs. AP75 is mixed. This supports a robust AP50 trend under checkpoint lock, not universal improvement or an independent public-test claim.

## Experiment still required

Run the frozen V76 single-modality queue:

- RGB-only: seeds 0, 1, 2;
- thermal-only: seeds 0, 1, 2;
- event-only: seeds 0, 1, 2.

All nine runs use the frozen V40 component-disjoint train/validation manifests, 50 epochs, batch size 4, image size 640, AdamW learning rate `1e-4`, no modality dropout, checkpoint retention by project-local validation AP50, and one standardized COCO evaluation of the retained checkpoint. No adaptive rerun, seed replacement, or result-driven schedule change is permitted.

## Remaining author closure

1. Confirm competing interests and final author/institution metadata.
2. Verify the exact local TriAir dataset version and conversion mapping against the cited provider paper.
3. Confirm data access and dissemination wording.
4. Execute and audit the nine single-modality runs.
5. Preserve the distinction between component-disjoint development validation, locked internal holdout, and exposed supervised MM-UAV devval.

## Acceptance outlook

With the single-modality table and metadata/provenance closure, the manuscript is a plausible journal submission. The most likely reviewer request after that would concern a truly independent sensor-compatible test set or broader seed replication rather than a missing basic control.
