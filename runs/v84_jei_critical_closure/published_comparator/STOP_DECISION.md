# V84 Published Comparator Stop Decision

Candidate: TriModalDet, official source `https://github.com/radlab-sketch/trimodal-uav-det.git` pinned at `8f4e31ed64f1f2fe019d4706670fc4560c0b2e23`.

Status: **DOCUMENTED STOP**. No training or evaluation was started.

The pinned official loader performs an internal random 80/20 split and retains only samples with non-empty labels. Its primary path also lacks the frozen component-disjoint manifest interface, the V84 standardized COCO evaluator, and the frozen development-validation checkpoint-selection contract. Replacing those parts would be a substantial new adaptation, not a direct reproduction. In addition, the tree has no LICENSE/COPYING grant text, although the README labels the project MIT.

Therefore V84 reports no cross-protocol number and does not invent a comparison. The source inventory, hashes, and line-level protocol evidence are archived beside this decision. The locked holdout was not accessed.
