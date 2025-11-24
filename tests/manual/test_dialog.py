#!/usr/bin/env python3
"""Test if ProgressDialog opens correctly"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from src.ui.progress_dialog import ProgressDialog

app = QApplication(sys.argv)

# Test with a dummy file
test_file = Path(__file__).parent / "tests" / "test_images" / "test_image.jpg"
if test_file.exists():
    files = [str(test_file)]
else:
    files = ["/tmp/dummy.jpg"]

settings = {
    'depth_intensity': 75,
    'ipd': 6.5,
    'output_format': 'half_sbs',
    'quality': 'high',
    'hole_filling': True
}

print(f"Opening ProgressDialog with {len(files)} file(s)...")
dialog = ProgressDialog(files, settings)
print("Dialog created successfully!")
dialog.show()
print("Dialog shown!")

sys.exit(app.exec())
