#!/bin/bash
# Quick setup and test script

echo "=================================="
echo "2D to 3D Converter - Quick Setup"
echo "=================================="

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install opencv-python numpy pillow pyyaml tqdm

echo ""
echo "=================================="
echo "Installation complete!"
echo "=================================="

# Check GPU
echo ""
echo "Checking GPU availability..."
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"

# Run test
echo ""
echo "=================================="
echo "Running test conversion..."
echo "=================================="
echo ""
python3 test_depth.py

echo ""
echo "=================================="
echo "Setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Check test_output/ for results"
echo "  2. Try with your own image:"
echo "     python convert_image.py your_image.jpg output_3d.jpg"
echo ""
