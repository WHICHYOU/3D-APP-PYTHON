# Technical Architecture Documentation

## Project Structure Overview

This document provides the complete file and folder architecture for the 2D to 3D SBS conversion software, designed as a **downloadable desktop application** with modular components suitable for B2B SDK extraction.

---

## Complete Directory Structure

```
/2d_to_3d_converter/
├── README.md
├── LICENSE
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── config.yaml
├── .gitignore
├── .env.example
│
├── src/
│   ├── __init__.py
│   │
│   ├── ai_core/                      # AI/ML depth estimation module
│   │   ├── __init__.py
│   │   ├── depth_estimation.py      # Main depth map generation logic
│   │   ├── model_loader.py          # Model loading and management
│   │   ├── preprocessing.py         # Image preprocessing pipeline
│   │   ├── postprocessing.py        # Depth map refinement
│   │   ├── temporal_filter.py       # Temporal consistency for video
│   │   ├── models/                  # AI model storage
│   │   │   ├── midas_v3_dpt_large.pt
│   │   │   ├── depth_anything_v2.pth
│   │   │   ├── model_config.json
│   │   │   └── README.md
│   │   └── __pycache__/
│   │
│   ├── rendering/                    # Stereoscopic rendering module
│   │   ├── __init__.py
│   │   ├── dibr_renderer.py         # Depth Image-Based Rendering core
│   │   ├── stereoscopy.py           # Left/right eye view generation
│   │   ├── hole_filling.py          # Inpainting algorithms for disocclusions
│   │   ├── view_synthesis.py        # Multi-layer rendering
│   │   ├── sbs_composer.py          # SBS/TB format composition
│   │   └── __pycache__/
│   │
│   ├── video_processing/             # Video I/O and frame management
│   │   ├── __init__.py
│   │   ├── ffmpeg_handler.py        # FFmpeg wrapper for video operations
│   │   ├── frame_extractor.py       # Frame extraction and buffering
│   │   ├── frame_manager.py         # Frame queue and memory management
│   │   ├── audio_handler.py         # Audio stream preservation
│   │   ├── encoder.py               # Video encoding (H.264/H.265)
│   │   └── __pycache__/
│   │
│   ├── ui/                           # Graphical User Interface
│   │   ├── __init__.py
│   │   ├── main_window.py           # Main application window (PyQt6)
│   │   ├── preview_widget.py        # Real-time preview panel
│   │   ├── settings_panel.py        # Parameter adjustment controls
│   │   ├── progress_dialog.py       # Conversion progress UI
│   │   ├── batch_manager.py         # Batch processing interface
│   │   ├── help_dialog.py           # In-app help and documentation
│   │   ├── about_dialog.py          # About/license information
│   │   ├── license_dialog.py        # License activation UI
│   │   ├── resources/               # UI assets
│   │   │   ├── icons/
│   │   │   │   ├── app_icon.ico
│   │   │   │   ├── app_icon.icns
│   │   │   │   ├── convert.png
│   │   │   │   ├── preview.png
│   │   │   │   └── settings.png
│   │   │   ├── images/
│   │   │   │   ├── logo.png
│   │   │   │   ├── splash.png
│   │   │   │   └── tutorial/
│   │   │   └── qss/                 # Qt Style Sheets
│   │   │       ├── dark_theme.qss
│   │   │       └── light_theme.qss
│   │   └── __pycache__/
│   │
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py                # Logging configuration
│   │   ├── config_manager.py        # Configuration file management
│   │   ├── helpers.py               # General helper functions
│   │   ├── gpu_utils.py             # GPU detection and management
│   │   ├── file_utils.py            # File operations utilities
│   │   ├── validation.py            # Input validation
│   │   └── __pycache__/
│   │
│   ├── licensing/                    # License management (DTC)
│   │   ├── __init__.py
│   │   ├── license_manager.py       # License validation logic
│   │   ├── activation.py            # Online activation system
│   │   ├── hardware_fingerprint.py  # Device identification
│   │   └── __pycache__/
│   │
│   ├── analytics/                    # Usage analytics (opt-in)
│   │   ├── __init__.py
│   │   ├── telemetry.py             # Anonymous usage tracking
│   │   ├── crash_reporter.py        # Automated crash reporting
│   │   └── __pycache__/
│   │
│   ├── cli.py                        # Command-Line Interface entry point
│   ├── app.py                        # GUI application entry point
│   └── version.py                    # Version information
│
├── sdk/                              # B2B SDK components (for partners)
│   ├── README.md                    # SDK documentation
│   ├── python/
│   │   ├── __init__.py
│   │   ├── conversion_api.py        # High-level Python API
│   │   └── examples/
│   │       ├── basic_conversion.py
│   │       └── advanced_usage.py
│   ├── cpp/                         # C++ SDK (future)
│   │   ├── include/
│   │   └── src/
│   └── docs/
│       ├── integration_guide.md
│       ├── api_reference.md
│       └── performance_tuning.md
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── test_depth_estimation.py
│   ├── test_rendering.py
│   ├── test_video_processing.py
│   ├── test_ui.py                   # UI automation tests
│   ├── test_integration.py          # End-to-end tests
│   ├── test_performance.py          # Performance benchmarks
│   ├── fixtures/                    # Test data
│   │   ├── images/
│   │   │   ├── test_image_1080p.jpg
│   │   │   └── test_image_4k.jpg
│   │   ├── videos/
│   │   │   ├── test_video_1080p.mp4 (short clip)
│   │   │   └── test_video_4k.mp4 (short clip)
│   │   └── expected_outputs/
│   └── conftest.py                  # pytest configuration
│
├── docs/                             # Documentation
│   ├── index.md
│   ├── user_manual/
│   │   ├── installation.md
│   │   ├── getting_started.md
│   │   ├── understanding_3d.md
│   │   ├── parameter_reference.md
│   │   ├── best_practices.md
│   │   └── troubleshooting.md
│   ├── developer_guide/
│   │   ├── architecture_overview.md
│   │   ├── contributing.md
│   │   ├── code_style.md
│   │   └── testing_guide.md
│   ├── api/                         # API documentation (Sphinx)
│   │   ├── conf.py
│   │   ├── index.rst
│   │   └── modules/
│   └── images/                      # Documentation images
│
├── scripts/                          # Build and utility scripts
│   ├── install_dependencies.sh      # Install Python packages and FFmpeg
│   ├── install_dependencies.bat     # Windows version
│   ├── setup_dev_environment.sh     # Complete dev setup
│   ├── build_app.sh                 # Build standalone application
│   ├── build_app.bat                # Windows build script
│   ├── build_installer.sh           # Create installer (NSIS/DMG)
│   ├── run_tests.sh                 # Execute test suite
│   ├── run_benchmarks.sh            # Run performance benchmarks
│   ├── download_models.py           # Download AI models
│   ├── package_sdk.sh               # Package SDK for distribution
│   └── code_signing.sh              # Code signing for macOS/Windows
│
├── installers/                       # Installer configuration
│   ├── windows/
│   │   ├── installer.nsi            # NSIS installer script
│   │   ├── icon.ico
│   │   └── license.txt
│   ├── macos/
│   │   ├── create_dmg.sh
│   │   ├── dmg_background.png
│   │   └── Info.plist
│   └── linux/
│       └── create_appimage.sh
│
├── deployment/                       # Deployment configurations
│   ├── docker/
│   │   ├── Dockerfile               # For cloud/server deployment (API service)
│   │   └── docker-compose.yml
│   ├── ci_cd/
│   │   ├── .github/
│   │   │   └── workflows/
│   │   │       ├── build.yml
│   │   │       ├── test.yml
│   │   │       └── release.yml
│   │   └── gitlab-ci.yml
│   └── cloud/                       # Cloud deployment (future API service)
│       ├── aws/
│       └── gcp/
│
├── assets/                           # Marketing and media assets
│   ├── screenshots/
│   ├── demo_videos/
│   ├── comparison_videos/           # Before/after, vs competitors
│   └── promotional/
│
├── planning/                         # Project planning documents
│   ├── MASTER_DEVELOPMENT_PLAN.md
│   ├── BUSINESS_MODEL_AND_PARTNERSHIP_STRATEGY.md
│   ├── COMPETITIVE_ANALYSIS.md
│   ├── TECHNICAL_ARCHITECTURE.md
│   └── DEPLOYMENT_STRATEGY.md
│
└── .vscode/                          # VS Code workspace settings
    ├── settings.json
    ├── launch.json                  # Debug configurations
    └── tasks.json
```

