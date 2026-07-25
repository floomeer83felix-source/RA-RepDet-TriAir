# Current Task

## Authorization

The user reported that V70 completed and was pushed. Under the standing automatic handoff workflow, the next task is authorized as:

`V71_MMUAV_PROVIDER_SOURCE_RIGHTS_AND_OFFICIAL_TEST_ACQUISITION_AUTHORIZED`

V70 completed at commit `bd62068aa0f3ab046d8545c4eef69938b4e73c9b` with `V70_BLOCKED_EXTERNAL_TEST_MATERIAL_NOT_SUPPLIED`. It verified that the known local MM-UAV root still contains only the previously audited provider `train` split and that no official test package or wholly new independent provider sequence package had been supplied.

V71 is a source-recovery, rights-verification, and external-package-acquisition task. Its purpose is to obtain or make request-ready the provider-defined untouched MM-UAV material required for a genuine TriAir-trained-model zero-shot external evaluation. It authorizes no model inference, training, fine-tuning, adaptation, prediction generation, metric computation, or manuscript claim.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Expected authorization base and V70 completion commit:

`bd62068aa0f3ab046d8545c4eef69938b4e73c9b`

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, the four current task files, V52/V68/V69/V70 provenance and rights records, all preserved MM-UAV paper/code/provider references, the active TriAir manuscript data-availability boundary, and protected-file rules. Record the actual starting commit.

## Correct Objective

The required path remains:

```text
identify the authoritative MM-UAV release source
-> determine whether an official untouched test split or new provider sequences exist
-> establish access, citation, version, and reporting terms
-> acquire or request the package without opening media or labels
-> hash and seal the received archive outside Git
-> hand off to a later blind-independence and protocol-freeze task
```

Do not repeat V70 against the unchanged local `train` root. Do not randomly split, rename, sample, or repurpose any of the existing `424` provider-train sequences.

## Authoritative Source Recovery

Using existing V52/V68 records as leads, identify and preserve the strongest available authoritative chain for MM-UAV:

1. dataset or benchmark full name and accepted aliases;
2. original paper title, authors, venue, DOI/arXiv identifier, and canonical citation;
3. official project page, institutional page, provider repository, data portal, or release page;
4. dataset release authority and maintainers;
5. exact version, release date, package names, and documented split structure;
6. whether an official `test`, evaluation-server, hidden-label, challenge, or additional-sequence route exists;
7. whether test annotations are public, private, server-scored, or available by request;
8. provider-issued license, access terms, data card, README, download notice, or terms of use;
9. permitted research use, publication of aggregate derived metrics and methodological descriptions, citation requirements, and redistribution restrictions;
10. official contact route when access or clarification is required.

Prefer original provider, institutional, publisher, official repository, or official data-portal records. Mirrors, reposts, search snippets, code licenses, paper-content licenses, and unattributed archives are not sufficient authority.

Save source URLs and retrieval dates in the internal evidence package. Do not place credentials, private messages, access tokens, or personal contact details in Git.

## Official Test Availability Decision

Determine exactly one of the following:

- an official untouched MM-UAV test split is publicly downloadable;
- an official test split exists but requires registration, application, credentials, challenge access, or provider approval;
- a provider evaluation server or hidden-label submission route exists;
- the provider offers additional wholly new sequences/flights/components by request;
- the available official release contains only train/development material and no defensible external-test route can be verified.

Do not infer a test split from directory names in unofficial packages. Do not treat withheld labels alone as independence if the sequences were already linked to V52-V70 development.

## Publicly Available Package Acquisition

If an authoritative untouched official test package is openly available and its terms permit the standing private research use:

1. download it only from the authoritative source or a provider-declared mirror;
2. keep the complete archive and extracted material outside Git;
3. record source URL, retrieval timestamp, redirect chain when relevant, exact filename, byte count, SHA256, and provider version/split identity;
4. preserve provider README, data card, license/terms, checksum, and citation files without modifying them;
5. do not decode media, inspect annotations, compute label statistics, visualize samples, or run model inference;
6. do not merge the package with the existing local train root;
7. mark the archive as sealed pending the later independence audit.

A successful public acquisition must finish with:

`V71_MMUAV_OFFICIAL_TEST_PACKAGE_ACQUIRED_AND_SEALED`

## Access-Controlled or Provider-Request Route

If the official test package or new independent sequences require provider action:

1. identify the authoritative contact or application route;
2. prepare a concise access request describing the research purpose as zero-shot evaluation of already frozen TriAir-trained RGB/thermal/event vehicle detectors;
3. explicitly request the exact official test split or wholly new independent sequences, version identity, sequence/component metadata, canonical citation, and terms governing research use and publication of aggregate metrics;
4. state that raw data will not be redistributed and that no MM-UAV training, fine-tuning, adaptation, or test-informed tuning is planned;
5. request clarification on hidden labels or evaluation-server procedures when applicable;
6. create a reviewable request draft and submission checklist, but do not send messages automatically or expose private correspondence in Git.

