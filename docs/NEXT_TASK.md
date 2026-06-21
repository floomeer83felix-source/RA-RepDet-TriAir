# Current Task

Execute Phase 2A post-processing for paper-ready RA-RepDet TriAir results.

# Goal

Produce the Phase 2A paper-facing result package: threshold=0.50 main metrics, repeated E0/E2 profiling, brightness-proxy grouped evaluation, reliability alpha statistics, and a consolidated report.

# Why This Matters

Phase 2A converts completed E0/E1/E2 experiments into stable paper tables and robustness diagnostics without retraining or changing the detector implementations.

# Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `rarepdet/tools/`
- `runs/phase2a_report.md`
- `runs/phase2a_*.csv`
- `runs/phase2a_*.txt`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`

# Forbidden Files To Modify

- `rarepdet/train_early_fusion.py`
- `rarepdet/models/early_fusion_fcos.py`
- `rarepdet/models/reliability_fusion_fcos.py`
- `datasets/triair_dataset.py`
- Dataset files under `D:\download\triair`
- Model weights, checkpoints, prediction images, raw `.npy` files, and large visual outputs

# Required Commands

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
python rarepdet/tools/phase2a_main_results.py
python rarepdet/tools/profile_phase2a.py --model early --weights runs/E0_early_repvit_fcos_e50/weights/best.pt --img-size 640 --device cuda --batch-size 1 --warmup 100 --iters 300 --repeats 3 --out runs/phase2a_profile_e0
python rarepdet/tools/profile_phase2a.py --model reliability --weights runs/E2_reliability_dropout015_repvit_fcos_e50/weights/best.pt --img-size 640 --device cuda --batch-size 1 --warmup 100 --iters 300 --repeats 3 --out runs/phase2a_profile_e2
python rarepdet/tools/eval_brightness_proxy.py --data D:\download\triair --split-file D:\download\triair\splits\val.txt --img-size 640 --device cuda --batch-size 4 --score-thr 0.50 --out runs/phase2a_brightness_proxy
python rarepdet/tools/analyze_alpha_modes.py --data D:\download\triair --split-file D:\download\triair\splits\val.txt --img-size 640 --device cuda --batch-size 4 --out runs/phase2a_alpha
python rarepdet/tools/build_phase2a_report.py
python rarepdet/tools/update_project_status.py
python rarepdet/tools/generate_handoff.py
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

# Required Outputs

- `runs/phase2a_main_results.csv`
- `runs/phase2a_main_results.md`
- `runs/phase2a_profile_e0/profile_results.csv`
- `runs/phase2a_profile_e2/profile_results.csv`
- `runs/phase2a_brightness_proxy/brightness_proxy_results.csv`
- `runs/phase2a_alpha/alpha_mode_summary.csv`
- `runs/phase2a_report.md`
- Updated `runs/handoff_latest.md`
- Updated `docs/EXPERIMENT_STATUS.md`

# Acceptance Criteria

- No E0/E1/E2 retraining is performed.
- Training model files and `datasets/triair_dataset.py` are unchanged.
- Main table uses score threshold 0.50 for Precision, Recall, and F1.
- Profiling uses batch=1, img-size=640, warmup=100, iters=300, repeats=3.
- Profiling reports both raw forward and complete detector inference FPS, latency, and CUDA memory.
- Brightness-proxy grouping is not named day/night.
- Alpha statistics cover E1 and E2 under full, no_rgb, no_thermal, and no_event.
- Only code, markdown, CSV, and TXT files are committed and pushed.

# Commit Message

Add Phase 2A paper result summaries

# After Completion

Keep Phase 2A outputs as the latest paper-facing post-processing package until the next single task is assigned.
