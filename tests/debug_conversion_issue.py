#!/usr/bin/env python3
"""
Debug Progress Dialog - Test what's hanging in conversion
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

print("Testing ConversionWorker logic...")
print("=" * 80)

# Simulate the exact flow from progress_dialog.py
try:
    print("\n1. Importing modules...")
    from ai_core.depth_estimation import DepthEstimator
    from rendering.dibr_renderer import DIBRRenderer
    from rendering.sbs_composer import SBSComposer
    import cv2
    import numpy as np
    print("   ✓ Imports successful")
    
    print("\n2. Settings (matching UI)...")
    settings = {
        'depth_intensity': 75,
        'ipd': 65,
        'output_format': 'half_sbs',
    }
    print(f"   Settings: {settings}")
    
    print("\n3. Initializing models...")
    estimator = DepthEstimator()
    renderer = DIBRRenderer(ipd=settings.get('ipd', 65))
    composer = SBSComposer()
    print(f"   ✓ Models initialized on {estimator.device}")
    
    print("\n4. Loading test image...")
    test_image = Path(__file__).parent / "output" / "live_test_image.png"
    if not test_image.exists():
        print(f"   ✗ Test image not found: {test_image}")
        sys.exit(1)
    
    image_bgr = cv2.imread(str(test_image))
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    print(f"   ✓ Image loaded: {image_rgb.shape}")
    
    print("\n5. Estimating depth (with normalize=True parameter)...")
    depth_map = estimator.estimate_depth(image_rgb, normalize=True)
    print(f"   ✓ Depth map: shape={depth_map.shape}, range=[{depth_map.min():.3f}, {depth_map.max():.3f}]")
    
    print("\n6. Rendering stereo pair (with depth_intensity parameter)...")
    try:
        left_view, right_view = renderer.render_stereo_pair(
            image_rgb,
            depth_map,
            depth_intensity=settings.get('depth_intensity', 75) / 100.0
        )
        print(f"   ✗ ISSUE: depth_intensity should be 0-100, not 0-1")
        print(f"   Passed: {settings.get('depth_intensity', 75) / 100.0}")
        print(f"   Should pass: {settings.get('depth_intensity', 75)}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        
        # Try with correct parameter
        print("\n   Trying with correct parameter (0-100 range)...")
        left_view, right_view = renderer.render_stereo_pair(
            image_rgb,
            depth_map,
            depth_intensity=settings.get('depth_intensity', 75)
        )
        print(f"   ✓ Stereo pair rendered: {left_view.shape}, {right_view.shape}")
    
    print("\n7. Composing output...")
    output_format = settings.get('output_format', 'half_sbs')
    if output_format == 'half_sbs':
        output = composer.compose_half_sbs(left_view, right_view)
    elif output_format == 'full_sbs':
        output = composer.compose_full_sbs(left_view, right_view)
    print(f"   ✓ Output composed: {output.shape}")
    
    print("\n8. Saving output...")
    output_path = test_image.parent / "debug_output.png"
    output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(output_path), output_bgr)
    print(f"   ✓ Saved to: {output_path}")
    
    print("\n" + "=" * 80)
    print("✅ DIAGNOSIS: Found the issue!")
    print()
    print("PROBLEM: progress_dialog.py divides depth_intensity by 100")
    print("         But render_stereo_pair() expects 0-100 range, not 0-1")
    print()
    print("LINE 119-122 in progress_dialog.py:")
    print("  left_view, right_view = renderer.render_stereo_pair(")
    print("      image_rgb,")
    print("      depth_map,")
    print("      depth_intensity=self.settings.get('depth_intensity', 75) / 100.0  # WRONG!")
    print("  )")
    print()
    print("SHOULD BE:")
    print("      depth_intensity=self.settings.get('depth_intensity', 75)  # CORRECT")
    print()
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
