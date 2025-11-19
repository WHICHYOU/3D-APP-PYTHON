"""
Depth Image-Based Rendering (DIBR)
Core algorithm for generating stereoscopic views from depth maps
"""
import numpy as np
import cv2
from typing import Tuple


class DIBRRenderer:
    """Depth Image-Based Rendering for stereoscopic view generation"""
    
    def __init__(self, ipd: float = 65.0, convergence: float = 1.0):
        """
        Initialize DIBR renderer
        
        Args:
            ipd: Interpupillary distance in mm (typical: 55-75)
            convergence: Convergence distance multiplier
        """
        self.ipd = ipd
        self.convergence = convergence
    
    def render_stereo_pair(
        self,
        image: np.ndarray,
        depth: np.ndarray,
        depth_intensity: float = 75.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Render stereo pair from image and depth map
        
        Args:
            image: Input RGB image (H, W, 3)
            depth: Depth map (H, W) normalized to [0, 1]
            depth_intensity: Depth effect strength (0-100)
        
        Returns:
            Tuple of (left_view, right_view)
        """
        # Compute disparity map
        disparity = self.compute_disparity(depth, depth_intensity)
        
        # Generate left and right views
        left_view = self.shift_pixels(image, -disparity / 2)
        right_view = self.shift_pixels(image, disparity / 2)
        
        return left_view, right_view
    
    def compute_disparity(
        self,
        depth: np.ndarray,
        depth_intensity: float = 75.0
    ) -> np.ndarray:
        """
        Convert depth map to disparity (pixel shift amount)
        
        Args:
            depth: Normalized depth map [0, 1]
            depth_intensity: Strength multiplier (0-100)
        
        Returns:
            Disparity map in pixels
        """
        # Scale depth by intensity
        intensity_factor = depth_intensity / 100.0
        
        # Calculate disparity based on IPD and convergence
        # Further objects (depth=1) have less disparity
        # Closer objects (depth=0) have more disparity
        max_disparity = self.ipd * intensity_factor * 0.5
        disparity = max_disparity * (1.0 - depth)
        
        return disparity
    
    def shift_pixels(
        self,
        image: np.ndarray,
        disparity: np.ndarray
    ) -> np.ndarray:
        """
        Shift pixels horizontally based on disparity
        
        Args:
            image: Input image (H, W, 3)
            disparity: Disparity map (H, W) - positive shifts right
        
        Returns:
            Shifted image with holes filled
        """
        h, w = image.shape[:2]
        
        # Create meshgrid for coordinates
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        
        # Apply horizontal shift
        x_shifted = x + disparity
        
        # Clip to valid range
        x_shifted = np.clip(x_shifted, 0, w - 1)
        
        # Remap image
        shifted = cv2.remap(
            image,
            x_shifted,
            y,
            cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return shifted
    
    def set_ipd(self, ipd: float):
        """Set interpupillary distance"""
        self.ipd = max(50.0, min(80.0, ipd))  # Clamp to reasonable range
    
    def set_convergence(self, convergence: float):
        """Set convergence distance"""
        self.convergence = max(0.1, convergence)