---

## File Descriptions by Module

### Root Directory Files

#### `README.md`

```markdown
# 2D to 3D SBS Converter

Professional AI-powered 2D to 3D Side-by-Side video converter.

## Features

- AI depth estimation (MiDaS, Depth-Anything-V2)
- GPU-accelerated processing
- 4K/8K support
- Real-time preview
- Batch processing

## Quick Start

...

## Documentation

See docs/ folder or visit [website]
```

#### `LICENSE`

Software license file (MIT, Apache 2.0, or proprietary commercial license)

#### `requirements.txt`

```txt
# Core dependencies for production
torch>=2.0.0
torchvision>=0.15.0
opencv-python>=4.8.0
numpy>=1.24.0
PyQt6>=6.5.0
Pillow>=10.0.0
ffmpeg-python>=0.2.0
pyyaml>=6.0
tqdm>=4.65.0
requests>=2.31.0
```

#### `requirements-dev.txt`

```txt
# Development dependencies
-r requirements.txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-qt>=4.2.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
sphinx>=7.0.0
pre-commit>=3.3.0
```

#### `setup.py`

Python package setup configuration for pip installation and SDK distribution

#### `config.yaml`

```yaml
# Default application configuration
app:
  name: "2D to 3D Converter"
  version: "1.0.0"

depth_estimation:
  model: "midas_v3_dpt_large"
  device: "auto" # auto, cuda, cpu
  batch_size: 4

rendering:
  default_depth_intensity: 75
  default_ipd: 65 # mm
  default_convergence: 1.0

video:
  default_quality: "balanced" # fast, balanced, high
  temp_dir: "temp"

ui:
  theme: "dark" # dark, light, auto
  language: "en"
```

