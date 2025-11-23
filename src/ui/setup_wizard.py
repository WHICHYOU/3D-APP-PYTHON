"""
Setup Wizard Dialog

First-time setup screen for downloading dependencies.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QGroupBox, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import logging

logger = logging.getLogger(__name__)


class DownloadWorker(QThread):
    """Worker thread for downloading dependencies."""
    
    progress_updated = pyqtSignal(int, int, str)  # downloaded, total, message
    download_finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, dependency_manager, download_type):
        super().__init__()
        self.dependency_manager = dependency_manager
        self.download_type = download_type
    
    def run(self):
        """Run download."""
        try:
            if self.download_type == "ai_model":
                success = self.dependency_manager.download_ai_model(
                    progress_callback=self._on_progress
                )
                if success:
                    self.download_finished.emit(True, "AI model ready!")
                else:
                    self.download_finished.emit(False, "AI model download failed")
            
            elif self.download_type == "ffmpeg":
                success = self.dependency_manager.download_ffmpeg(
                    progress_callback=self._on_progress
                )
                if success:
                    self.download_finished.emit(True, "FFmpeg ready!")
                else:
                    self.download_finished.emit(False, "FFmpeg download failed")
            
            elif self.download_type == "ffprobe":
                success = self.dependency_manager.download_ffprobe(
                    progress_callback=self._on_progress
                )
                if success:
                    self.download_finished.emit(True, "ffprobe ready!")
                else:
                    self.download_finished.emit(False, "ffprobe download failed")
            
        except Exception as e:
            logger.error(f"Download error: {e}")
            self.download_finished.emit(False, f"Error: {str(e)}")
    
    def _on_progress(self, downloaded, total, message):
        """Handle progress update."""
        self.progress_updated.emit(downloaded, total, message)


class SetupWizard(QDialog):
    """Setup wizard for first-time dependency download."""
    
    def __init__(self, dependency_manager, parent=None):
        super().__init__(parent)
        self.dependency_manager = dependency_manager
        self.download_worker = None
        
        self.setWindowTitle("Setup Required - 2D to 3D Converter")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        self._setup_ui()
        self._check_status()
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Welcome to 2D to 3D Converter")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel(
            "To start converting, you need to download required dependencies.\n"
            "This is a one-time setup that will download approximately 1.4 GB."
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        # Dependencies status
        layout.addWidget(self._create_dependency_group("AI Model (MiDaS)", "ai_model", "~1.3 GB"))
        layout.addWidget(self._create_dependency_group("FFmpeg", "ffmpeg", "~25 MB"))
        layout.addWidget(self._create_dependency_group("ffprobe", "ffprobe", "~10 MB"))
        
        # Progress section
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setMaximumHeight(120)
        self.status_log.setPlaceholderText("Click 'Download All' to begin...")
        progress_layout.addWidget(self.status_log)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.download_all_btn = QPushButton("📥 Download All Dependencies")
        self.download_all_btn.setMinimumHeight(50)
        self.download_all_btn.clicked.connect(self._download_all)
        button_layout.addWidget(self.download_all_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _create_dependency_group(self, name, dep_type, size):
        """Create dependency status group."""
        group = QGroupBox(name)
        layout = QHBoxLayout()
        
        size_label = QLabel(f"Size: {size}")
        size_label.setStyleSheet("color: #666;")
        layout.addWidget(size_label)
        
        layout.addStretch()
        
        status_label = QLabel()
        status_label.setObjectName(f"{dep_type}_status")
        setattr(self, f"{dep_type}_status", status_label)
        layout.addWidget(status_label)
        
        download_btn = QPushButton("Download")
        download_btn.setObjectName(f"{dep_type}_btn")
        download_btn.clicked.connect(lambda: self._download_single(dep_type))
        setattr(self, f"{dep_type}_btn", download_btn)
        layout.addWidget(download_btn)
        
        group.setLayout(layout)
        return group
    
    def _check_status(self):
        """Check and update dependency status."""
        deps = self.dependency_manager.check_all_dependencies()
        
        for dep_type, is_ready in deps.items():
            status_label = getattr(self, f"{dep_type}_status")
            btn = getattr(self, f"{dep_type}_btn")
            
            if is_ready:
                status_label.setText("✅ Ready")
                status_label.setStyleSheet("color: green; font-weight: bold;")
                btn.setEnabled(False)
            else:
                status_label.setText("❌ Not Downloaded")
                status_label.setStyleSheet("color: red; font-weight: bold;")
                btn.setEnabled(True)
        
        # Enable close if all ready
        if self.dependency_manager.is_ready():
            self.download_all_btn.setEnabled(False)
            self.download_all_btn.setText("✅ All Dependencies Ready!")
            self.close_btn.setEnabled(True)
            self.status_log.append("\n✅ All dependencies are ready! You can now use the converter.")
    
    def _download_single(self, dep_type):
        """Download single dependency."""
        self._log(f"Starting {dep_type} download...")
        
        # Disable all buttons
        self.download_all_btn.setEnabled(False)
        self.ai_model_btn.setEnabled(False)
        self.ffmpeg_btn.setEnabled(False)
        self.ffprobe_btn.setEnabled(False)
        
        # Start download
        self.download_worker = DownloadWorker(self.dependency_manager, dep_type)
        self.download_worker.progress_updated.connect(self._on_progress)
        self.download_worker.download_finished.connect(self._on_download_finished)
        self.download_worker.start()
    
    def _download_all(self):
        """Download all missing dependencies."""
        self._log("Starting download of all dependencies...")
        self.download_all_btn.setEnabled(False)
        
        # Start with AI model, then FFmpeg, then ffprobe
        self._download_queue = []
        
        deps = self.dependency_manager.check_all_dependencies()
        if not deps["ai_model"]:
            self._download_queue.append("ai_model")
        if not deps["ffmpeg"]:
            self._download_queue.append("ffmpeg")
        if not deps["ffprobe"]:
            self._download_queue.append("ffprobe")
        
        if self._download_queue:
            self._download_next()
        else:
            self._log("All dependencies already downloaded!")
            self.close_btn.setEnabled(True)
    
    def _download_next(self):
        """Download next item in queue."""
        if not self._download_queue:
            self._log("\n✅ All downloads complete!")
            self._check_status()
            return
        
        dep_type = self._download_queue.pop(0)
        self._download_single(dep_type)
    
    def _on_progress(self, downloaded, total, message):
        """Handle progress update."""
        if total > 0:
            percent = int((downloaded / total) * 100)
            self.progress_bar.setValue(percent)
        
        self._log(message)
    
    def _on_download_finished(self, success, message):
        """Handle download completion."""
        self._log(f"\n{message}\n")
        
        self._check_status()
        
        # Re-enable buttons
        self.ai_model_btn.setEnabled(not self.dependency_manager.is_model_downloaded())
        self.ffmpeg_btn.setEnabled(not self.dependency_manager.is_ffmpeg_downloaded())
        self.ffprobe_btn.setEnabled(not self.dependency_manager.is_ffprobe_downloaded())
        
        # If downloading all, continue to next
        if hasattr(self, '_download_queue'):
            self._download_next()
        else:
            self.download_all_btn.setEnabled(True)
    
    def _log(self, message):
        """Add message to log."""
        self.status_log.append(message)
        self.status_log.verticalScrollBar().setValue(
            self.status_log.verticalScrollBar().maximum()
        )
