"""
Update Dialog UI
---------------
PyQt6 dialog for notifying users about updates.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from typing import Dict, Optional


class DownloadThread(QThread):
    """Background thread for downloading updates"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)
    
    def __init__(self, updater):
        super().__init__()
        self.updater = updater
    
    def run(self):
        """Download update in background"""
        success = self.updater.download_update(
            progress_callback=self.progress.emit
        )
        self.finished.emit(success)


class UpdateDialog(QDialog):
    """Dialog for update notification and installation"""
    
    def __init__(self, update_info: Dict, updater, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.updater = updater
        self.download_thread = None
        
        self.setWindowTitle("Update Available")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel(f"Version {self.update_info['version']} Available")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Current version
        current_label = QLabel(
            f"Current version: {self.updater.CURRENT_VERSION}"
        )
        layout.addWidget(current_label)
        
        # Release notes
        notes_label = QLabel("What's New:")
        notes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(notes_label)
        
        notes_text = QTextEdit()
        notes_text.setReadOnly(True)
        notes_text.setMaximumHeight(200)
        notes_text.setPlainText(
            self.update_info.get("release_notes", "No release notes available")
        )
        layout.addWidget(notes_text)
        
        # Download info
        system = self._get_platform_key()
        download_info = self.update_info.get("downloads", {}).get(system, {})
        size_mb = download_info.get("size", 0) / (1024 * 1024)
        
        size_label = QLabel(f"Download size: {size_mb:.1f} MB")
        size_label.setStyleSheet("color: #666;")
        layout.addWidget(size_label)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Skip this version checkbox
        self.skip_checkbox = QCheckBox("Skip this version")
        layout.addWidget(self.skip_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.later_button = QPushButton("Remind Me Later")
        self.later_button.clicked.connect(self.on_later)
        button_layout.addWidget(self.later_button)
        
        self.download_button = QPushButton("Download Update")
        self.download_button.setDefault(True)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        self.download_button.clicked.connect(self.on_download)
        button_layout.addWidget(self.download_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _get_platform_key(self) -> str:
        """Get platform key for downloads"""
        import platform
        system = platform.system()
        if system == "Darwin":
            return "macos"
        elif system == "Windows":
            return "windows"
        else:
            return "linux"
    
    def on_later(self):
        """Handle 'Remind Me Later' button"""
        if self.skip_checkbox.isChecked():
            self.updater.skip_version(self.update_info["version"])
        self.reject()
    
    def on_download(self):
        """Handle 'Download Update' button"""
        # Disable buttons
        self.download_button.setEnabled(False)
        self.later_button.setEnabled(False)
        self.skip_checkbox.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.status_label.setText("Downloading update...")
        self.status_label.setVisible(True)
        
        # Start download in background
        self.download_thread = DownloadThread(self.updater)
        self.download_thread.progress.connect(self.on_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()
    
    def on_progress(self, value: int):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        self.status_label.setText(f"Downloading update... {value}%")
    
    def on_download_finished(self, success: bool):
        """Handle download completion"""
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("Download complete!")
            
            # Show install button
            self.download_button.setText("Install and Restart")
            self.download_button.setEnabled(True)
            self.download_button.clicked.disconnect()
            self.download_button.clicked.connect(self.on_install)
            
            self.later_button.setText("Install Later")
            self.later_button.setEnabled(True)
        else:
            self.status_label.setText("Download failed. Please try again.")
            self.status_label.setStyleSheet("color: red;")
            
            self.download_button.setText("Retry")
            self.download_button.setEnabled(True)
            self.download_button.clicked.disconnect()
            self.download_button.clicked.connect(self.on_download)
            
            self.later_button.setEnabled(True)
    
    def on_install(self):
        """Handle 'Install and Restart' button"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Install Update",
            "The application will now restart to install the update. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Install update (this will restart the app)
            self.updater.install_update()
            self.accept()


class UpdateCheckDialog(QDialog):
    """Simple dialog for manual update check"""
    
    def __init__(self, updater, parent=None):
        super().__init__(parent)
        self.updater = updater
        
        self.setWindowTitle("Check for Updates")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.init_ui()
        self.check_updates()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Checking for updates...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
    
    def check_updates(self):
        """Check for updates"""
        from PyQt6.QtCore import QTimer
        
        # Simulate async check (in real app, use QThread)
        QTimer.singleShot(1000, self._perform_check)
    
    def _perform_check(self):
        """Perform the actual check"""
        if self.updater.check_for_updates(force=True):
            update_info = self.updater.get_update_info()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            
            self.status_label.setText(
                f"Update available: v{update_info['version']}"
            )
            
            # Show update dialog
            dialog = UpdateDialog(update_info, self.updater, self)
            dialog.exec()
            self.accept()
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.status_label.setText("You're up to date!")
            self.close_button.setEnabled(True)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    # Test update dialog
    app = QApplication(sys.argv)
    
    # Mock update info
    mock_info = {
        "version": "1.1.0",
        "release_date": "2025-12-01",
        "release_notes": """
• New: Improved depth estimation quality
• New: Batch processing performance boost
• Fix: Memory leak in video conversion
• Fix: GUI responsiveness improvements
        """,
        "downloads": {
            "macos": {
                "url": "https://example.com/update.dmg",
                "size": 89128960,
                "sha256": "abc123..."
            }
        }
    }
    
    from src.update.updater import UpdateManager
    updater = UpdateManager()
    
    dialog = UpdateDialog(mock_info, updater)
    dialog.exec()
    
    sys.exit(0)
