"""
Video Encoder Module

Handles video encoding from processed frames.
Reassembles frames into video with optional audio.
"""

from pathlib import Path
from typing import Optional, List
import subprocess
import logging

logger = logging.getLogger(__name__)


class VideoEncoder:
    """Encodes frames into video."""
    
    def __init__(self, ffmpeg_handler=None, ffmpeg_path: str = None):
        """
        Initialize video encoder.
        
        Args:
            ffmpeg_handler: FFmpegHandler instance (preferred)
            ffmpeg_path: Path to FFmpeg executable (fallback)
        """
        if ffmpeg_handler is not None:
            self.ffmpeg_path = ffmpeg_handler.ffmpeg_path
        elif ffmpeg_path is not None:
            self.ffmpeg_path = ffmpeg_path
        else:
            # Try to get from installer
            try:
                from .ffmpeg_handler import FFmpegHandler
                handler = FFmpegHandler()
                self.ffmpeg_path = handler.ffmpeg_path
            except Exception:
                self.ffmpeg_path = "ffmpeg"
    
    def encode_from_frames(
        self,
        frame_dir: Path,
        output_path: Path,
        fps: float = 30.0,
        frame_pattern: str = "frame_%06d.png",
        codec: str = "libx264",
        crf: int = 18,
        preset: str = "medium",
        audio_path: Optional[Path] = None
    ) -> None:
        """
        Encode video from frames.
        
        Args:
            frame_dir: Directory containing frames
            output_path: Path for output video
            fps: Frame rate
            frame_pattern: Naming pattern for frames
            codec: Video codec to use
            crf: Constant Rate Factor (0-51, lower = better quality)
            preset: Encoding preset (ultrafast, fast, medium, slow, veryslow)
            audio_path: Optional audio file to include
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build FFmpeg command
        input_pattern = frame_dir / frame_pattern
        
        cmd = [
            self.ffmpeg_path,
            "-framerate", str(fps),
            "-i", str(input_pattern)
        ]
        
        # Add audio input if provided
        if audio_path and audio_path.exists():
            cmd.extend(["-i", str(audio_path)])
        
        # Now add output options (after all inputs)
        cmd.extend([
            "-c:v", codec,
            "-crf", str(crf),
            "-preset", preset,
            "-pix_fmt", "yuv420p"
        ])
        
        # Add audio encoding options if audio is present
        if audio_path and audio_path.exists():
            cmd.extend([
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest"  # Match shortest stream
            ])
        
        cmd.extend([
            "-hide_banner",
            "-loglevel", "error",
            "-stats",
            "-y", str(output_path)
        ])
        
        logger.info(f"Encoding video: {output_path.name}")
        logger.info(f"Settings: {codec}, CRF={crf}, preset={preset}, FPS={fps}")
        logger.info(f"FFmpeg command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg stderr: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, cmd, stderr=result.stderr)
            
            logger.info(f"Video encoded successfully: {output_path}")
            
            # Log file size
            size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Output size: {size_mb:.2f} MB")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Video encoding failed: {e}")
            raise
    
    def encode_stereo_video(
        self,
        left_frame_dir: Path,
        right_frame_dir: Path,
        output_path: Path,
        fps: float = 30.0,
        output_format: str = "half_sbs",
        frame_pattern: str = "frame_%06d.png",
        codec: str = "libx264",
        crf: int = 18,
        preset: str = "medium",
        audio_path: Optional[Path] = None
    ) -> None:
        """
        Encode stereo video from separate left/right frame directories.
        
        Args:
            left_frame_dir: Directory with left view frames
            right_frame_dir: Directory with right view frames
            output_path: Path for output video
            fps: Frame rate
            output_format: Output format (half_sbs, full_sbs, top_bottom)
            frame_pattern: Naming pattern for frames
            codec: Video codec
            crf: Constant Rate Factor
            preset: Encoding preset
            audio_path: Optional audio file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        left_pattern = left_frame_dir / frame_pattern
        right_pattern = right_frame_dir / frame_pattern
        
        # Build filter complex based on format
        if output_format == "half_sbs":
            # Scale each to 50% width, stack horizontally
            filter_complex = "[0:v]scale=iw/2:ih[left];[1:v]scale=iw/2:ih[right];[left][right]hstack"
        elif output_format == "full_sbs":
            # Stack horizontally at full resolution
            filter_complex = "[0:v][1:v]hstack"
        elif output_format == "top_bottom":
            # Scale each to 50% height, stack vertically
            filter_complex = "[0:v]scale=iw:ih/2[left];[1:v]scale=iw:ih/2[right];[left][right]vstack"
        else:
            raise ValueError(f"Unknown output format: {output_format}")
        
        cmd = [
            self.ffmpeg_path,
            "-framerate", str(fps),
            "-i", str(left_pattern),
            "-framerate", str(fps),
            "-i", str(right_pattern),
            "-filter_complex", filter_complex,
            "-c:v", codec,
            "-crf", str(crf),
            "-preset", preset,
            "-pix_fmt", "yuv420p",
            "-hide_banner",
            "-loglevel", "error",
            "-stats"
        ]
        
        if audio_path and audio_path.exists():
            cmd.extend([
                "-i", str(audio_path),
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest"
            ])
        
        cmd.extend(["-y", str(output_path)])
        
        logger.info(f"Encoding stereo video: {output_format}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg stderr: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, cmd, stderr=result.stderr)
            
            logger.info(f"Stereo video encoded: {output_path}")
            size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Output size: {size_mb:.2f} MB")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Stereo video encoding failed: {e}")
            raise

