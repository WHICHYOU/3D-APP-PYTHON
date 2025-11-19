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
        video_path: str,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Extract audio from video
        
        Args:
            video_path: Input video path
            output_path: Output audio path (optional, will auto-generate)
        
        Returns:
            Path to extracted audio file or None if no audio
        """
        # Get video info to check for audio
        video_info = self.ffmpeg.get_video_info(video_path)
        
        if not video_info.get('has_audio', False):
            print("No audio track found in video")
            return None
        
        # Generate output path if not provided
        if output_path is None:
            video_path_obj = Path(video_path)
            output_path = str(video_path_obj.parent / f"{video_path_obj.stem}_audio.aac")
        
        # Extract audio
        success = self.ffmpeg.extract_audio(video_path, output_path)
        
        if success:
            return output_path
        else:
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
