"""Single-modality RepViT-FPN-FCOS builders for the V76 major-revision ablation."""

from rarepdet.models.early_fusion_fcos import build_early_fusion_fcos

INPUT_CHANNELS = {"rgb": 3, "thermal": 1, "event": 1}


def build_v76_single_modality_detector(
    input_mode: str,
    *,
    model_name: str = "repvit_m0_9.dist_300e_in1k",
    img_size: int = 640,
    num_classes: int = 2,
    fpn_out_channels: int = 128,
    score_thresh: float = 0.2,
    nms_thresh: float = 0.6,
    detections_per_img: int = 100,
):
    """Build a detector whose input contains exactly one TriAir modality.

    RGB uses three channels. Thermal and event each use one channel. The detector
    stack and optimization contract otherwise match the frozen TriAir baseline.
    """
    try:
        in_chans = INPUT_CHANNELS[input_mode]
    except KeyError as exc:
        raise ValueError(f"input_mode must be one of {sorted(INPUT_CHANNELS)}, got {input_mode!r}") from exc
    return build_early_fusion_fcos(
        model_name=model_name,
        in_chans=in_chans,
        img_size=img_size,
        num_classes=num_classes,
        fpn_out_channels=fpn_out_channels,
        score_thresh=score_thresh,
        nms_thresh=nms_thresh,
        detections_per_img=detections_per_img,
    )
