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
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize video encoder.
        
        Args:
            ffmpeg_path: Path to FFmpeg executable
        """
        self.ffmpeg_path = ffmpeg_path
    
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
            "-i", str(input_pattern),
            "-c:v", codec,
            "-crf", str(crf),
            "-preset", preset,
            "-pix_fmt", "yuv420p",  # Compatibility
            "-hide_banner",
            "-loglevel", "error",
            "-stats"
        ]
        
        # Add audio if provided
        if audio_path and audio_path.exists():
            cmd.extend([
                "-i", str(audio_path),
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest"  # Match shortest stream
            ])
        
        cmd.extend(["-y", str(output_path)])  # Overwrite output
        
        logger.info(f"Encoding video: {output_path.name}")
        logger.info(f"Settings: {codec}, CRF={crf}, preset={preset}, FPS={fps}")
        
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
import os
from pathlib import Path
from typing import Optional, Callable, Dict
from .ffmpeg_handler import FFmpegHandler


class VideoEncoder:
    """Encode frames to video file"""
    
    # Quality presets
    QUALITY_PRESETS = {
        'ultra': {'crf': 18, 'preset': 'slow'},
        'high': {'crf': 23, 'preset': 'medium'},
        'medium': {'crf': 28, 'preset': 'fast'},
        'low': {'crf': 32, 'preset': 'veryfast'},
    }
    
    def __init__(self, ffmpeg_handler: Optional[FFmpegHandler] = None):
        """
        Initialize video encoder
        
        Args:
            ffmpeg_handler: FFmpeg handler instance
        """
        self.ffmpeg = ffmpeg_handler or FFmpegHandler()
    
    def encode(
        self,
        frames_dir: str,
        output_path: str,
        fps: int = 30,
        quality: str = 'high',
        audio_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """
        Encode frames to video
        
        Args:
            frames_dir: Directory containing frames
            output_path: Output video path
            fps: Output FPS
            quality: Quality preset ('ultra', 'high', 'medium', 'low')
            audio_path: Optional audio track
            progress_callback: Progress callback function
        
        Returns:
            True if successful
        """
        # Get quality settings
        preset = self.QUALITY_PRESETS.get(quality, self.QUALITY_PRESETS['high'])
        
        # Build frame pattern
        frame_pattern = os.path.join(frames_dir, 'frame_%06d.png')
        
        if progress_callback:
            progress_callback(0.0)
        
        # Encode video
        success = self.ffmpeg.encode_video(
            input_pattern=frame_pattern,
            output_path=output_path,
            fps=fps,
            codec='libx264',
            audio_path=audio_path,
            crf=preset['crf']
        )
        
        if progress_callback:
            progress_callback(1.0)
        
        return success
    
    def encode_stereo_sbs(
        self,
        left_frames_dir: str,
        right_frames_dir: str,
        output_path: str,
        fps: int = 30,
        mode: str = 'half',
        quality: str = 'high',
        audio_path: Optional[str] = None
    ) -> bool:
        """
        Encode side-by-side stereoscopic video
        
        Args:
            left_frames_dir: Directory with left eye frames
            right_frames_dir: Directory with right eye frames
            output_path: Output video path
            fps: Output FPS
            mode: 'half' or 'full' SBS
            quality: Quality preset
            audio_path: Optional audio track
        
        Returns:
            True if successful
        """
        # TODO: Implement SBS composition and encoding
        print(f"Would encode {mode} SBS video to {output_path}")
        return True
    
    def estimate_output_size(
        self,
        frame_count: int,
        width: int,
        height: int,
        fps: int,
        quality: str = 'high'
    ) -> int:
        """
        Estimate output video file size
        
        Args:
            frame_count: Number of frames
            width: Frame width
            height: Frame height
            fps: Target FPS
            quality: Quality preset
        
        Returns:
            Estimated size in bytes
        """
        # Rough estimation based on bitrate
        duration = frame_count / fps
        
        # Approximate bitrates for different qualities (Mbps)
        bitrates = {
            'ultra': 10,
            'high': 6,
            'medium': 3,
            'low': 1.5,
        }
        
        bitrate = bitrates.get(quality, 6)
        
        # Adjust for resolution
        resolution_factor = (width * height) / (1920 * 1080)
        adjusted_bitrate = bitrate * resolution_factor
        
        # Calculate size in bytes
        size_mb = (adjusted_bitrate * duration) / 8
        size_bytes = int(size_mb * 1024 * 1024)
        
        return size_bytes
    
    def get_recommended_settings(
        self,
        frame_count: int,
        width: int,
        height: int,
        target_size_mb: Optional[int] = None
    ) -> Dict:
        """
        Get recommended encoding settings
        
        Args:
            frame_count: Number of frames
            width: Frame width
            height: Frame height
            target_size_mb: Target file size in MB (optional)
        
        Returns:
            Dictionary of recommended settings
        """
        # Default to high quality
        recommended_quality = 'high'
        
        # If target size specified, find appropriate quality
        if target_size_mb:
            for quality in ['ultra', 'high', 'medium', 'low']:
                estimated_size = self.estimate_output_size(
                    frame_count, width, height, 30, quality
                )
                estimated_mb = estimated_size / (1024 * 1024)
                
                if estimated_mb <= target_size_mb:
                    recommended_quality = quality
                    break
        
        return {
            'quality': recommended_quality,
            'fps': 30,
            'codec': 'libx264',
            **self.QUALITY_PRESETS[recommended_quality]
        }
