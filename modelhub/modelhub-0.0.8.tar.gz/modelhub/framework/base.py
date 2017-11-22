# encoding=utf8
# author=spenly
# mail=i@spenly.com

from abc import ABCMeta, abstractmethod
import datetime

from modelhub.utils import json


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
        check preparation above before running
        :return: True or False
        """
        pass

    def preprocess(self, raw_input):
        """
        # optional
        preprocess data
        :param raw_input: input data in a dict format (may have a nested structure in values) from API Platform
        :return: preprocessed data, define data structure as you prefer
        """
        return raw_input

    @abstractmethod
    def run_model(self, preprocessed_data):
        """
        # must have, rewrite
        run model to do inference
        :param preprocessed_data: preprocessed data
        :return: inferred data, define data structure in your model. We recommend using a dict structure
            (may have a one-layer nested structure in values) to store results.
            This may output to API Platform directly without post-processing.
        """
        raise NotImplementedError

    def postprocess(self, result, raw_input, preprocessed_data):
        """
        # optional
        postprocess inferred data
        :param result: result
        :param raw_input: user input before preprocessing
        :param preprocessed_data: input after preprocessing
        :return: output data in a dict format (may have a one-layer nested structure in values) to API Platform
        """
        return result

    def run(self, raw_input):
        """
        # must have
        run function
        :param raw_input: data
        :return: result
        """
        self.validate_input_data(raw_input)
        preprocessed_data = self.preprocess(raw_input)
        inferenced_data = self.run_model(preprocessed_data)
        return self.postprocess(inferenced_data, raw_input, preprocessed_data)

    @abstractmethod
    def docstring(self):
        """
        # must have, rewrite
        docstring for running function
        :return: docs
        """
        docs = """
        inputs:
        outputs:
        """
        return docs

    class InvalidValueInput(Exception):
        pass

    @abstractmethod
    def validate_input_data(self, raw_input):
        "raise BaseModel.InvalidValueInput if input is not expected"
        pass

    def log_info(self, string, *args, extra=()):
        if self.verbose:
            print(datetime.datetime.now(), string % args, *extra)

    def log_error(self, string, *args, extra=()):
        print(datetime.datetime.now(), string % args, *extra)

    def _run_dict(self, data):
        result = self.run(data)
        return json.loads(json.dumps(result))
