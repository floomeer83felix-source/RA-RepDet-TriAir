from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/v72_mmuav_naive_grid_external_domain_stress_test"


def load(name: str):
    return json.loads((RUN / name).read_text(encoding="utf-8"))


class V72NaiveGridStressTest(unittest.TestCase):
    def test_manifest_lock_is_exact(self):
        value = load("devval_manifest_lock.json")
        self.assertEqual(value["rows"], 1845)
        self.assertEqual(value["sequence_count"], 85)
        self.assertEqual(
            value["manifest_sha256"],
            "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54",
        )
        self.assertEqual(
            value["row_order_sha256"],
            "dd454cfbafa39f2556628ad45dc191b39b0c54bb926028447d5f57553456e867",
        )

    def test_six_checkpoint_contract_is_strict(self):
        manifest = load("triair_checkpoint_manifest.json")
        verification = load("triair_checkpoint_verification.json")
        self.assertEqual(manifest["count"], 6)
        self.assertEqual(len(verification["entries"]), 6)
        self.assertTrue(all(row["strict_load"] for row in verification["entries"]))
        self.assertFalse(verification["mmuav_trained_checkpoints_used"])

    def test_naive_adapter_channel_order_and_determinism(self):
        from rarepdet.tools.run_v72_mmuav_naive_grid_stress_test import naive_grid_adapter

        sample = {
            "rgb": torch.full((3, 640, 640), 0.1),
            "ir": torch.full((1, 640, 640), 0.2),
            "event": torch.full((1, 640, 640), 0.3),
            "target_rgb": {
                "boxes": torch.tensor([[1.0, 2.0, 3.0, 4.0]]),
                "labels": torch.tensor([1]),
            },
        }
        first, _ = naive_grid_adapter(sample)
        second, _ = naive_grid_adapter(sample)
        self.assertTrue(torch.equal(first, second))
        self.assertEqual(tuple(first.shape), (5, 640, 640))
        self.assertTrue(torch.equal(first[:3], sample["rgb"]))
        self.assertTrue(torch.equal(first[3:4], sample["ir"]))
        self.assertTrue(torch.equal(first[4:5], sample["event"]))

    def test_adapter_contract_disclaims_registration(self):
        value = load("adapter_contract.json")
        self.assertEqual(value["status"], "FROZEN")
        self.assertFalse(value["learned_alignment"])
        self.assertFalse(value["physical_registration_asserted"])
        self.assertEqual(value["box_geometry"], "RGB letterbox transform only")

    def test_evaluator_constants_are_frozen(self):
        value = load("evaluator_contract.json")
        self.assertEqual(value["score_threshold"], 0.001)
        self.assertEqual(value["nms_threshold"], 0.6)
        self.assertEqual(value["maximum_detections"], [1, 10, 100])
        self.assertEqual(value["recall_threshold_count"], 101)

    def test_aggregation_and_paired_arithmetic(self):
        from rarepdet.tools.run_v72_mmuav_naive_grid_stress_test import METRICS, aggregate_records

        rows = []
        for method, offset in (("matched_early", 0.0), ("reliability_p015", 0.1)):
            for seed in (0, 1, 2):
                row = {"method": method, "seed": seed}
                row.update({metric: offset + seed * 0.01 for metric in METRICS})
                rows.append(row)
        aggregate, paired = aggregate_records(rows)
        self.assertEqual(len(paired), 3)
        self.assertTrue(all(math.isclose(row["ap50_95"], 0.1) for row in paired))
        self.assertTrue(
            math.isclose(
                aggregate["paired_reliability_minus_early"]["ap50_95"]["mean"],
                0.1,
            )
        )

    def test_claim_boundary_is_exact(self):
        value = load("claim_boundary.json")
        self.assertIn("naive normalized-grid five-channel adapter", value["scientific_label"])
        self.assertFalse(value["independent_or_blind_external_test"])
        self.assertFalse(value["physical_multimodal_registration"])

    def test_attempt_ledger_has_no_duplicate_checkpoint_attempts(self):
        value = load("attempt_ledger.json")
        self.assertTrue(all(len(attempts) <= 1 for attempts in value["checkpoint_attempts"].values()))

    def test_completed_metrics_are_finite_when_present(self):
        value = load("per_checkpoint_metrics.json")
        for row in value["records"]:
            for metric in ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100"):
                self.assertTrue(math.isfinite(float(row[metric])))
            self.assertEqual(row["images"], 1845)
            self.assertEqual(row["attempt_count"], 1)

    def test_outputs_are_compact_and_private_safe(self):
        forbidden = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".pkl", ".pickle", ".jpg", ".png", ".mp4"}
        for path in RUN.rglob("*"):
            if not path.is_file():
                continue
            self.assertNotIn(path.suffix.lower(), forbidden)
            self.assertLess(path.stat().st_size, 1024 * 1024)
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("E:\\\\", text)
            self.assertNotIn("D:\\\\", text)


if __name__ == "__main__":
    unittest.main()
