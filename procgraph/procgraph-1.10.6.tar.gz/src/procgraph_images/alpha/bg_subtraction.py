from procgraph import simple_block
from contracts import contract
import numpy as np


@simple_block
@contract(image='array[HxWx(3|4)]', bg='array[HxWx(3|4)]')
def bg_subtract(image, bg, perc=99, weighted=False):
    image_rbg = image[:, :, 0:3]
    bg_rgb = bg[:, :, 0:3]
    # pointwise difference
    error = image_diff(image_rbg, bg_rgb)
    
    threshold = np.percentile(error, perc)
    mask_robot = error > threshold
    mask_env = np.logical_not(mask_robot)

    H, W = image.shape[0:2]
    rgba = np.zeros((H, W, 4), 'uint8')
    rgba[:, :, 0] = image[:, :, 0]
    rgba[:, :, 1] = image[:, :, 1]
    rgba[:, :, 2] = image[:, :, 2]
    
     
    if weighted:
        error -= threshold
        min_alpha = 100
        alpha = min_alpha + (255 - min_alpha) * (error / error.max())
        alpha[mask_env] = 0
        rgba[..., 3] = alpha
    else:
        rgba[mask_env, 3] = 0
        rgba[mask_robot, 3] = 255

    return rgba
 


def image_diff(a, b):
    return np.mean(np.abs(a.astype('float32') - b.astype('float32')), axis=2)
