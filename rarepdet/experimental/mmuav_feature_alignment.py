"""STN-inspired residual affine feature alignment for private V53 preflight."""

from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class ResidualAffineFeatureAligner(nn.Module):
    """Warp source features toward an RGB reference grid using a learned affine residual."""

    def __init__(self, channels: int, hidden_channels: int = 32) -> None:
        super().__init__()
        self.localization = nn.Sequential(
            nn.Conv2d(channels * 2, hidden_channels, 3, padding=1, bias=False),
            nn.GroupNorm(4, hidden_channels),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.affine_residual = nn.Linear(hidden_channels, 6)
        nn.init.zeros_(self.affine_residual.weight)
        nn.init.zeros_(self.affine_residual.bias)
        self.register_buffer("identity_theta", torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]))

    def forward(self, source: torch.Tensor, reference: torch.Tensor,
                alignment_enabled: bool = True) -> tuple[torch.Tensor, torch.Tensor]:
        source = F.interpolate(source, size=reference.shape[-2:], mode="bilinear", align_corners=False)
        batch = source.shape[0]
        identity = self.identity_theta.unsqueeze(0).expand(batch, -1, -1)
        if not alignment_enabled:
            return source, identity
        residual = self.affine_residual(self.localization(torch.cat((reference, source), dim=1)).flatten(1))
        theta = identity + residual.view(-1, 2, 3)
        grid = F.affine_grid(theta, source.shape, align_corners=False)
        return F.grid_sample(source, grid, mode="bilinear", padding_mode="border", align_corners=False), theta


class EqualFeatureFusion(nn.Module):
    def forward(self, rgb: torch.Tensor, ir: torch.Tensor, event: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        weights = rgb.new_full((rgb.shape[0], 3), 1.0 / 3.0)
        return (rgb + ir + event) / 3.0, weights


class ReliabilityAwareFeatureFusion(nn.Module):
    def __init__(self, channels: int, hidden_channels: int = 32) -> None:
        super().__init__()
        self.score = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(channels, hidden_channels),
                                   nn.ReLU(inplace=True), nn.Linear(hidden_channels, 1))

    def forward(self, rgb: torch.Tensor, ir: torch.Tensor, event: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        features = (rgb, ir, event)
        weights = torch.softmax(torch.cat([self.score(feature) for feature in features], dim=1), dim=1)
        fused = sum(feature * weights[:, index, None, None, None] for index, feature in enumerate(features))
        return fused, weights
