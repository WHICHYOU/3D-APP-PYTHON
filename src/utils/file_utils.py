"""
File Utilities
File and directory operations
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional


def ensure_dir(path: str) -> Path:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        path: Directory path
    
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_size(path: str) -> int:
    """
    Get file size in bytes
    
    Args:
        path: File path
    
    Returns:
        File size in bytes
    """
    return os.path.getsize(path)


def format_file_size(bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "2.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


def get_temp_dir(base_dir: Optional[str] = None) -> Path:
    """
    Get temporary directory for processing
    
    Args:
        base_dir: Base directory for temp files
    
    Returns:
        Path to temp directory
    """
    if base_dir is None:
        base_dir = os.path.join(os.getcwd(), 'temp')
    
    temp_dir = Path(base_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    return temp_dir


def cleanup_temp_dir(temp_dir: str):
    """
    Clean up temporary directory
    
    Args:
        temp_dir: Directory to clean up
    """
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def list_files_by_extension(
    directory: str,
    extensions: List[str]
) -> List[Path]:
    """
    List files in directory with specific extensions
    
    Args:
        directory: Directory to search
        extensions: List of extensions (e.g., ['.mp4', '.avi'])
    
    Returns:
        List of matching file paths
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return []
    
    files = []
    for ext in extensions:
        # Normalize extension
        if not ext.startswith('.'):
            ext = '.' + ext
        
        files.extend(dir_path.glob(f'*{ext}'))
    
    return sorted(files)


def safe_filename(filename: str) -> str:
    """
    Create safe filename by removing invalid characters
    
    Args:
        filename: Original filename
    
    Returns:
        Safe filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename
    
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    return safe_name


def get_available_space(path: str) -> int:
    """
    Get available disk space
    
    Args:
        path: Path to check
    
    Returns:
        Available space in bytes
    """
    stat = shutil.disk_usage(path)
    return stat.free


def copy_with_progress(
    src: str,
    dst: str,
    callback: Optional[callable] = None
):
    """
    Copy file with progress callback
    
    Args:
        src: Source file path
        dst: Destination file path
        callback: Progress callback function(bytes_copied, total_bytes)
    """
    total_size = os.path.getsize(src)
    copied = 0
    
    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            while True:
                chunk = fsrc.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                
                fdst.write(chunk)
                copied += len(chunk)
                
                if callback:
                    callback(copied, total_size)


def find_video_files(directory: str) -> List[Path]:
    """
    Find all video files in directory
    
    Args:
        directory: Directory to search
    
    Returns:
        List of video file paths
    """
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    return list_files_by_extension(directory, video_extensions)
