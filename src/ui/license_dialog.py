"""
License Dialog UI
----------------
PyQt6 dialog for license activation and management.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QTextEdit, QGroupBox,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from typing import Optional


class ActivationThread(QThread):
    """Background thread for license activation"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, license_manager, license_key):
        super().__init__()
        self.license_manager = license_manager
        self.license_key = license_key
    
    def run(self):
        """Activate license in background"""
        success, message = self.license_manager.activate(self.license_key)
        self.finished.emit(success, message)


class LicenseDialog(QDialog):
    """Dialog for license activation and information"""
    
    license_changed = pyqtSignal()  # Emitted when license status changes
    
    def __init__(self, license_manager, parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.activation_thread = None
        
        self.setWindowTitle("License Management")
        self.setModal(True)
        self.setMinimumWidth(550)
        
        self.init_ui()
        self.update_license_info()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Title
        title = QLabel("License Management")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Current license info group
        self.info_group = QGroupBox("Current License")
        info_layout = QVBoxLayout()
        
        self.tier_label = QLabel()
        self.tier_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.tier_label)
        
        self.status_label = QLabel()
        info_layout.addWidget(self.status_label)
        
        self.expiry_label = QLabel()
        info_layout.addWidget(self.expiry_label)
        
        self.quota_label = QLabel()
        info_layout.addWidget(self.quota_label)
        
        self.features_text = QTextEdit()
        self.features_text.setReadOnly(True)
        self.features_text.setMaximumHeight(120)
        info_layout.addWidget(self.features_text)
        
        self.info_group.setLayout(info_layout)
        layout.addWidget(self.info_group)
        
        # Activation group
        self.activation_group = QGroupBox("Activate License")
        activation_layout = QVBoxLayout()
        
        # License key input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("License Key:"))
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.key_input.textChanged.connect(self._format_key_input)
        key_layout.addWidget(self.key_input)
        
        activation_layout.addLayout(key_layout)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        activation_layout.addWidget(self.progress_bar)
        
        # Status message
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setVisible(False)
        activation_layout.addWidget(self.message_label)
        
        # Activation buttons
        button_layout = QHBoxLayout()
        
        self.activate_button = QPushButton("Activate")
        self.activate_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.activate_button.clicked.connect(self.on_activate)
        button_layout.addWidget(self.activate_button)
        
        self.deactivate_button = QPushButton("Deactivate")
        self.deactivate_button.clicked.connect(self.on_deactivate)
        self.deactivate_button.setVisible(False)
        button_layout.addWidget(self.deactivate_button)
        
        activation_layout.addLayout(button_layout)
        
        self.activation_group.setLayout(activation_layout)
        layout.addWidget(self.activation_group)
        
        # Upgrade section
        upgrade_layout = QHBoxLayout()
        upgrade_label = QLabel("Want more features?")
        upgrade_layout.addWidget(upgrade_label)
        
        self.upgrade_button = QPushButton("Upgrade to Pro")
        self.upgrade_button.clicked.connect(self.on_upgrade)
        upgrade_layout.addWidget(self.upgrade_button)
        
        upgrade_layout.addStretch()
        layout.addLayout(upgrade_layout)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.on_help)
        bottom_layout.addWidget(help_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        bottom_layout.addWidget(close_button)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
    
    def _format_key_input(self, text: str):
        """Format license key input with dashes"""
        # Remove existing dashes
        text = text.replace('-', '').upper()
        
        # Add dashes every 4 characters
        formatted = '-'.join([text[i:i+4] for i in range(0, len(text), 4)])
        
        # Update input if different
        if formatted != self.key_input.text():
            cursor_pos = self.key_input.cursorPosition()
            self.key_input.setText(formatted)
            self.key_input.setCursorPosition(min(cursor_pos, len(formatted)))
    
    def update_license_info(self):
        """Update license information display"""
        info = self.license_manager.get_license_info()
        
        # Update tier
        tier_name = info["tier_name"]
        tier_colors = {
            "FREE": "#666666",
            "PRO": "#007AFF",
            "ENTERPRISE": "#FF9500"
        }
        color = tier_colors.get(tier_name, "#666666")
        self.tier_label.setText(f"<span style='color: {color}'>{tier_name}</span> Edition")
        
        # Update status
        if info["is_activated"]:
            self.status_label.setText("✓ License activated")
            self.status_label.setStyleSheet("color: green;")
            self.activation_group.setVisible(False)
            self.deactivate_button.setVisible(True)
        else:
            self.status_label.setText("✗ No license activated")
            self.status_label.setStyleSheet("color: #999;")
            self.activation_group.setVisible(True)
            self.deactivate_button.setVisible(False)
        
        # Update expiry
        if "days_remaining" in info:
            days = info["days_remaining"]
            if days > 30:
                self.expiry_label.setText(f"Valid for {days} days")
                self.expiry_label.setStyleSheet("")
            elif days > 0:
                self.expiry_label.setText(f"⚠ Expires in {days} days")
                self.expiry_label.setStyleSheet("color: orange;")
            else:
                self.expiry_label.setText("✗ License expired")
                self.expiry_label.setStyleSheet("color: red;")
        else:
            self.expiry_label.setText("")
        
        # Update quota
        if "remaining_quota" in info:
            quota = info["remaining_quota"]
            self.quota_label.setText(f"Remaining today: {quota}/10 conversions")
            if quota == 0:
                self.quota_label.setStyleSheet("color: red; font-weight: bold;")
            elif quota <= 3:
                self.quota_label.setStyleSheet("color: orange;")
            else:
                self.quota_label.setStyleSheet("")
            self.quota_label.setVisible(True)
        else:
            self.quota_label.setText("Unlimited conversions")
            self.quota_label.setStyleSheet("color: green;")
            self.quota_label.setVisible(True)
        
        # Update features
        features_text = self._get_features_text(info["tier"])
        self.features_text.setPlainText(features_text)
        
        # Show/hide upgrade button
        self.upgrade_button.setVisible(info["tier"] == "free")
    
    def _get_features_text(self, tier: str) -> str:
        """Get feature list for tier"""
        if tier == "free":
            return """Features:
• Basic image and video conversion
• 10 conversions per day
• Watermark on output
• Standard quality settings
• Community support"""
        elif tier == "pro":
            return """Features:
• Unlimited conversions
• No watermarks
• Batch processing
• Advanced quality settings
• All export formats
• Priority email support"""
        else:  # enterprise
            return """Features:
• All Pro features
• API access
• Custom branding
• Multi-user licenses
• Priority phone support
• Service Level Agreement"""
    
    def on_activate(self):
        """Handle activation button click"""
        license_key = self.key_input.text().strip()
        
        # Validate format
        if len(license_key.replace('-', '')) != 16:
            QMessageBox.warning(
                self,
                "Invalid Key",
                "Please enter a valid 16-character license key."
            )
            return
        
        # Disable UI during activation
        self.activate_button.setEnabled(False)
        self.key_input.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.message_label.setVisible(False)
        
        # Start activation in background
        self.activation_thread = ActivationThread(
            self.license_manager,
            license_key
        )
        self.activation_thread.finished.connect(self.on_activation_finished)
        self.activation_thread.start()
    
    def on_activation_finished(self, success: bool, message: str):
        """Handle activation completion"""
        # Re-enable UI
        self.activate_button.setEnabled(True)
        self.key_input.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Show message
        self.message_label.setText(message)
        self.message_label.setVisible(True)
        
        if success:
            self.message_label.setStyleSheet("color: green; font-weight: bold;")
            self.key_input.clear()
            
            # Update license info
            self.update_license_info()
            
            # Emit signal
            self.license_changed.emit()
            
            # Show success dialog
            QMessageBox.information(
                self,
                "Activation Successful",
                message
            )
        else:
            self.message_label.setStyleSheet("color: red;")
    
    def on_deactivate(self):
        """Handle deactivation button click"""
        reply = QMessageBox.question(
            self,
            "Deactivate License",
            "Are you sure you want to deactivate this license?\n\n"
            "You can reactivate it on another device.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.license_manager.deactivate()
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.update_license_info()
                self.license_changed.emit()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def on_upgrade(self):
        """Handle upgrade button click"""
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        
        url = self.license_manager.get_upgrade_url()
        QDesktopServices.openUrl(QUrl(url))
    
    def on_help(self):
        """Show help dialog"""
        help_text = """
<h3>License Help</h3>

<h4>Activating a License</h4>
<p>1. Purchase a license key from our website<br>
2. Enter the 16-character key in the format XXXX-XXXX-XXXX-XXXX<br>
3. Click Activate<br>
4. Wait for confirmation</p>

<h4>Deactivating a License</h4>
<p>You can deactivate your license to move it to another computer. 
Pro licenses can be activated on up to 3 devices simultaneously.</p>

<h4>Offline Activation</h4>
<p>If you don't have internet access, the app will activate offline 
with a 7-day grace period. Connect to the internet within 7 days 
to complete activation.</p>

<h4>Support</h4>
<p>Need help? Contact us at:<br>
Email: support@3dconversion.app<br>
Website: https://3dconversion.app/support</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("License Help")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.exec()


class UpgradePromptDialog(QDialog):
    """Simple prompt to upgrade license"""
    
    def __init__(self, feature_name: str, license_manager, parent=None):
        super().__init__(parent)
        self.feature_name = feature_name
        self.license_manager = license_manager
        
        self.setWindowTitle("Upgrade Required")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Icon and message
        message = QLabel(
            f"<h3>Upgrade to Pro</h3>"
            f"<p>The feature <b>{self.feature_name}</b> requires a Pro license.</p>"
            f"<p>Upgrade now to unlock:</p>"
            f"<ul>"
            f"<li>Unlimited conversions</li>"
            f"<li>No watermarks</li>"
            f"<li>Batch processing</li>"
            f"<li>Advanced settings</li>"
            f"<li>Priority support</li>"
            f"</ul>"
        )
        message.setTextFormat(Qt.TextFormat.RichText)
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Pricing
        pricing = QLabel(
            "<p style='text-align: center; font-size: 18px; margin: 20px;'>"
            "<b>$49/year</b> or <b>$5/month</b>"
            "</p>"
        )
        pricing.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(pricing)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        later_button = QPushButton("Maybe Later")
        later_button.clicked.connect(self.reject)
        button_layout.addWidget(later_button)
        
        upgrade_button = QPushButton("Upgrade Now")
        upgrade_button.setDefault(True)
        upgrade_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        upgrade_button.clicked.connect(self.on_upgrade)
        button_layout.addWidget(upgrade_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_upgrade(self):
        """Open upgrade page"""
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        
        url = self.license_manager.get_upgrade_url()
        QDesktopServices.openUrl(QUrl(url))
        self.accept()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    # Test license dialog
    app = QApplication(sys.argv)
    
    from src.license.manager import LicenseManager
    license_manager = LicenseManager()
    
    dialog = LicenseDialog(license_manager)
    dialog.exec()
    
    sys.exit(0)
