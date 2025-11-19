#!/usr/bin/env python3
"""
Video to 3D Converter

Command-line tool for converting 2D videos to stereoscopic 3D formats.
Supports Half Side-by-Side, Full Side-by-Side, Anaglyph, and Top-Bottom formats.
"""

import argparse
import logging
import sys
from pathlib import Path
import shutil
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai_core.depth_estimation import DepthEstimator
from src.ai_core.temporal_filter import TemporalFilter
from src.rendering.dibr_renderer import DIBRRenderer
from src.rendering.sbs_composer import SBSComposer
from src.video_processing.ffmpeg_handler import FFmpegHandler, AudioHandler
from src.video_processing.encoder import VideoEncoder
import cv2
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_video(
    input_path: Path,
    output_path: Path,
    output_format: str = "half_sbs",
    depth_intensity: float = 0.75,
    use_temporal_filter: bool = True,
    temporal_method: str = "ema",
    fps: float = None,
    keep_audio: bool = True,
    save_intermediate: bool = False
):
    """
    Convert a 2D video to stereoscopic 3D.
    
    Args:
        input_path: Path to input video
        output_path: Path for output video
        output_format: Output format (half_sbs, full_sbs, anaglyph, top_bottom)
        depth_intensity: Depth effect strength (0.0-1.0)
        use_temporal_filter: Apply temporal filtering to reduce flickering
        temporal_method: Temporal filter method (ema, median, gaussian)
        fps: Optional output FPS (None = same as input)
        keep_audio: Preserve audio track
        save_intermediate: Save intermediate frames
    """
    logger.info("=" * 60)
    logger.info("2D to 3D Video Conversion")
    logger.info("=" * 60)
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")
    logger.info(f"Format: {output_format}")
    logger.info(f"Depth Intensity: {depth_intensity}")
    logger.info(f"Temporal Filtering: {use_temporal_filter} ({temporal_method})")
    
    start_time = time.time()
    
    # Create working directory
    work_dir = Path("temp_video_work")
    frames_dir = work_dir / "frames"
    output_frames_dir = work_dir / "output_frames"
    audio_path = work_dir / "audio.aac"
    
    try:
        work_dir.mkdir(exist_ok=True)
        frames_dir.mkdir(exist_ok=True)
        output_frames_dir.mkdir(exist_ok=True)
        
        # Step 1: Get video information
        logger.info("\n[1/6] Analyzing video...")
        ffmpeg = FFmpegHandler()
        video_info = ffmpeg.get_video_info(input_path)
        
        logger.info(f"  Resolution: {video_info['width']}x{video_info['height']}")
        logger.info(f"  FPS: {video_info['fps']:.2f}")
        logger.info(f"  Duration: {video_info['duration']:.2f}s")
        logger.info(f"  Codec: {video_info['codec']}")
        logger.info(f"  Has Audio: {video_info['has_audio']}")
        
        output_fps = fps or video_info['fps']
        
        # Step 2: Extract audio if present
        has_audio = False
        if keep_audio and video_info['has_audio']:
            logger.info("\n[2/6] Extracting audio...")
            audio_handler = AudioHandler()
            has_audio = audio_handler.extract_audio(input_path, audio_path)
        else:
            logger.info("\n[2/6] Skipping audio extraction")
        
        # Step 3: Extract frames
        logger.info("\n[3/6] Extracting frames...")
        frame_count = ffmpeg.extract_frames(
            input_path,
            frames_dir,
            frame_pattern="frame_%06d.png",
            fps=output_fps
        )
        logger.info(f"  Extracted {frame_count} frames")
        
        # Step 4: Initialize processing pipeline
        logger.info("\n[4/6] Initializing AI models...")
        depth_estimator = DepthEstimator()
        dibr_renderer = DIBRRenderer()
        sbs_composer = SBSComposer()
        
        if use_temporal_filter:
            temporal_filter = TemporalFilter(window_size=3, alpha=0.7)
        
        # Step 5: Process frames
        logger.info(f"\n[5/6] Processing {frame_count} frames...")
        logger.info("  This may take a while depending on your hardware...")
        
        frame_files = sorted(frames_dir.glob("frame_*.png"))
        
        for i, frame_path in enumerate(frame_files, 1):
            # Load frame
            frame_bgr = cv2.imread(str(frame_path))
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            
            # Estimate depth
            depth_map = depth_estimator.estimate_depth(frame_rgb)
            
            # Apply temporal filtering
            if use_temporal_filter:
                depth_map = temporal_filter.filter(depth_map, method=temporal_method)
            
            # Render stereo pair
            left_view, right_view = dibr_renderer.render_stereo_pair(
                frame_rgb,
                depth_map,
                depth_intensity=depth_intensity
            )
            
            # Compose output format
            if output_format == "half_sbs":
                output = sbs_composer.compose_half_sbs(left_view, right_view)
            elif output_format == "full_sbs":
                output = sbs_composer.compose_full_sbs(left_view, right_view)
            elif output_format == "anaglyph":
                output = sbs_composer.compose_anaglyph(left_view, right_view)
            elif output_format == "top_bottom":
                output = sbs_composer.compose_top_bottom(left_view, right_view, half_resolution=True)
            else:
                raise ValueError(f"Unknown output format: {output_format}")
            
            # Save output frame
            output_path_frame = output_frames_dir / frame_path.name
            output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_path_frame), output_bgr)
            
            # Progress update
            if i % 10 == 0 or i == frame_count:
                elapsed = time.time() - start_time
                fps_rate = i / elapsed
                eta = (frame_count - i) / fps_rate if fps_rate > 0 else 0
                logger.info(f"  Progress: {i}/{frame_count} ({i*100//frame_count}%) | "
                          f"Speed: {fps_rate:.2f} fps | ETA: {eta:.0f}s")
        
        # Step 6: Encode video
        logger.info("\n[6/6] Encoding final video...")
        encoder = VideoEncoder()
        encoder.encode_from_frames(
            output_frames_dir,
            output_path,
            fps=output_fps,
            frame_pattern="frame_%06d.png",
            codec="libx264",
            crf=18,
            preset="medium",
            audio_path=audio_path if has_audio else None
        )
        
        # Done!
        total_time = time.time() - start_time
        logger.info("\n" + "=" * 60)
        logger.info("✓ Conversion complete!")
        logger.info(f"  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        logger.info(f"  Output: {output_path}")
        logger.info(f"  File size: {output_path.stat().st_size / (1024*1024):.2f} MB")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n✗ Conversion failed: {e}")
        raise
    
    finally:
        # Cleanup
        if not save_intermediate and work_dir.exists():
            logger.info("\nCleaning up temporary files...")
            shutil.rmtree(work_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Convert 2D videos to stereoscopic 3D formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion to Half Side-by-Side
  python convert_video.py input.mp4 output_3d.mp4
  
  # Full Side-by-Side with stronger depth
  python convert_video.py input.mp4 output.mp4 --format full_sbs --depth-intensity 90
  
  # Anaglyph (red-cyan) for testing
  python convert_video.py input.mp4 output.mp4 --format anaglyph
  
  # Without temporal filtering (faster but more flickering)
  python convert_video.py input.mp4 output.mp4 --no-temporal-filter
  
  # Save intermediate frames for debugging
  python convert_video.py input.mp4 output.mp4 --save-intermediate

Output Formats:
  half_sbs    - Half Side-by-Side (VR standard, 50% width per eye)
  full_sbs    - Full Side-by-Side (100% width per eye)
  anaglyph    - Red-Cyan anaglyph (for red-cyan glasses)
  top_bottom  - Top-Bottom stereoscopic (50% height per eye)
        """
    )
    
    parser.add_argument("input", type=Path, help="Input video file")
    parser.add_argument("output", type=Path, help="Output video file")
    
    parser.add_argument(
        "--format",
        choices=["half_sbs", "full_sbs", "anaglyph", "top_bottom"],
        default="half_sbs",
        help="Output format (default: half_sbs)"
    )
    
    parser.add_argument(
        "--depth-intensity",
        type=float,
        default=75,
        metavar="N",
        help="Depth effect strength 0-100 (default: 75)"
    )
    
    parser.add_argument(
        "--no-temporal-filter",
        action="store_true",
        help="Disable temporal filtering (faster but more flickering)"
    )
    
    parser.add_argument(
        "--temporal-method",
        choices=["ema", "median", "gaussian"],
        default="ema",
        help="Temporal filter method (default: ema)"
    )
    
    parser.add_argument(
        "--fps",
        type=float,
        default=None,
        help="Output FPS (default: same as input)"
    )
    
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Don't include audio in output"
    )
    
    parser.add_argument(
        "--save-intermediate",
        action="store_true",
        help="Keep intermediate frames for debugging"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)
    
    # Normalize depth intensity to 0-1
    depth_intensity = args.depth_intensity / 100.0
    if not 0 <= depth_intensity <= 1:
        logger.error("Depth intensity must be between 0 and 100")
        sys.exit(1)
    
    # Convert video
    try:
        convert_video(
            args.input,
            args.output,
            output_format=args.format,
            depth_intensity=depth_intensity,
            use_temporal_filter=not args.no_temporal_filter,
            temporal_method=args.temporal_method,
            fps=args.fps,
            keep_audio=not args.no_audio,
            save_intermediate=args.save_intermediate
        )
    except KeyboardInterrupt:
        logger.info("\n\nConversion cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
