@echo off
REM ============================================================================
REM 2D-to-3D-Converter - Windows Build Script
REM ============================================================================
REM This script builds the Windows executable using PyInstaller
REM 
REM Requirements:
REM   - Python 3.11+ with all dependencies installed
REM   - PyInstaller installed (pip install pyinstaller)
REM   - All requirements installed (see README.md)
REM
REM Usage:
REM   build_windows.bat
REM ============================================================================

echo.
echo ============================================================================
echo Building 2D-to-3D-Converter for Windows...
echo ============================================================================
echo.

REM Kill any existing processes
echo [1/5] Stopping existing processes...
taskkill /F /IM "2D-to-3D-Converter.exe" >NUL 2>&1
if %ERRORLEVEL% EQU 0 (
    echo       ✓ Stopped running instances
) else (
    echo       - No running instances found
)

REM Clean build directories
echo [2/5] Cleaning build directories...
if exist build (
    rmdir /S /Q build
    echo       ✓ Removed build/
)
if exist dist (
    rmdir /S /Q dist
    echo       ✓ Removed dist/
)

REM Check if PyInstaller is installed
echo [3/5] Checking PyInstaller...
python -c "import PyInstaller" >NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo       ✗ PyInstaller not found. Installing...
    pip install pyinstaller
    if %ERRORLEVEL% NEQ 0 (
        echo       ✗ Failed to install PyInstaller
        exit /b 1
    )
)
echo       ✓ PyInstaller ready

REM Build with PyInstaller
echo [4/5] Building executable (this may take several minutes)...
echo       Please wait...
python -m PyInstaller --noconfirm build_config\app.spec

REM Check if build was successful
echo [5/5] Verifying build...
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================================
    echo ✗ BUILD FAILED
    echo ============================================================================
    echo.
    echo Check the error messages above for details.
    echo Common issues:
    echo   - Missing dependencies (run: pip install -r requirements.txt)
    echo   - PyTorch not installed (run: pip install -r requirements-windows.txt)
    echo   - Insufficient disk space
    echo.
    exit /b 1
)

if not exist "dist\2D-to-3D-Converter.exe" (
    echo.
    echo ============================================================================
    echo ✗ BUILD FAILED - Executable not found
    echo ============================================================================
    echo.
    exit /b 1
)

REM Success
echo.
echo ============================================================================
echo ✓ BUILD COMPLETE
echo ============================================================================
echo.
echo Executable location: dist\2D-to-3D-Converter.exe
echo.
echo To run the application:
echo   dist\2D-to-3D-Converter.exe
echo.
echo To create an installer, consider using:
echo   - NSIS (Nullsoft Scriptable Install System)
echo   - Inno Setup
echo   - Or upload dist\2D-to-3D-Converter.exe to GitHub Releases
echo.

REM Optional: Show file size
for %%A in ("dist\2D-to-3D-Converter.exe") do (
    echo File size: %%~zA bytes
)

echo.
pause
