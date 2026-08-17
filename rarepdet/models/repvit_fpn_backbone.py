from collections import OrderedDict

import timm
import torch
from torch import nn
from torchvision.ops import FeaturePyramidNetwork


class RepViTFPNBackbone(nn.Module):
    """Early-fusion RepViT backbone with an FPN neck.

    TriAir stores 5 channels per image:
    channels 0-2 are RGB, channel 3 is thermal/infrared, and channel 4 is event.
    This baseline uses early fusion by projecting all 5 channels to a 3-channel
    tensor before feeding RepViT. No reliability fusion or modality dropout is
    used here.
    """

    def __init__(
        self,
        model_name="repvit_m0_9.dist_300e_in1k",
        in_chans=5,
        fpn_out_channels=128,
        pretrained=False,
    ):
        super().__init__()
        self.model_name = model_name
        self.in_chans = in_chans
        self.last_alpha = None

        # The detector receives RGB + thermal + event as 5 channels. RepViT-M0.9
        # is a 3-channel ImageNet model in timm, so a 1x1 projection is the
        # simplest first baseline for early fusion.
        self.input_proj = nn.Conv2d(in_chans, 3, kernel_size=1)

        self.repvit = timm.create_model(
            model_name,
            pretrained=pretrained,
            features_only=True,
            in_chans=3,
        )

        # For a 640x640 input, timm RepViT-M0.9 features_only=True returns:
        # 48x160x160, 96x80x80, 192x40x40, 384x20x20. These are the FPN input
        # channels for the four backbone stages.
        self.in_channels_list = [48, 96, 192, 384]
        if hasattr(self.repvit, "feature_info"):
            detected_channels = list(self.repvit.feature_info.channels())
            if detected_channels:
                self.in_channels_list = detected_channels

        self.fpn = FeaturePyramidNetwork(
            in_channels_list=self.in_channels_list,
            out_channels=fpn_out_channels,
        )

        # torchvision detection models expect all returned FPN levels to share
        # the same channel count and expose it as backbone.out_channels.
        self.out_channels = fpn_out_channels

    def forward(self, x):
        x = self.input_proj(x)
        features = self.repvit(x)

        if len(features) != len(self.in_channels_list):
            raise RuntimeError(
                f"{self.model_name} returned {len(features)} feature maps, "
                f"but FPN expects {len(self.in_channels_list)}."
            )

        feature_dict = OrderedDict((str(index), feature) for index, feature in enumerate(features))
        return self.fpn(feature_dict)


class ReliabilityRepViTFPNBackbone(nn.Module):
    """Reliability-gated RGB/Thermal/Event fusion before RepViT.

    Input is Bx5xHxW:
    RGB = channels 0:3, thermal = channel 3, event = channel 4.
    The three modality stems produce 16-channel feature maps. A lightweight
    reliability estimator predicts alpha_rgb, alpha_thermal, alpha_event and
    fuses the stems before a 1x1 projection to RepViT's 3-channel input.
    """

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
        self.reliability = nn.Sequential(
            nn.Linear(48, 16),
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

        # RepViT-M0.9 features_only=True outputs channels [48, 96, 192, 384].
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

    def forward(self, x):
        rgb = x[:, 0:3]
        thermal = x[:, 3:4]
        event = x[:, 4:5]

        f_rgb = self.rgb_stem(rgb)
        f_thermal = self.thermal_stem(thermal)
        f_event = self.event_stem(event)

        pooled = torch.cat(
            [
                torch.flatten(torch.nn.functional.adaptive_avg_pool2d(f_rgb, 1), 1),
                torch.flatten(torch.nn.functional.adaptive_avg_pool2d(f_thermal, 1), 1),
                torch.flatten(torch.nn.functional.adaptive_avg_pool2d(f_event, 1), 1),
            ],
            dim=1,
        )
        alpha = torch.softmax(self.reliability(pooled), dim=1)
        self.last_alpha = alpha.detach()

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
        return self.fpn(feature_dict)
