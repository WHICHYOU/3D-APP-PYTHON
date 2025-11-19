#!/usr/bin/env python3
"""
Test Video Conversion Pipeline

Creates a synthetic test video and converts it to 3D.
Tests the complete video processing pipeline.
"""

import cv2
import numpy as np
from pathlib import Path
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_video(output_path: Path, duration: float = 5.0, fps: float = 30.0):
    """
    Create a synthetic test video with moving objects.
    
    Args:
        output_path: Path for output video
        duration: Video duration in seconds
        fps: Frame rate
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    width, height = 640, 480
    frame_count = int(duration * fps)
    
    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    logger.info(f"Creating test video: {width}x{height} @ {fps} fps, {frame_count} frames")
    
    for i in range(frame_count):
        # Create frame with gradient background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Animated gradient background
        for y in range(height):
            color_value = int(100 + 50 * np.sin(i / 10.0))
            frame[y, :] = [color_value, y * 255 // height, 150]
        
        # Moving circle (closer - darker)
        circle_x = int(width * 0.3 + 100 * np.sin(i / 10.0))
        circle_y = height // 3
        cv2.circle(frame, (circle_x, circle_y), 40, (50, 50, 150), -1)
        
        # Moving rectangle (further - lighter)
        rect_x = int(width * 0.7 - 80 * np.sin(i / 10.0))
        rect_y = height // 2
        cv2.rectangle(
            frame,
            (rect_x - 50, rect_y - 30),
            (rect_x + 50, rect_y + 30),
            (200, 200, 250),
            -1
        )
        
        # Text overlay
        text = f"Frame {i+1}/{frame_count}"
        cv2.putText(
            frame,
            text,
            (10, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        
        writer.write(frame)
        
        if (i + 1) % 30 == 0:
            logger.info(f"  Generated {i+1}/{frame_count} frames")
    
    writer.release()
    logger.info(f"✓ Test video created: {output_path}")
    logger.info(f"  Size: {output_path.stat().st_size / (1024*1024):.2f} MB")


def test_video_conversion():
    """Test the complete video conversion pipeline."""
    logger.info("=" * 60)
    logger.info("Video Conversion Pipeline Test")
    logger.info("=" * 60)
    
    # Create output directory
    output_dir = Path("test_video_output")
    output_dir.mkdir(exist_ok=True)
    
    # Step 1: Create test video
    logger.info("\n[Step 1] Creating synthetic test video...")
    test_video = output_dir / "test_input.mp4"
    create_test_video(test_video, duration=3.0, fps=24.0)
    
    # Step 2: Test conversion with different formats
    logger.info("\n[Step 2] Testing video conversions...")
    
    formats = [
        ("half_sbs", "Half Side-by-Side"),
        ("anaglyph", "Anaglyph (Red-Cyan)")
    ]
    
    for format_name, description in formats:
        logger.info(f"\n  Testing {description}...")
        output_path = output_dir / f"test_output_{format_name}.mp4"
        
        try:
            # Import here to test import paths
            sys.path.insert(0, str(Path(__file__).parent / "src"))
            from convert_video import convert_video
            
            convert_video(
                test_video,
                output_path,
                output_format=format_name,
                depth_intensity=0.75,
                use_temporal_filter=True,
                temporal_method="ema",
                keep_audio=False,
                save_intermediate=False
            )
            
            logger.info(f"  ✓ {description} conversion successful!")
            
        except Exception as e:
            logger.error(f"  ✗ {description} conversion failed: {e}")
            raise
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("✓ All video conversion tests passed!")
    logger.info(f"\nOutput files in: {output_dir.absolute()}")
    logger.info("  test_input.mp4         - Original synthetic video")
    logger.info("  test_output_half_sbs.mp4 - Half Side-by-Side 3D")
    logger.info("  test_output_anaglyph.mp4 - Anaglyph 3D")
    logger.info("\nYou can view the anaglyph video with red-cyan glasses!")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        test_video_conversion()
    except KeyboardInterrupt:
        logger.info("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
