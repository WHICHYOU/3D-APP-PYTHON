#!/usr/bin/env python3
"""
End-to-end image conversion test
Creates a test image and runs full conversion pipeline
"""
import sys
import numpy as np
import cv2
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_core.depth_estimation import DepthEstimator
from src.rendering.dibr_renderer import DIBRRenderer
from src.rendering.sbs_composer import SBSComposer

def create_test_image(output_path):
    """Create a simple test image with gradient and shapes."""
    # Create 640x480 RGB image with gradient background
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Gradient background (blue to cyan)
    for y in range(480):
        intensity = int((y / 480) * 255)
        img[y, :] = [intensity, intensity, 255]
    
    # Add some shapes for depth variation
    cv2.circle(img, (320, 240), 100, (255, 255, 0), -1)  # Yellow circle
    cv2.rectangle(img, (100, 100), (200, 200), (0, 255, 0), -1)  # Green square
    cv2.rectangle(img, (440, 280), (540, 380), (255, 0, 0), -1)  # Red square
    
    cv2.imwrite(str(output_path), img)
    print(f"Created test image: {output_path} ({img.shape})")
    return img

def main():
    print("=" * 60)
    print("IMAGE CONVERSION TEST")
    print("=" * 60)
    
    # Setup paths
    test_dir = Path(__file__).parent
    test_image_path = test_dir / "test_input.png"
    output_dir = test_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Create test image
    print("\n1. Creating test image...")
    test_img_bgr = create_test_image(test_image_path)
    test_img_rgb = cv2.cvtColor(test_img_bgr, cv2.COLOR_BGR2RGB)
    
    # Initialize models
    print("\n2. Initializing AI models...")
    estimator = DepthEstimator()
    renderer = DIBRRenderer(ipd=65)
    composer = SBSComposer()
    print("   ✓ Models initialized")
    
    # Estimate depth
    print("\n3. Estimating depth map...")
    depth_map = estimator.estimate_depth(test_img_rgb, normalize=True)
    print(f"   ✓ Depth map: shape={depth_map.shape}, range=[{depth_map.min():.3f}, {depth_map.max():.3f}]")
    
    # Save depth visualization
    depth_vis = (depth_map * 255).astype(np.uint8)
    depth_vis_bgr = cv2.cvtColor(depth_vis, cv2.COLOR_GRAY2BGR)
    depth_path = output_dir / "test_depth.png"
    cv2.imwrite(str(depth_path), depth_vis_bgr)
    print(f"   Saved depth visualization: {depth_path}")
    
    # Render stereo pair
    print("\n4. Rendering stereo views...")
    left_view, right_view = renderer.render_stereo_pair(
        test_img_rgb,
        depth_map,
        depth_intensity=0.75
    )
    print(f"   ✓ Left view: {left_view.shape}")
    print(f"   ✓ Right view: {right_view.shape}")
    
    # Test all output formats
    formats = [
        ('half_sbs', 'Half Side-by-Side'),
        ('full_sbs', 'Full Side-by-Side'),
        ('anaglyph', 'Anaglyph (Red-Cyan)'),
        ('top_bottom', 'Top-Bottom')
    ]
    
    print("\n5. Composing outputs in all formats...")
    for format_id, format_name in formats:
        if format_id == 'half_sbs':
            output = composer.compose_half_sbs(left_view, right_view)
        elif format_id == 'full_sbs':
            output = composer.compose_full_sbs(left_view, right_view)
        elif format_id == 'anaglyph':
            output = composer.compose_anaglyph(left_view, right_view)
        elif format_id == 'top_bottom':
            output = composer.compose_top_bottom(left_view, right_view, half=True)
        
        output_path = output_dir / f"test_output_{format_id}.png"
        output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_path), output_bgr)
        
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"   ✓ {format_name}: {output_path.name} ({output.shape}, {file_size:.1f} KB)")
    
    print("\n" + "=" * 60)
    print("✓ IMAGE CONVERSION TEST PASSED")
    print("=" * 60)
    print(f"\nTest files created in: {output_dir}")
    print("\nYou can verify outputs:")
    print(f"  open {output_dir}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
