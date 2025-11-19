"""
Main GUI Application Entry Point
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Main entry point for GUI application"""
    from src.version import check_requirements
    
    # Check system requirements
    try:
        check_requirements()
    except RuntimeError as e:
        print(f"System requirement error: {e}")
        sys.exit(1)
    
    # Import Qt after requirements check
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    
    # Import main window (will be implemented)
    from src.ui.main_window import MainWindow
    from src.utils.logger import setup_logger
    from src.utils.config_manager import ConfigManager
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting 2D to 3D Converter...")
    
    # Load configuration
    config = ConfigManager()
    
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("2D to 3D Converter")
    app.setOrganizationName("2D3D Converter Inc.")
    
    # Create and show main window
    window = MainWindow(config)
    window.show()
    
    # Run application
    logger.info("Application started successfully")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
