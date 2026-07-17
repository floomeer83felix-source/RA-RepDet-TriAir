"""Contract tests for the bounded V60 bbox-collapse provenance audit."""

from __future__ import annotations

import hashlib
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

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.tools import run_v60_bbox_collapse_provenance_audit as audit


LOG_HASHES = {
    "v55_alignment_off": "78fa369fad95d6bebad5d1a9cf0721dc8b7839c3df3f2f5008048540b36b3ea1",
    "v55_alignment_on": "2a5f22ab392c861501865671cb53198434eaeee37ec1cd55765ddd10f96f711e",
    "v57_equal": "551f7bc09e202fde8b6aea14dd1511c0a0ee56ca14d5b49ad4cf09b60c11b74f",
    "v57_reliability": "68f9386142cc06dccd22f308cf712fc7bcc9cf6ec36c215e550b5ede83ae138c",
}


class V60AuditContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not audit.OUT.is_dir():
            raise unittest.SkipTest("run --prepare-only before the V60 contract tests")
        cls.protocol = json.loads((audit.OUT / "protocol.json").read_text(encoding="utf-8"))
        cls.lock = json.loads((audit.OUT / "source_lock_v60.json").read_text(encoding="utf-8"))

    def test_manifest_and_v59_evidence_locks(self) -> None:
        self.assertEqual(audit.sha256(audit.TRAIN_MANIFEST), audit.TRAIN_SHA256)
        self.assertEqual(audit.sha256(audit.DEVVAL_MANIFEST), audit.DEVVAL_SHA256)
        self.assertTrue(all(audit.verify_v59()["checks"].values()))
        self.assertEqual(self.protocol["train_rows"], 7187)
        self.assertEqual(self.protocol["devval_rows"], 1845)

    def test_all_five_checkpoint_contracts(self) -> None:
        self.assertEqual(len(audit.STATE_SPECS), 5)
        verification = json.loads((audit.OUT / "checkpoint_verification.json").read_text(encoding="utf-8"))
        for name, spec in audit.STATE_SPECS.items():
            self.assertEqual(audit.sha256(spec["path"]), spec["sha256"])
            self.assertEqual(verification[name]["sha256"], spec["sha256"])
            self.assertEqual(verification[name]["tensor_count"], spec["tensor_count"])
            self.assertEqual(verification[name]["missing_keys"], [])
            self.assertEqual(verification[name]["unexpected_keys"], [])

    def test_exact_initialization_reconstruction(self) -> None:
        rebuilt = json.loads((audit.OUT / "initialization_reconstruction.json").read_text(encoding="utf-8"))
        self.assertTrue(rebuilt["v55"]["serialized_exact"])
        self.assertTrue(rebuilt["v57"]["serialized_exact"])
        self.assertEqual(rebuilt["v55"]["rebuilt_sha256"], audit.STATE_SPECS["v55_initial"]["sha256"])
        self.assertEqual(rebuilt["v57"]["rebuilt_sha256"], audit.STATE_SPECS["v57_initial_equal"]["sha256"])
        self.assertTrue(rebuilt["initial_bbox_head_v55_v57_bit_identical"])

    def test_rng_trace_preserves_exact_construction(self) -> None:
        traces = json.loads((audit.OUT / "rng_construction_trace.json").read_text(encoding="utf-8"))
        v55_events = [item["event"] for item in traces["v55"]]
        v57_events = [item["event"] for item in traces["v57"]]
        for event in ("construction_start", "parent_multimodal_front_end", "detector_backbone_fpn_fcos",
                      "fcos_head", "fcos_regression_head", "construction_end"):
            self.assertIn(event, v55_events)
            self.assertIn(event, v57_events)
        self.assertIn("replacement_superset_front_end_and_scorer", v57_events)
        self.assertNotIn("replacement_superset_front_end_and_scorer", v55_events)

    def test_frozen_subsets_are_deterministic(self) -> None:
        train = MMUAVFeatureAlignmentDataset(audit.TRAIN_MANIFEST, 320, validate_paths=False)
        indices = torch.randperm(len(train), generator=torch.Generator(device="cpu").manual_seed(60))[:32].tolist()
        ids = [train.rows[index]["original_row_id"] for index in indices]
        payload = ("\n".join(ids) + "\n").encode()
        frozen = self.protocol["subsets"]
        self.assertEqual(indices, frozen["train_indices"])
        self.assertEqual(indices[:4], frozen["gradient_indices"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), frozen["train_sha256"])
        self.assertEqual(ids[:4], (audit.OUT / "gradient_probe_subset.txt").read_text().splitlines())
        self.assertEqual(frozen["devval_sha256"], audit.V59_SUBSET_SHA256)

    def test_historical_logs_are_complete_and_locked(self) -> None:
        schemas = json.loads((audit.OUT / "historical_log_schema.json").read_text(encoding="utf-8"))
        for name, expected in LOG_HASHES.items():
            self.assertEqual(audit.sha256(audit.LOG_SPECS[name]), expected)
            self.assertEqual(schemas[name]["sha256"], expected)
            self.assertEqual(schemas[name]["rows"], 7187)
            self.assertFalse(schemas[name]["bbox_gradient_field_present"])
            self.assertFalse(schemas[name]["bbox_output_field_present"])

    def test_torchvision_bbox_path_is_the_instrumented_path(self) -> None:
        regression = inspect.getsource(fcos_module.FCOSRegressionHead.forward)
        loss = inspect.getsource(fcos_module.FCOSHead.compute_loss)
        geometry = inspect.getsource(audit.geometry_forward)
        self.assertIn("functional.relu", regression)
        self.assertIn("generalized_box_iou_loss", loss)
        self.assertIn("box_coder.decode", geometry)
        self.assertIn("bbox_reg", geometry)
        self.assertIn("split(counts)", geometry)

    def test_no_optimizer_metric_repair_or_training_path(self) -> None:
        source = Path(audit.__file__).read_text(encoding="utf-8")
        self.assertNotIn("torch.optim", source)
        self.assertNotIn(".step(", source)
        self.assertNotIn("coco_detection_metrics", source)
        self.assertNotIn("from rarepdet.train_early_fusion", source)
        self.assertNotIn("import rarepdet.train_early_fusion", source)
        self.assertEqual(source.count("torch.save("), 1)
        self.assertEqual(self.protocol["optimizer_constructions"], 0)
        self.assertEqual(self.protocol["optimizer_steps"], 0)
        self.assertEqual(self.protocol["backward_limit"], 20)
        self.assertFalse(self.protocol["ap_ar_computed"])
        self.assertFalse(self.protocol["repair_authorized"])

    def test_source_and_protected_evidence_locks(self) -> None:
        self.assertEqual(audit.git("rev-parse", "HEAD"), audit.START_COMMIT)
        self.assertEqual(audit.source_lock()["source_hashes"], self.lock["source_hashes"])
        self.assertEqual(audit.aggregate_fingerprint(audit.protected_paths()), self.protocol["protected_baseline"])

    def test_cuda_results_respect_probe_limits_when_present(self) -> None:
        safety_path = audit.OUT / "safety_audit.json"
        if not safety_path.exists():
            self.skipTest("CUDA probe has not run yet")
        safety = json.loads(safety_path.read_text(encoding="utf-8"))
        self.assertEqual(safety["optimizer_constructions"], 0)
        self.assertEqual(safety["optimizer_steps"], 0)
        self.assertEqual(safety["backward_calls"], 20)
        self.assertTrue(safety["all_parameters_unchanged"])
        self.assertTrue(safety["all_checkpoints_unchanged"])
        self.assertTrue(safety["protected_fingerprint_unchanged"])
        gradients = json.loads((audit.OUT / "no_step_gradient_probe.json").read_text(encoding="utf-8"))
        self.assertEqual(sum(item["backward_calls"] for item in gradients.values()), 20)
        self.assertTrue(all(item["parameters_unchanged"] for item in gradients.values()))

    def test_only_compact_v60_artifacts_are_emitted(self) -> None:
        forbidden = {".pt", ".pth", ".pkl", ".pickle", ".npy", ".npz", ".png", ".jpg"}
        files = [path for path in audit.OUT.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertFalse([path for path in files if path.suffix.lower() in forbidden])
        self.assertLess(max(path.stat().st_size for path in files), 20 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