When the request package is complete but provider response or user submission is required, finish with:

`V71_MMUAV_ACCESS_REQUEST_READY_PROVIDER_RESPONSE_REQUIRED`

## Rights and Reporting Repair

V71 must attempt to repair the independent V68 blocker using provider-verifiable records. Record separately whether the evidence establishes:

- provider/release authority;
- canonical citation;
- exact dataset version and split identity;
- license/access terms;
- research-use permission;
- permission to publish aggregate derived metrics and methodological descriptions;
- redistribution restrictions;
- required acknowledgments or challenge rules.

An acquired package may be scientifically usable internally while manuscript reporting remains blocked. Do not claim publication readiness unless every required item is supported by provider-issued documentation or written release-authority authorization.

## Package Acceptance Boundary

Reject and quarantine, without opening content, any candidate package that is:

- an unofficial mirror with no provider endorsement;
- a renamed or repackaged copy of the existing local train data;
- missing source authority, version, split identity, or package hash;
- offered through an unauthorized route;
- covered only by a code-repository or paper-content license;
- ambiguous about whether it contains new sequences or an official test split.

Do not run V70/V72 intake against a rejected or ambiguous package.

## Required Outputs

Create `runs/v71_mmuav_provider_source_rights_and_test_acquisition/` containing compact records such as:

```text
protocol.md
source_chain.json
official_source_inventory.md
canonical_citation_record.json
release_and_split_structure.json
official_test_availability.json
rights_and_reporting_matrix.json
download_or_access_route.json
acquired_package_seal.json
provider_access_request_draft.md
provider_request_submission_checklist.md
rejected_source_audit.json
protected_file_audit.json
test_commands.txt
test_output.txt
final_decision.json
handoff.md
```

Keep downloaded archives, extracted data, provider correspondence, credentials, account identifiers, private email addresses, access tokens, and local absolute paths outside Git. Commit only compact metadata, hashes, public institutional contact routes where appropriate, redacted request text, tests, and conclusions.

## Required Checks

Before completion, prove:

- V52-V70 historical evidence and protected files remain unchanged;
- every asserted source, version, split, license, and permission traces to an authoritative record;
- no existing local provider-train material was renamed or resplit;
- no candidate media or annotation content was opened;
- no labels, predictions, or metrics were computed;
- no CUDA, model inference, training, fine-tuning, adaptation, calibration, checkpoint selection, threshold tuning, or new experiment occurred;
- any acquired archive is outside Git and has deterministic filename/byte-count/SHA256 records;
- any request draft accurately describes the zero-shot protocol and does not overstate rights or scientific readiness;
- private/heavy artifacts and credentials did not enter Git.

## Decision States

Choose exactly one:

- `V71_MMUAV_OFFICIAL_TEST_PACKAGE_ACQUIRED_AND_SEALED`;
- `V71_MMUAV_ACCESS_REQUEST_READY_PROVIDER_RESPONSE_REQUIRED`;
- `V71_BLOCKED_NO_PROVIDER_DEFINED_TEST_OR_NEW_SEQUENCE_ROUTE`;
- `V71_BLOCKED_PROVIDER_IDENTITY_VERSION_OR_RIGHTS_UNRESOLVED`;
- `V71_BLOCKED_UNAUTHORIZED_OR_UNVERIFIABLE_PACKAGE`;
- `V71_BLOCKED_SOURCE_PROTECTED_OR_PRIVATE_ARTIFACT_VIOLATION`.

No V71 outcome authorizes model inference or AP/AR computation. An acquired-and-sealed result authorizes a later blind independence/protocol-freeze task. A request-ready result requires the user or authorized project representative to submit the request and preserve the provider response before intake resumes.

## Allowed Changes

- the four current task/status/blocker/write-record files;
- `runs/v71_mmuav_provider_source_rights_and_test_acquisition/**` compact evidence;
- V71-only source-recovery, metadata, download-hash, redaction, and validation utilities;
- local acquisition of an authorized official package outside Git.

## Forbidden Changes

- V40-V70 historical scientific evidence;
- active TriAir manuscript or submission claims;
- production detector/training/evaluator behavior;
- any MM-UAV training, fine-tuning, learned alignment, domain adaptation, calibration, pseudo-labeling, or model inference;
- candidate media/annotation inspection, visualization, label statistics, predictions, or metrics;
- random resplitting or relabeling of the existing `424` sequences;
- automatic sending of provider communications;
- raw data, archives, labels, credentials, private correspondence, checkpoints, predictions, or heavy artifacts in Git;
- manuscript/public reporting without provider-verifiable rights and a later evidence re-audit.

## Completion

Update the four task/status files, V71 final decision, source/rights records, and handoff. Commit with:

`docs: acquire V71 MM-UAV official external test source`
