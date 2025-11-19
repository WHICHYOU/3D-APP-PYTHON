"""
Frame Management
Manage extracted frames and metadata
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
import cv2


class FrameManager:
    """Manage video frames and associated data"""
    
    def __init__(self, work_dir: str):
        """
        Initialize frame manager
        
        Args:
            work_dir: Working directory for frame storage
        """
        self.work_dir = Path(work_dir)
        self.frames_dir = self.work_dir / 'frames'
        self.depth_dir = self.work_dir / 'depth_maps'
        self.left_dir = self.work_dir / 'left_views'
        self.right_dir = self.work_dir / 'right_views'
        self.metadata_file = self.work_dir / 'metadata.json'
        
        # Create directories
        for directory in [self.frames_dir, self.depth_dir, self.left_dir, self.right_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_frame_list(self) -> List[Path]:
        """
        Get list of all frames
        
        Returns:
            Sorted list of frame paths
        """
        frames = sorted(self.frames_dir.glob('frame_*.png'))
        return frames
    
    def get_frame_count(self) -> int:
        """Get total number of frames"""
        return len(list(self.frames_dir.glob('frame_*.png')))
    
    def load_frame(self, frame_index: int) -> Optional[np.ndarray]:
        """
        Load a specific frame
        
        Args:
            frame_index: Frame index (0-based)
        
        Returns:
            Frame image or None if not found
        """
        frame_path = self.frames_dir / f'frame_{frame_index:06d}.png'
        
        if not frame_path.exists():
            return None
        
        frame = cv2.imread(str(frame_path))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return frame
    
    def save_depth_map(self, frame_index: int, depth_map: np.ndarray):
        """
        Save depth map for a frame
        
        Args:
            frame_index: Frame index
            depth_map: Depth map array
        """
        depth_path = self.depth_dir / f'depth_{frame_index:06d}.npy'
        np.save(depth_path, depth_map)
    
    def load_depth_map(self, frame_index: int) -> Optional[np.ndarray]:
        """
        Load depth map for a frame
        
        Args:
            frame_index: Frame index
        
        Returns:
            Depth map or None
        """
        depth_path = self.depth_dir / f'depth_{frame_index:06d}.npy'
        
        if not depth_path.exists():
            return None
        
        return np.load(depth_path)
    
    def save_stereo_pair(
        self,
        frame_index: int,
        left_view: np.ndarray,
        right_view: np.ndarray
    ):
        """
        Save stereoscopic pair for a frame
        
        Args:
            frame_index: Frame index
            left_view: Left eye view
            right_view: Right eye view
        """
        left_path = self.left_dir / f'left_{frame_index:06d}.png'
        right_path = self.right_dir / f'right_{frame_index:06d}.png'
        
        # Convert RGB to BGR for OpenCV
        left_bgr = cv2.cvtColor(left_view, cv2.COLOR_RGB2BGR)
        right_bgr = cv2.cvtColor(right_view, cv2.COLOR_RGB2BGR)
        
        cv2.imwrite(str(left_path), left_bgr)
        cv2.imwrite(str(right_path), right_bgr)
    
    def save_metadata(self, metadata: Dict):
        """
        Save metadata about the video processing
        
        Args:
            metadata: Dictionary of metadata
        """
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_metadata(self) -> Optional[Dict]:
        """
        Load metadata
        
        Returns:
            Metadata dictionary or None
        """
        if not self.metadata_file.exists():
            return None
        
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def cleanup(self):
        """Clean up all temporary files"""
        import shutil
        
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)
    
    def get_processing_status(self) -> Dict:
        """
        Get current processing status
        
        Returns:
            Status dictionary
        """
        total_frames = self.get_frame_count()
        depth_maps = len(list(self.depth_dir.glob('depth_*.npy')))
        stereo_pairs = len(list(self.left_dir.glob('left_*.png')))
        
        return {
            'total_frames': total_frames,
            'depth_maps_generated': depth_maps,
            'stereo_pairs_generated': stereo_pairs,
            'progress': stereo_pairs / max(total_frames, 1),
        }
