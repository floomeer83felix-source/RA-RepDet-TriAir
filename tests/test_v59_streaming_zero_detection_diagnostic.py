import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import unittest

import torch
from torchvision.models.detection.fcos import FCOS

from rarepdet.tools.run_v59_streaming_zero_detection_diagnostic import (
    DEVVAL_MANIFEST,
    DEVVAL_SHA256,
    EXPECTED_TENSORS,
    LADDER,
    ORDER_SHA256,
    OUT,
    RUN_ORDER,
    START_COMMIT,
    SUBSET_SHA256,
    V55_REFERENCE,
    V57_CHECKPOINTS,
    aggregate_file_fingerprint,
    protected_paths,
    sha256,
)
from rarepdet.tools.v59_streaming_histogram import (
    BIN_COUNT,
    LOGIT_WIDTH,
    StreamingHistogram,
    validate_histogram_implementation,
)


ROOT = Path(__file__).resolve().parents[1]


class V59StreamingDiagnosticTests(unittest.TestCase):
    def test_v58_blocker_is_exact(self):
        verification = json.loads((OUT / "v58_blocker_verification.json").read_text())
        self.assertTrue(all(verification["checks"].values()))
        error = (ROOT / "runs/v58_mmuav_zero_detection_diagnostic/blocker_error_tail.txt").read_text()
        self.assertIn("RuntimeError: quantile() input tensor is too large", error)

    def test_frozen_devval_order_and_subset(self):
        self.assertEqual(sha256(DEVVAL_MANIFEST), DEVVAL_SHA256)
        self.assertEqual(sha256(OUT / "devval_order.txt"), ORDER_SHA256)
        self.assertEqual(len((OUT / "devval_order.txt").read_text().splitlines()), 1845)
        indices = json.loads((OUT / "detailed_subset_indices.json").read_text())
        payload = (json.dumps(indices, separators=(",", ":")) + "\n").encode()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), SUBSET_SHA256)
        self.assertEqual(len(indices), 32)
        self.assertEqual(len(set(indices)), 32)

    def test_required_checkpoint_contracts(self):
        verification = json.loads((OUT / "checkpoint_verification.json").read_text())
        specs = {**V57_CHECKPOINTS, "v55_reference": V55_REFERENCE}
        for name in RUN_ORDER:
            self.assertTrue(verification[name]["available"])
            self.assertEqual(verification[name]["state_tensor_count"], EXPECTED_TENSORS[name])
            self.assertEqual(sha256(specs[name]["path"]), specs[name]["sha256"])
            self.assertEqual(verification[name]["missing_keys"], [])
            self.assertEqual(verification[name]["unexpected_keys"], [])
            self.assertEqual(verification[name]["shape_mismatch_keys"], [])
            self.assertTrue(verification[name]["all_tensors_finite"])

    def test_histogram_specification_is_frozen(self):
        spec = json.loads((OUT / "histogram_specification.json").read_text())
        self.assertTrue(spec["frozen_before_inference"])
        self.assertEqual(spec["logit"]["bins"], BIN_COUNT)
        self.assertEqual(spec["logit"]["range"], [-64.0, 64.0])
        self.assertEqual(spec["logit"]["bin_width"], LOGIT_WIDTH)
        self.assertEqual(spec["probability_and_combined"]["range"], [1e-12, 1.0])
        self.assertFalse(spec["all_row_tensor_concatenation"])
        self.assertFalse(spec["all_value_exact_quantiles"])

    def test_synthetic_histogram_validation(self):
        result = validate_histogram_implementation()
        self.assertTrue(result["passed"])
        self.assertTrue(result["chunk_and_update_order_histogram_counts_identical"])
        for case in result["cases"].values():
            self.assertTrue(all(case["checks"].values()))
            self.assertTrue(all(case["quantile_containment"].values()))

    def test_histogram_storage_is_bounded(self):
        histogram = StreamingHistogram("probability")
        histogram.update(torch.linspace(0, 1, 1_000_000))
        self.assertEqual(histogram.counts.dtype, torch.int64)
        self.assertEqual(histogram.counts.device.type, "cpu")
        self.assertEqual(histogram.counts.numel(), BIN_COUNT)
        self.assertLess(histogram.retained_bytes, 140_000)

    def test_actual_fcos_score_path(self):
        source = inspect.getsource(FCOS.postprocess_detections)
        for fragment in ("torch.sqrt", "torch.sigmoid", "> self.score_thresh", "topk", "batched_nms"):
            self.assertIn(fragment, source)

    def test_no_training_or_unbounded_retention_path(self):
        runner = (ROOT / "rarepdet/tools/run_v59_streaming_zero_detection_diagnostic.py").read_text()
        self.assertNotIn("torch.optim", runner)
        self.assertNotIn(".backward(", runner)
        self.assertNotIn(".train(", runner)
        self.assertNotIn("coco_detection_metrics", runner)
        self.assertNotIn("level_values", runner)
        self.assertNotIn("aggregate_predictions", runner)
        self.assertIn("Compact-array bound exceeded", runner)

    def test_pass_order_and_zero_training_contract(self):
        protocol = json.loads((OUT / "protocol.json").read_text())
        ledger = json.loads((OUT / "pass_ledger.json").read_text())
        self.assertEqual(protocol["run_order"], list(RUN_ORDER))
        self.assertEqual(protocol["passes_per_checkpoint"], 1)
        self.assertEqual(tuple(protocol["threshold_ladder"]), LADDER)
        self.assertEqual(protocol["optimizer_steps"], 0)
        self.assertEqual(protocol["backward_passes"], 0)
        self.assertEqual(protocol["training_mode_executions"], 0)
        self.assertFalse(protocol["alternate_threshold_ap_ar_computed"])
        self.assertEqual(ledger["order"], list(RUN_ORDER))
        self.assertTrue(all(ledger["passes"][name]["attempts_started"] <= 1 for name in RUN_ORDER))

    def test_source_lock_matches(self):
        lock = json.loads((OUT / "source_lock_v59.json").read_text())
        self.assertEqual(lock["starting_commit"], START_COMMIT)
        for relative, expected in lock["source_hashes"].items():
            self.assertEqual(sha256(ROOT / relative), expected)

    def test_protected_baseline_matches(self):
        protocol = json.loads((OUT / "protocol.json").read_text())
        self.assertEqual(aggregate_file_fingerprint(protected_paths()), protocol["protected_baseline"])

    def test_no_heavy_artifacts(self):
        forbidden = {".pt", ".pth", ".npy", ".npz", ".png", ".jpg", ".jpeg", ".pkl", ".pickle"}
        self.assertEqual([path for path in OUT.rglob("*") if path.is_file() and path.suffix.lower() in forbidden], [])
        self.assertTrue(all(path.stat().st_size < 50 * 1024 * 1024 for path in OUT.rglob("*") if path.is_file()))

    def test_v58_evidence_has_no_worktree_diff(self):
        result = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", "runs/v58_mmuav_zero_detection_diagnostic"],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
