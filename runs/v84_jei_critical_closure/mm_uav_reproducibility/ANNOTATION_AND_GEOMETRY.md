# MM-UAV Annotation and Geometry Contract

Each manifest row identifies one synchronized RGB, infrared, and event frame. Only rows with at least one RGB annotation are included. The 106 IR-only and 35,898 unlabeled inventory rows are excluded and are not interpreted as negatives. Train and devval contain 7,187 and 1,845 rows, respectively, with no sequence overlap. Exact sequence IDs and row counts are in `sequence_manifest_summary.json`.

Provider tracking rows are parsed at the manifest frame index. Columns are frame index, track ID, x, y, width, and height; positive-width/height boxes are converted from xywh to xyxy. The foreground category is the provider drone class, and track IDs are retained as metadata.

RGB, infrared, and event images are loaded independently and independently letterboxed to 640x640. This preprocessing is not geometric registration. Detection boxes remain in the RGB coordinate system and are transformed only with the RGB letterbox scale and padding. The model uses modality-specific feature extraction followed by learned feature alignment; it does not concatenate unregistered raw channels.