#### `.gitignore`

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
dist/
*.egg-info/
venv/
.env
*.log
temp/
.DS_Store
src/ai_core/models/*.pt
src/ai_core/models/*.pth
```

---

### Core Modules

### `src/ai_core/` - AI Depth Estimation

#### `depth_estimation.py`

**Purpose:** Main depth map generation logic  
**Key Classes/Functions:**

```python
class DepthEstimator:
    """Main class for depth estimation"""
    def __init__(self, model_type="midas", device="auto")
    def estimate_depth(self, image: np.ndarray) -> np.ndarray
    def batch_estimate(self, images: List[np.ndarray]) -> List[np.ndarray]
    def set_quality_preset(self, preset: str)

def load_model(model_name: str, device: str) -> nn.Module
def normalize_depth(depth_map: np.ndarray) -> np.ndarray
```

**Dependencies:**

- PyTorch (model inference)
- OpenCV (image handling)
- NumPy (array operations)

**Input:** RGB image (H×W×3)  
**Output:** Normalized depth map (H×W, values 0-1)

#### `model_loader.py`

**Purpose:** Load and manage AI models  
**Features:**

- Automatic model download if not present
- Model caching
- Multi-GPU support
- ONNX export capability

#### `preprocessing.py`

**Purpose:** Prepare images for depth estimation  
**Features:**

- Resize to model input size (384×384, 512×512, etc.)
- Normalization (ImageNet stats)
- Aspect ratio preservation
- Batch preparation

#### `postprocessing.py`

**Purpose:** Refine raw depth maps  
**Features:**

- Bilateral filtering (edge-preserving smoothing)
- Histogram equalization
- Edge refinement
- Depth range adjustment

#### `temporal_filter.py`

**Purpose:** Ensure consistency across video frames  
**Features:**

- Temporal smoothing (prevents flickering)
- Optical flow integration
- Scene change detection
- Adaptive filtering

---

### `src/rendering/` - Stereoscopic Rendering

#### `dibr_renderer.py`

**Purpose:** Depth Image-Based Rendering (DIBR) core algorithm  
**Key Functions:**

```python
class DIBRRenderer:
    def __init__(self, ipd=65, convergence=1.0)
    def render_stereo_pair(
        self,
        image: np.ndarray,
        depth: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]
    def compute_disparity(self, depth: np.ndarray) -> np.ndarray
    def shift_pixels(self, image: np.ndarray, disparity: np.ndarray) -> np.ndarray
```

**Algorithm:**

1. Convert depth to disparity (pixel shift amount)
2. Shift pixels left/right based on disparity
3. Identify holes (disocclusions)
4. Fill holes with inpainting

#### `stereoscopy.py`

**Purpose:** Manage stereoscopic parameters and view generation  
**Features:**

- Calculate IPD (Interpupillary Distance) effects
- Convergence plane adjustment
- Comfort zone validation
- Multi-layer rendering for complex scenes

#### `hole_filling.py`

**Purpose:** Fill disocclusions (holes) in rendered views  
**Algorithms:**

- Fast Marching Method inpainting
- Nearest neighbor filling
- Background propagation
- AI-based inpainting (future)

#### `sbs_composer.py`

**Purpose:** Combine left/right views into SBS format  
**Output Formats:**

- Half-SBS (1920×1080 → 1920×1080)
- Full-SBS (1920×1080 → 3840×1080)
- Top-Bottom (TB)
- Anaglyph (red-cyan)

---

### `src/video_processing/` - Video I/O

#### `ffmpeg_handler.py`

**Purpose:** Wrap FFmpeg for video operations  
**Key Functions:**

```python
class FFmpegHandler:
    def extract_video_info(self, video_path: str) -> dict
    def extract_frames(self, video_path: str) -> Generator
    def extract_audio(self, video_path: str, output: str)
    def encode_video(
        self,
        frames: Generator,
        output: str,
        fps: int,
        codec: str = "h264"
    )
    def merge_audio_video(self, video: str, audio: str, output: str)
```

**Supported Codecs:**

- H.264 (libx264) - most compatible
- H.265 (libx265) - better compression
- VP9 - open-source alternative

#### `frame_extractor.py`

**Purpose:** Efficient frame extraction and buffering  
**Features:**

- Generator-based streaming (memory efficient)
- Frame caching for preview
- Parallel frame extraction
- Frame range selection

#### `frame_manager.py`

**Purpose:** Manage frame queues and memory  
**Features:**

- Producer-consumer queue
- Memory monitoring and limits
- Adaptive batch sizing
- GPU memory management

#### `encoder.py`

**Purpose:** Video encoding with quality presets  
**Presets:**

- **Fast:** CRF 28, preset ultrafast
- **Balanced:** CRF 23, preset medium
- **High:** CRF 18, preset slow
- **Custom:** User-defined parameters

---

### `src/ui/` - User Interface (PyQt6)

#### `main_window.py`

**Purpose:** Main application window  
**Components:**

- Menu bar (File, Edit, View, Tools, Help)
- Toolbar with quick actions
- Central widget (file selection + preview)
- Settings panel (dockable)
- Status bar with progress

**Key Methods:**

```python
class MainWindow(QMainWindow):
    def __init__(self)
    def open_file(self)
    def start_conversion(self)
    def update_preview(self)
    def show_settings(self)
    def on_conversion_complete(self)
```

#### `preview_widget.py`

**Purpose:** Real-time preview of 3D effect  
**Features:**

- Side-by-side comparison (2D vs 3D)
- Anaglyph preview (red-cyan glasses)
- Frame selection slider
- Zoom and pan
- Depth map overlay toggle

#### `settings_panel.py`

**Purpose:** Parameter adjustment controls  
**Controls:**

- Depth intensity slider (0-100%)
- IPD slider (55-75mm)
- Convergence slider
- Quality preset dropdown
- Output format selection
- Advanced settings (collapsible)

#### `progress_dialog.py`

**Purpose:** Conversion progress UI  
**Features:**

- Progress bar with percentage
- Current frame / total frames
- Time elapsed / estimated remaining
- Pause/Resume/Cancel buttons
- Real-time preview of current frame

---

### `src/utils/` - Utilities

#### `logger.py`

**Purpose:** Centralized logging configuration  
**Features:**

- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- File and console output
- Rotation (max 10MB per file)
- User privacy (no sensitive data logged)

#### `config_manager.py`

**Purpose:** Manage application configuration  
**Features:**

- Load/save config.yaml
- User preferences (stored in ~/.config or AppData)
- Preset management
- Configuration validation

#### `gpu_utils.py`

**Purpose:** GPU detection and management  
**Features:**

```python
def detect_gpus() -> List[dict]
def get_best_gpu() -> str  # returns device ID
def get_gpu_memory_info(device: str) -> dict
def supports_cuda() -> bool
def supports_mps() -> bool  # Apple Silicon
def supports_rocm() -> bool  # AMD
```

---

### `src/licensing/` - License Management (DTC)

#### `license_manager.py`

**Purpose:** License validation and tier management  
**Features:**

- License key validation (online and offline)
- Tier enforcement (Free/Premium/Pro)
- Trial period management (14 days)
- Subscription expiry checking

#### `activation.py`

**Purpose:** Online license activation  
**Features:**

- Communicate with license server API
- Handle activation limits (2-3 devices)
- Deactivation capability
- Offline activation fallback

#### `hardware_fingerprint.py`

**Purpose:** Generate unique device ID  
**Method:**

- Hash of (CPU ID + MAC address + Disk serial)
- Privacy-preserving (one-way hash)
- Stable across reboots
- Different per OS reinstall (acceptable)

---

### `sdk/` - B2B SDK

#### `sdk/python/conversion_api.py`

**Purpose:** High-level API for hardware partners  
**Example Usage:**

```python
from conversion_api import Converter

# Initialize
converter = Converter(model="midas_v3", device="cuda:0")

# Convert single image
left, right = converter.convert_image(
    image_path="input.jpg",
    depth_intensity=75,
    ipd=65
)

# Convert video
converter.convert_video(
    input_path="movie.mp4",
    output_path="movie_sbs.mp4",
    format="half_sbs",
    quality="high"
)

# Real-time streaming
for frame in video_stream:
    left, right = converter.convert_frame(frame)
    display_stereo(left, right)
```

#### `sdk/docs/integration_guide.md`

**Content:**

- Step-by-step integration instructions
- Platform-specific considerations
- Performance optimization tips
- Code examples for common scenarios
- Troubleshooting guide

---

### `tests/` - Test Suite

#### `test_depth_estimation.py`

**Tests:**

- Model loading and inference
- Batch processing
- GPU acceleration
- Accuracy validation (using reference datasets)
- Performance benchmarks

#### `test_rendering.py`

**Tests:**

- DIBR algorithm correctness
- Hole filling quality
- SBS composition
- Parameter ranges

#### `test_video_processing.py`

**Tests:**

- Video parsing (various codecs)
- Frame extraction speed
- Audio preservation
- Encoding quality

#### `test_integration.py`

**Tests:**

- End-to-end conversion pipeline
- Memory usage under load
- Long video processing (>1 hour)
- Error handling and recovery

---

### `scripts/` - Build Scripts

#### `install_dependencies.sh`

**Purpose:** One-command setup for development  
**Actions:**

1. Check Python version (3.10+)
2. Create virtual environment
3. Install pip packages
4. Install FFmpeg (via apt/brew/choco)
5. Download AI models
6. Run post-install tests

#### `build_app.sh`

**Purpose:** Build standalone executable  
**Tool:** PyInstaller  
**Output:** Single-file or one-folder distribution  
**Process:**

1. Bundle Python runtime
2. Include all dependencies
3. Embed AI models (or download on first run)
4. Add FFmpeg binaries
5. Apply code obfuscation (optional)
6. Code signing (macOS/Windows)

#### `build_installer.sh`

**Purpose:** Create installer package  
**Windows:** NSIS installer (.exe)  
**macOS:** DMG with drag-to-Applications  
**Linux:** AppImage or .deb package

---

## Module Dependencies Graph

```
┌─────────────────────────────────────────────────────────────┐
│                         app.py (GUI)                         │
│                         cli.py (CLI)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│    UI    │  │  Utils   │  │  Licensing   │
│ (PyQt6)  │  │ (Config, │  │  (License    │
│          │  │  Logger) │  │   Manager)   │
└─────┬────┘  └────┬─────┘  └──────────────┘
      │            │
      └──────┬─────┘
             │
      ┌──────▼────────────────────────────┐
      │   Video Processing Module         │
      │   (FFmpeg, Frame Management)      │
      └──────┬────────────────────────────┘
             │
      ┌──────▼────────────────────────────┐
      │     AI Core Module                │
      │   (Depth Estimation, Models)      │
      └──────┬────────────────────────────┘
             │
      ┌──────▼────────────────────────────┐
      │   Rendering Module                │
      │   (DIBR, Stereoscopy, SBS)        │
      └───────────────────────────────────┘
```

---

## Data Flow Architecture

### Image Conversion Flow

```
Input Image
    │
    ▼
Preprocessing (resize, normalize)
    │
    ▼
Depth Estimation (AI model)
    │
    ▼
Depth Map Postprocessing
    │
    ▼
DIBR Rendering (left + right views)
    │
    ▼
Hole Filling
    │
    ▼
SBS Composition
    │
    ▼
Output SBS Image
```

### Video Conversion Flow

```
Input Video
    │
    ├──────► Extract Audio
    │
    ▼
Frame Extraction (FFmpeg)
    │
    ▼
Frame Queue (in-memory buffer)
    │
    ▼
Batch Processing (4-8 frames)
    │
    ├─► Depth Estimation (GPU)
    ├─► DIBR Rendering
    └─► SBS Composition
    │
    ▼
Encoded Video Frames
    │
    ▼
Video Encoding (FFmpeg, H.264)
    │
    ◄──────┘ Merge Audio
    │
    ▼
Output SBS Video
```

---

## Storage Requirements

### Development Environment

- Source Code: ~50 MB
- AI Models: ~1.5 GB (MiDaS + Depth-Anything-V2)
- Dependencies: ~3 GB (PyTorch, CUDA libraries)
- Test Fixtures: ~500 MB
- **Total: ~5 GB**

### Deployed Application

- Application Binary: ~150 MB (with PyTorch)
- AI Models: ~400 MB (optimized/quantized)
- FFmpeg: ~100 MB
- **Total Installation: ~650 MB**

### Runtime Storage (for users)

- Temp Files: ~2-5 GB per hour of 4K video processing
- Cache: ~100 MB
- Logs: ~10 MB

---

## Performance Targets

### Depth Estimation (on RTX 3080)

- 1080p single image: 100-200 ms
- 4K single image: 300-500 ms
- 1080p batch (8 frames): 400-600 ms

### Full Conversion (1080p → 1080p SBS)

- 1-minute video: 30-60 seconds (real-time to 2x)
- 90-minute movie: 45-90 minutes

### Memory Usage

- 1080p processing: 4-6 GB RAM, 4 GB VRAM
- 4K processing: 8-12 GB RAM, 8 GB VRAM

---

## Security Considerations

### Code Protection

- **PyInstaller:** Basic protection through bundling
- **PyArmor:** Advanced obfuscation (optional)
- **Code Signing:** Mandatory for macOS, recommended for Windows

### License Protection

- Online activation prevents basic piracy
- Hardware fingerprinting limits sharing
- Regular server checks for subscriptions
- Graceful degradation if offline

### User Privacy

- No telemetry without explicit opt-in
- Anonymous crash reports only
- No video content sent to servers
- Local processing only

---

## Scalability & Extensibility

### Adding New AI Models

1. Implement model loading in `model_loader.py`
2. Add preprocessing if needed
3. Update `DepthEstimator` class
4. Add to configuration options
5. Document in user manual

### Adding New Output Formats

1. Implement in `sbs_composer.py`
2. Add UI option in `settings_panel.py`
3. Update FFmpeg encoding parameters
4. Test compatibility

### Plugin System (Future)

- Define plugin interface
- Plugin directory: `~/.2d3d_converter/plugins/`
- Allow community-developed depth models, filters, etc.

---

## Continuous Integration

### Automated Tests (GitHub Actions)

**On Pull Request:**

- Linting (black, flake8)
- Type checking (mypy)
- Unit tests (pytest)
- Code coverage report

**On Push to Main:**

- All above tests
- Integration tests
- Build application packages
- Deploy to staging

**On Release Tag:**

- All above
- Build installers (Windows, macOS, Linux)
- Code signing
- Upload to release page
- Update documentation site

---

## Summary

This architecture provides:

- ✅ **Modularity:** Clear separation of concerns
- ✅ **Testability:** Comprehensive test coverage
- ✅ **Maintainability:** Well-documented, clean code
- ✅ **Scalability:** Easy to add features or models
- ✅ **SDK-Ready:** Core modules extractable for B2B
- ✅ **Professional:** Production-grade structure

The structure supports both immediate DTC launch and future B2B SDK distribution, with clear boundaries between core technology (AI/rendering) and application-specific code (UI/licensing).
