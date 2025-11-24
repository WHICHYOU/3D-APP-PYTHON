"""
Configuration Manager
Handle application configuration
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manage application configuration"""
    
    DEFAULT_CONFIG = {
        'depth_estimation': {
            'model': 'midas_hybrid',  # Default to balanced model
            'device': 'auto',
            'batch_size': 4,
            'precision': 'fp16',
        },
        'rendering': {
            'ipd': 65.0,
            'depth_intensity': 75.0,
            'hole_filling': 'fast_marching',
        },
        'video': {
            'fps': 30,
            'quality': 'high',
            'codec': 'libx264',
        },
        'ui': {
            'theme': 'light',
            'preview_size': [640, 360],
            'auto_save': True,
        },
        'paths': {
            'models_dir': './models',
            'temp_dir': './temp',
            'output_dir': './output',
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file (YAML)
        """
        self.config_path = config_path or 'config.yaml'
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load from file if exists
        if os.path.exists(self.config_path):
            self.load()
    
    def load(self, config_path: Optional[str] = None):
        """
        Load configuration from file
        
        Args:
            config_path: Path to config file (optional)
        """
        path = config_path or self.config_path
        
        if not os.path.exists(path):
            return
        
        with open(path, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        # Merge with defaults
        self._merge_config(self.config, loaded_config)
    
    def save(self, config_path: Optional[str] = None):
        """
        Save configuration to file
        
        Args:
            config_path: Path to save config (optional)
        """
        path = config_path or self.config_path
        
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Dot-separated key path (e.g., 'depth_estimation.model')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value
        
        Args:
            key: Dot-separated key path
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
    
    def _merge_config(self, base: Dict, override: Dict):
        """
        Recursively merge override config into base
        
        Args:
            base: Base configuration
            override: Override configuration
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get_all(self) -> Dict:
        """
        Get entire configuration
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
