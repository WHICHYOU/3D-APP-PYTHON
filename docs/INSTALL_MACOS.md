# 📦 Installation Guide - macOS

**2D to 3D Converter v1.0**  
**Platform:** macOS 10.15 or later  
**Last Updated:** November 19, 2025

---

## System Requirements

### Minimum Requirements

- **OS:** macOS 10.15 Catalina or later
- **Processor:** Apple Silicon (M1/M2/M3) or Intel Core i5
- **RAM:** 8 GB
- **Storage:** 5 GB free space
- **Graphics:** Integrated graphics
- **Internet:** Required for initial model download

### Recommended Requirements

- **OS:** macOS 13 Ventura or later
- **Processor:** Apple Silicon (M1 Pro/Max/Ultra) or Intel Core i7
- **RAM:** 16 GB or more
- **Storage:** 10 GB free space (SSD preferred)
- **Graphics:** Dedicated GPU or Apple Neural Engine
- **Internet:** Broadband connection

---

## Installation Methods

### Method 1: DMG Installer (Recommended)

**Step 1: Download**

1. Download `2D-to-3D-Converter-v1.0-macOS.dmg` from the official website
2. File size: ~85 MB
3. Save to your Downloads folder

**Step 2: Mount DMG**

1. Double-click the downloaded `.dmg` file
2. A new window will open showing the application
3. You may see a security prompt - this is normal

**Step 3: Install**

1. Drag `2D to 3D Converter.app` to the `Applications` folder
2. Wait for the copy to complete
3. Eject the DMG by dragging it to Trash or clicking Eject

**Step 4: First Launch**

1. Open **Finder** → **Applications**
2. Find `2D to 3D Converter`
3. Right-click (or Control-click) and select **Open**
4. Click **Open** in the security dialog
   - This is only needed on first launch
   - Future launches: just double-click normally

**Step 5: Initial Setup**

- On first run, the app will download AI models (~1.4 GB)
- This takes 5-15 minutes depending on your connection
- Models are cached for future use
- Progress is shown in the app

---

### Method 2: Build from Source

**Prerequisites:**

- Python 3.10 or later
- Xcode Command Line Tools
- Homebrew (optional)

**Steps:**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/3d_conversion_app_python.git
cd 3d_conversion_app_python

# 2. Install Python dependencies
pip3 install -r requirements-gui.txt

# 3. Run application
python3 app.py
```

**Build Standalone App:**

```bash
# Install PyInstaller
pip3 install pyinstaller

# Build .app bundle
~/Library/Python/3.9/bin/pyinstaller --name "2D-to-3D-Converter" \
    --windowed --onedir app.py

# Create DMG
./build_scripts/create_dmg_macos.sh

