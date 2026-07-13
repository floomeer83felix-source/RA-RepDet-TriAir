"""Read-only VisDrone-SEEN adapter for the V50 single-class vehicle task."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
import torch
from torch.utils.data import Dataset
from torchvision.transforms.functional import pil_to_tensor


def collate_fn(batch):
    return tuple(zip(*batch))


class VisDroneSeenVehicleDataset(Dataset):
    """Load RGB images and source-locked COCO vehicle annotations.

    The optional five-channel mode appends thermal and event channels filled
    with 0.0 after RGB is scaled to [0, 1]. It is inference-only and does not
    synthesize either missing modality.
    """

    def __init__(self, data_root, manifest, annotations, five_channel=False):
        self.data_root = Path(data_root).expanduser().resolve()
        self.manifest = Path(manifest).expanduser().resolve()
        self.annotations_path = Path(annotations).expanduser().resolve()
        self.five_channel = bool(five_channel)

        if not self.data_root.is_dir():
            raise FileNotFoundError(f"dataset root not found: {self.data_root}")
        if not self.manifest.is_file():
            raise FileNotFoundError(f"manifest not found: {self.manifest}")
        if not self.annotations_path.is_file():
            raise FileNotFoundError(f"annotations not found: {self.annotations_path}")

        entries = []
        for line_number, raw_line in enumerate(
            self.manifest.read_text(encoding="utf-8").splitlines(), start=1
        ):
            entry = raw_line.strip()
            if not entry or entry.startswith("#"):
                continue
            path = Path(entry)
            image_path = path if path.is_absolute() else self.data_root / path
            if not image_path.is_file():
                raise FileNotFoundError(
                    f"manifest image missing at line {line_number}: {image_path}"
                )
            entries.append((entry.replace("\\", "/"), image_path))

        coco = json.loads(self.annotations_path.read_text(encoding="utf-8"))
        images_by_name = {
            str(item["file_name"]).replace("\\", "/"): item
            for item in coco.get("images", [])
        }
        annotations_by_image = {}
        for annotation in coco.get("annotations", []):
            annotations_by_image.setdefault(int(annotation["image_id"]), []).append(annotation)

        self.samples = []
        for entry, image_path in entries:
            image_info = images_by_name.get(entry)
            if image_info is None:
                raise ValueError(f"manifest entry absent from COCO images: {entry}")
            annotations_for_image = annotations_by_image.get(int(image_info["id"]), [])
            positives = [
                item
                for item in annotations_for_image
                if int(item.get("category_id", 0)) == 1
                and not int(item.get("iscrowd", 0))
                and not int(item.get("ignore", 0))
            ]
            self.samples.append((image_path, image_info, positives))

        if len(self.samples) != len(images_by_name):
            raise ValueError(
                "manifest/COCO image count mismatch: "
                f"manifest={len(self.samples)} coco={len(images_by_name)}"
            )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        image_path, image_info, annotations = self.samples[index]
        with Image.open(image_path) as pil_image:
            image = pil_to_tensor(pil_image.convert("RGB")).to(torch.float32).div_(255.0)

        boxes = []
        for annotation in annotations:
            x, y, width, height = (float(value) for value in annotation["bbox"])
            boxes.append([x, y, x + width, y + height])

        if boxes:
            boxes_tensor = torch.tensor(boxes, dtype=torch.float32)
            labels = torch.ones((len(boxes),), dtype=torch.int64)
        else:
            boxes_tensor = torch.zeros((0, 4), dtype=torch.float32)
            labels = torch.zeros((0,), dtype=torch.int64)

        if self.five_channel:
            zeros = torch.zeros((2, image.shape[1], image.shape[2]), dtype=image.dtype)
            image = torch.cat((image, zeros), dim=0)

        return image, {
            "boxes": boxes_tensor,
            "labels": labels,
            "image_id": torch.tensor([int(image_info["id"])], dtype=torch.int64),
        }

