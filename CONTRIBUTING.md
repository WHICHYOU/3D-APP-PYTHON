# Contributing to 2D to 3D Converter

Thank you for your interest in contributing! This document provides guidelines for in-house developers working on this project.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Platform-specific requirements:
  - **macOS**: Xcode Command Line Tools (`xcode-select --install`)
  - **Windows**: Microsoft Visual C++ Redistributable
  - **Linux**: build-essential

### Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/WHICHYOU/3D-APP-PYTHON.git
   cd 3D-APP-PYTHON
   ```

2. **Create virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   # Core dependencies
   pip install -r requirements.txt

   # Platform-specific (choose one)
   pip install -r requirements-macos.txt    # macOS Apple Silicon
   pip install -r requirements-windows.txt  # Windows with CUDA

   # Development tools
   pip install -r requirements-dev.txt

   # GUI dependencies (if working on UI)
   pip install -r requirements-gui.txt
   ```

4. **Copy environment file**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Verify installation**
   ```bash
   python tests/manual/test_model_selection.py
   python -c "import torch; print(f'PyTorch: {torch.__version__}')"
   ```

## 📁 Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed directory layout.

Key directories:

- `src/ai_core/` - Depth estimation AI models
- `src/rendering/` - Stereoscopic rendering engine
- `src/ui/` - PyQt6 desktop interface
- `src/video_processing/` - Video handling and FFmpeg
- `src/utils/` - Common utilities
- `tests/` - Test suite

## 🔧 Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features (e.g., `feature/new-model-support`)
- `bugfix/*` - Bug fixes (e.g., `bugfix/depth-map-artifacts`)
- `hotfix/*` - Critical production fixes

### Creating a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Commit Messages

Follow conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring
- `perf`: Performance improvements
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(ai_core): add MiDaS Swin2-Tiny model support
fix(rendering): resolve hole-filling artifacts in high-motion scenes
docs(README): update installation instructions for Ubuntu 22.04
perf(video): optimize batch processing with parallel frame extraction
```

### Code Style

- **PEP 8** for Python code
- **Type hints** for function signatures
- **Docstrings** for all public functions/classes (Google style)
- **Max line length**: 100 characters
- **Format with**: `black` (auto-formatter)
- **Lint with**: `flake8`, `pylint`

**Example:**

```python
def estimate_depth(
    self,
    image: np.ndarray,
    normalize: bool = True
) -> np.ndarray:
    """
    Estimate depth map for a single image.

    Args:
        image: Input RGB image (H, W, 3)
        normalize: Whether to normalize output to [0, 1]

    Returns:
        Depth map (H, W) with values in [0, 1] if normalized

    Raises:
        RuntimeError: If model is not loaded
        ValueError: If image dimensions are invalid
    """
    # Implementation
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ai_core/test_depth_estimation.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests (fast)
pytest -m unit

# Run integration tests
pytest -m integration
```

### Writing Tests

- Place tests in `tests/` directory mirroring `src/` structure
- Use descriptive test names: `test_depth_estimation_handles_grayscale_images()`
- Include docstrings explaining what's being tested
- Mock external dependencies (models, network calls)
- Test edge cases and error conditions

**Example:**

```python
def test_depth_estimator_with_invalid_model():
    """Test that DepthEstimator raises error for unknown model."""
    with pytest.raises(ValueError, match="Unknown model type"):
        estimator = DepthEstimator(model_type="invalid_model")
```

## 🎨 UI Development

### Working on PyQt6 Interface

1. UI files are in `src/ui/`
2. Test UI changes:
   ```bash
   python src/app.py
   ```
3. Follow PyQt6 best practices:
   - Separate UI logic from business logic
   - Use signals/slots for communication
   - Keep UI responsive with QThread for long operations
   - Test on multiple screen resolutions

### UI Testing Checklist

- [ ] Works on macOS
- [ ] Works on Windows
- [ ] Works on Linux (if applicable)
- [ ] Responsive to window resizing
- [ ] Dark/light theme compatible
- [ ] Keyboard shortcuts functional
- [ ] Accessible (screen reader compatible)

## 🤖 AI Model Development

### Adding New Models

1. Update `MODEL_REGISTRY` in `src/ai_core/depth_estimation.py`
2. Add model metadata (speed, quality, VRAM, etc.)
3. Implement loading logic in `_load_model()`
4. Add appropriate transform
5. Update documentation
6. Test on all platforms
7. Benchmark performance

### Model Testing

```bash
python test_depth.py --model your_new_model --image test_images/sample.jpg
```

## 📊 Performance Guidelines

- **Video processing**: Aim for >10 FPS on mid-range GPUs
- **Memory usage**: Keep under 4GB VRAM for default models
- **Startup time**: < 5 seconds on SSD
- **Model loading**: Show progress for downloads >100MB

### Profiling

```bash
# Profile CPU usage
python -m cProfile -o profile.stats src/app.py

