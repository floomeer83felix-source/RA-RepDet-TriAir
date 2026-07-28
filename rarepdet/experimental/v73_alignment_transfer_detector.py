"""V73-only 640px alignment-aware transfer detector."""

from __future__ import annotations

from types import MethodType

from rarepdet.experimental.v57_fusion_superset_detector import V57FusionSupersetDetector
from rarepdet.experimental.v63_bbox_activation_detector import _softplus_regression_forward


FUSION_VARIANTS = {
    "equal": "alignment_on_equal_superset",
    "reliability": "alignment_on_reliability_superset",
}


class V73AlignmentTransferDetector(V57FusionSupersetDetector):
    """Expose the frozen V57 alignment contract at 640px with Softplus boxes."""

    def __init__(self, fusion_mode: str) -> None:
        if fusion_mode not in FUSION_VARIANTS:
            raise ValueError(f"Unknown V73 fusion mode: {fusion_mode}")
        super().__init__(FUSION_VARIANTS[fusion_mode], image_size=640, fpn_out_channels=128)
        self.fusion_mode = fusion_mode
        self.bbox_activation = "softplus_b1_t20"
        regression_head = self.detector.head.regression_head
        regression_head._v63_forward_calls = 0
        regression_head._v63_activation_applications = 0
        regression_head.forward = MethodType(_softplus_regression_forward, regression_head)

    def activation_counts(self) -> dict[str, int]:
        head = self.detector.head.regression_head
        return {
            "forward_calls": int(head._v63_forward_calls),
            "activation_applications": int(head._v63_activation_applications),
        }
