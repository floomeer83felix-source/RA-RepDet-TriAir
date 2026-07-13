# V50 Dataset Audit

- Audit time: `2026-07-13T19:23:05+08:00`
- Target root: `D:\datasets\visdrone_seen`
- Local source root: `D:\datasets\visdrone`
- Generator: `E:\yolo\yolo26-e\create_visdrone_seen.py` (`a59532c1a6630821c7e40a3bd73b298e91e526daea9167e6b85bbc06de908bfb`)
- Decision: RGB-only. No thermal or event files are present.
- Local README/license: absent in the target directory.
- Annotation format: five-column normalized YOLO labels. The linked source retains eight-column original annotations.
- `seen` meaning: train labels retain IDs `[0, 3, 4, 5, 8, 9]`; val/test remain unchanged; no images are removed.
- Generation validation: image mismatches `0`; label mismatches `0`.

## Partitions

| split | images | labels | empty labels | candidate sequence prefixes |
|---|---:|---:|---:|---:|
| train | 6471 | 6471 | 3 | 208 |
| devval | 548 | 548 | 0 | 76 |
| test | 1610 | 1610 | 0 | 61 |


## Integrity

- Exact cross-partition image duplicates: `0`.
- Within-partition exact duplicate image groups: `3`.
- Train/devval candidate filename-prefix overlap: `24` groups. These prefixes are leakage warnings, not asserted video IDs; the source-provided split is retained and the limitation must be reported.
- YOLO boxes are syntactically valid. Boxes crossing normalized image edges are clipped only in derived COCO annotations; source files are unchanged.
- Test labels and linked original annotations are locally available.
- `.cache` files are NumPy object arrays with pickle payloads. They were inspected only as raw bytes and were never unpickled.

## Provenance Boundary

The target is a locally generated derivative whose file counts and source directory names match the VisDrone2019-DET train/val/test-dev layout. It must be described as the audited local VisDrone-SEEN derivative, not as an untouched official release. The local generator is unversioned, so its exact SHA256 is the provenance pin.
