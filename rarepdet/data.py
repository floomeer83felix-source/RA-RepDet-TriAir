import random

import torch
from torch.utils.data import Dataset

from datasets.triair_dataset import TriAirDataset


class DetectionTriAirDataset(Dataset):
    """TriAir adapter for torchvision detection models.

    TriAir stores vehicle as raw class 0. torchvision detection models reserve
    label 0 for background, so this adapter shifts foreground labels to 1.
    Empty label samples remain valid with boxes=(0,4), labels=(0,).
    """

    def __init__(self, data_root, split_file=None, mode="rgbte", train=False, modality_dropout=0.0):
        self.dataset = TriAirDataset(data_root, mode=mode, split_file=split_file)
        self.train = train
        self.modality_dropout = float(modality_dropout)
        if self.modality_dropout < 0.0 or self.modality_dropout >= 1.0:
            raise ValueError("--modality-dropout must be in [0, 1)")

    def __len__(self):
        return len(self.dataset)

    def _apply_modality_dropout(self, image):
        if not self.train or self.modality_dropout <= 0.0:
            return image

        original = image.clone()
        dropped = []
        # Groups are RGB, thermal, and event. This is intentionally simple and
        # disabled by default; no mosaic, mixup, or complex augmentation is used.
        if random.random() < self.modality_dropout:
            image[0:3] = 0
            dropped.append("rgb")
        if random.random() < self.modality_dropout:
            image[3:4] = 0
            dropped.append("thermal")
        if random.random() < self.modality_dropout:
            image[4:5] = 0
            dropped.append("event")

        if len(dropped) == 3:
            keep = random.choice(("rgb", "thermal", "event"))
            if keep == "rgb":
                image[0:3] = original[0:3]
            elif keep == "thermal":
                image[3:4] = original[3:4]
            else:
                image[4:5] = original[4:5]
        return image

    def __getitem__(self, index):
        image, target = self.dataset[index]
        image = image / 255.0
        image = self._apply_modality_dropout(image)

        boxes = target["boxes"].clone()
        labels = target["labels"].clone()

        if boxes.numel() > 0:
            _, height, width = image.shape
            boxes[:, 0::2].clamp_(min=0.0, max=float(width))
            boxes[:, 1::2].clamp_(min=0.0, max=float(height))
            keep = (boxes[:, 2] > boxes[:, 0]) & (boxes[:, 3] > boxes[:, 1])
            boxes = boxes[keep]
            labels = labels[keep]

        # Raw TriAir class 0 -> torchvision foreground label 1.
        if labels.numel() > 0:
            labels = labels + 1

        return image, {
            "boxes": boxes.to(torch.float32),
            "labels": labels.to(torch.int64),
            "image_id": torch.tensor([index], dtype=torch.int64),
        }


def get_sample_info(dataset, index):
    base = dataset.dataset if hasattr(dataset, "dataset") else dataset
    return base.sample_infos[index]