# Profile memory
python -m memory_profiler src/video_processing/batch_processor.py

# Profile GPU
# Use nvidia-smi or Activity Monitor (macOS)
```

## 🐛 Debugging

### Enable Debug Mode

Edit `.env`:

```
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

### Common Issues

1. **Model download fails**: Check internet connection, try manual download
2. **CUDA out of memory**: Reduce batch size in `config.yaml`
3. **FFmpeg not found**: Install via package manager or use bundled version
4. **Qt rendering issues**: Update graphics drivers

### Log Locations

- **macOS**: `~/Library/Logs/2D-to-3D-Converter/`
- **Windows**: `%APPDATA%\2D-to-3D-Converter\logs\`
- **Linux**: `~/.local/share/2D-to-3D-Converter/logs/`

## 📦 Building

### Build Desktop App

**macOS:**

```bash
./build_config/build_macos.sh
```

**Windows:**

```batch
python build_scripts/build_windows.py
```

### Testing Builds

1. Test on clean system (VM recommended)
2. Verify all dependencies bundled
3. Check file size (should be <500MB without models)
4. Test first-run experience
5. Verify model auto-download

## 🔒 Security Guidelines

### Important Rules

1. **Never commit secrets** - Use `.env` for sensitive data
2. **Never commit API keys** - Use environment variables
3. **Validate all inputs** - Especially file paths and user data
4. **Sanitize file names** - Prevent path traversal attacks
5. **Review dependencies** - Check for known vulnerabilities

### Secret Management

- Use `.env` file (git-ignored)
- For production: Use proper secret management (Azure Key Vault, AWS Secrets Manager)
- Rotate API keys regularly
- Use different keys for dev/staging/prod

### Code Review Checklist

- [ ] No hardcoded secrets or keys
- [ ] Input validation present
- [ ] Error handling doesn't leak sensitive info
- [ ] Dependencies up to date
- [ ] No SQL injection vectors (if using DB)
- [ ] File operations are safe

## 📝 Documentation

### What to Document

- **New features**: Update README.md and relevant guides
- **API changes**: Update docstrings and API documentation
- **Breaking changes**: Add to CHANGELOG.md with migration guide
- **Configuration**: Update config examples and .env.example

### Documentation Standards

- Use markdown for all docs
- Include code examples
- Add screenshots for UI features
- Keep language clear and concise
- Update table of contents

## 🚢 Release Process

### Version Numbers

Follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Release Checklist

1. [ ] Update version in `src/version.py`
2. [ ] Update CHANGELOG.md
3. [ ] Run full test suite
4. [ ] Build for all platforms
5. [ ] Test built applications
6. [ ] Create git tag: `git tag -a v1.2.3 -m "Release 1.2.3"`
7. [ ] Push tag: `git push origin v1.2.3`
8. [ ] Create GitHub release with binaries
9. [ ] Update documentation site
10. [ ] Announce in team channels

## 🤝 Code Review

### As a Reviewer

- Be constructive and respectful
- Explain _why_ changes are needed
- Suggest alternatives when possible
- Approve if minor issues can be addressed in follow-up
- Test the changes locally if possible

### As an Author

- Keep PRs focused and small
- Provide context in PR description
- Respond to feedback promptly
- Don't take criticism personally
- Update PR based on feedback

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass and coverage maintained
- [ ] Documentation updated
- [ ] No security issues
- [ ] Performance acceptable
- [ ] Works on target platforms

## 🆘 Getting Help

### Communication Channels

- **Slack**: #3d-converter-dev (for daily discussions)
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and ideas
- **Team Meetings**: Weekly sync on Mondays 10 AM

### Resources

- [Project Documentation](docs/README.md)
- [API Reference](docs/api/README.md)
- [User Guide](docs/user-guides/GUI_USER_GUIDE.md)
- [Architecture Overview](planning/TECHNICAL_ARCHITECTURE.md)

## 📜 License

This project is proprietary software. All rights reserved by WHICHYOU.
See LICENSE file for details.

---

**Questions?** Contact the maintainers or ask in #3d-converter-dev

**Found a bug?** Create an issue with detailed reproduction steps

**Have an idea?** Start a discussion on GitHub Discussions
