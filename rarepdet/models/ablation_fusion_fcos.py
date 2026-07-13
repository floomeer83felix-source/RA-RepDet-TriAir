"""Static stem-fusion FCOS controls used by the V48 causal ablation."""

from collections import OrderedDict

import timm
import torch
from torch import nn
from torchvision.models.detection import FCOS
from torchvision.models.detection.anchor_utils import AnchorGenerator
from torchvision.ops import FeaturePyramidNetwork


class ModalityStemRepViTFPNBackbone(nn.Module):
    """Shared RGB/thermal/event stems and detector stack for static controls."""

    def __init__(
        self,
        model_name="repvit_m0_9.dist_300e_in1k",
        fpn_out_channels=128,
        pretrained=False,
    ):
        super().__init__()
        self.model_name = model_name
        self.last_alpha = None

        self.rgb_stem = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.SiLU(inplace=True),
        )
        self.thermal_stem = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.SiLU(inplace=True),
        )
        self.event_stem = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.SiLU(inplace=True),
        )
        self.to_repvit = nn.Conv2d(16, 3, kernel_size=1)

        self.repvit = timm.create_model(
            model_name,
            pretrained=pretrained,
            features_only=True,
            in_chans=3,
        )
        self.in_channels_list = [48, 96, 192, 384]
        if hasattr(self.repvit, "feature_info"):
            detected_channels = list(self.repvit.feature_info.channels())
            if detected_channels:
                self.in_channels_list = detected_channels
        self.fpn = FeaturePyramidNetwork(
            in_channels_list=self.in_channels_list,
            out_channels=fpn_out_channels,
        )
        self.out_channels = fpn_out_channels

    def stem_features(self, x):
        if x.ndim != 4 or x.shape[1] != 5:
            raise ValueError(f"expected Bx5xHxW input, received {tuple(x.shape)}")
        return (
            self.rgb_stem(x[:, 0:3]),
            self.thermal_stem(x[:, 3:4]),
            self.event_stem(x[:, 4:5]),
        )

    def finish_backbone(self, fused):
        features = self.repvit(self.to_repvit(fused))
        if len(features) != len(self.in_channels_list):
            raise RuntimeError(
                f"{self.model_name} returned {len(features)} feature maps, "
                f"but FPN expects {len(self.in_channels_list)}."
            )
        feature_dict = OrderedDict((str(index), feature) for index, feature in enumerate(features))
        return self.fpn(feature_dict)


class StaticEqualRepViTFPNBackbone(ModalityStemRepViTFPNBackbone):
    """Fixed one-third RGB/thermal/event feature fusion without a learned gate."""

    def forward(self, x):
        f_rgb, f_thermal, f_event = self.stem_features(x)
        self.last_alpha = torch.full(
            (x.shape[0], 3),
            1.0 / 3.0,
            dtype=f_rgb.dtype,
            device=f_rgb.device,
        )
        return self.finish_backbone((f_rgb + f_thermal + f_event) / 3.0)


class StemsProjectRepViTFPNBackbone(ModalityStemRepViTFPNBackbone):
    """Fixed-order stem concatenation followed by a learned deterministic projection."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stem_project = nn.Conv2d(48, 16, kernel_size=1)

    def forward(self, x):
        f_rgb, f_thermal, f_event = self.stem_features(x)
        self.last_alpha = None
        fused = self.stem_project(torch.cat((f_rgb, f_thermal, f_event), dim=1))
        return self.finish_backbone(fused)


def build_static_fusion_fcos(
    backbone_type,
    model_name="repvit_m0_9.dist_300e_in1k",
    img_size=640,
    num_classes=2,
    fpn_out_channels=128,
    score_thresh=0.2,
    nms_thresh=0.6,
    detections_per_img=100,
):
    builders = {
        "ra_static_equal": StaticEqualRepViTFPNBackbone,
        "ra_stems_project": StemsProjectRepViTFPNBackbone,
    }
    try:
        backbone_builder = builders[backbone_type]
    except KeyError as exc:
        raise ValueError(f"Unknown static fusion backbone '{backbone_type}'.") from exc

    backbone = backbone_builder(
        model_name=model_name,
        fpn_out_channels=fpn_out_channels,
        pretrained=False,
    )
    anchor_sizes = ((4,), (8,), (16,), (32,))
    anchor_generator = AnchorGenerator(anchor_sizes, ((1.0,),) * len(anchor_sizes))
    return FCOS(
        backbone=backbone,
        num_classes=num_classes,
        min_size=img_size,
        max_size=img_size,
        image_mean=[0.0] * 5,
        image_std=[1.0] * 5,
        anchor_generator=anchor_generator,
        score_thresh=score_thresh,
        nms_thresh=nms_thresh,
        detections_per_img=detections_per_img,
        fixed_size=(img_size, img_size),
    )


def build_ra_static_equal_fcos(**kwargs):
    return build_static_fusion_fcos("ra_static_equal", **kwargs)


def build_ra_stems_project_fcos(**kwargs):
    return build_static_fusion_fcos("ra_stems_project", **kwargs)
