"""
Main Depth Estimation Module
Handles depth map generation using AI models (MiDaS, Depth-Anything-V2)
"""
import numpy as np
import cv2
import torch
from typing import List, Optional, Tuple
from pathlib import Path


class DepthEstimator:
    """Main class for depth estimation from 2D images"""
    
    def __init__(
        self,
        model_type: str = "midas_v3",
        device: str = "auto",
        precision: str = "fp16",
        batch_size: int = 4
    ):
        """
        Initialize depth estimator
        
        Args:
            model_type: Model to use ('midas_v3', 'depth_anything_v2')
            device: Device for inference ('auto', 'cuda', 'cpu', 'mps')
            precision: Precision mode ('fp32', 'fp16')
        """
        self.model_type = model_type
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
        print(f"Loading {self.model_type} model on {self.device}...")
        print("Note: First-time download may take several minutes (~1.3 GB)")
        print("Subsequent runs will use cached models...")
        
        if self.model_type == "midas_v3":
            # Load MiDaS v3.1 DPT-Large model
            print("Downloading/Loading MiDaS DPT-Large...")
            self.model = torch.hub.load(
                "intel-isl/MiDaS",
                "DPT_Large",
                pretrained=True,
                trust_repo=True
            )
            
            # Load transforms
            print("Loading transforms...")
            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
            self.transform = midas_transforms.dpt_transform
            
        elif self.model_type == "midas_v3_small":
            # Smaller/faster MiDaS variant
            self.model = torch.hub.load(
                "intel-isl/MiDaS",
                "DPT_Hybrid",
                pretrained=True,
                trust_repo=True
            )
            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
            self.transform = midas_transforms.dpt_transform
            
        elif self.model_type == "depth_anything_v2":
            # Depth-Anything-V2 (requires manual download)
            raise NotImplementedError(
                "Depth-Anything-V2 requires manual model download. "
                "Use 'midas_v3' for now."
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Move model to device
        self.model.to(self.device)
        self.model.eval()
        
        # Enable half precision if requested and supported
        if self.precision == "fp16" and self.device.type == "cuda":
            self.model.half()
        
        print(f"✓ Model loaded successfully on {self.device}")
    
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
