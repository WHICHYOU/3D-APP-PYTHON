#!/usr/bin/env python3
"""
Quick test script for depth estimation
"""
import sys
import cv2
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ai_core.depth_estimation import DepthEstimator
from rendering.dibr_renderer import DIBRRenderer
from rendering.sbs_composer import SBSComposer


def test_depth_estimation():
    """Test depth estimation on a sample image"""
    print("=" * 60)
    print("Testing 2D to 3D Conversion Pipeline")
    print("=" * 60)
    
    # Create a sample image (gradient)
    print("\n1. Creating test image...")
    height, width = 480, 640
    test_image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create a gradient (simulating depth)
    for i in range(height):
        value = int(255 * (i / height))
        test_image[i, :, :] = [value, value // 2, 255 - value]
    
    # Add some shapes
    cv2.circle(test_image, (320, 240), 80, (255, 255, 255), -1)
    cv2.rectangle(test_image, (100, 100), (200, 200), (0, 255, 0), -1)
    
    print(f"   Test image created: {width}x{height}")
    
    # Initialize depth estimator
    print("\n2. Loading MiDaS model...")
    try:
        estimator = DepthEstimator(
            model_type="midas_v3",
            device="auto",
            precision="fp32"
        )
        print("   ✓ Model loaded successfully")
    except Exception as e:
        print(f"   ✗ Error loading model: {e}")
        print("\n   This is expected on first run.")
        print("   The model will be downloaded from PyTorch Hub.")
        print("   Please ensure you have internet connection.")
        return
    
    # Estimate depth
    print("\n3. Estimating depth map...")
    try:
        depth_map = estimator.estimate_depth(test_image, normalize=True)
        print(f"   ✓ Depth map generated: {depth_map.shape}")
        print(f"   Depth range: [{depth_map.min():.3f}, {depth_map.max():.3f}]")
    except Exception as e:
        print(f"   ✗ Error estimating depth: {e}")
        return
    
    # Render stereoscopic pair
    print("\n4. Rendering stereoscopic views...")
    try:
        renderer = DIBRRenderer(ipd=65.0, convergence=1.0)
        left_view, right_view = renderer.render_stereo_pair(
            test_image,
            depth_map,
            depth_intensity=75.0
        )
        print(f"   ✓ Stereo pair rendered")
        print(f"   Left view: {left_view.shape}")
        print(f"   Right view: {right_view.shape}")
    except Exception as e:
        print(f"   ✗ Error rendering: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Compose output formats
    print("\n5. Composing output formats...")
    try:
        composer = SBSComposer()
        
        # Half SBS
        half_sbs = composer.compose_half_sbs(left_view, right_view)
        print(f"   ✓ Half SBS: {half_sbs.shape}")
        
        # Anaglyph
        anaglyph = composer.compose_anaglyph(left_view, right_view)
        print(f"   ✓ Anaglyph: {anaglyph.shape}")
    except Exception as e:
        print(f"   ✗ Error composing: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Save outputs
    print("\n6. Saving outputs...")
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Save original
        cv2.imwrite(str(output_dir / "01_original.png"), 
                    cv2.cvtColor(test_image, cv2.COLOR_RGB2BGR))
        
        # Save depth map (as grayscale)
        depth_vis = (depth_map * 255).astype(np.uint8)
        cv2.imwrite(str(output_dir / "02_depth_map.png"), depth_vis)
        
        # Save left view
        cv2.imwrite(str(output_dir / "03_left_view.png"),
                    cv2.cvtColor(left_view, cv2.COLOR_RGB2BGR))
        
        # Save right view
        cv2.imwrite(str(output_dir / "04_right_view.png"),
                    cv2.cvtColor(right_view, cv2.COLOR_RGB2BGR))
        
        # Save half SBS
        cv2.imwrite(str(output_dir / "05_half_sbs.png"),
                    cv2.cvtColor(half_sbs, cv2.COLOR_RGB2BGR))
        
        # Save anaglyph
        cv2.imwrite(str(output_dir / "06_anaglyph.png"),
                    cv2.cvtColor(anaglyph, cv2.COLOR_RGB2BGR))
        
        print(f"   ✓ Outputs saved to: {output_dir.absolute()}")
    except Exception as e:
        print(f"   ✗ Error saving: {e}")
        return
    
    print("\n" + "=" * 60)
    print("SUCCESS! Core pipeline is working! 🎉")
    print("=" * 60)
    print(f"\nCheck the outputs in: {output_dir.absolute()}")
    print("\nNext steps:")
    print("  - Test with real images")
    print("  - Implement video processing")
    print("  - Connect to GUI")
    print()


if __name__ == "__main__":
    test_depth_estimation()
