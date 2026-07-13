#!/usr/bin/env python
"""Run V50 adapter, annotation, checkpoint, and RGB training smoke tests."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

from PIL import Image, ImageDraw
import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.visdrone_seen_dataset import VisDroneSeenVehicleDataset
from rarepdet.models.early_fusion_fcos import build_detector
from rarepdet.models.rgb_fcos import build_rgb_fcos
from rarepdet.v50_coco import evaluate_detections, outputs_to_detections


CHECKPOINTS = {
    "matched_early_seed0": (
        "early",
        "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt",
    ),
    "matched_early_seed1": (
        "early",
        "runs/v41_q1_upgrade/seed1/matched_early_seed1/weights/best.pt",
    ),
    "matched_early_seed2": (
        "early",
        "runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed2/weights/best.pt",
    ),
    "reliability_p015_seed0": (
        "reliability",
        "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt",
    ),
    "reliability_p015_seed1": (
        "reliability",
        "runs/v41_q1_upgrade/seed1/reliability_p015_seed1/weights/best.pt",
    ),
    "reliability_p015_seed2": (
        "reliability",
        "runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed2/weights/best.pt",
    ),
}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=r"D:\datasets\visdrone_seen")
    parser.add_argument("--run-dir", default="runs/v50_visdrone_seen")
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = PROJECT_ROOT / run_dir
    device = torch.device(args.device)

    devval = VisDroneSeenVehicleDataset(
        args.data,
        run_dir / "manifests/devval.txt",
        run_dir / "converted_annotations/devval.json",
        five_channel=True,
    )
    image, target = devval[0]
    assert image.shape[0] == 5
    assert image.dtype == torch.float32
    assert 0.0 <= float(image.min()) <= float(image.max()) <= 1.0
    assert torch.count_nonzero(image[3:]).item() == 0

    source_path, image_info, _ = devval.samples[0]
    with Image.open(source_path) as source:
        rendered = source.convert("RGB")
    draw = ImageDraw.Draw(rendered)
    for box in target["boxes"][:50].tolist():
        draw.rectangle(box, outline=(255, 0, 0), width=2)
    rendered.thumbnail((960, 960))
    rendered.save(run_dir / "coordinate_sanity.jpg", quality=85)

    loaded = {}
    for run_id, (model_type, relative_path) in CHECKPOINTS.items():
        path = PROJECT_ROOT / relative_path
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        cfg = checkpoint.get("model_cfg", {})
        model = build_detector(
            model_type=model_type,
            model_name=cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
            img_size=cfg.get("img_size", 640),
            num_classes=cfg.get("num_classes", 2),
            fpn_out_channels=cfg.get("fpn_out_channels", 128),
            score_thresh=0.001,
            nms_thresh=0.6,
            detections_per_img=100,
        )
        model.load_state_dict(checkpoint["model_state"], strict=True)
        loaded[run_id] = {"sha256": sha256(path), "strict_load": "PASS"}
        del model, checkpoint

    rgb_dataset = VisDroneSeenVehicleDataset(
        args.data,
        run_dir / "manifests/devval.txt",
        run_dir / "converted_annotations/devval.json",
        five_channel=False,
    )
    rgb_image, rgb_target = rgb_dataset[0]
    rgb_model = build_rgb_fcos(
        img_size=640, score_thresh=0.001, nms_thresh=0.6, detections_per_img=100
    ).to(device)
    rgb_model.train()
    losses = rgb_model(
        [rgb_image.to(device)],
        [{key: value.to(device) for key, value in rgb_target.items()}],
    )
    loss = sum(losses.values())
    assert torch.isfinite(loss)
    loss.backward()
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "rgb_smoke.pt"
        torch.save({"model_state": rgb_model.state_dict()}, path)
        reloaded = build_rgb_fcos(img_size=640)
        reloaded.load_state_dict(torch.load(path, map_location="cpu", weights_only=False)["model_state"])
    rgb_model.eval()
    with torch.no_grad():
        outputs = rgb_model([rgb_image.to(device)])
    detections = outputs_to_detections(outputs, [rgb_target])
    single_annotation = run_dir / "preflight_single_image.json"
    full = json.loads((run_dir / "converted_annotations/devval.json").read_text(encoding="utf-8"))
    image_id = int(rgb_target["image_id"].item())
    full["images"] = [item for item in full["images"] if int(item["id"]) == image_id]
    full["annotations"] = [
        item for item in full["annotations"] if int(item["image_id"]) == image_id
    ]
    single_annotation.write_text(json.dumps(full) + "\n", encoding="utf-8")
    metrics = evaluate_detections(single_annotation, detections)
    single_annotation.unlink()

    result = {
        "adapter_shape": list(image.shape),
        "adapter_min": float(image.min()),
        "adapter_max": float(image.max()),
        "zero_channel_nonzero": int(torch.count_nonzero(image[3:]).item()),
        "checkpoint_loads": loaded,
        "rgb_loss": float(loss.detach().cpu()),
        "rgb_checkpoint_reload": "PASS",
        "one_batch_metric_smoke": {
            key: metrics[key]
            for key in ("ap50_95", "ap50", "ap75", "ar100", "gt_boxes", "ignored_regions")
        },
        "coordinate_sanity": str(run_dir / "coordinate_sanity.jpg"),
        "status": "PASS",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
