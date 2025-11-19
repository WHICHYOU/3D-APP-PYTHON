"""
Image Preprocessing for Depth Estimation
"""
import cv2
import numpy as np
from typing import Tuple


def preprocess_image(
    image: np.ndarray,
    target_size: Tuple[int, int] = (512, 512),
    normalize: bool = True
) -> np.ndarray:
    """
    Preprocess image for depth estimation model
    
    Args:
        image: Input RGB image (H, W, 3)
        target_size: Target size for model input (height, width)
        normalize: Whether to normalize pixel values
    
    Returns:
        Preprocessed image
    """
    # Resize while maintaining aspect ratio
    h, w = image.shape[:2]
    target_h, target_w = target_size
    
    # Calculate scaling
    scale = min(target_h / h, target_w / w)
    new_h, new_w = int(h * scale), int(w * scale)
    
    # Resize
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    # Pad to target size
    pad_h = target_h - new_h
    pad_w = target_w - new_w
    top, bottom = pad_h // 2, pad_h - pad_h // 2
    left, right = pad_w // 2, pad_w - pad_w // 2
    
    padded = cv2.copyMakeBorder(
        resized,
        top, bottom, left, right,
        cv2.BORDER_CONSTANT,
        value=(0, 0, 0)
    )
    
    # Normalize
    if normalize:
        # ImageNet normalization
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        padded = padded.astype(np.float32) / 255.0
        padded = (padded - mean) / std
    
    return padded


def batch_preprocess(
    images: list,
    target_size: Tuple[int, int] = (512, 512)
) -> np.ndarray:
    """
    Preprocess batch of images
    
    Args:
        images: List of RGB images
        target_size: Target size for model input
    
    Returns:
        Batch of preprocessed images as numpy array
    """
    return np.array([
        preprocess_image(img, target_size)
        for img in images
    ])
