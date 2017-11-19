import abc
from pandas import DataFrame
from entities import Score, ScoreTypes, Config


class Model(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        """

        :param Config config:
        """
        self.config = config

    @classmethod
    def from_config(cls, config):
        """

        :param Config config:
        :return:
        """
        if config.modelConfig.name == cls.__name__:
            model = cls(config)
            return model
        else:
            return None

    @abc.abstractmethod
    def fit(self, dataset_train_in, dataset_train_out, dataset_test_in, dataset_test_out):
        raise NotImplementedError

    @abc.abstractmethod
    def predict(self, dataset_predict_in):
        raise NotImplementedError

    @abc.abstractmethod
    def serialize(self, to):
        raise NotImplementedError

    @abc.abstractmethod
    def deserialize(self, from_):
        raise NotImplementedError


class SimpleModel(Model):
    def fit(self, dataset_train_in, dataset_train_out, dataset_test_in, dataset_test_out):
        """

        :param DataFrame dataset_train_in:
        :param DataFrame dataset_train_out:
        :param DataFrame dataset_test_in:
        :param DataFrame dataset_test_out:
        :return:
        :rtype: list[Score]
        """
        return [Score(ScoreTypes.LOSS, 0.7), Score(ScoreTypes.AUC, 0.1)]

    def predict(self, dataset_predict_in):
        """

        :param DataFrame dataset_predict_in:
        :return:
        """
        return dataset_predict_in.assign(predicted=[i for i in range(0, len(dataset_predict_in))])

    def serialize(self, to):
        pass

    def deserialize(self, from_):
        pass
