#!/bin/bash
# Build script for creating distributable application

set -e

echo "Building 2D to 3D Converter..."

# Clean previous builds
rm -rf build/ dist/

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

# Build application
echo "Building executable..."
pyinstaller --name="Converter3D" \
    --windowed \
    --icon=assets/icon.ico \
    --add-data="config.yaml:." \
    --add-data="assets:assets" \
    --hidden-import=torch \
    --hidden-import=cv2 \
    --hidden-import=PyQt6 \
    src/app.py

echo "Build complete! Executable is in dist/Converter3D/"
