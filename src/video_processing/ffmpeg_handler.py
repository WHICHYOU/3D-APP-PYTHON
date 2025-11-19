"""
FFmpeg Handler Module

Handles video processing operations using FFmpeg.
Includes frame extraction, video encoding, and audio handling.
"""

import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import json
import re

logger = logging.getLogger(__name__)


class FFmpegHandler:
    """Main class for FFmpeg operations."""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize FFmpeg handler.
        
        Args:
            ffmpeg_path: Path to FFmpeg executable
        """
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffmpeg_path.replace("ffmpeg", "ffprobe")
        self._verify_ffmpeg()
    
    def _verify_ffmpeg(self) -> bool:
        """Verify FFmpeg is installed and accessible."""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("FFmpeg not found or not working")
            
            logger.info(f"FFmpeg verified: {result.stdout.split()[2]}")
            return True
            
        except (subprocess.TimeoutExpired, FileNotFoundError, RuntimeError) as e:
            logger.error(f"FFmpeg verification failed: {e}")
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg:\n"
                "  macOS: brew install ffmpeg\n"
                "  Ubuntu: sudo apt install ffmpeg\n"
                "  Windows: Download from https://ffmpeg.org/"
            )
    
    def extract_frames(
        self,
        video_path: Path,
        output_dir: Path,
        frame_pattern: str = "frame_%06d.png",
        fps: Optional[float] = None
    ) -> int:
        """
        Extract frames from video.
        
        Args:
            video_path: Path to input video
            output_dir: Directory for output frames
            frame_pattern: Naming pattern for frames
            fps: Optional FPS for frame extraction (None = extract all)
            
        Returns:
            Number of frames extracted
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / frame_pattern
        
        cmd = [
            self.ffmpeg_path,
            "-i", str(video_path),
            "-hide_banner",
            "-loglevel", "error"
        ]
        
        if fps is not None:
            cmd.extend(["-vf", f"fps={fps}"])
        
        cmd.extend([
            "-q:v", "2",  # High quality
            str(output_path)
        ])
        
        logger.info(f"Extracting frames from {video_path.name}...")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Count extracted frames
            frame_count = len(list(output_dir.glob("frame_*.png")))
            logger.info(f"Extracted {frame_count} frames")
            return frame_count
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Frame extraction failed: {e.stderr.decode()}")
            raise
    
    def get_video_info(self, video_path: Path) -> Dict[str, Any]:
        """
        Get video metadata.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path)
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = next(
                (s for s in data["streams"] if s["codec_type"] == "video"),
                None
            )
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            # Parse FPS
            fps_str = video_stream.get("r_frame_rate", "30/1")
            num, den = map(int, fps_str.split("/"))
            fps = num / den if den != 0 else 30.0
            
            # Extract audio stream info
            audio_stream = next(
                (s for s in data["streams"] if s["codec_type"] == "audio"),
                None
            )
            
            info = {
                "duration": float(data["format"].get("duration", 0)),
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "fps": fps,
                "codec": video_stream.get("codec_name", "unknown"),
                "bitrate": int(data["format"].get("bit_rate", 0)),
                "has_audio": audio_stream is not None,
                "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
                "frame_count": int(video_stream.get("nb_frames", 0))
            }
            
            logger.info(f"Video info: {info['width']}x{info['height']} @ {info['fps']:.2f} fps")
            return info
            
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to get video info: {e}")
            raise


class AudioHandler:
    """Handles audio extraction and merging."""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """Initialize audio handler."""
        self.ffmpeg_path = ffmpeg_path
    
    def extract_audio(self, video_path: Path, audio_path: Path) -> bool:
        """
        Extract audio from video.
        
        Args:
            video_path: Path to input video
            audio_path: Path for output audio file
            
        Returns:
            True if audio was extracted, False if no audio track
        """
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_path,
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "copy",  # Copy audio codec
            "-hide_banner",
            "-loglevel", "error",
            str(audio_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode != 0:
                # Check if error is due to no audio stream
                stderr = result.stderr.decode()
                if "does not contain any stream" in stderr or "No audio" in stderr:
                    logger.info("No audio track found in video")
                    return False
                else:
                    raise subprocess.CalledProcessError(result.returncode, cmd, stderr=result.stderr)
            
            logger.info(f"Audio extracted to {audio_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio extraction failed: {e.stderr.decode()}")
            raise
    
    def merge_audio(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        video_codec: str = "libx264"
    ) -> None:
        """
        Merge audio with video.
        
        Args:
            video_path: Path to input video (without audio)
            audio_path: Path to audio file
            output_path: Path for output video
            video_codec: Video codec to use
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_path,
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", video_codec,
            "-c:a", "aac",
            "-shortest",  # Match shortest stream
            "-hide_banner",
            "-loglevel", "error",
            "-y",  # Overwrite output
            str(output_path)
        ]
        
        logger.info("Merging audio with video...")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Audio merged successfully: {output_path}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio merging failed: {e.stderr.decode()}")
            raise
