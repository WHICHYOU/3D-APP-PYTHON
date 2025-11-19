"""
Depth Map Post-processing
"""
import cv2
import numpy as np


def smooth_depth_map(
    depth_map: np.ndarray,
    method: str = "bilateral",
    strength: int = 5
) -> np.ndarray:
    """
    Smooth depth map while preserving edges
    
    Args:
        depth_map: Input depth map
        method: Smoothing method ('bilateral', 'gaussian', 'median')
        strength: Smoothing strength (kernel size)
    
    Returns:
        Smoothed depth map
    """
    if method == "bilateral":
        # Bilateral filter preserves edges
        smoothed = cv2.bilateralFilter(
            depth_map.astype(np.float32),
            d=strength * 2 + 1,
            sigmaColor=0.1,
            sigmaSpace=strength
        )
    elif method == "gaussian":
        smoothed = cv2.GaussianBlur(
            depth_map,
            (strength * 2 + 1, strength * 2 + 1),
            0
        )
    elif method == "median":
        smoothed = cv2.medianBlur(
            (depth_map * 255).astype(np.uint8),
            strength * 2 + 1
        ) / 255.0
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return smoothed


def enhance_edges(depth_map: np.ndarray) -> np.ndarray:
    """
    Enhance edges in depth map
    
    Args:
        depth_map: Input depth map
    
    Returns:
        Edge-enhanced depth map
    """
    # Apply Sobel edge detection
    sobel_x = cv2.Sobel(depth_map, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(depth_map, cv2.CV_64F, 0, 1, ksize=3)
    edges = np.sqrt(sobel_x**2 + sobel_y**2)
    
    # Normalize edges
    edges = edges / edges.max() if edges.max() > 0 else edges
    
    # Sharpen original depth map using edges
    enhanced = depth_map + 0.1 * edges
    enhanced = np.clip(enhanced, 0, 1)
    
    return enhanced


def adjust_depth_range(
    depth_map: np.ndarray,
    near_clip: float = 0.0,
    far_clip: float = 1.0
) -> np.ndarray:
    """
    Adjust depth range by clipping near and far planes
    
    Args:
        depth_map: Input depth map
        near_clip: Near plane threshold (0-1)
        far_clip: Far plane threshold (0-1)
    
    Returns:
        Adjusted depth map
    """
    # Clip to range
    clipped = np.clip(depth_map, near_clip, far_clip)
    
    # Renormalize to [0, 1]
    if far_clip - near_clip > 1e-6:
        clipped = (clipped - near_clip) / (far_clip - near_clip)
    
    return clipped
