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
        # Enable High DPI scaling BEFORE creating QApplication
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # Use the PassThrough policy for high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        app = QApplication(sys.argv)
        app.setApplicationName("2D to 3D Converter")
        app.setOrganizationName("3DConversion")
        app.setOrganizationDomain("3dconversion.app")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        logger.info("Main window displayed successfully")
        
        # Run event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
