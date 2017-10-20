import lmfit
import numpy as np

VALID_FIT_OFFSETS = ["fit", "gauss", "mean", "mode"]
VALID_FIT_PROFILES = ["ramp", "offset"]


def estimate(data, fit_offset="average", fit_profile="ramp",
             border_px=0, from_binary=None, ret_binary=False):
    """Estimate the background value of an image

    Parameters
    ----------
    data: np.ndarray
        Data from which to compute the background value
    fit_profile: str
        The type of background profile to fit:
          - "ramp": 2D linear ramp with offset (default)
          - "offset": offset only
    fit_offset: str
        The method for computing the profile offset
          - "fit": offset as fitting parameter
          - "gauss": center of a gaussian fit
          - "mean": simple average
          - "mode": mode (see `qpimage.bg_estimate.mode`)
    border_px: float
        Assume that a frame of `border_px` pixels around
        the image is background.
    from_binary: boolean np.ndarray or None
        Use a boolean array to define the background area.
        The binary image must have the same shape as the
        input data.
    ret_binary: bool
        Return the binary image used to compute the background.

    Notes
    -----
    If both `border_px` and `from_binary` are given, the
    intersection of the two resulting binary images is used.
    """
    if fit_profile not in VALID_FIT_PROFILES:
        msg = "`fit_profile` must be one of {}".format(VALID_FIT_PROFILES)
        raise ValueError(msg)
    if fit_offset not in VALID_FIT_OFFSETS:
        msg = "`fit_offset` must be one of {}".format(VALID_FIT_OFFSETS)
        raise ValueError(msg)
    # initial binary image
    if from_binary is not None:
        assert isinstance(from_binary, np.ndarray)
        binary = from_binary.copy()
    else:
        binary = np.zeros_like(data, dtype=bool)
    # multiply with border binary image (intersection)
    if border_px > 0:
        border_px = int(np.round(border_px))
        binary_px = np.zeros_like(binary)
        binary_px[:border_px, :] = True
        binary_px[-border_px:, :] = True
        binary_px[:, :border_px] = True
        binary_px[:, -border_px:] = True
        np.logical_or(binary, binary_px, out=binary)
    # compute background image
    if fit_profile == "ramp":
        bgimg = profile_ramp(data, binary)
    else:
        bgimg = np.zeros_like(data, dtype=float)
    # add offsets
    if fit_offset == "fit":
        if fit_profile == "offset":
            msg = "`fit_offset=='fit'` only valid when `fit_profile!='offset`"
            raise ValueError(msg)
        # nothing else to do here, using offset from fit
    elif fit_offset == "gauss":
        bgimg += offset_gaussian((data - bgimg)[binary])
    elif fit_offset == "mean":
        bgimg += np.mean((data - bgimg)[binary])
    elif fit_offset == "mode":
        bgimg += offset_mode((data - bgimg)[binary])

    if ret_binary:
        ret = (bgimg, binary)
    else:
        ret = bgimg
    return ret


def offset_gaussian(data):
    nbins = 2 * int(np.ceil(np.sqrt(data.size)))
    mind, maxd = data.min(), data.max()
    drange = (mind - (maxd - mind) / 2, maxd + (maxd - mind) / 2)
    histo = np.histogram(data, nbins, density=True, range=drange)
    dx = abs(histo[1][1] - histo[1][2]) / 2
    hx = histo[1][1:] - dx
    hy = histo[0]
    # fit gaussian
    gauss = lmfit.models.GaussianModel()
    pars = gauss.guess(hy, x=hx)
    out = gauss.fit(hy, pars, x=hx)
    return out.params["center"]


def offset_mode(data):
    """Compute mode of data using small number of bins
    """
    nbins = int(np.ceil(np.sqrt(data.size)))
    mind, maxd = data.min(), data.max()
    histo = np.histogram(data, nbins, density=True, range=(mind, maxd))
    dx = abs(histo[1][1] - histo[1][2]) / 2
    hx = histo[1][1:] - dx
    hy = histo[0]
    idmax = np.argmax(hy)
    return hx[idmax]


def profile_ramp(data, binary):
    params = lmfit.Parameters()
    params.add(name="mx", value=0)
    params.add(name="my", value=0)
    params.add(name="off", value=np.average(data[binary]))
    fr = lmfit.minimize(ramp_residual, params, args=(data, binary))
    bg = ramp_model(fr.params, data.shape)
    return bg


def ramp_model(params, shape):
    mx = params["mx"].value
    my = params["my"].value
    off = params["off"].value
    bg = np.zeros(shape, dtype=float) + off
    x = np.arange(bg.shape[0]) - bg.shape[0] // 2
    y = np.arange(bg.shape[1]) - bg.shape[1] // 2
    x = x.reshape(-1, 1)
    y = y.reshape(1, -1)
    bg += mx * x + my * y
    return bg


def ramp_residual(params, data, binary):
    bg = ramp_model(params, shape=data.shape)
    res = (data - bg)[binary]
    return res.flatten()
