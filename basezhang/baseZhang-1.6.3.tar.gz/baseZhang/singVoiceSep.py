# -*- coding: utf-8 -*-
"""
================
Vocal separation
================

This notebook demonstrates a simple technique for separating vocals (and
other sporadic foreground signals) from accompanying instrumentation.

This is based on the "REPET-SIM" method of `Rafii and Pardo, 2012
<http://www.cs.northwestern.edu/~zra446/doc/Rafii-Pardo%20-%20Music-Voice%20Separation%20using%20the%20Similarity%20Matrix%20-%20ISMIR%202012.pdf>`_, but includes a couple of modifications and extensions:

    - FFT windows overlap by 1/4, instead of 1/2
    - Non-local filtering is converted into a soft mask by Wiener filtering.
      This is similar in spirit to the soft-masking method used by `Fitzgerald, 2012
      <http://arrow.dit.ie/cgi/viewcontent.cgi?article=1086&context=argcon>`_,
      but is a bit more numerically stable in practice.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
from baseZhang import wavwrite
import librosa.display


def split_vocal_music(mix_path='mix.wav'):
    #############################################
    # Load an example with vocals.
    y, sr = librosa.load(mix_path, duration=120)

    # And compute the spectrogram magnitude and phase
    D = librosa.stft(y)
    S_full, phase = librosa.magphase(D)
    # print(D[0][:5])
    # print ((S_full[0]*phase[0])[:5])
    # print ((S_full[0])[:5])
    # print ((phase[0])[:5])
    # print ((S_full[0]+phase[0])[:5])

    #######################################
    # Plot a 5-second slice of the spectrum
    # idx = slice(*librosa.time_to_frames([30, 35], sr=sr))
    # plt.figure(figsize=(12, 4))
    # librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
    #                          y_axis='log', x_axis='time', sr=sr)
    # plt.colorbar()
    # plt.tight_layout()

    ###########################################################
    # The wiggly lines above are due to the vocal component.
    # Our goal is to separate them from the accompanying
    # instrumentation.
    #

    # We'll compare frames using cosine similarity, and aggregate similar frames
    # by taking their (per-frequency) median value.
    #
    # To avoid being biased by local continuity, we constrain similar frames to be
    # separated by at least 2 seconds.
    #
    # This suppresses sparse/non-repetetitive deviations from the average spectrum,
    # and works well to discard vocal elements.

    S_filter = librosa.decompose.nn_filter(S_full,
                                           aggregate=np.median,
                                           metric='cosine',
                                           width=int(librosa.time_to_frames(2, sr=sr)))

    # The output of the filter shouldn't be greater than the input
    # if we assume signals are additive.  Taking the pointwise minimium
    # with the input spectrum forces this.
    S_filter = np.minimum(S_full, S_filter)

    ##############################################
    # The raw filter output can be used as a mask,
    # but it sounds better if we use soft-masking.

    # We can also use a margin to reduce bleed between the vocals and instrumentation masks.
    # Note: the margins need not be equal for foreground and background separation
    margin_i, margin_v = 2, 10
    power = 2

    mask_i = librosa.util.softmask(S_filter,
                                   margin_i * (S_full - S_filter),
                                   power=power)

    mask_v = librosa.util.softmask(S_full - S_filter,
                                   margin_v * S_filter,
                                   power=power)

    # Once we have the masks, simply multiply them with the input spectrum
    # to separate the components

    S_foreground = mask_v * S_full
    S_background = mask_i * S_full

    vocal = S_foreground * phase
    vocal_data = librosa.istft(vocal)
    wavwrite(mix_path.replace('.wav', '_vocal.wav'), vocal_data, sr)

    music = S_background * phase
    music_data = librosa.istft(music)
    wavwrite(mix_path.replace('.wav', '_music.wav'), music_data, sr)

    # ##########################################
    # # Plot the same slice, but separated into its foreground and background
    #
    # # sphinx_gallery_thumbnail_number = 2
    #
    # plt.figure(figsize=(12, 8))
    # plt.subplot(3, 1, 1)
    # librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
    #                          y_axis='log', sr=sr)
    # plt.title('Full spectrum')
    # plt.colorbar()
    #
    # plt.subplot(3, 1, 2)
    # librosa.display.specshow(librosa.amplitude_to_db(S_background[:, idx], ref=np.max),
    #                          y_axis='log', sr=sr)
    # plt.title('Background')
    # plt.colorbar()
    # plt.subplot(3, 1, 3)
    # librosa.display.specshow(librosa.amplitude_to_db(S_foreground[:, idx], ref=np.max),
    #                          y_axis='log', x_axis='time', sr=sr)
    # plt.title('Foreground')
    # plt.colorbar()
    # plt.tight_layout()
    # plt.show()

    return 0


def batch_split_vocal_music(mix_dir='../data/mix'):
    for root, dirs, names in os.walk(mix_dir):
        for name in names:
            if '.wav' in name:
                wav_path = os.path.join(root, name)
                split_vocal_music(wav_path)

    return 0


if __name__ == '__main__':
    split_vocal_music()

