# Development Environment Setup

Quick guide for in-house developers to set up their development environment.

## Prerequisites Checklist

- [ ] Python 3.10 or higher installed
- [ ] Git installed and configured
- [ ] GitHub access configured (SSH keys or token)
- [ ] Code editor (VS Code, PyCharm recommended)
- [ ] Platform-specific tools installed

### Platform-Specific Requirements

**macOS:**

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (if not already)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.10+
brew install python@3.10
```

**Windows:**

- Install Python from python.org (3.10+)
- Install Microsoft Visual C++ Redistributable
- Install Git for Windows
- (Optional) Install NVIDIA CUDA Toolkit if you have NVIDIA GPU

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip git build-essential
```

## Initial Setup (First Time)

### 1. Clone Repository

```bash
# Clone the repo
git clone https://github.com/WHICHYOU/3D-APP-PYTHON.git
cd 3D-APP-PYTHON

# Set up Git user info (if not done globally)
git config user.name "Your Name"
git config user.email "your.email@company.com"
```

### 2. Create Virtual Environment

```bash
# Create venv
python3 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Verify activation (should show path to .venv)
which python  # macOS/Linux
where python  # Windows
```

### 3. Install Dependencies

```bash
# Install core dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install platform-specific packages
# macOS (Apple Silicon):
pip install -r requirements-macos.txt

# Windows (with CUDA):
pip install -r requirements-windows.txt

# Install development tools
pip install -r requirements-dev.txt

# Install GUI dependencies (if working on UI)
pip install -r requirements-gui.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# Set DEBUG_MODE=true for development
```

**Recommended .env for development:**

```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
ENABLE_ANALYTICS=false
FORCE_CPU=false  # Set to true if no GPU
GPU_DEVICE=0
```

### 5. Verify Installation

```bash
# Test Python and imports
python -c "import torch; import cv2; import numpy; print('✓ Core dependencies OK')"

# Test PyQt6 (if working on UI)
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 OK')"

# Run model selection test
python test_model_selection.py

# Check PyTorch device
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'MPS: {torch.backends.mps.is_available() if hasattr(torch.backends, \"mps\") else False}')"
```

## IDE Setup

### VS Code (Recommended)

1. **Install VS Code**: Download from code.visualstudio.com

2. **Install Extensions:**

   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)
   - Python Debugger (ms-python.debugpy)
   - GitLens (eamodio.gitlens)
   - Markdown All in One (yzhang.markdown-all-in-one)

3. **Configure workspace:**

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".venv": true,
    "build": true,
    "dist": true
  }
}
```

4. **Configure debugging:**

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run GUI App",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/app.py",
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Run Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

### PyCharm

1. **Open Project**: File → Open → Select project folder
2. **Configure Interpreter**:
   - Settings → Project → Python Interpreter
   - Click gear icon → Add → Existing environment
   - Select `.venv/bin/python`
3. **Enable pytest**:
   - Settings → Tools → Python Integrated Tools
   - Default test runner: pytest
4. **Configure Code Style**:
   - Settings → Editor → Code Style → Python
   - Set line length: 100
   - Enable "Black" formatter plugin

## Development Tools

### Install Development Tools

```bash
# Code formatting
pip install black

# Linting
pip install flake8 pylint

# Type checking
pip install mypy

# Testing
pip install pytest pytest-cov pytest-mock

# Documentation
pip install sphinx sphinx-rtd-theme
```

### Pre-commit Hooks (Optional but Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks (creates .pre-commit-config.yaml if needed)
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

## Daily Workflow

### Starting Work

```bash
# Navigate to project
cd 3D-APP-PYTHON

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Update from remote
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### During Development

```bash
# Run app to test changes
python src/app.py

# Run specific tests
pytest tests/test_ai_core/test_depth_estimation.py -v

# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/
```

### Committing Changes

```bash
# Check status
git status

# Add files
git add src/ai_core/depth_estimation.py

# Commit with conventional message
git commit -m "feat(ai_core): add new model support"

# Push to remote
git push origin feature/your-feature-name
```

## Common Tasks

### Running the Application

```bash
# GUI application
python src/app.py

# CLI (convert image)
python convert_image.py input.jpg output_sbs.jpg

# CLI (convert video)
python convert_video.py input.mp4 output_3d.mp4
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_ai_core/test_depth_estimation.py

# With coverage
pytest --cov=src --cov-report=html
# Open htmlcov/index.html to view coverage report

# Verbose output
pytest -v -s
```

### Building the Application

```bash
# macOS
./build_config/build_macos.sh

# Windows
python build_scripts/build_windows.py

# Check build output
ls -lh dist/
```

### Updating Dependencies

```bash
# Update a specific package
pip install --upgrade package-name

# Update all packages (careful!)
pip list --outdated
pip install --upgrade package-name

# Freeze current state
pip freeze > requirements.txt
```

## Troubleshooting

### Virtual Environment Issues

**Problem**: `python` still points to system Python

**Solution**:

```bash
deactivate  # If already activated
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
which python  # Should show .venv path
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'torch'`

**Solution**:

```bash
# Ensure venv is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### CUDA/GPU Issues

**Problem**: PyTorch not detecting GPU

**Solution**:

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Check MPS (macOS)
python -c "import torch; print(torch.backends.mps.is_available())"

# Install correct PyTorch version
# See: https://pytorch.org/get-started/locally/
```

### PyQt6 Issues

**Problem**: Qt platform plugin errors

**Solution**:

```bash
# Reinstall PyQt6
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
pip install --no-cache-dir PyQt6

# macOS: Reset Qt cache
rm -rf ~/Library/Caches/QtProject
```

### Model Download Fails

**Problem**: Model download times out or fails

**Solution**:

```bash
# Download manually
python download_models.py

# Or use specific model
python download_models.py --model midas_hybrid

# Check internet connection
curl -I https://github.com
```

## Getting Help

### Documentation

- **README.md** - Project overview and quick start
- **CONTRIBUTING.md** - Full contribution guidelines
- **PROJECT_STRUCTURE.md** - Code organization
- **GUI_USER_GUIDE.md** - User interface guide

### Team Communication

- **Slack**: #3d-converter-dev
- **GitHub Issues**: Bug reports and features
- **GitHub Discussions**: Questions and ideas

### Useful Commands

```bash
# Show Python version
python --version

# Show installed packages
pip list

# Show package info
pip show torch

# Find a file
find . -name "depth_estimation.py"

# Search for text in files
grep -r "DepthEstimator" src/

# Count lines of code
find src -name "*.py" | xargs wc -l
```

## Quick Reference

| Task          | Command                                |
| ------------- | -------------------------------------- |
| Activate venv | `source .venv/bin/activate`            |
| Run app       | `python src/app.py`                    |
| Run tests     | `pytest`                               |
| Format code   | `black src/`                           |
| Check style   | `flake8 src/`                          |
| Update deps   | `pip install -r requirements.txt`      |
| Build app     | `./build_config/build_macos.sh`        |
| Git status    | `git status`                           |
| Create branch | `git checkout -b feature/name`         |
| Commit        | `git commit -m "type(scope): message"` |

## Next Steps

1. ✅ Complete this setup
2. ✅ Read [CONTRIBUTING.md](CONTRIBUTING.md)
3. ✅ Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
4. ✅ Pick an issue from GitHub Issues
5. ✅ Create a feature branch
6. ✅ Make your first commit!

---

**Need help?** Contact the team lead or ask in #3d-converter-dev Slack channel.
