import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runs/v51_visdrone_recovery"


class V51RecoveryTests(unittest.TestCase):
    def test_route_b_is_frozen_before_training(self):
        decision = json.loads((OUTPUT / "route_decision.json").read_text(encoding="utf-8"))
        status = json.loads((OUTPUT / "cv_run_status.json").read_text(encoding="utf-8"))
        self.assertEqual(decision["selected_route"], "B_GROUP_DISJOINT_CROSS_VALIDATION")
        self.assertTrue(decision["blind_or_independent_test_claim_abandoned"])
        self.assertEqual(status["state"], "AWAITING_GPU_AUTHORIZATION")

    def test_fold_groups_are_disjoint_and_cover_all_images(self):
        manifest = json.loads((OUTPUT / "fold_manifest.json").read_text(encoding="utf-8"))
        validation_entries = []
        validation_groups = []
        for fold in range(3):
            train = [
                item for item in (OUTPUT / f"folds/fold_{fold}_train.txt").read_text(encoding="utf-8").splitlines()
                if item
            ]
            val = [
                item for item in (OUTPUT / f"folds/fold_{fold}_val.txt").read_text(encoding="utf-8").splitlines()
                if item
            ]
            train_groups = {Path(item).stem.split("_")[0] for item in train}
            val_groups = {Path(item).stem.split("_")[0] for item in val}
            self.assertFalse(train_groups & val_groups)
            self.assertEqual(len(train) + len(val), manifest["source_entries"])
            validation_entries.extend(val)
            validation_groups.extend(val_groups)
        self.assertEqual(len(validation_entries), len(set(validation_entries)))
        self.assertEqual(len(validation_entries), manifest["source_entries"])
        self.assertEqual(len(validation_groups), len(set(validation_groups)))

    def test_fold_annotations_match_manifests(self):
        for fold in range(3):
            for role in ("train", "val"):
                manifest_entries = {
                    item
                    for item in (OUTPUT / f"folds/fold_{fold}_{role}.txt").read_text(encoding="utf-8").splitlines()
                    if item
                }
                coco = json.loads(
                    (OUTPUT / f"converted_annotations/fold_{fold}_{role}.json").read_text(encoding="utf-8")
                )
                image_entries = {item["file_name"] for item in coco["images"]}
                self.assertEqual(manifest_entries, image_entries)
                image_ids = {int(item["id"]) for item in coco["images"]}
                self.assertTrue(
                    all(int(annotation["image_id"]) in image_ids for annotation in coco["annotations"])
                )

    def test_gpu_queue_requires_explicit_authorization(self):
        process = subprocess.run(
            [sys.executable, "rarepdet/tools/run_v51_cv_queue.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("explicit --confirm-gpu-authorized is required", process.stderr)


if __name__ == "__main__":
    unittest.main()
