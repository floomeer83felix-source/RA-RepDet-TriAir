# TriAir Data Provenance Audit - V78

## Author-confirmed local audit

| Item | Result |
| --- | --- |
| Local root | `D:\download\triair` |
| Provider archive | untagged `triair.zip` |
| Google Drive file ID | `1w71v6n41yqjP7BCr9ni4JdcxMnQ2ocR0` |
| Last-Modified | 2025-11-21 |
| Archive bytes | 3,551,150,083 |
| Compared entries | 20,240 |
| Missing / extra / different | 0 / 0 / 0 |
| Comparison fields | relative path, size, CRC32 |

## Content inventory

| Item | Count / value |
| --- | ---: |
| Five-channel arrays | 10,489 |
| YOLO text files | 9,751 |
| Valid label lines | 30,634 |
| Array shape | `(301, 391, 5)` |
| Array dtype | `uint8` |
| Channel order | RGB 0-2; thermal 3; event 4 |

## Published-count warning

The CVPR 2026 paper reports 24,223 annotated vehicles. The current provider archive audit counts 30,634 valid single-class label lines. The 6,411 difference is unresolved. The two figures are retained with distinct labels and must not be substituted for one another.

## Initial split audit

The 8,391-image `train.txt` and 2,098-image `val.txt` were reproduced from the project split utility using seed 0 and an 80:20 random assignment. They are not official provider splits and are not the final reported leakage-aware manifests.

## License boundary

The upstream repository states an MIT license for code. No explicit dataset-archive license was found. No dataset media, labels, or transformed copies may be redistributed from this project package.
