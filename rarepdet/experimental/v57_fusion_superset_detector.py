"""V57-only alignment-on fusion superset for a controlled paired ablation."""

from __future__ import annotations

import torch
from torch import nn

from rarepdet.experimental.mmuav_feature_alignment import ResidualAffineFeatureAligner
from rarepdet.experimental.mmuav_feature_alignment_detector import MMUAVFeatureAlignmentDetector
from rarepdet.experimental.mmuav_feature_alignment_model import _stem


VARIANTS = ("alignment_on_equal_superset", "alignment_on_reliability_superset")


class V57FusionSupersetScaffold(nn.Module):
    """Identical parameter superset with only fusion behavior switched."""

    def __init__(self, variant: str, feature_channels: int = 32, hidden_channels: int = 32) -> None:
        super().__init__()
        if variant not in VARIANTS:
            raise ValueError(f"Unknown V57 variant: {variant}")
        self.variant = variant
        self.alignment_enabled = True
        self.rgb_stem = _stem(3, feature_channels)
        self.ir_stem = _stem(1, feature_channels)
        self.event_stem = _stem(1, feature_channels)
        self.ir_aligner = ResidualAffineFeatureAligner(feature_channels)
        self.event_aligner = ResidualAffineFeatureAligner(feature_channels)
        self.reliability_scorer = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(feature_channels, hidden_channels),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_channels, 1),
        )
        nn.init.zeros_(self.reliability_scorer[-1].weight)
        nn.init.zeros_(self.reliability_scorer[-1].bias)

    @property
    def reliability_active(self) -> bool:
        return self.variant == "alignment_on_reliability_superset"

    def forward(self, rgb: torch.Tensor, ir: torch.Tensor, event: torch.Tensor) -> dict[str, torch.Tensor]:
        rgb_features = self.rgb_stem(rgb)
        ir_features = self.ir_stem(ir)
        event_features = self.event_stem(event)
        aligned_ir, ir_theta = self.ir_aligner(ir_features, rgb_features, True)
        aligned_event, event_theta = self.event_aligner(event_features, rgb_features, True)
        features = (rgb_features, aligned_ir, aligned_event)
        if self.reliability_active:
            logits = torch.cat([self.reliability_scorer(feature) for feature in features], dim=1)
            weights = torch.softmax(logits, dim=1)
        else:
            weights = rgb.new_full((rgb.shape[0], 3), 1.0 / 3.0)
        fused = sum(feature * weights[:, index, None, None, None] for index, feature in enumerate(features))
        return {
            "rgb_reference": rgb_features,
            "aligned_ir": aligned_ir,
            "aligned_event": aligned_event,
            "fused": fused,
            "fusion_weights": weights,
            "ir_theta": ir_theta,
            "event_theta": event_theta,
        }


class V57FusionSupersetDetector(MMUAVFeatureAlignmentDetector):
    """RepViT-FCOS detector with identical V57 superset parameters in both modes."""

    def __init__(self, variant: str, image_size: int = 320, feature_channels: int = 32,
                 fpn_out_channels: int = 128) -> None:
        if variant not in VARIANTS:
            raise ValueError(f"Unknown V57 variant: {variant}")
        super().__init__("alignment_on_equal", image_size, feature_channels, fpn_out_channels)
        self.variant = variant
        self.feature_scaffold = V57FusionSupersetScaffold(variant, feature_channels)

    def fusion_diagnostics(self) -> dict[str, object]:
        if not self.last_feature_outputs:
            raise RuntimeError("No feature forward has been run")
        weights = self.last_feature_outputs["fusion_weights"].detach().float()
        if weights.ndim != 2 or weights.shape[1] != 3:
            raise RuntimeError(f"Invalid fusion weight shape: {tuple(weights.shape)}")
        entropy = -(weights.clamp_min(1e-12) * weights.clamp_min(1e-12).log()).sum(dim=1)
        maximum, modality = weights.max(dim=1)
        names = ("rgb", "ir", "event")
        return {
            "weights_per_sample": weights.cpu().tolist(),
            "per_modality": {
                names[index]: {
                    "mean": float(weights[:, index].mean().cpu()),
                    "std": float(weights[:, index].std(unbiased=False).cpu()),
                    "min": float(weights[:, index].min().cpu()),
                    "max": float(weights[:, index].max().cpu()),
                }
                for index in range(3)
            },
            "weight_sum_max_abs_error": float((weights.sum(dim=1) - 1.0).abs().max().cpu()),
            "entropy_mean": float(entropy.mean().cpu()),
            "entropy_min": float(entropy.min().cpu()),
            "entropy_max": float(entropy.max().cpu()),
            "maximum_weight_modality": [names[index] for index in modality.cpu().tolist()],
            "dominance_fraction_mean": float(maximum.mean().cpu()),
            "departed_from_exact_uniform": not torch.equal(weights, torch.full_like(weights, 1.0 / 3.0)),
            "finite": bool(torch.isfinite(weights).all() and torch.isfinite(entropy).all()),
        }
