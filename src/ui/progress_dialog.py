"""
Progress Dialog Module

Shows conversion progress with status updates and frame previews.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from pathlib import Path
import cv2
import numpy as np
import time
import logging

logger = logging.getLogger(__name__)


class ConversionWorker(QThread):
    """Worker thread for conversion process."""
    
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    file_completed = pyqtSignal(str, bool, str)  # filename, success, message
    conversion_finished = pyqtSignal(int, int)  # success_count, total_count
    preview_updated = pyqtSignal(np.ndarray)  # preview image
    
    def __init__(self, files, settings):
        """Initialize worker."""
        super().__init__()
        self.files = files
        self.settings = settings
        self.is_cancelled = False
    
    def run(self):
        """Run conversion process."""
        success_count = 0
        total_count = len(self.files)
        
        # Check if models need to be downloaded
        from pathlib import Path
        cache_dir = Path.home() / ".cache" / "torch" / "hub" / "checkpoints"
        model_file = cache_dir / "dpt_large_384.pt"
        
        if not model_file.exists():
            self.progress_updated.emit(
                0, total_count,
                "⏳ Downloading AI models (~1.3 GB)...\n"
                "This may take 5-30 minutes on first run.\n"
                "Models will be cached for future use.\n"
                "Please wait..."
            )
        
        # Initialize models once
        try:
            from ..ai_core.depth_estimation import DepthEstimator
            from ..rendering.dibr_renderer import DIBRRenderer
            from ..rendering.sbs_composer import SBSComposer
            
            self.progress_updated.emit(0, total_count, "Initializing AI models...")
            estimator = DepthEstimator()
            renderer = DIBRRenderer(ipd=self.settings.get('ipd', 65))
            composer = SBSComposer()
            
            # Confirm models loaded successfully
            self.progress_updated.emit(0, total_count, "✓ AI models ready. Starting conversion...")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            self.conversion_finished.emit(0, total_count)
            return
        
        # Process each file
        for i, file_path in enumerate(self.files, 1):
            if self.is_cancelled:
                break
            
            filename = Path(file_path).name
            self.progress_updated.emit(i, total_count, f"Processing: {filename}")
            
            try:
                # Check if video or image
                is_video = Path(file_path).suffix.lower() in {'.mp4', '.avi', '.mov', '.mkv'}
                
                if is_video:
                    success = self._convert_video(file_path, estimator, renderer, composer)
                else:
                    success = self._convert_image(file_path, estimator, renderer, composer)
                
                if success:
                    success_count += 1
                    self.file_completed.emit(filename, True, "Completed successfully")
                else:
                    self.file_completed.emit(filename, False, "Conversion failed")
                    
            except Exception as e:
                import traceback
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                logger.error(f"Error converting {filename}: {error_msg}")
                self.file_completed.emit(filename, False, str(e))
        
        self.conversion_finished.emit(success_count, total_count)
    
    def _convert_image(self, file_path, estimator, renderer, composer):
        """Convert single image."""
        try:
            filename = Path(file_path).name
            
            # Load image
            self.progress_updated.emit(0, 1, f"📂 Loading {filename}...")
            image_bgr = cv2.imread(file_path)
            if image_bgr is None:
                return False
            
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            h, w = image_rgb.shape[:2]
            self.progress_updated.emit(0, 1, f"✓ Loaded {w}x{h} image")
            
            # Estimate depth
            self.progress_updated.emit(0, 1, f"🧠 Analyzing depth (AI processing)...")
            depth_map = estimator.estimate_depth(image_rgb, normalize=True)
            self.progress_updated.emit(0, 1, f"✓ Depth map generated")
            
            # Render stereo
            self.progress_updated.emit(0, 1, f"👁️ Rendering stereo views...")
            left_view, right_view = renderer.render_stereo_pair(
                image_rgb,
                depth_map,
                depth_intensity=self.settings.get('depth_intensity', 75)
            )
            self.progress_updated.emit(0, 1, f"✓ Stereo pair created")
            
            # Compose output
            self.progress_updated.emit(0, 1, f"🎨 Composing 3D output...")
            output_format = self.settings.get('output_format', 'half_sbs')
            if output_format == 'half_sbs':
                output = composer.compose_half_sbs(left_view, right_view)
            elif output_format == 'full_sbs':
                output = composer.compose_full_sbs(left_view, right_view)
            elif output_format == 'anaglyph':
                output = composer.compose_anaglyph(left_view, right_view)
            elif output_format == 'top_bottom':
                output = composer.compose_top_bottom(left_view, right_view, half=True)
            
            # Emit preview
            self.preview_updated.emit(output)
            
            # Save output
            self.progress_updated.emit(0, 1, f"💾 Saving output file...")
            output_path = self._get_output_path(file_path)
            output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_path), output_bgr)
            
            size_kb = output_path.stat().st_size / 1024
            self.progress_updated.emit(1, 1, f"✅ Complete! Saved to {output_path.parent.name}/{output_path.name} ({size_kb:.1f} KB)")
            
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Image conversion error: {error_msg}")
            return False
    
    def _convert_video(self, file_path, estimator, renderer, composer):
        """Convert video file."""
        try:
            from ..video_processing.ffmpeg_handler import FFmpegHandler
            from ..video_processing.audio_handler import AudioHandler
            from ..video_processing.encoder import VideoEncoder
            from ..ai_core.temporal_filter import TemporalFilter
            import tempfile
            
            # Setup paths in system temp directory
            temp_base = Path(tempfile.gettempdir())
            work_dir = temp_base / "temp_conversion"
            frames_dir = work_dir / "frames"
            output_frames_dir = work_dir / "output_frames"
            audio_path = work_dir / "audio.aac"
            
            work_dir.mkdir(exist_ok=True)
            frames_dir.mkdir(exist_ok=True)
            output_frames_dir.mkdir(exist_ok=True)
            
            # Extract frames
            ffmpeg = FFmpegHandler()
            video_info = ffmpeg.get_video_info(Path(file_path))
            
            self.progress_updated.emit(0, 100, "Extracting frames...")
            frame_count = ffmpeg.extract_frames(
                Path(file_path),
                frames_dir,
                frame_pattern="frame_%06d.png"
            )
            
            # Extract audio
            has_audio = False
            if video_info['has_audio']:
                audio_handler = AudioHandler(ffmpeg_handler=ffmpeg)
                has_audio = audio_handler.extract_audio(Path(file_path), audio_path)
            
            # Process frames
            temporal_filter = TemporalFilter(window_size=3, alpha=0.7)
            frame_files = sorted(frames_dir.glob("frame_*.png"))
            
            for i, frame_path in enumerate(frame_files, 1):
                if self.is_cancelled:
                    break
                
                progress = int((i / frame_count) * 100)
                self.progress_updated.emit(progress, 100, f"Processing frame {i}/{frame_count}")
                
                # Load frame
                frame_bgr = cv2.imread(str(frame_path))
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                
                # Estimate depth with temporal filtering
                depth_map = estimator.estimate_depth(frame_rgb, normalize=True)
                depth_map = temporal_filter.filter(depth_map)
                
                # Render and compose
                left_view, right_view = renderer.render_stereo_pair(
                    frame_rgb, depth_map,
                    depth_intensity=self.settings.get('depth_intensity', 75)
                )
                
                output_format = self.settings.get('output_format', 'half_sbs')
                if output_format == 'half_sbs':
                    output = composer.compose_half_sbs(left_view, right_view)
                elif output_format == 'full_sbs':
                    output = composer.compose_full_sbs(left_view, right_view)
                elif output_format == 'anaglyph':
                    output = composer.compose_anaglyph(left_view, right_view)
                elif output_format == 'top_bottom':
                    output = composer.compose_top_bottom(left_view, right_view, half=True)
                
                # Save frame
                output_path = output_frames_dir / frame_path.name
                output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
                cv2.imwrite(str(output_path), output_bgr)
                
                # Emit preview occasionally
                if i % 10 == 0:
                    self.preview_updated.emit(output)
            
            # Encode video
            self.progress_updated.emit(100, 100, "Encoding video...")
            encoder = VideoEncoder(ffmpeg_handler=ffmpeg)
            output_path = self._get_output_path(file_path)
            
            # Only include audio if file actually exists and has content
            audio_file = None
            if has_audio and audio_path.exists() and audio_path.stat().st_size > 0:
                audio_file = audio_path
                logger.info(f"Including audio file: {audio_file} ({audio_path.stat().st_size} bytes)")
            else:
                logger.info("No audio file to include in output")
            
            encoder.encode_from_frames(
                output_frames_dir,
                Path(output_path),
                fps=video_info['fps'],
                frame_pattern="frame_%06d.png",
                audio_path=audio_file
            )
            
            # Cleanup
            import shutil
            shutil.rmtree(work_dir)
            
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Video conversion error: {error_msg}")
            return False
    
    def _get_output_path(self, input_path):
        """Get output path for file."""
        input_path = Path(input_path)
        suffix = input_path.suffix
        output_name = f"{input_path.stem}_3d{suffix}"
        output_dir = input_path.parent / "converted"
        output_dir.mkdir(exist_ok=True)
        return output_dir / output_name
    
    def cancel(self):
        """Cancel conversion."""
        self.is_cancelled = True


class ProgressDialog(QDialog):
    """Dialog showing conversion progress."""
    
    def __init__(self, files, settings, parent=None):
        """Initialize progress dialog."""
        super().__init__(parent)
        self.files = files
        self.settings = settings
        self.start_time = time.time()
        self._setup_ui()
        self._start_conversion()
    
    def _setup_ui(self):
        """Setup user interface."""
        self.setWindowTitle("Converting Files")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # Overall progress
        progress_group = QGroupBox("Overall Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.overall_label = QLabel("Initializing...")
        progress_layout.addWidget(self.overall_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, len(self.files))
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.time_label = QLabel("Elapsed: 0s | Remaining: --")
        progress_layout.addWidget(self.time_label)
        
        layout.addWidget(progress_group)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("No preview yet")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("border: 1px solid #ddd; background-color: #f0f0f0;")
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        # Log
        log_group = QGroupBox("Status Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel_conversion)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        
        self.open_folder_btn = QPushButton("📁 Open Output Folder")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        button_layout.addWidget(self.open_folder_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def _start_conversion(self):
        """Start conversion worker thread."""
        self.worker = ConversionWorker(self.files, self.settings)
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.file_completed.connect(self._on_file_completed)
        self.worker.conversion_finished.connect(self._on_conversion_finished)
        self.worker.preview_updated.connect(self._on_preview_updated)
        self.worker.start()
    
    def _on_progress_updated(self, current, total, message):
        """Handle progress update."""
        self.progress_bar.setValue(current)
        self.overall_label.setText(f"{message} ({current}/{total})")
        
        # Add to log
        self.log_text.append(message)
        
        # Update time estimate
        elapsed = time.time() - self.start_time
        if current > 0:
            avg_time = elapsed / current
            remaining = avg_time * (total - current)
            self.time_label.setText(
                f"Elapsed: {elapsed:.0f}s | Remaining: ~{remaining:.0f}s"
            )
    
    def _on_file_completed(self, filename, success, message):
        """Handle file completion."""
        status = "✓" if success else "✗"
        self.log_text.append(f"{status} {filename}: {message}")
    
    def _on_conversion_finished(self, success_count, total_count):
        """Handle conversion completion."""
        elapsed = time.time() - self.start_time
        self.overall_label.setText(
            f"Complete: {success_count}/{total_count} successful ({elapsed:.1f}s)"
        )
        self.cancel_btn.setEnabled(False)
        self.close_btn.setEnabled(True)
        
        # Enable open folder button if any conversions succeeded
        if success_count > 0:
            self.open_folder_btn.setEnabled(True)
        
        self.log_text.append(f"\n{'='*50}")
        self.log_text.append(f"Conversion finished!")
        self.log_text.append(f"Success: {success_count}/{total_count}")
        self.log_text.append(f"Total time: {elapsed:.1f}s")
        
        if success_count > 0:
            # Get output folder path
            first_file = Path(self.files[0])
            output_folder = first_file.parent / "converted"
            self.log_text.append(f"\n📁 Output saved to: {output_folder}")
    
    def _on_preview_updated(self, image_rgb):
        """Handle preview update."""
        # Convert to pixmap
        height, width = image_rgb.shape[:2]
        bytes_per_line = 3 * width
        qimage = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        
        # Scale to fit
        pixmap = pixmap.scaled(
            500, 200,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.preview_label.setPixmap(pixmap)
    
    def _cancel_conversion(self):
        """Cancel conversion."""
        self.worker.cancel()
        self.worker.wait()
        self.log_text.append("\n⚠️ Conversion cancelled by user")
        self.cancel_btn.setEnabled(False)
        self.close_btn.setEnabled(True)
    
    def _open_output_folder(self):
        """Open the output folder in Finder/Explorer."""
        import subprocess
        import sys
        
        # Get output folder from first file
        first_file = Path(self.files[0])
        output_folder = first_file.parent / "converted"
        
        if output_folder.exists():
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', str(output_folder)])
            elif sys.platform == 'win32':  # Windows
                subprocess.run(['explorer', str(output_folder)])
            else:  # Linux
                subprocess.run(['xdg-open', str(output_folder)])
    
    def closeEvent(self, event):
        """Handle dialog close."""
        if self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        event.accept()
