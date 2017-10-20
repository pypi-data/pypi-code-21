from os.path import abspath, dirname
import sys

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpimage  # noqa: E402
import qpimage.image_data  # noqa: E402


def test_set_bg():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))

    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")
    pha = qpi.pha
    clspha = qpi._pha
    assert np.all(pha == clspha.image)
    clspha.set_bg(None, key="data")
    assert not np.all(pha == clspha.image)


def test_get_bg():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))

    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")
    bgpha = qpi.bg_pha
    clspha = qpi._pha
    assert np.all(bgpha == clspha.bg)
    assert np.all(bgpha == clspha.get_bg(key=None))


def test_get_bg_error():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))

    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")
    clspha = qpi._pha
    try:
        clspha.get_bg(key=None, ret_attrs=True)
    except ValueError:
        pass
    else:
        assert False, "attrs of combined bg not supported"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
