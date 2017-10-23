#!/usr/bin/python2

import pylab, numpy, scipy
from os import mkdir
from os.path import join as path_join
from math import floor, ceil
import scipy.io.wavfile as wf


def frame(x, fs, framesz, hop):
    framesamp = int(framesz * fs)
    hopsamp = int(hop * fs)
    w = scipy.hamming(framesamp)
    return scipy.array([w * x[i:i + framesamp]
                        for i in range(0, len(x) - framesamp, hopsamp)])


def stft(x, fs, framesz, hop):
    framesamp = int(framesz * fs)
    hopsamp = int(hop * fs)
    w = scipy.hamming(framesamp)
    X = scipy.array([scipy.fft(w * x[i:i + framesamp])
                     for i in range(0, len(x) - framesamp, hopsamp)])
    return X


def istft(X, fs, T, hop):
    x = scipy.zeros(T * fs)
    framesamp = X.shape[1]
    hopsamp = int(hop * fs)
    for n, i in enumerate(range(0, len(x) - framesamp, hopsamp)):
        x[i:i + framesamp] += scipy.real(scipy.ifft(X[n]))
    return x


def plot_selected(l, nst, ned, val=8e9):
    start_plot = scipy.zeros(l)
    end_plot = scipy.zeros(l)
    for a, b, n in zip(nst, ned, range(0, len(ned))):
        if n % 2 == 0:
            start_plot[a:b] = val * numpy.ones(b - a)
        else:
            end_plot[a:b] = val * numpy.ones(b - a)
    pylab.fill(start_plot, color="green")
    pylab.fill(end_plot, color="red")
    return 0


def signal_energy(signal, fs, fl=0.05, fh=0.02):
    X = stft(signal, fs, fl, fh)
    mag = scipy.absolute(X)
    energy = scipy.sum(mag, 1)
    return energy


def split_into_words(filename="singing5-w-fan.wav", wn=7,
                     thresh=13e6,
                     too_short=4, frame_len=0.025,
                     frame_hop=0.010):
    WORDS = [str(word) for word in range(wn)]
    (folder, ext) = filename.rsplit('.', 1)
    (fs, sig) = wf.read(filename)

    energy = signal_energy(sig, fs, frame_len, frame_hop)
    xx = scipy.diff(scipy.r_[[0], (energy > thresh).astype(int)])
    yy = scipy.diff(scipy.r_[(energy > thresh).astype(int), [0]])
    start_sig = scipy.nonzero(xx > 0)[0]
    end_sig = scipy.nonzero(yy < 0)[0]
    nst = start_sig
    ned = end_sig
    dist = ned - nst
    tooshort = scipy.nonzero(dist < too_short)
    nst = scipy.delete(nst, tooshort)
    ned = scipy.delete(ned, tooshort)
    dist = ned - nst
    edist = ned[1:] - ned[:-1]
    ll = len(nst) - wn
    tor = edist.argsort()[:ll]
    nst = scipy.delete(nst, tor + 1)
    ned = scipy.delete(ned, tor)
    for a, b in zip(nst, ned):
        print(fs * frame_hop * a), (fs * frame_hop * b)

    words = scipy.array([sig[int(fs * frame_hop * a):int(fs * frame_hop * b)] for a, b in zip(nst, ned)])

    try:
        mkdir(folder)
        for w in WORDS:
            mkdir(path_join(folder, w))
    except OSError, ex:
        pass

    for w, n in zip(words, range(0, len(words))):
        ww = n % wn
        wwig = floor(float(n) / float(wn))
        flnm = path_join(folder, WORDS[ww], "%02d.wav" % (wwig + 1))
        wf.write(flnm, fs, w)
    pylab.figure()
    pylab.plot(energy)
    plot_selected(len(energy), nst, ned, thresh)
    pylab.show()
    return energy,nst,ned,thresh
