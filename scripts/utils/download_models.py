#!/usr/bin/env python3
"""
Model Download Script

Downloads and caches required AI models for 3D conversion.
Run this before first use to avoid hanging during conversion.
"""

import torch
import sys
from pathlib import Path


def download_midas_models():
    """Download MiDaS models."""
    print("=" * 60)
    print("3D Converter - Model Download")
    print("=" * 60)
    print()
    print("This will download AI models (~1.3 GB total)")
    print("Models will be cached for future use")
    print()
    
    # Check device
    if torch.cuda.is_available():
        device = "cuda"
        print(f"✓ CUDA GPU detected: {torch.cuda.get_device_name(0)}")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        device = "mps"
        print("✓ Apple Silicon GPU detected (Metal)")
    else:
        device = "cpu"
        print("✓ Using CPU (GPU not available)")
    
    print()
    print("Downloading models...")
    print("-" * 60)
    
    try:
        # Download DPT-Large (main model - ~1.3 GB)
        print("\n1. Downloading MiDaS DPT-Large model...")
        print("   (This is the largest file - ~1.3 GB)")
        model = torch.hub.load(
            "intel-isl/MiDaS",
            "DPT_Large",
            pretrained=True,
            trust_repo=True,
            verbose=True
        )
        print("   ✓ DPT-Large downloaded successfully")
        
        # Download transforms
        print("\n2. Downloading MiDaS transforms...")
        transforms = torch.hub.load(
            "intel-isl/MiDaS",
            "transforms",
            verbose=True
        )
        print("   ✓ Transforms downloaded successfully")
        
        # Test model
        print("\n3. Testing model...")
        model.to(device)
        model.eval()
        print(f"   ✓ Model loaded successfully on {device}")
        
        # Show cache location
        cache_dir = Path.home() / ".cache" / "torch" / "hub"
        print()
        print("=" * 60)
        print("✓ All models downloaded successfully!")
        print(f"✓ Models cached in: {cache_dir}")
        print()
        print("You can now use the 3D converter without delays.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Error downloading models: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check your internet connection")
        print("2. Make sure you have ~2 GB free disk space")
        print("3. Try running again")
        print("=" * 60)
        return False


def check_models():
    """Check if models are already downloaded."""
    try:
        cache_dir = Path.home() / ".cache" / "torch" / "hub" / "checkpoints"
        if cache_dir.exists():
            model_files = list(cache_dir.glob("*.pt"))
            if model_files:
                print("Models already cached:")
                for model_file in model_files:
                    size_mb = model_file.stat().st_size / (1024 * 1024)
                    print(f"  - {model_file.name} ({size_mb:.1f} MB)")
                return True
        return False
    except Exception:
        return False


def main():
    """Main entry point."""
    print()
    
    # Check if already downloaded
    if check_models():
        print()
        print("✓ Models are already downloaded and cached.")
        print("  You can use the converter without downloading again.")
        print()
        response = input("Re-download models anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Skipping download.")
            return 0
        print()
    
    # Download models
    success = download_midas_models()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
