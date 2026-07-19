"""Contract tests for the frozen V61 paired bbox-bias pilot."""

from __future__ import annotations

import csv
import inspect
import json
import sys
import unittest
from pathlib import Path

import torch
from torchvision.models.detection import fcos as fcos_module


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rarepdet.tools import run_v61_mmuav_bbox_bias_pilot as audit


class V61ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not audit.OUT.is_dir():
            raise unittest.SkipTest("run V61 --prepare-only first")
        cls.protocol = json.loads((audit.OUT / "protocol.json").read_text(encoding="utf-8"))
        cls.lock = json.loads((audit.OUT / "source_lock_v61.json").read_text(encoding="utf-8"))

    def test_evidence_data_order_and_subset_locks(self) -> None:
        self.assertEqual(audit.sha256(audit.TRAIN_MANIFEST), audit.TRAIN_SHA256)
        self.assertEqual(audit.sha256(audit.ORDER_PATH), audit.ORDER_SHA256)
        self.assertEqual(audit.sha256(audit.COMMON_INIT), audit.INIT_SHA256)
        self.assertTrue(all(self.protocol["v60_verification"]["checks"].values()))
        self.assertTrue(all(self.protocol["subsets"]["checks"].values()))

    def test_prefix_is_exact_unique_first_500(self) -> None:
        full = json.loads(audit.ORDER_INDICES_PATH.read_text(encoding="utf-8"))
        prefix = json.loads((audit.OUT / "train_prefix_500_indices.json").read_text(encoding="utf-8"))
        self.assertEqual(prefix, full[:500])
        self.assertEqual(len(prefix), len(set(prefix)))
        self.assertEqual(self.protocol["prefix"]["rows"], 500)
        self.assertEqual((audit.OUT / "train_prefix_500_sha256.txt").read_text().strip(),
                         self.protocol["prefix"]["sha256"])

    def test_intervention_is_only_exact_four_element_p001(self) -> None:
        delta = json.loads((audit.OUT / "intervention_delta.json").read_text(encoding="utf-8"))
        self.assertEqual(delta["parameter_name"], audit.BBOX_BIAS_KEY)
        self.assertEqual(delta["before"], [0.0] * 4)
        float32_p001 = torch.tensor(0.01, dtype=torch.float32).item()
        self.assertEqual(delta["after"], [float32_p001] * 4)
        self.assertEqual(delta["delta"], [float32_p001] * 4)
        self.assertEqual(delta["changed_tensor_count"], 1)
        self.assertEqual(delta["changed_element_count"], 4)
        self.assertTrue(delta["all_other_tensors_bit_identical"])
        self.assertFalse(delta["bias_sweep"])

    def test_paired_configuration_and_dormant_scorer(self) -> None:
        configs = self.protocol["configs"]
        differing = [key for key in configs[audit.VARIANTS[0]]
                     if configs[audit.VARIANTS[0]][key] != configs[audit.VARIANTS[1]][key]]
        self.assertEqual(set(differing), {"name", "initial_bbox_bias"})
        for config in configs.values():
            self.assertEqual(config["fusion_weights"], [1 / 3, 1 / 3, 1 / 3])
            self.assertTrue(config["alignment_enabled"])
            self.assertFalse(config["reliability_scorer_active"])
            self.assertEqual(config["optimizer"], "AdamW")
            self.assertEqual(config["steps"], 500)

    def test_fixed_run_order_and_budgets(self) -> None:
        self.assertEqual(self.protocol["run_order"], list(audit.VARIANTS))
        self.assertEqual(self.protocol["steps_per_variant"], 500)
        self.assertEqual(self.protocol["optimizer_step_limit"], 1000)
        self.assertEqual(self.protocol["probe_backward_limit"], 96)
        self.assertEqual(list(audit.TRACE_STEPS), [0, 1, 2, 5, 10, 20, 50, 100, 200, 300, 400, 500])

    def test_actual_torchvision_activation_loss_and_matching_path(self) -> None:
        self.assertIn("functional.relu", inspect.getsource(fcos_module.FCOSRegressionHead.forward))
        self.assertIn("generalized_box_iou_loss", inspect.getsource(fcos_module.FCOSHead.compute_loss))
        self.assertIn("pairwise", inspect.getsource(audit.matched_anchor_count))
        self.assertIn("box_coder.decode", inspect.getsource(audit.geometry_row))

    def test_no_sweep_ap_full_devval_or_extension_path(self) -> None:
        source = Path(audit.__file__).read_text(encoding="utf-8")
        self.assertNotIn("coco_detection_metrics", source)
        self.assertNotIn("detections_per_img", source)
        self.assertNotIn("score_thresh", source)
        self.assertNotIn("scheduler.step", source)
        self.assertEqual(source.count("torch.optim.AdamW"), 1)
        self.assertEqual(source.count("optimizer.step()"), 1)
        self.assertEqual(source.count("bias.fill_(0.01)"), 1)

    def test_source_and_protected_locks(self) -> None:
        self.assertEqual(audit.git("rev-parse", "HEAD"), audit.START_COMMIT)
        self.assertEqual(audit.source_lock()["source_hashes"], self.lock["source_hashes"])
        self.assertEqual(audit.aggregate_fingerprint(audit.protected_paths()), self.protocol["protected_baseline"])

    def test_cuda_outputs_respect_all_limits_when_present(self) -> None:
        path = audit.OUT / "safety_audit.json"
        if not path.exists():
            self.skipTest("CUDA run not complete")
        safety = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(safety["optimizer_steps"], 1000)
        self.assertEqual(safety["per_variant_optimizer_steps"], {name: 500 for name in audit.VARIANTS})
        self.assertEqual(safety["probe_backward_calls"], 96)
        self.assertTrue(safety["all_trace_isolation_checks"])
        self.assertTrue(safety["protected_fingerprint_unchanged"])
        self.assertEqual(safety["full_devval_rows"], 0)
        self.assertFalse(safety["ap_ar_computed"])
        with (audit.OUT / "per_variant_training_log.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 1000)
        self.assertEqual([row["variant"] for row in rows[:500]], [audit.VARIANTS[0]] * 500)
        self.assertEqual([row["variant"] for row in rows[500:]], [audit.VARIANTS[1]] * 500)
        expected_ids = (audit.OUT / "train_prefix_500.txt").read_text().splitlines()
        self.assertEqual([row["original_row_id"] for row in rows[:500]], expected_ids)
        self.assertEqual([row["original_row_id"] for row in rows[500:]], expected_ids)

    def test_classification_uses_preregistered_joint_definitions(self) -> None:
        source = inspect.getsource(audit.trace_classification)
        self.assertIn('valid == 0 and all_zero_grad', source)
        self.assertIn('valid > 0 and any_nonzero_grad', source)
        comparison = audit.OUT / "paired_trace_comparison.json"
        if comparison.exists():
            payload = json.loads(comparison.read_text(encoding="utf-8"))
            self.assertEqual(set(payload["trace_classifications"]), set(audit.VARIANTS))
            self.assertTrue(payload["single_seed_early_engineering_evidence_only"])

    def test_only_compact_git_artifacts(self) -> None:
        forbidden = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".png", ".jpg", ".pkl"}
        files = [path for path in audit.OUT.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertFalse([path for path in files if path.suffix.lower() in forbidden])
        self.assertLess(max(path.stat().st_size for path in files), 30 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
