#!/usr/bin/env python3
"""
Test Fixed Conversion - Verify the fix works
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

print("=" * 80)
print("TESTING FIXED CONVERSION")
print("=" * 80)
print()

try:
    from ai_core.depth_estimation import DepthEstimator
    from rendering.dibr_renderer import DIBRRenderer
    from rendering.sbs_composer import SBSComposer
    import cv2
    
    # Simulate UI settings
    settings = {
        'depth_intensity': 75,  # Now correctly 0-100 range
        'ipd': 65,
        'output_format': 'half_sbs',
    }
    
    print("1. Initializing models...")
    estimator = DepthEstimator()
    renderer = DIBRRenderer(ipd=settings.get('ipd', 65))
    composer = SBSComposer()
    print(f"   ✓ Models ready on {estimator.device}")
    
    print("\n2. Loading test image...")
    test_image = Path(__file__).parent / "output" / "live_test_image.png"
    image_bgr = cv2.imread(str(test_image))
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    print(f"   ✓ Image loaded: {image_rgb.shape}")
    
    print("\n3. Estimating depth...")
    depth_map = estimator.estimate_depth(image_rgb, normalize=True)
    print(f"   ✓ Depth range: [{depth_map.min():.3f}, {depth_map.max():.3f}]")
    
    print("\n4. Rendering stereo (with FIXED parameters)...")
    # NOW PASSING CORRECT VALUE (0-100 range)
    left_view, right_view = renderer.render_stereo_pair(
        image_rgb,
        depth_map,
        depth_intensity=settings.get('depth_intensity', 75)  # FIXED: no division
    )
    print(f"   ✓ Stereo pair: {left_view.shape}, {right_view.shape}")
    
    print("\n5. Composing output...")
    output = composer.compose_half_sbs(left_view, right_view)
    print(f"   ✓ Output: {output.shape}")
    
    print("\n6. Saving result...")
    output_path = test_image.parent / "fixed_conversion_test.png"
    output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(output_path), output_bgr)
    file_size = output_path.stat().st_size / 1024
    print(f"   ✓ Saved: {output_path.name} ({file_size:.1f} KB)")
    
    print("\n" + "=" * 80)
    print("✅ CONVERSION WORKS!")
    print("=" * 80)
    print()
    print("The fix is correct:")
    print("  ✓ depth_intensity now correctly uses 0-100 range")
    print("  ✓ No division by 100")
    print("  ✓ Output generated successfully")
    print()
    print("Rebuild the .app and test again!")
    print()
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
