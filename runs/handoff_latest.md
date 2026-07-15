# RA-RepDet-TriAir Handoff

Generated: 2026-07-15

## Current task

- V52 final outcome: `OFFICIAL_LEARNED_ALIGNMENT_ONLY_DIRECT_FUSION_NO_GO`.
- Starting commit: `895a09753f84a3883a709d587c3a852ace8af0c4`.
- Frozen interval-20 contract reproduced: 45,036 rows = 9,138 with any source GT + 35,898 `UNLABELED`.
- Train: RGB 7,187; IR 7,171; both 7,077; RGB-only 110; IR-only 94; neither 28,613; any 7,281; common-track 7,063.
- Devval: RGB 1,845; IR 1,836; both 1,824; RGB-only 21; IR-only 12; neither 7,285; any 1,857; common-track 1,820.
- Total: RGB 9,032; IR 9,007; both 8,901; RGB-only 131; IR-only 106; neither 35,898; any 9,138; common-track 8,883.
- Sparse GT: `PARTIALLY_CONFIRMED`; category/fields: `PARTIALLY_CONFIRMED`; dataset license: `UNRESOLVED`.
- Official baseline commit `5051e4451a2b66dba9128fb0f766832152e7d120` uses learned deformable or STN feature alignment.
- No complete deterministic RGB/IR/event raw-grid transform was found. Verification: `NOT_RUN_NO_OFFICIAL_DETERMINISTIC_TRANSFORM`.
- Official downloads: 9,569 tracked files inventoried; 560,363,481 total bytes including git metadata, below 1 GB.
- V52 tests: 9/9 pass. Protected core/manuscript changes: none. GPU optimizer steps: 0. Pilot gate: locked.

## Required action

Do not start direct-fusion MM-UAV training. A future route requires either a complete provider raw-grid calibration and dataset license, or explicit authorization for a new learned-alignment method and annotated-only protocol. V51 remains separate and unchanged.
