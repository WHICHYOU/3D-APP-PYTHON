"""
Side-by-Side (SBS) and Other Format Composition
"""
import numpy as np
import cv2
from typing import Tuple


class SBSComposer:
    """Compose stereo pairs into various output formats"""
    
    @staticmethod
    def compose_half_sbs(
        left_view: np.ndarray,
        right_view: np.ndarray
    ) -> np.ndarray:
        """
        Compose Half Side-by-Side format
        Both views are horizontally compressed to 50% width
        
        Args:
            left_view: Left eye view (H, W, 3)
            right_view: Right eye view (H, W, 3)
        
        Returns:
            Half-SBS image (H, W, 3) - same size as input
        """
        h, w = left_view.shape[:2]
        
        # Resize both views to half width
        left_half = cv2.resize(left_view, (w // 2, h), interpolation=cv2.INTER_LINEAR)
        right_half = cv2.resize(right_view, (w // 2, h), interpolation=cv2.INTER_LINEAR)
        
        # Concatenate horizontally
        half_sbs = np.concatenate([left_half, right_half], axis=1)
        
        return half_sbs
    
    @staticmethod
    def compose_full_sbs(
        left_view: np.ndarray,
        right_view: np.ndarray
    ) -> np.ndarray:
        """
        Compose Full Side-by-Side format
        Views placed side by side at full resolution
        
        Args:
            left_view: Left eye view (H, W, 3)
            right_view: Right eye view (H, W, 3)
        
        Returns:
            Full-SBS image (H, 2W, 3) - double width
        """
        # Simply concatenate horizontally
        full_sbs = np.concatenate([left_view, right_view], axis=1)
        
        return full_sbs
    
    @staticmethod
    def compose_top_bottom(
        left_view: np.ndarray,
        right_view: np.ndarray,
        half: bool = True
    ) -> np.ndarray:
        """
        Compose Top-Bottom (Over-Under) format
        
        Args:
            left_view: Left eye view (H, W, 3)
            right_view: Right eye view (H, W, 3)
            half: Whether to use half resolution (compressed height)
        
        Returns:
            Top-Bottom image
        """
        h, w = left_view.shape[:2]
        
        if half:
            # Resize both views to half height
            left_half = cv2.resize(left_view, (w, h // 2), interpolation=cv2.INTER_LINEAR)
            right_half = cv2.resize(right_view, (w, h // 2), interpolation=cv2.INTER_LINEAR)
            
            # Stack vertically
            result = np.concatenate([left_half, right_half], axis=0)
        else:
            # Full resolution vertical stack
            result = np.concatenate([left_view, right_view], axis=0)
        
        return result
    
    @staticmethod
    def compose_anaglyph(
        left_view: np.ndarray,
        right_view: np.ndarray,
        mode: str = 'red_cyan'
    ) -> np.ndarray:
        """
        Compose anaglyph 3D image (for red-cyan glasses)
        
        Args:
            left_view: Left eye view (H, W, 3)
            right_view: Right eye view (H, W, 3)
            mode: Anaglyph mode ('red_cyan', 'amber_blue')
        
        Returns:
            Anaglyph image (H, W, 3)
        """
        if mode == 'red_cyan':
            # Red channel from left, green+blue from right
            anaglyph = np.zeros_like(left_view)
            anaglyph[:, :, 0] = left_view[:, :, 0]  # Red from left
            anaglyph[:, :, 1] = right_view[:, :, 1]  # Green from right
            anaglyph[:, :, 2] = right_view[:, :, 2]  # Blue from right
        elif mode == 'amber_blue':
            # Amber (red+green) from left, blue from right
            anaglyph = np.zeros_like(left_view)
            anaglyph[:, :, 0] = left_view[:, :, 0]  # Red from left
            anaglyph[:, :, 1] = left_view[:, :, 1]  # Green from left
            anaglyph[:, :, 2] = right_view[:, :, 2]  # Blue from right
        else:
            raise ValueError(f"Unknown anaglyph mode: {mode}")
        
        return anaglyph
    
    @staticmethod
    def add_watermark(
        image: np.ndarray,
        text: str = "2D3D Converter - Free Version",
        position: str = 'bottom_right',
        opacity: float = 0.5
    ) -> np.ndarray:
        """
        Add watermark to image (for free tier)
        
        Args:
            image: Input image
            text: Watermark text
            position: Position ('bottom_right', 'bottom_center', 'top_right')
            opacity: Watermark opacity (0-1)
        
        Returns:
            Image with watermark
        """
        result = image.copy()
        h, w = result.shape[:2]
        
        # Calculate text size and position
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.5, min(w / 1000, 1.5))
        thickness = max(1, int(font_scale * 2))
        
        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Position calculations
        margin = 20
        if position == 'bottom_right':
            x = w - text_w - margin
            y = h - margin
        elif position == 'bottom_center':
            x = (w - text_w) // 2
            y = h - margin
        elif position == 'top_right':
            x = w - text_w - margin
            y = text_h + margin
        else:
            x = margin
            y = h - margin
        
        # Draw semi-transparent background
        overlay = result.copy()
        cv2.rectangle(
            overlay,
            (x - 5, y - text_h - 5),
            (x + text_w + 5, y + 5),
            (0, 0, 0),
            -1
        )
        cv2.addWeighted(overlay, 0.5, result, 0.5, 0, result)
        
        # Draw text
        cv2.putText(
            result,
            text,
            (x, y),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA
        )
        
        return result
