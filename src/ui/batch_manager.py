"""
Batch Manager Module

Manages batch conversion queue with priority and scheduling.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFileDialog, QGroupBox, QLabel, QComboBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BatchManagerDialog(QDialog):
    """Dialog for managing batch conversion queue."""
    
    def __init__(self, parent=None):
        """Initialize batch manager."""
        super().__init__(parent)
        self.queue = []
        self._setup_ui()
        self.setWindowTitle("Batch Manager")
        self.resize(800, 600)
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        
        # Queue table
        queue_group = QGroupBox("Conversion Queue")
        queue_layout = QVBoxLayout(queue_group)
        
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(5)
        self.queue_table.setHorizontalHeaderLabels([
            "File", "Type", "Format", "Priority", "Status"
        ])
        self.queue_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.queue_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        queue_layout.addWidget(self.queue_table)
        
        layout.addWidget(queue_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.add_files_btn = QPushButton("Add Files")
        self.add_files_btn.clicked.connect(self._add_files)
        controls_layout.addWidget(self.add_files_btn)
        
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self._add_folder)
        controls_layout.addWidget(self.add_folder_btn)
        
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self._remove_selected)
        controls_layout.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self._clear_all)
        controls_layout.addWidget(self.clear_btn)
        
        controls_layout.addStretch()
        
        self.move_up_btn = QPushButton("↑ Move Up")
        self.move_up_btn.clicked.connect(self._move_up)
        controls_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("↓ Move Down")
        self.move_down_btn.clicked.connect(self._move_down)
        controls_layout.addWidget(self.move_down_btn)
        
        layout.addLayout(controls_layout)
        
        # Batch settings
        settings_group = QGroupBox("Batch Settings")
        settings_layout = QHBoxLayout(settings_group)
        
        settings_layout.addWidget(QLabel("Default Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Half Side-by-Side",
            "Full Side-by-Side",
            "Anaglyph",
            "Top-Bottom"
        ])
        settings_layout.addWidget(self.format_combo)
        
        settings_layout.addWidget(QLabel("Default Priority:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Normal", "High"])
        self.priority_combo.setCurrentText("Normal")
        settings_layout.addWidget(self.priority_combo)
        
        settings_layout.addStretch()
        
        layout.addWidget(settings_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Batch")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.start_btn.clicked.connect(self._start_batch)
        button_layout.addWidget(self.start_btn)
        
        button_layout.addStretch()
        
        self.save_queue_btn = QPushButton("Save Queue")
        self.save_queue_btn.clicked.connect(self._save_queue)
        button_layout.addWidget(self.save_queue_btn)
        
        self.load_queue_btn = QPushButton("Load Queue")
        self.load_queue_btn.clicked.connect(self._load_queue)
        button_layout.addWidget(self.load_queue_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def _add_files(self):
        """Add files to queue."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter(
            "Media Files (*.jpg *.jpeg *.png *.bmp *.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            for file_path in files:
                self._add_to_queue(file_path)
    
    def _add_folder(self):
        """Add folder contents to queue."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            folder_path = Path(folder)
            media_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.mp4', '.avi', '.mov', '.mkv'}
            files = [str(f) for f in folder_path.iterdir() 
                    if f.suffix.lower() in media_extensions]
            for file_path in files:
                self._add_to_queue(file_path)
    
    def _add_to_queue(self, file_path):
        """Add single file to queue."""
        path = Path(file_path)
        file_type = "Video" if path.suffix.lower() in {'.mp4', '.avi', '.mov', '.mkv'} else "Image"
        
        format_map = {
            "Half Side-by-Side": "half_sbs",
            "Full Side-by-Side": "full_sbs",
            "Anaglyph": "anaglyph",
            "Top-Bottom": "top_bottom"
        }
        format_code = format_map[self.format_combo.currentText()]
        priority = self.priority_combo.currentText()
        
        self.queue.append({
            'path': file_path,
            'type': file_type,
            'format': format_code,
            'priority': priority,
            'status': 'Pending'
        })
        
        self._update_table()
    
    def _update_table(self):
        """Update queue table."""
        self.queue_table.setRowCount(len(self.queue))
        
        for i, item in enumerate(self.queue):
            self.queue_table.setItem(i, 0, QTableWidgetItem(Path(item['path']).name))
            self.queue_table.setItem(i, 1, QTableWidgetItem(item['type']))
            self.queue_table.setItem(i, 2, QTableWidgetItem(item['format']))
            self.queue_table.setItem(i, 3, QTableWidgetItem(item['priority']))
            self.queue_table.setItem(i, 4, QTableWidgetItem(item['status']))
    
    def _remove_selected(self):
        """Remove selected items from queue."""
        selected_rows = set(item.row() for item in self.queue_table.selectedItems())
        for row in sorted(selected_rows, reverse=True):
            del self.queue[row]
        self._update_table()
    
    def _clear_all(self):
        """Clear entire queue."""
        reply = QMessageBox.question(
            self,
            "Clear Queue",
            "Are you sure you want to clear all items from the queue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.queue.clear()
            self._update_table()
    
    def _move_up(self):
        """Move selected item up in queue."""
        current_row = self.queue_table.currentRow()
        if current_row > 0:
            self.queue[current_row], self.queue[current_row - 1] = \
                self.queue[current_row - 1], self.queue[current_row]
            self._update_table()
            self.queue_table.selectRow(current_row - 1)
    
    def _move_down(self):
        """Move selected item down in queue."""
        current_row = self.queue_table.currentRow()
        if current_row < len(self.queue) - 1:
            self.queue[current_row], self.queue[current_row + 1] = \
                self.queue[current_row + 1], self.queue[current_row]
            self._update_table()
            self.queue_table.selectRow(current_row + 1)
    
    def _start_batch(self):
        """Start batch conversion."""
        if not self.queue:
            QMessageBox.warning(self, "Empty Queue", "Please add files to the queue first.")
            return
        
        # Get settings
        settings = {
            'depth_intensity': 75,
            'ipd': 65,
            'output_format': 'half_sbs',
            'quality': 'high',
            'hole_filling': True
        }
        
        # Extract file paths
        files = [item['path'] for item in self.queue]
        
        # Open progress dialog
        from .progress_dialog import ProgressDialog
        dialog = ProgressDialog(files, settings, self)
        result = dialog.exec()
        
        if result:
            # Update status
            for item in self.queue:
                item['status'] = 'Completed'
            self._update_table()
    
    def _save_queue(self):
        """Save queue to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Queue",
            "batch_queue.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            import json
            with open(file_path, 'w') as f:
                json.dump(self.queue, f, indent=2)
            QMessageBox.information(self, "Success", "Queue saved successfully!")
    
    def _load_queue(self):
        """Load queue from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Queue",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            import json
            with open(file_path, 'r') as f:
                self.queue = json.load(f)
            self._update_table()
            QMessageBox.information(self, "Success", "Queue loaded successfully!")
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QFileDialog
)
from PyQt6.QtCore import pyqtSignal
from typing import List


class BatchManager(QWidget):
    """Widget for managing batch conversions"""
    
    # Signals
    batch_started = pyqtSignal(list)
    
    def __init__(self, parent=None):
        """
        Initialize batch manager
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.file_list = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel('Batch Processing')
        header_label.setStyleSheet('font-size: 14pt; font-weight: bold;')
        layout.addWidget(header_label)
        
        # File list
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_files_btn = QPushButton('Add Files')
        add_files_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(add_files_btn)
        
        add_folder_btn = QPushButton('Add Folder')
        add_folder_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(add_folder_btn)
        
        clear_btn = QPushButton('Clear')
        clear_btn.clicked.connect(self.clear_list)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        # Start button
        self.start_btn = QPushButton('Start Batch Conversion')
        self.start_btn.clicked.connect(self.start_batch)
        self.start_btn.setEnabled(False)
        layout.addWidget(self.start_btn)
        
        # Status
        self.status_label = QLabel('No files added')
        layout.addWidget(self.status_label)
    
    def add_files(self):
        """Add files to batch"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            'Select Files',
            '',
            'Media Files (*.mp4 *.avi *.mov *.jpg *.png);;All Files (*)'
        )
        
        if files:
            for file in files:
                if file not in self.file_list:
                    self.file_list.append(file)
                    self.list_widget.addItem(file)
            
            self.update_status()
    
    def add_folder(self):
        """Add all files from folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            'Select Folder'
        )
        
        if folder:
            # TODO: Scan folder for video/image files
            print(f"Would add files from: {folder}")
            self.update_status()
    
    def clear_list(self):
        """Clear file list"""
        self.file_list.clear()
        self.list_widget.clear()
        self.update_status()
    
    def start_batch(self):
        """Start batch conversion"""
        if self.file_list:
            self.batch_started.emit(self.file_list.copy())
    
    def update_status(self):
        """Update status label"""
        count = len(self.file_list)
        self.status_label.setText(f'{count} file(s) ready')
        self.start_btn.setEnabled(count > 0)
    
    def get_file_list(self) -> List[str]:
        """
        Get current file list
        
        Returns:
            List of file paths
        """
        return self.file_list.copy()
