# coding: utf-8
import numpy as np
import scipy.io.wavfile as wav
from matplotlib import pyplot as plt
from numpy.lib import stride_tricks

""" short time fourier transform of audio signal """


def stft(sig, frameSize, overlapFac=0.5, window=np.hanning):
    # print frameSize
    win = window(frameSize)
    hopSize = int(frameSize - np.floor(overlapFac * frameSize))

    # zeros at beginning (thus center of 1st window should be for sample nr. 0)
    samples = np.append(np.zeros(int(np.floor(frameSize / 2.0))), sig)
    # cols for windowing
    cols = int(np.ceil((len(samples) - frameSize) / float(hopSize)) + 1)
    # zeros at end (thus samples can be fully covered by frames)
    samples = np.append(samples, np.zeros(frameSize))
    # print samples, (cols, frameSize),(samples.strides[0] * hopSize, samples.strides[0])

    frames = stride_tricks.as_strided(samples, shape=(cols, frameSize),
                                      strides=(samples.strides[0] * hopSize, samples.strides[0])).copy()
    frames *= win

    return np.fft.rfft(frames)


""" scale frequency axis logarithmically """


def logscale_spec(spec, sr=44100, factor=20.):
    timebins, freqbins = np.shape(spec)

    scale = np.linspace(0, 1, freqbins) ** factor
    scale *= (freqbins - 1) / max(scale)
    scale = np.unique(np.round(scale))

    # create spectrogram with new freq bins
    newspec = np.complex128(np.zeros([timebins, len(scale)]))
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            newspec[:, i] = np.sum(spec[:, int(scale[i]):], axis=1)
        else:

            newspec[:, i] = np.sum(spec[:, int(scale[i]):int(scale[i + 1])], axis=1)

    # list center freq of bins
    allfreqs = np.abs(np.fft.fftfreq(freqbins * 2, 1. / sr)[:freqbins + 1])
    freqs = []
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            freqs += [np.mean(allfreqs[int(scale[i]):])]
        else:
            freqs += [np.mean(allfreqs[int(scale[i]):int(scale[i + 1])])]

    return newspec, freqs


""" get spectrogram"""


def getstft(audiopath, binsize=2 ** 10, plotpath=None, colormap="jet"):
    samplerate, samples = wav.read(audiopath)
    s = stft(samples, binsize)
    sshow, freq = logscale_spec(s, factor=1.0, sr=samplerate)
    ims = 20. * np.log10(np.abs(sshow) / 10e-6)  # amplitude to decibel
    ims = ims / 255
    timebins, freqbins = np.shape(ims)
    print timebins, freqbins
    return ims


""" plot spectrogram"""


def plotstft(audiopath, binsize=2 ** 10, plotpath=None, colormap="jet"):
    samplerate, samples = wav.read(audiopath)
    s = stft(samples, binsize)
    sshow, freq = logscale_spec(s, factor=1.0, sr=samplerate)
    ims = 20. * np.log10(np.abs(sshow) / 10e-6)  # amplitude to decibel
    ims = ims / 255

    timebins, freqbins = np.shape(ims)
    print timebins, freqbins
    plt.figure(figsize=(15, 7.5))
    plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap=colormap, interpolation="none")
    plt.colorbar()

    plt.xlabel("time (s)")
    plt.ylabel("frequency (hz)")
    plt.xlim([0, timebins - 1])
    plt.ylim([0, freqbins])

    xlocs = np.float32(np.linspace(0, timebins - 1, 5))
    plt.xticks(xlocs, ["%.02f" % l for l in ((xlocs * len(samples) / timebins) + (0.5 * binsize)) / samplerate])
    ylocs = np.int16(np.round(np.linspace(0, freqbins - 1, 10)))
    plt.yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])

    if plotpath:
        plt.savefig(plotpath, bbox_inches="tight")
    else:
        plt.show()

    plt.clf()


def main():
    wavPath = "../data/pop.wav"
    res = getstft(wavPath)
    print type(res)
    plotstft(wavPath)
    return 0


if __name__ == '__main__':
    main()
