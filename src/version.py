"""Version information for 2D to 3D Converter"""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# Release information
RELEASE_NAME = "Genesis"
RELEASE_DATE = "2025-12-01"
BUILD_NUMBER = "1000"

# Minimum requirements
MIN_PYTHON_VERSION = (3, 10)
MIN_TORCH_VERSION = "2.0.0"
MIN_CUDA_VERSION = "11.8"  # If using NVIDIA GPU

def get_version_string():
    """Get formatted version string"""
    return f"{__version__} ({RELEASE_NAME})"

def check_requirements():
    """Check if system meets minimum requirements"""
    import sys
    
    # Check Python version
    if sys.version_info < MIN_PYTHON_VERSION:
        raise RuntimeError(
            f"Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ required"
        )
    
    # Check PyTorch
    try:
        import torch
        if torch.__version__ < MIN_TORCH_VERSION:
            print(f"Warning: PyTorch {MIN_TORCH_VERSION}+ recommended")
    except ImportError:
        raise RuntimeError("PyTorch not installed")
    
    return True
