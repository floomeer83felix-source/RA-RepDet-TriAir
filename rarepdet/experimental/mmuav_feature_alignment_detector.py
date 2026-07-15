"""V54-only MM-UAV feature-alignment integration with the existing RepViT-FCOS path."""

from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F

from rarepdet.experimental.mmuav_feature_alignment_model import MMUAVFeatureAlignmentScaffold
from rarepdet.models.early_fusion_fcos import build_early_fusion_fcos


VARIANTS = {
    "rgb_only": {"alignment_enabled": False, "fusion_mode": "equal", "rgb_only": True},
    "alignment_off_equal": {"alignment_enabled": False, "fusion_mode": "equal", "rgb_only": False},
    "alignment_on_equal": {"alignment_enabled": True, "fusion_mode": "equal", "rgb_only": False},
    "alignment_on_reliability": {"alignment_enabled": True, "fusion_mode": "reliability", "rgb_only": False},
}


class MMUAVFeatureAlignmentDetector(nn.Module):
    """Keeps modality inputs separate until feature-space fusion before RepViT-FCOS."""

    def __init__(self, variant: str = "alignment_on_equal", image_size: int = 320,
                 feature_channels: int = 32, fpn_out_channels: int = 128) -> None:
        super().__init__()
        if variant not in VARIANTS:
            raise ValueError(f"Unknown V54 variant: {variant}")
        settings = VARIANTS[variant]
        self.variant = variant
        self.image_size = image_size
        self.rgb_only = settings["rgb_only"]
        self.feature_scaffold = MMUAVFeatureAlignmentScaffold(
            feature_channels=feature_channels,
            alignment_enabled=settings["alignment_enabled"],
            fusion_mode=settings["fusion_mode"],
        )
        self.to_detector_image = nn.Conv2d(feature_channels, 3, kernel_size=1)
        self.detector = build_early_fusion_fcos(
            in_chans=3, img_size=image_size, num_classes=2, fpn_out_channels=fpn_out_channels,
        )
        self.last_feature_outputs: dict[str, torch.Tensor] = {}

    def _feature_forward(self, rgb: torch.Tensor, ir: torch.Tensor, event: torch.Tensor) -> torch.Tensor:
        if self.rgb_only:
            rgb_features = self.feature_scaffold.rgb_stem(rgb)
            zeros = torch.zeros_like(rgb_features)
            identity = self.feature_scaffold.ir_aligner.identity_theta.unsqueeze(0).expand(rgb.shape[0], -1, -1)
            outputs = {"rgb_reference": rgb_features, "aligned_ir": zeros, "aligned_event": zeros,
                       "fused": rgb_features, "fusion_weights": rgb.new_tensor([[1.0, 0.0, 0.0]]).expand(rgb.shape[0], -1),
                       "ir_theta": identity, "event_theta": identity}
        else:
            outputs = self.feature_scaffold(rgb, ir, event)
        self.last_feature_outputs = outputs
        detector_image = self.to_detector_image(outputs["fused"])
        return F.interpolate(detector_image, size=(self.image_size, self.image_size), mode="bilinear",
                             align_corners=False)

    def forward(self, rgb: torch.Tensor, ir: torch.Tensor, event: torch.Tensor,
                targets: list[dict[str, torch.Tensor]] | None = None):
        detector_images = self._feature_forward(rgb, ir, event)
        return self.detector(list(detector_images), targets)

    def alignment_diagnostics(self) -> dict[str, object]:
        if not self.last_feature_outputs:
            raise RuntimeError("No feature forward has been run")
        outputs = self.last_feature_outputs
        diagnostics: dict[str, object] = {"feature_shapes": {}, "feature_stats": {}}
        for key in ("rgb_reference", "aligned_ir", "aligned_event", "fused"):
            value = outputs[key].detach().float()
            diagnostics["feature_shapes"][key] = list(value.shape)
            diagnostics["feature_stats"][key] = {"mean": float(value.mean().cpu()),
                                                   "std": float(value.std(unbiased=False).cpu())}
        diagnostics["fusion_weights"] = outputs["fusion_weights"].detach().float().cpu().tolist()
        for modality in ("ir", "event"):
            theta = outputs[f"{modality}_theta"].detach().float()
            identity = theta.new_tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
            determinant = theta[:, 0, 0] * theta[:, 1, 1] - theta[:, 0, 1] * theta[:, 1, 0]
            feature = outputs[f"aligned_{modality}"]
            grid = F.affine_grid(theta, feature.shape, align_corners=False)
            diagnostics[modality] = {
                "theta_mean": float(theta.mean().cpu()), "theta_std": float(theta.std(unbiased=False).cpu()),
                "theta_min": float(theta.min().cpu()), "theta_max": float(theta.max().cpu()),
                "theta_max_abs_deviation": float((theta - identity).abs().max().cpu()),
                "determinant_mean": float(determinant.mean().cpu()),
                "determinant_min": float(determinant.min().cpu()),
                "determinant_max": float(determinant.max().cpu()),
                "grid_oob_fraction": float((grid.abs() > 1.0).any(dim=-1).float().mean().cpu()),
                "finite": bool(torch.isfinite(theta).all() and torch.isfinite(grid).all()),
            }
        return diagnostics
