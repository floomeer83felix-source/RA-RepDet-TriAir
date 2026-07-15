import csv
import inspect
import json
from pathlib import Path
import unittest

import torch

from datasets.mmuav_feature_alignment_dataset import (
    MMUAVFeatureAlignmentDataset,
    transform_rgb_boxes,
)
from rarepdet.experimental.mmuav_feature_alignment import ResidualAffineFeatureAligner
from rarepdet.experimental.mmuav_feature_alignment_model import MMUAVFeatureAlignmentScaffold


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs/v53_mmuav_feature_alignment_preflight"
V52 = ROOT / "runs/v52_mmuav_audit"


def read_manifest(split):
    with (OUT / f"manifests/{split}_rgb_supervised.txt").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class V53MMUAVFeatureAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = read_manifest("train")
        cls.devval = read_manifest("devval")

    def test_exact_rgb_supervised_contract_and_exclusions(self):
        contract = json.loads((OUT / "rgb_target_contract.json").read_text(encoding="utf-8"))
        self.assertEqual((len(self.train), len(self.devval)), (7187, 1845))
        self.assertEqual(contract["counts"]["total"], 9032)
        self.assertEqual(contract["ir_only_excluded"], 106)
        self.assertEqual(contract["unlabeled_excluded"], 35898)
        self.assertTrue(all(int(row["rgb_annotation_rows"]) > 0 for row in self.train + self.devval))
        self.assertTrue(all(row["supervision_state"] == "RGB_SOURCE_GT_PRESENT" for row in self.train + self.devval))

    def test_sequence_split_and_original_row_traceability(self):
        self.assertFalse({row["sequence"] for row in self.train} & {row["sequence"] for row in self.devval})
        source_ids = set()
        for split in ("train", "devval"):
            with (V52 / f"manifests/{split}_sampled.txt").open(encoding="utf-8", newline="") as handle:
                source_ids.update(f"{split}:{index:08d}" for index, _ in enumerate(csv.DictReader(handle, delimiter="\t"), 1))
        manifest_ids = {row["original_row_id"] for row in self.train + self.devval}
        self.assertEqual(len(manifest_ids), 9032)
        self.assertTrue(manifest_ids <= source_ids)

    def test_all_paths_and_synchronized_frame_ids(self):
        for row in self.train + self.devval:
            frame = int(row["frame_index"])
            for key in ("rgb", "ir", "event", "gt_rgb"):
                self.assertTrue(Path(row[key]).is_file(), (row["original_row_id"], key))
            self.assertEqual({int(Path(row[key]).stem) for key in ("rgb", "ir", "event")}, {frame})

    def test_adapter_metadata_and_rgb_only_box_transform(self):
        dataset = MMUAVFeatureAlignmentDataset(OUT / "manifests/train_rgb_supervised.txt", branch_size=128,
                                               validate_paths=False)
        sample = dataset[0]
        self.assertEqual(set(sample["modality_native_shapes"]), {"rgb", "ir", "event"})
        self.assertEqual(sample["modality_native_shapes"], {"rgb": (360, 640), "ir": (512, 640), "event": (260, 346)})
        transforms = sample["modality_transforms"]
        self.assertNotEqual(transforms["rgb"], transforms["ir"])
        box = torch.tensor([[10.0, 20.0, 30.0, 40.0]])
        expected = transform_rgb_boxes(box, transforms["rgb"])
        self.assertFalse(torch.equal(expected, transform_rgb_boxes(box, transforms["ir"])))
        self.assertEqual(sample["target_rgb"]["boxes"].shape[1], 4)
        self.assertEqual(tuple(sample["rgb"].shape), (3, 128, 128))
        self.assertEqual(tuple(sample["ir"].shape), (1, 128, 128))
        self.assertEqual(tuple(sample["event"].shape), (1, 128, 128))

    def test_three_independent_branches_and_no_raw_concat_interface(self):
        model = MMUAVFeatureAlignmentScaffold(32)
        self.assertIsNot(model.rgb_stem, model.ir_stem)
        self.assertIsNot(model.ir_stem, model.event_stem)
        self.assertEqual(model.rgb_stem[0].in_channels, 3)
        self.assertEqual(model.ir_stem[0].in_channels, 1)
        self.assertEqual(model.event_stem[0].in_channels, 1)
        signature = inspect.signature(model.forward)
        self.assertEqual(list(signature.parameters), ["rgb", "ir", "event"])
        source = inspect.getsource(MMUAVFeatureAlignmentScaffold.forward)
        self.assertNotIn("torch.cat", source)

    def test_alignment_switch_identity_and_finite_cpu_forward(self):
        inputs = (torch.randn(1, 3, 64, 64), torch.randn(1, 1, 64, 64), torch.randn(1, 1, 64, 64))
        identity = torch.tensor([[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]])
        for enabled in (False, True):
            model = MMUAVFeatureAlignmentScaffold(32, alignment_enabled=enabled)
            output = model(*inputs)
            self.assertEqual(output["fused"].shape, (1, 32, 16, 16))
            self.assertTrue(torch.isfinite(output["fused"]).all())
            self.assertTrue(torch.equal(output["ir_theta"], identity))
            self.assertTrue(torch.equal(output["event_theta"], identity))

    def test_enabled_alignment_has_finite_gradients(self):
        model = MMUAVFeatureAlignmentScaffold(32, alignment_enabled=True, fusion_mode="reliability")
        inputs = (torch.randn(2, 3, 64, 64), torch.randn(2, 1, 64, 64), torch.randn(2, 1, 64, 64))
        model(*inputs)["fused"].square().mean().backward()
        gradients = [parameter.grad for name, parameter in model.named_parameters() if "aligner" in name]
        self.assertTrue(gradients)
        self.assertTrue(all(gradient is not None and torch.isfinite(gradient).all() for gradient in gradients))

    def test_no_devval_fitting_cuda_or_gpu_steps(self):
        files = [ROOT / "datasets/mmuav_feature_alignment_dataset.py",
                 ROOT / "rarepdet/experimental/mmuav_feature_alignment.py",
                 ROOT / "rarepdet/experimental/mmuav_feature_alignment_model.py"]
        source = "\n".join(path.read_text(encoding="utf-8") for path in files)
        self.assertNotIn("torch.cuda", source)
        self.assertNotIn(".cuda(", source)
        method = json.loads((OUT / "method_contract.json").read_text(encoding="utf-8"))
        gate = json.loads((OUT / "pilot_gate.json").read_text(encoding="utf-8"))
        self.assertFalse(method["devval_gt_fitting"])
        self.assertTrue(gate["locked"])
        self.assertEqual(gate["gpu_optimizer_steps"], 0)

    def test_source_lock_protects_history_and_manuscript(self):
        lock = json.loads((OUT / "source_lock_v53.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["protected_core_changed"], [])
        self.assertEqual(lock["v52_evidence_changed"], [])
        self.assertEqual(lock["manuscript_changed"], [])
        self.assertEqual(len(lock["source_hashes"]), 7)
        self.assertTrue(all(len(value) == 64 for value in lock["source_hashes"].values()))


if __name__ == "__main__":
    unittest.main()
