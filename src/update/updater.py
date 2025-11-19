"""
Auto-Update System
-----------------
Handles version checking, download, and installation of updates.

Features:
- Checks for updates on launch
- Background download with progress
- Platform-specific installation
- Rollback support
- Delta updates (future)

Usage:
    from src.update.updater import UpdateManager
    
    updater = UpdateManager()
    if updater.check_for_updates():
        updater.download_update()
        updater.install_update()
"""

import requests
import json
import os
import sys
import subprocess
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Dict, Callable
from packaging import version
import tempfile
import platform


class UpdateManager:
    """Manages application updates"""
    
    # Update server configuration
    UPDATE_SERVER = "https://api.3dconversion.app"
    VERSION_ENDPOINT = "/updates/version.json"
    DOWNLOAD_ENDPOINT = "/updates/download"
    
    # Current version
    CURRENT_VERSION = "1.0.0"
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize update manager.
        
        Args:
            config_dir: Directory for update cache and metadata
        """
        if config_dir is None:
            if platform.system() == "Windows":
                config_dir = Path(os.getenv("LOCALAPPDATA")) / "3DConversion"
            elif platform.system() == "Darwin":
                config_dir = Path.home() / "Library" / "Application Support" / "com.3dconversion.app"
            else:  # Linux
                config_dir = Path.home() / ".config" / "3DConversion"
        
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_dir = self.config_dir / "updates"
        self.cache_dir.mkdir(exist_ok=True)
        
        self.version_cache = self.config_dir / "version_cache.json"
        self.update_settings = self.config_dir / "update_settings.json"
        
        # Load settings
        self.settings = self._load_settings()
        
        # Update info
        self.latest_version = None
        self.update_info = None
        self.download_path = None
        
    def _load_settings(self) -> Dict:
        """Load update settings from disk"""
        if self.update_settings.exists():
            with open(self.update_settings) as f:
                return json.load(f)
        return {
            "auto_check": True,
            "auto_download": False,
            "auto_install": False,
            "check_interval": 86400,  # 24 hours
            "last_check": 0,
            "skip_version": None
        }
    
    def _save_settings(self):
        """Save update settings to disk"""
        with open(self.update_settings, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def check_for_updates(self, force: bool = False) -> bool:
        """
        Check if updates are available.
        
        Args:
            force: Force check even if recently checked
            
        Returns:
            True if update available, False otherwise
        """
        import time
        
        # Check if we should skip this check
        if not force:
            if not self.settings["auto_check"]:
                return False
            
            last_check = self.settings.get("last_check", 0)
            interval = self.settings.get("check_interval", 86400)
            
            if time.time() - last_check < interval:
                # Use cached version info
                if self.version_cache.exists():
                    with open(self.version_cache) as f:
                        cached = json.load(f)
                        self.update_info = cached
                        self.latest_version = cached.get("version")
                        return self._is_newer_version(self.latest_version)
                return False
        
        try:
            # Fetch version info from server
            url = f"{self.UPDATE_SERVER}{self.VERSION_ENDPOINT}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            self.update_info = response.json()
            self.latest_version = self.update_info.get("version")
            
            # Cache the version info
            with open(self.version_cache, 'w') as f:
                json.dump(self.update_info, f, indent=2)
            
            # Update last check time
            self.settings["last_check"] = time.time()
            self._save_settings()
            
            # Check if this version should be skipped
            skip_version = self.settings.get("skip_version")
            if skip_version == self.latest_version:
                return False
            
            return self._is_newer_version(self.latest_version)
            
        except requests.exceptions.RequestException as e:
            print(f"Update check failed: {e}")
            return False
    
    def _is_newer_version(self, new_version: str) -> bool:
        """Check if new version is newer than current"""
        try:
            return version.parse(new_version) > version.parse(self.CURRENT_VERSION)
        except Exception:
            return False
    
    def get_update_info(self) -> Optional[Dict]:
        """Get information about available update"""
        return self.update_info
    
    def download_update(self, progress_callback: Optional[Callable] = None) -> bool:
        """
        Download the update package.
        
        Args:
            progress_callback: Function to call with download progress (0-100)
            
        Returns:
            True if download successful, False otherwise
        """
        if not self.update_info:
            print("No update info available")
            return False
        
        try:
            # Get download URL for current platform
            system = platform.system()
            downloads = self.update_info.get("downloads", {})
            
            if system == "Darwin":
                download_info = downloads.get("macos")
                extension = ".dmg"
            elif system == "Windows":
                download_info = downloads.get("windows")
                extension = ".exe"
            else:  # Linux
                download_info = downloads.get("linux")
                extension = ".AppImage"
            
            if not download_info:
                print(f"No download available for {system}")
                return False
            
            download_url = download_info.get("url")
            expected_sha256 = download_info.get("sha256")
            file_size = download_info.get("size", 0)
            
            # Download file
            filename = f"2D-to-3D-Converter-v{self.latest_version}{extension}"
            self.download_path = self.cache_dir / filename
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Download with progress
            downloaded = 0
            with open(self.download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and file_size > 0:
                            progress = int((downloaded / file_size) * 100)
                            progress_callback(progress)
            
            # Verify checksum
            if expected_sha256:
                actual_sha256 = self._calculate_sha256(self.download_path)
                if actual_sha256 != expected_sha256:
                    print("Checksum verification failed")
                    self.download_path.unlink()
                    self.download_path = None
                    return False
            
            print(f"Update downloaded: {self.download_path}")
            return True
            
        except Exception as e:
            print(f"Download failed: {e}")
            if self.download_path and self.download_path.exists():
                self.download_path.unlink()
            self.download_path = None
            return False
    
    def _calculate_sha256(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def install_update(self) -> bool:
        """
        Install the downloaded update.
        
        Returns:
            True if installation initiated, False otherwise
        """
        if not self.download_path or not self.download_path.exists():
            print("No update file to install")
            return False
        
        try:
            system = platform.system()
            
            if system == "Darwin":
                return self._install_macos()
            elif system == "Windows":
                return self._install_windows()
            else:  # Linux
                return self._install_linux()
                
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
    
    def _install_macos(self) -> bool:
        """Install update on macOS"""
        # Mount DMG
        mount_output = subprocess.check_output(
            ['hdiutil', 'attach', str(self.download_path)],
            text=True
        )
        
        # Find mount point
        for line in mount_output.split('\n'):
            if '/Volumes/' in line:
                mount_point = line.split('\t')[-1].strip()
                break
        else:
            return False
        
        # Copy app bundle
        app_source = Path(mount_point) / "2D to 3D Converter.app"
        app_dest = Path("/Applications") / "2D to 3D Converter.app"
        
        # Backup current version
        if app_dest.exists():
            backup = app_dest.parent / f"{app_dest.stem}.backup"
            if backup.exists():
                shutil.rmtree(backup)
            shutil.move(str(app_dest), str(backup))
        
        # Install new version
        shutil.copytree(str(app_source), str(app_dest))
        
        # Unmount DMG
        subprocess.run(['hdiutil', 'detach', mount_point])
        
        # Clean up download
        self.download_path.unlink()
        
        # Restart application
        subprocess.Popen(['open', str(app_dest)])
        sys.exit(0)
    
    def _install_windows(self) -> bool:
        """Install update on Windows"""
        # Run installer with silent flag
        subprocess.Popen([
            str(self.download_path),
            '/SILENT',
            '/CLOSEAPPLICATIONS',
            '/RESTARTAPPLICATIONS'
        ])
        
        # Exit current instance
        sys.exit(0)
    
    def _install_linux(self) -> bool:
        """Install update on Linux (AppImage)"""
        # Get current AppImage path
        current_app = Path(sys.argv[0]).resolve()
        
        if not current_app.exists():
            print("Cannot determine current AppImage location")
            return False
        
        # Backup current version
        backup = current_app.parent / f"{current_app.stem}.backup"
        if backup.exists():
            backup.unlink()
        shutil.copy2(current_app, backup)
        
        # Replace with new version
        shutil.copy2(self.download_path, current_app)
        os.chmod(current_app, 0o755)
        
        # Clean up download
        self.download_path.unlink()
        
        # Restart application
        subprocess.Popen([str(current_app)])
        sys.exit(0)
    
    def skip_version(self, version: str):
        """Mark a version to be skipped"""
        self.settings["skip_version"] = version
        self._save_settings()
    
    def enable_auto_update(self, auto_check: bool = True, 
                          auto_download: bool = False,
                          auto_install: bool = False):
        """
        Configure auto-update settings.
        
        Args:
            auto_check: Automatically check for updates
            auto_download: Automatically download updates
            auto_install: Automatically install updates (not recommended)
        """
        self.settings["auto_check"] = auto_check
        self.settings["auto_download"] = auto_download
        self.settings["auto_install"] = auto_install
        self._save_settings()
    
    def rollback(self) -> bool:
        """Rollback to previous version"""
        system = platform.system()
        
        try:
            if system == "Darwin":
                app_path = Path("/Applications") / "2D to 3D Converter.app"
                backup_path = app_path.parent / f"{app_path.stem}.backup"
                
                if not backup_path.exists():
                    print("No backup found")
                    return False
                
                # Replace current with backup
                if app_path.exists():
                    shutil.rmtree(app_path)
                shutil.move(str(backup_path), str(app_path))
                
                # Restart
                subprocess.Popen(['open', str(app_path)])
                sys.exit(0)
                
            elif system == "Windows":
                # Windows installer keeps backup automatically
                # Use Control Panel to uninstall and reinstall previous version
                print("Use Control Panel to uninstall and reinstall previous version")
                return False
                
            else:  # Linux
                current_app = Path(sys.argv[0]).resolve()
                backup_app = current_app.parent / f"{current_app.stem}.backup"
                
                if not backup_app.exists():
                    print("No backup found")
                    return False
                
                # Replace current with backup
                shutil.copy2(backup_app, current_app)
                os.chmod(current_app, 0o755)
                
                # Restart
                subprocess.Popen([str(current_app)])
                sys.exit(0)
                
        except Exception as e:
            print(f"Rollback failed: {e}")
            return False


def check_updates_on_launch():
    """
    Convenience function to check for updates on application launch.
    Returns update info if available, None otherwise.
    """
    updater = UpdateManager()
    
    if updater.check_for_updates():
        return updater.get_update_info()
    
    return None


if __name__ == "__main__":
    # Test update manager
    print("Testing Update Manager...")
    print(f"Current version: {UpdateManager.CURRENT_VERSION}")
    print(f"Platform: {platform.system()}")
    
    updater = UpdateManager()
    
    # Check for updates
    print("\nChecking for updates...")
    if updater.check_for_updates(force=True):
        info = updater.get_update_info()
        print(f"Update available: v{info['version']}")
        print(f"Release notes: {info.get('release_notes', 'N/A')}")
        
        # Download (uncomment to test)
        # print("\nDownloading update...")
        # if updater.download_update(lambda p: print(f"Progress: {p}%")):
        #     print("Download complete!")
        #     
        #     # Install (uncomment to test - will exit app!)
        #     # print("\nInstalling update...")
        #     # updater.install_update()
    else:
        print("No updates available")
