"""
Temporal Filtering for Video Consistency
Reduces flickering between frames
"""
import numpy as np
from collections import deque
from typing import Optional


class TemporalFilter:
    """Applies temporal smoothing to depth maps in video sequences"""
    
    def __init__(self, window_size: int = 5, alpha: float = 0.3):
        """
        Initialize temporal filter
        
        Args:
            window_size: Number of frames to consider for smoothing
            alpha: Blending factor for exponential moving average (0-1)
        """
        self.window_size = window_size
        self.alpha = alpha
        self.history = deque(maxlen=window_size)
        self.prev_depth = None
    
    def filter(self, depth_map: np.ndarray) -> np.ndarray:
        """
        Apply temporal filtering to current depth map
        
        Args:
            depth_map: Current frame depth map
        
        Returns:
            Temporally filtered depth map
        """
        # Add to history
        self.history.append(depth_map.copy())
        
        # Exponential moving average with previous frame
        if self.prev_depth is not None:
            filtered = (
                self.alpha * depth_map +
                (1 - self.alpha) * self.prev_depth
            )
        else:
            filtered = depth_map.copy()
        
        self.prev_depth = filtered.copy()
        
        return filtered
    
    def reset(self):
        """Reset filter state"""
        self.history.clear()
        self.prev_depth = None


def detect_scene_change(
    depth_map1: np.ndarray,
    depth_map2: np.ndarray,
    threshold: float = 0.3
) -> bool:
    """
    Detect if there's a scene change between two frames
    
    Args:
        depth_map1: Previous frame depth map
        depth_map2: Current frame depth map
        threshold: Threshold for scene change detection (0-1)
    
    Returns:
        True if scene change detected
    """
    # Calculate mean absolute difference
    diff = np.abs(depth_map1 - depth_map2).mean()
    
    return diff > threshold
