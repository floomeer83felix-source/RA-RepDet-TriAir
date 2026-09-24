"""M3OT RGB/thermal adapter using frozen official RGB COCO vehicle boxes."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image


class M3OTExternalDataset:
    """Return the TriAir detector's normalized tensor and RGB-coordinate target.

    The two-way routing checkpoint expects five input slots but reads only the
    first four. Slot five is constant zero padding and is never called an event
    observation. The four-channel early-fusion checkpoint receives no padding.
    """

    def __init__(self, manifest: Path | str, *, model_type: str, expected_split: str = "test"):
        if model_type not in {"early", "reliability_rgbt"}:
            raise ValueError(f"Unsupported model type: {model_type}")
        self.model_type = model_type
        self.manifest_path = Path(manifest).resolve(strict=True)
        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        if expected_split not in {"train", "val", "test"}:
            raise ValueError(f"Unsupported M3OT split: {expected_split}")
        if payload.get("split") != expected_split:
            raise ValueError(f"Expected M3OT {expected_split} manifest, got {payload.get('split')}")
        self.records = payload["records"]
        if len({row["sample_id"] for row in self.records}) != len(self.records):
            raise ValueError("Duplicate sample IDs in M3OT evaluation manifest")

    def __len__(self) -> int:
        return len(self.records)

    def get_record(self, index: int) -> dict:
        return self.records[index]

    def read_images(self, index: int) -> tuple[np.ndarray, np.ndarray]:
        row = self.records[index]
        rgb_path, thermal_path = Path(row["rgb"]), Path(row["thermal"])
        with Image.open(rgb_path) as image:
            rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
        with Image.open(thermal_path) as image:
            raw = np.asarray(image, dtype=np.uint8)
        if raw.ndim == 2:
            thermal = raw
        elif raw.ndim == 3 and raw.shape[2] == 3 and np.array_equal(raw[:, :, 0], raw[:, :, 1]) and np.array_equal(raw[:, :, 1], raw[:, :, 2]):
            thermal = raw[:, :, 0]
        else:
            raise ValueError(f"Thermal image is not losslessly single-channel: {thermal_path}")
        if rgb.shape[:2] != thermal.shape or rgb.shape[:2] != (row["height"], row["width"]):
            raise ValueError(f"RGB/thermal/COCO dimensions disagree at {row['sample_id']}")
        return rgb, thermal

    def boxes_xyxy(self, index: int) -> np.ndarray:
        row = self.records[index]
        width, height = row["width"], row["height"]
        boxes = np.asarray(row["boxes_xywh"], dtype=np.float32).reshape(-1, 4)
        if boxes.size == 0:
            return boxes
        result = boxes.copy()
        result[:, 2] = boxes[:, 0] + boxes[:, 2]
        result[:, 3] = boxes[:, 1] + boxes[:, 3]
        result[:, 0::2] = np.clip(result[:, 0::2], 0, width)
        result[:, 1::2] = np.clip(result[:, 1::2], 0, height)
        if np.any(result[:, 2] <= result[:, 0]) or np.any(result[:, 3] <= result[:, 1]):
            raise ValueError(f"Invalid clipped GT box at {row['sample_id']}")
        return result

    def target(self, index: int):
        import torch

        boxes = torch.from_numpy(self.boxes_xyxy(index))
        return {
            "boxes": boxes,
            "labels": torch.ones((len(boxes),), dtype=torch.int64),
            "image_id": torch.tensor([index], dtype=torch.int64),
        }

    def __getitem__(self, index: int):
        import torch

        rgb, thermal = self.read_images(index)
        rgbt = np.concatenate((rgb, thermal[:, :, None]), axis=2)
        if self.model_type == "reliability_rgbt":
            unused_padding = np.zeros((*thermal.shape, 1), dtype=np.uint8)
            rgbt = np.concatenate((rgbt, unused_padding), axis=2)
        image = torch.from_numpy(np.ascontiguousarray(rgbt)).permute(2, 0, 1).float() / 255.0
        return image, self.target(index)
