# Why Some MP4 Files Fail to Convert

## Root Cause

Your app is running from **source code** (not the built `.app` bundle), so FFmpeg binary detection is failing. Some videos succeed when FFmpeg happens to be found, others fail when it's not.

## The Problem

1. **No System FFmpeg**: You don't have FFmpeg installed via Homebrew
2. **Downloaded FFmpeg Missing Codecs**: The auto-downloaded FFmpeg from evermeet.cx is incomplete and missing required codecs (libx264/aac)
3. **Inconsistent Path Detection**: Each `FFmpegHandler()` instance tries to find FFmpeg independently, sometimes succeeding (cached), sometimes failing

## The Solution

### Option 1: Install FFmpeg via Homebrew (RECOMMENDED)

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg with all codecs
brew install ffmpeg

# Restart the app
```

This gives you a **complete FFmpeg** with all codecs including:

- libx264 (H.264 video encoding)
- aac (AAC audio encoding)
- All other standard codecs

### Option 2: Build and Use the .app Bundle

The built `.app` bundle includes FFmpeg binaries:

```bash
cd /Users/SB/Downloads/3d_conversion_app_python

# Kill any running instances
pkill -9 "Python" 2>/dev/null
pkill -9 "2D-to-3D-Converter" 2>/dev/null

# Build the app (takes 3-5 minutes)
rm -rf build dist
/Users/SB/Downloads/3d_conversion_app_python/.venv/bin/pyinstaller \
  --noconfirm build_config/app.spec

# Run the built app
open dist/2D-to-3D-Converter.app
```

The built app bundles FFmpeg inside `Contents/Frameworks/ffmpeg_bin/`.

## Quick Test

After installing FFmpeg via Homebrew, verify it works:

```bash
which ffmpeg
ffmpeg -version
ffmpeg -codecs 2>&1 | grep "libx264\|aac"
```

You should see output showing FFmpeg is installed with libx264 and aac codecs.

## What I Fixed in Code

I updated `src/video_processing/ffmpeg_handler.py` to:

1. **Prioritize Homebrew FFmpeg** over auto-download
2. Check PATH and common Homebrew locations first
3. Only fall back to auto-download if nothing is found
4. Give clear error message when FFmpeg is missing

The changes are already in your source code. Once you install Homebrew FFmpeg, all videos should convert successfully.
