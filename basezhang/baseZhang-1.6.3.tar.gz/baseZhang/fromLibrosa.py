import linecache
import os
import re
import sys

import audioread
import numpy
import numpy as np
import resampy
import scipy
import six
from numpy.lib.stride_tricks import as_strided
from scipy.fftpack import _fftpack
from scipy.fftpack.basic import _fake_cfft
from scipy.ndimage import median_filter

MAX_MEM_BLOCK = 2 ** 8 * 2 ** 10
WINDOW_BANDWIDTHS = {'bart': 1.3334961334912805,
                     'barthann': 1.4560255965133932,
                     'bartlett': 1.3334961334912805,
                     'bkh': 2.0045975283585014,
                     'black': 1.7269681554262326,
                     'blackharr': 2.0045975283585014,
                     'blackman': 1.7269681554262326,
                     'blackmanharris': 2.0045975283585014,
                     'blk': 1.7269681554262326,
                     'bman': 1.7859588613860062,
                     'bmn': 1.7859588613860062,
                     'bohman': 1.7859588613860062,
                     'box': 1.0,
                     'boxcar': 1.0,
                     'brt': 1.3334961334912805,
                     'brthan': 1.4560255965133932,
                     'bth': 1.4560255965133932,
                     'cosine': 1.2337005350199792,
                     'flat': 2.7762255046484143,
                     'flattop': 2.7762255046484143,
                     'flt': 2.7762255046484143,
                     'halfcosine': 1.2337005350199792,
                     'ham': 1.3629455320350348,
                     'hamm': 1.3629455320350348,
                     'hamming': 1.3629455320350348,
                     'han': 1.50018310546875,
                     'hann': 1.50018310546875,
                     'hanning': 1.50018310546875,
                     'nut': 1.9763500280946082,
                     'nutl': 1.9763500280946082,
                     'nuttall': 1.9763500280946082,
                     'ones': 1.0,
                     'par': 1.9174603174603191,
                     'parz': 1.9174603174603191,
                     'parzen': 1.9174603174603191,
                     'rect': 1.0,
                     'rectangular': 1.0,
                     'tri': 1.3331706523555851,
                     'triang': 1.3331706523555851,
                     'triangle': 1.3331706523555851}
BW_BEST = resampy.filters.get_filter('kaiser_best')[2]
BW_FASTEST = resampy.filters.get_filter('kaiser_fast')[2]


def _is_safe_size(n):
    """
    Is the size of FFT such that FFTPACK can handle it in single precision
    with sufficient accuracy?

    Composite numbers of 2, 3, and 5 are accepted, as FFTPACK has those
    """
    n = int(n)

    if n == 0:
        return True

    # Divide by 3 until you can't, then by 5 until you can't
    for c in (3, 5):
        while n % c == 0:
            n //= c

    # Return True if the remainder is a power of 2
    return not n & (n - 1)


def _fake_crfft(x, n, *a, **kw):
    if _is_safe_size(n):
        return _fftpack.crfft(x, n, *a, **kw)
    else:
        return _fftpack.zrfft(x, n, *a, **kw).astype(numpy.complex64)


_DTYPE_TO_FFT = {
    #        numpy.dtype(numpy.float32): _fftpack.crfft,
    numpy.dtype(numpy.float32): _fake_crfft,
    numpy.dtype(numpy.float64): _fftpack.zrfft,
    #        numpy.dtype(numpy.complex64): _fftpack.cfft,
    numpy.dtype(numpy.complex64): _fake_cfft,
    numpy.dtype(numpy.complex128): _fftpack.zfft,
}


class LibrosaError(Exception):
    '''The root librosa exception class'''
    pass


class ParameterError(LibrosaError):
    '''Exception class for mal-formed inputs'''
    pass


def valid_audio(y, mono=True):

    if not isinstance(y, np.ndarray):
        raise ParameterError('data must be of type numpy.ndarray')

    if mono and y.ndim != 1:
        raise ParameterError('Invalid shape for monophonic audio: '
                             'ndim={:d}, shape={}'.format(y.ndim, y.shape))
    elif y.ndim > 2:
        raise ParameterError('Invalid shape for audio: '
                             'ndim={:d}, shape={}'.format(y.ndim, y.shape))

    if not np.isfinite(y).all():
        raise ParameterError('Audio buffer is not finite everywhere')

    return True


def to_mono(y):

    # Validate the buffer.  Stereo is ok here.
    valid_audio(y, mono=False)

    if y.ndim > 1:
        y = np.mean(y, axis=0)

    return y


def buf_to_float(x, n_bytes=2, dtype=np.float32):
    """Convert an integer buffer to floating point values.
    This is primarily useful when loading integer-valued wav data
    into numpy arrays.

    See Also
    --------
    buf_to_float

    Parameters
    ----------
    x : np.ndarray [dtype=int]
        The integer-valued data buffer

    n_bytes : int [1, 2, 4]
        The number of bytes per sample in `x`

    dtype : numeric type
        The target output type (default: 32-bit float)

    Returns
    -------
    x_float : np.ndarray [dtype=float]
        The input data buffer cast to floating point
    """

    # Invert the scale of the data
    scale = 1. / float(1 << ((8 * n_bytes) - 1))

    # Construct the format string
    fmt = '<i{:d}'.format(n_bytes)

    # Rescale and format the data buffer
    return scale * np.frombuffer(x, fmt).astype(dtype)


def fix_length(data, size, axis=-1, **kwargs):

    kwargs.setdefault('mode', 'constant')

    n = data.shape[axis]

    if n > size:
        slices = [slice(None)] * data.ndim
        slices[axis] = slice(0, size)
        return data[slices]

    elif n < size:
        lengths = [(0, 0)] * data.ndim
        lengths[axis] = (0, size - n)
        return np.pad(data, lengths, **kwargs)

    return data


def resample(y, orig_sr, target_sr, res_type='kaiser_best', fix=True, scale=False, **kwargs):
    # First, validate the audio buffer
    valid_audio(y, mono=False)

    if orig_sr == target_sr:
        return y

    ratio = float(target_sr) / orig_sr

    n_samples = int(np.ceil(y.shape[-1] * ratio))

    if res_type == 'scipy':
        y_hat = scipy.signal.resample(y, n_samples, axis=-1)
    else:
        y_hat = resampy.resample(y, orig_sr, target_sr, filter=res_type, axis=-1)

    if fix:
        y_hat = fix_length(y_hat, n_samples, **kwargs)

    if scale:
        y_hat /= np.sqrt(ratio)

    return np.ascontiguousarray(y_hat, dtype=y.dtype)


def load(path, sr=22050, mono=True, offset=0.0, duration=None,
         dtype=np.float32, res_type='kaiser_best'):
    y = []
    with audioread.audio_open(os.path.realpath(path)) as input_file:
        sr_native = input_file.samplerate
        n_channels = input_file.channels

        s_start = int(np.round(sr_native * offset)) * n_channels

        if duration is None:
            s_end = np.inf
        else:
            s_end = s_start + (int(np.round(sr_native * duration))
                               * n_channels)

        n = 0

        for frame in input_file:
            frame = buf_to_float(frame, dtype=dtype)
            n_prev = n
            n = n + len(frame)

            if n < s_start:
                # offset is after the current frame
                # keep reading
                continue

            if s_end < n_prev:
                # we're off the end.  stop reading
                break

            if s_end < n:
                # the end is in this frame.  crop.
                frame = frame[:s_end - n_prev]

            if n_prev <= s_start <= n:
                # beginning is in this frame
                frame = frame[(s_start - n_prev):]

            # tack on the current frame
            y.append(frame)

    if y:
        y = np.concatenate(y)

        if n_channels > 1:
            y = y.reshape((-1, 2)).T
            if mono:
                y = to_mono(y)

        if sr is not None:
            y = resample(y, sr_native, sr, res_type=res_type)

        else:
            sr = sr_native

    # Final cleanup for dtype and contiguity
    y = np.ascontiguousarray(y, dtype=dtype)

    return (y, sr)


