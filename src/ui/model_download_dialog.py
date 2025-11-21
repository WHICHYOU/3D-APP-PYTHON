"""
Model Download Dialog

Shows progress when AI models are being downloaded on first run.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar,
    QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ModelDownloadThread(QThread):
    """Thread for downloading models with progress updates."""
    
    progress_updated = pyqtSignal(str)  # status message
    download_finished = pyqtSignal(bool, str)  # success, message
    
    def run(self):
        """Download models in background."""
        try:
            self.progress_updated.emit("Checking torch.hub cache...")
            
            # Import torch
            import torch
            
            self.progress_updated.emit("Downloading MiDaS DPT-Large model (~1.3 GB)...")
            self.progress_updated.emit("This may take 5-30 minutes depending on your connection.")
            self.progress_updated.emit("")
            
            # Download model (this will use cached version if available)
            model = torch.hub.load(
                "intel-isl/MiDaS",
                "DPT_Large",
                pretrained=True,
                trust_repo=True
            )
            
            self.progress_updated.emit("Downloading transforms...")
            transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
            
            self.progress_updated.emit("")
            self.progress_updated.emit("✓ Models downloaded successfully!")
            self.progress_updated.emit("Future conversions will use cached models.")
            
            self.download_finished.emit(True, "Models ready")
            
        except Exception as e:
            logger.error(f"Model download failed: {e}")
            self.progress_updated.emit(f"✗ Download failed: {str(e)}")
            self.download_finished.emit(False, str(e))


class ModelDownloadDialog(QDialog):
    """Dialog showing model download progress."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloading AI Models")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        self.download_thread = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<h2>⏳ Downloading AI Models</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Info text
        info = QLabel(
            "The AI models need to be downloaded on first use (~1.3 GB).\n"
            "This is a one-time download. Future conversions will be instant."
        )
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        layout.addSpacing(10)
        
        # Progress bar (indeterminate)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        # Status log
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setMaximumHeight(150)
        layout.addWidget(self.status_log)
        
        # Close button (disabled until download complete)
        self.close_btn = QPushButton("Close")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)
    
    def start_download(self):
        """Start the download process."""
        self.status_log.append("Starting download...")
        
        self.download_thread = ModelDownloadThread()
        self.download_thread.progress_updated.connect(self._on_progress)
        self.download_thread.download_finished.connect(self._on_finished)
        self.download_thread.start()
    
    def _on_progress(self, message):
        """Handle progress update."""
        if message:
            self.status_log.append(message)
    
    def _on_finished(self, success, message):
        """Handle download completion."""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        if success:
            self.status_log.append("")
            self.status_log.append("=" * 50)
            self.status_log.append("✓ Download complete!")
            self.status_log.append("=" * 50)
        else:
            self.status_log.append("")
            self.status_log.append("=" * 50)
            self.status_log.append("✗ Download failed")
            self.status_log.append("=" * 50)
        
        self.close_btn.setEnabled(True)
    
    def showEvent(self, event):
        """Start download when dialog is shown."""
        super().showEvent(event)
        # Start download after a brief delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.start_download)