# Find installer in dist/
ls -lh dist/*.dmg
```

---

## Troubleshooting

### Issue 1: "App can't be opened because it is from an unidentified developer"

**Solution:**

1. Open **System Settings** → **Privacy & Security**
2. Scroll down to find the blocked app message
3. Click **Open Anyway**
4. Enter your password if prompted
5. Click **Open** in the confirmation dialog

**Alternative:**

```bash
# Remove quarantine attribute
xattr -dr com.apple.quarantine "/Applications/2D to 3D Converter.app"
```

### Issue 2: App crashes on launch

**Check Console for errors:**

1. Open **Console.app** (Applications → Utilities)
2. Filter for "2D-to-3D-Converter"
3. Launch the app and observe crash logs

**Common fixes:**

- Update to latest macOS
- Ensure sufficient RAM available
- Clear app cache: `~/Library/Caches/com.3dconversion.app`
- Reinstall: Delete app and install again

### Issue 3: Model download fails

**Symptoms:** App hangs on first launch

**Solutions:**

1. Check internet connection
2. Disable VPN (some regions block model servers)
3. Manually download models:
   ```bash
   python3 -c "from src.ai_core.depth_estimation import DepthEstimator; DepthEstimator()"
   ```
4. Models cache location: `~/.cache/torch/hub/`
5. Check firewall settings

### Issue 4: GPU not detected

**Check Metal support:**

```bash
system_profiler SPDisplaysDataType | grep Metal
```

**Should show:** Metal: Supported

**If not supported:**

- GPU too old (pre-2012 Mac)
- App will fall back to CPU (slower but functional)

### Issue 5: Out of memory errors

**Solutions:**

1. Close other applications
2. Reduce quality setting in app (Ultra → High → Medium)
3. Process smaller files first
4. Upgrade RAM if possible
5. Process one file at a time (not batch)

### Issue 6: Slow performance

**Optimization tips:**

1. Ensure running on Apple Silicon or dedicated GPU
2. Close background apps
3. Use Medium quality for testing
4. Process images before videos (faster)
5. Use Half SBS format (smaller output)

---

## Uninstallation

### Remove Application

1. Open **Finder** → **Applications**
2. Find `2D to 3D Converter`
3. Drag to **Trash** or right-click → **Move to Trash**
4. Empty Trash

### Remove All Data (Optional)

**Remove cached models (~1.4 GB):**

```bash
rm -rf ~/.cache/torch/hub/
```

**Remove application data:**

```bash
rm -rf ~/Library/Application\ Support/com.3dconversion.app
rm -rf ~/Library/Caches/com.3dconversion.app
rm -rf ~/Library/Preferences/com.3dconversion.app.plist
```

**Remove logs:**

```bash
rm -rf ~/Library/Logs/2D-to-3D-Converter
```

---

## Verification

### Check Installation

**Launch Test:**

```bash
# Check if app exists
ls -la "/Applications/2D to 3D Converter.app"

# Launch from command line (for debugging)
open "/Applications/2D to 3D Converter.app"
```

**Version Check:**

1. Launch app
2. Menu: **Help** → **About**
3. Should show: Version 1.0

### Test Functionality

**Quick Test:**

1. Launch application
2. Click "Add Files"
3. Select a test image (JPG, PNG)
4. Preview should generate automatically
5. Click "Convert Selected"
6. Check output in `converted/` folder

**Expected Results:**

- Preview displays in <5 seconds
- Depth map shows color gradient
- 3D output shows side-by-side view
- Conversion completes without errors
- Output file created successfully

---

## Getting Started

Once installed, see the [GUI User Guide](user-guides/GUI_USER_GUIDE.md) for:

- Interface walkthrough
- Converting your first image
- Adjusting settings
- Batch processing
- VR headset viewing
- Troubleshooting

---

## Support

### Resources

- **User Guide:** Help → User Guide (in app)
- **Documentation:** [GitHub Wiki](#)
- **Issues:** [GitHub Issues](#)
- **Discord:** [Community Server](#)

### Contact

- **Email:** support@3dconversion.app
- **Website:** https://3dconversion.app
- **Twitter:** @3DConversionApp

---

## Security & Privacy

### Code Signing

- Current build: Not signed (requires developer certificate)
- Future releases: Will be signed and notarized
- Safe to use: Built from verified open-source code

### Data Privacy

- **No telemetry by default** - Your data stays local
- Optional analytics: Opt-in during first launch
- No images/videos uploaded to servers
- Model downloads: From official PyTorch/Hugging Face

### Permissions

- **Files and Folders:** To read input and save output
- **Network:** To download AI models (first run only)
- **GPU:** For hardware acceleration (optional)

---

## Advanced Configuration

### Command Line Usage

**Set custom model cache:**

```bash
export TORCH_HOME="/path/to/custom/cache"
open "/Applications/2D to 3D Converter.app"
```

**Enable debug logging:**

```bash
open "/Applications/2D to 3D Converter.app" --args --debug
```

**Check logs:**

```bash
tail -f ~/Library/Logs/2D-to-3D-Converter/app.log
```

### Performance Tuning

**For Apple Silicon:**

- App uses Metal acceleration automatically
- No configuration needed

**For Intel Macs:**

- Consider external GPU (eGPU) for better performance
- Thunderbolt 3 eGPU supported

### Custom Settings

**Config file location:**

```
~/Library/Application Support/com.3dconversion.app/settings.json
```

**Example settings:**

```json
{
  "default_format": "half_sbs",
  "default_quality": "high",
  "depth_intensity": 65,
  "ipd": 63,
  "auto_update_check": true,
  "analytics_enabled": false
}
```

---

## Updates

### Auto-Update (Coming Soon)

- App will check for updates on launch
- Notification when new version available
- One-click update and restart

### Manual Update

1. Download latest DMG
2. Quit current app
3. Install new version (overwrites old)
4. Launch and verify version number

### Release Notes

- Check **Help** → **Release Notes** in app
- Or visit: https://3dconversion.app/releases

---

## Platform-Specific Notes

### Apple Silicon (M1/M2/M3)

- ✅ Native ARM64 support
- ✅ Metal acceleration
- ✅ Neural Engine utilization
- ✅ Excellent performance
- ✅ Energy efficient

### Intel Macs

- ✅ x86_64 support
- ✅ Metal acceleration (2012+ models)
- ⚠️ Slower than Apple Silicon
- ⚠️ Higher power consumption
- ✅ Fully functional

### macOS Versions

- **Catalina (10.15):** Minimum supported
- **Big Sur (11):** Fully supported
- **Monterey (12):** Fully supported
- **Ventura (13):** Fully supported
- **Sonoma (14):** Fully supported
- **Sequoia (15):** Fully supported

---

## FAQ

**Q: Is this safe to install?**  
A: Yes, built from verified open-source code. Not yet code-signed, but safe.

**Q: Why is the app so large?**  
A: Includes PyTorch and AI models. First download is 85MB DMG + 1.4GB models.

**Q: Do I need internet after installation?**  
A: No, only for initial model download. Works offline after that.

**Q: Can I move the app after installation?**  
A: Yes, can be moved anywhere. Best kept in Applications folder.

**Q: Does it work offline?**  
A: Yes, after initial model download.

**Q: How do I upgrade to Pro?**  
A: Click "Upgrade" in app or visit website for license key.

---

**Installation complete? → See [GUI User Guide](user-guides/GUI_USER_GUIDE.md) to get started!**

_Last updated: November 19, 2025 | Version 1.0_