def get_window(window, Nx, fftbins=True):

    if six.callable(window):
        return window(Nx)

    elif (isinstance(window, (six.string_types, tuple)) or
              np.isscalar(window)):
        # TODO: if we add custom window functions in librosa, call them here

        return scipy.signal.get_window(window, Nx, fftbins=fftbins)

    elif isinstance(window, (np.ndarray, list)):
        if len(window) == Nx:
            return np.asarray(window)

        raise ParameterError('Window size mismatch: '
                             '{:d} != {:d}'.format(len(window), Nx))
    else:
        raise ParameterError('Invalid window specification: {}'.format(window))


def pad_center(data, size, axis=-1, **kwargs):

    kwargs.setdefault('mode', 'constant')

    n = data.shape[axis]

    lpad = int((size - n) // 2)

    lengths = [(0, 0)] * data.ndim
    lengths[axis] = (lpad, int(size - n - lpad))

    if lpad < 0:
        raise ParameterError(('Target size ({:d}) must be '
                              'at least input size ({:d})').format(size, n))

    return np.pad(data, lengths, **kwargs)


def frame(y, frame_length=2048, hop_length=512):
    if len(y) < frame_length:
        raise ParameterError('Buffer is too short (n={:d})'
                             ' for frame_length={:d}'.format(len(y), frame_length))

    if hop_length < 1:
        raise ParameterError('Invalid hop_length: {:d}'.format(hop_length))

    if not y.flags['C_CONTIGUOUS']:
        raise ParameterError('Input buffer must be contiguous.')

    valid_audio(y)

    # Compute the number of frames that will fit. The end may get truncated.
    n_frames = 1 + int((len(y) - frame_length) / hop_length)

    # Vertical stride is one sample
    # Horizontal stride is `hop_length` samples
    y_frames = as_strided(y, shape=(frame_length, n_frames),
                          strides=(y.itemsize, hop_length * y.itemsize))
    return y_frames


def _asfarray(x):
    """Like numpy asfarray, except that it does not modify x dtype if x is
    already an array with a float dtype, and do not cast complex types to
    real."""
    if hasattr(x, "dtype") and x.dtype.char in numpy.typecodes["AllFloat"]:
        # 'dtype' attribute does not ensure that the
        # object is an ndarray (e.g. Series class
        # from the pandas library)
        if x.dtype == numpy.half:
            # no half-precision routines, so convert to single precision
            return numpy.asarray(x, dtype=numpy.float32)
        return numpy.asarray(x, dtype=x.dtype)
    else:
        # We cannot use asfarray directly because it converts sequences of
        # complex to sequence of real
        ret = numpy.asarray(x)
        if ret.dtype == numpy.half:
            return numpy.asarray(ret, dtype=numpy.float32)
        elif ret.dtype.char not in numpy.typecodes["AllFloat"]:
            return numpy.asfarray(x)
        return ret


def istype(arr, typeclass):
    return issubclass(arr.dtype.type, typeclass)


def _datacopied(arr, original):
    """
    Strict check for `arr` not sharing any data with `original`,
    under the assumption that arr = asarray(original)

    """
    if arr is original:
        return False
    if not isinstance(original, numpy.ndarray) and hasattr(original, '__array__'):
        return False
    return arr.base is None


def _fix_shape(x, n, axis):
    """ Internal auxiliary function for _raw_fft, _raw_fftnd."""
    s = list(x.shape)
    if s[axis] > n:
        index = [slice(None)] * len(s)
        index[axis] = slice(0, n)
        x = x[index]
        return x, False
    else:
        index = [slice(None)] * len(s)
        index[axis] = slice(0, s[axis])
        s[axis] = n
        z = np.zeros(s, x.dtype.char)
        z[index] = x
        return z, True


def fft(x, n=None, axis=-1, overwrite_x=False):
    tmp = _asfarray(x)

    try:
        work_function = _DTYPE_TO_FFT[tmp.dtype]
    except KeyError:
        raise ValueError("type %s is not supported" % tmp.dtype)

    if not (istype(tmp, numpy.complex64) or istype(tmp, numpy.complex128)):
        overwrite_x = 1

    overwrite_x = overwrite_x or _datacopied(tmp, x)

    if n is None:
        n = tmp.shape[axis]
    elif n != tmp.shape[axis]:
        tmp, copy_made = _fix_shape(tmp, n, axis)
        overwrite_x = overwrite_x or copy_made

    if n < 1:
        raise ValueError("Invalid number of FFT data points "
                         "(%d) specified." % n)

    if axis == -1 or axis == len(tmp.shape) - 1:
        return work_function(tmp, n, 1, 0, overwrite_x)

    tmp = numpy.swapaxes(tmp, axis, -1)
    tmp = work_function(tmp, n, 1, 0, overwrite_x)
    return numpy.swapaxes(tmp, axis, -1)


def _spectrogram(y=None, S=None, n_fft=2048, hop_length=512, power=1):
    if S is not None:
        # Infer n_fft from spectrogram shape
        n_fft = 2 * (S.shape[0] - 1)
    else:
        # Otherwise, compute a magnitude spectrogram from input
        S = np.abs(stft(y, n_fft=n_fft, hop_length=hop_length)) ** power

    return S, n_fft


def fft_frequencies(sr=22050, n_fft=2048):
    return np.linspace(0,
                       float(sr) / 2,
                       int(1 + n_fft // 2),
                       endpoint=True)


def localmax(x, axis=0):
    """Find local maxima in an array `x`.

    Examples
    --------
    >>> x = np.array([1, 0, 1, 2, -1, 0, -2, 1])
    >>> librosa.localmax(x)
    array([False, False, False,  True, False,  True, False,  True], dtype=bool)

    >>> # Two-dimensional example
    >>> x = np.array([[1,0,1], [2, -1, 0], [2, 1, 3]])
    >>> librosa.localmax(x, axis=0)
    array([[False, False, False],
           [ True, False, False],
           [False,  True,  True]], dtype=bool)
    >>> librosa.localmax(x, axis=1)
    array([[False, False,  True],
           [False, False,  True],
           [False, False,  True]], dtype=bool)

    Parameters
    ----------
    x     : np.ndarray [shape=(d1,d2,...)]
      input vector or array

    axis : int
      axis along which to compute local maximality

    Returns
    -------
    m     : np.ndarray [shape=x.shape, dtype=bool]
        indicator array of local maximality along `axis`

    """

    paddings = [(0, 0)] * x.ndim
    paddings[axis] = (1, 1)

    x_pad = np.pad(x, paddings, mode='edge')

    inds1 = [slice(None)] * x.ndim
    inds1[axis] = slice(0, -2)

    inds2 = [slice(None)] * x.ndim
    inds2[axis] = slice(2, x_pad.shape[axis])

    return (x > x_pad[inds1]) & (x >= x_pad[inds2])


def piptrack(y=None, sr=22050, S=None, n_fft=2048, hop_length=None,
             fmin=150.0, fmax=4000.0, threshold=0.1):

    # Check that we received an audio time series or STFT
    if hop_length is None:
        hop_length = int(n_fft // 4)

    S, n_fft = _spectrogram(y=y, S=S, n_fft=n_fft, hop_length=hop_length)

    # Make sure we're dealing with magnitudes
    S = np.abs(S)

    # Truncate to feasible region
    fmin = np.maximum(fmin, 0)
    fmax = np.minimum(fmax, float(sr) / 2)

    fft_freqs = fft_frequencies(sr=sr, n_fft=n_fft)

    # Do the parabolic interpolation everywhere,
    # then figure out where the peaks are
    # then restrict to the feasible range (fmin:fmax)
    avg = 0.5 * (S[2:] - S[:-2])

    shift = 2 * S[1:-1] - S[2:] - S[:-2]

    # Suppress divide-by-zeros.
    # Points where shift == 0 will never be selected by localmax anyway
    shift = avg / (shift + (np.abs(shift) < tiny(shift)))

    # Pad back up to the same shape as S
    avg = np.pad(avg, ([1, 1], [0, 0]), mode='constant')
    shift = np.pad(shift, ([1, 1], [0, 0]), mode='constant')

    dskew = 0.5 * avg * shift

    # Pre-allocate output
    pitches = np.zeros_like(S)
    mags = np.zeros_like(S)

    # Clip to the viable frequency range
    freq_mask = ((fmin <= fft_freqs) & (fft_freqs < fmax)).reshape((-1, 1))

    # Compute the column-wise local max of S after thresholding
    # Find the argmax coordinates
    idx = np.argwhere(freq_mask &
                      localmax(S * (S > (threshold * S.max(axis=0)))))

    # Store pitch and magnitude
    pitches[idx[:, 0], idx[:, 1]] = ((idx[:, 0] + shift[idx[:, 0], idx[:, 1]])
                                     * float(sr) / n_fft)

    mags[idx[:, 0], idx[:, 1]] = (S[idx[:, 0], idx[:, 1]]
                                  + dskew[idx[:, 0], idx[:, 1]])

    return pitches, mags


def hz_to_octs(frequencies, A440=440.0):
    return np.log2(np.atleast_1d(frequencies) / (float(A440) / 16))


def pitch_tuning(frequencies, resolution=0.01, bins_per_octave=12):

    frequencies = np.atleast_1d(frequencies)

    # Trim out any DC components
    frequencies = frequencies[frequencies > 0]

    if not np.any(frequencies):
        scipy.warnings.warn('Trying to estimate tuning from empty frequency set.')
        return 0.0

    # Compute the residual relative to the number of bins
    residual = np.mod(bins_per_octave *
                      hz_to_octs(frequencies), 1.0)

    # Are we on the wrong side of the semitone?
    # A residual of 0.95 is more likely to be a deviation of -0.05
    # from the next tone up.
    residual[residual >= 0.5] -= 1.0

    bins = np.linspace(-0.5, 0.5, int(np.ceil(1. / resolution)), endpoint=False)

    counts, tuning = np.histogram(residual, bins)

    # return the histogram peak
    return tuning[np.argmax(counts)]


def estimate_tuning(y=None, sr=22050, S=None, n_fft=2048,
                    resolution=0.01, bins_per_octave=12, **kwargs):
    pitch, mag = piptrack(y=y, sr=sr, S=S, n_fft=n_fft, **kwargs)

    # Only count magnitude where frequency is > 0
    pitch_mask = pitch > 0

    if pitch_mask.any():
        threshold = np.median(mag[pitch_mask])
    else:
        threshold = 0.0

    return pitch_tuning(pitch[(mag >= threshold) & pitch_mask],
                        resolution=resolution,
                        bins_per_octave=bins_per_octave)


def tiny(x):
    # Make sure we have an array view
    x = np.asarray(x)

    # Only floating types generate a tiny
    if np.issubdtype(x.dtype, float) or np.issubdtype(x.dtype, complex):
        dtype = x.dtype
    else:
        dtype = np.float32

    return np.finfo(dtype).tiny


def normalize(S, norm=np.inf, axis=0, threshold=None, fill=None):
    # Avoid div-by-zero
    if threshold is None:
        threshold = tiny(S)

    elif threshold <= 0:
        raise ParameterError('threshold={} must be strictly '
                             'positive'.format(threshold))

    if fill not in [None, False, True]:
        raise ParameterError('fill={} must be None or boolean'.format(fill))

    if not np.all(np.isfinite(S)):
        raise ParameterError('Input must be finite')

    # All norms only depend on magnitude, let's do that first
    mag = np.abs(S).astype(np.float)

    # For max/min norms, filling with 1 works
    fill_norm = 1

    if norm == np.inf:
        length = np.max(mag, axis=axis, keepdims=True)

    elif norm == -np.inf:
        length = np.min(mag, axis=axis, keepdims=True)

    elif norm == 0:
        if fill is True:
            raise ParameterError('Cannot normalize with norm=0 and fill=True')

        length = np.sum(mag > 0, axis=axis, keepdims=True, dtype=mag.dtype)

    elif np.issubdtype(type(norm), np.number) and norm > 0:
        length = np.sum(mag ** norm, axis=axis, keepdims=True) ** (1. / norm)

        if axis is None:
            fill_norm = mag.size ** (-1. / norm)
        else:
            fill_norm = mag.shape[axis] ** (-1. / norm)

    elif norm is None:
        return S

    else:
        raise ParameterError('Unsupported norm: {}'.format(repr(norm)))

    # indices where norm is below the threshold
    small_idx = length < threshold

    if fill is None:
        # Leave small indices un-normalized
        length[small_idx] = 1.0
        Snorm = S / length

    elif fill:
        # If we have a non-zero fill value, we locate those entries by
        # doing a nan-divide.
        # If S was finite, then length is finite (except for small positions)
        length[small_idx] = np.nan
        Snorm = S / length
        Snorm[np.isnan(Snorm)] = fill_norm
    else:
        # Set small values to zero by doing an inf-divide.
        # This is safe (by IEEE-754) as long as S is finite.
        length[small_idx] = np.inf
        Snorm = S / length

    return Snorm


def chroma(sr, n_fft, n_chroma=12, A440=440.0, ctroct=5.0,
           octwidth=2, norm=2, base_c=True):
    wts = np.zeros((n_chroma, n_fft))

    # Get the FFT bins, not counting the DC component
    frequencies = np.linspace(0, sr, n_fft, endpoint=False)[1:]

    frqbins = n_chroma * hz_to_octs(frequencies, A440)

    # make up a value for the 0 Hz bin = 1.5 octaves below bin 1
    # (so chroma is 50% rotated from bin 1, and bin width is broad)
    frqbins = np.concatenate(([frqbins[0] - 1.5 * n_chroma], frqbins))

    binwidthbins = np.concatenate((np.maximum(frqbins[1:] - frqbins[:-1],
                                              1.0), [1]))

    D = np.subtract.outer(frqbins, np.arange(0, n_chroma, dtype='d')).T

    n_chroma2 = np.round(float(n_chroma) / 2)

    # Project into range -n_chroma/2 .. n_chroma/2
    # add on fixed offset of 10*n_chroma to ensure all values passed to
    # rem are positive
    D = np.remainder(D + n_chroma2 + 10 * n_chroma, n_chroma) - n_chroma2

    # Gaussian bumps - 2*D to make them narrower
    wts = np.exp(-0.5 * (2 * D / np.tile(binwidthbins, (n_chroma, 1))) ** 2)

    # normalize each column
    wts = normalize(wts, norm=norm, axis=0)

    # Maybe apply scaling for fft bins
    if octwidth is not None:
        wts *= np.tile(
            np.exp(-0.5 * (((frqbins / n_chroma - ctroct) / octwidth) ** 2)),
            (n_chroma, 1))

    if base_c:
        wts = np.roll(wts, -3, axis=0)

    # remove aliasing columns, copy to ensure row-contiguity
    return np.ascontiguousarray(wts[:, :int(1 + n_fft / 2)])


def chroma_stft(y=None, sr=22050, S=None, norm=np.inf, n_fft=2048,
                hop_length=512, tuning=None, **kwargs):

    S, n_fft = _spectrogram(y=y, S=S, n_fft=n_fft, hop_length=hop_length,
                            power=2)

    n_chroma = kwargs.get('n_chroma', 12)

    if tuning is None:
        tuning = estimate_tuning(S=S, sr=sr, bins_per_octave=n_chroma)

    # Get the filter bank
    if 'A440' not in kwargs:
        kwargs['A440'] = 440.0 * 2.0 ** (float(tuning) / n_chroma)

    chromafb = chroma(sr, n_fft, **kwargs)

    # Compute raw chroma
    raw_chroma = np.dot(chromafb, S)

    # Compute normalization factor for each frame
    return normalize(raw_chroma, norm=norm, axis=0)


class Deprecated(object):
    '''A dummy class to catch usage of deprecated variable names'''

    def __repr__(self):
        return '<DEPRECATED parameter>'


def hz_to_midi(frequencies):
    return 12 * (np.log2(np.atleast_1d(frequencies)) - np.log2(440.0)) + 69


def hz_to_note(frequencies, **kwargs):
    return midi_to_note(hz_to_midi(frequencies), **kwargs)


def hz_to_mel(frequencies, htk=False):
    frequencies = np.atleast_1d(frequencies)

    if htk:
        return 2595.0 * np.log10(1.0 + frequencies / 700.0)

    # Fill in the linear part
    f_min = 0.0
    f_sp = 200.0 / 3

    mels = (frequencies - f_min) / f_sp

    # Fill in the log-scale part

    min_log_hz = 1000.0  # beginning of log region (Hz)
    min_log_mel = (min_log_hz - f_min) / f_sp  # same (Mels)
    logstep = np.log(6.4) / 27.0  # step size for log region

    log_t = (frequencies >= min_log_hz)
    mels[log_t] = min_log_mel + np.log(frequencies[log_t] / min_log_hz) / logstep

    return mels


def mel_to_hz(mels, htk=False):
    mels = np.atleast_1d(mels)

    if htk:
        return 700.0 * (10.0 ** (mels / 2595.0) - 1.0)

    # Fill in the linear scale
    f_min = 0.0
    f_sp = 200.0 / 3
    freqs = f_min + f_sp * mels

    # And now the nonlinear scale
    min_log_hz = 1000.0  # beginning of log region (Hz)
    min_log_mel = (min_log_hz - f_min) / f_sp  # same (Mels)
    logstep = np.log(6.4) / 27.0  # step size for log region
    log_t = (mels >= min_log_mel)

    freqs[log_t] = min_log_hz * np.exp(logstep * (mels[log_t] - min_log_mel))

    return freqs


def midi_to_note(midi, octave=True, cents=False):
    if cents and not octave:
        raise ParameterError('Cannot encode cents without octave information.')

    if not np.isscalar(midi):
        return [midi_to_note(x, octave=octave, cents=cents) for x in midi]

    note_map = ['C', 'C#', 'D', 'D#',
                'E', 'F', 'F#', 'G',
                'G#', 'A', 'A#', 'B']

    note_num = int(np.round(midi))
    note_cents = int(100 * np.around(midi - note_num, 2))

    note = note_map[note_num % 12]

    if octave:
        note = '{:s}{:0d}'.format(note, int(note_num / 12) - 1)
    if cents:
        note = '{:s}{:+02d}'.format(note, note_cents)

    return note


def note_to_midi(note, round_midi=True):
    if not isinstance(note, six.string_types):
        return np.array([note_to_midi(n, round_midi=round_midi) for n in note])

    pitch_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    acc_map = {'#': 1, '': 0, 'b': -1, '!': -1}

    match = re.match(r'^(?P<note>[A-Ga-g])'
                     r'(?P<accidental>[#b!]*)'
                     r'(?P<octave>[+-]?\d+)?'
                     r'(?P<cents>[+-]\d+)?$',
                     note)
    if not match:
        raise ParameterError('Improper note format: {:s}'.format(note))

    pitch = match.group('note').upper()
    offset = np.sum([acc_map[o] for o in match.group('accidental')])
    octave = match.group('octave')
    cents = match.group('cents')

    if not octave:
        octave = 0
    else:
        octave = int(octave)

    if not cents:
        cents = 0
    else:
        cents = int(cents) * 1e-2

    note_value = 12 * (octave + 1) + pitch_map[pitch] + offset + cents

    if round_midi:
        note_value = int(np.round(note_value))

    return note_value


def midi_to_hz(notes):
    return 440.0 * (2.0 ** ((np.atleast_1d(notes) - 69.0) / 12.0))


def octs_to_hz(octs, A440=440.0):
    """Convert octaves numbers to frequencies.

    Octaves are counted relative to A.

    Examples
    --------
    >>> librosa.octs_to_hz(1)
    array([ 55.])
    >>> librosa.octs_to_hz([-2, -1, 0, 1, 2])
    array([   6.875,   13.75 ,   27.5  ,   55.   ,  110.   ])

    Parameters
    ----------
    octaves       : np.ndarray [shape=(n,)] or float
        octave number for each frequency
    A440          : float
        frequency of A440

    Returns
    -------
    frequencies   : np.ndarray [shape=(n,)]
        scalar or vector of frequencies

    See Also
    --------
    hz_to_octs
    """
    return (float(A440) / 16) * (2.0 ** np.atleast_1d(octs))


def note_to_hz(note, **kwargs):
    return midi_to_hz(note_to_midi(note, **kwargs))


def __num_two_factors(x):
    """Return how many times integer x can be evenly divided by 2.

    Returns 0 for non-positive integers.
    """
    if x <= 0:
        return 0
    num_twos = 0
    while x % 2 == 0:
        num_twos += 1
        x //= 2

    return num_twos


def cqt_frequencies(n_bins, fmin, bins_per_octave=12, tuning=0.0):
    correction = 2.0 ** (float(tuning) / bins_per_octave)
    frequencies = 2.0 ** (np.arange(0, n_bins, dtype=float) / bins_per_octave)

    return correction * fmin * frequencies


def __early_downsample_count(nyquist, filter_cutoff, hop_length, n_octaves):
    '''Compute the number of early downsampling operations'''

    downsample_count1 = max(0, int(np.ceil(np.log2(BW_FASTEST * nyquist /
                                                   filter_cutoff)) - 1) - 1)

    num_twos = __num_two_factors(hop_length)
    downsample_count2 = max(0, num_twos - n_octaves + 1)

    return min(downsample_count1, downsample_count2)


def __early_downsample(y, sr, hop_length, res_type, n_octaves,
                       nyquist, filter_cutoff, scale):
    '''Perform early downsampling on an audio signal, if it applies.'''

    downsample_count = __early_downsample_count(nyquist, filter_cutoff,
                                                hop_length, n_octaves)

    if downsample_count > 0 and res_type == 'kaiser_fast':
        downsample_factor = 2 ** (downsample_count)

        hop_length //= downsample_factor

        if len(y) < downsample_factor:
            raise ParameterError('Input signal length={:d} is too short for '
                                 '{:d}-octave CQT'.format(len(y), n_octaves))

        new_sr = sr / float(downsample_factor)
        y = resample(y, sr, new_sr,
                     res_type=res_type,
                     scale=True)

        # If we're not going to length-scale after CQT, we
        # need to compensate for the downsampling factor here
        if not scale:
            y *= np.sqrt(downsample_factor)

        sr = new_sr

    return y, sr, hop_length


def sparsify_rows(x, quantile=0.01):
    if x.ndim == 1:
        x = x.reshape((1, -1))

    elif x.ndim > 2:
        raise ParameterError('Input must have 2 or fewer dimensions. '
                             'Provided x.shape={}.'.format(x.shape))

    if not 0.0 <= quantile < 1:
        raise ParameterError('Invalid quantile {:.2f}'.format(quantile))

    x_sparse = scipy.sparse.lil_matrix(x.shape, dtype=x.dtype)

    mags = np.abs(x)
    norms = np.sum(mags, axis=1, keepdims=True)

    mag_sort = np.sort(mags, axis=1)
    cumulative_mag = np.cumsum(mag_sort / norms, axis=1)

    threshold_idx = np.argmin(cumulative_mag < quantile, axis=1)

    for i, j in enumerate(threshold_idx):
        idx = np.where(mags[i] >= mag_sort[i, j])
        x_sparse[i, idx] = x[i, idx]

    return x_sparse.tocsr()


def roll_sparse(x, shift, axis=0):
    if not scipy.sparse.isspmatrix(x):
        return np.roll(x, shift, axis=axis)

    # shift-mod-length lets us have shift > x.shape[axis]
    if axis not in [0, 1, -1]:
        raise ParameterError('axis must be one of (0, 1, -1)')

    shift = np.mod(shift, x.shape[axis])

    if shift == 0:
        return x.copy()

    fmt = x.format
    if axis == 0:
        x = x.tocsc()
    elif axis in (-1, 1):
        x = x.tocsr()

    # lil matrix to start
    x_r = scipy.sparse.lil_matrix(x.shape, dtype=x.dtype)

    idx_in = [slice(None)] * x.ndim
    idx_out = [slice(None)] * x_r.ndim

    idx_in[axis] = slice(0, -shift)
    idx_out[axis] = slice(shift, None)
    x_r[tuple(idx_out)] = x[tuple(idx_in)]

    idx_out[axis] = slice(0, shift)
    idx_in[axis] = slice(-shift, None)
    x_r[tuple(idx_out)] = x[tuple(idx_in)]

    return x_r.asformat(fmt)


def fix_frames(frames, x_min=0, x_max=None, pad=True):
    frames = np.asarray(frames)

    if np.any(frames < 0):
        raise ParameterError('Negative frame index detected')

    if pad and (x_min is not None or x_max is not None):
        frames = np.clip(frames, x_min, x_max)

    if pad:
        pad_data = []
        if x_min is not None:
            pad_data.append(x_min)
        if x_max is not None:
            pad_data.append(x_max)
        frames = np.concatenate((pad_data, frames))

    if x_min is not None:
        frames = frames[frames >= x_min]

    if x_max is not None:
        frames = frames[frames <= x_max]

    return np.unique(frames).astype(int)


def index_to_slice(idx, idx_min=None, idx_max=None, step=None, pad=True):
    # First, normalize the index set
    idx_fixed = fix_frames(idx, idx_min, idx_max, pad=pad)

    # Now convert the indices to slices
    return [slice(start, end, step) for (start, end) in zip(idx_fixed, idx_fixed[1:])]


def constant_q_lengths(sr, fmin, n_bins=84, bins_per_octave=12,
                       tuning=0.0, window='hann', filter_scale=1):
    r'''Return length of each filter in a constant-Q basis.

    Parameters
    ----------
    sr : number > 0 [scalar]
        Audio sampling rate

    fmin : float > 0 [scalar]
        Minimum frequency bin.

    n_bins : int > 0 [scalar]
        Number of frequencies.  Defaults to 7 octaves (84 bins).

    bins_per_octave : int > 0 [scalar]
        Number of bins per octave

    tuning : float in `[-0.5, +0.5)` [scalar]
        Tuning deviation from A440 in fractions of a bin

    window : str or callable
        Window function to use on filters

    filter_scale : float > 0 [scalar]
        Resolution of filter windows. Larger values use longer windows.

    Returns
    -------
    lengths : np.ndarray
        The length of each filter.

    Notes
    -----
    This function caches at level 10.

    See Also
    --------
    constant_q
    librosa.core.cqt
    '''

    if fmin <= 0:
        raise ParameterError('fmin must be positive')

    if bins_per_octave <= 0:
        raise ParameterError('bins_per_octave must be positive')

    if filter_scale <= 0:
        raise ParameterError('filter_scale must be positive')

    if n_bins <= 0 or not isinstance(n_bins, int):
        raise ParameterError('n_bins must be a positive integer')

    correction = 2.0 ** (float(tuning) / bins_per_octave)

    fmin = correction * fmin

    # Q should be capitalized here, so we suppress the name warning
    # pylint: disable=invalid-name
    Q = float(filter_scale) / (2.0 ** (1. / bins_per_octave) - 1)

    # Compute the frequencies
    freq = fmin * (2.0 ** (np.arange(n_bins, dtype=float) / bins_per_octave))

    if freq[-1] * (1 + 0.5 * window_bandwidth(window) / Q) > sr / 2.0:
        raise ParameterError('Filter pass-band lies beyond Nyquist')

    # Convert frequencies to filter lengths
    lengths = Q * sr / freq

    return lengths


def __float_window(window_spec):
    '''Decorator function for windows with fractional input.

    This function guarantees that for fractional `x`, the following hold:

    1. `__float_window(window_function)(x)` has length `np.ceil(x)`
    2. all values from `np.floor(x)` are set to 0.

    For integer-valued `x`, there should be no change in behavior.
    '''

    def _wrap(n, *args, **kwargs):
        '''The wrapped window'''
        n_min, n_max = int(np.floor(n)), int(np.ceil(n))

        window = get_window(window_spec, n_min)

        if len(window) < n_max:
            window = np.pad(window, [(0, n_max - len(window))],
                            mode='constant')

        window[n_min:] = 0.0

        return window

    return _wrap


def constant_q(sr, fmin=None, n_bins=84, bins_per_octave=12, tuning=0.0,
               window='hann', filter_scale=1, pad_fft=True, norm=1,
               **kwargs):
    if fmin is None:
        fmin = note_to_hz('C1')

    # Pass-through parameters to get the filter lengths
    lengths = constant_q_lengths(sr, fmin,
                                 n_bins=n_bins,
                                 bins_per_octave=bins_per_octave,
                                 tuning=tuning,
                                 window=window,
                                 filter_scale=filter_scale)

    # Apply tuning correction
    correction = 2.0 ** (float(tuning) / bins_per_octave)
    fmin = correction * fmin

    # Q should be capitalized here, so we suppress the name warning
    # pylint: disable=invalid-name
    Q = float(filter_scale) / (2.0 ** (1. / bins_per_octave) - 1)

    # Convert lengths back to frequencies
    freqs = Q * sr / lengths

    # Build the filters
    filters = []
    for ilen, freq in zip(lengths, freqs):
        # Build the filter: note, length will be ceil(ilen)
        sig = np.exp(np.arange(ilen, dtype=float) * 1j * 2 * np.pi * freq / sr)

        # Apply the windowing function
        sig = sig * __float_window(window)(ilen)

        # Normalize
        sig = normalize(sig, norm=norm)

        filters.append(sig)

    # Pad and stack
    max_len = max(lengths)
    if pad_fft:
        max_len = int(2.0 ** (np.ceil(np.log2(max_len))))
    else:
        max_len = int(np.ceil(max_len))

    filters = np.asarray([pad_center(filt, max_len, **kwargs)
                          for filt in filters])

    return filters, np.asarray(lengths)


def __cqt_filter_fft(sr, fmin, n_bins, bins_per_octave, tuning,
                     filter_scale, norm, sparsity, hop_length=None,
                     window='hann'):
    '''Generate the frequency domain constant-Q filter basis.'''

    basis, lengths = constant_q(sr,
                                fmin=fmin,
                                n_bins=n_bins,
                                bins_per_octave=bins_per_octave,
                                tuning=tuning,
                                filter_scale=filter_scale,
                                norm=norm,
                                pad_fft=True,
                                window=window)

    # Filters are padded up to the nearest integral power of 2
    n_fft = basis.shape[1]

    if (hop_length is not None and
                n_fft < 2.0 ** (1 + np.ceil(np.log2(hop_length)))):
        n_fft = int(2.0 ** (1 + np.ceil(np.log2(hop_length))))

    # re-normalize bases with respect to the FFT window length
    basis *= lengths[:, np.newaxis] / float(n_fft)

    # FFT and retain only the non-negative frequencies
    fft_basis = fft(basis, n=n_fft, axis=1)[:, :(n_fft // 2) + 1]

    # sparsify the basis
    fft_basis = sparsify_rows(fft_basis, quantile=sparsity)

    return fft_basis, n_fft, lengths


def window_bandwidth(window, n=1000):
    if hasattr(window, '__name__'):
        key = window.__name__
    else:
        key = window

    if key not in WINDOW_BANDWIDTHS:
        win = get_window(window, n)
        WINDOW_BANDWIDTHS[key] = n * np.sum(win ** 2) / np.sum(np.abs(win)) ** 2

    return WINDOW_BANDWIDTHS[key]


def __cqt_response(y, n_fft, hop_length, fft_basis):
    '''Compute the filter response with a target STFT hop.'''

    # Compute the STFT matrix
    D = stft(y, n_fft=n_fft, hop_length=hop_length, window=np.ones)

    # And filter response energy
    return fft_basis.dot(D)


def __trim_stack(cqt_resp, n_bins):
    '''Helper function to trim and stack a collection of CQT responses'''

    # cleanup any framing errors at the boundaries
    max_col = min([x.shape[1] for x in cqt_resp])

    cqt_resp = np.vstack([x[:, :max_col] for x in cqt_resp][::-1])

    # Finally, clip out any bottom frequencies that we don't really want
    # Transpose magic here to ensure column-contiguity
    return np.ascontiguousarray(cqt_resp[-n_bins:].T).T


_warnings_defaults = False
try:
    from _warnings import (filters, default_action, once_registry,
                           warn, warn_explicit)

    defaultaction = default_action
    onceregistry = once_registry
    _warnings_defaults = True
except ImportError:
    filters = []
    defaultaction = "default"
    onceregistry = {}


def formatwarning(message, category, filename, lineno, line=None):
    """Function to format a warning the standard way."""
    try:
        unicodetype = unicode
    except NameError:
        unicodetype = ()
    try:
        message = str(message)
    except UnicodeEncodeError:
        pass
    s = "%s: %s: %s\n" % (lineno, category.__name__, message)
    line = linecache.getline(filename, lineno) if line is None else line
    if line:
        line = line.strip()
        if isinstance(s, unicodetype) and isinstance(line, str):
            line = unicode(line, 'latin1')
        s += "  %s\n" % line
    if isinstance(s, unicodetype) and isinstance(filename, str):
        enc = sys.getfilesystemencoding()
        if enc:
            try:
                filename = unicode(filename, enc)
            except UnicodeDecodeError:
                pass
    s = "%s:%s" % (filename, s)
    return s


def _show_warning(message, category, filename, lineno, file=None, line=None):
    """Hook to write a warning to a file; replace if you like."""
    if file is None:
        file = sys.stderr
        if file is None:
            # sys.stderr is None - warnings get lost
            return
    try:
        file.write(formatwarning(message, category, filename, lineno, line))
    except (IOError, UnicodeError):
        pass  # the file (probably stderr) is invalid - this warning gets lost.


# Keep a working version around in case the deprecation of the old API is
# triggered.
showwarning = _show_warning


def cqt(y, sr=22050, hop_length=512, fmin=None, n_bins=84,
        bins_per_octave=12, tuning=0.0, filter_scale=1,
        norm=1, sparsity=0.01, window='hann',
        scale=True,
        real=Deprecated()):
    # How many octaves are we dealing with?
    n_octaves = int(np.ceil(float(n_bins) / bins_per_octave))
    n_filters = min(bins_per_octave, n_bins)

    len_orig = len(y)

    if fmin is None:
        # C1 by default
        fmin = note_to_hz('C1')

    if tuning is None:
        tuning = estimate_tuning(y=y, sr=sr)

    # First thing, get the freqs of the top octave
    freqs = cqt_frequencies(n_bins, fmin,
                            bins_per_octave=bins_per_octave)[-bins_per_octave:]

    fmin_t = np.min(freqs)
    fmax_t = np.max(freqs)

    # Determine required resampling quality
    Q = float(filter_scale) / (2.0 ** (1. / bins_per_octave) - 1)
    filter_cutoff = fmax_t * (1 + 0.5 * window_bandwidth(window) / Q)
    nyquist = sr / 2.0
    if filter_cutoff < BW_FASTEST * nyquist:
        res_type = 'kaiser_fast'
    else:
        res_type = 'kaiser_best'

    y, sr, hop_length = __early_downsample(y, sr, hop_length,
                                           res_type,
                                           n_octaves,
                                           nyquist, filter_cutoff, scale)

    cqt_resp = []

    if res_type != 'kaiser_fast':
        # Do the top octave before resampling to allow for fast resampling
        fft_basis, n_fft, _ = __cqt_filter_fft(sr, fmin_t,
                                               n_filters,
                                               bins_per_octave,
                                               tuning,
                                               filter_scale,
                                               norm,
                                               sparsity,
                                               window=window)

        # Compute the CQT filter response and append it to the stack
        cqt_resp.append(__cqt_response(y, n_fft, hop_length, fft_basis))

        fmin_t /= 2
        fmax_t /= 2
        n_octaves -= 1

        filter_cutoff = fmax_t * (1 + 0.5 * window_bandwidth(window) / Q)

        res_type = 'kaiser_fast'

    # Make sure our hop is long enough to support the bottom octave
    num_twos = __num_two_factors(hop_length)
    if num_twos < n_octaves - 1:
        raise ParameterError('hop_length must be a positive integer '
                             'multiple of 2^{0:d} for {1:d}-octave CQT'
                             .format(n_octaves - 1, n_octaves))

    # Now do the recursive bit
    fft_basis, n_fft, _ = __cqt_filter_fft(sr, fmin_t,
                                           n_filters,
                                           bins_per_octave,
                                           tuning,
                                           filter_scale,
                                           norm,
                                           sparsity,
                                           window=window)

    my_y, my_sr, my_hop = y, sr, hop_length

    # Iterate down the octaves
    for i in range(n_octaves):

        # Resample (except first time)
        if i > 0:
            if len(my_y) < 2:
                raise ParameterError('Input signal length={} is too short for '
                                     '{:d}-octave CQT'.format(len_orig,
                                                              n_octaves))

            # The additional scaling of sqrt(2) here is to implicitly rescale
            # the filters
            my_y = np.sqrt(2) * resample(my_y, my_sr, my_sr / 2.0,
                                         res_type=res_type,
                                         scale=True)
            my_sr /= 2.0
            my_hop //= 2

        # Compute the cqt filter response and append to the stack
        cqt_resp.append(__cqt_response(my_y, n_fft, my_hop, fft_basis))

    C = __trim_stack(cqt_resp, n_bins)

    if scale:
        lengths = constant_q_lengths(sr, fmin,
                                     n_bins=n_bins,
                                     bins_per_octave=bins_per_octave,
                                     tuning=tuning,
                                     window=window,
                                     filter_scale=filter_scale)
        C /= np.sqrt(lengths[:, np.newaxis])

    if not isinstance(real, Deprecated):
        warn('Real-valued CQT (real=True) is deprecated in 0.4.2. '
             'The `real` parameter will be removed in 0.6.0.'
             'Use np.abs(librosa.cqt(...)) '
             'instead of real=True to maintain forward compatibility.',
             DeprecationWarning)
        if real:
            C = np.abs(C)

    return C


def pseudo_cqt(y, sr=22050, hop_length=512, fmin=None, n_bins=84,
               bins_per_octave=12, tuning=0.0, filter_scale=1,
               norm=1, sparsity=0.01, window='hann', scale=True):
    if fmin is None:
        # C1 by default
        fmin = note_to_hz('C1')

    if tuning is None:
        tuning = estimate_tuning(y=y, sr=sr)

    fft_basis, n_fft, _ = __cqt_filter_fft(sr, fmin, n_bins,
                                           bins_per_octave,
                                           tuning, filter_scale,
                                           norm, sparsity,
                                           hop_length=hop_length,
                                           window=window)

    fft_basis = np.abs(fft_basis)

    # Compute the magnitude STFT with Hann window
    D = np.abs(stft(y, n_fft=n_fft, hop_length=hop_length))

    # Project onto the pseudo-cqt basis
    C = fft_basis.dot(D)

    if scale:
        C /= np.sqrt(n_fft)
    else:
        lengths = filters.constant_q_lengths(sr, fmin,
                                             n_bins=n_bins,
                                             bins_per_octave=bins_per_octave,
                                             tuning=tuning,
                                             window=window,
                                             filter_scale=filter_scale)

        C *= np.sqrt(lengths[:, np.newaxis] / n_fft)

    return C


def hybrid_cqt(y, sr=22050, hop_length=512, fmin=None, n_bins=84,
               bins_per_octave=12, tuning=0.0, filter_scale=1,
               norm=1, sparsity=0.01, window='hann', scale=True):
    if fmin is None:
        # C1 by default
        fmin = note_to_hz('C1')

    if tuning is None:
        tuning = estimate_tuning(y=y, sr=sr)

    # Get all CQT frequencies
    freqs = cqt_frequencies(n_bins, fmin,
                            bins_per_octave=bins_per_octave,
                            tuning=tuning)

    # Compute the length of each constant-Q basis function
    lengths = filters.constant_q_lengths(sr, fmin,
                                         n_bins=n_bins,
                                         bins_per_octave=bins_per_octave,
                                         tuning=tuning,
                                         filter_scale=filter_scale,
                                         window=window)

    # Determine which filters to use with Pseudo CQT
    # These are the ones that fit within 2 hop lengths after padding
    pseudo_filters = 2.0 ** np.ceil(np.log2(lengths)) < 2 * hop_length

    n_bins_pseudo = int(np.sum(pseudo_filters))

    n_bins_full = n_bins - n_bins_pseudo
    cqt_resp = []

    if n_bins_pseudo > 0:
        fmin_pseudo = np.min(freqs[pseudo_filters])

        cqt_resp.append(pseudo_cqt(y, sr,
                                   hop_length=hop_length,
                                   fmin=fmin_pseudo,
                                   n_bins=n_bins_pseudo,
                                   bins_per_octave=bins_per_octave,
                                   tuning=tuning,
                                   filter_scale=filter_scale,
                                   norm=norm,
                                   sparsity=sparsity,
                                   window=window,
                                   scale=scale))

    if n_bins_full > 0:
        cqt_resp.append(np.abs(cqt(y, sr,
                                   hop_length=hop_length,
                                   fmin=fmin,
                                   n_bins=n_bins_full,
                                   bins_per_octave=bins_per_octave,
                                   tuning=tuning,
                                   filter_scale=filter_scale,
                                   norm=norm,
                                   sparsity=sparsity,
                                   window=window,
                                   scale=scale)))

    return __trim_stack(cqt_resp, n_bins)


def cq_to_chroma(n_input, bins_per_octave=12, n_chroma=12,
                 fmin=None, window=None, base_c=True):
    # How many fractional bins are we merging?
    n_merge = float(bins_per_octave) / n_chroma

    if fmin is None:
        fmin = note_to_hz('C1')

    if np.mod(n_merge, 1) != 0:
        raise ParameterError('Incompatible CQ merge: '
                             'input bins must be an '
                             'integer multiple of output bins.')

    # Tile the identity to merge fractional bins
    cq_to_ch = np.repeat(np.eye(n_chroma), n_merge, axis=1)

    # Roll it left to center on the target bin
    cq_to_ch = np.roll(cq_to_ch, - int(n_merge // 2), axis=1)

    # How many octaves are we repeating?
    n_octaves = np.ceil(np.float(n_input) / bins_per_octave)

    # Repeat and trim
    cq_to_ch = np.tile(cq_to_ch, int(n_octaves))[:, :n_input]

    # What's the note number of the first bin in the CQT?
    # midi uses 12 bins per octave here
    midi_0 = np.mod(hz_to_midi(fmin), 12)

    if base_c:
        # rotate to C
        roll = midi_0
    else:
        # rotate to A
        roll = midi_0 - 9

    # Adjust the roll in terms of how many chroma we want out
    # We need to be careful with rounding here
    roll = int(np.round(roll * (n_chroma / 12.)))

    # Apply the roll
    cq_to_ch = np.roll(cq_to_ch, roll, axis=0).astype(float)

    if window is not None:
        cq_to_ch = scipy.signal.convolve(cq_to_ch,
                                         np.atleast_2d(window),
                                         mode='same')

    return cq_to_ch


def chroma_cqt(y=None, sr=22050, C=None, hop_length=512, fmin=None,
               norm=np.inf, threshold=0.0, tuning=None, n_chroma=12,
               n_octaves=7, window=None, bins_per_octave=None, cqt_mode='full'):
    cqt_func = {'full': cqt, 'hybrid': hybrid_cqt}

    if bins_per_octave is None:
        bins_per_octave = n_chroma

    # Build the CQT if we don't have one already
    if C is None:
        C = np.abs(cqt_func[cqt_mode](y, sr=sr,
                                      hop_length=hop_length,
                                      fmin=fmin,
                                      n_bins=n_octaves * bins_per_octave,
                                      bins_per_octave=bins_per_octave,
                                      tuning=tuning))

    # Map to chroma
    cq_to_chr = cq_to_chroma(C.shape[0],
                             bins_per_octave=bins_per_octave,
                             n_chroma=n_chroma,
                             fmin=fmin,
                             window=window)
    chroma = cq_to_chr.dot(C)

    if threshold is not None:
        chroma[chroma < threshold] = 0.0

    # Normalize
    if norm is not None:
        chroma = normalize(chroma, norm=norm, axis=0)

    return chroma


def chroma_cens(y=None, sr=22050, C=None, hop_length=512, fmin=None,
                tuning=None, n_chroma=12,
                n_octaves=7, bins_per_octave=None, cqt_mode='full', window=None,
                norm=2, win_len_smooth=41):
    chroma = chroma_cqt(y=y, C=C, sr=sr,
                        hop_length=hop_length,
                        fmin=fmin,
                        bins_per_octave=bins_per_octave,
                        tuning=tuning,
                        norm=None,
                        n_chroma=n_chroma,
                        n_octaves=n_octaves,
                        cqt_mode=cqt_mode,
                        window=window)

    # L1-Normalization
    chroma = normalize(chroma, norm=1, axis=0)

    # Quantize amplitudes
    QUANT_STEPS = [0.4, 0.2, 0.1, 0.05]
    QUANT_WEIGHTS = [0.25, 0.25, 0.25, 0.25]

    chroma_quant = np.zeros_like(chroma)

    for cur_quant_step_idx, cur_quant_step in enumerate(QUANT_STEPS):
        chroma_quant += (chroma > cur_quant_step) * QUANT_WEIGHTS[cur_quant_step_idx]

    # Apply temporal smoothing
    win = scipy.signal.hanning(win_len_smooth + 2, sym=False)
    win /= np.sum(win)
    win = np.atleast_2d(win)

    cens = scipy.signal.convolve2d(chroma_quant, win, mode='same')

    # L2-Normalization
    return normalize(cens, norm=norm, axis=0)


def stft(y, n_fft=2048, hop_length=None, win_length=None, window='hann',
         center=True, dtype=np.complex64):
    # By default, use the entire frame
    if win_length is None:
        win_length = n_fft

    # Set the default hop, if it's not already specified
    if hop_length is None:
        hop_length = int(win_length // 4)

    fft_window = get_window(window, win_length, fftbins=True)

    # Pad the window out to n_fft size
    fft_window = pad_center(fft_window, n_fft)

    # Reshape so that the window can be broadcast
    fft_window = fft_window.reshape((-1, 1))

    # Pad the time series so that frames are centered
    if center:
        valid_audio(y)
        y = np.pad(y, int(n_fft // 2), mode='reflect')

    # Window the time series.
    y_frames = frame(y, frame_length=n_fft, hop_length=hop_length)

    # Pre-allocate the STFT matrix
    stft_matrix = np.empty((int(1 + n_fft // 2), y_frames.shape[1]),
                           dtype=dtype,
                           order='F')

    # how many columns can we fit within MAX_MEM_BLOCK?
    n_columns = int(MAX_MEM_BLOCK / (stft_matrix.shape[0] *
                                     stft_matrix.itemsize))

    for bl_s in range(0, stft_matrix.shape[1], n_columns):
        bl_t = min(bl_s + n_columns, stft_matrix.shape[1])

        # RFFT and Conjugate here to match phase from DPWE code
        stft_matrix[:, bl_s:bl_t] = fft(fft_window *
                                        y_frames[:, bl_s:bl_t],
                                        axis=0)[:stft_matrix.shape[0]].conj()

    return stft_matrix


def istft(stft_matrix, hop_length=None, win_length=None, window='hann',
          center=True, dtype=np.float32):
    n_fft = 2 * (stft_matrix.shape[0] - 1)

    # By default, use the entire frame
    if win_length is None:
        win_length = n_fft

    # Set the default hop, if it's not already specified
    if hop_length is None:
        hop_length = int(win_length // 4)

    ifft_window = get_window(window, win_length, fftbins=True)

    # Pad out to match n_fft
    ifft_window = pad_center(ifft_window, n_fft)

    n_frames = stft_matrix.shape[1]
    expected_signal_len = n_fft + hop_length * (n_frames - 1)
    y = np.zeros(expected_signal_len, dtype=dtype)
    ifft_window_sum = np.zeros(expected_signal_len, dtype=dtype)
    ifft_window_square = ifft_window * ifft_window

    for i in range(n_frames):
        sample = i * hop_length
        spec = stft_matrix[:, i].flatten()
        spec = np.concatenate((spec.conj(), spec[-2:0:-1]), 0)
        ytmp = ifft_window * fft.ifft(spec).real

        y[sample:(sample + n_fft)] = y[sample:(sample + n_fft)] + ytmp
        ifft_window_sum[sample:(sample + n_fft)] += ifft_window_square

    # Normalize by sum of squared window
    approx_nonzero_indices = ifft_window_sum > tiny(ifft_window_sum)
    y[approx_nonzero_indices] /= ifft_window_sum[approx_nonzero_indices]

    if center:
        y = y[int(n_fft // 2):-int(n_fft // 2)]

    return y


def magphase(D):
    mag = np.abs(D)
    phase = np.exp(1.j * np.angle(D))

    return mag, phase


def softmask(X, X_ref, power=1, split_zeros=False):
    if X.shape != X_ref.shape:
        raise ParameterError('Shape mismatch: {}!={}'.format(X.shape,
                                                             X_ref.shape))

    if np.any(X < 0) or np.any(X_ref < 0):
        raise ParameterError('X and X_ref must be non-negative')

    if power <= 0:
        raise ParameterError('power must be strictly positive')

    # We're working with ints, cast to float.
    dtype = X.dtype
    if not np.issubdtype(dtype, float):
        dtype = np.float32

    # Re-scale the input arrays relative to the larger value
    Z = np.maximum(X, X_ref).astype(dtype)
    bad_idx = (Z < np.finfo(dtype).tiny)
    Z[bad_idx] = 1

    # For finite power, compute the softmask
    if np.isfinite(power):
        mask = (X / Z) ** power
        ref_mask = (X_ref / Z) ** power
        good_idx = ~bad_idx
        mask[good_idx] /= mask[good_idx] + ref_mask[good_idx]
        # Wherever energy is below energy in both inputs, split the mask
        if split_zeros:
            mask[bad_idx] = 0.5
        else:
            mask[bad_idx] = 0.0
    else:
        # Otherwise, compute the hard mask
        mask = X > X_ref

    return mask


def hpss(S, kernel_size=31, power=2.0, mask=False, margin=1.0):
    if np.iscomplexobj(S):
        S, phase = magphase(S)
    else:
        phase = 1

    if np.isscalar(kernel_size):
        win_harm = kernel_size
        win_perc = kernel_size
    else:
        win_harm = kernel_size[0]
        win_perc = kernel_size[1]

    if np.isscalar(margin):
        margin_harm = margin
        margin_perc = margin
    else:
        margin_harm = margin[0]
        margin_perc = margin[1]

    # margin minimum is 1.0
    if margin_harm < 1 or margin_perc < 1:
        raise ParameterError("Margins must be >= 1.0. "
                             "A typical range is between 1 and 10.")

    # Compute median filters. Pre-allocation here preserves memory layout.
    harm = np.empty_like(S)
    harm[:] = median_filter(S, size=(1, win_harm), mode='reflect')

    perc = np.empty_like(S)
    perc[:] = median_filter(S, size=(win_perc, 1), mode='reflect')

    split_zeros = (margin_harm == 1 and margin_perc == 1)

    mask_harm = softmask(harm, perc * margin_harm,
                         power=power,
                         split_zeros=split_zeros)

    mask_perc = softmask(perc, harm * margin_perc,
                         power=power,
                         split_zeros=split_zeros)

    if mask:
        return mask_harm, mask_perc

    return ((S * mask_harm) * phase, (S * mask_perc) * phase)


def sstft(y, n_fft=2048, hop_length=None, win_length=None, window='hann',
          center=True, dtype=np.complex64):
    # By default, use the entire frame
    if win_length is None:
        win_length = n_fft

    # Set the default hop, if it's not already specified
    if hop_length is None:
        hop_length = int(win_length // 4)

    fft_window = get_window(window, win_length, fftbins=True)

    # Pad the window out to n_fft size
    fft_window = pad_center(fft_window, n_fft)

    # Reshape so that the window can be broadcast
    fft_window = fft_window.reshape((-1, 1))

    # Pad the time series so that frames are centered
    if center:
        valid_audio(y)
        y = np.pad(y, int(n_fft // 2), mode='reflect')

    # Window the time series.
    y_frames = frame(y, frame_length=n_fft, hop_length=hop_length)

    # Pre-allocate the STFT matrix
    stft_matrix = np.empty((int(1 + n_fft // 2), y_frames.shape[1]),
                           dtype=dtype,
                           order='F')

    # how many columns can we fit within MAX_MEM_BLOCK?
    n_columns = int(MAX_MEM_BLOCK / (stft_matrix.shape[0] *
                                     stft_matrix.itemsize))

    for bl_s in range(0, stft_matrix.shape[1], n_columns):
        bl_t = min(bl_s + n_columns, stft_matrix.shape[1])

        # RFFT and Conjugate here to match phase from DPWE code
        stft_matrix[:, bl_s:bl_t] = fft(fft_window *
                                        y_frames[:, bl_s:bl_t],
                                        axis=0)[:stft_matrix.shape[0]].conj()

    return stft_matrix


def harmonic(y, **kwargs):
    # Compute the STFT matrix
    stft = sstft(y)

    # Remove percussives
    stft_harm = hpss(stft, **kwargs)[0]

    # Invert the STFTs
    y_harm = fix_length(istft(stft_harm, dtype=y.dtype), len(y))

    return y_harm


def tonnetz(y=None, sr=22050, chroma=None):
    if y is None and chroma is None:
        raise ParameterError('Either the audio samples or the chromagram must be '
                             'passed as an argument.')

    if chroma is None:
        chroma = chroma_cqt(y=y, sr=sr)

    # Generate Transformation matrix
    dim_map = np.linspace(0, 12, num=chroma.shape[0], endpoint=False)

    scale = np.asarray([7. / 6, 7. / 6,
                        3. / 2, 3. / 2,
                        2. / 3, 2. / 3])

    V = np.multiply.outer(scale, dim_map)

    # Even rows compute sin()
    V[::2] -= 0.5

    R = np.array([1, 1,  # Fifths
                  1, 1,  # Minor
                  0.5, 0.5])  # Major

    phi = R[:, np.newaxis] * np.cos(np.pi * V)

    # Do the transform to tonnetz
    return phi.dot(normalize(chroma, norm=1, axis=0))
