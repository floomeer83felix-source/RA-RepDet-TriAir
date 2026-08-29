# V86 Giant-Group Bridge Audit

Status: **PASS**

The largest group is `V86PG0001` with 4,077 images. It contains
`frame_00000` through `frame_04076`; all 4,076 consecutive numeric gaps equal 1.

## Edge inventory inside the giant group

- Exact decoded-RGB match edges: 0
- Manually confirmed adjacency edges: 114
- Filename numeric-adjacency edges: 4,076
- pHash candidate-only edges: 1,385
- dHash candidate-only edges: 427
- Unique pHash/dHash candidate-only edges: 1,812
- Candidate-only edges used by the V86 operational grouping graph: 0

## Counterfactual connectivity

| Edge rule | Components | Largest component sizes |
|---|---:|---|
| `v86_operational_graph` | 1 | 4077 |
| `remove_candidate_only_edges` | 1 | 4077 |
| `filename_adjacency_plus_confirmed_edges` | 1 | 4077 |
| `filename_adjacency_only` | 1 | 4077 |
| `confirmed_edges_only` | 3963 | 33, 22, 17, 12, 7, 7, 6, 5, 3, 3 |
| `candidate_only_edges` | 2844 | 37, 33, 28, 25, 25, 19, 15, 12, 12, 11 |

## Bridge sensitivity

The operational graph has 3,969 graph-theoretic bridge edges. This is the expected structure of a long consecutive-ID chain, not evidence that a small number of candidate similarity edges joined otherwise separate blocks.

Removing all candidate-only edges leaves one 4,077-image component. Keeping only
filename adjacency plus confirmed edges also leaves one component; filename adjacency
alone is sufficient. Therefore the giant group passes the requested bridge audit and
must not be split merely to balance folds.

The numeric filename relation remains proxy metadata. This audit does not establish a
verified flight, sequence, timestamp, or acquisition-session identity.
