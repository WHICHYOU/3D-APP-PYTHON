"""
General Helper Functions
Miscellaneous utility functions
"""
import time
from functools import wraps
from typing import Callable, Any


def timeit(func: Callable) -> Callable:
    """
    Decorator to measure function execution time
    
    Args:
        func: Function to measure
    
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        
        elapsed = end - start
        print(f"{func.__name__} took {elapsed:.2f} seconds")
        
        return result
    
    return wrapper


def format_time(seconds: float) -> str:
    """
    Format time duration in human-readable format
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "2h 34m 56s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    
    if minutes < 60:
        return f"{minutes}m {secs}s"
    
    hours = minutes // 60
    mins = minutes % 60
    
    return f"{hours}h {mins}m {secs}s"


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between min and max
    
    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value
    
    Returns:
        Clamped value
    """
    return max(min_value, min(max_value, value))


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between a and b
    
    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0-1)
    
    Returns:
        Interpolated value
    """
    return a + (b - a) * t


def progress_bar(
    current: int,
    total: int,
    prefix: str = '',
    suffix: str = '',
    length: int = 50
) -> str:
    """
    Create a text progress bar
    
    Args:
        current: Current progress
        total: Total items
        prefix: Prefix text
        suffix: Suffix text
        length: Bar length in characters
    
    Returns:
        Progress bar string
    """
    if total == 0:
        percent = 100
    else:
        percent = int(100 * current / total)
    
    filled = int(length * current / total) if total > 0 else 0
    bar = '█' * filled + '░' * (length - filled)
    
    return f'{prefix} |{bar}| {percent}% {suffix}'


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, name: str = "Operation"):
        """
        Initialize timer
        
        Args:
            name: Name of the operation
        """
        self.name = name
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        """Start timer"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        """Stop timer and print elapsed time"""
        self.elapsed = time.time() - self.start_time
        print(f"{self.name} completed in {format_time(self.elapsed)}")


def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(delay)
        
        return wrapper
    
    return decorator


def truncate_string(text: str, max_length: int = 50, suffix: str = '...') -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
