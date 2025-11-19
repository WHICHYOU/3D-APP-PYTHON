"""
Validation Utilities
Input validation and error checking
"""
import os
from pathlib import Path
from typing import Optional, Tuple


def validate_video_path(video_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate video file path
    
    Args:
        video_path: Path to video file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if file exists
    if not os.path.exists(video_path):
        return False, f"File not found: {video_path}"
    
    # Check if it's a file (not directory)
    if not os.path.isfile(video_path):
        return False, f"Path is not a file: {video_path}"
    
    # Check extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    ext = Path(video_path).suffix.lower()
    
    if ext not in valid_extensions:
        return False, f"Unsupported video format: {ext}"
    
    # Check file size (must be > 0)
    if os.path.getsize(video_path) == 0:
        return False, "Video file is empty"
    
    return True, None


def validate_image_path(image_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate image file path
    
    Args:
        image_path: Path to image file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(image_path):
        return False, f"File not found: {image_path}"
    
    if not os.path.isfile(image_path):
        return False, f"Path is not a file: {image_path}"
    
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    ext = Path(image_path).suffix.lower()
    
    if ext not in valid_extensions:
        return False, f"Unsupported image format: {ext}"
    
    if os.path.getsize(image_path) == 0:
        return False, "Image file is empty"
    
    return True, None


def validate_output_path(output_path: str, overwrite: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate output file path
    
    Args:
        output_path: Output file path
        overwrite: Whether to allow overwriting existing files
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if parent directory exists
    parent = Path(output_path).parent
    if not parent.exists():
        return False, f"Output directory does not exist: {parent}"
    
    # Check if file already exists and overwrite is not allowed
    if os.path.exists(output_path) and not overwrite:
        return False, f"Output file already exists: {output_path}"
    
    # Check if we have write permission
    if os.path.exists(output_path):
        if not os.access(output_path, os.W_OK):
            return False, f"No write permission for: {output_path}"
    else:
        if not os.access(parent, os.W_OK):
            return False, f"No write permission for directory: {parent}"
    
    return True, None


def validate_depth_intensity(value: float) -> Tuple[bool, Optional[str]]:
    """
    Validate depth intensity parameter
    
    Args:
        value: Depth intensity value
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, (int, float)):
        return False, "Depth intensity must be a number"
    
    if value < 0 or value > 100:
        return False, "Depth intensity must be between 0 and 100"
    
    return True, None


def validate_ipd(value: float) -> Tuple[bool, Optional[str]]:
    """
    Validate interpupillary distance
    
    Args:
        value: IPD value in mm
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, (int, float)):
        return False, "IPD must be a number"
    
    if value < 50 or value > 80:
        return False, "IPD must be between 50mm and 80mm"
    
    return True, None


def validate_fps(value: int) -> Tuple[bool, Optional[str]]:
    """
    Validate frames per second
    
    Args:
        value: FPS value
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, int):
        return False, "FPS must be an integer"
    
    if value < 1 or value > 120:
        return False, "FPS must be between 1 and 120"
    
    valid_fps = [23, 24, 25, 30, 50, 60, 120]
    if value not in valid_fps:
        return True, f"Warning: Non-standard FPS {value}, consider using {min(valid_fps, key=lambda x: abs(x - value))}"
    
    return True, None


def validate_batch_size(value: int) -> Tuple[bool, Optional[str]]:
    """
    Validate batch size
    
    Args:
        value: Batch size
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, int):
        return False, "Batch size must be an integer"
    
    if value < 1:
        return False, "Batch size must be at least 1"
    
    if value > 32:
        return True, f"Warning: Large batch size {value} may cause memory issues"
    
    return True, None
