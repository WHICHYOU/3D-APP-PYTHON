# 📦 Installation Guide - Windows

**2D to 3D Converter v1.0**  
**Platform:** Windows 10/11 (64-bit)  
**Last Updated:** November 19, 2025

---

## System Requirements

### Minimum Requirements

- **OS:** Windows 10 (64-bit) version 1809 or later
- **Processor:** Intel Core i5 or AMD Ryzen 5
- **RAM:** 8 GB
- **Storage:** 5 GB free space
- **Graphics:** DirectX 11 compatible GPU
- **Internet:** Required for initial model download

### Recommended Requirements

- **OS:** Windows 11 (64-bit)
- **Processor:** Intel Core i7/i9 or AMD Ryzen 7/9
- **RAM:** 16 GB or more
- **Storage:** 10 GB free space (SSD preferred)
- **Graphics:** NVIDIA GTX 1060 / AMD RX 580 or better
- **Internet:** Broadband connection

---

## Installation Methods

### Method 1: Windows Installer (Recommended)

**Step 1: Download**

1. Download `2D-to-3D-Converter-v1.0-Setup.exe` from the official website
2. File size: ~200 MB
3. Save to your Downloads folder

**Step 2: Run Installer**

1. Double-click the downloaded `.exe` file
2. If Windows Defender SmartScreen appears:
   - Click **More info**
   - Click **Run anyway**
   - This is normal for new applications

**Step 3: Installation Wizard**

