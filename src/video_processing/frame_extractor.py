"""
Frame Extraction
High-level frame extraction with progress tracking
"""
import os
from pathlib import Path
from typing import Callable, Optional
from .ffmpeg_handler import FFmpegHandler


class FrameExtractor:
    """Extract frames from video with progress tracking"""
    
    def __init__(self, ffmpeg_handler: Optional[FFmpegHandler] = None):
        """
        Initialize frame extractor
        
        Args:
            ffmpeg_handler: FFmpeg handler instance
        """
        self.ffmpeg = ffmpeg_handler or FFmpegHandler()
    
    def extract(
        self,
        video_path: str,
        output_dir: str,
        fps: Optional[int] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> dict:
        """
        Extract frames from video
        
        Args:
            video_path: Input video path
            output_dir: Directory to save frames
            fps: Target FPS (None = original)
            progress_callback: Callback function(progress: float) for progress updates
        
        Returns:
            Dictionary with extraction results
        """
        # Get video info
        video_info = self.ffmpeg.get_video_info(video_path)
        total_frames = int(video_info.get('duration', 0) * video_info.get('fps', 30))
        
        # Extract frames
        if progress_callback:
            progress_callback(0.0)
        
        frame_count = self.ffmpeg.extract_frames(video_path, output_dir, fps)
        
        if progress_callback:
            progress_callback(1.0)
        
        return {
            'frame_count': frame_count,
            'output_dir': output_dir,
            'fps': fps or video_info.get('fps', 30),
            'video_info': video_info,
        }
    
    def extract_key_frames(
        self,
        video_path: str,
        output_dir: str,
        threshold: float = 0.3
    ) -> int:
        """
        Extract only key frames (scene changes)
        
        Args:
            video_path: Input video path
            output_dir: Output directory
            threshold: Scene change detection threshold (0-1)
        
        Returns:
            Number of key frames extracted
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # FFmpeg scene detection
        cmd_args = [
            '-i', video_path,
            '-vf', f'select=gt(scene\\,{threshold})',
            '-vsync', 'vfr',
            os.path.join(output_dir, 'keyframe_%06d.png')
        ]
        
        # TODO: Execute FFmpeg command
        print(f"Would extract key frames with threshold {threshold}")
        
        return 0
    
    def estimate_extraction_time(self, video_path: str) -> float:
        """
        Estimate time needed for frame extraction
        
        Args:
            video_path: Path to video
        
        Returns:
            Estimated time in seconds
        """
        video_info = self.ffmpeg.get_video_info(video_path)
        duration = video_info.get('duration', 0)
        
        # Rough estimate: ~0.5x realtime for extraction
        estimated_time = duration * 0.5
        
        return estimated_time
