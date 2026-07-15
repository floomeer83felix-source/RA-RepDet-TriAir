# V52 Extracted Annotation Audit

Status: `BLOCKED_SPARSE_GT_EMPTY_FRAME_CONTRACT_UNVERIFIED`.

- RGB and IR each use separate MOT-like `gt.txt` files with native-coordinate `xywh` boxes and track IDs.
- RGB dimensions are 640x360; IR dimensions are 640x512; event frames are 346x260 and have no separate boxes.
- Sampled RGB/IR objects: 20,250 / 19,940.
- Sampled frames without RGB/IR GT rows: 36,004 / 36,029.
- GT is predominantly present at `1, 101, 201, ...` plus the sequence end. Missing rows cannot be treated as verified empty-target frames without the provider contract.
- The final three source columns and target category name remain unverified without provider documentation.
