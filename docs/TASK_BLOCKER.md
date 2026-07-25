# Task Blocker

Status: `V70_EXTERNAL_TEST_MATERIAL_REQUIRED_BEFORE_BLIND_FREEZE`

Generated: 2026-07-25

## Current state

V69 completed successfully as a fail-closed audit with `V69_BLOCKED_NO_UNUSED_MMUAV_PARTITION`.

The complete local inventory contains `897,578` synchronized triplets from `424` provider-train sequences. Every sequence is linked to V52-V67 development, so no local row or sequence is eligible for a defensible independent external test.

This is a scientific data-availability blocker, not a runtime or engineering failure.

## Required external input

Before V70 can pass its first gate, supply either:

- an authorized provider-defined official MM-UAV test split that was absent from and unexposed during V52-V69; or
- wholly new provider flights/sequences/components with provider metadata proving independence from all `424` development-linked sequences.

The package must identify the provider/release authority, exact dataset/version or split, sequence/component identities, acquisition source, and archive/package hashes. License, citation, research-use, aggregate-reporting, and redistribution terms must be preserved when available.

A renamed local directory, random resplit of existing train sequences, code-repository license, paper license, or unverified archive is not sufficient.

## Authorized V70 boundary

After new external material is supplied, V70 may:

- inspect package and sequence identity metadata before media access;
- compare identities and hashes against the frozen V69 ledger;
- freeze an independent blind manifest locally;
- hash and seal candidate labels without parsing them;
- verify six frozen TriAir manuscript checkpoints;
- freeze a deterministic parameter-free MM-UAV-to-TriAir five-channel adapter;
- freeze ontology, preprocessing, thresholds, NMS, maximum detections, and evaluator semantics;
- run a post-freeze schema-only pass without visualization, inference, or label access;
- commit compact hashes, counts, contracts, tests, and conclusions.

V70 may not:

- reuse, randomly resplit, or relabel any of the existing `424` provider-train sequences;
- train, fine-tune, adapt, calibrate, pseudo-label, or optimize on MM-UAV;
- use MM-UAV-trained V57/V63/V65-V67 checkpoints, learned alignment, or the Softplus MM-UAV path;
- inspect candidate labels, visualize candidate media, run candidate inference, generate predictions, or compute metrics;
- tune preprocessing, ontology, thresholds, NMS, checkpoints, seeds, or variants using candidate information;
- add MM-UAV material to the manuscript or publicly report results while V68 remains blocked;
- place raw media, labels, checkpoints, credentials, private correspondence, or heavy artifacts in Git.

## Fail-closed conditions

Finish with the matching V70 blocked state when:

1. no new external material is supplied;
2. provider/split/version identity is missing or ambiguous;
3. candidate sequence/component overlap with V52-V69 cannot be excluded;
4. the package is a renamed or randomly resplit form of the existing local train material;
5. any authoritative TriAir checkpoint or model contract cannot be verified;
6. a parameter-free five-channel adapter or vehicle ontology cannot be frozen;
7. evaluator determinism or label sealing cannot be established;
8. candidate schema differs after protocol freeze;
9. protected files drift or private/heavy artifacts enter Git.

## Independent publication blocker

V68 remains `V68_BLOCKED_DATA_RIGHTS_OR_CITATION_INCOMPLETE`. Even a scientifically valid V70 blind freeze does not authorize manuscript inclusion or public reporting until provider-verifiable rights and citation documentation pass a separate documentation-only re-audit.

## Next action

Place the authorized official test split or wholly new independent provider sequences in a local location outside Git together with provider metadata. Then execute V70 exactly as specified in `docs/NEXT_TASK.md`, beginning with identity-only package and sequence auditing. Do not open media or labels before that gate passes.
