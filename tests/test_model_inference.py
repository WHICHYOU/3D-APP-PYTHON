# Quick test: load DepthEstimator and run inference on a synthetic image
import numpy as np
from src.ai_core.depth_estimation import DepthEstimator

print('Starting quick model inference test...')
# Create a simple gradient RGB image (256x256)
img = np.tile(np.linspace(0, 255, 256, dtype=np.uint8), (256, 1))
img_rgb = np.stack([img, img, img], axis=2)

est = DepthEstimator()
print('Model loaded; running estimate_depth...')
d = est.estimate_depth(img_rgb, normalize=True)
print('Depth map stats: shape=%s, min=%.4f, max=%.4f, mean=%.4f' % (str(d.shape), float(d.min()), float(d.max()), float(d.mean())))

# Basic sanity checks
if d is None:
    print('ERROR: estimate_depth returned None')
    raise SystemExit(2)

if d.shape[0] == 0:
    print('ERROR: empty depth map')
    raise SystemExit(3)

print('Inference test completed successfully.')
