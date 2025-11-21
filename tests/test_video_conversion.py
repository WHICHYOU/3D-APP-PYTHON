#!/usr/bin/env python3
"""
Video conversion smoke test
Creates a tiny test video (3 frames) and runs conversion pipeline
"""
import sys
import numpy as np
import cv2
from pathlib import Path
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_core.depth_estimation import DepthEstimator
from src.rendering.dibr_renderer import DIBRRenderer
from src.rendering.sbs_composer import SBSComposer
from src.video_processing.ffmpeg_handler import FFmpegHandler
from src.video_processing.encoder import VideoEncoder
from src.ai_core.temporal_filter import TemporalFilter

def create_test_video(output_path, num_frames=3):
    """Create a simple test video with moving circle."""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(output_path), fourcc, 10.0, (320, 240))
    
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
        
        writer.write(frame)
    
    writer.release()
    print(f"Created test video: {output_path} ({num_frames} frames, 320x240)")

def main():
    print("=" * 60)
    print("VIDEO CONVERSION SMOKE TEST")
    print("=" * 60)
    
    # Setup paths
    test_dir = Path(__file__).parent
    test_video_path = test_dir / "test_input.mp4"
    work_dir = test_dir / "temp_video_test"
    frames_dir = work_dir / "frames"
    output_frames_dir = work_dir / "output_frames"
    output_video = test_dir / "output" / "test_output_video.mp4"
    
    # Clean and create directories
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(exist_ok=True)
    frames_dir.mkdir(exist_ok=True)
    output_frames_dir.mkdir(exist_ok=True)
    output_video.parent.mkdir(exist_ok=True)
    
    # Create test video
    print("\n1. Creating test video...")
    create_test_video(test_video_path, num_frames=3)
    
    # Initialize models
    print("\n2. Initializing AI models...")
    estimator = DepthEstimator()
    renderer = DIBRRenderer(ipd=65)
    composer = SBSComposer()
    temporal_filter = TemporalFilter(window_size=3, alpha=0.7)
    print("   ✓ Models initialized")
    
    # Extract frames
    print("\n3. Extracting frames with FFmpeg...")
    ffmpeg = FFmpegHandler()
    video_info = ffmpeg.get_video_info(test_video_path)
    print(f"   Video info: {video_info['width']}x{video_info['height']}, {video_info['fps']} fps")
    
    frame_count = ffmpeg.extract_frames(
        test_video_path,
        frames_dir,
        frame_pattern="frame_%03d.png"
    )
    print(f"   ✓ Extracted {frame_count} frames")
    
    # Process frames
    print("\n4. Processing frames...")
    frame_files = sorted(frames_dir.glob("frame_*.png"))
    
    for i, frame_path in enumerate(frame_files, 1):
        print(f"   Frame {i}/{len(frame_files)}: {frame_path.name}")
        
        # Load frame
        frame_bgr = cv2.imread(str(frame_path))
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        
        # Estimate depth with temporal filtering
        depth_map = estimator.estimate_depth(frame_rgb, normalize=True)
        depth_map = temporal_filter.filter(depth_map, method="ema")
        
        # Render stereo
        left_view, right_view = renderer.render_stereo_pair(
            frame_rgb, depth_map, depth_intensity=0.75
        )
        
        # Compose (half SBS)
        output = composer.compose_half_sbs(left_view, right_view)
        
        # Save output frame
        output_frame_path = output_frames_dir / f"frame_{i:03d}.png"
        output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_frame_path), output_bgr)
        print(f"      → {output_frame_path.name}")
    
    # Encode video
    print("\n5. Encoding output video...")
    encoder = VideoEncoder()
    
    # Get first frame dimensions
    first_frame = cv2.imread(str(output_frames_dir / "frame_001.png"))
    height, width = first_frame.shape[:2]
    
    encoder.encode_frames_to_video(
        output_frames_dir,
        output_video,
        fps=video_info['fps'],
        width=width,
        height=height,
        codec='libx264',
        quality='high'
    )
    
    if output_video.exists():
        file_size = output_video.stat().st_size / 1024  # KB
        print(f"   ✓ Output video: {output_video.name} ({file_size:.1f} KB)")
    else:
        print("   ✗ Failed to create output video")
        return 1
    
    # Cleanup
    print("\n6. Cleaning up...")
    shutil.rmtree(work_dir)
    test_video_path.unlink()
    print("   ✓ Temporary files removed")
    
    print("\n" + "=" * 60)
    print("✓ VIDEO CONVERSION SMOKE TEST PASSED")
    print("=" * 60)
    print(f"\nOutput video: {output_video}")
    print("You can play it:")
    print(f"  open {output_video}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
