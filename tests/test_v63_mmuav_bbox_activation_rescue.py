"""CPU/source-lock and post-run contract tests for V63."""

from __future__ import annotations

import csv
import inspect
import json
import sys
import tempfile
import unittest
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.v63_bbox_activation_detector import V63BBoxActivationDetector
from rarepdet.tools import run_v63_mmuav_bbox_activation_rescue as audit
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import target_to_device


class V63ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not audit.OUT.is_dir():
            raise unittest.SkipTest("run V63 --prepare-only first")
        cls.protocol = json.loads((audit.OUT / "protocol.json").read_text(encoding="utf-8"))
        cls.lock = json.loads((audit.OUT / "source_lock_v63.json").read_text(encoding="utf-8"))

    def test_historical_relu_and_softplus_source_contract(self) -> None:
        native = inspect.getsource(audit.fcos_module.FCOSRegressionHead.forward)
        intervention = Path(inspect.getsourcefile(audit.V63BBoxActivationDetector) or "").read_text(encoding="utf-8")
        self.assertEqual(native.count("nn.functional.relu(self.bbox_reg(bbox_feature))"), 1)
        self.assertIn("softplus", intervention)
        self.assertEqual(self.lock["historical_relu_line"], 251)
        self.assertEqual(self.lock["softplus_expression"], "F.softplus(pre_activation, beta=1.0, threshold=20.0)")
        self.assertTrue(self.lock["shared_training_inference_head"])

    def test_activation_is_parameter_free_and_state_keys_are_identical(self) -> None:
        control = V63BBoxActivationDetector("relu")
        softplus = V63BBoxActivationDetector("softplus_b1_t20")
        self.assertEqual(list(control.state_dict()), list(softplus.state_dict()))
        self.assertEqual(sum(parameter.numel() for parameter in control.parameters()),
                         sum(parameter.numel() for parameter in softplus.parameters()))
        self.assertFalse([name for name, _ in softplus.named_parameters() if "softplus" in name.lower()])

    def test_regression_head_train_and_eval_use_same_softplus_forward(self) -> None:
        model = V63BBoxActivationDetector("softplus_b1_t20")
        head = model.detector.head.regression_head
        channels = head.bbox_reg.in_channels
        features = [torch.randn(1, channels, 4, 4), torch.randn(1, channels, 2, 2)]
        model.train(); train_bbox, _ = head(features)
        model.eval(); eval_bbox, _ = head(features)
        self.assertTrue(torch.equal(train_bbox, eval_bbox))
        self.assertTrue((train_bbox > 0).all())
        self.assertEqual(model.activation_counts(), {"forward_calls": 2, "activation_applications": 4})

    def test_v62_data_order_subsets_and_initialization_are_exact(self) -> None:
        self.assertTrue(all(audit.verify_v62()["checks"].values()))
        self.assertEqual(audit.verify_v62(), self.protocol["v62_verification"])
        self.assertEqual(audit.sha256(audit.base.TRAIN_MANIFEST), audit.base.TRAIN_SHA256)
        self.assertEqual(audit.sha256(audit.base.ORDER_PATH), audit.base.ORDER_SHA256)
        self.assertEqual(audit.sha256(audit.base.COMMON_INIT), audit.base.INIT_SHA256)
        self.assertTrue(all(self.protocol["subsets"]["checks"].values()))
        order = json.loads(audit.base.ORDER_INDICES_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.protocol["prefix"]["indices"], order[:200])
        self.assertEqual(self.protocol["prefix"]["rows"], 200)
        self.assertEqual(self.protocol["prefix"]["unique_rows"], 200)

    def test_step0_identity_and_activation_only_difference(self) -> None:
        checks = self.protocol["step0_identity"]["checks"]
        self.assertTrue(all(checks.values()))
        initialization = self.protocol["initialization"]
        self.assertEqual(initialization["changed_tensor_count"], 0)
        self.assertEqual(initialization["changed_element_count"], 0)
        self.assertEqual(initialization["historical_bbox_bias_unchanged"], [0.0, 0.0, 0.0, 0.0])
        self.assertEqual(initialization["softplus"], {"beta": 1.0, "threshold": 20.0})

    def test_actual_devval_trace_path_and_train_guard(self) -> None:
        manifest = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"
        dataset = MMUAVFeatureAlignmentDataset(manifest, 320, validate_paths=False)
        _, sample = audit.v62.actual_failed_devval_sample(dataset)
        moved = audit.trace_target_to_device(sample, torch.device("cpu"))[0]
        self.assertEqual(sample["original_row_id"], audit.FAILED_ROW_ID)
        self.assertTrue(torch.equal(moved["boxes"], sample["target_rgb"]["boxes"]))
        self.assertTrue(torch.equal(moved["labels"], sample["target_rgb"]["labels"]))
        with self.assertRaisesRegex(RuntimeError, "Invalid optimization sample"):
            target_to_device(sample, torch.device("cpu"))

    def test_atomic_recovery_round_trip(self) -> None:
        model = torch.nn.Linear(3, 2)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
        model(torch.ones(1, 3)).sum().backward(); optimizer.step()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); log_path = root / "log.csv"
            with log_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle); writer.writerow(["step"]); writer.writerow([1])
                info = audit.v62.log_contract(handle, log_path)
                result = audit.atomic_snapshot(model, optimizer, 1, audit.VARIANTS[0], log_path, info,
                                               [{"event": "trace_complete", "trace_step": 0}], root / "latest.pt")
        self.assertTrue(all(result["round_trip_checks"].values()))
        self.assertEqual(result["log_row_count"], 1)

    def test_fixed_budget_trace_and_no_metric_path(self) -> None:
        self.assertEqual(self.protocol["run_order"], list(audit.VARIANTS))
        self.assertEqual(self.protocol["steps_per_variant"], 200)
        self.assertEqual(self.protocol["optimizer_step_limit"], 400)
        self.assertEqual(self.protocol["probe_backward_limit"], 104)
        self.assertEqual(list(audit.TRACE_STEPS), [0, 1, 2, 3, 5, 10, 15, 20, 30, 50, 100, 150, 200])
        source = Path(audit.__file__).read_text(encoding="utf-8")
        self.assertNotIn("coco_detection_metrics", source)
        self.assertNotIn("detections_per_img", source)

    def test_source_and_protected_locks(self) -> None:
        self.assertEqual(audit.git("rev-parse", "HEAD"), audit.START_COMMIT)
        self.assertEqual(audit.source_lock(), self.lock)
        self.assertEqual(audit.protected_fingerprint(), self.protocol["protected_baseline"])

    def test_cuda_outputs_when_present(self) -> None:
        path = audit.OUT / "safety_audit.json"
        if not path.exists():
            self.skipTest("CUDA run not complete")
        safety = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(safety["optimizer_steps"], 400)
        self.assertEqual(safety["probe_backward_calls"], 104)
        self.assertEqual(safety["verified_recovery_snapshots"], 26)
        self.assertTrue(safety["all_recovery_round_trips"])
        self.assertTrue(safety["all_trace_isolation_checks"])
        self.assertEqual(safety["frozen_devval_rows_per_variant"], 32)
        self.assertEqual(safety["full_devval_rows"], 0)
        self.assertFalse(safety["ap_ar_computed"])

    def test_no_heavy_artifacts_in_git_output(self) -> None:
        forbidden = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".png", ".jpg", ".pkl"}
        files = [path for path in audit.OUT.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertFalse([path for path in files if path.suffix.lower() in forbidden])


if __name__ == "__main__":
    unittest.main()
