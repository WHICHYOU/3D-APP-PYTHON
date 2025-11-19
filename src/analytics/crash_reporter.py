"""
Crash Reporter
Capture and report application crashes
"""
import sys
import traceback
import platform
from datetime import datetime
from typing import Optional, Dict


class CrashReporter:
    """Report application crashes"""
    
    def __init__(
        self,
        enabled: bool = True,
        server_url: Optional[str] = None
    ):
        """
        Initialize crash reporter
        
        Args:
            enabled: Whether crash reporting is enabled
            server_url: Crash reporting server URL
        """
        self.enabled = enabled
        self.server_url = server_url or 'https://crashes.converter3d.com/v1'
    
    def report_crash(
        self,
        exception: Exception,
        context: Optional[Dict] = None
    ):
        """
        Report a crash
        
        Args:
            exception: The exception that caused the crash
            context: Additional context about the crash
        """
        if not self.enabled:
            return
        
        # Collect crash information
        crash_info = {
            'timestamp': datetime.now().isoformat(),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback.format_exc(),
            'system_info': self._get_system_info(),
            'context': context or {},
        }
        
        # Try to send crash report
        try:
            self._send_crash_report(crash_info)
        except:
            # Don't let crash reporting crash the app
            pass
        
        # Also save locally
        self._save_crash_log(crash_info)
    
    def _get_system_info(self) -> Dict:
        """
        Get system information
        
        Returns:
            Dictionary of system info
        """
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
        }
    
    def _send_crash_report(self, crash_info: Dict):
        """
        Send crash report to server
        
        Args:
            crash_info: Crash information dictionary
        """
        # TODO: Send to crash reporting server
        print(f"Would send crash report to {self.server_url}")
        print(f"Exception: {crash_info['exception_type']}: {crash_info['exception_message']}")
    
    def _save_crash_log(self, crash_info: Dict):
        """
        Save crash log locally
        
        Args:
            crash_info: Crash information dictionary
        """
        try:
            import os
            log_dir = os.path.expanduser('~/.converter3d/crash_logs')
            os.makedirs(log_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = os.path.join(log_dir, f'crash_{timestamp}.log')
            
            with open(log_file, 'w') as f:
                f.write(f"Crash Report - {crash_info['timestamp']}\n")
                f.write(f"{'=' * 60}\n\n")
                f.write(f"Exception: {crash_info['exception_type']}\n")
                f.write(f"Message: {crash_info['exception_message']}\n\n")
                f.write(f"Traceback:\n{crash_info['traceback']}\n\n")
                f.write(f"System Info:\n")
                for key, value in crash_info['system_info'].items():
                    f.write(f"  {key}: {value}\n")
                
                if crash_info['context']:
                    f.write(f"\nContext:\n")
                    for key, value in crash_info['context'].items():
                        f.write(f"  {key}: {value}\n")
        
        except Exception as e:
            print(f"Failed to save crash log: {e}")
    
    def install_exception_handler(self):
        """Install global exception handler"""
        def exception_handler(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions"""
            # Don't report KeyboardInterrupt
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # Report the crash
            self.report_crash(exc_value)
            
            # Call default handler
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = exception_handler