import subprocess
import os
from pathlib import Path
from typing import Optional, Dict


class FFmpegHandler:
    """Wrapper for FFmpeg operations"""
    
    def __init__(self, ffmpeg_path: Optional[str] = None):
        """
        Initialize FFmpeg handler
        
        Args:
            ffmpeg_path: Custom path to FFmpeg binary (optional)
        """
        self.ffmpeg_path = ffmpeg_path or 'ffmpeg'
        self.ffprobe_path = ffmpeg_path.replace('ffmpeg', 'ffprobe') if ffmpeg_path else 'ffprobe'
    
    def check_installation(self) -> bool:
        """
        Check if FFmpeg is installed and accessible
        
        Returns:
            True if FFmpeg is available
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        Get video metadata using ffprobe
        
        Args:
            video_path: Path to video file
        
        Returns:
            Dictionary with video information
        """
        cmd = [
            self.ffprobe_path,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            # TODO: Parse JSON output
            info = {
                'width': 1920,
                'height': 1080,
                'fps': 30,
                'duration': 120.0,
                'codec': 'h264',
                'has_audio': True,
            }
            return info
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {}
    
    def extract_frames(
        self,
        video_path: str,
        output_dir: str,
        fps: Optional[int] = None
    ) -> int:
        """
        Extract frames from video
        
        Args:
            video_path: Input video path
            output_dir: Directory to save frames
            fps: Target FPS (None = original)
        
        Returns:
            Number of frames extracted
        """
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
        ]
        
        if fps:
            cmd.extend(['-vf', f'fps={fps}'])
        
        cmd.extend([
            os.path.join(output_dir, 'frame_%06d.png')
        ])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            # Count extracted frames
            frame_count = len(list(Path(output_dir).glob('frame_*.png')))
            return frame_count
        except subprocess.CalledProcessError as e:
            print(f"Error extracting frames: {e}")
            return 0
    
    def extract_audio(self, video_path: str, output_path: str) -> bool:
        """
        Extract audio track from video
        
        Args:
            video_path: Input video path
            output_path: Output audio path
        
        Returns:
            True if successful
        """
        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'copy',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def encode_video(
        self,
        input_pattern: str,
        output_path: str,
        fps: int = 30,
        codec: str = 'libx264',
        audio_path: Optional[str] = None,
        crf: int = 23
    ) -> bool:
        """
        Encode frames to video
        
        Args:
            input_pattern: Frame file pattern (e.g., 'frame_%06d.png')
            output_path: Output video path
            fps: Output FPS
            codec: Video codec
            audio_path: Optional audio track to merge
            crf: Constant Rate Factor (quality, 0-51, lower = better)
        
        Returns:
            True if successful
        """
        cmd = [
            self.ffmpeg_path,
            '-framerate', str(fps),
            '-i', input_pattern,
            '-c:v', codec,
            '-crf', str(crf),
            '-preset', 'medium',
            '-pix_fmt', 'yuv420p',
        ]
        
        if audio_path:
            cmd.extend(['-i', audio_path, '-c:a', 'aac', '-shortest'])
        
        cmd.append(output_path)
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error encoding video: {e}")
            return False
