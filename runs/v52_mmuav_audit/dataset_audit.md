# V52 MM-UAV Dataset Audit

Status: `BLOCKED_ARCHIVE_ONLY_INSUFFICIENT_EXTRACTION_SPACE`

Generated: `2026-07-14T11:40:39+08:00`

- Local root: `D:\BaiduNetdiskDownload\MM-UAV`.
- Local state: 35 10-GiB split parts plus one 7.2-GB final ZIP; no extracted sequence directory exists.
- Archive bytes: 383,014,670,799; free D-drive bytes: 360,268,697,600; deficit relative to archive size: 22,745,973,199 bytes.
- Central-directory compressed/uncompressed totals: 381,258,293,141 / 388,670,441,933 bytes.
- Free E-drive bytes: 655,513,616,384; extraction feasibility there still requires filesystem placement and a safety margin.
- ZIP64 entries: 8,460,602; central-directory SHA256: `23ad66adc07bd1a6831ffed9afe96dcba47f9f6df90817e6d595c67f5da395ee`.
- Sequence records inferred from paths: 1,321.
- RGB/IR/event entry counts: 2,813,654 / 2,812,333 / 2,812,333.
- Filename-index synchronization is reported in `sequence_alignment.csv`; this does not establish pixel geometry.

The archive directory is readable, but V52 cannot decode representative media, inspect annotation contents, verify licensing, measure geometry, benchmark the loader, or freeze usable manifests until the data are extracted to a filesystem with adequate space.
