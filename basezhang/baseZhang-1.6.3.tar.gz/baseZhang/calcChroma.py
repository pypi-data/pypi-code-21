import fromLibrosa


def calcChroma_stft(wav_path, hop_length=512,n_fft=2048):
    y, sr = fromLibrosa.load(wav_path)
    chroma_stft = fromLibrosa.chroma_stft(y=y, sr=sr, hop_length=hop_length,n_fft=n_fft)
    return chroma_stft.T


def calcChroma_cqt(wav_path, hop_length=512):
    y, sr = fromLibrosa.load(wav_path)
    chroma_cqt = fromLibrosa.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    return chroma_cqt


def calcChroma_cens(wav_path, hop_length=512,n_fft=2048):
    y, sr = fromLibrosa.load(wav_path)
    chroma_cens = fromLibrosa.chroma_cens(y=y, sr=sr, hop_length=hop_length)
    return chroma_cens


def calcTonnetz(wav_path):
    y, sr = fromLibrosa.load(wav_path)
    y = fromLibrosa.harmonic(y)
    tonnetz = fromLibrosa.tonnetz(y=y, sr=sr)
    return tonnetz
