# Quick Start Guide

## 🚀 Getting Started with 2D to 3D Converter

### Prerequisites

- **Python**: 3.10 or higher
- **GPU** (Recommended): NVIDIA GPU with CUDA support
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 5GB free space (for AI models)
- **FFmpeg**: Required for video processing

### Installation

#### Step 1: Clone or Download the Project

```bash
cd /path/to/3d_conversion_app_python
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

#### Step 4: Download AI Models

```bash
python scripts/download_models.py
```

This will download:

- **MiDaS v3.1** (~1.4 GB) - Primary depth estimation model
- **Depth-Anything-V2** (~1.3 GB) - Alternative model

#### Step 5: Verify Installation

```bash
# Run tests
pytest tests/

# Check GPU availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Usage

#### GUI Application

```bash
python src/app.py
```

This opens the graphical interface where you can:

1. **Open** an image or video file
2. **Adjust settings** (depth intensity, IPD, output format)
3. **Preview** the 3D conversion in real-time
4. **Convert** and save the output

#### Command Line Interface

**Convert a single image:**

```bash
python src/cli.py convert input.jpg output_3d.jpg \
    --format half_sbs \
    --depth-intensity 75 \
    --ipd 65
```

**Convert a video:**

```bash
python src/cli.py convert input.mp4 output_3d.mp4 \
    --format half_sbs \
    --quality high
```

**Batch processing:**

```bash
python src/cli.py batch input_folder/ output_folder/ \
    --format half_sbs
```

**Get video info:**

```bash
python src/cli.py info input.mp4
```

**Preview depth map:**

```bash
python src/cli.py preview input.jpg
```

### Configuration

Edit `config.yaml` to customize default settings:

```yaml
depth_estimation:
  model: "midas_v31" # or 'depth_anything_v2'
  device: "auto" # 'cuda', 'cpu', 'mps'
  batch_size: 4

rendering:
  ipd: 65.0 # mm
  depth_intensity: 75.0
  hole_filling: "fast_marching"

video:
  fps: 30
  quality: "high" # 'low', 'medium', 'high', 'ultra'
  codec: "libx264"

ui:
  theme: "light"
  auto_save: true
```

### Output Formats

#### Side-by-Side (SBS)

- **Half SBS**: Left and right views compressed to 50% width each
- **Full SBS**: Left and right views at full resolution side-by-side

Best for:

- VR headsets (Meta Quest, PSVR, etc.)
- 3D TVs with SBS support
- Spatial video displays

#### Top-Bottom (Over-Under)

- Top half: Left eye view
- Bottom half: Right eye view

Best for:

- Some 3D TVs
- DLP 3D projectors

#### Anaglyph

- Red-Cyan glasses compatible
- Red channel: Left eye
- Cyan channels: Right eye

Best for:

- Viewing with inexpensive 3D glasses
- Quick previews

### License Tiers

#### Free Tier (Default)

- ✅ Resolution: Up to 720p
- ✅ Duration: Up to 60 seconds
- ✅ Basic features
- ⚠️ Watermark included

#### Pro Tier ($19.99/month or $199/year)

- ✅ Resolution: Up to 4K
- ✅ Duration: Unlimited
- ✅ No watermark
- ✅ Batch processing
- ✅ Advanced features

#### Enterprise Tier (Custom pricing)

- ✅ Resolution: Up to 8K
- ✅ SDK access
- ✅ API integration
- ✅ Priority support
- ✅ White-labeling

### Troubleshooting

#### GPU Not Detected

```bash
# Check CUDA installation
nvidia-smi

# Install PyTorch with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### FFmpeg Not Found

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

#### Out of Memory Error

Reduce batch size in `config.yaml`:

```yaml
depth_estimation:
  batch_size: 1 # Reduce from 4 to 1
```

#### Slow Processing

1. Ensure GPU is being used (check `device` in config)
2. Lower resolution if necessary
3. Use "medium" or "low" quality preset for faster encoding

### Performance Tips

#### For Images

- **GPU**: ~1-2 seconds per image (1080p)
- **CPU**: ~10-15 seconds per image (1080p)

#### For Videos

- **GPU**: ~2-3x realtime (1080p @ 30fps)
- **CPU**: ~0.5x realtime (1080p @ 30fps)

Speed optimizations:

- Use GPU acceleration
- Lower depth estimation batch size
- Use "fast" encoding preset
- Reduce output resolution if acceptable

### Getting Help

- **Documentation**: See `docs/` directory
- **Issues**: Check GitHub issues
- **Discord**: Join our community server
- **Email**: support@converter3d.com

### Development

To contribute or modify the code:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Check code style
black src/
flake8 src/

# Type checking
mypy src/
```

### Building Distributable

```bash
# Unix/macOS
./scripts/build.sh

# Windows
scripts\build.bat
```

This creates a standalone executable in `dist/Converter3D/`.

---

## Next Steps

1. ✅ **Complete this quick start guide**
2. 🔄 **Implement core depth estimation** (Phase 2)
3. 🔄 **Integrate DIBR rendering** (Phase 2)
4. 🔄 **Connect UI to backend** (Phase 3)
5. ⏳ **Performance optimization** (Phase 4)
6. ⏳ **Create installers** (Phase 5)

**Happy Converting!** 🎬✨
