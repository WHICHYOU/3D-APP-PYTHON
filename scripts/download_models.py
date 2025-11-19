#!/usr/bin/env python3
"""
Download AI Models Script

Downloads required AI models for depth estimation.
"""

import os
import sys
from pathlib import Path
import urllib.request
from tqdm import tqdm


MODELS = {
    'midas_v31': {
        'url': 'https://github.com/isl-org/MiDaS/releases/download/v3_1/dpt_beit_large_512.pt',
        'filename': 'midas_v31_large.pt',
        'size': '1.4 GB',
    },
    'depth_anything_v2': {
        'url': 'https://huggingface.co/depth-anything/Depth-Anything-V2-Large/resolve/main/depth_anything_v2_vitl.pth',
        'filename': 'depth_anything_v2_large.pth',
        'size': '1.3 GB',
    },
}


def download_file(url: str, destination: Path):
    """Download file with progress bar"""
    print(f"Downloading to {destination}...")
    
    # TODO: Implement actual download with progress
    # For now, just create placeholder
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Download URL: {url}")
    print("NOTE: Actual download not implemented in placeholder")


def main():
    """Main function"""
    models_dir = Path(__file__).parent.parent / 'src' / 'ai_core' / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("2D to 3D Converter - Model Downloader")
    print("=" * 50)
    
    for model_name, model_info in MODELS.items():
        print(f"\nModel: {model_name}")
        print(f"Size: {model_info['size']}")
        
        destination = models_dir / model_info['filename']
        
        if destination.exists():
            print(f"✓ Already downloaded")
            continue
        
        response = input(f"Download {model_name}? (y/n): ")
        if response.lower() == 'y':
            download_file(model_info['url'], destination)
            print("✓ Download complete")
    
    print("\n" + "=" * 50)
    print("Model download complete!")


if __name__ == '__main__':
    main()
