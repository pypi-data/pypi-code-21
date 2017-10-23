#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Spectral feature extraction"""
import numpy as np
from librosa import util
from librosa.core.audio import zero_crossings, to_mono
from librosa.core.spectrum import power_to_db, _spectrogram
from librosa.core.time_frequency import fft_frequencies
from librosa.util.deprecation import Deprecated, rename_kw
from librosa.util.exceptions import ParameterError

__all__ = ['spectral_centroid',
           'spectral_bandwidth',
           'spectral_contrast',
           'spectral_rolloff',
           'poly_features',
           'rmse',
           'zero_crossing_rate',
           ]


# -- Spectral features -- #
def calc_spectral_centroid(y=None, sr=22050, S=None, n_fft=2048, hop_length=512,
                      freq=None):

    S, n_fft = _spectrogram(y=y, S=S, n_fft=n_fft, hop_length=hop_length)

    if not np.isrealobj(S):
        raise ParameterError('Spectral centroid is only defined '
                             'with real-valued input')
    elif np.any(S < 0):
        raise ParameterError('Spectral centroid is only defined '
                             'with non-negative energies')

    # Compute the center frequencies of each bin
    if freq is None:
        freq = fft_frequencies(sr=sr, n_fft=n_fft)

    if freq.ndim == 1:
        freq = freq.reshape((-1, 1))

    # Column-normalize S
    return np.sum(freq * util.normalize(S, norm=1, axis=0),
                  axis=0, keepdims=True)


def calc_spectral_bandwidth(y=None, sr=22050, S=None, n_fft=2048, hop_length=512,
                       freq=None, centroid=None, norm=True, p=2):

    S, n_fft = _spectrogram(y=y, S=S, n_fft=n_fft, hop_length=hop_length)

    if not np.isrealobj(S):
        raise ParameterError('Spectral bandwidth is only defined '
                             'with real-valued input')
    elif np.any(S < 0):
        raise ParameterError('Spectral bandwidth is only defined '
                             'with non-negative energies')

    if centroid is None:
        centroid = calc_spectral_centroid(y=y, sr=sr, S=S,
                                     n_fft=n_fft,
                                     hop_length=hop_length,
                                     freq=freq)

    # Compute the center frequencies of each bin
    if freq is None:
        freq = fft_frequencies(sr=sr, n_fft=n_fft)

    if freq.ndim == 1:
        deviation = np.abs(np.subtract.outer(freq, centroid[0]))
    else:
        deviation = np.abs(freq - centroid[0])

    # Column-normalize S
    if norm:
        S = util.normalize(S, norm=1, axis=0)

    return np.sum(S * deviation**p, axis=0, keepdims=True)**(1./p)


def calc_spectral_contrast(y=None, sr=22050, S=None, n_fft=2048, hop_length=512,
                      freq=None, fmin=200.0, n_bands=6, quantile=0.02,
                      linear=False):

    S, n_fft = _spectrogram(y=y, S=S, n_fft=n_fft, hop_length=hop_length)

    # Compute the center frequencies of each bin
    if freq is None:
        freq = fft_frequencies(sr=sr, n_fft=n_fft)

    freq = np.atleast_1d(freq)

    if freq.ndim != 1 or len(freq) != S.shape[0]:
        raise ParameterError('freq.shape mismatch: expected '
                             '({:d},)'.format(S.shape[0]))

    if n_bands < 1 or not isinstance(n_bands, int):
        raise ParameterError('n_bands must be a positive integer')

    if not 0.0 < quantile < 1.0:
        raise ParameterError('quantile must lie in the range (0, 1)')

    if fmin <= 0:
        raise ParameterError('fmin must be a positive number')

    octa = np.zeros(n_bands + 2)
    octa[1:] = fmin * (2.0**np.arange(0, n_bands + 1))

    if np.any(octa[:-1] >= 0.5 * sr):
        raise ParameterError('Frequency band exceeds Nyquist. '
                             'Reduce either fmin or n_bands.')

    valley = np.zeros((n_bands + 1, S.shape[1]))
    peak = np.zeros_like(valley)

    for k, (f_low, f_high) in enumerate(zip(octa[:-1], octa[1:])):
        current_band = np.logical_and(freq >= f_low, freq <= f_high)

        idx = np.flatnonzero(current_band)

        if k > 0:
            current_band[idx[0] - 1] = True

        if k == n_bands:
            current_band[idx[-1] + 1:] = True

        sub_band = S[current_band]

        if k < n_bands:
            sub_band = sub_band[:-1]

        # Always take at least one bin from each side
        idx = np.rint(quantile * np.sum(current_band))
        idx = int(np.maximum(idx, 1))

        sortedr = np.sort(sub_band, axis=0)

        valley[k] = np.mean(sortedr[:idx], axis=0)
        peak[k] = np.mean(sortedr[-idx:], axis=0)

    if linear:
        return peak - valley
    else:
        return power_to_db(peak) - power_to_db(valley)


