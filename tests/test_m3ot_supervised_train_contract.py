"""Small training-protocol guards that do not require GPU or source images."""

import unittest

from tools.train_m3ot_supervised import (
    BATCH_SIZE, EPOCHS, IMAGE_SIZE, LR, MAX_DETECTIONS, NMS_IOU,
    SCORE_FLOOR, WEIGHT_DECAY, should_update_best,
)


class TrainingContractTests(unittest.TestCase):
    def test_frozen_numerical_configuration(self):
        self.assertEqual((EPOCHS, BATCH_SIZE, IMAGE_SIZE), (50, 4, 640))
        self.assertEqual((LR, WEIGHT_DECAY), (1e-4, 1e-4))
        self.assertEqual((SCORE_FLOOR, NMS_IOU, MAX_DETECTIONS), (0.001, 0.60, 100))

    def test_best_checkpoint_keeps_earliest_tie(self):
        self.assertTrue(should_update_best(0.1, -1))
        self.assertFalse(should_update_best(0.1, 0.1))
        self.assertFalse(should_update_best(0.09, 0.1))


if __name__ == "__main__":
    unittest.main()
