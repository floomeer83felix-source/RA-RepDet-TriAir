"""CPU/source-lock tests for the V62 clean paired rerun."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import torch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.v57_fusion_superset_detector import V57FusionSupersetDetector
from rarepdet.tools import run_v62_mmuav_clean_bbox_bias_pilot as audit
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import target_to_device


class V62ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not audit.OUT.is_dir():
            raise unittest.SkipTest("run V62 --prepare-only first")
        cls.protocol = json.loads((audit.OUT / "protocol.json").read_text(encoding="utf-8"))
        cls.lock = json.loads((audit.OUT / "source_lock_v62.json").read_text(encoding="utf-8"))

    def test_v61_blocked_evidence_is_exact_and_immutable(self) -> None:
        self.assertTrue(all(audit.verify_v61()["checks"].values()))
        self.assertEqual(audit.verify_v61(), self.protocol["v61_verification"])
        self.assertEqual(audit.sha256(audit.V61_OUT / "per_variant_training_log.csv"), audit.V61_LOG_SHA256)

    def test_actual_failed_devval_row_trace_mover_is_exact(self) -> None:
        manifest = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"
        dataset = MMUAVFeatureAlignmentDataset(manifest, 320, validate_paths=False)
        index, sample = audit.actual_failed_devval_sample(dataset)
        self.assertEqual(sample["original_row_id"], audit.FAILED_ROW_ID)
        moved = audit.trace_target_to_device(sample, torch.device("cpu"))[0]
        self.assertTrue(torch.equal(moved["boxes"], sample["target_rgb"]["boxes"]))
        self.assertTrue(torch.equal(moved["labels"], sample["target_rgb"]["labels"]))
        self.assertEqual(moved["boxes"].dtype, sample["target_rgb"]["boxes"].dtype)
        self.assertEqual(moved["labels"].dtype, sample["target_rgb"]["labels"].dtype)
        self.assertGreaterEqual(index, 0)

    def test_historical_optimization_guard_still_rejects_devval(self) -> None:
        manifest = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"
        dataset = MMUAVFeatureAlignmentDataset(manifest, 320, validate_paths=False)
        _, sample = audit.actual_failed_devval_sample(dataset)
        with self.assertRaisesRegex(RuntimeError, "Invalid optimization sample"):
            target_to_device(sample, torch.device("cpu"))

    def test_complete_actual_train_and_devval_geometry_call_chain_cpu(self) -> None:
        train = MMUAVFeatureAlignmentDataset(audit.base.TRAIN_MANIFEST, 320, validate_paths=False)
        dev = MMUAVFeatureAlignmentDataset(
            ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt", 320,
            validate_paths=False)
        _, dev_sample = audit.actual_failed_devval_sample(dev)
        train_sample = train[self.protocol["subsets"]["train_indices"][0]]
        model = V57FusionSupersetDetector("alignment_on_equal_superset")
        model.load_state_dict(audit.base.load_common_state(), strict=True)
        model.eval()
        before = audit.base.parameter_hash(model)
        with patch("torch.optim.AdamW", side_effect=AssertionError("geometry trace constructed optimizer")):
            with torch.no_grad():
                train_result = audit.geometry_row(model, train_sample, torch.device("cpu"))
                dev_result = audit.geometry_row(model, dev_sample, torch.device("cpu"))
        self.assertEqual(train_result["split"], "train")
        self.assertEqual(dev_result["row_id"], audit.FAILED_ROW_ID)
        self.assertEqual(dev_result["split"], "devval")
        self.assertEqual(len(train_result["levels"]), 4)
        self.assertEqual(len(dev_result["levels"]), 4)
        self.assertEqual(audit.base.parameter_hash(model), before)

    def test_atomic_recovery_round_trip_with_model_optimizer_rng_and_log(self) -> None:
        model = torch.nn.Linear(3, 2)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
        loss = model(torch.ones(1, 3)).sum(); loss.backward(); optimizer.step()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log_path = root / "log.csv"
            with log_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle); writer.writerow(["step"]); writer.writerow([1])
                info = audit.log_contract(handle, log_path)
                result = audit.atomic_recovery_snapshot(
                    model, optimizer, 1, 1, audit.VARIANTS[0], log_path, info,
                    [{"event": "trace_complete", "trace_step": 0}], root / "latest.pt")
            self.assertTrue(all(result["round_trip_checks"].values()))
            self.assertEqual(result["log_row_count"], 1)
            self.assertTrue((root / "latest.pt").is_file())
            self.assertFalse((root / "latest.pt.tmp").exists())

    def test_data_order_subsets_initialization_and_intervention(self) -> None:
        self.assertEqual(audit.sha256(audit.base.TRAIN_MANIFEST), audit.base.TRAIN_SHA256)
        self.assertEqual(audit.sha256(audit.base.ORDER_PATH), audit.base.ORDER_SHA256)
        self.assertEqual(audit.sha256(audit.base.COMMON_INIT), audit.base.INIT_SHA256)
        self.assertTrue(all(self.protocol["subsets"]["checks"].values()))
        full = json.loads(audit.base.ORDER_INDICES_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.protocol["prefix"]["indices"], full[:500])
        delta = self.protocol["intervention"]
        self.assertEqual(delta["changed_tensor_count"], 1)
        self.assertEqual(delta["changed_element_count"], 4)
        self.assertTrue(delta["all_other_tensors_bit_identical"])

    def test_fixed_pair_budgets_trace_schedule_and_no_metric_path(self) -> None:
        self.assertEqual(self.protocol["run_order"], list(audit.VARIANTS))
        self.assertEqual(self.protocol["steps_per_variant"], 500)
        self.assertEqual(self.protocol["optimizer_step_limit"], 1000)
        self.assertEqual(self.protocol["probe_backward_limit"], 96)
        self.assertEqual(list(audit.base.TRACE_STEPS), [0, 1, 2, 5, 10, 20, 50, 100, 200, 300, 400, 500])
        source = Path(audit.__file__).read_text(encoding="utf-8")
        self.assertNotIn("coco_detection_metrics", source)
        self.assertNotIn("score_thresh", source)
        self.assertNotIn("detections_per_img", source)

    def test_source_and_protected_locks(self) -> None:
        self.assertEqual(audit.git("rev-parse", "HEAD"), audit.START_COMMIT)
        self.assertEqual(audit.source_lock()["source_hashes"], self.lock["source_hashes"])
        self.assertEqual(audit._aggregate(audit.protected_paths()), self.protocol["protected_baseline"])

    def test_cuda_outputs_when_present(self) -> None:
        path = audit.OUT / "safety_audit.json"
        if not path.exists():
            self.skipTest("CUDA run not complete")
        safety = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(safety["optimizer_steps"], 1000)
        self.assertEqual(safety["probe_backward_calls"], 96)
        self.assertEqual(safety["verified_recovery_snapshots"], 24)
        self.assertTrue(safety["all_recovery_round_trips"])
        self.assertTrue(safety["all_trace_isolation_checks"])
        self.assertTrue(safety["v61_evidence_unchanged"])
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
