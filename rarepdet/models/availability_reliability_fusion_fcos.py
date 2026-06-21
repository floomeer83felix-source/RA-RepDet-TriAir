"""Availability-conditioned reliability fusion FCOS detector."""

from collections import OrderedDict

import timm
import torch
from torch import nn
from torchvision.models.detection import FCOS
from torchvision.models.detection.anchor_utils import AnchorGenerator
from torchvision.ops import FeaturePyramidNetwork


class AvailabilityReliabilityRepViTFPNBackbone(nn.Module):
    """Reliability fusion with explicit modality availability conditioning.

    Input channels follow the project convention:
    RGB = x[:, 0:3], thermal = x[:, 3:4], event = x[:, 4:5].

    When an availability tensor is supplied, it must be shaped Bx3 in RGB,
    thermal, event order. If it is not supplied, the backbone derives it from
    exact all-zero modality tensors. That fallback is intended only for the
    project's synthetic missing-modality evaluation convention.
    """

    def __init__(
        self,
        model_name="repvit_m0_9.dist_300e_in1k",
        fpn_out_channels=128,
        pretrained=False,
    ):
        super().__init__()
        self.model_name = model_name
        self.current_availability = None
        self.last_alpha = None
        self.last_availability = None
        self.last_post_stem_energy = None

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
        self.reliability = nn.Sequential(
            nn.Linear(51, 16),
            nn.SiLU(inplace=True),
            nn.Linear(16, 3),
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

    def set_availability(self, availability):
        self.current_availability = availability

    def _derive_availability(self, x):
        rgb_present = x[:, 0:3].abs().flatten(1).sum(dim=1) > 0
        thermal_present = x[:, 3:4].abs().flatten(1).sum(dim=1) > 0
        event_present = x[:, 4:5].abs().flatten(1).sum(dim=1) > 0
        availability = torch.stack([rgb_present, thermal_present, event_present], dim=1).to(
            dtype=x.dtype,
            device=x.device,
        )

        # Avoid an undefined all-absent softmax in degenerate synthetic inputs.
        all_absent = availability.sum(dim=1) == 0
        if bool(all_absent.any()):
            availability[all_absent] = 1.0
        return availability

    def _get_availability(self, x):
        if self.current_availability is None:
            return self._derive_availability(x)
        availability = self.current_availability.to(device=x.device, dtype=x.dtype)
        if availability.ndim != 2 or availability.shape != (x.shape[0], 3):
            raise ValueError(f"availability must have shape ({x.shape[0]}, 3), got {tuple(availability.shape)}")
        all_absent = availability.sum(dim=1) == 0
        if bool(all_absent.any()):
            availability = availability.clone()
            availability[all_absent] = 1.0
        return availability

    def forward(self, x):
        availability = self._get_availability(x)

        rgb = x[:, 0:3]
        thermal = x[:, 3:4]
        event = x[:, 4:5]

        f_rgb = self.rgb_stem(rgb) * availability[:, 0].view(-1, 1, 1, 1)
        f_thermal = self.thermal_stem(thermal) * availability[:, 1].view(-1, 1, 1, 1)
        f_event = self.event_stem(event) * availability[:, 2].view(-1, 1, 1, 1)

        self.last_post_stem_energy = torch.stack(
            [
                f_rgb.detach().abs().flatten(1).sum(dim=1),
                f_thermal.detach().abs().flatten(1).sum(dim=1),
                f_event.detach().abs().flatten(1).sum(dim=1),
            ],
            dim=1,
        )

        pooled = torch.cat(
            [
                torch.flatten(torch.nn.functional.adaptive_avg_pool2d(f_rgb, 1), 1),
                torch.flatten(torch.nn.functional.adaptive_avg_pool2d(f_thermal, 1), 1),
                torch.flatten(torch.nn.functional.adaptive_avg_pool2d(f_event, 1), 1),
                availability,
            ],
            dim=1,
        )
        logits = self.reliability(pooled)
        logits = logits.masked_fill(availability <= 0, -1e9)
        alpha = torch.softmax(logits, dim=1)
        self.last_alpha = alpha.detach()
        self.last_availability = availability.detach()

        fused = (
            alpha[:, 0].view(-1, 1, 1, 1) * f_rgb
            + alpha[:, 1].view(-1, 1, 1, 1) * f_thermal
            + alpha[:, 2].view(-1, 1, 1, 1) * f_event
        )
        x = self.to_repvit(fused)
        features = self.repvit(x)

        if len(features) != len(self.in_channels_list):
            raise RuntimeError(
                f"{self.model_name} returned {len(features)} feature maps, "
                f"but FPN expects {len(self.in_channels_list)}."
            )

        feature_dict = OrderedDict((str(index), feature) for index, feature in enumerate(features))
        self.current_availability = None
        return self.fpn(feature_dict)


class AvailabilityConditionedFCOS(nn.Module):
    """Thin wrapper that keeps torchvision FCOS return conventions intact."""

    def __init__(self, detector):
        super().__init__()
        self.detector = detector

    @property
    def backbone(self):
        return self.detector.backbone

    def forward(self, images, targets=None, availability=None):
        self.detector.backbone.set_availability(availability)
        return self.detector(images, targets)


def build_availability_reliability_fcos(
    model_name="repvit_m0_9.dist_300e_in1k",
    img_size=640,
    num_classes=2,
    fpn_out_channels=128,
    score_thresh=0.2,
    nms_thresh=0.6,
    detections_per_img=100,
):
    backbone = AvailabilityReliabilityRepViTFPNBackbone(
        model_name=model_name,
        fpn_out_channels=fpn_out_channels,
        pretrained=False,
    )
    anchor_sizes = ((4,), (8,), (16,), (32,))
    aspect_ratios = ((1.0,),) * len(anchor_sizes)
    anchor_generator = AnchorGenerator(anchor_sizes, aspect_ratios)

    detector = FCOS(
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
    return AvailabilityConditionedFCOS(detector)
