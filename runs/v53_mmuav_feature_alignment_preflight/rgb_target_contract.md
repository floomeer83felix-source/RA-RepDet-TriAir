# V53 RGB Target Contract

Only frozen rows with `rgb_annotation_rows > 0` are supervised: 7,187 train + 1,845 devval = 9,032. RGB boxes are detector targets. IR boxes are metadata only; event has no target. The 106 IR-only and 35,898 unlabeled rows are excluded, never converted to negatives.
