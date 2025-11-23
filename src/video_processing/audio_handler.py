"""
Audio Handling
Extract and manage audio tracks
"""
import os
from pathlib import Path
from typing import Optional
from .ffmpeg_handler import FFmpegHandler


class AudioHandler:
    """Handle audio extraction and merging"""
    
    def __init__(self, ffmpeg_handler: Optional[FFmpegHandler] = None):
        """
        Initialize audio handler
        
        Args:
            ffmpeg_handler: FFmpeg handler instance
        """
        self.ffmpeg = ffmpeg_handler or FFmpegHandler()
    
    def extract_audio(
        self,
        video_path,
        output_path = None
    ) -> Optional[str]:
        """
        Extract audio from video
        
        Args:
            video_path: Input video path (str or Path)
            output_path: Output audio path (optional, will auto-generate, str or Path)
        
        Returns:
            Path to extracted audio file or None if no audio
        """
        # Convert to Path if string
        video_path = Path(video_path) if isinstance(video_path, str) else video_path
        
        # Get video info to check for audio
        video_info = self.ffmpeg.get_video_info(video_path)
        
        if not video_info.get('has_audio', False):
            print("No audio track found in video")
            return None
        
        # Generate output path if not provided
        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_audio.aac"
        else:
            output_path = Path(output_path) if isinstance(output_path, str) else output_path
        
        # Extract audio using FFmpegHandler's method (which doesn't exist!)
        # Need to call the correct method
        cmd = [
            self.ffmpeg.ffmpeg_path,
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "copy",  # Copy audio codec
            "-hide_banner",
            "-loglevel", "error",
            str(output_path)
        ]
        
        import subprocess
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode != 0:
                stderr = result.stderr.decode()
                if "does not contain any stream" in stderr or "No audio" in stderr:
                    logger.info("No audio track found in video")
                    return None
                else:
                    raise subprocess.CalledProcessError(result.returncode, cmd, stderr=result.stderr)
            
            logger.info(f"Audio extracted to {output_path}")
            return str(output_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio extraction failed: {e.stderr.decode()}")
            return None
    
    def merge_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> bool:
        """
        Merge audio track with video
        
        Args:
            video_path: Input video (without audio or to replace audio)
            audio_path: Audio track to merge
            output_path: Output video path
        
        Returns:
            True if successful
        """
        # TODO: Implement audio merging
        print(f"Would merge {audio_path} with {video_path}")
        return True
    
    def adjust_audio_duration(
        self,
        audio_path: str,
        target_duration: float,
        output_path: str
    ) -> bool:
        """
        Adjust audio duration to match video
        
        Args:
            audio_path: Input audio path
            target_duration: Target duration in seconds
            output_path: Output audio path
        
        Returns:
            True if successful
        """
        # TODO: Implement audio stretching/compression
        print(f"Would adjust audio to {target_duration} seconds")
        return True
    
    def has_audio(self, video_path: str) -> bool:
        """
        Check if video has audio track
        
        Args:
            video_path: Path to video
        
        Returns:
            True if video has audio
        """
        video_info = self.ffmpeg.get_video_info(video_path)
        return video_info.get('has_audio', False)
