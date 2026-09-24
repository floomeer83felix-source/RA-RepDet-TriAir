"""CPU-only M3OT supervised manifest contract checks."""

import unittest

from tools.audit_m3ot_supervised import validate_manifest_records


def row(split, frame, boxes=None):
    return {"split": split, "sample_id": f"1/{split}/1-01/{frame}",
            "group": "1", "sequence": "1-01", "frame": frame,
            "width": 640, "height": 512,
            "boxes_xywh": boxes or [[1, 2, 3, 4]]}


class AuditContractTests(unittest.TestCase):
    def test_disjoint_valid_splits(self):
        report = validate_manifest_records([row("train", "000001")], [row("val", "000002")])
        self.assertEqual(report["cross_split_frame_overlap"], 0)

    def test_shared_frame_rejected_even_when_split_string_differs(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            validate_manifest_records([row("train", "000001")], [row("val", "000001")])

    def test_out_of_bounds_box_rejected(self):
        with self.assertRaisesRegex(ValueError, "Out-of-bounds"):
            validate_manifest_records([row("train", "000001", [[639, 5, 2, 1]])], [])


if __name__ == "__main__":
    unittest.main()
