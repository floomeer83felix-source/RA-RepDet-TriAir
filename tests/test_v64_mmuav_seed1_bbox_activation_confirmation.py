"""CPU/source-lock and post-run contract tests for V64."""

from __future__ import annotations

import inspect
import json
import sys
import unittest
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rarepdet.experimental.v63_bbox_activation_detector import V63BBoxActivationDetector
from rarepdet.tools import run_v64_mmuav_seed1_bbox_activation_confirmation as audit


class V64ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not audit.OUT.is_dir():
            raise unittest.SkipTest("run V64 --prepare-only first")
        cls.protocol = json.loads((audit.OUT / "protocol.json").read_text(encoding="utf-8"))
        cls.lock = json.loads((audit.OUT / "source_lock_v64.json").read_text(encoding="utf-8"))
        cls.init_sha = cls.protocol["seed1_initialization"]["sha256"]
        audit._configure_runtime(cls.init_sha)

    def test_v63_evidence_is_exact_and_immutable(self) -> None:
        self.assertTrue(all(audit.verify_v63()["checks"].values()))
        self.assertEqual(audit.verify_v63(), self.protocol["v63_verification"])

    def test_seed1_initialization_was_generated_once_frozen_and_round_tripped(self) -> None:
        initialization = self.protocol["seed1_initialization"]
        self.assertEqual(initialization["seed"], 1)
        self.assertEqual(initialization["generation_count"], 1)
        self.assertFalse(initialization["regeneration_allowed"])
        self.assertFalse(initialization["trained_checkpoint_used"])
        self.assertTrue(all(initialization["checks"].values()))
        self.assertEqual(audit.sha256(audit.INIT_PATH), self.init_sha)
        candidates = list(audit.LOCAL.glob("*common_init*.pt"))
        self.assertEqual(candidates, [audit.INIT_PATH])
        state = audit.load_frozen_initialization(self.init_sha)
        self.assertEqual(len(state), initialization["tensor_count"])
        self.assertTrue(all(torch.isfinite(value).all() for value in state.values()))

    def test_paired_state_and_step0_outputs_are_bit_identical(self) -> None:
        states, intervention = audit.initial_states(self.init_sha)
        self.assertEqual(list(states[audit.VARIANTS[0]]), list(states[audit.VARIANTS[1]]))
        self.assertTrue(all(torch.equal(states[audit.VARIANTS[0]][key], states[audit.VARIANTS[1]][key])
                            for key in states[audit.VARIANTS[0]]))
        self.assertEqual(intervention["changed_tensor_count"], 0)
        self.assertEqual(intervention["historical_bbox_bias_unchanged"], [0.0] * 4)
        identity = self.protocol["step0_identity"]
        self.assertTrue(all(identity["checks"].values()))
        self.assertTrue(all(identity["alignment_and_fusion_checks"].values()))

    def test_activation_source_location_parameters_and_shared_path(self) -> None:
        native = inspect.getsource(audit.fcos_module.FCOSRegressionHead.forward)
        wrapper = Path(inspect.getsourcefile(V63BBoxActivationDetector) or "").read_text(encoding="utf-8")
        self.assertEqual(native.count("nn.functional.relu(self.bbox_reg(bbox_feature))"), 1)
        self.assertIn("F.softplus(pre_activation, beta=1.0, threshold=20.0)", wrapper)
        self.assertEqual(self.lock["historical_relu_line"], 251)
        self.assertTrue(self.lock["shared_training_inference_head"])
        control, softplus = V63BBoxActivationDetector("relu"), V63BBoxActivationDetector("softplus_b1_t20")
        self.assertEqual(list(control.state_dict()), list(softplus.state_dict()))
        self.assertEqual(sum(parameter.numel() for parameter in control.parameters()),
                         sum(parameter.numel() for parameter in softplus.parameters()))

    def test_softplus_is_once_per_feature_in_train_and_eval(self) -> None:
        model = V63BBoxActivationDetector("softplus_b1_t20")
        head = model.detector.head.regression_head
        channels = head.bbox_reg.in_channels
        features = [torch.randn(1, channels, 4, 4), torch.randn(1, channels, 2, 2)]
        model.train(); train_bbox, _ = head(features)
        model.eval(); eval_bbox, _ = head(features)
        self.assertTrue(torch.equal(train_bbox, eval_bbox))
        self.assertTrue((train_bbox > 0).all())
        self.assertEqual(model.activation_counts(), {"forward_calls": 2, "activation_applications": 4})

    def test_data_order_prefix_subsets_and_devval_guard(self) -> None:
        self.assertEqual(audit.sha256(audit.v63.base.TRAIN_MANIFEST), audit.v63.base.TRAIN_SHA256)
        self.assertEqual(audit.sha256(audit.v63.base.ORDER_PATH), audit.v63.base.ORDER_SHA256)
        self.assertEqual(self.protocol["prefix"]["sha256"],
                         "6345848e3287bea04f5c89927be7a714a6eed549a6b73d352779a6192b5c86ec")
        self.assertEqual(self.protocol["prefix"]["rows"], 200)
        self.assertEqual(self.protocol["prefix"]["unique_rows"], 200)
        self.assertTrue(all(self.protocol["subsets"]["checks"].values()))
        gate = self.protocol["actual_devval_gate"]
        self.assertEqual(gate["row_id"], "devval:00005919")
        self.assertTrue(gate["trace_path_exact"])
        self.assertTrue(gate["historical_optimization_guard_rejects"])

    def test_budget_trace_and_no_metric_path(self) -> None:
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
        self.assertEqual(audit.source_lock(self.init_sha), self.lock)
        self.assertEqual(audit.protected_fingerprint(), self.protocol["protected_baseline"])

    def test_cuda_outputs_when_present(self) -> None:
        path = audit.OUT / "safety_audit.json"
        if not path.exists():
            self.skipTest("CUDA run not complete")
        safety = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(safety["optimizer_steps"], 400)
        self.assertEqual(safety["probe_backward_calls"], 104)
        self.assertEqual(safety["verified_recovery_snapshots"], 26)
        self.assertEqual(safety["initialization_candidates_generated"], 1)
        self.assertTrue(safety["all_recovery_round_trips"])
        self.assertTrue(safety["all_trace_isolation_checks"])
        self.assertTrue(safety["seed1_initialization_unchanged"])
        self.assertEqual(safety["full_devval_rows"], 0)
        self.assertFalse(safety["ap_ar_computed"])

    def test_no_heavy_artifacts_in_git_output(self) -> None:
        forbidden = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".png", ".jpg", ".pkl"}
        files = [path for path in audit.OUT.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertFalse([path for path in files if path.suffix.lower() in forbidden])


if __name__ == "__main__":
    unittest.main()
