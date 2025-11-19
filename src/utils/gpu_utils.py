"""
GPU Utilities
GPU detection and management
"""
import torch
from typing import Dict, List, Optional


def get_gpu_info() -> Dict:
    """
    Get information about available GPUs
    
    Returns:
        Dictionary with GPU information
    """
    info = {
        'cuda_available': torch.cuda.is_available(),
        'device_count': 0,
        'devices': [],
        'current_device': None,
        'cuda_version': None,
    }
    
    if torch.cuda.is_available():
        info['device_count'] = torch.cuda.device_count()
        info['cuda_version'] = torch.version.cuda
        info['current_device'] = torch.cuda.current_device()
        
        for i in range(info['device_count']):
            device_props = torch.cuda.get_device_properties(i)
            device_info = {
                'index': i,
                'name': device_props.name,
                'total_memory': device_props.total_memory,
                'major': device_props.major,
                'minor': device_props.minor,
            }
            info['devices'].append(device_info)
    
    return info


def get_optimal_device() -> torch.device:
    """
    Get optimal device for computation
    
    Returns:
        PyTorch device (cuda or cpu)
    """
    if torch.cuda.is_available():
        return torch.device('cuda')
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        # Apple Silicon
        return torch.device('mps')
    else:
        return torch.device('cpu')


def get_memory_info(device: Optional[torch.device] = None) -> Dict:
    """
    Get GPU memory usage information
    
    Args:
        device: Device to query (default: current device)
    
    Returns:
        Memory usage dictionary
    """
    if not torch.cuda.is_available():
        return {
            'allocated': 0,
            'reserved': 0,
            'total': 0,
        }
    
    if device is None:
        device = torch.cuda.current_device()
    elif isinstance(device, torch.device):
        device = device.index if device.index is not None else 0
    
    return {
        'allocated': torch.cuda.memory_allocated(device),
        'reserved': torch.cuda.memory_reserved(device),
        'total': torch.cuda.get_device_properties(device).total_memory,
    }


def clear_gpu_memory():
    """Clear GPU memory cache"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def estimate_batch_size(
    image_size: tuple,
    model_memory: float = 2.0,
    available_memory: Optional[float] = None
) -> int:
    """
    Estimate optimal batch size for given image size
    
    Args:
        image_size: (height, width) tuple
        model_memory: Estimated model memory in GB
        available_memory: Available GPU memory in GB (auto-detect if None)
    
    Returns:
        Recommended batch size
    """
    if available_memory is None:
        if torch.cuda.is_available():
            mem_info = get_memory_info()
            available_memory = (mem_info['total'] - mem_info['allocated']) / (1024 ** 3)
        else:
            # Conservative estimate for CPU
            available_memory = 4.0
    
    # Rough estimate: image memory = H * W * 3 * 4 bytes (float32)
    h, w = image_size
    image_memory_gb = (h * w * 3 * 4) / (1024 ** 3)
    
    # Account for intermediate activations (roughly 3x image size)
    per_image_memory = image_memory_gb * 3
    
    # Leave some headroom
    usable_memory = available_memory * 0.7 - model_memory
    
    batch_size = max(1, int(usable_memory / per_image_memory))
    
    return batch_size


def set_gpu_device(device_id: int):
    """
    Set active GPU device
    
    Args:
        device_id: GPU device ID
    """
    if torch.cuda.is_available() and device_id < torch.cuda.device_count():
        torch.cuda.set_device(device_id)


def format_memory_size(bytes: int) -> str:
    """
    Format memory size in human-readable format
    
    Args:
        bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "2.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"
