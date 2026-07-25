# MM-UAV Versus TriAir Protocol Difference Matrix

| Dimension | MM-UAV V65-V67 | Current TriAir headline protocol | Manuscript consequence |
|---|---|---|---|
| Role | Matched two-seed devval stress test | Primary within-TriAir headline evaluation | MM-UAV is not an external replication of the headline configuration |
| Input size | 320 x 320 | 640 x 640 | Resolution and compute regime differ |
| Training length | One ordered pass, 7,187 optimizer steps | 50 epochs | Optimization exposure is not matched |
| Modal path | Independent RGB/IR/event stems with learned IR/event feature alignment to RGB | Modality-specific stems and sample-dependent fusion on the TriAir five-channel representation | Alignment and input contracts differ |
| Fusion comparison | Equal weights versus active shared V57 reliability scorer | Early fusion, dynamic reliability fusion, controls, and preselected dropout configuration | The intervention families are not identical |
| Bbox activation | Softplus(beta=1, threshold=20) distance head | Current production/headline detector path; no V65-V67 Softplus intervention | Head behavior differs |
| Modality dropout | None | Headline configuration uses preselected p=0.15 | V67 does not replicate the full headline method |
| Split/evaluation | Frozen source-train-derived train/devval; devval is not an independent test set | Component-disjoint development-validation plus locked within-dataset holdout | Neither protocol supplies cross-dataset independent-test evidence |
| Seeds | Two matched initialization states | Three paired seeds in the current active manuscript | Replication depth differs |
| Claims | Descriptive stress-test evidence only | Descriptive within-TriAir evidence only | No external-generalization bridge is permitted |

TriAir protocol facts are sourced from `main.tex` and `manuscript/tables/Table_2_implementation_and_reproducibility.csv`; MM-UAV facts are sourced from V53 and V65-V67 protocol/configuration records.
