"""
Logging Configuration
Centralized logging setup
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = 'converter_3d',
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up application logger
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        console: Whether to log to console
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = 'converter_3d') -> logging.Logger:
    """
    Get existing logger instance
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class PerformanceLogger:
    """Log performance metrics"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize performance logger
        
        Args:
            logger: Logger instance to use
        """
        self.logger = logger or get_logger()
        self.metrics = {}
    
    def log_metric(self, name: str, value: float, unit: str = ''):
        """
        Log a performance metric
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
        """
        self.metrics[name] = {'value': value, 'unit': unit}
        self.logger.info(f"{name}: {value:.2f} {unit}")
    
    def log_summary(self):
        """Log summary of all metrics"""
        self.logger.info("Performance Summary:")
        for name, data in self.metrics.items():
            self.logger.info(f"  {name}: {data['value']:.2f} {data['unit']}")
