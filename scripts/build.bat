@echo off
REM Build script for Windows

echo Building 2D to 3D Converter...

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Build application
echo Building executable...
pyinstaller --name="Converter3D" ^
    --windowed ^
    --icon=assets/icon.ico ^
    --add-data="config.yaml;." ^
    --add-data="assets;assets" ^
    --hidden-import=torch ^
    --hidden-import=cv2 ^
    --hidden-import=PyQt6 ^
    src/app.py

echo Build complete! Executable is in dist\Converter3D\
pause
