from __future__ import annotations

import unittest

import torch

from rarepdet.experimental.v73_alignment_transfer_detector import V73AlignmentTransferDetector
from rarepdet.tools import run_v73_mmuav_transfer_benchmark as v73


class V73ContractTests(unittest.TestCase):
    def test_equal_and_reliability_share_state_contract(self) -> None:
        equal = V73AlignmentTransferDetector("equal")
        reliability = V73AlignmentTransferDetector("reliability")
        self.assertEqual(list(equal.state_dict()), list(reliability.state_dict()))
        self.assertEqual(equal.image_size, 640)
        self.assertEqual(reliability.image_size, 640)
        self.assertEqual(equal.detector.backbone.out_channels, 128)

    def test_reliability_final_layer_is_zero(self) -> None:
        model = V73AlignmentTransferDetector("reliability")
        final = model.feature_scaffold.reliability_scorer[-1]
        self.assertEqual(torch.count_nonzero(final.weight).item(), 0)
        self.assertEqual(torch.count_nonzero(final.bias).item(), 0)

    def test_softplus_is_installed_for_both_modes(self) -> None:
        for mode in ("equal", "reliability"):
            model = V73AlignmentTransferDetector(mode)
            self.assertEqual(model.bbox_activation, "softplus_b1_t20")
            self.assertEqual(model.activation_counts(), {"forward_calls": 0, "activation_applications": 0})

    def test_learning_rate_schedule_boundaries(self) -> None:
        self.assertAlmostEqual(v73.lr_for_step(1), 2e-7)
        self.assertAlmostEqual(v73.lr_for_step(500), 1e-4)
        self.assertAlmostEqual(v73.lr_for_step(v73.STEPS_PER_RUN), 1e-6)
        self.assertGreater(v73.lr_for_step(501), v73.lr_for_step(5000))

    def test_frozen_run_order_and_budget(self) -> None:
        expected = [
            f"v73_seed{seed}_{method}"
            for seed in (0, 1, 2)
            for method in ("scratch_equal", "triair_init_equal", "triair_init_reliability")
        ]
        self.assertEqual([v73.run_id(seed, method) for seed, method in v73.RUN_ORDER], expected)
        self.assertEqual(v73.STEPS_PER_RUN, 71870)
        self.assertEqual(v73.TOTAL_STEPS, 646830)


if __name__ == "__main__":
    unittest.main()
