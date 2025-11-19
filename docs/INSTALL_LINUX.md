# 📦 Installation Guide - Linux

**2D to 3D Converter v1.0**  
**Platform:** Linux (64-bit)  
**Last Updated:** November 19, 2025

---

## System Requirements

### Minimum Requirements

- **OS:** Ubuntu 20.04, Fedora 35, or equivalent
- **Processor:** Intel Core i5 or AMD Ryzen 5
- **RAM:** 8 GB
- **Storage:** 5 GB free space
- **Graphics:** OpenGL 3.3+ compatible GPU
- **Internet:** Required for initial model download

### Recommended Requirements

- **OS:** Ubuntu 22.04 LTS or later
- **Processor:** Intel Core i7/i9 or AMD Ryzen 7/9
- **RAM:** 16 GB or more
- **Storage:** 10 GB free space (SSD preferred)
- **Graphics:** NVIDIA GTX 1060 / AMD RX 580 or better
- **Internet:** Broadband connection

### Supported Distributions

- ✅ Ubuntu 20.04, 22.04, 23.10, 24.04
- ✅ Debian 11, 12
- ✅ Fedora 38, 39, 40
- ✅ Arch Linux (latest)
- ✅ openSUSE Leap 15.5+
- ✅ Linux Mint 21+
- ⚠️ Other distros may work (not officially tested)

---

## Installation Methods

### Method 1: AppImage (Recommended)

**Universal format - works on most Linux distributions**

**Step 1: Download**

```bash
wget https://3dconversion.app/downloads/2D-to-3D-Converter-v1.0-x86_64.AppImage
```

**Step 2: Make Executable**

```bash
chmod +x 2D-to-3D-Converter-v1.0-x86_64.AppImage
```

**Step 3: Run**

```bash
./2D-to-3D-Converter-v1.0-x86_64.AppImage
```

**Step 4: Integrate with Desktop (Optional)**

Install AppImageLauncher for automatic integration:

**Ubuntu/Debian:**

```bash
sudo add-apt-repository ppa:appimagelauncher-team/stable
sudo apt update
sudo apt install appimagelauncher
```

**Fedora:**

```bash
sudo dnf install appimagelauncher
```

**Arch Linux:**

```bash
yay -S appimagelauncher
```

Then double-click the AppImage - it will auto-integrate!

**Manual Integration:**

```bash
# Move to applications directory
mkdir -p ~/.local/bin
mv 2D-to-3D-Converter-v1.0-x86_64.AppImage ~/.local/bin/

# Create desktop entry
cat > ~/.local/share/applications/3dconverter.desktop << EOF
[Desktop Entry]
Name=2D to 3D Converter
Exec=$HOME/.local/bin/2D-to-3D-Converter-v1.0-x86_64.AppImage
Icon=3dconverter
Type=Application
Categories=Graphics;AudioVideo;
Comment=Convert 2D images/videos to 3D stereoscopic format
EOF

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

---

### Method 2: Package Manager (Coming Soon)

**Ubuntu/Debian (.deb package):**

```bash
wget https://3dconversion.app/downloads/2d-to-3d-converter_1.0_amd64.deb
sudo apt install ./2d-to-3d-converter_1.0_amd64.deb
```

**Fedora (.rpm package):**

```bash
wget https://3dconversion.app/downloads/2d-to-3d-converter-1.0-1.x86_64.rpm
sudo dnf install ./2d-to-3d-converter-1.0-1.x86_64.rpm
```

**Arch Linux (AUR):**

```bash
yay -S 3d-conversion-app
# or
paru -S 3d-conversion-app
```

---

### Method 3: Build from Source

**Prerequisites:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git \
    build-essential libgl1-mesa-glx libglib2.0-0

# Fedora
sudo dnf install python3 python3-pip git gcc gcc-c++ \
    mesa-libGL glib2

# Arch Linux
sudo pacman -S python python-pip git base-devel mesa
```

**Build Steps:**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/3d_conversion_app_python.git
cd 3d_conversion_app_python

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements-gui.txt

