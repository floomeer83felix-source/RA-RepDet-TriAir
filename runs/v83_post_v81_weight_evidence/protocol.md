# V83 Post-V81 Weight Evidence Protocol

- Authoritative single-modality registry: `runs/v81_single_modality_retraining_reconciliation/checkpoint_manifest.json`.
- V81 identity fields: SHA256, retained epoch, input mode, seed, input channels, image size, class count, FPN width, model name, and common split hash.
- Fusion identity source: matched-early and reliability-aware seed 0/1/2 records in `runs/v48_complete_ablation/causal_ablation_summary.json`.
- Hardware: NVIDIA GeForce RTX 3090; batch 1; 640x640; FP32; AMP, TensorRT, and `torch.compile` disabled.
- Timing: synthetic tensors, full detector call, no dataloader or file I/O, 50 warm-up iterations, 200 measured iterations, CUDA synchronization before and after every measured call.
- Outputs: parameter counts, PyTorch-profiler FLOPs and derived MACs, mean/median/p95 latency, FPS, peak allocated memory, and peak reserved memory.
- No dataset image, annotation, validation label, or locked-holdout sample was opened. No training, tuning, checkpoint selection, or threshold sweep was performed.
