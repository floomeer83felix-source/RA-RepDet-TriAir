#!/usr/bin/env python
"""
Check whether a timm RepViT model can expose multi-scale backbone features.

Example:
    python tools/check_repvit_features.py --model repvit_m0_9.dist_300e_in1k --img-size 640 --in-chans 3
"""

import argparse
import sys


def import_dependencies():
    try:
        import torch
    except Exception as exc:
        raise RuntimeError(f"Failed to import torch: {exc}") from exc

    try:
        import timm
    except Exception as exc:
        raise RuntimeError(f"Failed to import timm: {exc}") from exc

    return torch, timm


def shape_of(output):
    if hasattr(output, "shape"):
        return tuple(output.shape)
    if isinstance(output, (list, tuple)):
        return [shape_of(item) for item in output]
    if isinstance(output, dict):
        return {key: shape_of(value) for key, value in output.items()}
    return type(output).__name__


def print_feature_summary(args, features):
    if isinstance(features, dict):
        feature_items = list(features.items())
    elif isinstance(features, (list, tuple)):
        feature_items = [(str(index), feature) for index, feature in enumerate(features)]
    else:
        feature_items = [("0", features)]

    print("=== RepViT Feature Check ===")
    print(f"model name: {args.model}")
    print(f"in_chans: {args.in_chans}")
    print(f"img_size: {args.img_size}")
    print(f"feature layer count: {len(feature_items)}")

    for name, feature in feature_items:
        shape = shape_of(feature)
        if hasattr(feature, "shape") and len(feature.shape) == 4:
            _, channels, height, width = feature.shape
            print(f"feature {name}: shape={shape}, C={channels}, H={height}, W={width}")
        else:
            print(f"feature {name}: shape={shape}")


def run_features_only(args, torch, timm):
    print("Trying timm.create_model(..., features_only=True)")
    model = timm.create_model(
        args.model,
        pretrained=False,
        features_only=True,
        in_chans=args.in_chans,
    )
    model.eval()

    x = torch.randn(1, args.in_chans, args.img_size, args.img_size)
    with torch.no_grad():
        features = model(x)

    print_feature_summary(args, features)
    return True


def run_classification_fallback(args, torch, timm, original_error):
    print("=== features_only=True failed ===")
    print(f"model name: {args.model}")
    print(f"in_chans: {args.in_chans}")
    print(f"img_size: {args.img_size}")
    print(f"features_only error: {type(original_error).__name__}: {original_error}")
    print("\nTrying timm.create_model(..., features_only=False)")

    model = timm.create_model(
        args.model,
        pretrained=False,
        features_only=False,
        in_chans=args.in_chans,
    )
    model.eval()

    x = torch.randn(1, args.in_chans, args.img_size, args.img_size)
    with torch.no_grad():
        output = model(x)

    print(f"classification output shape: {shape_of(output)}")
    print("\n提示: timm features_only=True 不支持该 RepViT 配置时，需要用 forward hook 提取中间特征。")
    return False


def main():
    parser = argparse.ArgumentParser(description="Check timm RepViT multi-scale feature outputs.")
    parser.add_argument("--model", default="repvit_m0_9.dist_300e_in1k", help="timm model name")
    parser.add_argument("--img-size", default=640, type=int, help="Input image size")
    parser.add_argument("--in-chans", default=3, type=int, help="Input channel count")
    args = parser.parse_args()

    if args.img_size <= 0:
        raise SystemExit("ERROR: --img-size must be positive.")
    if args.in_chans <= 0:
        raise SystemExit("ERROR: --in-chans must be positive.")

    try:
        torch, timm = import_dependencies()
    except RuntimeError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc

    try:
        run_features_only(args, torch, timm)
    except Exception as exc:
        try:
            run_classification_fallback(args, torch, timm, exc)
        except Exception as fallback_exc:
            print("=== Classification Fallback Failed ===")
            print(f"fallback error: {type(fallback_exc).__name__}: {fallback_exc}")
            print("\n提示: 请确认 timm 版本包含该模型名，或检查模型是否支持自定义 in_chans。")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
