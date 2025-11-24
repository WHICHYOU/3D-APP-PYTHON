# Video Conversion Guide 🎬

## Quick Start

### 1. Install FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
# Add to PATH
```

Verify installation:

```bash
ffmpeg -version
```

### 2. Convert Your First Video

```bash
# Basic conversion to Half Side-by-Side (VR standard)
python scripts/utils/convert_video.py input.mp4 output_3d.mp4
```

That's it! Your video will be converted to stereoscopic 3D.

---

## Command Line Options

### Basic Usage

```bash
python scripts/utils/convert_video.py <input_video> <output_video> [options]
```

### Output Formats

**Half Side-by-Side (Recommended for VR)**

```bash
python scripts/utils/convert_video.py input.mp4 output.mp4 --format half_sbs
```

- Best for VR headsets (Oculus Quest, PSVR, Google Cardboard)
- Each eye gets 50% width
- Most efficient file size

**Full Side-by-Side (Maximum Quality)**

```bash
python scripts/utils/convert_video.py input.mp4 output.mp4 --format full_sbs
```

- Full resolution per eye
- Larger file size (2x width)
- Best for high-end displays

**Anaglyph (Red-Cyan Glasses)**

```bash
python scripts/utils/convert_video.py input.mp4 output.mp4 --format anaglyph
```

- Works with cheap red-cyan 3D glasses
- Easy to test depth effect
- Same resolution as input

**Top-Bottom (3D TVs)**

```bash
python scripts/utils/convert_video.py input.mp4 output.mp4 --format top_bottom
```

- Compatible with some 3D TVs
- Each eye gets 50% height

### Depth Control

**Adjust depth intensity (0-100)**

```bash
# Subtle 3D effect
python convert_video.py input.mp4 output.mp4 --depth-intensity 50

# Normal 3D effect (default)
python convert_video.py input.mp4 output.mp4 --depth-intensity 75

# Strong 3D effect
python convert_video.py input.mp4 output.mp4 --depth-intensity 100
```

### Temporal Filtering

**Choose filtering method**

```bash
# EMA - Fast, good quality (default)
python convert_video.py input.mp4 output.mp4 --temporal-method ema

# Median - Best quality, slower
python convert_video.py input.mp4 output.mp4 --temporal-method median

# Gaussian - Smooth, artistic
python convert_video.py input.mp4 output.mp4 --temporal-method gaussian

# Disable filtering (faster, more flickering)
python convert_video.py input.mp4 output.mp4 --no-temporal-filter
```

### Frame Rate

**Change output FPS**

```bash
# Convert to 30 fps
python convert_video.py input.mp4 output.mp4 --fps 30

# Convert to 24 fps (cinematic)
python convert_video.py input.mp4 output.mp4 --fps 24
```

### Audio Control

**Remove audio from output**

```bash
python convert_video.py input.mp4 output.mp4 --no-audio
```

### Debugging

**Keep intermediate frames**

```bash
python convert_video.py input.mp4 output.mp4 --save-intermediate
```

Frames will be saved in `temp_video_work/` directory.

---

## Complete Examples

### Convert for Oculus Quest

```bash
python convert_video.py vacation.mp4 vacation_3d.mp4 \
  --format half_sbs \
  --depth-intensity 75 \
  --fps 30
```

### Convert for Testing (Anaglyph)

```bash
python convert_video.py sample.mp4 sample_test.mp4 \
  --format anaglyph \
  --depth-intensity 80
```

### High Quality Conversion

```bash
python convert_video.py movie.mp4 movie_3d.mp4 \
  --format full_sbs \
  --depth-intensity 70 \
  --temporal-method median
```

### Fast Preview (Lower Quality)

```bash
python convert_video.py clip.mp4 preview.mp4 \
  --format half_sbs \
  --depth-intensity 75 \
  --no-temporal-filter \
  --fps 15
