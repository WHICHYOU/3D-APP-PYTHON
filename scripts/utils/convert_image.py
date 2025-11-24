#!/usr/bin/env python3
"""
Convert a single image to 3D
Usage: python convert_image.py input.jpg output_3d.jpg
"""
import sys
import argparse
from pathlib import Path
import cv2
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ai_core.depth_estimation import DepthEstimator
from rendering.dibr_renderer import DIBRRenderer
from rendering.sbs_composer import SBSComposer


def convert_image_to_3d(
    input_path: str,
    output_path: str,
    format: str = "half_sbs",
    depth_intensity: float = 75.0,
    ipd: float = 65.0,
    save_depth: bool = False
):
    """
    Convert a 2D image to 3D
    
    Args:
        input_path: Path to input image
        output_path: Path to output image
        format: Output format ('half_sbs', 'full_sbs', 'anaglyph')
        depth_intensity: Depth effect strength (0-100)
        ipd: Interpupillary distance in mm
        save_depth: Whether to save depth map
    """
    print(f"Converting {input_path} to 3D...")
    
    # Load image
    print("1. Loading image...")
    image_bgr = cv2.imread(input_path)
    if image_bgr is None:
        raise ValueError(f"Could not load image: {input_path}")
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]
    print(f"   Image loaded: {width}x{height}")
    
    # Initialize depth estimator
    print("2. Loading MiDaS model...")
    estimator = DepthEstimator(model_type="midas_v3", device="auto")
    print("   ✓ Model loaded")
    
    # Estimate depth
    print("3. Estimating depth...")
    depth_map = estimator.estimate_depth(image, normalize=True)
    print(f"   ✓ Depth estimated (range: {depth_map.min():.3f} - {depth_map.max():.3f})")
    
    # Save depth map if requested
    if save_depth:
        depth_path = Path(output_path).parent / (Path(output_path).stem + "_depth.png")
        depth_vis = (depth_map * 255).astype(np.uint8)
        cv2.imwrite(str(depth_path), depth_vis)
        print(f"   ✓ Depth map saved: {depth_path}")
    
    # Render stereoscopic pair
    print("4. Rendering stereo pair...")
    renderer = DIBRRenderer(ipd=ipd)
    left_view, right_view = renderer.render_stereo_pair(
        image, depth_map, depth_intensity=depth_intensity
    )
    print("   ✓ Stereo pair rendered")
    
    # Compose output
    print(f"5. Composing {format} output...")
    composer = SBSComposer()
    
    if format == "half_sbs":
        output = composer.compose_half_sbs(left_view, right_view)
    elif format == "full_sbs":
        output = composer.compose_full_sbs(left_view, right_view)
    elif format == "anaglyph":
        output = composer.compose_anaglyph(left_view, right_view)
    elif format == "top_bottom":
        output = composer.compose_top_bottom(left_view, right_view, half=True)
    else:
        raise ValueError(f"Unknown format: {format}")
    
    print(f"   ✓ Output composed: {output.shape}")
    
    # Save output
    print("6. Saving output...")
    output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, output_bgr)
    print(f"   ✓ Saved to: {output_path}")
    
    print("\n✅ Conversion complete!")


def main():
    parser = argparse.ArgumentParser(description="Convert 2D image to 3D")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument(
        "--format",
        choices=["half_sbs", "full_sbs", "anaglyph", "top_bottom"],
        default="half_sbs",
        help="Output format (default: half_sbs)"
    )
    parser.add_argument(
        "--depth-intensity",
        type=float,
        default=75.0,
        help="Depth effect strength 0-100 (default: 75)"
    )
    parser.add_argument(
        "--ipd",
        type=float,
        default=65.0,
        help="Interpupillary distance in mm (default: 65)"
    )
    parser.add_argument(
        "--save-depth",
        action="store_true",
        help="Save depth map as separate file"
    )
    
    args = parser.parse_args()
    
    try:
        convert_image_to_3d(
            args.input,
            args.output,
            format=args.format,
            depth_intensity=args.depth_intensity,
            ipd=args.ipd,
            save_depth=args.save_depth
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
