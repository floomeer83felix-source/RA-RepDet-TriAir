"""Private, CPU-safe MM-UAV adapter for the V53 RGB-supervised contract."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import Dataset


def _load_image(path: Path, channels: int) -> tuple[torch.Tensor, tuple[int, int]]:
    mode = "RGB" if channels == 3 else "L"
    with Image.open(path) as image:
        image = image.convert(mode)
        width, height = image.size
        array = np.asarray(image, dtype=np.uint8).copy()
    if channels == 1:
        array = array[:, :, None]
    tensor = torch.from_numpy(array).permute(2, 0, 1).float().div_(255.0)
    return tensor, (height, width)


def letterbox(tensor: torch.Tensor, output_size: tuple[int, int]) -> tuple[torch.Tensor, dict[str, object]]:
    _, height, width = tensor.shape
    output_height, output_width = output_size
    scale = min(output_width / width, output_height / height)
    resized_width = max(1, round(width * scale))
    resized_height = max(1, round(height * scale))
    resized = F.interpolate(tensor.unsqueeze(0), size=(resized_height, resized_width), mode="bilinear",
                            align_corners=False).squeeze(0)
    pad_left = (output_width - resized_width) // 2
    pad_top = (output_height - resized_height) // 2
    pad_right = output_width - resized_width - pad_left
    pad_bottom = output_height - resized_height - pad_top
    output = F.pad(resized, (pad_left, pad_right, pad_top, pad_bottom))
    transform = {
        "type": "independent_letterbox_not_registration",
        "input_size": [height, width],
        "output_size": [output_height, output_width],
        "scale_x": resized_width / width,
        "scale_y": resized_height / height,
        "pad_left": pad_left,
        "pad_top": pad_top,
        "pad_right": pad_right,
        "pad_bottom": pad_bottom,
    }
    return output, transform


def transform_rgb_boxes(boxes: torch.Tensor, transform: dict[str, object]) -> torch.Tensor:
    if boxes.numel() == 0:
        return boxes.reshape(0, 4)
    result = boxes.clone()
    result[:, [0, 2]] = result[:, [0, 2]] * float(transform["scale_x"]) + int(transform["pad_left"])
    result[:, [1, 3]] = result[:, [1, 3]] * float(transform["scale_y"]) + int(transform["pad_top"])
    return result


def parse_rgb_targets(path: Path, frame_index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    boxes, labels, track_ids = [], [], []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            if len(row) < 6 or int(float(row[0])) != frame_index:
                continue
            x, y, width, height = map(float, row[2:6])
            if width <= 0 or height <= 0:
                continue
            boxes.append((x, y, x + width, y + height))
            labels.append(1)  # torchvision detector foreground label; category is provider "drone".
            track_ids.append(int(float(row[1])))
    if not boxes:
        raise ValueError(f"RGB-supervised manifest row has no valid RGB target: {path}, frame {frame_index}")
    return (torch.tensor(boxes, dtype=torch.float32), torch.tensor(labels, dtype=torch.int64),
            torch.tensor(track_ids, dtype=torch.int64))


class MMUAVFeatureAlignmentDataset(Dataset):
    """Loads one synchronized triplet at a time without raw-channel concatenation."""

    required_columns = {
        "original_row_id", "split", "sequence", "frame_index", "rgb", "ir", "event", "gt_rgb", "gt_ir",
        "rgb_annotation_rows", "ir_annotation_rows", "common_track_ids",
    }

    def __init__(self, manifest: str | Path, branch_size: int | tuple[int, int] = 320,
                 validate_paths: bool = True) -> None:
        self.manifest = Path(manifest)
        if isinstance(branch_size, int):
            branch_size = (branch_size, branch_size)
        self.branch_size = tuple(branch_size)
        with self.manifest.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            missing = self.required_columns - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"Manifest missing columns: {sorted(missing)}")
            self.rows = list(reader)
        if not self.rows:
            raise ValueError(f"Empty manifest: {self.manifest}")
        if validate_paths:
            self.validate_all_paths()

    def validate_all_paths(self) -> None:
        for row in self.rows:
            if int(row["rgb_annotation_rows"]) <= 0:
                raise ValueError(f"Non-RGB-supervised row in manifest: {row['original_row_id']}")
            frame = int(row["frame_index"])
            for key in ("rgb", "ir", "event", "gt_rgb"):
                path = Path(row[key])
                if not path.is_file():
                    raise FileNotFoundError(f"Missing {key} path for {row['original_row_id']}: {path}")
            media_indices = {int(Path(row[key]).stem) for key in ("rgb", "ir", "event")}
            if media_indices != {frame}:
                raise ValueError(f"Synchronized frame mismatch for {row['original_row_id']}: {media_indices} vs {frame}")

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, object]:
        row = self.rows[index]
        frame = int(row["frame_index"])
        rgb_native, rgb_shape = _load_image(Path(row["rgb"]), 3)
        ir_native, ir_shape = _load_image(Path(row["ir"]), 1)
        event_native, event_shape = _load_image(Path(row["event"]), 1)
        rgb, rgb_transform = letterbox(rgb_native, self.branch_size)
        ir, ir_transform = letterbox(ir_native, self.branch_size)
        event, event_transform = letterbox(event_native, self.branch_size)
        boxes, labels, track_ids = parse_rgb_targets(Path(row["gt_rgb"]), frame)
        boxes = transform_rgb_boxes(boxes, rgb_transform)
        target = {"boxes": boxes, "labels": labels, "track_ids": track_ids}
        common_ids = tuple(int(value) for value in row["common_track_ids"].split(";") if value)
        return {
            "rgb": rgb,
            "ir": ir,
            "event": event,
            "target_rgb": target,
            "sequence_id": row["sequence"],
            "frame_index": frame,
            "split": row["split"],
            "original_row_id": row["original_row_id"],
            "rgb_gt_present": True,
            "ir_gt_present": int(row["ir_annotation_rows"]) > 0,
            "common_track_ids": common_ids,
            "modality_native_shapes": {"rgb": rgb_shape, "ir": ir_shape, "event": event_shape},
            "modality_transforms": {"rgb": rgb_transform, "ir": ir_transform, "event": event_transform},
        }


def collate_fn(batch: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    return list(batch)
