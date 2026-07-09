# Post-Edit Claim Scan Review

Generated: 2026-07-09

## Summary

The post-edit scan of `submission/sivp/tex/ra_repdet_sivp.tex` found zero active occurrences of the older headline markers:

- `p=0.20`: 0
- `R4`: 0
- `block64`: 0
- `guard16`: 0
- `optimal`: 0

The manuscript active result is now reliability-aware `p=0.15` versus matched early fusion across seed0/seed1/seed2 on the frozen V40 component-disjoint development-validation split.

## Remaining High-Risk Terms

The remaining high-risk terms are retained only as claim-boundary or limitation text:

| Term | Count | Location and interpretation |
| --- | ---: | --- |
| `independent test` | 1 | Introduction claim-boundary sentence states the evidence is not an independent test. |
| `external generalization` | 1 | Introduction claim-boundary sentence states the evidence is not an external generalization result. |
| `statistical significance` | 1 | Introduction claim-boundary sentence states the three-seed summary is not a statistical-significance test. |
| `physical sensor` | 3 | Auxiliary-analysis, limitations, and conclusion sentences state that zero-channel stress testing is not physical sensor-failure robustness. |

These occurrences are negative/limiting statements, not active claims.

## Main-Entry Scan Note

`submission/sivp/tex/main.tex` was also checked because it contains the active abstract. It has no `p=0.20`, `R4`, `block64`, `guard16`, `independent test`, `external generalization`, `statistical significance`, or `optimal` occurrences. It retains one `physical sensor-failure` limitation phrase in the abstract, explicitly stating the absence of such experiments.

## Residual Submission Blockers

The edit does not resolve final submission blockers: final artwork, author metadata, declarations, funding/conflict/contribution statements, data/code availability wording, public archive or DOI information, TriAir provider/version/license/redistribution/synchronization confirmation, final environment records, and label-quality review remain open.
