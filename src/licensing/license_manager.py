"""
License Manager
Handle license validation and tiers
"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from enum import Enum


class LicenseTier(Enum):
    """License tier enumeration"""
    FREE = 'free'
    BASIC = 'basic'
    PRO = 'pro'
    ENTERPRISE = 'enterprise'


class LicenseManager:
    """Manage application licensing"""
    
    # Feature limits by tier
    TIER_LIMITS = {
        LicenseTier.FREE: {
            'max_resolution': (1280, 720),
            'max_duration': 60,  # seconds
            'watermark': True,
            'batch_processing': False,
            'advanced_features': False,
        },
        LicenseTier.BASIC: {
            'max_resolution': (1920, 1080),
            'max_duration': 600,  # 10 minutes
            'watermark': False,
            'batch_processing': True,
            'advanced_features': False,
        },
        LicenseTier.PRO: {
            'max_resolution': (3840, 2160),  # 4K
            'max_duration': None,  # unlimited
            'watermark': False,
            'batch_processing': True,
            'advanced_features': True,
        },
        LicenseTier.ENTERPRISE: {
            'max_resolution': (7680, 4320),  # 8K
            'max_duration': None,
            'watermark': False,
            'batch_processing': True,
            'advanced_features': True,
            'api_access': True,
        },
    }
    
    def __init__(self, license_file: str = 'license.json'):
        """
        Initialize license manager
        
        Args:
            license_file: Path to license file
        """
        self.license_file = license_file
        self.license_data = None
        self.current_tier = LicenseTier.FREE
        
        self.load_license()
    
    def load_license(self) -> bool:
        """
        Load license from file
        
        Returns:
            True if license loaded successfully
        """
        if not os.path.exists(self.license_file):
            # No license file, default to free tier
            self.current_tier = LicenseTier.FREE
            return False
        
        try:
            with open(self.license_file, 'r') as f:
                self.license_data = json.load(f)
            
            # Validate license
            if self.validate_license():
                tier_str = self.license_data.get('tier', 'free')
                self.current_tier = LicenseTier(tier_str)
                return True
            else:
                self.current_tier = LicenseTier.FREE
                return False
        
        except Exception as e:
            print(f"Error loading license: {e}")
            self.current_tier = LicenseTier.FREE
            return False
    
    def validate_license(self) -> bool:
        """
        Validate current license
        
        Returns:
            True if license is valid
        """
        if not self.license_data:
            return False
        
        # Check expiration date
        expiry = self.license_data.get('expiry')
        if expiry:
            expiry_date = datetime.fromisoformat(expiry)
            if datetime.now() > expiry_date:
                print("License has expired")
                return False
        
        # Check license key format
        license_key = self.license_data.get('key')
        if not license_key or len(license_key) < 20:
            print("Invalid license key")
            return False
        
        # TODO: Verify license key with server
        # For now, just basic validation
        
        return True
    
    def activate_license(self, license_key: str, email: str) -> bool:
        """
        Activate license with key
        
        Args:
            license_key: License key
            email: User email
        
        Returns:
            True if activation successful
        """
        # TODO: Contact license server for activation
        print(f"Activating license for {email}")
        
        # Mock activation
        self.license_data = {
            'key': license_key,
            'email': email,
            'tier': 'pro',
            'activated': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(days=365)).isoformat(),
        }
        
        # Save license
        with open(self.license_file, 'w') as f:
            json.dump(self.license_data, f, indent=2)
        
        self.current_tier = LicenseTier.PRO
        
        return True
    
    def get_tier(self) -> LicenseTier:
        """
        Get current license tier
        
        Returns:
            Current license tier
        """
        return self.current_tier
    
    def get_limits(self) -> Dict:
        """
        Get feature limits for current tier
        
        Returns:
            Dictionary of limits
        """
        return self.TIER_LIMITS.get(self.current_tier, self.TIER_LIMITS[LicenseTier.FREE])
    
    def can_process_video(self, width: int, height: int, duration: float) -> tuple:
        """
        Check if video can be processed with current license
        
        Args:
            width: Video width
            height: Video height
            duration: Video duration in seconds
        
        Returns:
            Tuple of (can_process, reason)
        """
        limits = self.get_limits()
        
        max_width, max_height = limits['max_resolution']
        if width > max_width or height > max_height:
            return False, f"Resolution exceeds limit for {self.current_tier.value} tier"
        
        max_duration = limits['max_duration']
        if max_duration and duration > max_duration:
            return False, f"Duration exceeds limit for {self.current_tier.value} tier"
        
        return True, "OK"
    
    def needs_watermark(self) -> bool:
        """
        Check if watermark is required
        
        Returns:
            True if watermark required
        """
        limits = self.get_limits()
        return limits.get('watermark', True)
    
    def deactivate_license(self):
        """Deactivate current license"""
        if os.path.exists(self.license_file):
            os.remove(self.license_file)
        
        self.license_data = None
        self.current_tier = LicenseTier.FREE
