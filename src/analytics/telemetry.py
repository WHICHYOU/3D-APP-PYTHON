"""
Telemetry Collection
Collect usage statistics (with user consent)
"""
import json
import time
from datetime import datetime
from typing import Dict, Optional
import platform


class TelemetryCollector:
    """Collect anonymous usage telemetry"""
    
    def __init__(
        self,
        enabled: bool = False,
        server_url: Optional[str] = None
    ):
        """
        Initialize telemetry collector
        
        Args:
            enabled: Whether telemetry is enabled
            server_url: Telemetry server URL
        """
        self.enabled = enabled
        self.server_url = server_url or 'https://telemetry.converter3d.com/v1'
        self.session_start = time.time()
        self.events = []
    
    def track_event(
        self,
        event_name: str,
        properties: Optional[Dict] = None
    ):
        """
        Track an event
        
        Args:
            event_name: Name of the event
            properties: Event properties
        """
        if not self.enabled:
            return
        
        event = {
            'name': event_name,
            'timestamp': datetime.now().isoformat(),
            'properties': properties or {},
            'session_duration': time.time() - self.session_start,
        }
        
        self.events.append(event)
        
        # Send if batch is large enough
        if len(self.events) >= 10:
            self.flush()
    
    def track_conversion(
        self,
        input_type: str,
        resolution: tuple,
        duration: float,
        success: bool,
        processing_time: float
    ):
        """
        Track a conversion operation
        
        Args:
            input_type: Type of input ('image' or 'video')
            resolution: (width, height)
            duration: Duration in seconds (for video)
            success: Whether conversion succeeded
            processing_time: Time taken in seconds
        """
        properties = {
            'input_type': input_type,
            'width': resolution[0],
            'height': resolution[1],
            'duration': duration,
            'success': success,
            'processing_time': processing_time,
        }
        
        self.track_event('conversion', properties)
    
    def track_feature_usage(
        self,
        feature_name: str,
        parameters: Optional[Dict] = None
    ):
        """
        Track feature usage
        
        Args:
            feature_name: Name of the feature
            parameters: Feature parameters
        """
        properties = {
            'feature': feature_name,
            'parameters': parameters or {},
        }
        
        self.track_event('feature_usage', properties)
    
    def track_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict] = None
    ):
        """
        Track an error
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
        """
        properties = {
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {},
        }
        
        self.track_event('error', properties)
    
    def get_system_info(self) -> Dict:
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
        }
    
    def flush(self):
        """Send queued events to server"""
        if not self.enabled or not self.events:
            return
        
        try:
            # TODO: Send events to server
            payload = {
                'events': self.events,
                'system_info': self.get_system_info(),
            }
            
            print(f"Would send {len(self.events)} events to telemetry server")
            
            # Clear events
            self.events = []
        
        except Exception as e:
            print(f"Failed to send telemetry: {e}")
    
    def set_enabled(self, enabled: bool):
        """
        Enable or disable telemetry
        
        Args:
            enabled: Whether to enable telemetry
        """
        self.enabled = enabled
        
        if not enabled:
            # Clear any queued events
            self.events = []
