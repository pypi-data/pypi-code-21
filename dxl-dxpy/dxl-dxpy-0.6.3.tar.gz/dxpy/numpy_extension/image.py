import numpy as np
from . import tensor as te


def try_unbatch(images):
    if isinstance(images, np.ndarray) and images.ndim == 4:
        return te.unbatch(images)
    return images


def fix_dim(image):
    if image.ndim == 3 and image.shape[-1] == 1:
        return np.reshape(image, image.shape[:-1])
    return image
