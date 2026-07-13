from torchvision.models.detection import FCOS
from torchvision.models.detection.anchor_utils import AnchorGenerator

from rarepdet.models.repvit_fpn_backbone import RepViTFPNBackbone, ReliabilityRepViTFPNBackbone


def build_early_fusion_fcos(
    model_name="repvit_m0_9.dist_300e_in1k",
    in_chans=5,
    img_size=640,
    num_classes=2,
    fpn_out_channels=128,
    score_thresh=0.2,
    nms_thresh=0.6,
    detections_per_img=100,
):
    """Build the first Early Fusion RepViT + FPN + FCOS baseline.

    num_classes is 2 because torchvision detection reserves class 0 for
    background. TriAir vehicle labels are class 0 in the txt files, so the
    training wrapper shifts them to class 1.
    """

    backbone = RepViTFPNBackbone(
        model_name=model_name,
        in_chans=in_chans,
        fpn_out_channels=fpn_out_channels,
        pretrained=False,
    )

    # RepViT-M0.9 produces four feature levels at strides 4, 8, 16, and 32 for
    # a 640x640 image. torchvision FCOS still uses one 1:1 anchor point per
    # feature location internally, so the anchor sizes must match the four FPN
    # levels instead of torchvision's default five-level FCOS setup.
    anchor_sizes = ((4,), (8,), (16,), (32,))
    aspect_ratios = ((1.0,),) * len(anchor_sizes)
    anchor_generator = AnchorGenerator(anchor_sizes, aspect_ratios)

    return FCOS(
        backbone=backbone,
        num_classes=num_classes,
        min_size=img_size,
        max_size=img_size,
        image_mean=[0.0] * in_chans,
        image_std=[1.0] * in_chans,
        anchor_generator=anchor_generator,
        score_thresh=score_thresh,
        nms_thresh=nms_thresh,
        detections_per_img=detections_per_img,
        fixed_size=(img_size, img_size),
    )


def build_reliability_fcos(
    model_name="repvit_m0_9.dist_300e_in1k",
    img_size=640,
    num_classes=2,
    fpn_out_channels=128,
    score_thresh=0.2,
    nms_thresh=0.6,
    detections_per_img=100,
):
    """Build Reliability Fusion RepViT + FPN + FCOS.

    The input is still 5 channels, but RGB, thermal, and event are fused by a
    learned reliability estimator before projecting to RepViT's 3-channel input.
    """

    backbone = ReliabilityRepViTFPNBackbone(
        model_name=model_name,
        fpn_out_channels=fpn_out_channels,
        pretrained=False,
    )

    anchor_sizes = ((4,), (8,), (16,), (32,))
    aspect_ratios = ((1.0,),) * len(anchor_sizes)
    anchor_generator = AnchorGenerator(anchor_sizes, aspect_ratios)

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


def build_detector(
    model_type="early",
    model_name="repvit_m0_9.dist_300e_in1k",
    img_size=640,
    num_classes=2,
    fpn_out_channels=128,
    score_thresh=0.2,
    nms_thresh=0.6,
    detections_per_img=100,
):
    if model_type == "early":
        return build_early_fusion_fcos(
            model_name=model_name,
            in_chans=5,
            img_size=img_size,
            num_classes=num_classes,
            fpn_out_channels=fpn_out_channels,
            score_thresh=score_thresh,
            nms_thresh=nms_thresh,
            detections_per_img=detections_per_img,
        )
    if model_type == "reliability":
        return build_reliability_fcos(
            model_name=model_name,
            img_size=img_size,
            num_classes=num_classes,
            fpn_out_channels=fpn_out_channels,
            score_thresh=score_thresh,
            nms_thresh=nms_thresh,
            detections_per_img=detections_per_img,
        )
    if model_type in {"ra_static_equal", "ra_stems_project"}:
        from rarepdet.models.ablation_fusion_fcos import build_static_fusion_fcos

        return build_static_fusion_fcos(
            model_type,
            model_name=model_name,
            img_size=img_size,
            num_classes=num_classes,
            fpn_out_channels=fpn_out_channels,
            score_thresh=score_thresh,
            nms_thresh=nms_thresh,
            detections_per_img=detections_per_img,
        )
    raise ValueError(
        f"Unknown model type '{model_type}'. Use 'early', 'reliability', "
        "'ra_static_equal', or 'ra_stems_project'."
    )
