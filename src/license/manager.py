"""
License Management System
------------------------
Handles license validation, activation, and feature gating.

Tiers:
- Free: 10 files/day, watermark on output, basic features
- Pro ($49/year): Unlimited files, no watermark, all features
- Enterprise ($299/year): Pro + API access, priority support, custom branding

Usage:
    from src.license.manager import LicenseManager
    
    license = LicenseManager()
    if license.is_feature_enabled("batch_processing"):
        # Allow batch processing
        pass
"""

import json
import os
import hashlib
import hmac
import secrets
import time
import platform
import subprocess
import uuid
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum


class LicenseTier(Enum):
    """License tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class LicenseManager:
    """Manages license validation and feature access"""
    
    # License server configuration
    LICENSE_SERVER = "https://api.3dconversion.app"
    ACTIVATION_ENDPOINT = "/license/activate"
    VALIDATION_ENDPOINT = "/license/validate"
    DEACTIVATION_ENDPOINT = "/license/deactivate"
    
    # Secret key for local validation (should be obfuscated in production)
    SECRET_KEY = "3d_conv_app_secret_2025"
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize license manager.
        
        Args:
            config_dir: Directory for license storage
        """
        if config_dir is None:
            if platform.system() == "Windows":
                config_dir = Path(os.getenv("LOCALAPPDATA")) / "3DConversion"
            elif platform.system() == "Darwin":
                config_dir = Path.home() / "Library" / "Application Support" / "com.3dconversion.app"
            else:  # Linux
                config_dir = Path.home() / ".config" / "3DConversion"
        
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.license_file = self.config_dir / "license.json"
        self.usage_file = self.config_dir / "usage.json"
        
        # Load license and usage data
        self.license_data = self._load_license()
        self.usage_data = self._load_usage()
        
        # Get hardware ID
        self.hardware_id = self._get_hardware_id()
    
    def _load_license(self) -> Dict:
        """Load license data from disk"""
        if self.license_file.exists():
            try:
                with open(self.license_file) as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_license(self):
        """Save license data to disk"""
        with open(self.license_file, 'w') as f:
            json.dump(self.license_data, f, indent=2)
    
    def _load_usage(self) -> Dict:
        """Load usage data from disk"""
        if self.usage_file.exists():
            try:
                with open(self.usage_file) as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_usage(self):
        """Save usage data to disk"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
    
    def _get_hardware_id(self) -> str:
        """
        Generate unique hardware ID for this machine.
        Combination of MAC address, CPU info, and disk serial.
        """
        identifiers = []
        
        # Get MAC address
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                          for elements in range(0,8*6,8)][::-1])
            identifiers.append(mac)
        except Exception:
            pass
        
        # Get CPU info
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(
                    "wmic cpu get processorid", shell=True, text=True
                )
                cpu_id = output.split('\n')[1].strip()
                identifiers.append(cpu_id)
            elif platform.system() == "Darwin":
                output = subprocess.check_output(
                    ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
                )
                identifiers.append(output.strip())
            else:  # Linux
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "Serial" in line or "processor" in line:
                            identifiers.append(line.strip())
                            break
        except Exception:
            pass
        
        # Get platform info
        identifiers.append(platform.platform())
        
        # Hash all identifiers
        combined = ''.join(identifiers)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def get_tier(self) -> LicenseTier:
        """Get current license tier"""
        if not self.license_data:
            return LicenseTier.FREE
        
        tier = self.license_data.get("tier", "free")
        
        try:
            return LicenseTier(tier)
        except ValueError:
            return LicenseTier.FREE
    
    def is_activated(self) -> bool:
        """Check if a license is activated"""
        if not self.license_data:
            return False
        
        # Check if license has expired
        expiry = self.license_data.get("expiry")
        if expiry:
            expiry_date = datetime.fromisoformat(expiry)
            if datetime.now() > expiry_date:
                return False
        
        # Verify signature
        return self._verify_license()
    
    def _verify_license(self) -> bool:
        """Verify license signature"""
        if not self.license_data:
            return False
        
        # Extract signature
        signature = self.license_data.get("signature")
        if not signature:
            return False
        
        # Reconstruct message
        message = f"{self.license_data.get('key')}:{self.license_data.get('tier')}:{self.license_data.get('expiry')}:{self.hardware_id}"
        
        # Verify HMAC
        expected = hmac.new(
            self.SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)
    
    def activate(self, license_key: str) -> tuple[bool, str]:
        """
        Activate a license key.
        
        Args:
            license_key: The license key to activate
            
        Returns:
            (success, message) tuple
        """
        import requests
        
        try:
            # Send activation request to server
            response = requests.post(
                f"{self.LICENSE_SERVER}{self.ACTIVATION_ENDPOINT}",
                json={
                    "key": license_key,
                    "hardware_id": self.hardware_id,
                    "platform": platform.system()
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store license data
                self.license_data = {
                    "key": license_key,
                    "tier": data["tier"],
                    "expiry": data["expiry"],
                    "hardware_id": self.hardware_id,
                    "signature": data["signature"],
                    "activated_at": datetime.now().isoformat()
                }
                
                self._save_license()
                return True, "License activated successfully!"
                
            elif response.status_code == 400:
                error = response.json().get("error", "Invalid license key")
                return False, error
                
            elif response.status_code == 409:
                return False, "License key already in use on another device"
                
            else:
                return False, "Activation failed. Please try again."
                
        except requests.exceptions.RequestException as e:
            # Offline activation (limited validation)
            if self._validate_key_format(license_key):
                # Store with grace period
                self.license_data = {
                    "key": license_key,
                    "tier": "pro",  # Assume Pro for offline
                    "expiry": (datetime.now() + timedelta(days=7)).isoformat(),
                    "hardware_id": self.hardware_id,
                    "signature": "",
                    "activated_at": datetime.now().isoformat(),
                    "offline": True
                }
                self._save_license()
                return True, "License activated offline (7-day grace period)"
            
            return False, f"Activation failed: {str(e)}"
    
    def _validate_key_format(self, key: str) -> bool:
        """Validate license key format"""
        # Format: XXXX-XXXX-XXXX-XXXX (16 alphanumeric characters)
        parts = key.split('-')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if len(part) != 4 or not part.isalnum():
                return False
        
        return True
    
    def deactivate(self) -> tuple[bool, str]:
        """
        Deactivate current license.
        
        Returns:
            (success, message) tuple
        """
        if not self.license_data:
            return False, "No license to deactivate"
        
        import requests
        
        try:
            # Send deactivation request
            response = requests.post(
                f"{self.LICENSE_SERVER}{self.DEACTIVATION_ENDPOINT}",
                json={
                    "key": self.license_data.get("key"),
                    "hardware_id": self.hardware_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                # Clear license data
                self.license_data = {}
                self._save_license()
                return True, "License deactivated successfully"
            else:
                return False, "Deactivation failed"
                
        except requests.exceptions.RequestException:
            # Offline deactivation (just clear local data)
            self.license_data = {}
            self._save_license()
            return True, "License deactivated locally"
    
    def check_usage_limit(self, increment: int = 1) -> bool:
        """
        Check if user has exceeded usage limits (Free tier only).
        
        Args:
            increment: Number of files to add to usage count
            
        Returns:
            True if within limits, False if exceeded
        """
        tier = self.get_tier()
        
        # Pro and Enterprise have unlimited usage
        if tier in [LicenseTier.PRO, LicenseTier.ENTERPRISE]:
            return True
        
        # Free tier: 10 files per day
        today = datetime.now().date().isoformat()
        
        if self.usage_data.get("date") != today:
            # Reset daily counter
            self.usage_data = {"date": today, "count": 0}
        
        current_count = self.usage_data.get("count", 0)
        
        if current_count + increment > 10:
            return False
        
        # Increment and save
        self.usage_data["count"] = current_count + increment
        self._save_usage()
        
        return True
    
    def get_remaining_quota(self) -> Optional[int]:
        """
        Get remaining file conversions for today (Free tier).
        
        Returns:
            Number of remaining conversions, or None if unlimited
        """
        tier = self.get_tier()
        
        if tier in [LicenseTier.PRO, LicenseTier.ENTERPRISE]:
            return None  # Unlimited
        
        today = datetime.now().date().isoformat()
        
        if self.usage_data.get("date") != today:
            return 10  # Fresh day
        
        used = self.usage_data.get("count", 0)
        return max(0, 10 - used)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled for current license tier.
        
        Args:
            feature: Feature name to check
            
        Returns:
            True if feature is enabled
        """
        tier = self.get_tier()
        
        # Feature matrix
        features = {
            "batch_processing": [LicenseTier.PRO, LicenseTier.ENTERPRISE],
            "no_watermark": [LicenseTier.PRO, LicenseTier.ENTERPRISE],
            "video_conversion": [LicenseTier.FREE, LicenseTier.PRO, LicenseTier.ENTERPRISE],
            "api_access": [LicenseTier.ENTERPRISE],
            "custom_branding": [LicenseTier.ENTERPRISE],
            "priority_support": [LicenseTier.PRO, LicenseTier.ENTERPRISE],
            "advanced_settings": [LicenseTier.PRO, LicenseTier.ENTERPRISE],
            "export_formats": [LicenseTier.PRO, LicenseTier.ENTERPRISE]
        }
        
        allowed_tiers = features.get(feature, [LicenseTier.FREE, LicenseTier.PRO, LicenseTier.ENTERPRISE])
        return tier in allowed_tiers
    
    def get_license_info(self) -> Dict:
        """Get human-readable license information"""
        tier = self.get_tier()
        
        info = {
            "tier": tier.value,
            "tier_name": tier.name,
            "is_activated": self.is_activated(),
            "hardware_id": self.hardware_id
        }
        
        if self.license_data:
            info.update({
                "key": self.license_data.get("key", ""),
                "expiry": self.license_data.get("expiry"),
                "activated_at": self.license_data.get("activated_at")
            })
            
            # Calculate days remaining
            if info["expiry"]:
                expiry_date = datetime.fromisoformat(info["expiry"])
                days_remaining = (expiry_date - datetime.now()).days
                info["days_remaining"] = max(0, days_remaining)
        
        # Add quota info for Free tier
        if tier == LicenseTier.FREE:
            info["remaining_quota"] = self.get_remaining_quota()
        
        return info
    
    def get_upgrade_url(self) -> str:
        """Get URL for upgrading license"""
        return "https://3dconversion.app/upgrade"
    
    @staticmethod
    def generate_license_key(tier: str, duration_days: int = 365) -> tuple[str, Dict]:
        """
        Generate a new license key (server-side only).
        
        Args:
            tier: License tier (pro/enterprise)
            duration_days: Validity period in days
            
        Returns:
            (license_key, metadata) tuple
        """
        # Generate random key
        key_parts = [
            ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(4))
            for _ in range(4)
        ]
        license_key = '-'.join(key_parts)
        
        # Calculate expiry
        expiry = (datetime.now() + timedelta(days=duration_days)).isoformat()
        
        # Generate metadata
        metadata = {
            "tier": tier,
            "expiry": expiry,
            "created_at": datetime.now().isoformat(),
            "max_activations": 3 if tier == "pro" else 10
        }
        
        return license_key, metadata


if __name__ == "__main__":
    # Test license manager
    print("Testing License Manager...")
    
    lm = LicenseManager()
    
    print(f"\nHardware ID: {lm.hardware_id}")
    print(f"Current Tier: {lm.get_tier().value}")
    print(f"Is Activated: {lm.is_activated()}")
    
    # Check features
    print("\nFeature Access:")
    features = [
        "batch_processing",
        "no_watermark",
        "video_conversion",
        "api_access",
        "priority_support"
    ]
    
    for feature in features:
        enabled = lm.is_feature_enabled(feature)
        print(f"  {feature}: {'✓' if enabled else '✗'}")
    
    # Check quota
    if lm.get_tier() == LicenseTier.FREE:
        remaining = lm.get_remaining_quota()
        print(f"\nRemaining quota: {remaining}/10 files today")
    
    # Get license info
    print("\nLicense Info:")
    info = lm.get_license_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test key generation (server-side)
    print("\nGenerating test Pro license key...")
    key, meta = LicenseManager.generate_license_key("pro", 365)
    print(f"  Key: {key}")
    print(f"  Metadata: {meta}")
