# Integration status

Code integration complete.

This branch now includes the V23 evaluator implementations in `rarepdet/eval_map.py` and `rarepdet/tools/eval_missing_modality.py`. Both scripts separate detector-output thresholding from the precision/recall/F1 operating threshold, preserve the legacy `--score-thr` / `--score-thresh` entry points, and write the V23 provenance fields required by the standardized re-evaluation protocol.

The lightweight V23 evidence files are published under `reproducibility/standardized_evaluation_v23/results_v23/`. No raw data, model weight, checkpoint, split, or reported V23 numeric result was changed by this integration commit.

Note: the external file named `RA_RepDet_SIVP_v24_SubmissionReadiness_Source.zip` was not present in the searched local paths during this repository sync. The evaluator files and evidence copied here come from the local V23 standardized re-evaluation outputs generated under `<LOCAL_PROJECT_ROOT>`.
