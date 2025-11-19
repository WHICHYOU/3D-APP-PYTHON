"""
Hardware Fingerprinting
Generate unique hardware identifier
"""
import hashlib
import platform
import uuid
from typing import Optional


class HardwareFingerprint:
    """Generate hardware fingerprint for license binding"""
    
    @staticmethod
    def generate() -> str:
        """
        Generate hardware fingerprint
        
        Returns:
            Hardware fingerprint string
        """
        # Collect hardware identifiers
        components = []
        
        # MAC address
        try:
            mac = uuid.getnode()
            components.append(str(mac))
        except:
            pass
        
        # Machine UUID (platform-specific)
        try:
            machine_id = uuid.uuid1().hex
            components.append(machine_id)
        except:
            pass
        
        # Platform info
        components.append(platform.system())
        components.append(platform.machine())
        
        # Hostname
        try:
            hostname = platform.node()
            components.append(hostname)
        except:
            pass
        
        # Combine and hash
        combined = '|'.join(components)
        fingerprint = hashlib.sha256(combined.encode()).hexdigest()
        
        return fingerprint
    
    @staticmethod
    def format_fingerprint(fingerprint: str) -> str:
        """
        Format fingerprint for display
        
        Args:
            fingerprint: Raw fingerprint
        
        Returns:
            Formatted fingerprint (e.g., XXXX-XXXX-XXXX-XXXX)
        """
        # Take first 16 characters and format
        short = fingerprint[:16].upper()
        return '-'.join([short[i:i+4] for i in range(0, 16, 4)])
    
    @staticmethod
    def verify(fingerprint: str, stored_fingerprint: str) -> bool:
        """
        Verify fingerprint matches stored value
        
        Args:
            fingerprint: Current fingerprint
            stored_fingerprint: Stored fingerprint
        
        Returns:
            True if match
        """
        return fingerprint == stored_fingerprint
