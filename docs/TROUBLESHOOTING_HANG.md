# Troubleshooting: "Converting..." Hangs Forever

## Problem

When you click the "Convert" button, the app shows "Converting..." but appears to hang forever with no progress.

## Root Cause

The app uses AI models (MiDaS DPT-Large) for depth estimation. On **first run**, these models need to be downloaded from the internet (~1.3 GB). During this download, the app may appear frozen because:

1. The download happens in the background with minimal feedback
2. No progress bar shows the download status
3. The process can take 5-30 minutes depending on your internet speed

## Solution

### Option 1: Pre-download Models (Recommended)

Run the model download script **before** your first conversion:

```bash
cd /Users/SB/Downloads/3d_conversion_app_python
python3 download_models.py
```

This script will:
- Download all required models (~1.3 GB)
- Show progress during download
- Cache models for future use
- Test that everything works

After this completes, conversions will start immediately.

### Option 2: Wait During First Conversion

If you already clicked "Convert":

1. **Don't close the app** - it's downloading models in the background
2. Wait 5-30 minutes (depending on internet speed)
3. Check the terminal/console for download progress
4. Once complete, future conversions will be instant

### Option 3: Run from Terminal to See Progress

Instead of double-clicking the app, run it from Terminal to see what's happening:

```bash
cd /Users/SB/Downloads/3d_conversion_app_python
python3 app.py
```

You'll see messages like:
```
Loading midas_v3 model on mps...
Note: First-time download may take several minutes (~1.3 GB)
Downloading/Loading MiDaS DPT-Large...
Downloading: "https://github.com/isl-org/MiDaS/releases/download/v3/dpt_large_384.pt"
```

## How to Verify Models Are Downloaded

Check if models are cached:

```bash
ls -lh ~/.cache/torch/hub/checkpoints/
```

You should see:
- `dpt_large_384.pt` (~1.3 GB) - Main depth estimation model

## Why This Happens

The MiDaS model is loaded using PyTorch Hub, which automatically downloads models on first use. This is standard behavior for AI applications, but it can be confusing if you don't know it's happening.

## Future Improvements

We plan to add:
- [ ] Pre-download prompt on first launch
- [ ] Progress bar for model downloads
- [ ] Offline mode with pre-bundled models
- [ ] Better error messages if download fails
- [ ] Option to use smaller/faster models

## Still Not Working?

If the app still hangs after downloading models:

1. **Check internet connection** - models require download
2. **Check disk space** - need ~2 GB free
3. **Check GPU compatibility** - CUDA/Metal/MPS
4. **Run from terminal** - see actual error messages:
   ```bash
   cd /Users/SB/Downloads/3d_conversion_app_python
   python3 app.py 2>&1 | tee app_debug.log
   ```
5. **Check the log file** - `app_debug.log` will contain errors

## Related Files

- `download_models.py` - Script to pre-download models
- `src/ai_core/depth_estimation.py` - Model loading code
- `src/ui/progress_dialog.py` - Conversion progress UI

## System Requirements

- **Disk Space**: 2 GB free (for models and temporary files)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Internet**: Required for first-time model download
- **GPU**: Optional but highly recommended
  - NVIDIA GPU with CUDA
  - Apple Silicon (M1/M2/M3) with Metal
  - AMD GPU (limited support)
