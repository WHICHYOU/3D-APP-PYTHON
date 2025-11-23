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
    
    def __init__(self, ffmpeg_path: Optional[str] = None):
        """
        Initialize FFmpeg handler.
        
        Args:
            ffmpeg_path: Path to FFmpeg executable (None = auto-detect/install)
        """
        if ffmpeg_path is None:
            # Try to find FFmpeg in PATH or common locations first (prioritize Homebrew)
            self.ffmpeg_path = self._find_ffmpeg()
            
            # If not found, try automatic installation as fallback
            if not self.ffmpeg_path:
                try:
                    from ..utils.ffmpeg_installer import get_ffmpeg_path
                    self.ffmpeg_path = get_ffmpeg_path()
                    logger.info(f"Using downloaded FFmpeg: {self.ffmpeg_path}")
                except Exception as e:
                    logger.error(f"Could not find or install FFmpeg: {e}")
                    raise RuntimeError(
                        "FFmpeg not found. Please install via Homebrew:\n"
                        "brew install ffmpeg"
                    )
        else:
            self.ffmpeg_path = ffmpeg_path
        
        # Get ffprobe path from same directory
        ffmpeg_dir = Path(self.ffmpeg_path).parent
        ffprobe_name = "ffprobe.exe" if Path(self.ffmpeg_path).suffix == ".exe" else "ffprobe"
        self.ffprobe_path = str(ffmpeg_dir / ffprobe_name)
        
        self._verify_ffmpeg()
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Try to find FFmpeg in common locations."""
        import shutil
        import platform
        
        # Try PATH first
        ffmpeg_cmd = shutil.which("ffmpeg")
        if ffmpeg_cmd:
            logger.info(f"Found FFmpeg in PATH: {ffmpeg_cmd}")
            return ffmpeg_cmd
        
        # Try common Homebrew locations on macOS (prioritize these)
        if platform.system() == "Darwin":
            homebrew_paths = [
                "/opt/homebrew/bin/ffmpeg",  # Apple Silicon
                "/usr/local/bin/ffmpeg",      # Intel Mac
            ]
            for path in homebrew_paths:
                if Path(path).exists():
                    logger.info(f"Found FFmpeg at: {path}")
                    return path
        
        # Try common Linux locations
        elif platform.system() == "Linux":
            linux_paths = [
                "/usr/bin/ffmpeg",
                "/usr/local/bin/ffmpeg",
            ]
            for path in linux_paths:
                if Path(path).exists():
                    logger.info(f"Found FFmpeg at: {path}")
                    return path
        
        # Try common Windows locations
        elif platform.system() == "Windows":
            windows_paths = [
                "C:\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            ]
            for path in windows_paths:
                if Path(path).exists():
                    logger.info(f"Found FFmpeg at: {path}")
                    return path
        
        # Not found - return default and let verification fail with instructions
        return "ffmpeg"
    
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
                raise RuntimeError("FFmpeg not working properly")
            
            # Extract version
            version_line = result.stdout.split('\n')[0]
            logger.info(f"FFmpeg verified: {version_line}")
            return True
            
        except (subprocess.TimeoutExpired, FileNotFoundError, RuntimeError) as e:
            logger.error(f"FFmpeg verification failed: {e}")
            
            import platform
            system = platform.system()
            
            install_msg = (
                "\n╔════════════════════════════════════════════════════════════╗\n"
                "║         VIDEO CONVERSION REQUIRES FFMPEG                   ║\n"
                "╠════════════════════════════════════════════════════════════╣\n"
                "║                                                            ║\n"
            )
            
            if system == "Darwin":
                install_msg += (
                    "║  macOS Installation:                                       ║\n"
                    "║  1. Install Homebrew (if not installed):                  ║\n"
                    "║     /bin/bash -c \"$(curl -fsSL https://...brew.sh)\"       ║\n"
                    "║  2. Install FFmpeg:                                        ║\n"
                    "║     brew install ffmpeg                                    ║\n"
                )
            elif system == "Linux":
                install_msg += (
                    "║  Linux Installation:                                       ║\n"
                    "║  Ubuntu/Debian:                                            ║\n"
                    "║     sudo apt update && sudo apt install ffmpeg             ║\n"
                    "║  Fedora:                                                   ║\n"
                    "║     sudo dnf install ffmpeg                                ║\n"
                )
            elif system == "Windows":
                install_msg += (
                    "║  Windows Installation:                                     ║\n"
                    "║  1. Download from: https://ffmpeg.org/download.html       ║\n"
                    "║  2. Extract to C:\\ffmpeg\\                                 ║\n"
                    "║  3. Add C:\\ffmpeg\\bin to PATH                             ║\n"
                )
            
            install_msg += (
                "║                                                            ║\n"
                "║  After installation, restart this application.             ║\n"
                "║                                                            ║\n"
                "║  Note: Image conversion works without FFmpeg.              ║\n"
                "║        Only video conversion requires FFmpeg.              ║\n"
                "╚════════════════════════════════════════════════════════════╝\n"
            )
            
            raise RuntimeError(install_msg)
    
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
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get video info: {e}")
            raise



