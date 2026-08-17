# Reproduction

## Recorded Environment

- Windows 10
- Python 3.9.21
- PyTorch 2.5.1
- Torchvision 0.20.1
- CUDA 12.4 and cuDNN 9.1
- NVIDIA RTX 3090, 24 GB
- NumPy 1.26.4
- timm 1.0.22

The dependency file captures compatible package ranges rather than a byte-for-byte environment lock.

## Training Contract

- Image size: 640 x 640
- Epochs: 50
- Batch size: 4
- Optimizer learning rate: 1e-4
- Seeds: 0, 1, and 2
- Primary model: reliability-aware dynamic gate with modality dropout 0.0
- Robustness regularizer variant: modality dropout 0.15

Example:

```bash
python -m rarepdet.train_early_fusion \
  --model reliability --data /path/to/triair \
  --train-split splits/train.txt --val-split splits/validation.txt \
  --epochs 50 --batch-size 4 --img-size 640 --device cuda \
  --lr 1e-4 --num-workers 0 --modality-dropout 0.0 \
  --seed 0 --out runs/ra_seed0
```

## Evaluation Contract

Standardized COCO AP uses detector score threshold `0.001`, NMS IoU `0.60`, and at most 100 detections per image.

```bash
python -m rarepdet.tools.eval_coco_map \
  --run-id ra_seed0 --protocol devval --variant ra_no_moddrop \
  --model reliability --seed 0 --modality-dropout 0.0 \
  --data /path/to/triair --split-file splits/validation.txt \
  --weights /path/to/best.pt --img-size 640 --device cuda \
  --batch-size 4 --detector-score-thr 0.001 \
  --metric-score-thr 0.50 --nms-thresh 0.6 \
  --detections-per-img 100 --out-json results/ra_seed0.json
```

Checkpoints are intentionally not distributed. The reported model for each seed is the checkpoint retained by the frozen training protocol; checkpoint substitution, selective reruns, and validation-threshold tuning are outside the contract.

## Evidence Files

- [`results/core_metrics.csv`](../results/core_metrics.csv)
- [`results/single_modality_metrics.csv`](../results/single_modality_metrics.csv)
- [`results/efficiency.csv`](../results/efficiency.csv)
- [`results/channel_removal_summary.csv`](../results/channel_removal_summary.csv)
- [`results/component_bootstrap_summary.csv`](../results/component_bootstrap_summary.csv)

The qualitative PNG and PDF in [`assets/`](../assets/) are byte-identical copies of the frozen V85 manuscript assets.
