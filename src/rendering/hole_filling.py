"""
Hole Filling Algorithms
Fill disocclusions (holes) in rendered stereoscopic views
"""
import cv2
import numpy as np


def fill_holes_fast_marching(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Fill holes using Fast Marching Method (inpainting)
    
    Args:
        image: Image with holes (H, W, 3)
        mask: Binary mask where 1 = hole, 0 = valid (H, W)
    
    Returns:
        Image with filled holes
    """
    # Convert mask to uint8
    mask_uint8 = (mask * 255).astype(np.uint8)
    
    # Apply inpainting
    filled = cv2.inpaint(
        image,
        mask_uint8,
        inpaintRadius=3,
        flags=cv2.INPAINT_TELEA
    )
    
    return filled


def fill_holes_nearest(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Fill holes using nearest neighbor interpolation
    
    Args:
        image: Image with holes (H, W, 3)
        mask: Binary mask where 1 = hole, 0 = valid (H, W)
    
    Returns:
        Image with filled holes
    """
    # Find coordinates of holes
    hole_coords = np.where(mask > 0)
    
    if len(hole_coords[0]) == 0:
        return image
    
    # Find coordinates of valid pixels
    valid_coords = np.where(mask == 0)
    
    if len(valid_coords[0]) == 0:
        return image
    
    # Simple nearest neighbor fill
    filled = image.copy()
    
    # For each hole pixel, find nearest valid pixel
    # This is simplified - could be optimized with KD-tree
    for i in range(len(hole_coords[0])):
        y, x = hole_coords[0][i], hole_coords[1][i]
        
        # Find nearest valid pixel (simple Manhattan distance)
        distances = np.abs(valid_coords[0] - y) + np.abs(valid_coords[1] - x)
        nearest_idx = np.argmin(distances)
        
        nearest_y = valid_coords[0][nearest_idx]
        nearest_x = valid_coords[1][nearest_idx]
        
        filled[y, x] = image[nearest_y, nearest_x]
    
    return filled


def detect_holes(left_view: np.ndarray, right_view: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Detect holes (disocclusions) in stereo pair
    
    Args:
        left_view: Left eye view (H, W, 3)
        right_view: Right eye view (H, W, 3)
    
    Returns:
        Tuple of (left_holes_mask, right_holes_mask)
    """
    # Simple hole detection: look for black pixels or sudden changes
    # This is a placeholder - real implementation would be more sophisticated
    
    left_gray = cv2.cvtColor(left_view, cv2.COLOR_RGB2GRAY)
    right_gray = cv2.cvtColor(right_view, cv2.COLOR_RGB2GRAY)
    
    # Detect very dark regions (potential holes)
    left_holes = (left_gray < 10).astype(np.float32)
    right_holes = (right_gray < 10).astype(np.float32)
    
    return left_holes, right_holes


def fill_stereo_pair_holes(
    left_view: np.ndarray,
    right_view: np.ndarray,
    method: str = 'fast_marching'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fill holes in both views of stereo pair
    
    Args:
        left_view: Left eye view
        right_view: Right eye view
        method: Hole filling method
    
    Returns:
        Tuple of filled (left_view, right_view)
    """
    # Detect holes
    left_mask, right_mask = detect_holes(left_view, right_view)
    
    # Fill holes
    if method == 'fast_marching':
        left_filled = fill_holes_fast_marching(left_view, left_mask)
        right_filled = fill_holes_fast_marching(right_view, right_mask)
    elif method == 'nearest':
        left_filled = fill_holes_nearest(left_view, left_mask)
        right_filled = fill_holes_nearest(right_view, right_mask)
    else:
        # No filling
        left_filled = left_view
        right_filled = right_view
    
    return left_filled, right_filled
