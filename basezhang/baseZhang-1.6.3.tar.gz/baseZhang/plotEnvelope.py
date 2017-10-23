#!/usr/bin/env python

from pylab import *
from scipy.signal import *


def plotEnvelope(signal, xlabel_string='Time (seconds)', ylabel_String='Amplitude',
                 fig_title='X, with calculated envelope', legend_signal_str='signal', legend_envelop_str='envelope'):
    # t=linspace(0, 1, len(signal))
    # Calculate envelope, called m_hat via hilbert transform
    m_hat = abs(hilbert(signal))
    max_signal = max(signal)
    min_signal = min(signal)
    y_label = max(abs(min_signal), abs(max_signal))

    # Plot x
    plot(signal)
    plot(m_hat)
    axis('tight')
    xlabel(xlabel_string)
    ylabel(ylabel_String)
    title(fig_title)
    legend([legend_signal_str, legend_envelop_str])
    ylim(-y_label - 1, y_label + 1)
    show()
    return 0


def main():
    # Generate AM-modulated sinusoid
    N = 256
    t = linspace(0, 2, N)

    # Modulator
    m = 1 + .2 * cos(2 * pi * t)

    # Carrier
    c = sin(2 * pi * 20 * t)

    # Signal is modulator times carrier
    x = m * c

    # Calculate envelope, called m_hat via hilbert transform
    m_hat = abs(hilbert(x))

    # Plot x
    plot(t, x)
    plot(t, m_hat)
    axis('tight')
    xlabel('Time (seconds)')
    ylabel('Amplitude')
    title('X, with calculated envelope')
    legend(['x', 'm_hat'])
    ylim(-2, 2)
    show()
    return 0


if __name__ == '__main__':
    # from baseZhang import wavread
    # audio,fs=wavread('../../data/read.wav')
    # plotEnvelope(audio)
    # plotEnvelope([1, 1, 2, 3, -1, 4, 5, 6, 2, 2])
    main()
