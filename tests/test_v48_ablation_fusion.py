"""Smoke tests for the V48 static fusion controls."""

import argparse
from pathlib import Path
import sys
import tempfile
import unittest

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.models.early_fusion_fcos import build_detector
from rarepdet.train_early_fusion import save_checkpoint


MODEL_TYPES = ("early", "reliability", "ra_static_equal", "ra_stems_project")
STATIC_MODEL_TYPES = ("ra_static_equal", "ra_stems_project")


def build(model_type):
    return build_detector(
        model_type=model_type,
        img_size=64,
        score_thresh=1.0,
        detections_per_img=10,
    )


class V48AblationFusionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)
        torch.manual_seed(48)
        cls.image = torch.randn(5, 64, 64)
        cls.target = {
            "boxes": torch.tensor([[8.0, 8.0, 40.0, 40.0]]),
            "labels": torch.tensor([1], dtype=torch.int64),
            "image_id": torch.tensor([48]),
        }

    def test_all_factories_construct(self):
        for model_type in MODEL_TYPES:
            with self.subTest(model_type=model_type):
                model = build(model_type)
                self.assertEqual(model.backbone.out_channels, 128)
                del model

    def test_static_controls_forward_and_gradients(self):
        for model_type in STATIC_MODEL_TYPES:
            with self.subTest(model_type=model_type):
                model = build(model_type)
                model.train()
                losses = model([self.image], [self.target])
                self.assertTrue(losses)
                total_loss = sum(losses.values())
                self.assertTrue(torch.isfinite(total_loss))
                total_loss.backward()
                self.assertTrue(any(parameter.grad is not None for parameter in model.parameters()))
                model.eval()
                with torch.no_grad():
                    outputs = model([self.image])
                self.assertEqual(len(outputs), 1)
                self.assertEqual(set(outputs[0]), {"boxes", "labels", "scores"})
                self.assertEqual(outputs[0]["boxes"].ndim, 2)
                del model

    def test_static_controls_checkpoint_round_trip_and_determinism(self):
        for model_type in STATIC_MODEL_TYPES:
            with self.subTest(model_type=model_type):
                model = build(model_type).eval()
                optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
                args = argparse.Namespace(model=model_type, img_size=64)
                with tempfile.TemporaryDirectory() as directory:
                    checkpoint_path = Path(directory) / "checkpoint.pt"
                    save_checkpoint(
                        checkpoint_path,
                        model,
                        optimizer,
                        epoch=1,
                        args=args,
                        best_ap50=0.0,
                        metrics={"ap50": 0.0},
                    )
                    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
                    reloaded = build(checkpoint["model_cfg"]["model_type"]).eval()
                    reloaded.load_state_dict(checkpoint["model_state"], strict=True)
                    with torch.no_grad():
                        first = reloaded([self.image])[0]
                        second = reloaded([self.image])[0]
                    for key in ("boxes", "labels", "scores"):
                        self.assertTrue(torch.equal(first[key], second[key]), key)
                del model


if __name__ == "__main__":
    unittest.main(verbosity=2)
