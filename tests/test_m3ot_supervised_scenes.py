"""Selection must cover both groups and never consume predictions."""

import unittest

from tools.select_m3ot_supervised_scenes import select


class SceneSelectionTests(unittest.TestCase):
    def test_group_coverage_and_dense_scene(self):
        records = []
        for group, counts in (("1", (1, 2, 3)), ("2", (2, 3, 8))):
            for index, count in enumerate(counts):
                records.append({"group": group, "sample_id": f"{group}/val/{index}",
                                "boxes_xywh": [[0, 0, 1, 1]] * count})
        chosen = select(records)
        self.assertEqual(chosen["group1_typical"]["group"], "1")
        self.assertEqual(chosen["group2_typical"]["group"], "2")
        self.assertEqual(chosen["dense"]["gt_boxes"], 8)
        self.assertEqual(len({row["sample_id"] for row in chosen.values()}), 3)


if __name__ == "__main__":
    unittest.main()
