"""
Settings Panel
User adjustable parameters
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QComboBox, QGroupBox, QPushButton, QCheckBox, QToolButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon
from typing import Dict, Optional


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
        
        # Load model registry
        from ..ai_core.depth_estimation import MODEL_REGISTRY, DEFAULT_MODEL
        self.model_registry = MODEL_REGISTRY
        self.default_model = DEFAULT_MODEL
        
        self.settings = {
            'model_type': DEFAULT_MODEL,
            'depth_intensity': 75,
            'ipd': 65,
            'output_format': 'half_sbs',
            'quality': 'high',
            'hole_filling': True,
        }
        
        # Load saved preferences
        self._load_preferences()
        
        self.init_ui()
    
    def _load_preferences(self):
        """Load saved preferences from config"""
        try:
            from ..utils.config_manager import ConfigManager
            config = ConfigManager()
            
            # Load model preference
            model = config.get('depth_estimation.model', self.default_model)
            if model in self.model_registry:
                self.settings['model_type'] = model
            
            # Load other settings
            self.settings['depth_intensity'] = config.get('rendering.depth_intensity', 75)
            self.settings['ipd'] = config.get('rendering.ipd', 65)
            
        except Exception as e:
            print(f"Could not load preferences: {e}")
    
    def _save_preferences(self):
        """Save current settings to config"""
        try:
            from ..utils.config_manager import ConfigManager
            config = ConfigManager()
            
            config.set('depth_estimation.model', self.settings['model_type'])
            config.set('rendering.depth_intensity', self.settings['depth_intensity'])
            config.set('rendering.ipd', self.settings['ipd'])
            config.save()
            
        except Exception as e:
            print(f"Could not save preferences: {e}")
    
    def init_ui(self):
        """Initialize user interface"""
        # Create scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Model Selection Group (NEW - First priority)
        model_group = self.create_model_selection()
        layout.addWidget(model_group)
        
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
        
        scroll.setWidget(content)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_model_selection(self) -> QGroupBox:
        """
        Create model selection group with help tooltips
        
        Returns:
            Group box widget
        """
        group = QGroupBox('AI Model Selection')
        layout = QVBoxLayout(group)
        
        # Info label
        info_label = QLabel(
            '<i>Choose the AI model for depth estimation. '
            'Faster models are better for quick conversions, '
            'while larger models provide higher quality.</i>'
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet('color: #666; padding: 5px;')
        layout.addWidget(info_label)
        
        # Model dropdown with help button
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel('Model:'))
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(250)
        
        # Populate models
        for model_id, model_info in self.model_registry.items():
            self.model_combo.addItem(model_info['name'], model_id)
        
        # Set current model
        current_index = 0
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == self.settings['model_type']:
                current_index = i
                break
        self.model_combo.setCurrentIndex(current_index)
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        
        model_layout.addWidget(self.model_combo)
        
        # Help button
        help_btn = QToolButton()
        help_btn.setText('?')
        help_btn.setStyleSheet("""
            QToolButton {
                background-color: #2196F3;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                padding: 2px;
                min-width: 20px;
                min-height: 20px;
                max-width: 20px;
                max-height: 20px;
            }
            QToolButton:hover {
                background-color: #1976D2;
            }
        """)
        help_btn.setToolTip('Click for detailed model information')
        help_btn.clicked.connect(self.show_model_help)
        model_layout.addWidget(help_btn)
        
        model_layout.addStretch()
        layout.addLayout(model_layout)
        
        # Model info display
        self.model_info_label = QLabel()
        self.model_info_label.setWordWrap(True)
        self.model_info_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin-top: 5px;
            }
        """)
        layout.addWidget(self.model_info_label)
        
        # Update info for current model
        self.update_model_info()
        
        return group
    
    def update_model_info(self):
        """Update the model information display"""
        model_id = self.model_combo.currentData()
        if model_id and model_id in self.model_registry:
            info = self.model_registry[model_id]
            
            html = f"""
            <b>Description:</b> {info['description']}<br><br>
            <b>⚡ Speed:</b> {info['speed']}<br>
            <b>🎨 Quality:</b> {info['quality']}<br>
            <b>💾 VRAM:</b> {info['vram']}<br>
            <b>📦 Size:</b> {info['model_size']}<br>
            <b>✅ Best for:</b> {info['recommended']}
            """
            
            self.model_info_label.setText(html)
    
    def show_model_help(self):
        """Show detailed model comparison dialog"""
        from PyQt6.QtWidgets import QDialog, QTextBrowser
        
        dialog = QDialog(self)
        dialog.setWindowTitle('AI Model Comparison Guide')
        dialog.resize(700, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Create text browser for rich content
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        
        # Build comparison HTML
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 10px; }
                h2 { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px; }
                h3 { color: #555; margin-top: 15px; }
                .model-card {
                    background: #f9f9f9;
                    border-left: 4px solid #2196F3;
                    padding: 10px;
                    margin: 10px 0;
                }
                .recommended { border-left-color: #4CAF50; background: #f1f8f4; }
                .fastest { border-left-color: #FF9800; }
                .quality { border-left-color: #9C27B0; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #2196F3; color: white; }
                .speed-fast { color: #4CAF50; font-weight: bold; }
                .speed-medium { color: #FF9800; font-weight: bold; }
                .speed-slow { color: #F44336; font-weight: bold; }
            </style>
        </head>
        <body>
            <h2>🤖 AI Model Selection Guide</h2>
            <p>Choose the right model based on your needs:</p>
            
            <h3>Quick Comparison</h3>
            <table>
                <tr>
                    <th>Model</th>
                    <th>Speed (FPS)</th>
                    <th>Quality</th>
                    <th>VRAM</th>
                    <th>Use Case</th>
                </tr>
        """
        
        # Add each model
        speed_class_map = {
            'Very Fast': 'speed-fast',
            'Fast': 'speed-fast',
            'Medium': 'speed-medium',
            'Slow': 'speed-slow'
        }
        
        for model_id, info in self.model_registry.items():
            speed_parts = info['speed'].split('(')
            speed_label = speed_parts[0].strip()
            speed_class = speed_class_map.get(speed_label, '')
            
            html += f"""
                <tr>
                    <td><b>{info['name']}</b></td>
                    <td class="{speed_class}">{info['speed']}</td>
                    <td>{info['quality']}</td>
                    <td>{info['vram']}</td>
                    <td>{info['recommended']}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h3>Detailed Model Information</h3>
        """
        
        # Add detailed cards for each model
        for model_id, info in self.model_registry.items():
            card_class = 'model-card'
            if 'hybrid' in model_id:
                card_class += ' recommended'
            elif 'small' in model_id or 'tiny' in model_id:
                card_class += ' fastest'
            elif 'large' in model_id:
                card_class += ' quality'
            
            html += f"""
            <div class="{card_class}">
                <h3>{info['name']}</h3>
                <p><b>Description:</b> {info['description']}</p>
                <p>
                    <b>⚡ Speed:</b> {info['speed']} &nbsp;&nbsp;
                    <b>🎨 Quality:</b> {info['quality']}<br>
                    <b>💾 VRAM Required:</b> {info['vram']} &nbsp;&nbsp;
                    <b>📦 Download Size:</b> {info['model_size']}<br>
                    <b>✅ Recommended for:</b> {info['recommended']}
                </p>
            </div>
            """
        
        html += """
            <h3>💡 Tips for Choosing</h3>
            <ul>
                <li><b>For Quick Tests:</b> Use MiDaS Small or Swin2-Tiny</li>
                <li><b>For Most Users:</b> MiDaS Hybrid offers the best balance</li>
                <li><b>For High Quality:</b> Use Swin2-Large or MiDaS Large</li>
                <li><b>Limited VRAM?</b> Choose Small or Tiny models</li>
                <li><b>Processing Many Videos?</b> Faster models save significant time</li>
            </ul>
            
            <h3>Performance Notes</h3>
            <p>
                <b>FPS (Frames Per Second)</b> indicates how many video frames can be processed 
                per second on a typical gaming GPU (like RTX 3090). Actual speed depends on:
            </p>
            <ul>
                <li>Your GPU model and VRAM</li>
                <li>Video resolution (higher = slower)</li>
                <li>Other running applications</li>
                <li>CPU and RAM capacity</li>
            </ul>
            
            <p><i>You can change the model at any time in Settings.</i></p>
        </body>
        </html>
        """
        
        browser.setHtml(html)
        layout.addWidget(browser)
        
        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def on_model_changed(self, index):
        """Handle model selection change"""
        model_id = self.model_combo.currentData()
        if model_id:
            self.settings['model_type'] = model_id
            self.update_model_info()
            self._save_preferences()
            self.on_settings_changed()
    
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
        # Reset model to default
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == self.default_model:
                self.model_combo.setCurrentIndex(i)
                break
        
        self.intensity_slider.setValue(75)
        self.ipd_slider.setValue(65)
        self.format_combo.setCurrentIndex(0)
        self.quality_combo.setCurrentText('High')
        self.hole_filling_check.setChecked(True)
        
        self._save_preferences()
    
    def get_settings(self) -> dict:
        """
        Get current settings
        
        Returns:
            Settings dictionary
        """
        return self.settings.copy()