# 4. Run application
python3 app.py
```

**Build AppImage:**

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --name "2D-to-3D-Converter" --windowed --onedir app.py

# Download appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Create AppImage structure
mkdir -p AppDir/usr/bin
cp dist/2D-to-3D-Converter/* AppDir/usr/bin/

# Create .desktop file
cat > AppDir/3dconverter.desktop << EOF
[Desktop Entry]
Name=2D to 3D Converter
Exec=2D-to-3D-Converter
Icon=3dconverter
Type=Application
Categories=Graphics;AudioVideo;
EOF

# Build AppImage
./appimagetool-x86_64.AppImage AppDir 2D-to-3D-Converter-v1.0-x86_64.AppImage
```

---

## Troubleshooting

### Issue 1: "No such file or directory" when running AppImage

**Cause:** FUSE not installed

**Solution:**

```bash
# Ubuntu/Debian
sudo apt install fuse libfuse2

# Fedora
sudo dnf install fuse fuse-libs

# Arch Linux
sudo pacman -S fuse2
```

**Alternative (extract and run):**

```bash
./2D-to-3D-Converter-v1.0-x86_64.AppImage --appimage-extract
cd squashfs-root
./AppRun
```

### Issue 2: Application Won't Start

**Check dependencies:**

```bash
# Ubuntu/Debian
sudo apt install libgl1-mesa-glx libglib2.0-0 libxkbcommon-x11-0

# Fedora
sudo dnf install mesa-libGL glib2 libxkbcommon-x11

# Arch Linux
sudo pacman -S mesa glib2 libxkbcommon-x11
```

**Check logs:**

```bash
./2D-to-3D-Converter-v1.0-x86_64.AppImage 2>&1 | tee app.log
cat app.log
```

### Issue 3: Model Download Fails

**Solutions:**

1. Check internet connection
2. Test model server connectivity:
   ```bash
   ping download.pytorch.org
   curl -I https://download.pytorch.org
   ```
3. Disable VPN if using
4. Check firewall:
   ```bash
   sudo ufw status
   sudo ufw allow out 443/tcp
   ```
5. Manually download models:
   ```bash
   python3 -c "from src.ai_core.depth_estimation import DepthEstimator; DepthEstimator()"
   ```

### Issue 4: GPU Not Detected

**Check NVIDIA GPU:**

```bash
nvidia-smi
```

**If not working, install drivers:**

**Ubuntu/Debian:**

```bash
sudo ubuntu-drivers autoinstall
# or
sudo apt install nvidia-driver-535
```

**Fedora:**

```bash
sudo dnf install akmod-nvidia
```

**Arch Linux:**

```bash
sudo pacman -S nvidia nvidia-utils
```

**Check AMD GPU:**

```bash
lspci | grep -i amd
glxinfo | grep -i "OpenGL vendor"
```

**Install ROCm (AMD):**

```bash
# Ubuntu
wget https://repo.radeon.com/amdgpu-install/latest/ubuntu/focal/amdgpu-install_*_all.deb
sudo apt install ./amdgpu-install_*_all.deb
sudo amdgpu-install --usecase=graphics,rocm
```

### Issue 5: Out of Memory

**Check available memory:**

```bash
free -h
```

**Increase swap:**

```bash
# Create 8GB swap file
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Reduce quality settings in app**

### Issue 6: Permission Denied Errors

**Fix executable permissions:**

```bash
chmod +x 2D-to-3D-Converter-v1.0-x86_64.AppImage
```

**Fix cache directory:**

```bash
mkdir -p ~/.cache/torch/hub
chmod 755 ~/.cache/torch/hub
```

### Issue 7: Qt Platform Plugin Error

**Error:** "Could not find the Qt platform plugin 'xcb'"

**Solution:**

```bash
# Install Qt dependencies
# Ubuntu/Debian
sudo apt install libqt6gui6 libqt6widgets6 libqt6core6

# Fedora
sudo dnf install qt6-qtbase-gui

# Arch
sudo pacman -S qt6-base
```

**Or set Qt platform:**

```bash
export QT_QPA_PLATFORM=offscreen
./2D-to-3D-Converter-v1.0-x86_64.AppImage
```

---

## Uninstallation

### Remove AppImage

```bash
rm ~/.local/bin/2D-to-3D-Converter-v1.0-x86_64.AppImage
rm ~/.local/share/applications/3dconverter.desktop
update-desktop-database ~/.local/share/applications/
```

### Remove Package

**Ubuntu/Debian:**

```bash
sudo apt remove 2d-to-3d-converter
sudo apt autoremove
```

**Fedora:**

```bash
sudo dnf remove 2d-to-3d-converter
```

**Arch:**

```bash
yay -R 3d-conversion-app
```

### Remove All Data

```bash
# Remove cached models (~1.4 GB)
rm -rf ~/.cache/torch/hub/

