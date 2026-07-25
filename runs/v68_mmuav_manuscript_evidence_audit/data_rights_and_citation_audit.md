# V68 MM-UAV Data Rights And Citation Audit

## Available source-backed facts

- Dataset name used in the records: `MM-UAV`; extracted internal directory label: `MMMUAV`.
- An official benchmark repository and evaluation repository were audited at pinned commits, and an arXiv v3 record (`2511.18344v3`) was preserved by URL and SHA256 in V52.
- The repository code license is Apache-2.0. V52 explicitly records that this covers repository code and is not an express license for dataset files.
- The arXiv content license recorded by V52 is not a dataset-use grant.
- No dataset README, provider metadata, version identifier, or dataset license text was present in the extracted subset or preserved archive inventory.
- V52 found no explicit dataset research-use grant, reporting permission, or redistribution permission.

## Required rights fields

| Field | Status | Evidence and consequence |
|---|---|---|
| Canonical dataset name | Partial | `MM-UAV` is used consistently, but a provider-issued data card/version record is absent |
| Provider / release authority | Unresolved | Official code sources exist, but the dataset release authority is not established in preserved records |
| Submission-ready citation | Incomplete | An arXiv record is identified, but canonical dataset citation metadata is not preserved as a verified repository citation |
| Dataset version | Unresolved | No version identifier was found |
| Dataset license | Unresolved | Code and paper licenses do not grant dataset rights |
| Research-use permission | Unresolved | Local possession and successful experimentation are not permission evidence |
| Aggregate-results reporting permission | Unresolved | No explicit term authorizes publication of derived benchmark metrics or methodological descriptions |
| Redistribution | Prohibited pending proof | No media, annotations, labels, transformed copies, or derivative data may be redistributed |

## Legal and ethical gate

The scientific evidence is internally auditable, but the available records do not establish that aggregate metrics and MM-UAV methodological descriptions may be included in a journal submission. V68 therefore fails closed. The blocker can be cleared only by provider-verifiable citation, dataset version, license/access terms, research-use permission, and permission to report aggregate derived results. No inference from code licensing, paper licensing, archive possession, or prior local use is acceptable.
