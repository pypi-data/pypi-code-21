import numpy as np

import cpyImagingMSpec.utils as utils
ffi = utils.init_ffi()
_ims = utils.load_shared_lib()

def _compute_metric(metric, images_flat, theor_iso_intensities):
    assert len(images_flat) == len(theor_iso_intensities)
    assert all(np.shape(im) == np.shape(images_flat[0]) for im in images_flat)
    assert all(len(np.shape(im)) == 1 for im in images_flat)
    assert all(intensity >= 0 for intensity in theor_iso_intensities)

    n = len(images_flat)
    images = ffi.new("float*[]", n)
    buffers = [utils.cffi_buffer(im, 'f') for im in images_flat]
    for i, im in enumerate(images_flat):
        images[i] = buffers[i].ptr
    abundances = utils.cffi_buffer(theor_iso_intensities, 'd')

    return metric(images,
                  ffi.cast("int", n),
                  ffi.cast("int", len(images_flat[0])),
                  ffi.cast("int", 1),
                  abundances.ptr)

def isotope_image_correlation(images_flat, weights=None):
    """
    Calculates weighted average of correlations between principal peak image and the rest.

    :param images_flat: list of flattened isotope images
    :param weights: If provided, must be one element shorter than :code:`images_flat` list.
                    Default value of :code:`None` corresponds to equal weights.
    :rtype: float
    """
    if weights is None:
        weights = np.ones(len(images_flat))
    else:
        weights = np.concatenate(([1.0], weights))
    return _compute_metric(_ims.iso_img_correlation_f, images_flat, weights)

def isotope_pattern_match(images_flat, theor_iso_intensities):
    """
    Measures similarity between total isotope image intensities and the theoretical pattern.

    :param images_flat: list of flattened isotope images
    :param theor_iso_intensities: list of the corresponding theoretical isotope abundances
    :rtype: float
    """
    return _compute_metric(_ims.pattern_match_f, images_flat, theor_iso_intensities)

def measure_of_chaos(im, nlevels):
    """
    Compute a measure for the spatial chaos in given image using the level sets method.

    :param im: 2d array
    :param nlevels: how many levels to use (maximum of 32 in this implementation)
    :type nlevels: int
    """
    assert nlevels > 0
    if nlevels > 32:
        raise RuntimeError("maximum of 32 levels is supported")
    im = utils.cffi_buffer(im, 'f')
    return _ims.measure_of_chaos_f(im.ptr,
                                   ffi.cast("int", im.buf.shape[1]),
                                   ffi.cast("int", im.buf.shape[0]),
                                   ffi.cast("int", nlevels))