# Remove application data
rm -rf ~/.local/share/3DConversion
rm -rf ~/.config/3DConversion
rm -rf ~/.cache/3DConversion
```

---

## Verification

### Check Installation

```bash
# Verify AppImage
ls -lh ~/.local/bin/2D-to-3D-Converter-v1.0-x86_64.AppImage

# Check desktop integration
ls -la ~/.local/share/applications/3dconverter.desktop

# Launch from terminal
~/.local/bin/2D-to-3D-Converter-v1.0-x86_64.AppImage --version
```

### Test Functionality

```bash
# 1. Launch application
./2D-to-3D-Converter-v1.0-x86_64.AppImage

# 2. In app: Add test image
# 3. Generate preview (should take <5 seconds)
# 4. Convert and check output in converted/ folder
```

---

## Getting Started

Once installed, see the [GUI User Guide](../GUI_USER_GUIDE.md) for:

- Interface walkthrough
- Converting your first image
- Settings and optimization
- Batch processing
- VR viewing

---

## Support

### Resources

- **Documentation:** [GitHub Wiki](#)
- **Issues:** [GitHub Issues](#)
- **Discord:** [Community Server](#)

### Contact

- **Email:** support@3dconversion.app
- **Website:** https://3dconversion.app

---

## Security & Privacy

### AppImage Security

- AppImages are self-contained and sandboxed
- No system modifications required
- Easy to verify integrity:
  ```bash
  sha256sum 2D-to-3D-Converter-v1.0-x86_64.AppImage
  ```

### Data Privacy

- All processing happens locally
- No telemetry by default
- Optional analytics (opt-in)
- No uploads to servers

---

## Advanced Configuration

### Command Line Options

```bash
# Enable debug logging
./2D-to-3D-Converter-v1.0-x86_64.AppImage --debug

# Set custom model cache
TORCH_HOME=/custom/path ./2D-to-3D-Converter-v1.0-x86_64.AppImage

# Use CPU only (disable GPU)
CUDA_VISIBLE_DEVICES="" ./2D-to-3D-Converter-v1.0-x86_64.AppImage
```

### Performance Tuning

**For NVIDIA GPUs:**

```bash
# Check CUDA version
nvcc --version

# Monitor GPU usage
watch -n 1 nvidia-smi
```

**For AMD GPUs (ROCm):**

```bash
# Check ROCm
rocm-smi

# Set visible devices
export HIP_VISIBLE_DEVICES=0
```

### Custom Settings

**Config file location:**

```
~/.config/3DConversion/settings.json
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

## Distribution-Specific Notes

### Ubuntu 22.04 LTS

- ✅ Recommended distro
- ✅ Best tested
- ✅ Long-term support

### Fedora 40

- ✅ Latest packages
- ✅ Wayland works
- ✅ Excellent performance

### Arch Linux

- ✅ Rolling release
- ✅ Cutting-edge packages
- ⚠️ More maintenance

### Debian 12

- ✅ Very stable
- ⚠️ Older Qt packages
- ✅ Works reliably

---

## FAQ

**Q: Which format should I use - AppImage, .deb, or .rpm?**  
A: AppImage is universal and recommended. Use .deb/.rpm if you prefer package management.

**Q: Does it work on Wayland?**  
A: Yes, tested on Wayland and X11.

**Q: Do I need NVIDIA GPU?**  
A: No, works with NVIDIA, AMD, Intel, or CPU-only. NVIDIA recommended for best performance.

**Q: Can I run on Raspberry Pi?**  
A: Not officially supported (ARM architecture). May work with source build.

**Q: Does it work offline?**  
A: Yes, after initial model download (~1.4 GB).

**Q: How do I upgrade?**  
A: Download new AppImage and replace old one.

---

**Installation complete? → See [GUI User Guide](../GUI_USER_GUIDE.md) to get started!**

_Last updated: November 19, 2025 | Version 1.0_
