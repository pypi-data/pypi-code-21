import random

import numpy as np
import pandas as pd
from sklearn import preprocessing


class Container:
    def __init__(self,
                 data_frame,
                 training_set_split_ratio=0.7,
                 cross_validation_set_split_ratio=0.2,
                 test_set_split_ratio=0.1):
        """

        :param data_frame:
        :param training_set_split_ratio:
        :param cross_validation_set_split_ratio:
        :param test_set_split_ratio:
        """
        self.data = data_frame
        self.__data__ = data_frame
        self.scale = preprocessing.StandardScaler()
        self.normalizer = self.scale.fit(data_frame)
        self.feature_tags = []
        self.target_tags = []

        # take control over randomness
        self.__random_seed__ = random.seed(a=10)

        # create train/cv/test dataSet
        self.training_set_split_ratio = training_set_split_ratio
        self.cross_validation_set_split_ratio = cross_validation_set_split_ratio
        self.test_set_split_ratio = test_set_split_ratio
        self.__training_set_mask__ = None
        self.__cross_validation_set_mask__ = None
        self.__test_set_mask__ = None
        self.__feature_data__ = None
        self.__target_data__ = None

    def gen_mask(self, days=0):
        # define pseudo mask for generating class
        mask = np.random.rand(len(self.data) - days)
        self.__training_set_mask__ = mask <= self.training_set_split_ratio
        self.__cross_validation_set_mask__ = (mask > self.training_set_split_ratio) & \
                                             (
                                                 mask < (
                                                     self.training_set_split_ratio + self.cross_validation_set_split_ratio))
        self.__test_set_mask__ = mask >= (self.training_set_split_ratio + self.cross_validation_set_split_ratio)

    def detect_null(self):
        """

        :return:
        """
        # TODO: To make this fn fitting to different ranks
        return self.data.isnull().any()

    def restore(self):
        """

        :return:
        """
        self.data = self.__data__
        return self

    def interpolate(self, data, method=None):
        """

        :param data:
        :param method:
        :return:
        """
        self.__data__ = self.data
        self.data = data.interpolate(method=method)
        return self

    def set_feature_tags(self, feature_tags):
        """

        :param feature_tags:
        :return:
        """
        self.feature_tags = feature_tags
        return self

    def set_target_tags(self, target_tags):
        """

        :param target_tags:
        :return:
        """
        self.target_tags = target_tags
        return self

    def add_feature_tag(self, tag):
        """

        :param tag:
        :return:
        """
        self.feature_tags.append(tag)
        return self

    def add_target_tag(self, tag):
        """

        :param tag:
        :return:
        """
        self.target_tags.append(tag)
        return self

    def fit(self, data):
        """

        :param data:
        :return:
        """
        self.normalizer = self.scale.fit(data)
        return self

    def normalize(self, data):
        """

        :param data:
        :return:
        """
        return self.normalizer.transform(data)

    def compute_feature_data(self, shuffle=False):
        """

        :return:
        """
        if self.feature_tags is None:
            raise Exception('Feature tags not set, can\'t get feature data')
        result = self.data[self.feature_tags]
        # fit and transform feature data
        self.fit(result)
        normalized_array = self.normalize(result)
        constructed_df = pd.DataFrame(normalized_array, columns=self.feature_tags)
        self.__feature_data__ = constructed_df
        return self

    def compute_target_data(self):
        """

        :return:
        """
        if self.target_tags is None:
            raise Exception('Target tags not set, can\'t get target data')
        self.__target_data__ = self.data[self.target_tags]
        return self

    def get_last_data(self, days=30):
        gen_labels = []
        gen_data = []
        data = self.__feature_data__
        labels = self.feature_tags
        num_data = data.shape[0]
        starts_at = days
        num_feature_labels = days * len(self.feature_tags)

        for label in self.feature_tags:
            for j in range(days):
                gen_labels.append(label + '_' + str(j + 1))

        for k in range(starts_at, num_data):
            _from = k - days
            _to = k
            days_back_data = data[_from: _to]
            selected_day_back_data = days_back_data.loc[:, labels[0]:labels[-1]]
            selected_day_back_data_np = selected_day_back_data.values
            reshaped = np.reshape(selected_day_back_data_np.T,
                                  (1, num_feature_labels))
            gen_data.append(reshaped)
        stacked = np.vstack(row for row in gen_data)
        data_frame = pd.DataFrame(data=stacked, columns=gen_labels)
        self.__feature_data__ = data_frame
        self.__target_data__ = self.__target_data__[days:]
        return self

    def get_training_features(self):
        """

        :return:
        """
        return self.__feature_data__[self.__training_set_mask__]

    def get_training_targets(self):
        """

        :return:
        """
        return self.__target_data__[self.__training_set_mask__]

    def get_cross_validation_features(self):
        """

        :return:
        """
        return self.__feature_data__[self.__cross_validation_set_mask__]

    def get_cross_validation_targets(self):
        """

        :return:
        """
        return self.__target_data__[self.__cross_validation_set_mask__]

    def get_test_features(self):
        """

        :return:
        """
        return self.__feature_data__[self.__test_set_mask__]

    def get_test_targets(self):
        """

        :return:
        """
        return self.__target_data__[self.__test_set_mask__]
