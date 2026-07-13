import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image
import torch

from datasets.visdrone_seen_dataset import VisDroneSeenVehicleDataset
from rarepdet.tools.prepare_v50_visdrone_seen import (
    SEEN_IDS,
    VEHICLE_ORIGINAL_IDS,
    VEHICLE_YOLO_IDS,
)
from rarepdet.v50_coco import evaluate_detections, outputs_to_detections


def build_fixture(tmp_path):
    image_dir = tmp_path / "images" / "val"
    image_dir.mkdir(parents=True)
    image_path = image_dir / "sample.jpg"
    Image.new("RGB", (32, 24), color=(64, 128, 255)).save(image_path)
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("images/val/sample.jpg\n", encoding="utf-8")
    annotations = tmp_path / "annotations.json"
    annotations.write_text(
        json.dumps(
            {
                "info": {},
                "licenses": [],
                "images": [
                    {"id": 1, "file_name": "images/val/sample.jpg", "width": 32, "height": 24}
                ],
                "annotations": [
                    {
                        "id": 1,
                        "image_id": 1,
                        "category_id": 1,
                        "bbox": [2, 3, 10, 8],
                        "area": 80,
                        "iscrowd": 0,
                        "ignore": 0,
                    },
                    {
                        "id": 2,
                        "image_id": 1,
                        "category_id": 1,
                        "bbox": [20, 10, 8, 10],
                        "area": 80,
                        "iscrowd": 1,
                        "ignore": 1,
                    },
                ],
                "categories": [{"id": 1, "name": "vehicle"}],
            }
        ),
        encoding="utf-8",
    )
    return manifest, annotations


class V50DatasetTests(unittest.TestCase):
    def test_frozen_mapping(self):
        self.assertEqual(SEEN_IDS, {0, 3, 4, 5, 8, 9})
        self.assertEqual(VEHICLE_YOLO_IDS, {3, 4, 5, 8})
        self.assertEqual(VEHICLE_ORIGINAL_IDS, {4, 5, 6, 9})

    def test_rgb_and_zero_channel_adapter(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, annotations = build_fixture(root)
            rgb = VisDroneSeenVehicleDataset(root, manifest, annotations, five_channel=False)
            image, target = rgb[0]
            self.assertEqual(tuple(image.shape), (3, 24, 32))
            self.assertEqual(image.dtype, torch.float32)
            self.assertLessEqual(0.0, float(image.min()))
            self.assertLessEqual(float(image.max()), 1.0)
            self.assertEqual(target["boxes"].tolist(), [[2.0, 3.0, 12.0, 11.0]])

            five = VisDroneSeenVehicleDataset(root, manifest, annotations, five_channel=True)
            image, _ = five[0]
            self.assertEqual(tuple(image.shape), (5, 24, 32))
            self.assertEqual(torch.count_nonzero(image[3:]).item(), 0)

    def test_coco_metric_and_detection_conversion(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, annotations = build_fixture(root)
            outputs = [
                {
                    "boxes": torch.tensor([[2.0, 3.0, 12.0, 11.0]]),
                    "scores": torch.tensor([0.9]),
                    "labels": torch.tensor([1]),
                }
            ]
            targets = [{"image_id": torch.tensor([1])}]
            detections = outputs_to_detections(outputs, targets)
            metrics = evaluate_detections(annotations, detections)
            self.assertEqual(metrics["gt_boxes"], 1)
            self.assertEqual(metrics["ignored_regions"], 1)
            self.assertAlmostEqual(metrics["ap50"], 1.0)


if __name__ == "__main__":
    unittest.main()
