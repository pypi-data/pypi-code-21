import gammatone.gtgram as gmt
import pylab
import scipy.io.wavfile as wav
import stft
from gammatone.plot import render_audio_from_file
from scipy.io import wavfile


def get_wav_info(wav_file):
    rate, data = wavfile.read(wav_file)
    return rate, data


def get_spec(wavPath):
    frame_rate, sound_info = get_wav_info(wavPath)
    # print frame_rate
    Pxx, freqs, bins, im = pylab.specgram(sound_info, Fs=frame_rate)
    return Pxx


def get_spec_2(wav_path):
    fs, audio = wav.read(wav_path)
    specgram = stft.spectrogram(audio, 256)

    return specgram


def get_spec_gammatone(wav_path):
    fs, audio = wav.read(wav_path)
    win_size = 0.08  # s
    hop_len = 0.04  # s
    channels = 1024
    f_min = 20
    specgram = gmt.gtgram(audio, fs, win_size, hop_len, channels, f_min)
    return specgram


def plot_spec_gammatone(wav_path):
    render_audio_from_file(wav_path, None, gmt.gtgram)
    return 0

def plot_spectrogram(wav_file):
    sound_info, frame_rate = get_wav_info(wav_file)
    pylab.figure(num=None, figsize=(19, 12))
    pylab.subplot(111)
    pylab.title('spectrogram of %r' % wav_file)
    pylab.specgram(sound_info, Fs=frame_rate)
    pylab.savefig('spectrogram.png')