1. Click **Next** on the welcome screen
2. Accept the license agreement
3. Choose installation location (default: `C:\Program Files\2D to 3D Converter\`)
4. Select components to install:
   - ✅ Application files (required)
   - ✅ Desktop shortcut (recommended)
   - ✅ Start Menu shortcuts (recommended)
   - ⬜ File association for .jpg/.png (optional)
5. Click **Install**
6. Wait for installation to complete (~2 minutes)
7. Click **Finish**

**Step 4: First Launch**

1. Find desktop shortcut or Start Menu entry
2. Double-click to launch
3. Windows Firewall may ask for permission:
   - Allow for **Private networks** (recommended)
   - Block for **Public networks** (optional)

**Step 5: Initial Setup**

- On first run, the app will download AI models (~1.4 GB)
- This takes 5-15 minutes depending on your connection
- Models are cached in: `C:\Users\<username>\.cache\torch\hub\`
- Progress is shown in the app

---

### Method 2: Portable Version

**Step 1: Download**

1. Download `2D-to-3D-Converter-v1.0-Portable.zip`
2. File size: ~250 MB
3. No installation required

**Step 2: Extract**

1. Right-click the downloaded `.zip` file
2. Select **Extract All...**
3. Choose destination folder (e.g., `D:\PortableApps\`)
4. Click **Extract**

**Step 3: Run**

1. Navigate to extracted folder
2. Double-click `2D-to-3D-Converter.exe`
3. Create shortcut on desktop if desired

**Portable Version Benefits:**

- No admin rights required
- Can run from USB drive
- No registry entries
- Easy to move/backup

---

### Method 3: Build from Source

**Prerequisites:**

- Python 3.10 or later
- Visual Studio Build Tools 2019+
- Git for Windows

**Steps:**

```powershell
# 1. Clone repository
git clone https://github.com/yourusername/3d_conversion_app_python.git
cd 3d_conversion_app_python

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements-gui.txt

# 4. Run application
python app.py
```

**Build Standalone Executable:**

```powershell
# Install PyInstaller
pip install pyinstaller

# Build .exe
pyinstaller --name "2D-to-3D-Converter" --windowed --onefile app.py

# Find executable in dist\
dir dist\*.exe
```

---

## Troubleshooting

### Issue 1: "Windows protected your PC" SmartScreen Warning

**Solution A: Run Anyway**

1. Click **More info**
2. Click **Run anyway**
3. This is normal for unsigned applications

**Solution B: Disable SmartScreen (Not Recommended)**

1. Windows Settings → Privacy & Security → Windows Security
2. App & browser control → Reputation-based protection settings
3. Turn off "Check apps and files"
4. Install the app
5. Re-enable SmartScreen after installation

### Issue 2: Installation Fails - "Error 1603"

**Cause:** Insufficient permissions or corrupted installer

**Solutions:**

1. Right-click installer → **Run as administrator**
2. Disable antivirus temporarily
3. Re-download installer (may be corrupted)
4. Check free disk space (need 5 GB+)
5. Use portable version instead

### Issue 3: Application Won't Start

**Check Event Viewer:**

1. Press **Win + X** → Event Viewer
2. Windows Logs → Application
3. Look for errors from "2D-to-3D-Converter"

**Common fixes:**

- Install Visual C++ Redistributable 2015-2022
- Update Windows to latest version
- Update graphics drivers
- Check antivirus quarantine

**Required Dependencies:**

- Download from Microsoft: https://aka.ms/vs/17/release/vc_redist.x64.exe

### Issue 4: Model Download Fails

**Symptoms:** App hangs with "Downloading models..." message

**Solutions:**

1. Check internet connection
2. Disable VPN (some regions block model servers)
3. Check Windows Firewall:
   - Settings → Privacy & Security → Windows Security
   - Firewall & network protection
   - Allow an app through firewall
   - Add `2D-to-3D-Converter.exe`
4. Manually download models:
   ```powershell
   python -c "from src.ai_core.depth_estimation import DepthEstimator; DepthEstimator()"
   ```

### Issue 5: GPU Not Detected

**Check GPU:**

```powershell
# Open PowerShell
nvidia-smi  # For NVIDIA GPUs
```

**Should show:** GPU name, driver version, CUDA version

**If not detected:**

- Update GPU drivers from manufacturer website
- NVIDIA: https://www.nvidia.com/drivers
- AMD: https://www.amd.com/support
- Intel: https://www.intel.com/support

**Install CUDA (NVIDIA only):**

- Download CUDA Toolkit 11.8+
- https://developer.nvidia.com/cuda-downloads

### Issue 6: Out of Memory Errors

**Solutions:**

1. Close other applications
2. Reduce quality setting (Ultra → High → Medium)
3. Process smaller files
4. Increase virtual memory:
   - System → Advanced system settings
   - Performance → Settings → Advanced
   - Virtual memory → Change
   - Set custom size: Initial 16384 MB, Maximum 32768 MB
5. Upgrade RAM if possible

### Issue 7: Antivirus False Positive

**Common with:** Windows Defender, Norton, Avast

**Solutions:**

1. Add exception for application folder
2. Whitelist `2D-to-3D-Converter.exe`
3. Report false positive to antivirus vendor
4. Use portable version (less flagged)

---

## Uninstallation

### Method 1: Windows Settings

1. Windows Settings → Apps → Installed apps
2. Search for "2D to 3D Converter"
3. Click **⋯** menu → **Uninstall**
4. Confirm uninstallation
5. Follow uninstaller wizard
6. Reboot if prompted

### Method 2: Control Panel

1. Control Panel → Programs → Programs and Features
2. Find "2D to 3D Converter"
3. Right-click → **Uninstall**
4. Follow prompts

### Remove All Data (Optional)

**Remove cached models (~1.4 GB):**

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\torch\hub\"
```

**Remove application data:**

```powershell
Remove-Item -Recurse -Force "$env:APPDATA\3DConversion"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\3DConversion"
```

**Remove registry entries:**

```powershell
# Run as Administrator
Remove-Item -Path "HKCU:\Software\3DConversion" -Recurse -ErrorAction SilentlyContinue
```

---

## Verification

### Check Installation

**File Locations:**

- Program: `C:\Program Files\2D to 3D Converter\`
- Executable: `2D-to-3D-Converter.exe`
- Settings: `%APPDATA%\3DConversion\settings.json`
- Logs: `%LOCALAPPDATA%\3DConversion\logs\`

**Launch Test:**

```powershell
# Open PowerShell
cd "C:\Program Files\2D to 3D Converter"
.\2D-to-3D-Converter.exe
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
4. Preview should generate in <5 seconds
5. Click "Convert Selected"
6. Check output in `converted\` folder

---

## Getting Started

Once installed, see the [GUI User Guide](../GUI_USER_GUIDE.md) for:

- Interface walkthrough
- Converting your first image
- Adjusting settings
- Batch processing
- VR headset viewing

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

---

## Security & Privacy

### Code Signing

- Future releases will be code-signed
- Safe to use: Built from verified open-source code

### Windows Defender

- May show warning on first install (normal)
- Click "More info" → "Run anyway"

### Data Privacy

- No telemetry by default
- Optional analytics: Opt-in during first launch
- No uploads to servers
- All processing happens locally

### Required Permissions

- **Files and Folders:** To read input and save output
- **Network:** To download AI models (first run only)
- **GPU:** For hardware acceleration

---

## Advanced Configuration

### Command Line Usage

**Enable debug mode:**

```powershell
"C:\Program Files\2D to 3D Converter\2D-to-3D-Converter.exe" --debug
```

**Set custom model cache:**

```powershell
$env:TORCH_HOME = "D:\CustomCache"
.\2D-to-3D-Converter.exe
```

**Check logs:**

```powershell
Get-Content "$env:LOCALAPPDATA\3DConversion\logs\app.log" -Tail 50 -Wait
```

### Performance Tuning

**For NVIDIA GPUs:**

- Install latest Game Ready drivers
- CUDA 11.8+ recommended
- cuDNN will be auto-configured

**For AMD GPUs:**

- Install Adrenalin drivers
- ROCm support coming soon
- Currently uses CPU if AMD GPU

**Registry Tweaks (Advanced):**

```powershell
# Increase GPU priority (run as admin)
New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" -Name "GPU Priority" -Value 8 -PropertyType DWORD -Force
```

### Custom Settings

**Config file:**

```
%APPDATA%\3DConversion\settings.json
```

**Example:**

```json
{
  "default_format": "half_sbs",
  "default_quality": "high",
  "depth_intensity": 65,
  "ipd": 63,
  "auto_update_check": true,
  "analytics_enabled": false,
  "gpu_acceleration": true
}
```

---

## Platform-Specific Notes

### Windows 11

- ✅ Full support
- ✅ DirectX 12 support
- ✅ Better GPU scheduling
- ✅ WSL2 compatible

### Windows 10

- ✅ Version 1809+ supported
- ✅ DirectX 11 minimum
- ⚠️ Update to 22H2 recommended
- ✅ Fully functional

### GPU Support

- **NVIDIA:** ✅ Full CUDA support
- **AMD:** ⚠️ CPU fallback (ROCm soon)
- **Intel Arc:** ⚠️ CPU fallback
- **Integrated:** ✅ Works but slower

---

## FAQ

**Q: Is this safe to install?**  
A: Yes, built from verified open-source code. Windows Defender warning is normal.

**Q: Why does Windows Defender block it?**  
A: Not yet code-signed. Click "More info" → "Run anyway".

**Q: Do I need NVIDIA GPU?**  
A: No, works with any GPU or CPU. NVIDIA recommended for best performance.

**Q: Can I run on 32-bit Windows?**  
A: No, requires 64-bit Windows 10/11.

**Q: Does it work offline?**  
A: Yes, after initial model download.

**Q: How do I upgrade to Pro?**  
A: Click "Upgrade" in app or visit website for license key.

---

**Installation complete? → See [GUI User Guide](../GUI_USER_GUIDE.md) to get started!**

_Last updated: November 19, 2025 | Version 1.0_
