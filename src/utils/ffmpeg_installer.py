"""
Automatic FFmpeg Installer

Downloads and installs FFmpeg automatically for the application.
No user intervention required.
"""

import sys
import platform
import urllib.request
import tarfile
import zipfile
import shutil
from pathlib import Path
import logging
import subprocess

logger = logging.getLogger(__name__)


class FFmpegInstaller:
    """Handles automatic FFmpeg installation."""
    
    # Static FFmpeg builds - no dependencies needed
    FFMPEG_URLS = {
        "Darwin": {
            "arm64": {
                "ffmpeg": "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip",
                "ffprobe": "https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip"
            },
            "x86_64": {
                "ffmpeg": "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip",
                "ffprobe": "https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip"
            }
        },
        "Linux": {
            "x86_64": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
            "aarch64": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz"
        },
        "Windows": {
            "AMD64": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        }
    }
    
    def __init__(self):
        """Initialize installer."""
        self.system = platform.system()
        self.machine = platform.machine()
        
        # Installation directory inside app resources
        if getattr(sys, 'frozen', False):
            # Running as bundled app
            base_path = Path(sys._MEIPASS)
        else:
            # Running from source
            base_path = Path.home() / ".2d_to_3d_converter"
        
        self.install_dir = base_path / "ffmpeg_bin"
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
    def get_ffmpeg_path(self) -> str:
        """
        Get FFmpeg executable path, installing if necessary.
        
        Returns:
            Path to FFmpeg executable
        """
        # Check if already installed in our directory
        ffmpeg_name = "ffmpeg.exe" if self.system == "Windows" else "ffmpeg"
        ffprobe_name = "ffprobe.exe" if self.system == "Windows" else "ffprobe"
        local_ffmpeg = self.install_dir / ffmpeg_name
        local_ffprobe = self.install_dir / ffprobe_name
        
        if local_ffmpeg.exists() and local_ffprobe.exists() and self._test_ffmpeg(str(local_ffmpeg)):
            logger.info(f"Using bundled FFmpeg: {local_ffmpeg}")
            return str(local_ffmpeg)
        
        # Try system FFmpeg
        system_ffmpeg = self._find_system_ffmpeg()
        if system_ffmpeg:
            logger.info(f"Using system FFmpeg: {system_ffmpeg}")
            return system_ffmpeg
        
        # Need to download
        logger.info("FFmpeg not found. Attempting download...")
        try:
            downloaded_path = self._download_and_install()
            
            # Test if downloaded FFmpeg has required codecs
            if self._test_ffmpeg(downloaded_path):
                return downloaded_path
            else:
                logger.warning("Downloaded FFmpeg is missing required codecs (libx264/aac)")
                raise RuntimeError(
                    "Downloaded FFmpeg build is incomplete.\n\n"
                    "Please install FFmpeg via Homebrew for full codec support:\n"
                    "1. Install Homebrew: https://brew.sh\n"
                    "2. Run: brew install ffmpeg\n"
                    "3. Restart this application"
                )
        except Exception as e:
            logger.error(f"FFmpeg download failed: {e}")
            raise RuntimeError(
                "Could not download FFmpeg automatically.\n\n"
                "Please install FFmpeg manually via Homebrew:\n"
                "1. Install Homebrew: https://brew.sh\n"
                "2. Run: brew install ffmpeg\n"
                "3. Restart this application"
            )
    
    def _find_system_ffmpeg(self) -> str:
        """Try to find FFmpeg in system."""
        import shutil as sh
        
        # Check PATH
        ffmpeg_path = sh.which("ffmpeg")
        if ffmpeg_path and self._test_ffmpeg(ffmpeg_path):
            return ffmpeg_path
        
        # Check common locations
        common_paths = []
        
        if self.system == "Darwin":
            common_paths = [
                "/opt/homebrew/bin/ffmpeg",
                "/usr/local/bin/ffmpeg",
            ]
        elif self.system == "Linux":
            common_paths = [
                "/usr/bin/ffmpeg",
                "/usr/local/bin/ffmpeg",
            ]
        elif self.system == "Windows":
            common_paths = [
                "C:\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            ]
        
        for path in common_paths:
            if Path(path).exists() and self._test_ffmpeg(path):
                return path
        
        return None
    
    def _test_ffmpeg(self, path: str) -> bool:
        """Test if FFmpeg executable works and has required codecs."""
        try:
            # Test version
            result = subprocess.run(
                [path, "-version"],
                capture_output=True,
                timeout=3
            )
            if result.returncode != 0:
                return False
            
            # Test for required codecs
            result = subprocess.run(
                [path, "-codecs"],
                capture_output=True,
                timeout=3,
                text=True
            )
            if result.returncode == 0:
                output = result.stdout
                # Check for essential codecs
                has_h264 = "libx264" in output or "DEV.LS h264" in output
                has_aac = "aac" in output.lower()
                return has_h264 and has_aac
            
            return False
        except:
            return False
    
    def _download_and_install(self) -> str:
        """Download and install FFmpeg (and ffprobe for macOS)."""
        try:
            # Get download URL for this platform
            if self.system not in self.FFMPEG_URLS:
                raise RuntimeError(f"Unsupported platform: {self.system}")
            
            platform_urls = self.FFMPEG_URLS[self.system]
            
            # macOS: Download both ffmpeg and ffprobe separately
            if self.system == "Darwin":
                if self.machine not in platform_urls:
                    raise RuntimeError(f"No FFmpeg build for {self.machine}")
                
                urls_dict = platform_urls[self.machine]
                
                # Download and install both
                for binary_name, url in urls_dict.items():
                    logger.info(f"Downloading {binary_name} from {url}")
                    self._download_binary(url, binary_name)
                
                ffmpeg_path = self.install_dir / "ffmpeg"
                return str(ffmpeg_path)
            
            # Linux/Windows: Download full package (includes both)
            else:
                url = None
                if self.machine in platform_urls:
                    url = platform_urls[self.machine]
                elif "x86_64" in platform_urls or "AMD64" in platform_urls:
                    url = platform_urls.get("x86_64") or platform_urls.get("AMD64")
                
                if not url:
                    raise RuntimeError(f"No FFmpeg build for {self.machine}")
                
                logger.info(f"Downloading FFmpeg from {url}")
                return self._download_package(url)
            
        except Exception as e:
            logger.error(f"Failed to download FFmpeg: {e}")
            raise RuntimeError(
                f"Could not install FFmpeg automatically: {e}\n\n"
                "Please install FFmpeg manually:\n"
                "  macOS: brew install ffmpeg\n"
                "  Linux: sudo apt install ffmpeg\n"
                "  Windows: Download from https://ffmpeg.org"
            )
    
    def _download_binary(self, url: str, binary_name: str):
        """Download and install a single binary (for macOS)."""
        download_path = self.install_dir / f"{binary_name}_download"
        download_path.mkdir(exist_ok=True)
        
        archive_path = download_path / f"{binary_name}_archive"
        
        # Download
        logger.info(f"Downloading {binary_name} (this may take a moment)...")
        urllib.request.urlretrieve(url, archive_path)
        
        # Detect file type and extract
        import subprocess
        file_type = subprocess.run(
            ["file", "-b", str(archive_path)],
            capture_output=True, text=True
        ).stdout.lower()
        
        logger.info(f"Extracting {binary_name}...")
        if "zip" in file_type:
            self._extract_zip(archive_path, download_path)
        else:
            self._extract_tar(archive_path, download_path)
        
        # Find binary
        binary_file = self._find_binary_in_dir(download_path, binary_name)
        if not binary_file:
            raise RuntimeError(f"{binary_name} binary not found in download")
        
        # Move to install directory
        final_path = self.install_dir / binary_name
        shutil.copy2(binary_file, final_path)
        final_path.chmod(0o755)
        
        # Cleanup
        shutil.rmtree(download_path)
        
        logger.info(f"{binary_name} installed successfully")
    
    def _download_package(self, url: str) -> str:
        """Download and install full package (for Linux/Windows)."""
        download_path = self.install_dir / "ffmpeg_download"
        download_path.mkdir(exist_ok=True)
        
        # Determine file extension
        if url.endswith(".zip"):
            archive_path = download_path / "ffmpeg.zip"
        elif url.endswith(".tar.xz"):
            archive_path = download_path / "ffmpeg.tar.xz"
        else:
            archive_path = download_path / "ffmpeg_archive"
        
        # Download
        logger.info("Downloading FFmpeg (this may take a minute)...")
        urllib.request.urlretrieve(url, archive_path)
        
        # Detect file type
        import subprocess
        file_type = subprocess.run(
            ["file", "-b", str(archive_path)],
            capture_output=True, text=True
        ).stdout.lower()
        
        # Extract
        logger.info("Extracting FFmpeg...")
        if "zip" in file_type:
            self._extract_zip(archive_path, download_path)
        else:
            self._extract_tar(archive_path, download_path)
        
        # Find and move binaries
        ffmpeg_binary = self._find_binary_in_dir(download_path, "ffmpeg")
        ffprobe_binary = self._find_binary_in_dir(download_path, "ffprobe")
        
        if not ffmpeg_binary:
            raise RuntimeError("FFmpeg binary not found in download")
        if not ffprobe_binary:
            raise RuntimeError("ffprobe binary not found in download")
        
        # Move to install directory
        ffmpeg_name = "ffmpeg.exe" if self.system == "Windows" else "ffmpeg"
        ffprobe_name = "ffprobe.exe" if self.system == "Windows" else "ffprobe"
        
        final_ffmpeg = self.install_dir / ffmpeg_name
        final_ffprobe = self.install_dir / ffprobe_name
        
        shutil.copy2(ffmpeg_binary, final_ffmpeg)
        shutil.copy2(ffprobe_binary, final_ffprobe)
        
        # Make executable on Unix
        if self.system != "Windows":
            final_ffmpeg.chmod(0o755)
            final_ffprobe.chmod(0o755)
        
        # Cleanup
        shutil.rmtree(download_path)
        
        logger.info(f"FFmpeg installed successfully: {final_ffmpeg}")
        return str(final_ffmpeg)
    
    def _extract_zip(self, archive_path: Path, extract_to: Path):
        """Extract zip archive."""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        except zipfile.BadZipFile as e:
            logger.error(f"Bad zip file: {e}")
            raise RuntimeError(f"Downloaded file is not a valid zip: {e}")
    
    def _extract_tar(self, archive_path: Path, extract_to: Path):
        """Extract tar archive."""
        with tarfile.open(archive_path, 'r:*') as tar_ref:
            tar_ref.extractall(extract_to)
    
    def _find_binary_in_dir(self, directory: Path, binary_name: str) -> Path:
        """Find binary in extracted directory."""
        if self.system == "Windows":
            search_names = [f"{binary_name}.exe"]
        else:
            search_names = [binary_name]
        
        # Search recursively
        for name in search_names:
            for path in directory.rglob(name):
                if path.is_file():
                    return path
        
        return None


# Global installer instance
_installer = None


def get_ffmpeg_path() -> str:
    """
    Get FFmpeg path, installing automatically if needed.
    
    Returns:
        Path to FFmpeg executable
    """
    global _installer
    if _installer is None:
        _installer = FFmpegInstaller()
    
    return _installer.get_ffmpeg_path()
