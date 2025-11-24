"""
Main Depth Estimation Module
Handles depth map generation using AI models (MiDaS, Depth-Anything-V2)
"""
import numpy as np
import cv2
import torch
from typing import List, Optional, Tuple, Dict
from pathlib import Path


# Model metadata for UI selection
MODEL_REGISTRY = {
    'midas_small': {
        'name': 'MiDaS Small (Fastest)',
        'hub_name': 'MiDaS_small',
        'transform_type': 'small_transform',
        'description': 'Smallest and fastest model. Good for real-time preview or quick processing.',
        'speed': 'Very Fast (~90 FPS)',
        'quality': 'Basic',
        'vram': '~1 GB',
        'model_size': '~100 MB',
        'recommended': 'Quick conversions, preview mode',
    },
    'midas_hybrid': {
        'name': 'MiDaS Hybrid (Balanced)',
        'hub_name': 'DPT_Hybrid',
        'transform_type': 'dpt_transform',
        'description': 'Balanced speed and quality. Best for most use cases.',
        'speed': 'Fast (~30-40 FPS)',
        'quality': 'Good',
        'vram': '~2 GB',
        'model_size': '~470 MB',
        'recommended': 'General purpose, best speed/quality ratio',
    },
    'midas_swin2_large': {
        'name': 'MiDaS Swin2-Large (High Quality)',
        'hub_name': 'DPT_Swin2_L_384',
        'transform_type': 'swin384_transform',
        'description': 'High quality depth with excellent details. Good balance of speed and accuracy.',
        'speed': 'Medium (~20-25 FPS)',
        'quality': 'Very Good',
        'vram': '~3 GB',
        'model_size': '~840 MB',
        'recommended': 'High quality video conversion',
    },
    'midas_swin2_tiny': {
        'name': 'MiDaS Swin2-Tiny (Fast)',
        'hub_name': 'DPT_Swin2_T_256',
        'transform_type': 'swin256_transform',
        'description': 'Tiny Swin transformer. Very fast with good quality.',
        'speed': 'Very Fast (~64 FPS)',
        'quality': 'Good',
        'vram': '~1.5 GB',
        'model_size': '~155 MB',
        'recommended': 'Fast processing with good results',
    },
    'midas_large': {
        'name': 'MiDaS Large (Maximum Quality)',
        'hub_name': 'DPT_Large',
        'transform_type': 'dpt_transform',
        'description': 'Highest quality depth estimation. Slowest but most accurate.',
        'speed': 'Slow (~5-7 FPS)',
        'quality': 'Excellent',
        'vram': '~4 GB',
        'model_size': '~1.3 GB',
        'recommended': 'Professional work, maximum quality needed',
    },
}

# Default model (fastest good quality)
DEFAULT_MODEL = 'midas_hybrid'


