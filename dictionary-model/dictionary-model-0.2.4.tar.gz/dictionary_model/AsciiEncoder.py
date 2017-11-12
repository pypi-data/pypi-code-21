import string
import sklearn.preprocessing as skl_preproc


class AsciiEncoder:
    def __init__(self, available_chars):
        self.AVAILABLE_CHARS = available_chars
        self.encoder = skl_preproc.LabelEncoder()
        self.encoder.fit(list(self.AVAILABLE_CHARS))

    def convert_chars_to_indexes(self, characters_array):
        return self.encoder.transform(characters_array)

    def convert_indexes_to_chars(self, indexes_array):
        return self.encoder.inverse_transform(indexes_array)