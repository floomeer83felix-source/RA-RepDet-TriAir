"""CPU-only checks for frozen M3OT evaluation arithmetic."""

import unittest

import torch

from tools.eval_m3ot_external import infer, mean_std
from tools.m3ot_matching import match_prediction


class M3OTContractTests(unittest.TestCase):
    def test_second_prediction_can_match_second_best_unmatched_gt(self):
        target = {"boxes": torch.tensor([[0, 0, 10, 10], [2, 0, 12, 10]], dtype=torch.float32),
                  "labels": torch.ones(2, dtype=torch.int64)}
        prediction = {"boxes": torch.tensor([[0, 0, 10, 10], [1, 0, 11, 10]], dtype=torch.float32),
                      "scores": torch.tensor([0.9, 0.8]), "labels": torch.ones(2, dtype=torch.int64)}
        result = match_prediction(prediction, target)
        self.assertEqual((result["tp"], result["fp"], result["fn"]), (2, 0, 0))

    def test_duplicate_predictions_and_empty_gt(self):
        prediction = {"boxes": torch.tensor([[0, 0, 10, 10], [0, 0, 10, 10]], dtype=torch.float32),
                      "scores": torch.tensor([0.9, 0.8]), "labels": torch.ones(2, dtype=torch.int64)}
        one_gt = {"boxes": torch.tensor([[0, 0, 10, 10]], dtype=torch.float32),
                  "labels": torch.ones(1, dtype=torch.int64)}
        empty_gt = {"boxes": torch.empty((0, 4)), "labels": torch.empty(0, dtype=torch.int64)}
        result = match_prediction(prediction, one_gt)
        self.assertEqual((result["tp"], result["fp"], result["fn"]), (1, 1, 0))
        result = match_prediction(prediction, empty_gt)
        self.assertEqual((result["tp"], result["fp"], result["fn"]), (0, 2, 0))

    def test_sample_standard_deviation(self):
        mean, std = mean_std([1.0, 2.0, 3.0])
        self.assertEqual((mean, std), (2.0, 1.0))

    def test_inference_records_clipped_and_degenerate_predictions(self):
        class OneImage:
            def __len__(self):
                return 1

            def __getitem__(self, index):
                return torch.zeros((4, 4, 4)), {
                    "boxes": torch.empty((0, 4)), "labels": torch.empty(0, dtype=torch.int64),
                    "image_id": torch.tensor([index]),
                }

        class TwoBoxes(torch.nn.Module):
            def forward(self, images):
                return [{"boxes": torch.tensor([[-1., -1., 3., 3.], [10., 10., 11., 11.]]),
                         "scores": torch.tensor([0.8, 0.7]), "labels": torch.ones(2, dtype=torch.int64)}]

        predictions, clipped, filtered = infer(TwoBoxes(), OneImage(), torch.device("cpu"), 1)
        self.assertEqual((clipped, filtered), (2, 1))
        self.assertEqual(predictions[0]["boxes"], [[0.0, 0.0, 3.0, 3.0]])


if __name__ == "__main__":
    unittest.main()
