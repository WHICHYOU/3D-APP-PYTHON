#!/bin/bash
# ============================================================================
# 2D-to-3D-Converter - macOS Build Script
# ============================================================================
# This script builds the macOS application bundle using PyInstaller
# 
# Requirements:
#   - Python 3.11+ with all dependencies installed
#   - PyInstaller installed (pip install pyinstaller)
#   - All requirements installed (see README.md)
#
# Usage:
#   ./build_macos.sh
# ============================================================================

set -e  # Exit on error

echo ""
echo "============================================================================"
echo "Building 2D-to-3D-Converter for macOS..."
echo "============================================================================"
echo ""

# Kill any existing processes
echo "[1/5] Stopping existing processes..."
if pkill -9 "2D-to-3D-Converter" 2>/dev/null; then
    echo "      ✓ Stopped running instances"
else
    echo "      - No running instances found"
fi

# Clean build directories
echo "[2/5] Cleaning build directories..."
if [ -d "build" ]; then
    rm -rf build
    echo "      ✓ Removed build/"
fi
if [ -d "dist" ]; then
    rm -rf dist
    echo "      ✓ Removed dist/"
fi

# Check if PyInstaller is installed
echo "[3/5] Checking PyInstaller..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "      ✗ PyInstaller not found. Installing..."
    pip install pyinstaller
fi
echo "      ✓ PyInstaller ready"

# Determine Python executable
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
    PYINSTALLER=".venv/bin/pyinstaller"
    echo "      Using virtual environment Python"
else
    PYTHON="python3"
    PYINSTALLER="pyinstaller"
    echo "      Using system Python"
fi

# Build with PyInstaller
echo "[4/5] Building application bundle (this may take several minutes)..."
echo "      Please wait..."
$PYINSTALLER --noconfirm build_config/app.spec

# Check if build was successful
echo "[5/5] Verifying build..."
if [ ! -d "dist/2D-to-3D-Converter.app" ]; then
    echo ""
    echo "============================================================================"
    echo "✗ BUILD FAILED - Application bundle not found"
    echo "============================================================================"
    echo ""
    echo "Check the error messages above for details."
    echo "Common issues:"
    echo "  - Missing dependencies (run: pip install -r requirements.txt)"
    echo "  - PyTorch not installed (run: pip install -r requirements-macos.txt)"
    echo "  - Insufficient disk space"
    echo ""
    exit 1
fi

# Success
echo ""
echo "============================================================================"
echo "✓ BUILD COMPLETE"
echo "============================================================================"
echo ""
echo "Application location: dist/2D-to-3D-Converter.app"
echo ""
echo "To run the application:"
echo "  open dist/2D-to-3D-Converter.app"
echo ""
echo "To create a DMG installer:"
echo "  brew install create-dmg"
echo "  create-dmg --volname '2D to 3D Converter' \\"
echo "    --window-pos 200 120 --window-size 800 400 \\"
echo "    --icon-size 100 \\"
echo "    --icon '2D-to-3D-Converter.app' 175 120 \\"
echo "    --hide-extension '2D-to-3D-Converter.app' \\"
echo "    --app-drop-link 625 120 \\"
echo "    '2D-to-3D-Converter.dmg' 'dist/'"
echo ""

# Show bundle size
if command -v du &> /dev/null; then
    SIZE=$(du -sh "dist/2D-to-3D-Converter.app" | cut -f1)
    echo "Bundle size: $SIZE"
    echo ""
fi

# Optional: Open the app
read -p "Open the application now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open dist/2D-to-3D-Converter.app
fi
