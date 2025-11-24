# 2D to 3D SBS Converter

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![License](https://img.shields.io/badge/License-MIT-yellow) ![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)

AI-powered desktop application that converts 2D images and videos into 3D Side-by-Side (SBS) format for viewing on VR headsets, 3D displays, and AR glasses. Uses state-of-the-art depth estimation models to create immersive 3D content from standard 2D media.

## Features

- **AI Depth Estimation:** Multiple MiDaS models with configurable quality/performance tradeoffs
- **Desktop GUI:** Professional PyQt6 interface with drag-and-drop support
- **Real-Time Preview:** View depth maps and 3D results before conversion
- **Batch Processing:** Queue multiple files for automated conversion
- **Multiple Output Formats:** Side-by-Side (SBS), Anaglyph, Top-Bottom
- **Video Support:** Full video processing pipeline with FFmpeg integration
- **GPU Acceleration:** CUDA (NVIDIA), MPS (Apple Silicon), and CPU fallback
- **CLI Tools:** Command-line utilities for automation and scripting

## 🚀 Quick Start

## Installation

### Option 1: Download Pre-Built Application (Recommended)

Get the latest release for your platform:

**[📥 Download from Releases Repository](https://github.com/WHICHYOU/3D-APP-PYTHON-releases-only/releases/latest)**

Available platforms:
- **macOS:** Available now - `.zip` app bundle (Apple Silicon and Intel)
- **Windows:** Coming soon - `.zip` with CUDA support for NVIDIA GPUs
- **Linux:** Coming soon - `.tar.gz` CPU-only version

For detailed installation instructions and system requirements, visit the [Releases Repository](https://github.com/WHICHYOU/3D-APP-PYTHON-releases-only).

### Option 2: Run from Source

**macOS (Apple Silicon M1/M2/M3):**

```bash
git clone https://github.com/WHICHYOU/3D-APP-PYTHON.git
cd 3D-APP-PYTHON
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-macos.txt
python app.py
```

**Windows (with NVIDIA GPU - Recommended):**

```batch
git clone https://github.com/WHICHYOU/3D-APP-PYTHON.git
cd 3D-APP-PYTHON
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-windows.txt
python app.py
```

**Windows (CPU-only - Slower):**

```batch
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python app.py
```

**Linux:**

```bash
git clone https://github.com/WHICHYOU/3D-APP-PYTHON.git
cd 3D-APP-PYTHON
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python app.py
```

See the [GUI User Guide](docs/user-guides/GUI_USER_GUIDE.md) for detailed usage instructions and [Video Conversion Guide](docs/user-guides/VIDEO_CONVERSION_GUIDE.md) for video processing tips.

## System Requirements

### Build Requirements

- **Python 3.11+** installed and in PATH
- **PyInstaller** (`pip install pyinstaller`)
- All dependencies installed (see platform-specific requirements above)
- **Windows:** Microsoft Visual C++ Redistributable
- **macOS:** Xcode Command Line Tools (`xcode-select --install`)

### Build Commands

**macOS:**

```bash
# Make script executable (first time only)
chmod +x build_config/build_macos.sh

# Build the .app bundle
./build_config/build_macos.sh

# Output: dist/2D-to-3D-Converter.app
```

**Windows:**

```batch
# Build the .exe
build_config\build_windows.bat

# Output: dist\2D-to-3D-Converter.exe
```

**Create macOS DMG Installer:**

```bash
# Install create-dmg (first time only)
brew install create-dmg

# Create DMG
create-dmg \
  --volname "2D to 3D Converter" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "2D-to-3D-Converter.app" 175 120 \
  --hide-extension "2D-to-3D-Converter.app" \
  --app-drop-link 625 120 \
  "2D-to-3D-Converter.dmg" \
  "dist/"
```

### Automated Multi-Platform Builds

This repository includes GitHub Actions workflows for automated builds:

```bash
# Trigger builds by creating a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Or manually trigger from GitHub Actions tab
```

The workflow automatically builds for:

- ✅ macOS (Apple Silicon + Intel)
- ✅ Windows (CUDA support)
- ✅ Linux (CPU-only)

Artifacts are uploaded to GitHub Releases automatically.

## System Requirements

### Minimum Requirements

- **OS:** macOS 11.0+, Windows 10/11 64-bit, or Ubuntu 20.04+
- **Processor:** Intel Core i5 / AMD Ryzen 5 (6th gen or newer) or Apple Silicon
- **RAM:** 8GB (16GB recommended)
- **Storage:** 5GB free space (includes model downloads)

### GPU Acceleration (Recommended)

- **NVIDIA GPU:** GTX 1060 or better with CUDA support
- **Apple Silicon:** M1/M2/M3 with automatic MPS acceleration
- **CPU-only mode:** Available but 10-20x slower

### Performance Expectations

| Configuration                  | 1080p Video      | 4K Video         |
| ------------------------------ | ---------------- | ---------------- |
| NVIDIA RTX 3080 / Apple M1 Max | ~1.5-3 sec/frame | ~4-8 sec/frame   |
| NVIDIA GTX 1060 / Apple M1     | ~3-6 sec/frame   | ~10-15 sec/frame |
| CPU-only                       | ~10-20 sec/frame | ~40-80 sec/frame |

## Command Line Interface

**Convert an image:**

```bash
python scripts/utils/convert_image.py input.jpg output_3d.jpg --format half_sbs
```

**Convert a video:**

```bash
python scripts/utils/convert_video.py input.mp4 output_3d.mp4 --format half_sbs
```

## Technical Architecture

### Core Components

- **ai_core/**: Depth estimation using MiDaS models with preprocessing and optimization
- **rendering/**: DIBR (Depth Image-Based Rendering), stereoscopy, and hole-filling
- **video_processing/**: FFmpeg wrapper for frame extraction and video encoding
- **ui/**: PyQt6 GUI with preview system and settings panel
- **license/**: License management and activation system

### Technology Stack

- **Language:** Python 3.10+
- **AI Framework:** PyTorch 2.0+ with CUDA/MPS support
- **Computer Vision:** OpenCV 4.8+
- **Video Processing:** FFmpeg 5.0+
- **GUI Framework:** PyQt6 6.5+

## Documentation

### Getting Started

- **[Project Overview](PROJECT_OVERVIEW.md)** - Comprehensive project information, goals, and roadmap
- **[GUI User Guide](docs/user-guides/GUI_USER_GUIDE.md)** - Desktop application usage
- **[Video Conversion Guide](docs/user-guides/VIDEO_CONVERSION_GUIDE.md)** - Video processing tips

### For Developers

- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to the project
- **[Development Setup](docs/development/DEVELOPMENT_SETUP.md)** - Developer environment setup
- **[Documentation Index](docs/INDEX.md)** - Complete documentation overview

## Project Status

This software is under active development. Current capabilities:

- ✅ AI-powered depth estimation with multiple model options
- ✅ Professional desktop GUI with real-time preview
- ✅ Full video processing pipeline
- ✅ Batch processing with queue management
- ✅ Multiple output formats (SBS, Anaglyph, Top-Bottom)
- ✅ GPU acceleration (CUDA, MPS)
- 🚧 Standalone installers and auto-update system (in progress)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Code style and standards
- Development workflow
- Testing requirements
- Pull request process

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **MiDaS Team (Intel)** - Depth estimation model
- **PyTorch Community** - Machine learning framework
- **FFmpeg Project** - Video processing capabilities

## Support

For issues, questions, or feature requests, please use the [GitHub Issues](https://github.com/WHICHYOU/3D-APP-PYTHON/issues) page.

---

**Last Updated:** 2025-01-24
