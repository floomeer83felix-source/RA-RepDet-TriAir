# V84 P3 Component-Mapping Recovery

At 2026-08-11 13:01 +08:00, P3 stopped before GPU inference with
`KeyError: frame_00417` while constructing clean quality descriptors.

The initial implementation incorrectly filtered `component_membership.csv` by
the historical `v39_partition` column. The frozen V40 split subsequently moved
61 former TRAIN samples into VALIDATION as whole components. The validation
manifest is therefore the authoritative final partition selector, while the
membership table remains the authoritative sample-to-component map.

The repair removes the historical partition filter in P3 and P4. A full
coverage check passed for all 2,213 frozen validation samples and 1,298 final
validation components. P2 was already complete at 48/48 and is not recomputed.
No locked-holdout resource was accessed.
