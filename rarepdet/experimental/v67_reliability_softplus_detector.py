"""V67-only active reliability-fusion detector with the frozen Softplus head."""

from __future__ import annotations

from types import MethodType

from rarepdet.experimental.v57_fusion_superset_detector import V57FusionSupersetDetector
from rarepdet.experimental.v63_bbox_activation_detector import _softplus_regression_forward


class V67ReliabilitySoftplusDetector(V57FusionSupersetDetector):
    """Activate the existing V57 scorer and retain the exact V63 Softplus head."""

    def __init__(self) -> None:
        super().__init__("alignment_on_reliability_superset")
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
