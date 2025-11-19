"""
PyTest Configuration and Fixtures
"""
import pytest
import numpy as np
import cv2
from pathlib import Path


@pytest.fixture
def sample_image():
    """Create sample test image"""
    # Create a simple 640x480 RGB image
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add some gradients for testing
    image[:, :, 0] = np.linspace(0, 255, 640, dtype=np.uint8)
    return image


@pytest.fixture
def sample_depth_map():
    """Create sample depth map"""
    # Create a simple depth gradient
    depth = np.linspace(0, 1, 640, dtype=np.float32)
    depth_map = np.tile(depth, (480, 1))
    return depth_map


@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for test files"""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def sample_video_path(temp_dir):
    """Create sample video file for testing"""
    # TODO: Generate actual video file
    video_path = temp_dir / "test_video.mp4"
    # For now, just create an empty file
    video_path.touch()
    return str(video_path)