def calc_spectral_rolloff(y=None, sr=22050, S=None, n_fft=2048, hop_length=512,
                     freq=None, roll_percent=0.85):

    if not 0.0 < roll_percent < 1.0:
        raise ParameterError('roll_percent must lie in the range (0, 1)')

    S, n_fft = _spectrogram(y=y, S=S, n_fft=n_fft, hop_length=hop_length)

    if not np.isrealobj(S):
        raise ParameterError('Spectral rolloff is only defined '
                             'with real-valued input')
    elif np.any(S < 0):
        raise ParameterError('Spectral rolloff is only defined '
                             'with non-negative energies')

    # Compute the center frequencies of each bin
    if freq is None:
        freq = fft_frequencies(sr=sr, n_fft=n_fft)

    # Make sure that frequency can be broadcast
    if freq.ndim == 1:
        freq = freq.reshape((-1, 1))

    total_energy = np.cumsum(S, axis=0)

    threshold = roll_percent * total_energy[-1]

    ind = np.where(total_energy < threshold, np.nan, 1)

    return np.nanmin(ind * freq, axis=0, keepdims=True)


def calc_rmse(y=None, S=None, frame_length=2048, hop_length=512,
         center=True, pad_mode='reflect',
         n_fft=Deprecated()):

    frame_length = rename_kw('n_fft', n_fft,
                             'frame_length', frame_length,
                             '0.5', '0.6')

    if y is not None and S is not None:
        raise ValueError('Either `y` or `S` should be input.')
    if y is not None:
        y = to_mono(y)
        if center:
            y = np.pad(y, int(frame_length // 2), mode=pad_mode)

        x = util.frame(y,
                       frame_length=frame_length,
                       hop_length=hop_length)
    elif S is not None:
        x, _ = _spectrogram(y=y, S=S,
                            n_fft=frame_length,
                            hop_length=hop_length)
    else:
        raise ValueError('Either `y` or `S` must be input.')
    return np.sqrt(np.mean(np.abs(x)**2, axis=0, keepdims=True))


def calc_poly_features(y=None, sr=22050, S=None, n_fft=2048, hop_length=512,
                  order=1, freq=None):

    S, n_fft = _spectrogram(y=y, S=S, n_fft=n_fft, hop_length=hop_length)

    # Compute the center frequencies of each bin
    if freq is None:
        freq = fft_frequencies(sr=sr, n_fft=n_fft)

    # If frequencies are constant over frames, then we only need to fit once
    if freq.ndim == 1:
        coefficients = np.polyfit(freq, S, order)
    else:
        # Else, fit each frame independently and stack the results
        coefficients = np.concatenate([[np.polyfit(freq[:, i], S[:, i], order)]
                                       for i in range(S.shape[1])], axis=0).T

    return coefficients


def calc_zero_crossing_rate(y, frame_length=2048, hop_length=512, center=True,
                       **kwargs):

    util.valid_audio(y)

    if center:
        y = np.pad(y, int(frame_length // 2), mode='edge')

    y_framed = util.frame(y, frame_length, hop_length)

    kwargs['axis'] = 0
    kwargs.setdefault('pad', False)

    crossings = zero_crossings(y_framed, **kwargs)

    return np.mean(crossings, axis=0, keepdims=True)



