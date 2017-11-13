# encoding=utf8
# author=spenly
# mail=i@spenly.com

from abc import ABCMeta, abstractmethod
import datetime


class BaseModel(metaclass=ABCMeta):
    TYPE = "NTF"  # choose from 'TF' or 'NTF': TensorFlow-based or not

    def __init__(self, verbose=False, **kwargs):
        self.__dict__.update(kwargs)
        self.verbose = verbose
        self.prepare()

    @abstractmethod
    def prepare(self):
        """
        # must have, rewrite
        prepare models/datasets only once
        :return:
        """
        pass

    @abstractmethod
    def is_ready(self):
        """
        # must have, rewrite
        check preparetion above before running
        :return: True or False
        """
        pass

    def preprocess(self, data):
        """
        # optional
        preprocess data
        :param data: input data in a dict format (may have a nested structure in values) from API Platform
        :return: preprocessed data, define data structure as you prefer
        """
        return data

    @abstractmethod
    def run_model(self, data):
        """
        # must have, rewrite
        run model to do inference
        :param data: preprocessed data
        :return: infered data, define data structure in your model. We recommend using a dict structure 
            (may have a one-layer nested structure in values) to store results.
            This may output to API Platform directly without post-processing.
        """
        return data

    def postprocess(self, result):
        """
        # optional
        postprocess infered data
        :param result: result
        :return: output data in a dict format (may have a one-layer nested structure in values) to API Platform
        """
        return result

    def run(self, data):
        """
        # must have
        run function
        :param data: data
        :return: data
        """
        self.validate_input_data(data)
        data = self.preprocess(data)
        result = self.run_model(data)
        return self.postprocess(result)

    @abstractmethod
    def docstring(self):
        """
        # must have, rewrite
        docstring for running function
        :return: docstring
        """
        docs = """
        input:
        output:
        """
        return docs

    class InvalidValueInput(Exception):
        pass

    @abstractmethod
    def validate_input_data(self, data):
        "raise BaseModel.InvalidValueInput if input is not expected"
        pass

    def log_info(self, string, *args, extra=()):
        if self.verbose:
            print(datetime.datetime.now(), string % args, *extra)

    def log_error(self, string, *args, extra=()):
        print(datetime.datetime.now(), string % args, *extra)
