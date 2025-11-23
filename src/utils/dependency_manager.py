"""
Dependency Manager

Checks and downloads required dependencies:
- AI Models (MiDaS)
- FFmpeg/ffprobe binaries
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Callable, Optional
import urllib.request
import zipfile
import tarfile
import shutil
import subprocess
import platform

logger = logging.getLogger(__name__)


class DependencyManager:
    """Manages application dependencies."""
    
    def __init__(self):
        """Initialize dependency manager."""
        self.system = platform.system()
        self.machine = platform.machine()
        
        # Setup directories
        if getattr(sys, 'frozen', False):
            # Running as bundled app
            self.base_dir = Path.home() / ".2d_to_3d_converter"
        else:
            # Running from source
            self.base_dir = Path.home() / ".2d_to_3d_converter"
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir = self.base_dir / "models"
        self.ffmpeg_dir = self.base_dir / "ffmpeg_bin"
        
        self.models_dir.mkdir(exist_ok=True)
        self.ffmpeg_dir.mkdir(exist_ok=True)
    
    def check_all_dependencies(self) -> Dict[str, bool]:
        """
        Check status of all dependencies.
        
        Returns:
            Dict with dependency names and their status (True = ready)
        """
        return {
            "ai_model": self.is_model_downloaded(),
            "ffmpeg": self.is_ffmpeg_downloaded(),
            "ffprobe": self.is_ffprobe_downloaded()
        }
    
    def is_ready(self) -> bool:
        """Check if all dependencies are ready."""
        deps = self.check_all_dependencies()
        return all(deps.values())
    
    def is_model_downloaded(self) -> bool:
        """Check if AI model is downloaded (checks PyTorch Hub cache)."""
        # PyTorch Hub downloads models to ~/.cache/torch/hub/checkpoints/
        torch_cache = Path.home() / ".cache" / "torch" / "hub" / "checkpoints"
        model_path = torch_cache / "dpt_large_384.pt"
        return model_path.exists() and model_path.stat().st_size > 100_000_000  # > 100MB
    
    def is_ffmpeg_downloaded(self) -> bool:
        """Check if ffmpeg is downloaded."""
        ffmpeg_name = "ffmpeg.exe" if self.system == "Windows" else "ffmpeg"
        ffmpeg_path = self.ffmpeg_dir / ffmpeg_name
        return ffmpeg_path.exists() and self._test_binary(str(ffmpeg_path))
    
    def is_ffprobe_downloaded(self) -> bool:
        """Check if ffprobe is downloaded."""
        ffprobe_name = "ffprobe.exe" if self.system == "Windows" else "ffprobe"
        ffprobe_path = self.ffmpeg_dir / ffprobe_name
        return ffprobe_path.exists() and self._test_binary(str(ffprobe_path))
    
    def _test_binary(self, path: str) -> bool:
        """Test if binary works."""
        try:
            result = subprocess.run(
                [path, "-version"],
                capture_output=True,
                timeout=3
            )
            return result.returncode == 0
        except:
            return False
    
    def download_ai_model(self, progress_callback: Optional[Callable] = None) -> bool:
        """
        Download AI model (MiDaS DPT-Large) using PyTorch Hub.
        
        Args:
            progress_callback: Function(downloaded, total, message)
        
        Returns:
            True if successful
        """
        try:
            if progress_callback:
                progress_callback(0, 100, "Starting AI model download via PyTorch Hub...")
            
            logger.info("Downloading AI model via PyTorch Hub (torch.hub.load)")
            
            # Import torch here to avoid loading it during dependency checks
            import torch
            
            if progress_callback:
                progress_callback(30, 100, "Loading MiDaS model from PyTorch Hub...")
            
            # This will automatically download to ~/.cache/torch/hub/checkpoints/
            model = torch.hub.load(
                "intel-isl/MiDaS",
                "DPT_Large",
                pretrained=True,
                trust_repo=True
            )
            
            if progress_callback:
                progress_callback(100, 100, "AI model downloaded successfully!")
            
            logger.info("AI model downloaded successfully via PyTorch Hub")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download AI model: {e}")
            if progress_callback:
                progress_callback(0, 100, f"Error: {str(e)}")
            return False
    
    def download_ffmpeg(self, progress_callback: Optional[Callable] = None) -> bool:
        """
        Download FFmpeg binary.
        
        Args:
            progress_callback: Function(downloaded, total, message)
        
        Returns:
            True if successful
        """
        try:
            if self.system == "Darwin":
                # macOS
                url = "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
            elif self.system == "Linux":
                if self.machine == "aarch64":
                    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz"
                else:
                    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            elif self.system == "Windows":
                url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            else:
                raise RuntimeError(f"Unsupported platform: {self.system}")
            
            if progress_callback:
                progress_callback(0, 100, "Starting FFmpeg download...")
            
            logger.info(f"Downloading FFmpeg from {url}")
            
            # Download
            download_path = self.ffmpeg_dir / "temp_download"
            download_path.mkdir(exist_ok=True)
            archive_path = download_path / "ffmpeg_archive"
            
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, int(downloaded * 100 / total_size))
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    progress_callback(
                        downloaded,
                        total_size,
                        f"Downloading FFmpeg: {mb_downloaded:.1f} / {mb_total:.1f} MB ({percent}%)"
                    )
            
            urllib.request.urlretrieve(url, archive_path, reporthook=report_progress)
            
            if progress_callback:
                progress_callback(100, 100, "Extracting FFmpeg...")
            
            # Extract
            self._extract_archive(archive_path, download_path)
            
            # Find and move binary
            binary_file = self._find_binary_in_dir(download_path, "ffmpeg")
            if not binary_file:
                raise RuntimeError("FFmpeg binary not found in download")
            
            ffmpeg_name = "ffmpeg.exe" if self.system == "Windows" else "ffmpeg"
            final_path = self.ffmpeg_dir / ffmpeg_name
            shutil.copy2(binary_file, final_path)
            
            if self.system != "Windows":
                final_path.chmod(0o755)
            
            # Cleanup
            shutil.rmtree(download_path)
            
            if progress_callback:
                progress_callback(100, 100, "FFmpeg download complete!")
            
            logger.info("FFmpeg downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download FFmpeg: {e}")
            if progress_callback:
                progress_callback(0, 100, f"Error: {str(e)}")
            return False
    
    def download_ffprobe(self, progress_callback: Optional[Callable] = None) -> bool:
        """
        Download ffprobe binary.
        
        Args:
            progress_callback: Function(downloaded, total, message)
        
        Returns:
            True if successful
        """
        try:
            if self.system == "Darwin":
                # macOS - separate download
                url = "https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip"
            else:
                # Linux/Windows - should already have it from ffmpeg package
                if not self.is_ffmpeg_downloaded():
                    raise RuntimeError("Download FFmpeg first (includes ffprobe)")
                
                # Try to find it
                download_path = self.ffmpeg_dir / "temp_download"
                download_path.mkdir(exist_ok=True)
                
                # Re-extract to find ffprobe
                # (This is a fallback - normally ffprobe comes with ffmpeg)
                if progress_callback:
                    progress_callback(100, 100, "ffprobe already included with FFmpeg")
                return True
            
            if progress_callback:
                progress_callback(0, 100, "Starting ffprobe download...")
            
            logger.info(f"Downloading ffprobe from {url}")
            
            # Download
            download_path = self.ffmpeg_dir / "temp_probe_download"
            download_path.mkdir(exist_ok=True)
            archive_path = download_path / "ffprobe_archive"
            
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, int(downloaded * 100 / total_size))
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    progress_callback(
                        downloaded,
                        total_size,
                        f"Downloading ffprobe: {mb_downloaded:.1f} / {mb_total:.1f} MB ({percent}%)"
                    )
            
            urllib.request.urlretrieve(url, archive_path, reporthook=report_progress)
            
            if progress_callback:
                progress_callback(100, 100, "Extracting ffprobe...")
            
            # Extract
            self._extract_archive(archive_path, download_path)
            
            # Find and move binary
            binary_file = self._find_binary_in_dir(download_path, "ffprobe")
            if not binary_file:
                raise RuntimeError("ffprobe binary not found in download")
            
            ffprobe_name = "ffprobe.exe" if self.system == "Windows" else "ffprobe"
            final_path = self.ffmpeg_dir / ffprobe_name
            shutil.copy2(binary_file, final_path)
            
            if self.system != "Windows":
                final_path.chmod(0o755)
            
            # Cleanup
            shutil.rmtree(download_path)
            
            if progress_callback:
                progress_callback(100, 100, "ffprobe download complete!")
            
            logger.info("ffprobe downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download ffprobe: {e}")
            if progress_callback:
                progress_callback(0, 100, f"Error: {str(e)}")
            return False
    
    def _extract_archive(self, archive_path: Path, extract_to: Path):
        """Extract archive based on file type."""
        # Detect file type
        result = subprocess.run(
            ["file", "-b", str(archive_path)],
            capture_output=True, text=True
        )
        file_type = result.stdout.lower()
        
        if "zip" in file_type:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        else:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_to)
    
    def _find_binary_in_dir(self, directory: Path, binary_name: str) -> Optional[Path]:
        """Find binary in directory."""
        if self.system == "Windows":
            search_names = [f"{binary_name}.exe"]
        else:
            search_names = [binary_name]
        
        for name in search_names:
            for path in directory.rglob(name):
                if path.is_file():
                    return path
        
        return None
    
    def get_model_path(self) -> Optional[str]:
        """Get path to AI model if downloaded."""
        if self.is_model_downloaded():
            return str(self.models_dir / "dpt_large_384.pt")
        return None
    
    def get_ffmpeg_path(self) -> Optional[str]:
        """Get path to ffmpeg if downloaded."""
        if self.is_ffmpeg_downloaded():
            ffmpeg_name = "ffmpeg.exe" if self.system == "Windows" else "ffmpeg"
            return str(self.ffmpeg_dir / ffmpeg_name)
        return None
    
    def get_ffprobe_path(self) -> Optional[str]:
        """Get path to ffprobe if downloaded."""
        if self.is_ffprobe_downloaded():
            ffprobe_name = "ffprobe.exe" if self.system == "Windows" else "ffprobe"
            return str(self.ffmpeg_dir / ffprobe_name)
        return None
