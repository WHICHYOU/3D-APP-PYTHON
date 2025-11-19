# Test Suite

This directory contains all tests for the 3D conversion application.

## Structure

- `test_ai_core/` - Tests for AI depth estimation
- `test_rendering/` - Tests for rendering and stereoscopy
- `test_video_processing/` - Tests for video processing
- `test_utils/` - Tests for utilities
- `conftest.py` - PyTest configuration and fixtures

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_ai_core/test_depth_estimation.py
```
