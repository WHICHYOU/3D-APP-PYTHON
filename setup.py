"""
Setup script for 2D to 3D Converter
"""
from setuptools import setup, find_packages
import os

# Read version from version.py
version = {}
with open("src/version.py") as f:
    exec(f.read(), version)

# Read long description from README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="2d3d-converter",
    version=version["__version__"],
    author="2D3D Converter Team",
    author_email="dev@2d3dconverter.com",
    description="AI-powered 2D to 3D Side-by-Side video converter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/2d3d-converter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video :: Conversion",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "PyQt6>=6.5.0",
        "Pillow>=10.0.0",
        "ffmpeg-python>=0.2.0",
        "pyyaml>=6.0",
        "tqdm>=4.65.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "2d3d-converter=src.app:main",
            "2d3d-cli=src.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.qss", "*.png", "*.ico", "*.icns"],
    },
)
