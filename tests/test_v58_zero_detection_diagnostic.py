import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import unittest

from torchvision.models.detection.fcos import FCOS

from rarepdet.tools.run_v58_zero_detection_diagnostic import (
    DEVVAL_MANIFEST,
    LADDER,
    OUT,
    QUANTILES,
    START_COMMIT,
    V55_REFERENCE,
    V57_CHECKPOINTS,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]


class V58ZeroDetectionDiagnosticTests(unittest.TestCase):
    def test_devval_contract(self):
        self.assertEqual(sha256(DEVVAL_MANIFEST), "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54")
        self.assertEqual(len((OUT / "devval_order.txt").read_text().splitlines()), 1845)
        self.assertEqual(sha256(OUT / "devval_order.txt"), (OUT / "devval_order_sha256.txt").read_text().strip())

    def test_required_checkpoint_hashes_and_state_coverage(self):
        verification = json.loads((OUT / "checkpoint_verification.json").read_text())
        for name, spec in V57_CHECKPOINTS.items():
            self.assertTrue(verification[name]["available"])
            self.assertEqual(sha256(spec["path"]), spec["sha256"])
            self.assertEqual(verification[name]["missing_keys"], [])
            self.assertEqual(verification[name]["unexpected_keys"], [])
            self.assertEqual(verification[name]["shape_mismatch_keys"], [])
            self.assertTrue(verification[name]["all_tensors_finite"])

    def test_optional_v55_is_truthfully_recorded(self):
        availability = json.loads((OUT / "v55_reference_availability.json").read_text())
        if V55_REFERENCE["path"].is_file() and sha256(V55_REFERENCE["path"]) == V55_REFERENCE["sha256"]:
            self.assertTrue(availability["available"])
        else:
            self.assertFalse(availability["available"])

    def test_subset_is_deterministic_and_frozen(self):
        indices = json.loads((OUT / "detailed_subset_indices.json").read_text())
        self.assertEqual(len(indices), 32)
        self.assertEqual(len(set(indices)), 32)
        self.assertTrue(all(0 <= value < 1845 for value in indices))
        payload = (json.dumps(indices, separators=(",", ":")) + "\n").encode()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), (OUT / "detailed_subset_sha256.txt").read_text().strip())

    def test_actual_fcos_score_path(self):
        source = inspect.getsource(FCOS.postprocess_detections)
        for fragment in ("torch.sqrt", "torch.sigmoid", "> self.score_thresh", "topk", "batched_nms"):
            self.assertIn(fragment, source)

    def test_fixed_ladder_and_no_alternate_metrics(self):
        protocol = json.loads((OUT / "protocol.json").read_text())
        self.assertEqual(tuple(protocol["threshold_ladder_frozen_before_inference"]), LADDER)
        self.assertEqual(tuple(protocol["quantiles"]), QUANTILES)
        self.assertFalse(protocol["alternate_threshold_ap_ar_computed"])

    def test_zero_training_boundary_in_source(self):
        source = (ROOT / "rarepdet/tools/run_v58_zero_detection_diagnostic.py").read_text()
        self.assertNotIn("torch.optim", source)
        self.assertNotIn(".backward(", source)
        self.assertNotIn(".train(", source)
        self.assertNotIn("coco_detection_metrics", source)
        protocol = json.loads((OUT / "protocol.json").read_text())
        self.assertEqual(protocol["optimizer_steps"], 0)
        self.assertEqual(protocol["backward_passes"], 0)

    def test_required_outputs_are_compact_and_no_heavy_artifacts(self):
        self.assertEqual(list(OUT.rglob("*.pt")), [])
        self.assertEqual(list(OUT.rglob("*.npy")), [])
        self.assertEqual(list(OUT.rglob("*.png")), [])
        self.assertTrue(all(path.stat().st_size < 50 * 1024 * 1024 for path in OUT.rglob("*") if path.is_file()))

    def test_protected_paths_unchanged(self):
        changed = subprocess.check_output(["git", "diff", "--name-only", START_COMMIT], cwd=ROOT, text=True).splitlines()
        forbidden = [path for path in changed if (path.startswith("runs/v5") and not path.startswith(
            "runs/v58_mmuav_zero_detection_diagnostic/")) or path.startswith("manuscript/") or
            path.startswith("submission/") or path in {"datasets/triair_dataset.py", "rarepdet/train_early_fusion.py",
            "rarepdet/models/early_fusion_fcos.py", "rarepdet/models/reliability_fusion_fcos.py",
            "main.tex", "main_sivp_snjnl.tex"}]
        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
