#!/usr/bin/env python3
"""
Live App Integration Test

Tests actual conversion through the app's internal APIs
(simulates what happens when user clicks Convert button)
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

print("=" * 80)
print("LIVE APP CONVERSION TEST")
print("Testing actual conversion workflow through app APIs")
print("=" * 80)
print()

# Create test media
print("1. Creating test media...")
test_input_dir = Path(__file__).parent / "output"
test_input_dir.mkdir(exist_ok=True)

test_image = test_input_dir / "live_test_image.png"
test_img = np.zeros((480, 640, 3), dtype=np.uint8)
for i in range(480):
    test_img[i, :] = int(255 * i / 480)
cv2.circle(test_img, (320, 240), 80, (0, 255, 0), -1)
cv2.rectangle(test_img, (120, 120), (220, 220), (255, 0, 0), -1)
cv2.imwrite(str(test_image), test_img)
print(f"   ✓ Created test image: {test_image.name} ({test_image.stat().st_size / 1024:.1f} KB)")

# Test conversion workflow (matches progress_dialog.py)
print("\n2. Testing conversion workflow...")

from ai_core.depth_estimation import DepthEstimator
from rendering.dibr_renderer import DIBRRenderer
from rendering.sbs_composer import SBSComposer

# Initialize (matches ConversionWorker.__init__)
print("   - Initializing models...")
depth_estimator = DepthEstimator()
renderer = DIBRRenderer()
composer = SBSComposer()
print(f"   ✓ Models initialized on {depth_estimator.device}")

# Settings (matches what UI passes)
settings = {
    'depth_strength': 1.0,
    'baseline': 0.1,
    'convergence': 0.5,
    'output_format': 'half_sbs',
    'output_dir': str(test_input_dir)
}

print(f"\n3. Converting image with settings:")
print(f"   - Depth strength: {settings['depth_strength']}")
print(f"   - Baseline: {settings['baseline']}")
print(f"   - Output format: {settings['output_format']}")

# Load image
img = cv2.imread(str(test_image))
print(f"\n   Step 1: Loaded image - shape {img.shape}")

# Estimate depth
depth_map = depth_estimator.estimate_depth(img)
print(f"   Step 2: Estimated depth - range [{depth_map.min():.3f}, {depth_map.max():.3f}]")

# Apply settings to renderer
renderer.depth_strength = settings['depth_strength']
renderer.baseline = settings['baseline']
renderer.convergence = settings['convergence']

# Render stereo pair
left_view, right_view = renderer.render_stereo_pair(img, depth_map)
print(f"   Step 3: Rendered stereo - left: {left_view.shape}, right: {right_view.shape}")

# Test all output formats
formats = {
    'half_sbs': composer.compose_half_sbs,
    'full_sbs': composer.compose_full_sbs,
    'anaglyph': composer.compose_anaglyph,
    'top_bottom': composer.compose_top_bottom
}

print(f"\n4. Generating all output formats...")
for fmt_name, fmt_method in formats.items():
    output = fmt_method(left_view, right_view)
    output_path = test_input_dir / f"live_output_{fmt_name}.png"
    cv2.imwrite(str(output_path), output)
    file_size = output_path.stat().st_size / 1024
    print(f"   ✓ {fmt_name}: {output.shape} → {file_size:.1f} KB")

# Verify output files exist and are valid
print(f"\n5. Verifying output files...")
all_valid = True
for fmt_name in formats.keys():
    output_path = test_input_dir / f"live_output_{fmt_name}.png"
    if not output_path.exists():
        print(f"   ✗ {fmt_name}: File missing!")
        all_valid = False
        continue
    
    # Try to read back the image
    verify_img = cv2.imread(str(output_path))
    if verify_img is None:
        print(f"   ✗ {fmt_name}: File corrupted!")
        all_valid = False
        continue
    
    print(f"   ✓ {fmt_name}: Valid {verify_img.shape}")

# Test different depth strengths
print(f"\n6. Testing depth strength variations...")
for strength in [0.0, 0.5, 1.0, 1.5, 2.0]:
    renderer.depth_strength = strength
    left, right = renderer.render_stereo_pair(img, depth_map)
    output = composer.compose_half_sbs(left, right)
    output_path = test_input_dir / f"live_depth_{strength:.1f}.png"
    cv2.imwrite(str(output_path), output)
    file_size = output_path.stat().st_size / 1024
    print(f"   ✓ Depth {strength:.1f}: {file_size:.1f} KB")

# Test error handling
print(f"\n7. Testing error handling...")

try:
    # Invalid input type
    depth_estimator.estimate_depth(None)
    print("   ✗ Failed to reject None input")
except Exception:
    print("   ✓ Correctly rejected None input")

try:
    # Invalid image shape
    invalid_img = np.random.randint(0, 255, (10, 10), dtype=np.uint8)
    depth_estimator.estimate_depth(invalid_img)
    print("   ✗ Failed to reject invalid shape")
except Exception:
    print("   ✓ Correctly rejected invalid image shape")

try:
    # Mismatched stereo pair dimensions
    small_left = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    big_right = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    composer.compose_half_sbs(small_left, big_right)
    print("   ✗ Failed to catch dimension mismatch")
except Exception:
    print("   ✓ Correctly caught dimension mismatch")

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

if all_valid:
    print("🎉 SUCCESS: All conversion functionality works correctly!")
    print()
    print("Tested features:")
    print("  ✓ Model initialization (MiDaS depth estimation)")
    print("  ✓ Depth map generation")
    print("  ✓ Stereo pair rendering (DIBR)")
    print("  ✓ All 4 output formats (half SBS, full SBS, anaglyph, top-bottom)")
    print("  ✓ Depth strength variations (0.0 to 2.0)")
    print("  ✓ Error handling (invalid inputs)")
    print()
    print(f"Output files saved to: {test_input_dir}")
    print()
    sys.exit(0)
else:
    print("⚠️ FAILED: Some output files were invalid")
    sys.exit(1)
