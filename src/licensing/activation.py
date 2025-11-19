"""
License Activation
Handle online license activation
"""
import requests
from typing import Optional, Dict


class ActivationManager:
    """Manage license activation with server"""
    
    def __init__(self, server_url: Optional[str] = None):
        """
        Initialize activation manager
        
        Args:
            server_url: License server URL
        """
        self.server_url = server_url or 'https://api.converter3d.com/v1'
    
    def activate(
        self,
        license_key: str,
        email: str,
        hardware_id: str
    ) -> tuple:
        """
        Activate license with server
        
        Args:
            license_key: License key
            email: User email
            hardware_id: Hardware fingerprint
        
        Returns:
            Tuple of (success, result_data or error_message)
        """
        endpoint = f"{self.server_url}/licenses/activate"
        
        payload = {
            'license_key': license_key,
            'email': email,
            'hardware_id': hardware_id,
        }
        
        try:
            # TODO: Implement actual API call
            # response = requests.post(endpoint, json=payload, timeout=10)
            
            # Mock response for now
            print(f"Would activate license with server: {endpoint}")
            
            result = {
                'tier': 'pro',
                'expiry': '2025-12-31T23:59:59',
                'features': ['batch_processing', 'advanced_features'],
            }
            
            return True, result
        
        except Exception as e:
            return False, f"Activation failed: {str(e)}"
    
    def deactivate(
        self,
        license_key: str,
        hardware_id: str
    ) -> tuple:
        """
        Deactivate license on server
        
        Args:
            license_key: License key
            hardware_id: Hardware fingerprint
        
        Returns:
            Tuple of (success, message)
        """
        endpoint = f"{self.server_url}/licenses/deactivate"
        
        payload = {
            'license_key': license_key,
            'hardware_id': hardware_id,
        }
        
        try:
            # TODO: Implement actual API call
            print(f"Would deactivate license with server: {endpoint}")
            return True, "License deactivated successfully"
        
        except Exception as e:
            return False, f"Deactivation failed: {str(e)}"
    
    def validate(
        self,
        license_key: str,
        hardware_id: str
    ) -> tuple:
        """
        Validate license with server
        
        Args:
            license_key: License key
            hardware_id: Hardware fingerprint
        
        Returns:
            Tuple of (is_valid, license_data or error_message)
        """
        endpoint = f"{self.server_url}/licenses/validate"
        
        payload = {
            'license_key': license_key,
            'hardware_id': hardware_id,
        }
        
        try:
            # TODO: Implement actual API call
            print(f"Would validate license with server: {endpoint}")
            
            result = {
                'valid': True,
                'tier': 'pro',
                'expires': '2025-12-31',
            }
            
            return True, result
        
        except Exception as e:
            return False, f"Validation failed: {str(e)}"
