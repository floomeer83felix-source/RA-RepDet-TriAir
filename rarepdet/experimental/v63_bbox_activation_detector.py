"""V63-only FCOS bbox-distance activation intervention."""

from __future__ import annotations

from types import MethodType
from typing import List, Tuple

import torch
from torch import Tensor, nn
import torch.nn.functional as F

from rarepdet.experimental.v57_fusion_superset_detector import V57FusionSupersetDetector


ACTIVATIONS = ("relu", "softplus_b1_t20")


def _softplus_regression_forward(self: nn.Module, x: List[Tensor]) -> Tuple[Tensor, Tensor]:
    all_bbox_regression = []
    all_bbox_ctrness = []
    for features in x:
        bbox_feature = self.conv(features)
        pre_activation = self.bbox_reg(bbox_feature)
        bbox_regression = F.softplus(pre_activation, beta=1.0, threshold=20.0)
        self._v63_activation_applications += 1
        bbox_ctrness = self.bbox_ctrness(bbox_feature)
        n, _, height, width = bbox_regression.shape
        bbox_regression = bbox_regression.view(n, -1, 4, height, width)
        bbox_regression = bbox_regression.permute(0, 3, 4, 1, 2).reshape(n, -1, 4)
        bbox_ctrness = bbox_ctrness.view(n, -1, 1, height, width)
        bbox_ctrness = bbox_ctrness.permute(0, 3, 4, 1, 2).reshape(n, -1, 1)
        all_bbox_regression.append(bbox_regression)
        all_bbox_ctrness.append(bbox_ctrness)
    self._v63_forward_calls += 1
    return torch.cat(all_bbox_regression, dim=1), torch.cat(all_bbox_ctrness, dim=1)


class V63BBoxActivationDetector(V57FusionSupersetDetector):
    """Keep the V57 state contract while changing only bbox-distance activation."""

    def __init__(self, activation: str) -> None:
        if activation not in ACTIVATIONS:
            raise ValueError(f"Unknown V63 bbox activation: {activation}")
        super().__init__("alignment_on_equal_superset")
        self.bbox_activation = activation
        regression_head = self.detector.head.regression_head
        regression_head._v63_forward_calls = 0
        regression_head._v63_activation_applications = 0
        if activation == "softplus_b1_t20":
            regression_head.forward = MethodType(_softplus_regression_forward, regression_head)

    def activation_counts(self) -> dict[str, int]:
        head = self.detector.head.regression_head
        return {
            "forward_calls": int(head._v63_forward_calls),
            "activation_applications": int(head._v63_activation_applications),
        }

