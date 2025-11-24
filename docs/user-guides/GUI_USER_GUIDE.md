# 📘 2D to 3D Converter - User Guide

**Version:** 1.0 (Phase 4)  
**Last Updated:** 2025  
**Platform:** Windows, macOS, Linux

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Interface Overview](#interface-overview)
5. [Converting Images](#converting-images)
6. [Converting Videos](#converting-videos)
7. [Batch Processing](#batch-processing)
8. [Settings Explained](#settings-explained)
9. [Output Formats](#output-formats)
10. [Viewing 3D Output](#viewing-3d-output)
11. [Troubleshooting](#troubleshooting)
12. [Tips & Best Practices](#tips--best-practices)
13. [FAQ](#faq)

---

## Introduction

Welcome to the **2D to 3D Converter** - a powerful desktop application that transforms your regular images and videos into immersive 3D content using AI depth estimation and advanced rendering techniques.

### What Can You Do?

✅ Convert regular photos to 3D stereoscopic images  
✅ Transform videos into 3D with preserved audio  
✅ Generate depth maps from any image  
✅ Create VR-ready content (Side-by-Side format)  
✅ Make anaglyph 3D for red-cyan glasses  
✅ Batch process entire folders  
✅ Preview results in real-time

### Who Is This For?

- **VR Content Creators** - Convert 2D content for VR headsets
- **Photographers** - Add depth to your photos
- **Video Editors** - Create 3D effects for videos
- **Hobbyists** - Experiment with 3D conversion
- **Researchers** - Study depth estimation and DIBR

---

## Installation

### Prerequisites

- **Operating System:** Windows 10+, macOS 10.15+, or Ubuntu 20.04+
- **Python:** 3.10 or higher
- **RAM:** 8GB minimum (16GB recommended)
- **Storage:** 5GB free space (for models and libraries)
- **GPU:** Optional but recommended (NVIDIA CUDA or Apple Metal)

### Step 1: Install Python

**Windows:**

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify: Open Command Prompt and type `python --version`

**macOS:**

1. Python 3.9 comes pre-installed
2. Or install via Homebrew: `brew install python@3.11`
3. Verify: Open Terminal and type `python3 --version`

**Linux:**

```bash
sudo apt update
sudo apt install python3.11 python3-pip
python3 --version
```

### Step 2: Install Application

1. **Download or Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/3d_conversion_app_python.git
   cd 3d_conversion_app_python
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements-gui.txt
   ```

   This will install:

   - PyQt6 (GUI framework)
   - PyTorch (AI models)
   - OpenCV (video processing)
   - FFmpeg (audio/video encoding)
   - Other supporting libraries

3. **First Run**

   ```bash
   python app.py
   ```

   On first launch, the application will automatically download AI models (~1.4GB). This is a one-time process and may take several minutes depending on your internet connection.

### Step 3: Verify Installation

If the application window opens successfully, installation is complete! You should see:

- Main window with menu bar
- Two-panel layout (file list + preview)
- Status bar at the bottom

---

## Quick Start

### 5-Minute Tutorial

1. **Launch the Application**

   ```bash
   python app.py
   ```

2. **Add a Test Image**

   - Click **"Add Files"** button
   - Select an image (JPG, PNG, etc.)
   - Or drag & drop an image into the window

3. **View Preview**

   - Image appears in the preview area
   - Switch between tabs:
     - **Original** - Your source image
     - **Depth Map** - AI-generated depth (hot colors = near, cool = far)
     - **3D Output** - Final stereoscopic result
     - **Comparison** - Side-by-side view

4. **Adjust Settings**

   - Use **Depth Intensity** slider to control 3D effect strength
   - Leave other settings at defaults for now

5. **Convert**
   - Click **"Convert Selected"**
   - Watch progress in the dialog
   - Find output in `converted/` subfolder

**Congratulations!** You just created your first 3D image. 🎉

---

## Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ File  Edit  Tools  Help                       [Menu Bar]    │
├─────────────────────────────────────────────────────────────┤
│ 📂 📁 🗑️ ▶️                                  [Toolbar]     │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ │ ┌──────────────────────────────────┐ │
│ │ File List       │ │ │ Preview Area                     │ │
│ │ ├─ image1.jpg   │ │ │ [Original] [Depth] [3D] [All]   │ │
│ │ ├─ video.mp4    │ │ │                                  │ │
│ │ └─ photo.png    │ │ │      [Image Preview Here]        │ │
│ │                 │ │ │                                  │ │
│ │ [+ Add Files]   │ │ │                                  │ │
│ │ [+ Add Folder]  │ │ └──────────────────────────────────┘ │
│ │ [− Remove]      │ │                                       │
│ │ [✕ Clear All]   │ │                                       │
│ │                 │ │                                       │
│ │ ─Settings────── │ │                                       │
│ │ Depth: [====]   │ │                                       │
│ │ IPD:   [===]    │ │                                       │
│ │ Format: [▼]     │ │                                       │
│ │ Quality: [▼]    │ │                                       │
│ │ [↻ Reset]       │ │                                       │
│ │                 │ │                                       │
│ │ [▶ Convert]     │ │                                       │
│ │ [▶▶ Convert All]│ │                                       │
│ └─────────────────┘ │                                       │
├─────────────────────────────────────────────────────────────┤
│ Ready  •  0 files loaded                      [Status Bar]  │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Menu Bar

- **File** - Open files, folders, recent items, exit
- **Edit** - Preferences, settings
- **Tools** - Batch Manager, model management
- **Help** - User guide, about, documentation

#### 2. Toolbar

Quick access buttons:

- 📂 Add Files
- 📁 Add Folder
- 🗑️ Remove Selected
- ▶️ Convert

#### 3. File List Panel (Left)

- Displays all loaded files
- Select multiple files (Ctrl+Click or Shift+Click)
- Shows file type icons (image/video)
- File management buttons

#### 4. Settings Panel (Left, Bottom)

- **Depth Intensity:** 3D effect strength (0-100)
- **IPD:** Eye separation for stereoscopy (50-80mm)
- **Output Format:** SBS, Anaglyph, Top-Bottom
- **Quality:** Low, Medium, High, Ultra
- **Hole Filling:** Smooth depth discontinuities
- **Reset Button:** Restore defaults

#### 5. Preview Panel (Right)

Tabbed interface with four views:

- **Original:** Source image/video frame
- **Depth Map:** Visualized depth estimation
- **3D Output:** Final stereoscopic result
- **Comparison:** All three views side-by-side

#### 6. Status Bar (Bottom)

- Current operation status
- File count
- Warnings and notifications

---

## Converting Images

### Single Image Conversion

1. **Load Image**

   - Click **"Add Files"**
   - Or drag & drop image file
   - Supported: JPG, PNG, BMP, TIFF, WebP

2. **Preview**

   - Select image in file list
   - Preview generates automatically
   - Switch tabs to see depth map and 3D output

3. **Adjust Settings**

   - **Depth Intensity:** Higher = stronger 3D (try 60-80)
   - **IPD:** Keep at 63mm for normal viewing
   - **Format:** Choose based on viewing method:
     - **Half SBS** - VR headsets (recommended)
     - **Anaglyph** - Red-cyan glasses
     - **Top-Bottom** - 3D TVs

4. **Convert**

   - Click **"Convert Selected"**
   - Progress dialog appears
   - Output saved to `converted/` folder

5. **Find Output**
   ```
   converted/
   ├── image1_3d_half_sbs.jpg
   └── image1_depth_map.png
   ```

### Tips for Images

- **High Resolution:** Works best with 1920×1080 or higher
- **Good Lighting:** Well-lit photos produce better depth maps
- **Clear Subjects:** Distinct foreground/background separation
- **Avoid Motion Blur:** Sharp images give best results
- **Portraits Work Great:** Faces are detected accurately

---

## Converting Videos

### Single Video Conversion

1. **Load Video**

   - Click **"Add Files"** and select video
   - Or drag & drop video file
   - Supported: MP4, AVI, MOV, MKV, WebM

2. **Preview First Frame**

   - Preview extracts first frame
   - Check if depth estimation looks good
   - Adjust settings based on preview

3. **Configure Settings**

   - **Depth Intensity:** 60-70 for videos (subtle works better)
   - **Format:** Half SBS for VR video playback
   - **Quality:** High or Ultra recommended
   - **Hole Filling:** Enable for smoother motion

4. **Convert**

   - Click **"Convert Selected"**
   - Video processing begins
   - Live preview updates during conversion
   - ETA displayed (depends on video length and GPU)

5. **Output**
   - Stereoscopic video with preserved audio
   - Same frame rate as source
   - Same resolution (adjusted for format)

### Video Processing Time

| Resolution | Length | GPU        | Estimated Time |
| ---------- | ------ | ---------- | -------------- |
| 1920×1080  | 1 min  | NVIDIA RTX | 2-3 minutes    |
| 1920×1080  | 1 min  | Apple M1   | 3-5 minutes    |
| 1920×1080  | 1 min  | CPU only   | 10-15 minutes  |
| 3840×2160  | 1 min  | NVIDIA RTX | 5-8 minutes    |

### Tips for Videos

- **Shorter Clips:** Start with 10-30 second clips for testing
- **Stable Footage:** Less camera shake = better results
- **Continuous Scenes:** Avoid rapid cuts during processing
- **Audio Preserved:** Original audio track is kept intact
- **Test Frame First:** Preview helps identify potential issues

---

## Batch Processing

### Using Batch Manager

For converting multiple files with different settings:

1. **Open Batch Manager**

   - Menu: **Tools → Batch Manager**
   - Or toolbar button

2. **Add Files to Queue**

   - Click **"Add Files"** or **"Add Folder"**
   - Files appear in queue table
   - Each row shows: File, Type, Format, Priority, Status

3. **Configure Per-File Settings**

   - Select a file in queue
   - Change output format for that file
   - Set priority (Low, Normal, High)

4. **Organize Queue**

   - **Move Up/Down:** Reorder processing
   - **Remove:** Delete unwanted items
   - **Clear All:** Empty queue

5. **Save/Load Queue**

   - **Save Queue:** Export to JSON for later
   - **Load Queue:** Import previously saved queue
   - Useful for repetitive workflows

6. **Start Batch**
   - Click **"Start Batch Conversion"**
   - Progress dialog shows overall progress
   - Files processed in order

### Batch Settings

**Default Output Format:** Applied to all new files added to queue  
**Default Priority:** Normal (can change per-file)  
**Processing Order:** High priority first, then by queue position

### Queue Table Columns

- **File:** Filename with full path on hover
- **Type:** Image or Video icon
- **Format:** Half SBS, Full SBS, Anaglyph, Top-Bottom
- **Priority:** Low, Normal, High
- **Status:** Pending, Processing, Completed, Failed

### Example Batch Workflow

```
Use Case: Convert vacation photos for VR viewing

1. Add all photos from folder (50 images)
2. Set default format to "Half SBS"
3. Set default priority to "Normal"
4. Select favorite 5 photos, change priority to "High"
5. Save queue as "vacation_photos.json"
6. Start batch conversion
7. Go grab coffee ☕
8. Return to find all images converted
```

---

## Settings Explained

### Depth Intensity (0-100)

**What it does:** Controls the strength of the 3D effect

- **0-30:** Subtle depth (subtle 3D, comfortable)
- **31-60:** Moderate depth (standard 3D effect)
- **61-80:** Strong depth (pronounced 3D, dramatic)
- **81-100:** Extreme depth (can cause eye strain)

**Recommendations:**

- **Portraits:** 50-60
- **Landscapes:** 60-75
- **Videos:** 60-70
- **VR 360:** 40-50

### IPD - Inter-Pupillary Distance (50-80mm)

**What it does:** Sets the distance between virtual cameras (simulates eye separation)

- **50-58mm:** Children, narrow faces
- **59-65mm:** Average adults (default: 63mm)
- **66-80mm:** Wide-set eyes, exaggerated effect

**Recommendations:**

- Use **63mm** for most content
- Increase for more dramatic depth
- Decrease if viewers report eye strain

### Output Format

#### Half Side-by-Side (Half SBS)

- **Best for:** VR headsets, 3D TVs
- **Size:** Same as input (each eye gets half width)
- **Quality:** Good (slight horizontal compression)
- **Use Case:** VR video players, Oculus/Meta Quest, PSVR

#### Full Side-by-Side (Full SBS)

- **Best for:** High-quality stereoscopy
- **Size:** Double width (no compression)
- **Quality:** Excellent
- **Use Case:** Professional 3D displays, cinema

#### Top-Bottom (TB)

- **Best for:** Some 3D TVs, projectors
- **Size:** Double height
- **Quality:** Good (vertical arrangement)
- **Use Case:** 3D TV playback

#### Anaglyph (Red-Cyan)

- **Best for:** Testing with 3D glasses
- **Size:** Same as input
- **Quality:** Good (color distortion inherent)
- **Use Case:** Quick viewing with red-cyan glasses, sharing online

### Quality Presets

#### Low

- **Processing:** Fast
- **GPU Memory:** 2GB
- **Details:** Reduced
- **Use:** Quick testing, previews

#### Medium (Default)

- **Processing:** Moderate
- **GPU Memory:** 4GB
- **Details:** Good balance
- **Use:** General use, most content

#### High

- **Processing:** Slow
- **GPU Memory:** 6GB
- **Details:** Excellent
- **Use:** Final output, important content

#### Ultra

- **Processing:** Very slow
- **GPU Memory:** 8GB+
- **Details:** Maximum
- **Use:** Professional work, archival

### Hole Filling

**What it does:** Smooths artifacts in depth-based rendering

- **Enabled:** Fills gaps where depth discontinuities occur
- **Disabled:** Faster but may show holes in 3D view

**When to use:**

- ✅ Videos (prevents flickering)
- ✅ Complex scenes (many depth layers)
- ⚠️ Can slightly soften fine details

---

## Output Formats

### File Naming

Converted files follow this pattern:

```
{original_name}_3d_{format}_{timestamp}.{ext}
```

Examples:

```
sunset.jpg → sunset_3d_half_sbs_20250119_143025.jpg
video.mp4 → video_3d_half_sbs_20250119_143025.mp4
```

### Output Location

```
your_project_folder/
├── input_images/
│   └── photo.jpg
├── converted/
│   ├── photo_3d_half_sbs.jpg       # 3D output
│   └── photo_depth_map.png         # Depth map
└── app.py
```

### Depth Maps

Always saved alongside 3D output:

- **Filename:** `{original}_depth_map.png`
- **Format:** Grayscale or color-mapped
- **Use:** Debugging, analysis, custom processing

---

## Viewing 3D Output

### VR Headsets

**Meta Quest / Oculus:**

1. Copy Half SBS files to headset
2. Open media player app (Skybox VR, DeoVR)
3. Select "3D Side-by-Side" mode
4. Enjoy immersive viewing

**PSVR / PC VR:**

1. Transfer files to PC
2. Use VR video player (BigScreen, Virtual Desktop)
3. Select SBS format
4. View in headset

### Red-Cyan Glasses

**Anaglyph Format:**

1. Convert using "Anaglyph" output format
2. Open image/video on any device
3. Wear red-cyan 3D glasses (red on left eye)
4. View normally - 3D effect appears

### 3D TVs / Monitors

**Side-by-Side:**

1. Convert using "Full SBS" or "Half SBS"
2. Copy to USB drive
3. Connect to 3D TV
4. Enable 3D mode on TV (Side-by-Side)
5. Wear active shutter glasses (if required)

**Top-Bottom:**

1. Convert using "Top-Bottom" format
2. TV must support TB format
3. Enable 3D mode (Top-Bottom)

### Computer (Cross-Eyed Viewing)

**Free Viewing Method:**

1. Open Half SBS image
2. Place eyes ~20" from screen
3. Cross eyes slightly until images overlap
4. Focus - 3D effect appears

**Note:** Requires practice, not comfortable for everyone

---

## Troubleshooting

### Application Won't Launch

**Problem:** Python error or nothing happens

**Solutions:**

1. Verify Python version: `python --version` (need 3.10+)
2. Reinstall dependencies: `pip install -r requirements-gui.txt --force-reinstall`
3. Check error log: Open `app.log` file
4. Try: `python3 app.py` instead of `python app.py`

### Model Download Fails

**Problem:** Timeout or connection error during first launch

**Solutions:**

1. Check internet connection
2. Disable VPN (some regions block Hugging Face)
3. Manually download models:
   ```bash
   python -c "from src.ai_core.depth_estimation import DepthEstimator; DepthEstimator()"
   ```
4. Wait 10-15 minutes for large model files

### Out of Memory Error

**Problem:** GPU memory error during conversion

**Solutions:**

1. Lower quality setting (High → Medium → Low)
2. Close other GPU applications (games, 3D software)
3. Process smaller images (resize to 1920×1080)
4. Enable CPU mode in settings (slower but works)
5. Restart application to clear memory

### Depth Map Looks Wrong

**Problem:** Incorrect depth estimation (foreground as background)

**Solutions:**

1. Try different depth intensity (50-70 range)
2. Use higher quality preset
3. Ensure good lighting in source image
4. Check for motion blur or low contrast
5. Some scenes are inherently difficult (mirrors, glass)

### 3D Effect Not Visible

**Problem:** Output looks flat or incorrect

**Solutions:**

1. Verify correct output format for your viewing device
2. Check IPD setting (try 63mm default)
3. Increase depth intensity (try 70-80)
4. Ensure viewing device is set to correct 3D mode
5. For anaglyph: confirm red filter over LEFT eye

### Video Processing is Slow

**Problem:** Takes too long to convert video

**Solutions:**

1. Check GPU is being used (watch GPU activity)
2. Install GPU drivers (NVIDIA CUDA / Apple Metal)
3. Lower quality setting
4. Process shorter clips
5. Close background applications
6. Upgrade hardware (GPU is critical)

### Audio Missing from Video

**Problem:** Converted video has no sound

**Solutions:**

1. Verify source video has audio track
2. Check output file in media player
3. Try different video player
4. Reinstall FFmpeg:
   ```bash
   pip install --upgrade opencv-python
   ```

### Conversion Fails Midway

**Problem:** Processing stops with error

**Solutions:**

1. Check disk space (need ~2x input file size)
2. Review `app.log` for error details
3. Try different file (file may be corrupted)
4. Update all dependencies:
   ```bash
   pip install --upgrade -r requirements-gui.txt
   ```
5. Restart application

### Preview Not Updating

**Problem:** Changes don't reflect in preview

**Solutions:**

1. Re-select file in list (click it again)
2. Click "Refresh" if available
3. Close and re-add file
4. Restart application

---

## Tips & Best Practices

### Content Selection

**Good Candidates for Conversion:**
✅ Portraits with clear background  
✅ Landscapes with distinct depth layers  
✅ Architecture with geometric depth  
✅ Nature scenes (forests, mountains)  
✅ Product photography  
✅ Well-lit indoor scenes

**Challenging Content:**
⚠️ Reflective surfaces (mirrors, water)  
⚠️ Transparent objects (glass, clear plastic)  
⚠️ Low contrast scenes  
⚠️ Motion-blurred images  
⚠️ Foggy or hazy conditions  
⚠️ Complex patterns (can confuse depth)

### Optimization Tips

1. **Test Before Batch:** Always convert one sample first
2. **Start with Medium Quality:** Good balance for testing
3. **Use Presets:** Save settings for different content types
4. **Monitor GPU Temperature:** Take breaks for sustained processing
5. **Keep Originals:** Never overwrite source files
6. **Organize Output:** Create folders for different projects
7. **Backup Important Conversions:** 3D files can't be easily regenerated

### Workflow Recommendations

**For VR Content Creation:**

```
1. Capture/gather source content (16:9 ratio)
2. Test one image with Half SBS format
3. Adjust depth intensity (60-70 works well)
4. Batch convert all content
5. Transfer to VR headset
6. Review in VR player
7. Re-convert problem files with adjusted settings
```

**For Anaglyph Sharing:**

```
1. Select best images
2. Use Anaglyph format
3. Moderate depth intensity (55-65)
4. Test with red-cyan glasses
5. Share online (works in any viewer)
```

**For Professional Projects:**

```
1. Use highest source resolution available
2. Set quality to Ultra
3. Enable hole filling
4. Use Full SBS format
5. Save depth maps for archival
6. Document settings used
```

### Performance Tips

- **GPU Utilization:** Ensure CUDA (NVIDIA) or Metal (Apple) is enabled
- **RAM Management:** Close unused applications during batch processing
- **SSD vs HDD:** Process from SSD for faster read/write
- **Parallel Processing:** Batch manager processes files sequentially (by design)
- **Background Mode:** Run overnight for large batches

---

## FAQ

### General Questions

**Q: Is this free to use?**  
A: Yes, the core software is open-source. Commercial use may have different licensing.

**Q: Do I need an internet connection?**  
A: Only for initial model download (~1.4GB). After that, works offline.

**Q: What AI model is used?**  
A: MiDaS v3.1 DPT-BEiT Large for depth estimation.

**Q: Can I use my own depth maps?**  
A: Currently no, but planned for future versions.

**Q: Will this work on my old computer?**  
A: Minimum: 8GB RAM, any OS from 2020+. GPU highly recommended but not required.

### Technical Questions

**Q: Why does first conversion take so long?**  
A: Model initialization and CUDA setup happen on first run. Subsequent conversions are faster.

**Q: What's the difference between Half and Full SBS?**  
A: Half SBS compresses each eye's view to 50% width (standard for VR). Full SBS keeps full resolution (double width).

**Q: Can I adjust depth after conversion?**  
A: No, depth is "baked in" to output. Adjust settings and reconvert if needed.

**Q: Does this work with 360° videos?**  
A: Equirectangular (360°) video support planned for future release.

**Q: Why are there "holes" in my 3D output?**  
A: DIBR (Depth Image-Based Rendering) can create disocclusions. Enable "Hole Filling" to minimize this.

### Viewing Questions

**Q: What VR headsets are supported?**  
A: Any headset that supports Side-by-Side video (Meta Quest, PSVR, Valve Index, etc.)

**Q: Do I need special glasses?**  
A: Depends on format:

- Anaglyph: Red-cyan glasses (cheap, widely available)
- SBS: VR headset OR 3D TV with active glasses
- Top-Bottom: 3D TV/monitor

**Q: Can I view on a normal monitor?**  
A: Yes, using:

- Anaglyph: with red-cyan glasses
- Cross-eyed viewing: free but requires practice
- VR apps: like BigScreen on PC

**Q: Why doesn't 3D work on my phone?**  
A: Most phones don't support 3D output. Use VR headset adapter (Google Cardboard style) or convert to anaglyph.

### Conversion Questions

**Q: How long does a video take?**  
A: Depends on GPU and resolution. Roughly 2-5x real-time playback duration.

- 1 min video @ 1080p = 2-5 min processing (GPU)
- 1 min video @ 1080p = 10-20 min processing (CPU only)

**Q: Can I convert multiple videos at once?**  
A: Batch manager processes files sequentially to avoid GPU memory issues. Parallel processing may be added in future.

**Q: What's the maximum video resolution?**  
A: Tested up to 4K (3840×2160). Higher resolutions need 16GB+ GPU memory.

**Q: Why is output file size larger?**  
A: SBS formats double width (or height), increasing file size. Use video compression to reduce if needed.

**Q: Can I convert live camera feed?**  
A: Not in current version. Real-time mode planned for future release.

---

## Keyboard Shortcuts

| Shortcut                       | Action                |
| ------------------------------ | --------------------- |
| `Ctrl+O` / `Cmd+O`             | Add Files             |
| `Ctrl+Shift+O` / `Cmd+Shift+O` | Add Folder            |
| `Ctrl+R` / `Cmd+R`             | Remove Selected       |
| `Ctrl+Q` / `Cmd+Q`             | Quit Application      |
| `F5`                           | Refresh Preview       |
| `Ctrl+,` / `Cmd+,`             | Preferences (future)  |
| `F1`                           | Help Documentation    |
| `Delete`                       | Remove Selected Files |
| `Esc`                          | Cancel Conversion     |

---

## Getting Help

### Resources

- **📖 User Guide:** This document
- **🛠️ Technical Documentation:** See `PHASE4_COMPLETE.md`
- **📝 Development Plan:** See `README.md`
- **🐛 Bug Reports:** GitHub Issues
- **💬 Community:** Discord / Forum (links in README)

### Support Channels

1. **Check `app.log`** - Most issues leave clues here
2. **Search GitHub Issues** - Someone may have solved it
3. **Create New Issue** - Include log file and system info
4. **Community Forum** - Ask questions, share tips

### System Information (for bug reports)

```bash
# Run this and include output in bug reports:
python --version
pip show torch opencv-python PyQt6
```

---

## What's Next?

### Upcoming Features (Phase 5)

- ✨ Standalone installers (Windows .exe, macOS .dmg, Linux AppImage)
- 🔄 Auto-update system
- 📊 Usage analytics and crash reporting
- 🎫 License management (Free/Pro tiers)
- 🌐 Cloud processing option
- 📱 Mobile companion app
- 🎥 Real-time preview mode
- 🔌 Plugin system for custom effects

### Community Contributions

We welcome:

- 🐛 Bug reports
- 💡 Feature suggestions
- 📝 Documentation improvements
- 🔧 Code contributions
- 🎨 UI/UX enhancements

See `CONTRIBUTING.md` for guidelines.

---

## Credits

**Developed by:** [Your Team Name]  
**AI Models:** MiDaS (Intel ISL), TIMM (Ross Wightman)  
**Framework:** PyQt6 (Riverbank Computing)  
**Libraries:** PyTorch, OpenCV, FFmpeg  
**Special Thanks:** [Contributors]

---

**Thank you for using 2D to 3D Converter!**  
**Enjoy creating immersive 3D content! 🎉🎬🥽**

_Last Updated: 2025 | Version 1.0 | Phase 4 Complete_
