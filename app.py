#!/usr/bin/env python3
"""
2D to 3D Converter - Desktop Application

Main entry point for the PyQt6 desktop GUI application.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the desktop application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting 2D to 3D Converter GUI")
    
    try:
        # Qt6 has high DPI support enabled by default
        # Set the rounding policy BEFORE creating QApplication
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        app = QApplication(sys.argv)
        app.setApplicationName("2D to 3D Converter")
        app.setOrganizationName("3DConversion")
        app.setOrganizationDomain("3dconversion.app")
        
        # Check if models are downloaded
        _check_models_downloaded(app)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        logger.info("Main window displayed successfully")
        
        # Run event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


def _check_models_downloaded(app):
    """Check if AI models are downloaded and warn user if not."""
    from pathlib import Path
    from PyQt6.QtWidgets import QMessageBox
    
    cache_dir = Path.home() / ".cache" / "torch" / "hub" / "checkpoints"
    model_file = cache_dir / "dpt_large_384.pt"
    
    if not model_file.exists():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("First Time Setup")
        msg.setText("<h3>AI Models Need to be Downloaded</h3>")
        msg.setInformativeText(
            "<p>On first use, the app needs to download AI models (~1.3 GB).</p>"
            "<p><b>This may take 5-30 minutes</b> depending on your internet speed.</p>"
            "<br>"
            "<p><b>What happens next:</b></p>"
            "<ul>"
            "<li>When you click 'Convert', the download will start</li>"
            "<li>The app may appear frozen during download</li>"
            "<li>Check Terminal/Console for progress</li>"
            "<li>Future conversions will be instant (models are cached)</li>"
            "</ul>"
            "<br>"
            "<p><b>Tip:</b> Run <code>python3 download_models.py</code> in Terminal<br>"
            "to download models with progress bar before using the app.</p>"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()


if __name__ == "__main__":
    main()

