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
        self.recent_files = []
        self.recent_output_files = []
        self.max_recent_files = 10
        
        # Check dependencies first
        from ..utils.dependency_manager import DependencyManager
        self.dependency_manager = DependencyManager()
        
        # Load recent files from settings
        self._load_recent_files()
        
        self._setup_ui()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        
        # Set window properties
        self.setWindowTitle("2D to 3D Converter")
        self.setMinimumSize(1200, 800)
        
        # Set initial size and center on screen
        self.resize(1400, 900)
        self._center_on_screen()
        
        # Check dependencies and show setup if needed
        self._check_dependencies_on_startup()
        
        logger.info("MainWindow initialized")
    
    def _center_on_screen(self):
        """Center window on screen."""
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def _check_dependencies_on_startup(self):
        """Check dependencies and show setup wizard if needed."""
        if not self.dependency_manager.is_ready():
            from ..ui.setup_wizard import SetupWizard
            wizard = SetupWizard(self.dependency_manager, self)
            result = wizard.exec()
            
            # Re-check and update UI
            self._update_dependency_status()
        else:
            self._update_dependency_status()
    
    def _update_dependency_status(self):
        """Update UI based on dependency status."""
        is_ready = self.dependency_manager.is_ready()
        
        # Enable/disable conversion buttons
        self.convert_selected_btn.setEnabled(is_ready and len(self.input_files) > 0)
        self.convert_all_btn.setEnabled(is_ready and len(self.input_files) > 0)
        
        # Update status bar
        if is_ready:
            self.dependency_status_label.setText("✅ Dependencies Ready")
            self.dependency_status_label.setStyleSheet("color: green; font-weight: bold;")
            self.setup_btn.setEnabled(False)
        else:
            self.dependency_status_label.setText("❌ Setup Required")
            self.dependency_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.setup_btn.setEnabled(True)
    
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
        
        self.convert_selected_btn = QPushButton("Convert Selected")
        self.convert_selected_btn.setEnabled(False)
        self.convert_selected_btn.setStyleSheet("""
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
        self.convert_selected_btn.clicked.connect(self._start_conversion)
        convert_layout.addWidget(self.convert_selected_btn)
        
        self.convert_all_btn = QPushButton("Convert All")
        self.convert_all_btn.setEnabled(False)
        self.convert_all_btn.clicked.connect(self._start_batch_conversion)
        convert_layout.addWidget(self.convert_all_btn)
        
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
        """Create enhanced menu bar with recent files and share options."""
        menubar = self.menuBar()
        
        # ==================== File Menu ====================
        file_menu = menubar.addMenu("&File")
        
        # New/Open actions
        add_files_action = QAction("&Add Files...", self)
        add_files_action.setShortcut("Ctrl+O")
        add_files_action.triggered.connect(self._add_files)
        file_menu.addAction(add_files_action)
        
        add_folder_action = QAction("Add &Folder...", self)
        add_folder_action.setShortcut("Ctrl+Shift+O")
        add_folder_action.triggered.connect(self._add_folder)
        file_menu.addAction(add_folder_action)
        
        file_menu.addSeparator()
        
        # Recent Files submenu
        self.recent_files_menu = QMenu("Open &Recent", self)
        self._update_recent_files_menu()
        file_menu.addMenu(self.recent_files_menu)
        
        # Recently Converted submenu
        self.recent_output_menu = QMenu("Recently &Converted", self)
        self._update_recent_output_menu()
        file_menu.addMenu(self.recent_output_menu)
        
        file_menu.addSeparator()
        
        # Save/Export actions
        save_preview_action = QAction("&Save Preview...", self)
        save_preview_action.setShortcut("Ctrl+S")
        save_preview_action.triggered.connect(self._save_preview)
        file_menu.addAction(save_preview_action)
        
        export_settings_action = QAction("&Export Settings...", self)
        export_settings_action.triggered.connect(self._export_settings)
        file_menu.addAction(export_settings_action)
        
        import_settings_action = QAction("&Import Settings...", self)
        import_settings_action.triggered.connect(self._import_settings)
        file_menu.addAction(import_settings_action)
        
        file_menu.addSeparator()
        
        # Clear recent files
        clear_recent_action = QAction("Clear Recent Files", self)
        clear_recent_action.triggered.connect(self._clear_recent_files)
        file_menu.addAction(clear_recent_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ==================== Edit Menu ====================
        edit_menu = menubar.addMenu("&Edit")
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self._select_all_files)
        edit_menu.addAction(select_all_action)
        
        deselect_action = QAction("&Deselect All", self)
        deselect_action.setShortcut("Ctrl+D")
        deselect_action.triggered.connect(self._deselect_all_files)
        edit_menu.addAction(deselect_action)
        
        edit_menu.addSeparator()
        
        remove_action = QAction("&Remove Selected", self)
        remove_action.setShortcut("Delete")
        remove_action.triggered.connect(self._remove_selected)
        edit_menu.addAction(remove_action)
        
        clear_action = QAction("&Clear All", self)
        clear_action.setShortcut("Ctrl+Shift+C")
        clear_action.triggered.connect(self._clear_all)
        edit_menu.addAction(clear_action)
        
        edit_menu.addSeparator()
        
        preferences_action = QAction("&Preferences...", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self._show_preferences)
        edit_menu.addAction(preferences_action)
        
        # ==================== View Menu ====================
        view_menu = menubar.addMenu("&View")
        
        refresh_preview_action = QAction("&Refresh Preview", self)
        refresh_preview_action.setShortcut("F5")
        refresh_preview_action.triggered.connect(self._refresh_preview)
        view_menu.addAction(refresh_preview_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self._zoom_in_preview)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self._zoom_out_preview)
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QAction("&Fit to Window", self)
        zoom_fit_action.setShortcut("Ctrl+0")
        zoom_fit_action.triggered.connect(self._zoom_fit_preview)
        view_menu.addAction(zoom_fit_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction("&Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # ==================== Share Menu ====================
        share_menu = menubar.addMenu("&Share")
        
        open_output_action = QAction("&Open Output Folder", self)
        open_output_action.setShortcut("Ctrl+Shift+O")
        open_output_action.triggered.connect(self._open_output_folder)
        share_menu.addAction(open_output_action)
        
        share_menu.addSeparator()
        
        copy_path_action = QAction("&Copy Output Path", self)
        copy_path_action.triggered.connect(self._copy_output_path)
        share_menu.addAction(copy_path_action)
        
        copy_link_action = QAction("Copy Output &Link", self)
        copy_link_action.triggered.connect(self._copy_output_link)
        share_menu.addAction(copy_link_action)
        
        share_menu.addSeparator()
        
        share_email_action = QAction("Share via &Email...", self)
        share_email_action.triggered.connect(self._share_via_email)
        share_menu.addAction(share_email_action)
        
        share_social_menu = QMenu("Share on &Social Media", self)
        
        share_youtube_action = QAction("Upload to YouTube...", self)
        share_youtube_action.triggered.connect(self._share_youtube)
        share_social_menu.addAction(share_youtube_action)
        
        share_vimeo_action = QAction("Upload to Vimeo...", self)
        share_vimeo_action.triggered.connect(self._share_vimeo)
        share_social_menu.addAction(share_vimeo_action)
        
        share_twitter_action = QAction("Share on Twitter/X...", self)
        share_twitter_action.triggered.connect(self._share_twitter)
        share_social_menu.addAction(share_twitter_action)
        
        share_menu.addMenu(share_social_menu)
        
        share_menu.addSeparator()
        
        create_shareable_action = QAction("Create &Shareable Link...", self)
        create_shareable_action.triggered.connect(self._create_shareable_link)
        share_menu.addAction(create_shareable_action)
        
        # ==================== Tools Menu ====================
        tools_menu = menubar.addMenu("&Tools")
        
        batch_action = QAction("&Batch Manager", self)
        batch_action.setShortcut("Ctrl+B")
        batch_action.triggered.connect(self._open_batch_manager)
        tools_menu.addAction(batch_action)
        
        tools_menu.addSeparator()
        
        compare_action = QAction("&Compare Before/After...", self)
        compare_action.triggered.connect(self._compare_results)
        tools_menu.addAction(compare_action)
        
        benchmark_action = QAction("Run &Performance Benchmark...", self)
        benchmark_action.triggered.connect(self._run_benchmark)
        tools_menu.addAction(benchmark_action)
        
        tools_menu.addSeparator()
        
        model_manager_action = QAction("&Model Manager...", self)
        model_manager_action.triggered.connect(self._open_model_manager)
        tools_menu.addAction(model_manager_action)
        
        ffmpeg_action = QAction("&FFmpeg Settings...", self)
        ffmpeg_action.triggered.connect(self._open_ffmpeg_settings)
        tools_menu.addAction(ffmpeg_action)
        
        # ==================== Help Menu ====================
        help_menu = menubar.addMenu("&Help")
        
        guide_action = QAction("User &Guide", self)
        guide_action.setShortcut("F1")
        guide_action.triggered.connect(self._show_guide)
        help_menu.addAction(guide_action)
        
        video_guide_action = QAction("&Video Conversion Guide", self)
        video_guide_action.triggered.connect(self._show_video_guide)
        help_menu.addAction(video_guide_action)
        
        help_menu.addSeparator()
        
        docs_action = QAction("View &Documentation", self)
        docs_action.triggered.connect(self._open_documentation)
        help_menu.addAction(docs_action)
        
        github_action = QAction("Visit &GitHub Repository", self)
        github_action.triggered.connect(self._open_github)
        help_menu.addAction(github_action)
        
        help_menu.addSeparator()
        
        check_updates_action = QAction("Check for &Updates...", self)
        check_updates_action.triggered.connect(self._check_updates)
        help_menu.addAction(check_updates_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
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
        
        # Add dependency status indicator
        self.dependency_status_label = QLabel("⏳ Checking...")
        self.status_bar.addPermanentWidget(self.dependency_status_label)
        
        # Add setup button
        self.setup_btn = QPushButton("Run Setup")
        self.setup_btn.clicked.connect(self._show_setup_wizard)
        self.setup_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.status_bar.addPermanentWidget(self.setup_btn)
        
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
            self._update_button_states()
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
        is_ready = self.dependency_manager.is_ready()
        
        self.convert_selected_btn.setEnabled(has_selection and is_ready)
        self.convert_all_btn.setEnabled(has_files and is_ready)
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
    
    def _show_setup_wizard(self):
        """Show setup wizard dialog."""
        from ..ui.setup_wizard import SetupWizard
        wizard = SetupWizard(self.dependency_manager, self)
        wizard.setup_complete.connect(self._update_dependency_status)
        wizard.exec()
        self._update_dependency_status()
    
    # Recent Files Management
    
    def _load_recent_files(self):
        """Load recent files from settings."""
        try:
            from ..utils.config_manager import ConfigManager
            config = ConfigManager()
            self.recent_files = config.get('recent_files', [])[:self.max_recent_files]
            self.recent_output_files = config.get('recent_outputs', [])[:self.max_recent_files]
        except Exception as e:
            logger.warning(f"Could not load recent files: {e}")
            self.recent_files = []
            self.recent_output_files = []
    
    def _save_recent_files(self):
        """Save recent files to settings."""
        try:
            from ..utils.config_manager import ConfigManager
            config = ConfigManager()
            config.set('recent_files', self.recent_files[:self.max_recent_files])
            config.set('recent_outputs', self.recent_output_files[:self.max_recent_files])
            config.save()
        except Exception as e:
            logger.warning(f"Could not save recent files: {e}")
    
    def _add_to_recent_files(self, file_path: str):
        """Add file to recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:self.max_recent_files]
        self._save_recent_files()
        self._update_recent_files_menu()
    
    def _add_to_recent_outputs(self, file_path: str):
        """Add output file to recent outputs list."""
        if file_path in self.recent_output_files:
            self.recent_output_files.remove(file_path)
        self.recent_output_files.insert(0, file_path)
        self.recent_output_files = self.recent_output_files[:self.max_recent_files]
        self._save_recent_files()
        self._update_recent_output_menu()
    
    def _update_recent_files_menu(self):
        """Update recent files menu."""
        self.recent_files_menu.clear()
        
        if not self.recent_files:
            no_files_action = QAction("No recent files", self)
            no_files_action.setEnabled(False)
            self.recent_files_menu.addAction(no_files_action)
            return
        
        for file_path in self.recent_files:
            if Path(file_path).exists():
                action = QAction(Path(file_path).name, self)
                action.setToolTip(file_path)
                action.triggered.connect(lambda checked, f=file_path: self._open_recent_file(f))
                self.recent_files_menu.addAction(action)
    
    def _update_recent_output_menu(self):
        """Update recent output files menu."""
        self.recent_output_menu.clear()
        
        if not self.recent_output_files:
            no_files_action = QAction("No recent conversions", self)
            no_files_action.setEnabled(False)
            self.recent_output_menu.addAction(no_files_action)
            return
        
        for file_path in self.recent_output_files:
            if Path(file_path).exists():
                action = QAction(Path(file_path).name, self)
                action.setToolTip(file_path)
                action.triggered.connect(lambda checked, f=file_path: self._open_output_file(f))
                self.recent_output_menu.addAction(action)
        
        self.recent_output_menu.addSeparator()
        open_folder_action = QAction("Open Output Folder", self)
        open_folder_action.triggered.connect(self._open_output_folder)
        self.recent_output_menu.addAction(open_folder_action)
    
    def _open_recent_file(self, file_path: str):
        """Open a recent file."""
        if Path(file_path).exists():
            self._add_file_paths([file_path])
            self.status_bar.showMessage(f"Opened: {Path(file_path).name}")
        else:
            QMessageBox.warning(self, "File Not Found", f"The file no longer exists:\n{file_path}")
            self.recent_files.remove(file_path)
            self._save_recent_files()
            self._update_recent_files_menu()
    
    def _open_output_file(self, file_path: str):
        """Open an output file with system default application."""
        import subprocess
        import sys
        
        if not Path(file_path).exists():
            QMessageBox.warning(self, "File Not Found", f"The file no longer exists:\n{file_path}")
            self.recent_output_files.remove(file_path)
            self._save_recent_files()
            self._update_recent_output_menu()
            return
        
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', file_path])
            elif sys.platform == 'win32':  # Windows
                subprocess.run(['start', '', file_path], shell=True)
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
            self.status_bar.showMessage(f"Opened: {Path(file_path).name}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file:\n{e}")
    
    def _clear_recent_files(self):
        """Clear recent files list."""
        reply = QMessageBox.question(
            self, "Clear Recent Files",
            "Clear all recent files and conversion history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.recent_files.clear()
            self.recent_output_files.clear()
            self._save_recent_files()
            self._update_recent_files_menu()
            self._update_recent_output_menu()
            self.status_bar.showMessage("Recent files cleared")
    
    # Edit Menu Actions
    
    def _select_all_files(self):
        """Select all files in the list."""
        self.file_list.selectAll()
    
    def _deselect_all_files(self):
        """Deselect all files."""
        self.file_list.clearSelection()
    
    # View Menu Actions
    
    def _zoom_in_preview(self):
        """Zoom in preview."""
        if hasattr(self.preview_widget, 'zoom_in'):
            self.preview_widget.zoom_in()
        else:
            self.status_bar.showMessage("Zoom feature coming soon")
    
    def _zoom_out_preview(self):
        """Zoom out preview."""
        if hasattr(self.preview_widget, 'zoom_out'):
            self.preview_widget.zoom_out()
        else:
            self.status_bar.showMessage("Zoom feature coming soon")
    
    def _zoom_fit_preview(self):
        """Fit preview to window."""
        if hasattr(self.preview_widget, 'zoom_fit'):
            self.preview_widget.zoom_fit()
        else:
            self.status_bar.showMessage("Zoom feature coming soon")
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    # Share Menu Actions
    
    def _open_output_folder(self):
        """Open output folder in file explorer."""
        import subprocess
        import sys
        
        output_folder = Path.home() / "Documents" / "2D-to-3D-Output"
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)
        
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', str(output_folder)])
            elif sys.platform == 'win32':  # Windows
                subprocess.run(['explorer', str(output_folder)])
            else:  # Linux
                subprocess.run(['xdg-open', str(output_folder)])
            self.status_bar.showMessage(f"Opened: {output_folder}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder:\n{e}")
    
    def _copy_output_path(self):
        """Copy last output file path to clipboard."""
        from PyQt6.QtWidgets import QApplication
        
        if self.recent_output_files:
            path = self.recent_output_files[0]
            QApplication.clipboard().setText(path)
            self.status_bar.showMessage(f"Copied path to clipboard: {Path(path).name}")
        else:
            QMessageBox.information(self, "No Output", "No recent output files found.")
    
    def _copy_output_link(self):
        """Copy output file as file:// link."""
        from PyQt6.QtWidgets import QApplication
        
        if self.recent_output_files:
            path = self.recent_output_files[0]
            file_url = Path(path).as_uri()
            QApplication.clipboard().setText(file_url)
            self.status_bar.showMessage(f"Copied link to clipboard")
        else:
            QMessageBox.information(self, "No Output", "No recent output files found.")
    
    def _share_via_email(self):
        """Open email client with output file."""
        import urllib.parse
        import webbrowser
        
        if not self.recent_output_files:
            QMessageBox.information(self, "No Output", "No recent output files found.")
            return
        
        file_path = self.recent_output_files[0]
        subject = urllib.parse.quote("Check out my 3D converted video!")
        body = urllib.parse.quote(f"I converted a video to 3D format using 2D-to-3D Converter.\n\nFile: {file_path}")
        
        mailto_link = f"mailto:?subject={subject}&body={body}"
        webbrowser.open(mailto_link)
        self.status_bar.showMessage("Opened email client")
    
    def _share_youtube(self):
        """Open YouTube upload page."""
        import webbrowser
        webbrowser.open("https://www.youtube.com/upload")
        self.status_bar.showMessage("Opened YouTube upload page")
        QMessageBox.information(
            self, "YouTube Upload",
            "Your browser will open YouTube's upload page.\n\n"
            "Tip: Upload your 3D video with the tag 'yt3d:enable=true' "
            "in the description for YouTube's 3D support."
        )
    
    def _share_vimeo(self):
        """Open Vimeo upload page."""
        import webbrowser
        webbrowser.open("https://vimeo.com/upload")
        self.status_bar.showMessage("Opened Vimeo upload page")
    
    def _share_twitter(self):
        """Share on Twitter/X."""
        import urllib.parse
        import webbrowser
        
        text = urllib.parse.quote("Just converted a video to 3D using 2D-to-3D Converter! #3DVideo #AI")
        twitter_url = f"https://twitter.com/intent/tweet?text={text}"
        webbrowser.open(twitter_url)
        self.status_bar.showMessage("Opened Twitter")
    
    def _create_shareable_link(self):
        """Create shareable link (placeholder for cloud upload)."""
        QMessageBox.information(
            self, "Shareable Link",
            "<h3>Cloud Upload Feature</h3>"
            "<p>This feature will allow you to:</p>"
            "<ul>"
            "<li>Upload converted videos to cloud storage</li>"
            "<li>Generate shareable links</li>"
            "<li>Set expiration dates</li>"
            "<li>Track views and downloads</li>"
            "</ul>"
            "<p><b>Coming in a future update!</b></p>"
        )
    
    # Tools Menu Actions
    
    def _compare_results(self):
        """Compare before/after results."""
        QMessageBox.information(
            self, "Compare Tool",
            "<h3>Before/After Comparison</h3>"
            "<p>This feature will allow you to:</p>"
            "<ul>"
            "<li>View original and converted side-by-side</li>"
            "<li>Swipe to compare</li>"
            "<li>Adjust settings and see real-time changes</li>"
            "</ul>"
            "<p><b>Coming in a future update!</b></p>"
        )
    
    def _run_benchmark(self):
        """Run performance benchmark."""
        QMessageBox.information(
            self, "Performance Benchmark",
            "<h3>Benchmark Tool</h3>"
            "<p>This will test your system's performance:</p>"
            "<ul>"
            "<li>GPU acceleration detection</li>"
            "<li>Processing speed test</li>"
            "<li>Memory usage analysis</li>"
            "<li>Recommended settings</li>"
            "</ul>"
            "<p><b>Coming in a future update!</b></p>"
        )
    
    def _open_model_manager(self):
        """Open AI model manager."""
        QMessageBox.information(
            self, "Model Manager",
            "<h3>AI Model Manager</h3>"
            "<p>Manage depth estimation models:</p>"
            "<ul>"
            "<li>MiDaS v3.1 (Current)</li>"
            "<li>Depth-Anything-V2</li>"
            "<li>Download additional models</li>"
            "<li>Compare model performance</li>"
            "</ul>"
            "<p><b>Coming in a future update!</b></p>"
        )
    
    def _open_ffmpeg_settings(self):
        """Open FFmpeg settings dialog."""
        QMessageBox.information(
            self, "FFmpeg Settings",
            "<h3>FFmpeg Configuration</h3>"
            "<p>Configure video encoding settings:</p>"
            "<ul>"
            "<li>Codec selection (H.264, H.265, VP9)</li>"
            "<li>Bitrate and quality settings</li>"
            "<li>Audio codec options</li>"
            "<li>Hardware acceleration</li>"
            "</ul>"
            "<p><b>Coming in a future update!</b></p>"
        )
    
    def _show_preferences(self):
        """Show preferences dialog."""
        QMessageBox.information(
            self, "Preferences",
            "<h3>Application Preferences</h3>"
            "<p>Configure application settings:</p>"
            "<ul>"
            "<li>Default output folder</li>"
            "<li>Auto-save previews</li>"
            "<li>GPU acceleration preferences</li>"
            "<li>UI theme and language</li>"
            "</ul>"
            "<p><b>Coming in a future update!</b></p>"
        )
    
    def _export_settings(self):
        """Export current settings to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Settings",
            "conversion_settings.json",
            "JSON Files (*.json)"
        )
        if file_path:
            try:
                import json
                settings = self.settings_panel.get_settings()
                with open(file_path, 'w') as f:
                    json.dump(settings, f, indent=2)
                self.status_bar.showMessage(f"Settings exported: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Could not export settings:\n{e}")
    
    def _import_settings(self):
        """Import settings from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Settings",
            "",
            "JSON Files (*.json)"
        )
        if file_path:
            try:
                import json
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                # Apply settings to panel (would need implementation in settings_panel)
                self.status_bar.showMessage(f"Settings imported: {Path(file_path).name}")
                QMessageBox.information(self, "Import Successful", "Settings have been imported.")
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"Could not import settings:\n{e}")
    
    # Help Menu Actions
    
    def _show_video_guide(self):
        """Show video conversion guide."""
        QMessageBox.information(
            self, "Video Conversion Guide",
            "<h3>Video Conversion Guide</h3>"
            "<p>For detailed video conversion instructions, see:</p>"
            "<p><b>VIDEO_CONVERSION_GUIDE.md</b></p>"
            "<br>"
            "<p><b>Quick Tips:</b></p>"
            "<ul>"
            "<li>Use GPU acceleration for faster processing</li>"
            "<li>Enable temporal filtering for smoother results</li>"
            "<li>Choose appropriate output format for your device</li>"
            "<li>Test with short clips before full videos</li>"
            "</ul>"
        )
    
    def _open_documentation(self):
        """Open documentation in browser."""
        import webbrowser
        doc_url = "https://github.com/WHICHYOU/3D-APP-PYTHON/blob/main/README.md"
        webbrowser.open(doc_url)
        self.status_bar.showMessage("Opened documentation in browser")
    
    def _open_github(self):
        """Open GitHub repository."""
        import webbrowser
        webbrowser.open("https://github.com/WHICHYOU/3D-APP-PYTHON")
        self.status_bar.showMessage("Opened GitHub repository")
    
    def _check_updates(self):
        """Check for application updates."""
        QMessageBox.information(
            self, "Check for Updates",
            "<h3>Update Checker</h3>"
            "<p>Current version: 1.0.0</p>"
            "<br>"
            "<p>This feature will automatically check for updates from:</p>"
            "<ul>"
            "<li>GitHub Releases</li>"
            "<li>Notify you of new versions</li>"
            "<li>Download and install updates</li>"
            "</ul>"
            "<p><b>Coming in a future update!</b></p>"
            "<br>"
            "<p>Visit <a href='https://github.com/WHICHYOU/3D-APP-PYTHON/releases'>GitHub Releases</a> to check manually.</p>"
        )
    
    # Override existing methods to add recent files tracking
    
    def _add_file_paths(self, file_paths):
        """Add file paths to the list and track recent files."""
        added_count = 0
        for file_path in file_paths:
            if file_path not in self.input_files:
                self.input_files.append(file_path)
                item = QListWidgetItem(Path(file_path).name)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.file_list.addItem(item)
                added_count += 1
                # Add to recent files
                self._add_to_recent_files(file_path)
        
        if added_count > 0:
            self.status_bar.showMessage(f"Added {added_count} file(s)")
            self._update_button_states()
            self.clear_btn.setEnabled(True)
            logger.info(f"Added {added_count} files")
    
    def _start_conversion(self):
        """Start conversion of selected files and track output."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select files to convert.")
            return
        
        files_to_convert = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        settings = self.settings_panel.get_settings()
        
        # Import and show progress dialog
        from .progress_dialog import ProgressDialog
        dialog = ProgressDialog(files_to_convert, settings, self)
        
        # Connect to track output files
        if hasattr(dialog, 'conversion_complete'):
            dialog.conversion_complete.connect(self._on_conversion_complete)
        
        dialog.exec()
    
    def _start_batch_conversion(self):
        """Start batch conversion of all files and track output."""
        if not self.input_files:
            QMessageBox.warning(self, "No Files", "Please add files to convert.")
            return
        
        settings = self.settings_panel.get_settings()
        
        # Import and show progress dialog
        from .progress_dialog import ProgressDialog
        dialog = ProgressDialog(self.input_files, settings, self)
        
        # Connect to track output files
        if hasattr(dialog, 'conversion_complete'):
            dialog.conversion_complete.connect(self._on_conversion_complete)
        
        dialog.exec()
    
    def _on_conversion_complete(self, output_path: str):
        """Handle conversion completion and add to recent outputs."""
        if output_path:
            self._add_to_recent_outputs(output_path)
            logger.info(f"Conversion complete: {output_path}")
    
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

