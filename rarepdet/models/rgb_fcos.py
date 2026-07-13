"""Pure RGB RepViT-M0.9 FPN FCOS used by the V50 external baseline."""

from rarepdet.models.early_fusion_fcos import build_early_fusion_fcos


def build_rgb_fcos(
    model_name="repvit_m0_9.dist_300e_in1k",
    img_size=640,
    num_classes=2,
    fpn_out_channels=128,
    score_thresh=0.2,
    nms_thresh=0.6,
    detections_per_img=100,
):
    return build_early_fusion_fcos(
        model_name=model_name,
        in_chans=3,
        img_size=img_size,
        num_classes=num_classes,
        fpn_out_channels=fpn_out_channels,
        score_thresh=score_thresh,
        nms_thresh=nms_thresh,
        detections_per_img=detections_per_img,
    )
