"""Minimal three-branch V53 model scaffold; intentionally outside production builders."""

from __future__ import annotations

import torch
from torch import nn

from rarepdet.experimental.mmuav_feature_alignment import (
    EqualFeatureFusion,
    ReliabilityAwareFeatureFusion,
    ResidualAffineFeatureAligner,
)


def _stem(in_channels: int, feature_channels: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv2d(in_channels, feature_channels // 2, 3, stride=2, padding=1, bias=False),
        nn.GroupNorm(4, feature_channels // 2),
        nn.ReLU(inplace=True),
        nn.Conv2d(feature_channels // 2, feature_channels, 3, stride=2, padding=1, bias=False),
        nn.GroupNorm(4, feature_channels),
        nn.ReLU(inplace=True),
    )


class MMUAVFeatureAlignmentScaffold(nn.Module):
    """Returns detector-ready fused features without implementing or invoking a detector."""

    def __init__(self, feature_channels: int = 32, alignment_enabled: bool = True,
                 fusion_mode: str = "equal") -> None:
        super().__init__()
        if feature_channels % 8:
            raise ValueError("feature_channels must be divisible by 8")
        if fusion_mode not in {"equal", "reliability"}:
            raise ValueError("fusion_mode must be 'equal' or 'reliability'")
        self.alignment_enabled = alignment_enabled
        self.fusion_mode = fusion_mode
        self.rgb_stem = _stem(3, feature_channels)
        self.ir_stem = _stem(1, feature_channels)
        self.event_stem = _stem(1, feature_channels)
        self.ir_aligner = ResidualAffineFeatureAligner(feature_channels)
        self.event_aligner = ResidualAffineFeatureAligner(feature_channels)
        self.fusion = EqualFeatureFusion() if fusion_mode == "equal" else ReliabilityAwareFeatureFusion(feature_channels)

    def forward(self, rgb: torch.Tensor, ir: torch.Tensor, event: torch.Tensor) -> dict[str, torch.Tensor]:
        rgb_features = self.rgb_stem(rgb)
        ir_features = self.ir_stem(ir)
        event_features = self.event_stem(event)
        aligned_ir, ir_theta = self.ir_aligner(ir_features, rgb_features, self.alignment_enabled)
        aligned_event, event_theta = self.event_aligner(event_features, rgb_features, self.alignment_enabled)
        fused, weights = self.fusion(rgb_features, aligned_ir, aligned_event)
        return {
            "rgb_reference": rgb_features,
            "aligned_ir": aligned_ir,
            "aligned_event": aligned_event,
            "fused": fused,
            "fusion_weights": weights,
            "ir_theta": ir_theta,
            "event_theta": event_theta,
        }
