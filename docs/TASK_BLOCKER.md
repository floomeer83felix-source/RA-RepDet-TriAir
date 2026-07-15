# Task Blocker

Status: `V52_INTERVAL20_SUPERVISED_LABEL_ALIGNMENT_LICENSE_BLOCKER`

Generated: 2026-07-15T08:41:00+08:00

## Exact blocker

The user-authorized interval-20 manifest is frozen over 424 complete extracted train sequences: 45,036 synchronized triplets split across 339 train and 85 development-validation sequences. Only 9,138 sampled frames contain any source RGB or IR GT row; 35,898 contain no source GT row. Source annotations occur predominantly at frames `1, 101, 201, ...` plus sequence ends. No local provider contract establishes that absent rows are true empty-target frames, so they cannot be silently converted into negative detection samples.

RGB, IR, and event native grids are 640x360, 640x512, and 346x260. On a deterministic 100-frame/20-sequence sample, 215 same-track RGB/IR matches have mean dimension-scaled IoU 0.00867 (median 0), so direct channel-aligned early fusion is not defensible. Provider/license, category semantics, and the final three MOT-like fields also remain unresolved.

V51 remains incomplete with stale state `RUNNING` and no active process. No V52 GPU operation was executed.

## Last execution lines

```text
Complete sequences: 424
Interval-20 samples: 45036
Samples with source GT / unresolved no-row state: 9138/35898
Geometry frames/sequences: 100/20
V52 tests: 5/5 PASS
Repository tests: 14/15 PASS; stale V51 pre-authorization assertion fails
GPU operations: 0
Pilot gate: LOCKED
```

## Attempted checks

1. Stopped WinRAR after E: reached zero free bytes; no source archive was deleted.
2. Verified E: is exFAT with a 262,144-byte allocation unit, explaining the small-file space exhaustion.
3. Moved incomplete sequence `0512` to D: quarantine and verified identical file count and logical bytes before excluding it.
4. Verified exact `1..seqLength` RGB/IR/event filename sets for all 424 retained sequences.
5. Froze deterministic, sequence-disjoint interval-20 train/devval manifests before any model metric.
6. Parsed all available RGB/IR GT files, measured annotation cadence, and marked missing-row samples unresolved rather than empty.
7. Measured RGB-to-IR same-track geometry on 100 frames spanning 20 sequences.
8. Ran a 200-triplet CPU decode benchmark and 5 V52 unit tests.
9. Ran the full PyTorch-environment suite: 14/15 passed; only the out-of-scope stale V51 state assertion failed.

## Related files

- `runs/v52_mmuav_audit/manifests/train_sampled.txt`
- `runs/v52_mmuav_audit/manifests/devval_sampled.txt`
- `runs/v52_mmuav_audit/sampled_manifest.json`
- `runs/v52_mmuav_audit/annotation_audit.json`
- `runs/v52_mmuav_audit/geometry_audit.json`
- `runs/v52_mmuav_audit/pilot_gate.json`
- `runs/v52_mmuav_audit/source_lock_v52.json`

## Repair options

1. Obtain provider documentation confirming category/field semantics, whether absent GT rows mean true empty targets, dataset version/license, and calibration; then pre-register an explicit RGB/IR/event alignment method before any GPU pilot.
2. Approve a revised supervised protocol that keeps interval-20 file sampling for audit but trains/evaluates only the 9,138 rows with explicit source GT, with an amended source lock and no claim about unlabeled frames. This is a different evidence contract and must be authorized before implementation.
