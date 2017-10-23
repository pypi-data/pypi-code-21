from keras.utils import np_utils
from sklearn.preprocessing import LabelEncoder


def encode(Y=['a', 'b', 'c']):
    encoder = LabelEncoder()
    encoder.fit(Y)
    Y = encoder.transform(Y)
    Y = np_utils.to_categorical(Y)
    return Y, encoder


def decode(encoder, Y):
    Y = np_utils.probas_to_classes(Y)
    Y = encoder.inverse_transform(Y)
    return Y
