# Historical Exposure Ledger Schema

The full ledger is local-only and contains one row per synchronized provider-train triplet.

| Field | Meaning |
|---|---|
| opaque_sample_id | One-way identifier derived from provider split, sequence, and frame identity |
| provider_split | Provider split identity; only `train` is locally present |
| sequence / frame_index | Identity metadata, not content |
| direct_exposure | `DEVELOPMENT_USED`, `CONTENT_EXPOSED`, or `IDENTITY_ONLY` |
| sequence_exposure | Maximum historical exposure of the linked sequence |
| blind_eligible | False for every local row |
| exclusion_reason | `SAME_SEQUENCE_AS_DEVELOPMENT_USED` |

`DEVELOPMENT_USED` covers the 9,032 V53 supervised rows used by V54-V67. `CONTENT_EXPOSED` covers the remaining V52 interval-20 rows whose annotation/content-derived metadata was audited. Other frames are `IDENTITY_ONLY` directly, but remain ineligible because all 424 sequences contain development-used rows.
