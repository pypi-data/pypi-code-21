import numpy as np


class TrainingSampleStore(object):
    def __init__(self):
        self._data = np.array([])

    def __len__(self):
        return len(self._data)

    def add(self, sample_x, sample_y):
        sample = np.array([sample_x, sample_y])
        if len(self._data) == 0:
            self._data = np.array([sample])
        else:
            self._data = np.vstack((self._data, sample))

    def get_train_x(self):
        if self._data.shape[0] == 0:
            return np.array([])
        return np.vstack(self._data[:, 0])

    def get_train_y(self):
        if self._data.shape[0] == 0:
            return np.array([])
        return np.vstack(self._data[:, 1])
