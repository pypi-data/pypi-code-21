import numpy as np
from keras.utils.np_utils import to_categorical

from . import downloader
from .AsciiEncoder import AsciiEncoder


class CharPredictor:

    __CONFIG_FILE_URL = 'https://raw.githubusercontent.com/eemkos/ModelWeights/master/config.yaml'
    __OUT_KEY = 'chars'
    __MOD_URLS_KEY = 'MODELS_URLS'
    __WEI_URLS_KEY = 'WEIGHTS_URLS'
    __MOD_INFS_KEY = 'MODELS_INFOS'
    __NB_LETT_KEY = 'nb_letters'
    __NB_POSS_KEY = 'nb_possible_chars'
    __PSBL_LETT_KEY = 'possible_letters'

    def __init__(self, nb_letters=None):
        self.output = None
        self.config = downloader.download_config(CharPredictor.__CONFIG_FILE_URL)

        if nb_letters is not None:
            self.nb_letters = nb_letters
        else:
            self.nb_letters = self.config['MODELS_INFOS'][0]['nb_letters']
        self.nb_possible_chars = self.config[CharPredictor.__NB_POSS_KEY]

        self.context = np.zeros((self.nb_letters, self.nb_possible_chars))
        self.context_size = 0

        self.model_index = 0
        self.models = self.load_models()
        self.model = self.models[0]

        self.out_key = CharPredictor.__OUT_KEY

    def transform(self, X=0, **transform_params):
        if X is None:
            return None
        x_data = self.context
        self.output = self.model.predict(np.asarray([x_data]))[0]
        return self.output

    def add_to_context(self, letter):
        if np.isscalar(letter):
            if type(letter) is str:
                letter_ind = AsciiEncoder(self.config[CharPredictor.__PSBL_LETT_KEY]).convert_chars_to_indexes([letter])[0]
            else:
                letter_ind = int(letter)
            letter = to_categorical(letter_ind, self.config[CharPredictor.__NB_POSS_KEY])

        is_current_context_full = self.context_size == self.nb_letters
        is_current_model_last = self.model_index+1 == len(self.models)

        if is_current_context_full and not is_current_model_last:
            self.__switch_to_next_model()
        self.context = np.append(self.context[1:], letter, axis=0)
        self.context_size = min([self.context_size + 1, self.nb_letters])

    def load_models(self):
        return downloader.download_models(self.config[CharPredictor.__MOD_URLS_KEY],
                                          self.config[CharPredictor.__WEI_URLS_KEY],
                                          self.config[CharPredictor.__MOD_INFS_KEY])

    def load_model(self):
        return downloader.download_models(self.config[CharPredictor.__MOD_URLS_KEY][:1],
                                          self.config[CharPredictor.__WEI_URLS_KEY][:1],
                                          self.config[CharPredictor.__MOD_INFS_KEY][:1])[0]

    def __switch_to_next_model(self):
        self.model_index += 1
        self.model = self.models[self.model_index]
        old_nb_lett = self.nb_letters
        self.nb_letters = self.config[CharPredictor.__MOD_INFS_KEY][self.model_index][CharPredictor.__NB_LETT_KEY]
        diff = self.nb_letters - old_nb_lett
        old_cont = self.context
        self.context = np.r_[np.zeros((diff, self.nb_possible_chars)), old_cont]


