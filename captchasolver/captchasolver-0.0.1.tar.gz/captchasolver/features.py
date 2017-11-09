import librosa
import numpy as np


def get_features(audio_file):
    X, sample_rate = librosa.load(audio_file)

    stft = np.abs(librosa.stft(X))

    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T,
                    axis=0)

    chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,
                     axis=0)

    mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,
                  axis=0)

    contrast = np.mean(librosa.feature.spectral_contrast(
        S=stft, sr=sample_rate).T, axis=0)

    tonnetz = np.mean(librosa.feature.tonnetz(
        y=librosa.effects.harmonic(X), sr=sample_rate).T, axis=0)
    return mfccs, chroma, mel, contrast, tonnetz


def extract_audio_file_features(audio_file):
    features = np.empty((0, 193))
    mfccs, chroma, mel, contrast, tonnetz = get_features(audio_file)
    ext_features = np.hstack([mfccs, chroma, mel, contrast, tonnetz])
    features = np.array(np.vstack([features, ext_features]))
    return features