class DepthEstimator:
    """Main class for depth estimation from 2D images"""
    
    def __init__(
        self,
        model_type: str = DEFAULT_MODEL,
        device: str = "auto",
        precision: str = "fp16",
        batch_size: int = 4
    ):
        """
        Initialize depth estimator
        
        Args:
            model_type: Model to use (see MODEL_REGISTRY for options)
            device: Device for inference ('auto', 'cuda', 'cpu', 'mps')
            precision: Precision mode ('fp32', 'fp16')
            batch_size: Batch size for processing
        """
        if model_type not in MODEL_REGISTRY:
            print(f"Warning: Unknown model '{model_type}', using default '{DEFAULT_MODEL}'")
            model_type = DEFAULT_MODEL
            
        self.model_type = model_type
        self.model_info = MODEL_REGISTRY[model_type]
        self.device = self._select_device(device)
        self.precision = precision
        self.batch_size = batch_size
        self.model = None
        self.transform = None
        
        # Load model
        self._load_model()
    
    def _select_device(self, device: str) -> torch.device:
        """Select appropriate device for inference"""
        if device == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return torch.device("mps")
            else:
                return torch.device("cpu")
        return torch.device(device)
    
    def _load_model(self):
        """Load the depth estimation model"""
        model_name = self.model_info['name']
        model_size = self.model_info['model_size']
        
        print(f"Loading {model_name}...")
        print(f"Model size: {model_size}")
        print("Note: First-time download may take a few minutes")
        print("Subsequent runs will use cached models...")
        
        try:
            # Load MiDaS model from torch hub
            print(f"Loading model: {self.model_info['hub_name']}")
            self.model = torch.hub.load(
                "intel-isl/MiDaS",
                self.model_info['hub_name'],
                pretrained=True,
                trust_repo=True,
                skip_validation=True
            )
            
            # Load appropriate transforms
            print("Loading transforms...")
            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", skip_validation=True)
            
            # Select transform based on model type
            transform_name = self.model_info['transform_type']
            if transform_name == 'small_transform':
                self.transform = midas_transforms.small_transform
            elif transform_name == 'dpt_transform':
                self.transform = midas_transforms.dpt_transform
            elif transform_name == 'swin384_transform':
                # For Swin2-Large 384
                self.transform = midas_transforms.swin384_transform
            elif transform_name == 'swin256_transform':
                # For Swin2-Tiny 256
                self.transform = midas_transforms.swin256_transform
            else:
                # Fallback to dpt_transform
                self.transform = midas_transforms.dpt_transform
                
        except Exception as e:
            print(f"Error loading model: {e}")
            raise RuntimeError(f"Failed to load {model_name}: {e}")
        
        # Move model to device
        self.model.to(self.device)
        self.model.eval()
        
        # Enable half precision if requested and supported
        if self.precision == "fp16":
            if self.device.type == "cuda":
                self.model.half()
                print("Using FP16 precision on CUDA")
            elif self.device.type == "mps":
                # MPS supports FP16 since PyTorch 2.0
                try:
                    self.model.half()
                    print("Using FP16 precision on MPS")
                except Exception as e:
                    print(f"FP16 not supported on MPS, using FP32: {e}")
        
        print(f"✓ {model_name} loaded successfully on {self.device}")
        print(f"  Expected speed: {self.model_info['speed']}")
        print(f"  Quality level: {self.model_info['quality']}")
    
    @staticmethod
    def get_available_models() -> Dict[str, Dict]:
        """
        Get list of available models with metadata
        
        Returns:
            Dictionary of model configurations
        """
        return MODEL_REGISTRY.copy()
    
    @staticmethod
    def get_model_info(model_type: str) -> Optional[Dict]:
        """
        Get metadata for a specific model
        
        Args:
            model_type: Model identifier
            
        Returns:
            Model metadata dictionary or None
        """
        return MODEL_REGISTRY.get(model_type)
    
    def estimate_depth(
        self,
        image: np.ndarray,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Estimate depth map for a single image
        
        Args:
            image: Input RGB image (H, W, 3)
            normalize: Whether to normalize output to [0, 1]
        
        Returns:
            Depth map (H, W) with values in [0, 1] if normalized
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call _load_model() first.")
        
        # Store original dimensions
        original_height, original_width = image.shape[:2]
        
        # Convert BGR to RGB if needed (OpenCV loads as BGR)
        if image.shape[2] == 3:
            # Assume input is RGB (from PIL or already converted)
            img_rgb = image
        else:
            img_rgb = image
        
        # Apply model-specific transform
        input_batch = self.transform(img_rgb).to(self.device)
        
        # Add batch dimension if needed
        if len(input_batch.shape) == 3:
            input_batch = input_batch.unsqueeze(0)
        
        # Apply half precision if enabled
        if self.precision == "fp16" and self.device.type == "cuda":
            input_batch = input_batch.half()
        
        # Run inference
        with torch.no_grad():
            prediction = self.model(input_batch)
            
            # Handle different output formats
            if isinstance(prediction, torch.Tensor):
                depth = prediction
            else:
                depth = prediction[0]
            
            # Remove batch dimension
            depth = depth.squeeze().cpu().numpy()
        
        # Resize to original dimensions if needed
        if depth.shape != (original_height, original_width):
            depth = cv2.resize(
                depth,
                (original_width, original_height),
                interpolation=cv2.INTER_CUBIC
            )
        
        # Normalize to [0, 1] if requested
        if normalize:
            depth_min = depth.min()
            depth_max = depth.max()
            if depth_max - depth_min > 1e-6:
                depth = (depth - depth_min) / (depth_max - depth_min)
            else:
                depth = np.zeros_like(depth)
        
        return depth.astype(np.float32)
    
    def batch_estimate(
        self,
        images: List[np.ndarray],
        normalize: bool = True,
        batch_size: int = 4
    ) -> List[np.ndarray]:
        """
        Estimate depth maps for multiple images (batch processing)
        
        Args:
            images: List of RGB images
            normalize: Whether to normalize outputs
            batch_size: Number of images to process at once
        
        Returns:
            List of depth maps
        """
        if not images:
            return []
        
        depth_maps: List[np.ndarray] = []

        # Convert all images to transformed tensors first (CxHxW)
        tensors = []
        original_sizes = []
        for img in images:
            original_sizes.append(img.shape[:2])
            t = self.transform(img)
            # Ensure tensor is 3D (C,H,W)
            if t.dim() == 3:
                tensors.append(t)
            else:
                tensors.append(t.squeeze(0))

        # Run inference in batches
        for start in range(0, len(tensors), batch_size):
            batch_tensors = tensors[start:start + batch_size]
            batch = torch.stack(batch_tensors, dim=0).to(self.device)

            # Apply half precision on CUDA if requested
            if self.precision == "fp16" and self.device.type == "cuda":
                batch = batch.half()

            with torch.no_grad():
                preds = self.model(batch)

            # Normalize preds to a list of numpy arrays
            if isinstance(preds, torch.Tensor):
                pred_batch = preds
            else:
                # Some MiDaS variants return a tuple/list
                pred_batch = preds[0]

            # Move to CPU and convert
            pred_batch = pred_batch.squeeze(1).cpu().numpy() if pred_batch.dim() == 4 else pred_batch.cpu().numpy()

            # For each item in the batch, resize to original and normalize
            for i_in_batch, pred in enumerate(pred_batch):
                global_idx = start + i_in_batch
                orig_h, orig_w = original_sizes[global_idx]

                # pred may be in shape (H', W')
                if pred.shape != (orig_h, orig_w):
                    pred_resized = cv2.resize(pred, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC)
                else:
                    pred_resized = pred

                if normalize:
                    dmin = pred_resized.min()
                    dmax = pred_resized.max()
                    if dmax - dmin > 1e-6:
                        pred_resized = (pred_resized - dmin) / (dmax - dmin)
                    else:
                        pred_resized = np.zeros_like(pred_resized)

                depth_maps.append(pred_resized.astype(np.float32))

        return depth_maps
    
    def set_quality_preset(self, preset: str):
        """
        Set quality preset for depth estimation
        
        Args:
            preset: Quality preset ('fast', 'balanced', 'high')
        """
        # TODO: Implement quality presets
        print(f"Setting quality preset: {preset}")
        pass
    
    def release(self):
        """Release GPU memory and cleanup"""
        if self.model is not None:
            del self.model
            self.model = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def load_model(model_name: str, device: str) -> torch.nn.Module:
    """
    Load a depth estimation model
    
    Args:
        model_name: Name of the model
        device: Device to load model on
    
    Returns:
        Loaded model
    """
    # TODO: Implement model loading
    print(f"Loading model: {model_name} on {device}")
    return None


def normalize_depth(depth_map: np.ndarray) -> np.ndarray:
    """
    Normalize depth map to [0, 1] range
    
    Args:
        depth_map: Raw depth map
    
    Returns:
        Normalized depth map
    """
    min_val = depth_map.min()
    max_val = depth_map.max()
    
    if max_val - min_val < 1e-6:
        return np.zeros_like(depth_map)
    
    return (depth_map - min_val) / (max_val - min_val)
