#!/usr/bin/env python3
"""
Quick test for model selection feature
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_model_registry():
    """Test the model registry"""
    from src.ai_core.depth_estimation import MODEL_REGISTRY, DEFAULT_MODEL, DepthEstimator
    
    print("=" * 60)
    print("MODEL SELECTION TEST")
    print("=" * 60)
    print()
    
    print(f"Default Model: {DEFAULT_MODEL}")
    print(f"Total Models Available: {len(MODEL_REGISTRY)}")
    print()
    
    print("Available Models:")
    print("-" * 60)
    for model_id, info in MODEL_REGISTRY.items():
        print(f"\n{model_id}:")
        print(f"  Name: {info['name']}")
        print(f"  Speed: {info['speed']}")
        print(f"  Quality: {info['quality']}")
        print(f"  VRAM: {info['vram']}")
        print(f"  Size: {info['model_size']}")
        print(f"  Hub: {info['hub_name']}")
    
    print()
    print("=" * 60)
    print("Testing Model Info Retrieval:")
    print("-" * 60)
    
    # Test static methods
    models = DepthEstimator.get_available_models()
    print(f"✓ get_available_models() returned {len(models)} models")
    
    info = DepthEstimator.get_model_info('midas_hybrid')
    if info:
        print(f"✓ get_model_info('midas_hybrid'): {info['name']}")
    else:
        print("✗ get_model_info failed")
    
    print()
    print("=" * 60)
    print("Testing Config Manager:")
    print("-" * 60)
    
    from src.utils.config_manager import ConfigManager
    config = ConfigManager()
    
    default_model = config.get('depth_estimation.model', 'not_found')
    print(f"Default model in config: {default_model}")
    
    if default_model in MODEL_REGISTRY:
        print(f"✓ Default model '{default_model}' exists in registry")
    else:
        print(f"✗ Default model '{default_model}' NOT in registry")
    
    print()
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_model_registry()
