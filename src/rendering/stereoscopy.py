"""
Stereoscopy Management
Handles stereo parameter calculations and view generation
"""
import numpy as np
from typing import Tuple


class StereoscopyManager:
    """Manages stereoscopic rendering parameters and calculations"""
    
    # Standard IPD ranges (in mm)
    IPD_MIN = 50.0
    IPD_MAX = 80.0
    IPD_DEFAULT = 65.0
    
    def __init__(self):
        """Initialize stereoscopy manager"""
        self.ipd = self.IPD_DEFAULT
        self.convergence = 1.0
        self.depth_budget = 1.0
    
    def calculate_stereo_params(
        self,
        image_width: int,
        depth_intensity: float = 75.0
    ) -> dict:
        """
        Calculate stereoscopic rendering parameters
        
        Args:
            image_width: Width of source image in pixels
            depth_intensity: Depth effect strength (0-100)
        
        Returns:
            Dictionary of rendering parameters
        """
        # Calculate maximum disparity in pixels
        # Rough rule: max disparity ≈ 2% of image width for comfortable viewing
        max_disparity = image_width * 0.02 * (depth_intensity / 100.0)
        
        params = {
            'ipd_mm': self.ipd,
            'convergence': self.convergence,
            'max_disparity_px': max_disparity,
            'depth_intensity': depth_intensity,
            'comfort_zone': self._calculate_comfort_zone(max_disparity, image_width),
        }
        
        return params
    
    def _calculate_comfort_zone(
        self,
        max_disparity: float,
        image_width: int
    ) -> dict:
        """
        Calculate comfortable viewing zone parameters
        
        Args:
            max_disparity: Maximum disparity in pixels
            image_width: Image width in pixels
        
        Returns:
            Comfort zone parameters
        """
        # Comfort zone: disparity should be < 2% of image width
        disparity_ratio = max_disparity / image_width
        
        return {
            'is_comfortable': disparity_ratio < 0.03,
            'disparity_ratio': disparity_ratio,
            'recommended_max': image_width * 0.02,
        }
    
    def adjust_for_content_type(self, content_type: str):
        """
        Adjust parameters based on content type
        
        Args:
            content_type: Type of content ('action', 'documentary', 'animation', etc.)
        """
        presets = {
            'action': {'depth_intensity': 85, 'convergence': 1.2},
            'documentary': {'depth_intensity': 65, 'convergence': 1.0},
            'animation': {'depth_intensity': 90, 'convergence': 1.3},
            'talking_head': {'depth_intensity': 50, 'convergence': 0.8},
        }
        
        if content_type in presets:
            preset = presets[content_type]
            return preset
        
        return {'depth_intensity': 75, 'convergence': 1.0}
    
    def validate_parameters(self) -> bool:
        """
        Validate that current parameters are within safe ranges
        
        Returns:
            True if parameters are valid
        """
        if not (self.IPD_MIN <= self.ipd <= self.IPD_MAX):
            return False
        
        if not (0.1 <= self.convergence <= 2.0):
            return False
        
        return True