```

---

## Batch Processing

### Convert Multiple Videos

Create a batch script:

**Bash (macOS/Linux):**

```bash
#!/bin/bash
for video in videos/*.mp4; do
    output="output/$(basename $video .mp4)_3d.mp4"
    python convert_video.py "$video" "$output" --format half_sbs
done
```

**PowerShell (Windows):**

```powershell
Get-ChildItem videos\*.mp4 | ForEach-Object {
    $output = "output\$($_.BaseName)_3d.mp4"
    python convert_video.py $_.FullName $output --format half_sbs
}
```

---

## Testing

### Run Automated Test

```bash
python test_video.py
```

This creates:

- `test_video_output/test_input.mp4` - Synthetic test video
- `test_video_output/test_output_half_sbs.mp4` - 3D conversion
- `test_video_output/test_output_anaglyph.mp4` - Testable with 3D glasses

---

## Performance Tips

### GPU vs CPU

- **GPU (CUDA/MPS):** 8-15 fps processing (recommended)
- **CPU:** 1-2 fps processing (slow, not recommended)

### Speed Optimization

1. **Use lower FPS:** `--fps 24` instead of 30 or 60
2. **Disable temporal filter:** `--no-temporal-filter` (loses quality)
3. **Use Half SBS:** Smaller output file
4. **Close other GPU applications:** Free up VRAM

### Quality Optimization

1. **Use median filtering:** `--temporal-method median`
2. **Use Full SBS format:** `--format full_sbs`
3. **Increase depth:** `--depth-intensity 90`
4. **Keep original FPS:** Don't use `--fps` option

---

## Viewing Your 3D Videos

### VR Headsets

1. Transfer video to headset
2. Use VR video player:
   - **Oculus Quest:** Skybox VR, Pigasus VR
   - **PSVR:** Media Player
   - **Google Cardboard:** VR Player, Cardboard Camera
3. Select "Side-by-Side" or "SBS" mode

### 3D Glasses (Anaglyph)

1. Get red-cyan 3D glasses ($1-5 on Amazon)
2. Play video with any video player
3. Wear glasses (red lens over left eye)

### 3D TV

1. Convert with `--format top_bottom` or `--format full_sbs`
2. Transfer to USB drive
3. Play on 3D TV
4. Enable 3D mode on TV

### Desktop (Side-by-Side)

1. View in any video player
2. Cross your eyes or use a stereoscope
3. Each eye focuses on one side

---

## Troubleshooting

### "FFmpeg not found"

```bash
# Install FFmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: Download from ffmpeg.org
```

### "CUDA out of memory"

- Close other GPU applications
- Reduce video resolution before conversion
- Use CPU mode (slower): Set `device="cpu"` in code

### "Video has no sound"

- Original video may not have audio
- Check with: `ffmpeg -i input.mp4`
- Audio preservation is automatic when present

### "Processing too slow"

- Normal: 1080p video takes 2-5 minutes on GPU
- Use `--fps 24` for faster processing
- Consider upgrading GPU
- Process shorter clips for testing

### "Too much/too little 3D effect"

```bash
# Reduce depth
python convert_video.py input.mp4 output.mp4 --depth-intensity 50

# Increase depth
python convert_video.py input.mp4 output.mp4 --depth-intensity 90
```

### "Flickering depth in video"

```bash
# Use stronger temporal filtering
python convert_video.py input.mp4 output.mp4 --temporal-method median
```

---

## Video Format Support

**Input Formats:**

- ✅ MP4 (H.264, H.265)
- ✅ AVI
- ✅ MOV
- ✅ MKV
- ✅ WebM
- ✅ FLV
- ✅ Any format supported by FFmpeg

**Output Format:**

- 📹 MP4 (H.264) with AAC audio
- 🎵 Audio copied from source

---

## System Requirements

**Minimum:**

- Python 3.10+
- 8 GB RAM
- FFmpeg 4.0+
- 10 GB free disk space (for temp files)

**Recommended:**

- Python 3.10+
- 16 GB RAM
- NVIDIA GPU with 4+ GB VRAM (or Apple M1/M2)
- FFmpeg 5.0+
- 20+ GB free disk space

**Tested On:**

- ✅ NVIDIA RTX 3080/4090 (CUDA)
- ✅ Apple M1/M2 (MPS)
- ✅ AMD GPUs (CPU fallback)
- ✅ Intel integrated graphics (CPU fallback)

---

## Advanced Usage

### Custom Processing Pipeline

Edit `convert_video.py` to customize:

- Depth model selection
- Stereo rendering parameters
- Encoding quality settings
- Temporal filter parameters

### Integration with Other Tools

```python
from src.video_processing.ffmpeg_handler import FFmpegHandler
from src.ai_core.depth_estimation import DepthEstimator
from src.rendering.dibr_renderer import DIBRRenderer

# Your custom pipeline here
```

---

## Support & Feedback

- 📝 Report issues on GitHub
- 💡 Feature requests welcome
- 🤝 Contributions appreciated

---

## License & Credits

- MiDaS model: Intel ISL (MIT License)
- FFmpeg: LGPL/GPL
- Application: [Your License]

---

**Happy 3D Converting! 🎥✨**
