"""
Preview Widget Module

Displays preview of original image, depth map, and stereoscopic output.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTabWidget, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from pathlib import Path
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class PreviewWidget(QWidget):
    """Widget for previewing conversion results."""
    
    preview_updated = pyqtSignal()
    
    def __init__(self):
        """Initialize preview widget."""
        super().__init__()
        self.current_file = None
        self.original_image = None
        self.depth_map = None
        self.stereo_output = None
        self._setup_ui()
        
        logger.info("PreviewWidget initialized")
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Original image tab
        self.original_tab = self._create_image_tab()
        self.tab_widget.addTab(self.original_tab, "Original")
        
        # Depth map tab
        self.depth_tab = self._create_image_tab()
        self.tab_widget.addTab(self.depth_tab, "Depth Map")
        
        # Stereo output tab
        self.stereo_tab = self._create_image_tab()
        self.tab_widget.addTab(self.stereo_tab, "3D Output")
        
        # Side-by-side comparison tab
        self.comparison_tab = self._create_comparison_tab()
        self.tab_widget.addTab(self.comparison_tab, "Comparison")
        
        layout.addWidget(self.tab_widget)
        
        # Info label
        self.info_label = QLabel("No file loaded")
        self.info_label.setStyleSheet("padding: 5px; background-color: #f8f9fa;")
        layout.addWidget(self.info_label)
    
    def _create_image_tab(self):
        """Create a tab with image display."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel("No preview available")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: gray; font-size: 14px;")
        label.setMinimumSize(400, 300)
        
        scroll_area.setWidget(label)
        return scroll_area
    
    def _create_comparison_tab(self):
        """Create comparison tab with multiple views."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Original image section
        layout.addWidget(QLabel("<b>Original</b>"))
        self.comp_original = QLabel()
        self.comp_original.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comp_original.setStyleSheet("border: 1px solid #ddd; background-color: white;")
        layout.addWidget(self.comp_original)
        
        # Depth map section
        layout.addWidget(QLabel("<b>Depth Map</b>"))
        self.comp_depth = QLabel()
        self.comp_depth.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comp_depth.setStyleSheet("border: 1px solid #ddd; background-color: white;")
        layout.addWidget(self.comp_depth)
        
        # 3D output section
        layout.addWidget(QLabel("<b>3D Output</b>"))
        self.comp_stereo = QLabel()
        self.comp_stereo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comp_stereo.setStyleSheet("border: 1px solid #ddd; background-color: white;")
        layout.addWidget(self.comp_stereo)
        
        layout.addStretch()
        scroll_area.setWidget(widget)
        return scroll_area
    
    def load_file(self, file_path: str):
        """Load file for preview."""
        self.current_file = file_path
        path = Path(file_path)
        
        try:
            # Check if image or video
            is_video = path.suffix.lower() in {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
            
            if is_video:
                # For videos, extract first frame
                self._load_video_frame(file_path)
            else:
                # For images, load directly
                self._load_image(file_path)
            
            self.info_label.setText(f"Loaded: {path.name} ({self._get_file_size_str(path)})")
            logger.info(f"Loaded file: {path.name}")
            
        except Exception as e:
            logger.error(f"Failed to load file: {e}")
            self.info_label.setText(f"Error loading file: {e}")
    
    def _load_image(self, file_path: str):
        """Load image file."""
        # Load with OpenCV
        image_bgr = cv2.imread(file_path)
        if image_bgr is None:
            raise ValueError("Failed to load image")
        
        self.original_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        # Display original
        self._display_image(self.original_image, self.original_tab)
        
        # Generate initial depth map
        self._generate_depth_map()
    
    def _load_video_frame(self, file_path: str):
        """Load first frame from video."""
        cap = cv2.VideoCapture(file_path)
        
        if not cap.isOpened():
            raise ValueError("Failed to open video")
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise ValueError("Failed to read video frame")
        
        self.original_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Display original
        self._display_image(self.original_image, self.original_tab)
        
        # Generate initial depth map
        self._generate_depth_map()
    
    def _generate_depth_map(self):
        """Generate depth map from original image."""
        if self.original_image is None:
            return
        
        try:
            self.info_label.setText("Generating depth map...")
            
            # Import depth estimator
            from ..ai_core.depth_estimation import DepthEstimator
            
            estimator = DepthEstimator()
            self.depth_map = estimator.estimate_depth(self.original_image, normalize=True)
            
            # Display depth map
            depth_vis = (self.depth_map * 255).astype(np.uint8)
            depth_colored = cv2.applyColorMap(depth_vis, cv2.COLORMAP_INFERNO)
            depth_rgb = cv2.cvtColor(depth_colored, cv2.COLOR_BGR2RGB)
            self._display_image(depth_rgb, self.depth_tab)
            
            self.info_label.setText("Depth map generated")
            
            # Generate initial stereo output
            self._generate_stereo_output()
            
        except Exception as e:
            logger.error(f"Failed to generate depth map: {e}")
            self.info_label.setText(f"Error generating depth: {e}")
    
    def _generate_stereo_output(self, settings=None):
        """Generate stereoscopic output."""
        if self.original_image is None or self.depth_map is None:
            return
        
        try:
            self.info_label.setText("Generating 3D output...")
            
            # Get settings
            if settings is None:
                settings = {
                    'format': 'half_sbs',
                    'depth_intensity': 0.75,
                    'ipd': 65
                }
            
            # Import rendering components
            from ..rendering.dibr_renderer import DIBRRenderer
            from ..rendering.sbs_composer import SBSComposer
            
            # Render stereo pair
            renderer = DIBRRenderer(ipd=settings.get('ipd', 65))
            left_view, right_view = renderer.render_stereo_pair(
                self.original_image,
                self.depth_map,
                depth_intensity=settings.get('depth_intensity', 0.75)
            )
            
            # Compose output
            composer = SBSComposer()
            output_format = settings.get('format', 'half_sbs')
            
            if output_format == 'half_sbs':
                self.stereo_output = composer.compose_half_sbs(left_view, right_view)
            elif output_format == 'full_sbs':
                self.stereo_output = composer.compose_full_sbs(left_view, right_view)
            elif output_format == 'anaglyph':
                self.stereo_output = composer.compose_anaglyph(left_view, right_view)
            elif output_format == 'top_bottom':
                self.stereo_output = composer.compose_top_bottom(left_view, right_view, half=True)
            
            # Display stereo output
            self._display_image(self.stereo_output, self.stereo_tab)
            
            # Update comparison tab
            self._update_comparison_tab()
            
            self.info_label.setText(f"3D output generated ({output_format})")
            self.preview_updated.emit()
            
        except Exception as e:
            logger.error(f"Failed to generate stereo output: {e}")
            self.info_label.setText(f"Error generating 3D: {e}")
    
    def _display_image(self, image_rgb: np.ndarray, tab_widget):
        """Display image in a tab."""
        height, width = image_rgb.shape[:2]
        
        # Convert to QImage
        if len(image_rgb.shape) == 2:
            # Grayscale
            qimage = QImage(image_rgb.data, width, height, width, QImage.Format.Format_Grayscale8)
        else:
            # RGB
            bytes_per_line = 3 * width
            qimage = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Create pixmap and scale if needed
        pixmap = QPixmap.fromImage(qimage)
        
        # Scale to fit preview (max 800x600)
        max_width, max_height = 800, 600
        if width > max_width or height > max_height:
            pixmap = pixmap.scaled(
                max_width, max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        
        # Get label from scroll area
        label = tab_widget.widget()
        label.setPixmap(pixmap)
        label.setMinimumSize(pixmap.size())
    
    def _update_comparison_tab(self):
        """Update comparison tab with all images."""
        max_width = 600
        
        if self.original_image is not None:
            pixmap = self._numpy_to_pixmap(self.original_image, max_width)
            self.comp_original.setPixmap(pixmap)
        
        if self.depth_map is not None:
            depth_vis = (self.depth_map * 255).astype(np.uint8)
            depth_colored = cv2.applyColorMap(depth_vis, cv2.COLORMAP_INFERNO)
            depth_rgb = cv2.cvtColor(depth_colored, cv2.COLOR_BGR2RGB)
            pixmap = self._numpy_to_pixmap(depth_rgb, max_width)
            self.comp_depth.setPixmap(pixmap)
        
        if self.stereo_output is not None:
            pixmap = self._numpy_to_pixmap(self.stereo_output, max_width)
            self.comp_stereo.setPixmap(pixmap)
    
    def _numpy_to_pixmap(self, image_rgb: np.ndarray, max_width: int):
        """Convert numpy array to QPixmap."""
        height, width = image_rgb.shape[:2]
        bytes_per_line = 3 * width
        qimage = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        
        if width > max_width:
            pixmap = pixmap.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)
        
        return pixmap
    
    def update_preview(self, settings: dict):
        """Update preview with new settings."""
        if self.original_image is not None and self.depth_map is not None:
            self._generate_stereo_output(settings)
    
    def clear_preview(self):
        """Clear all preview images."""
        self.current_file = None
        self.original_image = None
        self.depth_map = None
        self.stereo_output = None
        
        # Reset all displays
        for tab in [self.original_tab, self.depth_tab, self.stereo_tab]:
            label = tab.widget()
            label.setPixmap(QPixmap())
            label.setText("No preview available")
        
        self.comp_original.setPixmap(QPixmap())
        self.comp_depth.setPixmap(QPixmap())
        self.comp_stereo.setPixmap(QPixmap())
        
        self.info_label.setText("No file loaded")
    
    def save_preview(self, output_path: str):
        """Save current stereo output."""
        if self.stereo_output is not None:
            output_bgr = cv2.cvtColor(self.stereo_output, cv2.COLOR_RGB2BGR)
            cv2.imwrite(output_path, output_bgr)
            logger.info(f"Preview saved: {output_path}")
    
    def _get_file_size_str(self, path: Path) -> str:
        """Get human-readable file size."""
        size = path.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import numpy as np


class PreviewWidget(QWidget):
    """Widget for previewing images and video frames"""
    
    # Signals
    view_mode_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        Initialize preview widget
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.current_image = None
        self.depth_map = None
        self.left_view = None
        self.right_view = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # View mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel('View Mode:'))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            'Original',
            'Depth Map',
            'Side-by-Side',
            'Anaglyph',
            'Left View',
            'Right View'
        ])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        
        layout.addLayout(mode_layout)
        
        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet('border: 1px solid #ccc; background: #000;')
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setScaledContents(True)
        
        layout.addWidget(self.image_label)
        
        # Info label
        self.info_label = QLabel('No image loaded')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
    
    def set_image(self, image: np.ndarray):
        """
        Set input image
        
        Args:
            image: Input image (H, W, 3) RGB
        """
        self.current_image = image
        self.update_preview()
    
    def set_depth_map(self, depth_map: np.ndarray):
        """
        Set depth map
        
        Args:
            depth_map: Depth map (H, W)
        """
        self.depth_map = depth_map
        self.update_preview()
    
    def set_stereo_pair(self, left_view: np.ndarray, right_view: np.ndarray):
        """
        Set stereoscopic pair
        
        Args:
            left_view: Left eye view
            right_view: Right eye view
        """
        self.left_view = left_view
        self.right_view = right_view
        self.update_preview()
    
    def on_mode_changed(self, mode: str):
        """
        Handle view mode change
        
        Args:
            mode: New view mode
        """
        self.view_mode_changed.emit(mode)
        self.update_preview()
    
    def update_preview(self):
        """Update preview based on current mode"""
        mode = self.mode_combo.currentText()
        
        image_to_display = None
        
        if mode == 'Original' and self.current_image is not None:
            image_to_display = self.current_image
        
        elif mode == 'Depth Map' and self.depth_map is not None:
            # Convert depth map to grayscale image
            depth_uint8 = (self.depth_map * 255).astype(np.uint8)
            image_to_display = np.stack([depth_uint8] * 3, axis=-1)
        
        elif mode == 'Side-by-Side' and self.left_view is not None and self.right_view is not None:
            # Create half SBS
            h, w = self.left_view.shape[:2]
            # TODO: Implement actual SBS composition
            image_to_display = self.left_view
        
        elif mode == 'Left View' and self.left_view is not None:
            image_to_display = self.left_view
        
        elif mode == 'Right View' and self.right_view is not None:
            image_to_display = self.right_view
        
        if image_to_display is not None:
            self.display_image(image_to_display)
        else:
            self.image_label.setText('No preview available')
    
    def display_image(self, image: np.ndarray):
        """
        Display image in label
        
        Args:
            image: Image to display (H, W, 3) RGB
        """
        h, w, c = image.shape
        bytes_per_line = c * w
        
        # Convert to QImage
        q_image = QImage(
            image.data,
            w, h,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )
        
        # Convert to QPixmap and display
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale to fit label
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        self.info_label.setText(f'Resolution: {w}x{h}')
    
    def clear(self):
        """Clear all previews"""
        self.current_image = None
        self.depth_map = None
        self.left_view = None
        self.right_view = None
        
        self.image_label.clear()
        self.image_label.setText('No image loaded')
        self.info_label.setText('')
