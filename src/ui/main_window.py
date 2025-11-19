"""
Main Window Module

The primary application window for the desktop GUI.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QFileDialog, QMessageBox, QStatusBar,
    QMenuBar, QMenu, QToolBar, QPushButton, QLabel,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QMimeData
from PyQt6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.current_file = None
        self.input_files = []
        self._setup_ui()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        
        # Set window properties
        self.setWindowTitle("2D to 3D Converter")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        logger.info("MainWindow initialized")
    
    def _setup_ui(self):
        """Setup user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - File list and settings
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Preview area
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def _create_left_panel(self):
        """Create left panel with file list and settings."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # File list section
        file_list_label = QLabel("<b>Input Files</b>")
        layout.addWidget(file_list_label)
        
        # File list widget
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.itemSelectionChanged.connect(self._on_file_selected)
        layout.addWidget(self.file_list)
        
        # File operation buttons
        button_layout = QHBoxLayout()
        
        self.add_files_btn = QPushButton("Add Files")
        self.add_files_btn.clicked.connect(self._add_files)
        button_layout.addWidget(self.add_files_btn)
        
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self._add_folder)
        button_layout.addWidget(self.add_folder_btn)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self._remove_selected)
        self.remove_btn.setEnabled(False)
        button_layout.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self._clear_all)
        self.clear_btn.setEnabled(False)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # Drag and drop hint
        hint_label = QLabel("💡 Tip: Drag & drop files here")
        hint_label.setStyleSheet("color: gray; font-size: 11px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)
        
        # Settings section
        settings_label = QLabel("<b>Conversion Settings</b>")
        layout.addWidget(settings_label)
        
        # Import settings panel
        from .settings_panel import SettingsPanel
        self.settings_panel = SettingsPanel()
        layout.addWidget(self.settings_panel)
        
        # Conversion buttons
        convert_layout = QVBoxLayout()
        
        self.convert_btn = QPushButton("Convert Selected")
        self.convert_btn.setEnabled(False)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.convert_btn.clicked.connect(self._start_conversion)
        convert_layout.addWidget(self.convert_btn)
        
        self.batch_convert_btn = QPushButton("Convert All")
        self.batch_convert_btn.setEnabled(False)
        self.batch_convert_btn.clicked.connect(self._start_batch_conversion)
        convert_layout.addWidget(self.batch_convert_btn)
        
        layout.addLayout(convert_layout)
        
        return panel
    
    def _create_right_panel(self):
        """Create right panel with preview area."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Preview label
        preview_label = QLabel("<b>Preview</b>")
        layout.addWidget(preview_label)
        
        # Import preview widget
        from .preview_widget import PreviewWidget
        self.preview_widget = PreviewWidget()
        layout.addWidget(self.preview_widget)
        
        # Preview controls
        control_layout = QHBoxLayout()
        
        self.refresh_preview_btn = QPushButton("Refresh Preview")
        self.refresh_preview_btn.setEnabled(False)
        self.refresh_preview_btn.clicked.connect(self._refresh_preview)
        control_layout.addWidget(self.refresh_preview_btn)
        
        self.save_preview_btn = QPushButton("Save Preview")
        self.save_preview_btn.setEnabled(False)
        self.save_preview_btn.clicked.connect(self._save_preview)
        control_layout.addWidget(self.save_preview_btn)
        
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        return panel
    
    def _create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        add_files_action = QAction("&Add Files...", self)
        add_files_action.setShortcut("Ctrl+O")
        add_files_action.triggered.connect(self._add_files)
        file_menu.addAction(add_files_action)
        
        add_folder_action = QAction("Add &Folder...", self)
        add_folder_action.setShortcut("Ctrl+Shift+O")
        add_folder_action.triggered.connect(self._add_folder)
        file_menu.addAction(add_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        clear_action = QAction("&Clear All", self)
        clear_action.triggered.connect(self._clear_all)
        edit_menu.addAction(clear_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        batch_action = QAction("&Batch Manager", self)
        batch_action.triggered.connect(self._open_batch_manager)
        tools_menu.addAction(batch_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        guide_action = QAction("User &Guide", self)
        guide_action.triggered.connect(self._show_guide)
        help_menu.addAction(guide_action)
    
    def _create_toolbar(self):
        """Create toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Add files action
        add_action = QAction("Add Files", self)
        add_action.triggered.connect(self._add_files)
        toolbar.addAction(add_action)
        
        # Add folder action
        folder_action = QAction("Add Folder", self)
        folder_action.triggered.connect(self._add_folder)
        toolbar.addAction(folder_action)
        
        toolbar.addSeparator()
        
        # Convert action
        convert_action = QAction("Convert", self)
        convert_action.triggered.connect(self._start_conversion)
        toolbar.addAction(convert_action)
    
    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    # File management methods
    
    def _add_files(self):
        """Add files through file dialog."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter(
            "Media Files (*.jpg *.jpeg *.png *.bmp *.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            self._add_file_paths(files)
    
    def _add_folder(self):
        """Add all media files from a folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            folder_path = Path(folder)
            media_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.mp4', '.avi', '.mov', '.mkv'}
            files = [str(f) for f in folder_path.iterdir() 
                    if f.suffix.lower() in media_extensions]
            self._add_file_paths(files)
    
    def _add_file_paths(self, file_paths):
        """Add file paths to the list."""
        added_count = 0
        for file_path in file_paths:
            if file_path not in self.input_files:
                self.input_files.append(file_path)
                item = QListWidgetItem(Path(file_path).name)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.file_list.addItem(item)
                added_count += 1
        
        if added_count > 0:
            self.status_bar.showMessage(f"Added {added_count} file(s)")
            self.convert_btn.setEnabled(True)
            self.batch_convert_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)
            logger.info(f"Added {added_count} files")
    
    def _remove_selected(self):
        """Remove selected files from list."""
        selected_items = self.file_list.selectedItems()
        for item in selected_items:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            self.input_files.remove(file_path)
            self.file_list.takeItem(self.file_list.row(item))
        
        self.status_bar.showMessage(f"Removed {len(selected_items)} file(s)")
        self._update_button_states()
    
    def _clear_all(self):
        """Clear all files from list."""
        self.input_files.clear()
        self.file_list.clear()
        self.current_file = None
        self.preview_widget.clear_preview()
        self._update_button_states()
        self.status_bar.showMessage("Cleared all files")
    
    def _update_button_states(self):
        """Update button enabled states."""
        has_files = len(self.input_files) > 0
        has_selection = len(self.file_list.selectedItems()) > 0
        
        self.convert_btn.setEnabled(has_selection)
        self.batch_convert_btn.setEnabled(has_files)
        self.clear_btn.setEnabled(has_files)
        self.remove_btn.setEnabled(has_selection)
    
    def _on_file_selected(self):
        """Handle file selection change."""
        selected_items = self.file_list.selectedItems()
        if selected_items:
            self.current_file = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.refresh_preview_btn.setEnabled(True)
            self._load_preview()
        else:
            self.current_file = None
            self.refresh_preview_btn.setEnabled(False)
        
        self._update_button_states()
    
    # Preview methods
    
    def _load_preview(self):
        """Load preview of selected file."""
        if self.current_file:
            self.status_bar.showMessage(f"Loading preview: {Path(self.current_file).name}")
            self.preview_widget.load_file(self.current_file)
            self.save_preview_btn.setEnabled(True)
    
    def _refresh_preview(self):
        """Refresh preview with current settings."""
        if self.current_file:
            settings = self.settings_panel.get_settings()
            self.status_bar.showMessage("Refreshing preview...")
            self.preview_widget.update_preview(settings)
    
    def _save_preview(self):
        """Save current preview."""
        if self.current_file:
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Preview",
                str(Path(self.current_file).stem) + "_preview.png",
                "PNG Files (*.png);;JPEG Files (*.jpg)"
            )
            if output_path:
                self.preview_widget.save_preview(output_path)
                self.status_bar.showMessage(f"Preview saved: {Path(output_path).name}")
    
    # Conversion methods
    
    def _start_conversion(self):
        """Start conversion of selected files."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select files to convert.")
            return
        
        files_to_convert = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        settings = self.settings_panel.get_settings()
        
        # Import and show progress dialog
        from .progress_dialog import ProgressDialog
        dialog = ProgressDialog(files_to_convert, settings, self)
        dialog.exec()
    
    def _start_batch_conversion(self):
        """Start batch conversion of all files."""
        if not self.input_files:
            QMessageBox.warning(self, "No Files", "Please add files to convert.")
            return
        
        settings = self.settings_panel.get_settings()
        
        # Import and show progress dialog
        from .progress_dialog import ProgressDialog
        dialog = ProgressDialog(self.input_files, settings, self)
        dialog.exec()
    
    def _open_batch_manager(self):
        """Open batch manager dialog."""
        from .batch_manager import BatchManagerDialog
        dialog = BatchManagerDialog(self)
        dialog.exec()
    
    # Help methods
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About 2D to 3D Converter",
            "<h3>2D to 3D Converter</h3>"
            "<p>Version 1.0.0 (Phase 4)</p>"
            "<p>Convert 2D images and videos to stereoscopic 3D formats using AI-powered depth estimation.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>AI depth estimation (MiDaS v3.1)</li>"
            "<li>Multiple output formats (Half SBS, Full SBS, Anaglyph, Top-Bottom)</li>"
            "<li>GPU acceleration (CUDA/MPS/CPU)</li>"
            "<li>Video conversion with temporal filtering</li>"
            "</ul>"
            "<p>© 2024 - Built with PyQt6 and PyTorch</p>"
        )
    
    def _show_guide(self):
        """Show user guide."""
        QMessageBox.information(
            self,
            "User Guide",
            "<h3>Quick Start Guide</h3>"
            "<p><b>1. Add Files:</b> Click 'Add Files' or drag & drop media files</p>"
            "<p><b>2. Adjust Settings:</b> Configure depth intensity, format, and other options</p>"
            "<p><b>3. Preview:</b> Select a file to see preview with current settings</p>"
            "<p><b>4. Convert:</b> Click 'Convert Selected' or 'Convert All'</p>"
            "<br>"
            "<p><b>Supported Formats:</b></p>"
            "<ul>"
            "<li>Images: JPG, PNG, BMP</li>"
            "<li>Videos: MP4, AVI, MOV, MKV</li>"
            "</ul>"
            "<br>"
            "<p>For detailed documentation, see VIDEO_CONVERSION_GUIDE.md</p>"
        )
    
    # Drag and drop support
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if Path(file_path).is_file():
                files.append(file_path)
        
        if files:
            self._add_file_paths(files)
            event.acceptProposedAction()
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMenuBar, QMenu,
    QStatusBar, QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional


class MainWindow(QMainWindow):
    """Main application window"""
    
    # Signals
    file_selected = pyqtSignal(str)
    conversion_requested = pyqtSignal()
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        
        self.current_file = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('2D to 3D Converter')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Top toolbar
        toolbar = self.create_toolbar()
        main_layout.addLayout(toolbar)
        
        # Content area with splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Preview
        # TODO: Add preview widget
        preview_label = QLabel('Preview Area')
        preview_label.setStyleSheet('border: 1px solid #ccc; background: #f0f0f0;')
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_splitter.addWidget(preview_label)
        
        # Right panel - Settings
        # TODO: Add settings panel
        settings_label = QLabel('Settings Panel')
        settings_label.setStyleSheet('border: 1px solid #ccc; background: #f0f0f0;')
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_splitter.addWidget(settings_label)
        
        content_splitter.setStretchFactor(0, 2)
        content_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.statusBar().showMessage('Ready')
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        # TODO: Add menu actions
        # open_action = QAction('&Open', self)
        # file_menu.addAction(open_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('&Edit')
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
    
    def create_toolbar(self) -> QHBoxLayout:
        """
        Create top toolbar
        
        Returns:
            Toolbar layout
        """
        toolbar = QHBoxLayout()
        
        # Open file button
        open_btn = QPushButton('Open File')
        open_btn.clicked.connect(self.open_file)
        toolbar.addWidget(open_btn)
        
        # Convert button
        convert_btn = QPushButton('Convert to 3D')
        convert_btn.clicked.connect(self.start_conversion)
        convert_btn.setEnabled(False)
        self.convert_btn = convert_btn
        toolbar.addWidget(convert_btn)
        
        toolbar.addStretch()
        
        # License info
        license_label = QLabel('Free Tier')
        toolbar.addWidget(license_label)
        
        return toolbar
    
    def open_file(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select Image or Video',
            '',
            'Media Files (*.mp4 *.avi *.mov *.jpg *.png);;All Files (*)'
        )
        
        if file_path:
            self.current_file = file_path
            self.file_selected.emit(file_path)
            self.convert_btn.setEnabled(True)
            self.statusBar().showMessage(f'Loaded: {file_path}')
    
    def start_conversion(self):
        """Start conversion process"""
        if self.current_file:
            self.conversion_requested.emit()
            self.statusBar().showMessage('Converting...')
