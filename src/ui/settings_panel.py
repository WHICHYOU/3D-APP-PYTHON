"""
Settings Panel
User adjustable parameters
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QComboBox, QGroupBox, QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal


class SettingsPanel(QWidget):
    """Panel for adjusting conversion settings"""
    
    # Signals
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        Initialize settings panel
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.settings = {
            'depth_intensity': 75,
            'ipd': 65,
            'output_format': 'half_sbs',
            'quality': 'high',
            'hole_filling': True,
        }
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Depth Settings Group
        depth_group = self.create_depth_settings()
        layout.addWidget(depth_group)
        
        # Stereoscopy Settings Group
        stereo_group = self.create_stereo_settings()
        layout.addWidget(stereo_group)
        
        # Output Settings Group
        output_group = self.create_output_settings()
        layout.addWidget(output_group)
        
        layout.addStretch()
        
        # Reset button
        reset_btn = QPushButton('Reset to Defaults')
        reset_btn.clicked.connect(self.reset_to_defaults)
        layout.addWidget(reset_btn)
    
    def create_depth_settings(self) -> QGroupBox:
        """
        Create depth settings group
        
        Returns:
            Group box widget
        """
        group = QGroupBox('Depth Settings')
        layout = QVBoxLayout(group)
        
        # Depth intensity slider
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel('Depth Intensity:'))
        
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(75)
        self.intensity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.intensity_slider.setTickInterval(10)
        self.intensity_slider.valueChanged.connect(self.on_intensity_changed)
        
        self.intensity_label = QLabel('75')
        self.intensity_label.setMinimumWidth(30)
        
        intensity_layout.addWidget(self.intensity_slider)
        intensity_layout.addWidget(self.intensity_label)
        
        layout.addLayout(intensity_layout)
        
        # Hole filling checkbox
        self.hole_filling_check = QCheckBox('Enable Hole Filling')
        self.hole_filling_check.setChecked(True)
        self.hole_filling_check.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.hole_filling_check)
        
        return group
    
    def create_stereo_settings(self) -> QGroupBox:
        """
        Create stereoscopy settings group
        
        Returns:
            Group box widget
        """
        group = QGroupBox('Stereoscopy Settings')
        layout = QVBoxLayout(group)
        
        # IPD slider
        ipd_layout = QHBoxLayout()
        ipd_layout.addWidget(QLabel('IPD (mm):'))
        
        self.ipd_slider = QSlider(Qt.Orientation.Horizontal)
        self.ipd_slider.setRange(50, 80)
        self.ipd_slider.setValue(65)
        self.ipd_slider.valueChanged.connect(self.on_ipd_changed)
        
        self.ipd_label = QLabel('65')
        self.ipd_label.setMinimumWidth(30)
        
        ipd_layout.addWidget(self.ipd_slider)
        ipd_layout.addWidget(self.ipd_label)
        
        layout.addLayout(ipd_layout)
        
        return group
    
    def create_output_settings(self) -> QGroupBox:
        """
        Create output settings group
        
        Returns:
            Group box widget
        """
        group = QGroupBox('Output Settings')
        layout = QVBoxLayout(group)
        
        # Output format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel('Format:'))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            'Half Side-by-Side',
            'Full Side-by-Side',
            'Top-Bottom',
            'Anaglyph (Red-Cyan)',
        ])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # Quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel('Quality:'))
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(['Low', 'Medium', 'High', 'Ultra'])
        self.quality_combo.setCurrentText('High')
        self.quality_combo.currentTextChanged.connect(self.on_settings_changed)
        
        quality_layout.addWidget(self.quality_combo)
        layout.addLayout(quality_layout)
        
        return group
    
    def on_intensity_changed(self, value: int):
        """Handle depth intensity change"""
        self.intensity_label.setText(str(value))
        self.settings['depth_intensity'] = value
        self.on_settings_changed()
    
    def on_ipd_changed(self, value: int):
        """Handle IPD change"""
        self.ipd_label.setText(str(value))
        self.settings['ipd'] = value
        self.on_settings_changed()
    
    def on_format_changed(self, format_text: str):
        """Handle output format change"""
        format_map = {
            'Half Side-by-Side': 'half_sbs',
            'Full Side-by-Side': 'full_sbs',
            'Top-Bottom': 'top_bottom',
            'Anaglyph (Red-Cyan)': 'anaglyph',
        }
        self.settings['output_format'] = format_map.get(format_text, 'half_sbs')
        self.on_settings_changed()
    
    def on_settings_changed(self):
        """Emit settings changed signal"""
        self.settings['hole_filling'] = self.hole_filling_check.isChecked()
        self.settings['quality'] = self.quality_combo.currentText().lower()
        
        self.settings_changed.emit(self.settings.copy())
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.intensity_slider.setValue(75)
        self.ipd_slider.setValue(65)
        self.format_combo.setCurrentIndex(0)
        self.quality_combo.setCurrentText('High')
        self.hole_filling_check.setChecked(True)
    
    def get_settings(self) -> dict:
        """
        Get current settings
        
        Returns:
            Settings dictionary
        """
        return self.settings.copy()
