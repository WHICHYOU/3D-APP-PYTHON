"""
Batch Processor Module

Handles batch processing of video frames through the depth estimation
and stereoscopic rendering pipeline.
"""

from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
import logging
import cv2
import numpy as np

from ..ai_core.depth_estimation import DepthEstimator
from ..rendering.dibr_renderer import DIBRRenderer
from ..rendering.hole_filling import fill_stereo_pair_holes
from ..rendering.sbs_composer import SBSComposer

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Processes video frames in batches through the 3D conversion pipeline."""
    
    def __init__(
        self,
        depth_estimator: Optional[DepthEstimator] = None,
        dibr_renderer: Optional[DIBRRenderer] = None,
        sbs_composer: Optional[SBSComposer] = None,
        max_workers: int = 1
    ):
        """
        Initialize batch processor.
        
        Args:
            depth_estimator: Depth estimation model (creates default if None)
            dibr_renderer: DIBR renderer (creates default if None)
            sbs_composer: SBS composer (creates default if None)
            max_workers: Number of parallel workers (1 = sequential)
        """
        self.depth_estimator = depth_estimator or DepthEstimator()
        self.dibr_renderer = dibr_renderer or DIBRRenderer()
        self.sbs_composer = sbs_composer or SBSComposer()
        self.max_workers = max_workers
        
        logger.info(f"BatchProcessor initialized with {max_workers} worker(s)")
    
    def process_frame(
        self,
        frame_path: Path,
        output_dir: Path,
        output_format: str = "half_sbs",
        depth_intensity: float = 0.75,
        save_intermediate: bool = False
    ) -> Path:
        """
        Process a single frame through the pipeline.
        
        Args:
            frame_path: Path to input frame
            output_dir: Directory for output
            output_format: Output format (half_sbs, full_sbs, anaglyph, top_bottom)
            depth_intensity: Depth effect strength (0.0-1.0)
            save_intermediate: Save depth maps and stereo pairs
            
        Returns:
            Path to output frame
        """
        # Load frame
        frame_bgr = cv2.imread(str(frame_path))
        if frame_bgr is None:
            raise ValueError(f"Failed to load frame: {frame_path}")
        
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        
        # Estimate depth
        depth_map = self.depth_estimator.estimate_depth(frame_rgb)
        
        # Render stereo pair
        left_view, right_view = self.dibr_renderer.render_stereo_pair(
            frame_rgb,
            depth_map,
            depth_intensity=depth_intensity
        )
        
        # Fill holes
        left_view, right_view = fill_stereo_pair_holes(left_view, right_view)
        
        # Compose output format
        if output_format == "half_sbs":
            output = self.sbs_composer.compose_half_sbs(left_view, right_view)
        elif output_format == "full_sbs":
            output = self.sbs_composer.compose_full_sbs(left_view, right_view)
        elif output_format == "anaglyph":
            output = self.sbs_composer.compose_anaglyph(left_view, right_view)
        elif output_format == "top_bottom":
            output = self.sbs_composer.compose_top_bottom(left_view, right_view, half_resolution=True)
        else:
            raise ValueError(f"Unknown output format: {output_format}")
        
        # Save output
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / frame_path.name
        output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_path), output_bgr)
        
        # Save intermediate results if requested
        if save_intermediate:
            depth_path = output_dir / f"depth_{frame_path.name}"
            depth_normalized = (depth_map * 255).astype(np.uint8)
            cv2.imwrite(str(depth_path), depth_normalized)
            
            left_path = output_dir / f"left_{frame_path.name}"
            left_bgr = cv2.cvtColor(left_view, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(left_path), left_bgr)
            
            right_path = output_dir / f"right_{frame_path.name}"
            right_bgr = cv2.cvtColor(right_view, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(right_path), right_bgr)
        
        return output_path
    
    def process_frames(
        self,
        frame_paths: List[Path],
        output_dir: Path,
        output_format: str = "half_sbs",
        depth_intensity: float = 0.75,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        save_intermediate: bool = False
    ) -> List[Path]:
        """
        Process frames sequentially through the pipeline.
        
        Args:
            frame_paths: List of input frame paths
            output_dir: Directory for output frames
            output_format: Output format
            depth_intensity: Depth effect strength
            progress_callback: Callback function(current, total)
            save_intermediate: Save depth maps and stereo pairs
            
        Returns:
            List of output frame paths
        """
        output_paths: List[Path] = []
        total = len(frame_paths)

        logger.info(f"Processing {total} frames (batch mode)...")

        # Determine batch size from depth estimator if available
        batch_size = getattr(self.depth_estimator, 'batch_size', 4)
        # Fallback to 4 if not set
        if not isinstance(batch_size, int) or batch_size <= 0:
            batch_size = 4

        # Process in batches: run depth estimation in batches, then render/save each frame (can be parallelized)
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            batch_paths = frame_paths[start:end]

            # Load batch images into memory
            images = []
            for p in batch_paths:
                img_bgr = cv2.imread(str(p))
                if img_bgr is None:
                    raise ValueError(f"Failed to load frame: {p}")
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                images.append(img_rgb)

            # Run batched depth estimation
            depth_maps = self.depth_estimator.batch_estimate(images, normalize=True, batch_size=batch_size)

            # For each result in the batch, render and save. Rendering/hole-filling/composition are CPU-bound
            for i_in_batch, frame_path in enumerate(batch_paths, start + 1):
                try:
                    depth_map = depth_maps[i_in_batch - start]

                    # Render stereo pair
                    left_view, right_view = self.dibr_renderer.render_stereo_pair(
                        images[i_in_batch - start],
                        depth_map,
                        depth_intensity=depth_intensity
                    )

                    # Fill holes (method comes from config manager elsewhere; using default fast_marching)
                    left_view, right_view = fill_stereo_pair_holes(left_view, right_view)

                    # Compose output format
                    if output_format == "half_sbs":
                        output = self.sbs_composer.compose_half_sbs(left_view, right_view)
                    elif output_format == "full_sbs":
                        output = self.sbs_composer.compose_full_sbs(left_view, right_view)
                    elif output_format == "anaglyph":
                        output = self.sbs_composer.compose_anaglyph(left_view, right_view)
                    elif output_format == "top_bottom":
                        output = self.sbs_composer.compose_top_bottom(left_view, right_view, half_resolution=True)
                    else:
                        raise ValueError(f"Unknown output format: {output_format}")

                    # Save output
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_path = output_dir / frame_path.name
                    output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(str(output_path), output_bgr)
                    output_paths.append(output_path)

                    # Save intermediate results if requested
                    if save_intermediate:
                        depth_path = output_dir / f"depth_{frame_path.name}"
                        depth_normalized = (depth_map * 255).astype(np.uint8)
                        cv2.imwrite(str(depth_path), depth_normalized)

                        left_path = output_dir / f"left_{frame_path.name}"
                        left_bgr = cv2.cvtColor(left_view, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(str(left_path), left_bgr)

                        right_path = output_dir / f"right_{frame_path.name}"
                        right_bgr = cv2.cvtColor(right_view, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(str(right_path), right_bgr)

                    # Progress callback (global index)
                    if progress_callback:
                        progress_callback(i_in_batch, total)

                    if i_in_batch % 10 == 0 or i_in_batch == total:
                        logger.info(f"Processed {i_in_batch}/{total} frames ({i_in_batch*100//total}%)")

                except Exception as e:
                    logger.error(f"Failed to process frame {frame_path}: {e}")
                    raise

        logger.info(f"Successfully processed {len(output_paths)} frames")
        return output_paths
