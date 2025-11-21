#!/usr/bin/env python3
"""
Simple video frame processing test (without FFmpeg)
Tests frame-by-frame conversion with temporal filtering
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
from src.ai_core.temporal_filter import TemporalFilter

def create_test_frames(output_dir, num_frames=3):
    """Create test frames simulating video frames."""
    frames = []
    for i in range(num_frames):
        # Create frame with moving circle
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        
        # Blue gradient background
        for y in range(240):
            intensity = int((y / 240) * 200)
            frame[y, :] = [intensity, intensity, 255]
        
        # Moving yellow circle
        x_pos = 50 + i * 90  # Move right each frame
        cv2.circle(frame, (x_pos, 120), 40, (255, 255, 0), -1)
        
        frame_path = output_dir / f"frame_{i+1:03d}.png"
        cv2.imwrite(str(frame_path), frame)
        frames.append(frame)
    
    print(f"Created {num_frames} test frames in {output_dir}")
    return frames

def main():
    print("=" * 60)
    print("VIDEO FRAME PROCESSING TEST")
    print("=" * 60)
    
    # Setup paths
    test_dir = Path(__file__).parent
    frames_dir = test_dir / "temp_frames"
    output_dir = test_dir / "output"
    
    frames_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Create test frames
    print("\n1. Creating test frames...")
    frames_bgr = create_test_frames(frames_dir, num_frames=3)
    
    # Initialize models
    print("\n2. Initializing AI models...")
    estimator = DepthEstimator()
    renderer = DIBRRenderer(ipd=65)
    composer = SBSComposer()
    temporal_filter = TemporalFilter(window_size=3, alpha=0.7)
    print("   ✓ Models initialized")
    
    # Process frames with temporal filtering
    print("\n3. Processing frames with temporal filtering...")
    frame_files = sorted(frames_dir.glob("frame_*.png"))
    
    for i, frame_path in enumerate(frame_files, 1):
        print(f"   Frame {i}/{len(frame_files)}: {frame_path.name}")
        
        # Load frame
        frame_bgr = cv2.imread(str(frame_path))
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        
        # Estimate depth with temporal filtering
        depth_map = estimator.estimate_depth(frame_rgb, normalize=True)
        depth_filtered = temporal_filter.filter(depth_map)
        
        print(f"      Depth: min={depth_map.min():.3f}, max={depth_map.max():.3f}, "
              f"filtered_mean={depth_filtered.mean():.3f}")
        
        # Render stereo
        left_view, right_view = renderer.render_stereo_pair(
            frame_rgb, depth_filtered, depth_intensity=0.75
        )
        
        # Compose (half SBS)
        output = composer.compose_half_sbs(left_view, right_view)
        
        # Save output frame
        output_path = output_dir / f"video_frame_{i:03d}_sbs.png"
        output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_path), output_bgr)
        
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"      → {output_path.name} ({file_size:.1f} KB)")
    
    # Cleanup
    print("\n4. Cleaning up...")
    import shutil
    shutil.rmtree(frames_dir)
    print("   ✓ Temporary frames removed")
    
    print("\n" + "=" * 60)
    print("✓ VIDEO FRAME PROCESSING TEST PASSED")
    print("=" * 60)
    print(f"\nProcessed frames saved in: {output_dir}")
    print("\nKey features tested:")
    print("  ✓ Frame-by-frame depth estimation")
    print("  ✓ Temporal filtering (EMA smoothing)")
    print("  ✓ Stereo rendering")
    print("  ✓ SBS composition")
    print("\nYou can view outputs:")
    print(f"  open {output_dir}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
