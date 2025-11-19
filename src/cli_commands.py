"""
CLI Command Implementations
"""
import sys
import cv2
import numpy as np
from pathlib import Path
from typing import Any
import logging

from .ai_core.depth_estimation import DepthEstimator
from .rendering.dibr_renderer import DIBRRenderer
from .rendering.sbs_composer import SBSComposer


def convert_file(args: Any, logger: logging.Logger) -> int:
    """Convert single file"""
    logger.info(f"Converting: {args.input}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Parameters: depth={args.depth}, ipd={args.ipd}, format={args.format}")
    
    try:
        # Load image
        logger.info("Loading image...")
        image_bgr = cv2.imread(args.input)
        if image_bgr is None:
            logger.error(f"Could not load image: {args.input}")
            return 1
        
        image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        height, width = image.shape[:2]
        logger.info(f"Image loaded: {width}x{height}")
        
        # Initialize depth estimator
        logger.info("Loading MiDaS model...")
        estimator = DepthEstimator(model_type="midas_v3", device="auto")
        logger.info("Model loaded successfully")
        
        # Estimate depth
        logger.info("Estimating depth...")
        depth_map = estimator.estimate_depth(image, normalize=True)
        logger.info(f"Depth estimated (range: {depth_map.min():.3f} - {depth_map.max():.3f})")
        
        # Render stereoscopic pair
        logger.info("Rendering stereo pair...")
        renderer = DIBRRenderer(ipd=args.ipd)
        left_view, right_view = renderer.render_stereo_pair(
            image, depth_map, depth_intensity=args.depth
        )
        logger.info("Stereo pair rendered")
        
        # Compose output
        logger.info(f"Composing {args.format} output...")
        composer = SBSComposer()
        
        if args.format == "half_sbs":
            output = composer.compose_half_sbs(left_view, right_view)
        elif args.format == "full_sbs":
            output = composer.compose_full_sbs(left_view, right_view)
        elif args.format == "anaglyph":
            output = composer.compose_anaglyph(left_view, right_view)
        elif args.format == "top_bottom":
            output = composer.compose_top_bottom(left_view, right_view, half=True)
        else:
            logger.error(f"Unknown format: {args.format}")
            return 1
        
        # Save output
        logger.info("Saving output...")
        output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        cv2.imwrite(args.output, output_bgr)
        logger.info(f"Saved to: {args.output}")
        
        logger.info("✅ Conversion complete!")
        return 0
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def batch_convert(args: Any, logger: logging.Logger) -> int:
    """Batch convert directory or video files"""
    from pathlib import Path
    
    input_path = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_path.exists():
        logger.error(f"Input path not found: {input_path}")
        return 1
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if input is a video file
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
    
    if input_path.is_file() and input_path.suffix.lower() in video_extensions:
        # Convert single video
        logger.info(f"Converting video: {input_path}")
        output_path = output_dir / f"{input_path.stem}_3d{input_path.suffix}"
        
        try:
            from convert_video import convert_video
            convert_video(
                input_path,
                output_path,
                output_format=args.format,
                depth_intensity=args.depth,
                use_temporal_filter=True,
                keep_audio=True,
                save_intermediate=False
            )
            return 0
        except Exception as e:
            logger.error(f"Video conversion failed: {e}")
            return 1
    
    elif input_path.is_dir():
        # Batch convert images
        files = list(input_path.glob(args.pattern))
        logger.info(f"Found {len(files)} files to convert")
        
        if len(files) == 0:
            logger.warning("No matching files found")
            return 1
        
        # Initialize pipeline once
        logger.info("Initializing conversion pipeline...")
        estimator = DepthEstimator(model_type="midas_v3", device="auto")
        renderer = DIBRRenderer(ipd=args.ipd)
        composer = SBSComposer()
        
        success_count = 0
        for i, file_path in enumerate(files, 1):
            try:
                logger.info(f"\n[{i}/{len(files)}] Converting {file_path.name}...")
                
                # Load image
                image_bgr = cv2.imread(str(file_path))
                if image_bgr is None:
                    logger.warning(f"Skipping: Could not load {file_path}")
                    continue
                
                image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                
                # Process
                depth_map = estimator.estimate_depth(image, normalize=True)
                left_view, right_view = renderer.render_stereo_pair(
                    image, depth_map, depth_intensity=args.depth
                )
                
                # Compose
                if args.format == "half_sbs":
                    output = composer.compose_half_sbs(left_view, right_view)
                elif args.format == "full_sbs":
                    output = composer.compose_full_sbs(left_view, right_view)
                elif args.format == "anaglyph":
                    output = composer.compose_anaglyph(left_view, right_view)
                elif args.format == "top_bottom":
                    output = composer.compose_top_bottom(left_view, right_view, half=True)
                
                # Save
                output_path = output_dir / file_path.name
                output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
                cv2.imwrite(str(output_path), output_bgr)
                
                success_count += 1
                logger.info(f"✓ Saved: {output_path}")
                
            except Exception as e:
                logger.error(f"✗ Failed to convert {file_path.name}: {e}")
                continue
        
        logger.info(f"\n✅ Batch conversion complete: {success_count}/{len(files)} successful")
        return 0 if success_count > 0 else 1
    
    else:
        logger.error("Input must be a directory or video file")
        return 1


def show_info(logger: logging.Logger) -> int:
    """Show system information"""
    import platform
    import torch
    from src.version import __version__, get_version_string
    
    logger.info("=== System Information ===")
    logger.info(f"2D3D Converter: {get_version_string()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"PyTorch: {torch.__version__}")
    
    # GPU information
    if torch.cuda.is_available():
        logger.info(f"CUDA: {torch.version.cuda}")
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        logger.info("GPU: Apple Metal Performance Shaders (MPS)")
    else:
        logger.info("GPU: Not available (CPU only)")
    
    return 0


def preview_frame(args: Any, logger: logging.Logger) -> int:
    """Preview single frame conversion"""
    logger.info(f"Previewing: {args.input}")
    logger.info(f"Frame: {args.frame}")
    
    # TODO: Implement preview
    logger.warning("Preview not yet implemented - placeholder")
    
    return 0
